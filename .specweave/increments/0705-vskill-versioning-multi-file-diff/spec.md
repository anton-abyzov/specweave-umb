---
increment: 0705-vskill-versioning-multi-file-diff
title: Fix vskill versioning pipeline + GitHub-backed multi-file diff
type: feature
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix vskill versioning pipeline + GitHub-backed multi-file diff

## Overview

Fix republish flow (500 Prisma error + "Already verified" short-circuit), ghost `SkillVersion` rows from the admin rescan path, populate the unused `manifest` column, and add a GitHub-API-backed multi-file diff — both a platform endpoint + compare page and a new Windows-safe `vskill diff` CLI command. All items verified against production on 2026-04-24.

## Context

Live investigation (2026-04-24) of `verified-skill.com` revealed three compounding failures in the vskill publish/update pipeline that together make it impossible for authors to meaningfully update an already-published skill:

1. **Resubmit crashes with a raw Prisma 500.** `POST /api/v1/submissions` routes into `prisma.submission.create()` without catching the `(repoUrl, skillName)` unique constraint (P2002). Reproduced on `anton-abyzov/vskill/survey-passing` and `anton-abyzov/vskill/scout` with CLI `0.5.79` against production.
2. **`upsertSubmission` short-circuits every republish of a `PUBLISHED` skill.** Even when the unique constraint is caught correctly, the existing row's state is `PUBLISHED` and the function returns `{ kind: "verified" }` — the CLI then prints "Already verified! Skill is up-to-date" and exits 0 even when the author just pushed new content to `origin/main`. There is no re-scan trigger.
3. **The admin rescan-published path writes ghost `SkillVersion` rows** with `content=""`, `contentHash=""`, `gitSha=""`. Live evidence: `scout` v1.0.1 has empty content and renders as `+0 / −311` on the compare UI (user screenshot 2026-04-24). `appstore` v1.0.0 and v1.0.1 have identical content hashes but `diffSummary: "Content updated"` on v1.0.1.

On top of these bugs, the version-compare UI renders only SKILL.md diffs — because the `manifest` column (declared in schema as per-file `[{path, sha256, size}]`) is never written by `publishSkill()`. There is no R2/blob storage for script/reference bytes, and `gitSha` is frequently empty or the literal string `"latest"`. The LCS diff in `src/lib/diff.ts` works correctly — it's the data feeding it that's broken.

The GitHub compare path is viable: `GET https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}` was verified live and returned 16 files with full patches for the scout commit `4f2285d...71a9132` (a real 4-file change: `.gitignore`, `SKILL.md`, `evals/benchmark.json`, `evals/evals.json`, +590/−8 lines).

## Goals

- Fix republish so authors can update a published skill and see a new `SkillVersion` row with correct `content`, `contentHash`, `gitSha`, and `manifest`.
- Stop ghost rows. Admin rescan either skips row creation when content is unchanged, or fetches content from GitHub at the rescan SHA and populates all fields.
- Show real multi-file diffs in the browser and CLI by delegating to GitHub's `/compare` API when `gitSha` is present on both versions.
- Expose a local equivalent — a `vskill diff` command that hits the same compare endpoint, Windows-safe.
- Populate the `manifest` column on every new `SkillVersion`.

## Non-Goals

- Storing script/reference bytes in R2 or any blob store. GitHub is the authoritative source; we only need SHAs.
- Windows compatibility fixes for `vskill install` / `update` / `studio` (shell-outs, `which` vs `where`, symlink fallback). Tracked separately. `vskill submit` and the new `vskill diff` MUST be Windows-safe; the rest is out of scope here.
- Replacing the existing LCS diff. It stays as the fallback for (a) non-GitHub hosts, (b) legacy rows with missing `gitSha`, (c) offline/rate-limited scenarios.

## User Stories

### US-001: Author republishes an updated skill
**Project**: vskill-platform

