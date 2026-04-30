---
increment: 0809-studio-copied-skill-source-link-and-repo-chip
title: 'Studio header parity: repo chip + GitHub link for Copied (independent) skills'
type: feature
priority: P1
status: completed
created: 2026-04-30T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio header parity — repo chip + GitHub link for Copied (independent) skills

## Overview

The vskill Studio detail header should match the verified-skill.com skill page layout — for every installed/available skill with a known GitHub origin, the byline shows three clickable affordances: **author** → owner profile, **repo** → repository root, **skill file** → `SKILL.md` blob. Today only author + file render, and even those go missing for skills installed via the Studio Copy / scope-transfer flow into Personal scope (`installMethod: "copied"`, label "Copied (independent)").

This increment closes both gaps in one ship:

1. **Data path (Copied skills)** — at scope-transfer time, snapshot the source skill's `{repoUrl, skillPath}` (already resolvable by the existing chain that powers 0737/0743/0770) into a new `.vskill-source.json` sidecar in the destination, then teach `resolveSourceLink` to read that sidecar between the lockfile branch and the authored-detector branch.
2. **UI path (all skills)** — add a new `RepoLink` component that renders a clickable `owner/repo` chip linking to `https://github.com/{owner}/{repo}`, and insert it into `DetailHeader.byline` between `AuthorLink` and `SourceFileLink`. Existing lockfile-installed and authored skills with `repoUrl` populated benefit immediately; copied skills benefit once their sidecar is in place.

Reference target: `verified-skill.com/skills/coreyhaines31/marketingskills/customer-research`.

## Problem

- **UI gap**: `DetailHeader.tsx:290-318` renders `<AuthorLink>` (links to `github.com/{owner}`) and `<SourceFileLink>` (links to file blob), but no clickable `owner/repo` chip linking to the repository root. Users cannot one-click jump from the studio header to a skill's GitHub repo, only to the author's profile or the file itself.
- **Data gap**: Studio's "Copy" / scope-transfer flow at `src/studio/lib/scope-transfer.ts:118` (`transfer()`) does not record source provenance. The destination skill at `~/.claude/skills/<name>/` has no lockfile receipt (so 0737/0743 returns null) and lives outside any `github.com`-origin git ancestor (so 0770's authored detector returns null). `resolveSourceLink` falls through to `{null, null}`, the API payload omits `repoUrl` + `skillPath`, the header byline collapses to a copy-chip with the absolute install path, and the user has no clickable path back to the source on GitHub.

Concrete repro from the user-supplied screenshot: `~/.claude/skills/survey-passing/` (copied via Studio from `greet-anton-test`) shows install method "Copied (independent)" and the path `/Users/antonabyzov/.claude/skills/survey-passing` as a copy chip — no `↗` anchor, no repo chip. The "Publish-ready" row below shows a GitHub origin, but that origin is the studio's CWD git remote (publish target), NOT the skill's source — the wrong source of truth for the header link.

## User Stories

### US-001: Studio Copy captures source provenance into a sidecar (P1)
**Project**: vskill

**As a** skill author who copies a skill into Personal scope via the Studio Copy / scope-transfer flow
**I want** the destination skill to remember its source GitHub repo and SKILL.md path
**So that** the studio detail header can render a clickable `↗` link to the source on GitHub — parity with lockfile-installed skills (0737/0743) and authored skills (0770)

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `transfer()` (scope-transfer.ts:118) finishes copying a skill from any source scope into any destination scope, it calls `resolveSourceLink(sourcePath, root)` and, if the result has a non-null `repoUrl`, writes `<destPath>/.vskill-source.json` with the JSON-stringified `{repoUrl, skillPath}` (2-space indent).
- [x] **AC-US1-02**: When `resolveSourceLink(sourcePath, root)` returns `{null, null}`, `transfer()` writes NO sidecar file. The destination directory contents match the pre-change behavior byte-for-byte.
- [x] **AC-US1-03**: When the source skill itself contains a `.vskill-source.json`, `resolveSourceLink(sourcePath, root)` reads the source's sidecar (via the new branch in US-002), so the destination's snapshot points to the ORIGINAL GitHub source — not to an intermediate copy location. The source's sidecar is filtered from the actual file copy (US-003) so it is never blindly propagated.
- [x] **AC-US1-04**: Sidecar payload is exactly `{ "repoUrl": "https://github.com/{owner}/{repo}", "skillPath": "<relative-path-or-null>" }`. `repoUrl` is the canonical form (no trailing `.git`, no `/tree/` or `/blob/` segments). `skillPath` may be `null` for multi-skill repos (preserves 0743 contract).

