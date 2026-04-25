# Implementation Plan: Studio Versions: resolve owner/repo for authored skills

## Overview

Add a git-remote fallback path to `resolveSkillApiName` (vskill/src/eval-server/api-routes.ts:1420). The lockfile path stays first; on miss, the resolver locates the authored skill on disk under `plugins/*/skills/<skill>/SKILL.md`, walks up to the enclosing git working tree, reads `remote.origin.url`, and parses it to `owner/repo`. Result is cached in a per-process `Map<string,string>` keyed by skill name. All four current callers (/versions, /versions/diff, /versions/compare, /update) consume the same helper unchanged.

## Design

### Components

- **`resolveSkillApiName(skill: string): string`** — existing helper, gains a fallback branch.
- **`findAuthoredSkillDir(skill: string): string | null`** — new internal helper. Globs `plugins/*/skills/<skill>/SKILL.md` under the eval-server's working repo root (resolved via existing `repoRoot`/process.cwd context) and returns the parent directory of the first lexicographic match.
- **`readGitOriginOwnerRepo(dir: string): { owner: string; repo: string } | null`** — new internal helper. Runs `git -C <dir> config --get remote.origin.url` via `execFile` (5 s timeout), parses GitHub HTTPS / SSH / git@ forms, returns `null` on any failure or unsupported host.
- **`authoredSkillCache: Map<string, string>`** — module-scoped Map. Stores the final resolved API name (either `owner/repo/skill` on success or the bare name on a confirmed miss) so repeat lookups never reshell-out.

### Data flow

```
resolveSkillApiName(skill)
├── lockfile hit? -> existing path -> return owner/repo/skill   (unchanged)
├── cache hit?    -> return cached value                         (new, fast path)
├── findAuthoredSkillDir(skill)
│     └── null -> cache + return bare skill name
├── readGitOriginOwnerRepo(skillDir)
│     └── null -> cache + return bare skill name
└── return owner/repo/skill  (cached)
```

### API Contracts

No public API changes. Behavior change is observable only through:
- `GET /api/skills/:plugin/:skill/versions` — now returns `source: "platform"` for authored skills with platform history (was `"none"`).
- `GET /api/skills/:plugin/:skill/versions/diff` — now succeeds for authored skills (was 200 with empty payload).
- `GET /api/skills/:plugin/:skill/versions/compare` — now hits the correct platform path.

### URL parser

Single regex set, ordered by frequency:
```
^https?://github\.com/([^/]+)/([^/.]+?)(?:\.git)?/?$
^git@github\.com:([^/]+)/([^/.]+?)(?:\.git)?$
^ssh://git@github\.com/([^/]+)/([^/.]+?)(?:\.git)?$
```
Anything else → null (silent fallback).

## Technology Stack

- **Language/Framework**: TypeScript (existing eval-server)
- **Libraries**: Node `node:child_process` (`execFile`), `node:fs/promises` (`access`, `readdir`), `node:path` — no new package dependencies.
- **Tools**: vitest for unit tests, existing `tsx` runner.

## Rationale

- **Why git remote and not skill metadata?** SKILL.md frontmatter has no canonical `repoUrl` for authored skills, and the platform record's `repoUrl` field is unavailable to the local resolver before resolution. Git remote is authoritative, already present, and matches the truth the platform's scanner uses.
- **Why disk scan + git rather than reuse `parseSource`?** `parseSource` parses lockfile source strings (`github:owner/repo#sha`) — different shape from `git remote get-url`. Reusing it would require synthesizing a fake source string. Direct URL parsing is simpler and lets us reject non-GitHub hosts cleanly.
- **Why per-process Map and not LRU?** Skill set is bounded (~50–100 authored skills max). Map memory is trivial. Studio session is short-lived. LRU adds complexity for no measurable benefit.
- **Why fallback to bare name (not 5xx) on git failure?** The /versions proxy is documented to return `source: "none"` for "no VCS surface" — that's the existing contract. Throwing breaks unrelated proxy routes.
- **Why first-match-wins for duplicate skill names?** Authored skills with identical bare names across plugins are vanishingly rare in practice (we found zero today), and the platform DB enforces uniqueness on `Skill.name = owner/repo/skill` so the deterministic lexicographic choice will route all duplicates to one resolved name. A future increment can add `pluginName` to the resolver signature if needed.

### ADR references

No new ADR. This change inherits the existing platform-routing convention recorded in `0707` (versions proxy hardening) and 0686 (skill API hierarchical names).

## Implementation Phases

### Phase 1 — Pure helpers (RED)
Failing unit tests for `findAuthoredSkillDir`, `readGitOriginOwnerRepo` (URL parser), and `resolveSkillApiName` authored-skill path.

### Phase 2 — Resolver fallback (GREEN)
Add the two helpers and wire them into `resolveSkillApiName` with the cache.

### Phase 3 — Integration & manual verify (REFACTOR)
Run full vskill vitest suite, restart Studio, confirm `appstore` Versions tab renders 1.0.0 + 1.0.1.

## Testing Strategy

- **Unit**: parser table for the three URL forms + 4 negative cases (non-GitHub, malformed, empty, undefined).
- **Unit**: `findAuthoredSkillDir` with a temp dir tree (multiple plugins, no match, ambiguous match).
- **Unit**: `readGitOriginOwnerRepo` with `execFile` mocked via `vi.hoisted` (existing pattern in vskill tests).
- **Unit**: `resolveSkillApiName` four-branch table — lockfile hit, authored hit, authored miss (no SKILL.md), authored found-but-no-remote.
- **Cache**: assert second call to `resolveSkillApiName` issues zero shell-outs (mock counter).
- **Existing tests**: must continue to pass with zero modifications (regression gate).

## Technical Challenges

### Challenge 1: Detecting eval-server's working repo root
**Solution**: The eval-server already knows its plugins directory via existing config / `process.cwd()`. Use the same source.
**Risk**: Wrong cwd → false-negative discovery → silent fallback to bare name → identical to today's broken behavior. No regression.

### Challenge 2: execFile cross-platform
**Solution**: Pass `git` as the command (resolved via PATH); rely on Node's cross-platform handling. Already works for other vskill code paths.
**Risk**: Windows path quirks; mitigated by passing `dir` via `-C <dir>` arg (no shell quoting).

### Challenge 3: Cache invalidation
**Solution**: None — cache lives for the eval-server process. Studio restart wipes it naturally; the next open re-derives. No code path mutates a skill's git remote during a Studio session.
**Risk**: Stale cache after a user changes `git remote set-url` mid-session. Acceptable: rare, and a Studio reload fixes it.
