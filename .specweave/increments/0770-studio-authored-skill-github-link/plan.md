# Implementation Plan: Studio header — clickable GitHub link for locally-authored skills

## Overview

Server-side enhancement to `vskill`'s eval-server. Two new pure helpers (`parseGithubRemote`, `walkUpForGitRoot`) and one I/O helper (`detectAuthoredSourceLink`) added to `api-routes.ts`. The existing `resolveSourceLink` function gets a single fall-through branch: when no lockfile entry resolves provenance, call `detectAuthoredSourceLink(skillDir)` and return its result. The eval-UI is unchanged — `SourceFileLink.tsx` already renders the `↗` anchor whenever `repoUrl` is a valid HTTPS URL.

This is a one-file, one-test-file change. No new modules, no new dependencies, no UI work.

## Design

### Components

- **`parseGithubRemote(remote: string): string | null`** — Pure string transform. Regex-based. Accepts SSH (`git@github.com:owner/repo[.git]`), HTTPS (`https://github.com/owner/repo[.git]`), and `ssh://` URL forms. Returns canonical `https://github.com/owner/repo` (no trailing `.git`, no path beyond `owner/repo`). Returns `null` for any non-`github.com` host or malformed input.

- **`walkUpForGitRoot(startDir: string, maxLevels = 12): string | null`** — Pure filesystem-only helper (uses `existsSync`, no git invocations). Walks parent directories looking for a `.git` entry (directory OR file — git worktrees use a `.git` file). Bails at filesystem root or `maxLevels`. Returns the discovered git root path or `null`.

- **`detectAuthoredSourceLink(skillDir: string): {repoUrl: string | null, skillPath: string | null}`** — Composes the two pure helpers with two `git` invocations. Memoized in a module-level `Map<absoluteSkillDir, result>`. Never throws — returns `{null, null}` on any error.

- **`resolveSourceLink(skillDir, root)`** — Existing function, modified: appends a single fall-through to `detectAuthoredSourceLink(skillDir)` after the existing lockfile branches return `{null, null}`. Lockfile precedence is preserved.

### Data flow

```
GET /api/skills
  └─ scan skills, for each skill.dir:
       └─ buildSkillMetadata(skillDir, origin, root)
            └─ resolveSourceLink(skillDir, root)
                 ├─ readLockfile(root)
                 ├─ if lockfile entry resolves → return {repoUrl, skillPath}    [existing 0737/0743 path]
                 └─ else → detectAuthoredSourceLink(skillDir)                   [NEW]
                      ├─ check module cache → return cached result
                      ├─ walkUpForGitRoot(skillDir) → null? cache + return {null, null}
                      ├─ execFileSync("git", ["config","--get","remote.origin.url"], {cwd: gitRoot, ...})
                      ├─ parseGithubRemote(remote) → null? cache + return {null, null}
                      ├─ execFileSync("git", ["ls-files","--full-name","SKILL.md"], {cwd: skillDir, ...})
                      │    └─ on empty stdout → fallback: relative(gitRoot, join(skillDir, "SKILL.md"))
                      └─ cache + return {repoUrl, skillPath}
```

### API contracts

No API surface changes. The shape of `/api/skills` response is unchanged — only the values of two existing fields (`repoUrl`, `skillPath`) become non-null for authored skills in github-pushed git repos.

### Files modified

| File | Change |
|------|--------|
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` | Add `parseGithubRemote`, `walkUpForGitRoot`, `detectAuthoredSourceLink`. Append fall-through to `resolveSourceLink`. ~80 LOC added. |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authored-source-link.test.ts` | New test file. ~250 LOC. Covers all branches via tmp directories with real `git init` + remotes. |

### Files NOT modified

- `eval-ui/src/components/SourceFileLink.tsx` — already correct
- `eval-ui/src/components/DetailHeader.tsx` — already passes through
- `eval-server/__tests__/skill-metadata-source-link.test.ts` — preserved as-is for 0737/0743 regression coverage

## Technology Stack

- **Language**: TypeScript (existing, ESM, `--moduleResolution nodenext`, `.js` import extensions)
- **Test framework**: Vitest (existing)
- **Runtime deps**: `node:child_process` (`execFileSync`), `node:fs` (`existsSync`), `node:path` (`dirname`, `join`, `relative`, `resolve`) — ALL already imported in `api-routes.ts`
- **External deps**: `git` CLI on PATH — assumed available; gracefully degrades to `{null, null}` if missing

## Rationale

### Why server-side detection?
The studio bundle runs in the browser. `child_process` is server-only. The eval-server already runs git commands elsewhere (version detection, plugin discovery), so adding two more is consistent. Doing this client-side would require shipping git remote info via a new API field, which is exactly what `repoUrl`/`skillPath` already are — so we just populate them.

### Why `HEAD` and not a specific branch?
Authored skills may have unpushed commits on feature branches; pinning to a specific branch would 404 for users viewing on github.com. `HEAD` on github.com resolves to whatever is currently on the default branch — the canonical "view this skill" target. Branch-aware URLs are explicitly out of scope (deferred to a future increment).

### Why memoize per-process, not per-request?
The studio session is short-lived (one process = one studio session). Skills don't move during a session. Persistent on-disk cache would require invalidation logic (file change detection), which is overkill — restarting the server invalidates cleanly.