---

### US-002: `resolveSourceLink` reads sidecar between lockfile and authored detector (P1)
**Project**: vskill

**As a** maintainer of the Studio source-link resolver
**I want** `.vskill-source.json` to slot into the precedence chain between the lockfile branch and the authored-detector branch
**So that** copied skills surface their GitHub origin in the header without disturbing the install-time provenance lockfile installs already have, and without letting the studio's CWD git remote leak into copied-skill links

**Acceptance Criteria**:
- [x] **AC-US2-01**: `readCopiedSkillSidecar(skillDir)` reads `<skillDir>/.vskill-source.json`, parses JSON, validates `repoUrl` is a non-empty `https://github.com/{owner}/{repo}` shape, and returns `{repoUrl, skillPath}` on success or `{null, null}` on missing file / parse error / shape failure / non-github host. Never throws.
- [x] **AC-US2-02**: Result is memoized in a module-level `Map<absoluteSkillDir, ...>` for the eval-server lifetime. A `resetCopiedSkillSidecarCache()` test hook clears the map (parallel to existing `resetAuthoredSourceLinkCache`).
- [x] **AC-US2-03**: `resolveSourceLink(skillDir, root)` precedence is exactly: (1) lockfile entry with `sourceRepoUrl` → return that; (2) lockfile entry with legacy `source: github:...` → existing logic at api-routes.ts:1058-1069; (3) NEW: `readCopiedSkillSidecar(skillDir)` returns non-null `repoUrl` → return that; (4) `detectAuthoredSourceLink(skillDir)` (existing 0770 path).
- [x] **AC-US2-04**: When BOTH lockfile entry AND sidecar exist, lockfile wins (sidecar branch never consulted) — preserves existing 0737/0743/0770 contract.
- [x] **AC-US2-05**: When sidecar is malformed (invalid JSON, missing `repoUrl`, non-`https://github.com/...`), resolver falls through to `detectAuthoredSourceLink` — no throw, no broken anchor in the UI.

---

### US-003: Sidecar is filtered on subsequent copies; resolver module is extracted (P2)
**Project**: vskill

**As a** maintainer
**I want** `.vskill-source.json` to be excluded from the file-copy in `copyOwnSkillFiltered` and `copyPluginFiltered`, AND I want `resolveSourceLink` + helpers to live in their own module so studio code can import them without circular-import risk
**So that** copying a copied skill re-derives provenance fresh in the destination (rather than blindly carrying a stale snapshot through), and the dependency graph stays clean

**Acceptance Criteria**:
- [x] **AC-US3-01**: `copyOwnSkillFiltered` (scope-transfer.ts:101) skips `.vskill-source.json` at the OWN scope root, parallel to existing `.vskill-meta.json` filter (line 104). Verified by unit test: source dir contains both sidecars → destination dir contains neither.
- [x] **AC-US3-02**: `copyPluginFiltered` (src/shared/copy-plugin-filtered.ts) similarly excludes `.vskill-source.json`. Uniform rule across both copy directions.
- [x] **AC-US3-03**: `resolveSourceLink`, `detectAuthoredSourceLink`, `parseGithubRemote`, `readCopiedSkillSidecar`, lockfile reader extracted into `src/eval-server/source-link.ts`. `api-routes.ts` re-exports them for backwards compatibility. All existing 0737/0743/0770 tests continue to pass against the new module structure.

---

### US-004: New `RepoLink` chip renders clickable owner/repo link in DetailHeader byline (P1)
**Project**: vskill

