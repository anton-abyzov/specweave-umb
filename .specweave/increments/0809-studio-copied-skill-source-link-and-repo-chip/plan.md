# Implementation Plan: Studio header parity — repo chip + GitHub link for Copied (independent) skills

## Overview

Two coordinated changes shipped together:

1. **Server data path** — extract the source-link resolver into its own module, add a `.vskill-source.json` sidecar reader, and write the sidecar at scope-transfer time so Studio "Copy" / promote into Personal scope persists source provenance for the destination skill.
2. **UI parity path** — add a `RepoLink` component and insert it into `DetailHeader`'s byline so every skill with a known GitHub `repoUrl` gets a clickable `owner/repo` chip alongside the existing author + file links.

No new external integrations, no schema migration, no auth surface, no new server payload fields. All changes live inside `repositories/anton-abyzov/vskill/` (the **Project**: vskill child repo per umbrella mode).

## Architecture

### Components

#### Server (`src/eval-server/`)
- **`source-link.ts` (NEW)** — Self-contained source-link resolver module. Exports `resolveSourceLink`, `detectAuthoredSourceLink`, `parseGithubRemote`, `readCopiedSkillSidecar`, `resetAuthoredSourceLinkCache`, `resetCopiedSkillSidecarCache`. Pure functions over disk + lockfile state. No network. No HTTP. Memoized per-skillDir.
- **`api-routes.ts` (MODIFIED)** — Re-exports the public surface from `source-link.ts` for backwards compatibility. `buildSkillMetadata()` calls `resolveSourceLink` from the new module. `resetAuthoredSourceLinkCache` test export preserved through re-export.

#### Studio lib (`src/studio/lib/`)
- **`scope-transfer.ts` (MODIFIED)** — `transfer()` calls `resolveSourceLink(sourcePath, root)` AFTER the copy completes; if `repoUrl` is non-null, writes `<destPath>/.vskill-source.json`. `copyOwnSkillFiltered()` filters `.vskill-source.json` parallel to existing `.vskill-meta.json` filter.

#### Shared copy (`src/shared/`)
- **`copy-plugin-filtered.ts` (MODIFIED)** — Add `.vskill-source.json` to the exclusion list (uniform with OWN-scope filter).

#### UI (`src/eval-ui/src/components/`)
- **`RepoLink.tsx` (NEW)** — Clickable owner/repo anchor. Reuses `canonicalRepoUrl` from `SourceFileLink.tsx`. Returns `null` when `repoUrl` is null or unparseable.
- **`DetailHeader.tsx` (MODIFIED)** — Byline row at lines 290-318 inserts `<RepoLink>` between `<AuthorLink>` and `<SourceFileLink>`.

### Data Model

#### Sidecar: `.vskill-source.json`
Lives at `<skillDir>/.vskill-source.json`. Two fields:
```json
{
  "repoUrl": "https://github.com/anton-abyzov/greet-anton-test",
  "skillPath": "SKILL.md"
}
```
- `repoUrl`: REQUIRED. Canonical `https://github.com/{owner}/{repo}` (no `.git`, no path segments beyond owner/repo).
- `skillPath`: OPTIONAL (`string | null`). Relative path to SKILL.md inside the repo. May be `null` for multi-skill repos (preserves 0743 contract).

Validation: any deviation → reader returns `{null, null}` and resolver falls through to authored detector.

#### `vskill.lock` schema
Unchanged. Existing `sourceRepoUrl` + `sourceSkillPath` fields retain their authority (lockfile beats sidecar in resolver precedence).

### API Contracts

`/api/skills` payload shape unchanged. `repoUrl: string | null` and `skillPath: string | null` already exist in `SkillMetadataFields` (api-routes.ts:557-581). The sidecar feeds the existing fields via the existing resolver — no new fields, no version bump.

### Resolver Precedence (final)

```
resolveSourceLink(skillDir, root):
  1. Lockfile entry with explicit sourceRepoUrl  →  return {repoUrl, skillPath ?? "SKILL.md"}    [0737/0743]
  2. Lockfile entry with legacy `source: github:...`  →  parse owner/repo, derive skillPath      [0743]
  3. <skillDir>/.vskill-source.json valid  →  return {repoUrl, skillPath}                        [NEW — this increment]
  4. detectAuthoredSourceLink(skillDir)                                                          [0770]
```