**As a** skill author whose skill is already `PUBLISHED`
**I want** to edit SKILL.md (or any file under my skill's directory) and run `vskill submit <repo> --skill <name>`
**So that** the registry sees my change, bumps the version, creates a new `SkillVersion` row with real content, and makes the update available to consumers.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `POST /api/v1/submissions` for an existing (`repoUrl`, `skillName`) pair does NOT return a 500 Prisma error. Instead it returns a clean 200 or 409 with a stable response shape.
- [x] **AC-US1-02**: When the new `contentHash` (SHA-256 of SKILL.md fetched from GitHub) differs from the latest `SkillVersion.contentHash`, the submission is re-enqueued for scanning; `upsertSubmission` does NOT return `{kind:"verified"}`.
- [x] **AC-US1-03**: After the scan completes, a new `SkillVersion` row exists with correct `content`, `contentHash`, `gitSha` (real commit SHA, not `"latest"` or `""`), `manifest` (non-null JSON), `treeHash`, and a server-bumped `version` (patch bump under `versioningMode="auto"`, frontmatter-respecting under `"author"`).
- [x] **AC-US1-04**: The CLI output on a successful republish shows the new version number, not "Already verified!".
- [x] **AC-US1-05**: When the new `contentHash` matches the latest `SkillVersion.contentHash`, the API returns `{kind:"verified"}` without creating a new row and without error — and the CLI prints a message that reflects "no changes detected".

### US-002: Admin rescans a published skill without creating ghost rows
**Project**: vskill-platform

**As a** platform operator
**I want** `POST /api/v1/admin/rescan-published` to only create a new `SkillVersion` when the underlying content has actually changed
**So that** the versions history remains an honest log and the compare UI never renders a row with empty content.

**Acceptance Criteria**:
- [x] **AC-US2-01**: When the rescan finds the same `contentHash` as the latest `SkillVersion`, no new row is created. The existing row is updated in place for cert tier/score only.
- [x] **AC-US2-02**: When the rescan finds a different `contentHash`, the new row is written with `content`, `contentHash`, `gitSha`, and `manifest` all populated — never empty strings.
- [x] **AC-US2-03**: An idempotent backfill script identifies existing `SkillVersion` rows with empty `content` or `contentHash` and either deletes them (if a sibling row with identical metadata exists) or repopulates from GitHub when `gitSha` is non-empty. Dry-run mode required (`--dry-run`).

### US-003: Browser compare page shows multi-file diffs
**Project**: vskill-platform

**As a** user browsing a skill's version history
**I want** to see per-file diffs across the entire skill bundle (SKILL.md + scripts + references + evals)
**So that** I can evaluate what actually changed between versions — not just SKILL.md.

**Acceptance Criteria**:
- [x] **AC-US3-01**: `GET /api/v1/skills/{owner}/{repo}/{skill}/versions/compare?from=X&to=Y` returns `{source: "github" | "local-content", baseSha, headSha, files: [{filename, status, additions, deletions, patch}], githubCompareUrl}`. `source: "github"` when both versions have valid non-empty `gitSha` AND the repo host is GitHub.
- [x] **AC-US3-02**: The endpoint filters `files[]` by the skill's `skillPath` so unrelated changes in the parent repo are excluded.
- [x] **AC-US3-03**: The compare page at `/skills/{owner}/{repo}/{skill}/versions/compare` renders a file tree (left) + selected-file unified/side-by-side diff (right), with file-level `+N / −M` counts. The existing viewMode toggle is preserved per file.
- [x] **AC-US3-04**: A "View on GitHub" link is visible when `source === "github"`, deep-linking to the GitHub compare URL.
- [x] **AC-US3-05**: When `gitSha` is missing on either version or the repo host is not GitHub, the page falls back to the existing LCS SKILL.md-only diff with a visible banner: "Showing SKILL.md diff only — full bundle diff unavailable for this version."
- [x] **AC-US3-06**: Integration test uses the real scout commit `4f2285d...71a9132` (4 files, +590/−8 lines) as the golden case. Mocked GitHub response → assert `files.length === 4` and `files[0].patch` includes at least one known substring from the real diff.

### US-004: CLI diff command works on all operating systems
**Project**: vskill

**As a** user on macOS, Linux, or Windows
**I want** to run `vskill diff <skill> <fromVersion> <toVersion>` in my terminal
**So that** I can review what changed between two published versions without opening a browser.

**Acceptance Criteria**:
- [x] **AC-US4-01**: `vskill diff <skill> <from> <to>` calls the compare endpoint and prints a unified diff per file to stdout, color-coded (+ green, − red, context grey). Exits 0 on success, 1 on API error.
- [x] **AC-US4-02**: `--stat` prints a file-level summary: `{filename}  +{additions}  −{deletions}` with totals at the bottom.
- [x] **AC-US4-03**: `--json` prints the raw API response to stdout for programmatic consumption. No colors, no TTY-only control sequences.
- [x] **AC-US4-04**: `--files <pattern>` filters the output to files matching a glob pattern (e.g., `"scripts/**"`).
- [x] **AC-US4-05**: Command runs correctly in Windows PowerShell and cmd.exe — no `which`, no `&&/~/2>/dev/null` shell-isms, no `lsof`, no symlinks. Verified via CI job running on `windows-latest`.
- [x] **AC-US4-06**: `vskill diff --help` documents all flags and exits 0.

### US-005: Version detail API surfaces manifest + gitSha
**Project**: vskill-platform

**As a** consumer of the version API
**I want** `/api/v1/skills/{owner}/{repo}/{skill}/versions/{version}` to return `treeHash`, `manifest`, and `gitSha`
**So that** clients can compute what-changed summaries without a full compare round-trip.

**Acceptance Criteria**:
- [x] **AC-US5-01**: The endpoint's `select:` includes `treeHash`, `manifest`, `gitSha` in addition to existing fields. Response shape remains backward-compatible.
- [x] **AC-US5-02**: `manifest` is returned as a parsed JSON value (array of `{path, sha256, size}`), not a stringified JSON.
- [x] **AC-US5-03**: When `manifest` is null (legacy row), the response sets `manifest: null` — never a partially-populated array.

## Out of Scope (Noted Here for Traceability)

| Concern | Where It's Handled |
|---|---|
| Windows fixes for `vskill install`/`update`/`studio` (`which`, hardcoded `/`, symlinks, `lsof`) | Future increment — not blocking for versioning pipeline |
| Storing script/reference bytes in R2 | Explicitly rejected — GitHub is authoritative |
| Non-GitHub host support (GitLab, Bitbucket) | LCS fallback covers it; adding host-specific compare APIs is a future increment |
| Richer release notes / changelog UI | `SkillVersion.releaseNotes` column exists; UI exposure is a future increment |

## Success Metrics

- After rollout: 0 occurrences of `Unique constraint failed on the fields: (repoUrl,skillName)` in CF Worker logs over a 7-day window.
- After rollout: 0 new `SkillVersion` rows with `content=""` OR `contentHash=""` created by the admin rescan path.
- After backfill: 0 `SkillVersion` rows with `content=""` AND `gitSha!=""` in the DB.
- 100% of submissions where `contentHash` changed produce a new `SkillVersion` row with real content (verified via scheduled probe test in CI).

## References

- Live investigation report (this session, 2026-04-24).
- User screenshot: `scout` v1.0.0→v1.0.1 compare showing `+0 / −311`.
- Prisma schema: `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma:360-434`.
- Publish code: `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts:337-356`.
- Upsert code: `repositories/anton-abyzov/vskill-platform/src/lib/submission/upsert.ts:101-120`.
- Submission route: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts:719`.
- Compare UI: `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/versions/compare/page.tsx`.
- Golden test commit: `anton-abyzov/vskill@71a9132` (parent `4f2285d`).
- GitHub compare API verified: `GET https://api.github.com/repos/anton-abyzov/vskill/compare/4f2285d...71a9132` → 200, 16 files with patches.