**As a** Studio user viewing any skill detail page
**I want** a clickable `owner/repo` chip in the header byline that opens the repository on GitHub
**So that** I have one-click navigation from the studio to the repo root — parity with verified-skill.com

**Acceptance Criteria**:
- [x] **AC-US4-01**: New `src/eval-ui/src/components/RepoLink.tsx` exports a `RepoLink({ repoUrl })` component that renders an `<a data-testid="repo-link" href="https://github.com/{owner}/{repo}" target="_blank" rel="noopener noreferrer">{owner}/{repo}</a>` styled to mirror `AuthorLink` (sans-serif 12px, dotted-underline, `var(--text-accent)`).
- [x] **AC-US4-02**: `RepoLink` returns `null` when `repoUrl` is `null`, empty, or unparseable as `github.com` — non-github skills keep the existing 2-chip byline (no orphaned chip, no broken anchor).
- [x] **AC-US4-03**: `RepoLink` correctly canonicalizes `repoUrl` shapes that include `/tree/<branch>`, `/blob/<branch>/path`, trailing slash, trailing `.git`, and `www.github.com` — extracts owner+repo and constructs the canonical `https://github.com/{owner}/{repo}` href. Reuses `canonicalRepoUrl` from `SourceFileLink.tsx` to avoid duplicating logic.
- [x] **AC-US4-04**: `DetailHeader.tsx` byline (lines 290-318) inserts `<RepoLink repoUrl={skill.repoUrl ?? null} />` between `<AuthorLink>` and `<SourceFileLink>`. Render order is author → repo → file. Existing `data-testid="detail-header-byline"` wrapper unchanged.
- [x] **AC-US4-05**: Skills with `repoUrl === null` (no resolvable provenance) render exactly the same byline as before this change — no visual regression. Skills with `repoUrl` populated render the new three-chip byline.

## Functional Requirements

### FR-001: Sidecar shape & validation
`readCopiedSkillSidecar(skillDir: string): { repoUrl: string | null; skillPath: string | null }`
- Reads `<skillDir>/.vskill-source.json`. Missing file → `{null, null}`.
- `JSON.parse` errors → `{null, null}`.
- `repoUrl` MUST match `/^https:\/\/github\.com\/[A-Za-z0-9][A-Za-z0-9-]{0,38}\/[A-Za-z0-9._-]+$/` (no trailing `.git` after canonicalization, no path segments beyond owner/repo). Failure → `{null, null}`.
- `skillPath` MAY be a non-empty string OR `null` (multi-skill repo per 0743 contract).
- Memoized per absolute `skillDir` for eval-server process lifetime. `resetCopiedSkillSidecarCache()` test hook clears the map.

### FR-002: `resolveSourceLink` precedence (final)
1. Read `vskill.lock`. If entry exists for `basename(skillDir)` or `basename(dirname(skillDir))`:
   - `entry.sourceRepoUrl` populated → return `{repoUrl: entry.sourceRepoUrl, skillPath: entry.sourceSkillPath ?? "SKILL.md"}` (existing 0737/0743).
   - Legacy `source: github:owner/repo` → existing logic at api-routes.ts:1058-1069.
2. NEW: `readCopiedSkillSidecar(skillDir)` returns non-null `repoUrl` → return that.
3. `detectAuthoredSourceLink(skillDir)` (existing 0770).

### FR-003: `transfer()` writes sidecar
After `copyOwnSkillFiltered` / `copyPluginFiltered` complete and BEFORE `emit({type:"copied"})`:
- Compute `sourceLink = resolveSourceLink(sourcePath, req.root)` (against the SOURCE).
- If `sourceLink.repoUrl` is non-null: `writeFileSync(join(destPath, ".vskill-source.json"), JSON.stringify(sourceLink, null, 2))`.
- Else: write nothing.

### FR-004: Sidecar filtered on copy
`copyOwnSkillFiltered` (scope-transfer.ts:101) at OWN-scope root: skip both `.vskill-meta.json` AND `.vskill-source.json`. `copyPluginFiltered` adds the same `.vskill-source.json` exclusion via `src/shared/copy-plugin-filtered.ts`.