Why this order:
- Lockfile = explicit install receipt (highest authority).
- Sidecar = explicit copy receipt (snapshots whatever the source itself resolved to at copy time).
- Authored detector = inferred fallback (walks up `.git`, parses origin remote).

Sidecar beats authored because the studio CWD's git remote (umbrella's repo) is the wrong source of truth for a skill copied from elsewhere.

## Technology Stack

- **Server language**: TypeScript ESM (`--moduleResolution nodenext`, `.js` import extensions required per project memory `project_vskill_platform_gotchas.md`).
- **UI language**: TypeScript + React 19 (Vite-built bundle served by eval-server per memory `project_vskill_studio_runtime.md`).
- **Tests**: Vitest. UI: `@testing-library/react` + jsdom (mirrors existing `DetailHeader.byline.test.tsx`, `SourceFileLink.test.tsx`).
- **Filesystem**: `node:fs` `readFileSync` / `writeFileSync` / `existsSync` (already used in scope-transfer + api-routes).
- **JSON**: `JSON.parse` / `JSON.stringify` — no external schema validator (regex + shape check is sufficient and matches the safety contract of `detectAuthoredSourceLink`).

**Architecture Decisions**:

- **Sidecar over frontmatter**: Keep SKILL.md content untouched (no-touch principle from `feedback_skill_naming_flat_dirs.md` and the publish flow). Sidecar follows the existing `.vskill-meta.json` precedent (scope-transfer.ts:13, 104).
- **Module extraction**: New `src/eval-server/source-link.ts` rather than keeping resolver inline in `api-routes.ts`. Eliminates circular-import risk for `scope-transfer.ts` importing the resolver. Re-export from `api-routes.ts` for backwards compat.
- **`RepoLink` returns null on unparseable input**: No copy-chip fallback for the repo chip. Keeps the byline visually clean for non-github skills (the file chip already covers the local-path-copy fallback).
- **Reuse `canonicalRepoUrl`**: Single canonicalization function shared between `SourceFileLink` and `RepoLink` to avoid divergent URL handling.

## Implementation Phases

### Phase 1: Foundation (US-002, US-003 server-side)
- Extract `resolveSourceLink`, `detectAuthoredSourceLink`, `parseGithubRemote`, lockfile reader from `api-routes.ts` into `src/eval-server/source-link.ts`. Re-export from `api-routes.ts`.
- Add `readCopiedSkillSidecar(skillDir)` with module-level memo + reset hook.
- Wire sidecar branch into `resolveSourceLink` precedence between lockfile fallback and authored detector.
- All 0737/0743/0770 tests must continue to pass against the new module structure.

### Phase 2: Core data path (US-001)
- Modify `transfer()` in `src/studio/lib/scope-transfer.ts` to call `resolveSourceLink(sourcePath, root)` post-copy and write `.vskill-source.json` when `repoUrl` is non-null.
- Add `.vskill-source.json` to `copyOwnSkillFiltered` exclusion (parallel to `.vskill-meta.json`).
- Add `.vskill-source.json` to `src/shared/copy-plugin-filtered.ts` exclusion list.

### Phase 3: UI parity (US-004)
- New `src/eval-ui/src/components/RepoLink.tsx`. Export `RepoLink` and `parseOwnerRepo`.
- Insert `<RepoLink>` into `DetailHeader.tsx` byline (lines 290-318) between `<AuthorLink>` and `<SourceFileLink>`.

### Phase 4: Tests + verification
- New + extended tests per `tasks.md` (BDD scenarios trace to ACs).
- `npm run build && npx vitest run`.
- Self-install vskill, launch studio on free port, screenshot proof: header with three chips for a Copied skill.

## Testing Strategy