### Why precedence: lockfile first, then authored detection?
Installed skills already carry authoritative `sourceRepoUrl`/`sourceSkillPath` from platform install. Falling through to git detection for an installed skill could produce wrong results in the rare case where the workspace itself is a git repo with a different remote (e.g., user has cloned the umbrella repo and installed skills into it). Lockfile-first preserves install-time provenance.

### Why no auto-fallback to non-github hosts?
`SourceFileLink` builds `/blob/HEAD/` URLs — that's github-specific syntax. Gitlab uses `/-/blob/HEAD/`, bitbucket `/src/HEAD/`. Returning `null` for non-github remotes keeps the existing copy-chip, which is correct. Adding gitlab/bitbucket support is a host-aware URL builder change in `SourceFileLink` — out of scope here.

### Why `execFileSync` and not `execSync`?
`execFileSync` accepts argv as a literal array — no shell interpolation, no command injection risk. The cwd path is the only user-influenced input, and it's already a controlled directory path. Defense in depth.

### Why a 12-level walk-up cap?
12 levels is well beyond any realistic project depth (a path like `/Users/a/projects/x/repos/y/.../skill` would already saturate at ~6-8 levels). Cap prevents pathological loops if `dirname` ever fails to terminate.

### Why fall back to filesystem-relative path when `git ls-files` is empty?
`git ls-files --full-name` returns empty for untracked files. An author may have created a SKILL.md but not yet `git add`-ed it. The blob URL `/blob/HEAD/path` will still 404 in that case — but once the file is committed and pushed, the same URL resolves correctly. The fallback gives a stable URL the moment the user pushes, without requiring a studio reload.

## Implementation Phases

### Phase 1: Pure helpers (TDD red → green)
- T-001: RED — write `parseGithubRemote` test cases (all SSH/HTTPS/ssh:// + non-github + malformed)
- T-002: GREEN — implement `parseGithubRemote`
- T-003: RED — write `walkUpForGitRoot` test cases (found at start, found at parent, not found, bails at root)
- T-004: GREEN — implement `walkUpForGitRoot`

### Phase 2: I/O helper with memoization (TDD)
- T-005: RED — `detectAuthoredSourceLink` integration tests with real `git init` in tmp dirs
- T-006: GREEN — implement `detectAuthoredSourceLink` with module-level Map memoization

### Phase 3: Wire into resolveSourceLink
- T-007: RED — test that lockfile precedence holds AND authored fall-through fires when lockfile is absent
- T-008: GREEN — append fall-through line to `resolveSourceLink`

### Phase 4: Manual verification
- T-009: Restart eval-server, open `http://localhost:3136/#/skills/TestLab/greet-anton`, verify `↗` link present and clickable

## Testing Strategy

**Unit tests** for the two pure helpers (no I/O): `parseGithubRemote`, `walkUpForGitRoot`. Fast, deterministic.

**Integration tests** for `detectAuthoredSourceLink` and the wired `resolveSourceLink`: use `mkdtempSync` + `execFileSync("git", ["init"])` + `execFileSync("git", ["remote", "add", ...])` to seed real git repos in tmp dirs. Cleanup with `rmSync(..., {recursive: true, force: true})` in `afterEach`.

**Regression coverage**: existing `skill-metadata-source-link.test.ts` (6 cases for 0737/0743) MUST continue to pass without modification. The fall-through addition only kicks in when the lockfile branch returns `{null, null}` — for all 6 existing cases the result must be byte-identical.

**Manual verification** (per memory `feedback_self_install_vskill.md`): the closer agent installs `vskill` at the candidate version and runs the studio itself — does NOT ask the user to restart their session.

## Technical Challenges

### Challenge 1: Git command availability
**Risk**: User environment may not have `git` on PATH (rare on dev machines, more common in containers).
**Solution**: All `execFileSync` calls are wrapped in `try/catch` and return `{null, null}` on any error. Detection silently degrades to the copy-chip fallback — same behavior as a non-git skill.

### Challenge 2: Git worktrees
**Risk**: Worktrees use a `.git` FILE (not a directory) pointing to the main repo's `.git` dir.
**Solution**: `existsSync(.git)` returns `true` for both files and directories. `git config --get remote.origin.url` works correctly from inside a worktree (it follows the `.git` file to find the real config). No special handling needed.

### Challenge 3: Submodules
**Risk**: A skill inside a submodule could resolve to the submodule's remote (correct) or the parent repo's remote (wrong).
**Solution**: `walkUpForGitRoot` finds the FIRST `.git` ancestor, which for a submodule is the submodule's own `.git` file. `git config --get remote.origin.url` from inside a submodule reports the submodule's remote. This is the intended behavior — viewing a submodule's SKILL.md should link to the submodule's repo on GitHub.

### Challenge 4: Concurrent calls during initial scan
**Risk**: First `/api/skills` request triggers parallel detection for many skills; the same skill could be detected twice.
**Solution**: The Map memoization is sufficient because `buildSkillMetadata` is called sequentially per skill in the scan loop (no parallelism in the existing code). If parallelism is added later, a `Map<dir, Promise>` upgrade is straightforward — but unnecessary for this increment.

## ADR References

No new ADRs required. The change is a pure additive enhancement to an existing well-defined function (`resolveSourceLink`); the architectural pattern (lockfile → fallback chain) is already established by 0737/0743.