### FR-005: Module extraction
New file `src/eval-server/source-link.ts` exports:
- `resolveSourceLink(skillDir, root)`
- `detectAuthoredSourceLink(skillDir)`
- `readCopiedSkillSidecar(skillDir)`
- `parseGithubRemote(remote)`
- `resetAuthoredSourceLinkCache()`
- `resetCopiedSkillSidecarCache()`

`src/eval-server/api-routes.ts` re-exports the public surface so existing imports keep working. `buildSkillMetadata` calls the new module.

### FR-006: `RepoLink.tsx` + byline integration
- New `src/eval-ui/src/components/RepoLink.tsx` exports `RepoLink({ repoUrl })` and `parseOwnerRepo(repoUrl)`.
- `parseOwnerRepo`: applies `canonicalRepoUrl` (imported from `SourceFileLink.tsx`), parses with `URL`, validates `hostname` is `github.com` or `www.github.com` (case-insensitive), extracts `owner`, `repo` (strip trailing `.git`), returns `null` on any failure.
- `DetailHeader.tsx` byline (lines 290-318): insert `<RepoLink repoUrl={skill.repoUrl ?? null} />` between `<AuthorLink>` and `<SourceFileLink>`.

### FR-007: No new server payload fields
`/api/skills` response shape is unchanged — `repoUrl` and `skillPath` already exist in `SkillMetadataFields` (api-routes.ts:557-581, populated at lines 1117-1118). The sidecar is read by the existing resolver path; no client-side changes required for the data path.

## Success Criteria

- Opening any "Copied (independent)" Personal-scope skill copied AFTER this ships in `vskill studio` shows author + repo + file links in the header byline, all clickable, all routing to the original GitHub source.
- Opening any lockfile-installed skill or authored-in-git skill ALSO shows the new repo chip (UI parity benefit applied to existing populated `repoUrl` data).
- Skills with no resolvable GitHub provenance (no lockfile, no sidecar, no github-origin git ancestor) render the same byline as before — no visual regression.
- Skills copied BEFORE this ships continue to render the same as before — no broken anchor, no orphaned chip.
- All 0737/0743/0770 tests pass unchanged.
- New unit tests cover the sidecar reader, the resolver precedence with sidecar, the scope-transfer sidecar write, the sidecar filtering on copy, and `RepoLink` rendering / null-handling / canonicalization.

## Out of Scope

- Retroactive backfill for skills copied before this ships — they keep current behavior until next re-copy.
- Editing or syncing back to the source repo from the copied skill.
- Non-`github.com` sources (gitlab, bitbucket, internal hosts) — repo chip returns null, file chip falls back to copy chip. Same `{null, null}` behavior as 0770 for non-github.
- Capturing source provenance for the CLI `installCopy()` path — already covered by lockfile receipts; this increment is Studio-copy + UI parity only.
- ONLINE/OFFLINE crawl status badge from verified-skill.com — that is a property of the marketplace, not the local studio.
- Category chip (e.g. "Marketing") in the header byline — `skill.category` already exists; rendering it is a separate UI parity task. Bundle in a follow-up increment if requested.
- Branch-aware blob URLs beyond `HEAD` — unchanged from 0770.

## Dependencies

- Existing `resolveSourceLink` chain at `src/eval-server/api-routes.ts:1026-1070` (introduced/refined by 0737/0743/0770) — must continue to honor lockfile precedence after extraction.
- Existing `SourceFileLink` component (introduced 0707, refined 0737/0743) — exports `canonicalRepoUrl` for reuse in `RepoLink`.
- Existing `AuthorLink` component (introduced 0707) — provides the visual style template `RepoLink` mirrors.
- Existing scope-transfer flow at `src/studio/lib/scope-transfer.ts:118` (`transfer()`) — unchanged copy semantics, only adds a post-copy sidecar write step.
- Existing `.vskill-meta.json` sidecar precedent — sets the convention `RepoLink`'s `.vskill-source.json` follows (filtered on copy, never propagated blindly).