| Layer | Test File | Coverage |
|---|---|---|
| Server unit | `src/eval-server/__tests__/copied-source-link.test.ts` (new) | Sidecar reader: missing file, malformed JSON, missing repoUrl, non-https URL, non-github host, valid → returned, memo + cache reset |
| Server unit | `src/eval-server/__tests__/authored-source-link.test.ts` (extended) | New `describe("resolveSourceLink with sidecar")` block — sidecar wins over authored, lockfile wins over sidecar, malformed sidecar falls through to authored |
| Server unit | `src/eval-server/__tests__/skill-metadata-source-link.test.ts` (regression) | All existing 0737/0743 cases still green after extraction |
| Studio unit | `src/studio/lib/__tests__/scope-transfer.test.ts` (extended; create if absent) | transfer() writes sidecar when source resolvable; no sidecar when source returns null pair; existing `.vskill-source.json` filtered from copy; chained copy snapshots ORIGINAL repoUrl |
| Shared unit | `src/shared/__tests__/copy-plugin-filtered.test.ts` (extended) | `.vskill-source.json` excluded |
| UI unit | `src/eval-ui/src/components/__tests__/RepoLink.test.tsx` (new) | Renders anchor with correct href; null on null/empty/non-github; canonicalizes /tree/, /blob/, .git, www subdomain |
| UI unit | `src/eval-ui/src/components/__tests__/DetailHeader.byline.test.tsx` (extended) | Three-chip byline order, repo chip presence/absence based on skill.repoUrl |
| Manual E2E | Studio at runtime | Copy a known-source skill via Studio, screenshot the resulting three-chip header byline; verify all three anchors resolve to the right GitHub URLs |

Coverage target per increment-level rubric: 90%. The resolver + sidecar reader hot path runs on every `/api/skills` call; comprehensive unit coverage is the right investment.

## Technical Challenges

### Challenge 1: Circular import risk between `api-routes.ts` and `scope-transfer.ts`
**Solution**: Extract resolver to standalone `src/eval-server/source-link.ts` with no dependencies on `api-routes.ts` or studio code. Both `api-routes.ts` (server response builder) and `scope-transfer.ts` (studio copy) import from `source-link.ts`. The resolver has no imports from either consumer.
**Risk**: If `source-link.ts` ends up needing helpers that currently live in `api-routes.ts`, those helpers must move with it (e.g., `readLockfile` already lives in `src/lockfile/` so it's safe to import). Mitigation: during extraction, follow imports out from `resolveSourceLink` and pull every transitively-needed local helper into `source-link.ts`. Run `tsc --noEmit` after extraction to catch any lingering circular shape.

### Challenge 2: Chained copy semantics — preserving the ORIGINAL source through multiple copies
**Solution**: In `transfer()`, call `resolveSourceLink(sourcePath, root)` — NOT a direct read of the source's sidecar. The resolver itself (after Phase 1 lands) traverses the chain (lockfile → sidecar → authored), so when source A already has a sidecar pointing to repo X, `resolveSourceLink(A)` returns X's coordinates. The destination's new sidecar therefore snapshots X, not A. This propagates the *ultimate origin* through any number of intermediate copies.
**Risk**: If the source is later moved or its sidecar deleted, that historic point-in-time still lives in destinations made before the change — by design (snapshot semantics). Mitigation: spec calls out that `.vskill-source.json` is a snapshot, not a live reference. Out of scope: invalidating downstream sidecars when source mutates.

### Challenge 3: Validating `repoUrl` shape strictly enough to never produce a 404 anchor
**Solution**: `parseOwnerRepo` (RepoLink helper) and `readCopiedSkillSidecar` (server helper) BOTH validate `repoUrl`. Server-side: regex `^https://github\.com/[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9._-]+$` + canonicalization. UI-side: `URL` parse + hostname check + path-segment count. Invalid → return `null` (server: `{null, null}`; UI: `null` element).
**Risk**: Owner segment regex tolerates legacy GitHub usernames; repo segment allows underscores and dots (legitimate). Mitigation: tests cover both extremes — `anton-abyzov/greet-anton-test` (kebab), `org_name/repo.with.dots`, malformed `://github.com/x` (URL-parse fail), `https://gitlab.com/x/y` (host fail).
