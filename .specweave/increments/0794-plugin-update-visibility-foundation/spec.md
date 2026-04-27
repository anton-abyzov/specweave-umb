---
increment: 0794-plugin-update-visibility-foundation
title: "Plugin Update Visibility & Version Alignment Foundation"
type: bug
priority: P1
status: planned
created: 2026-04-27
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Plugin Update Visibility & Version Alignment Foundation

## Overview

Three independent update-tracking systems coexist in this umbrella today and silently disagree:

1. **Claude Code plugin marketplace** — `marketplace.json` (per-repo) is consumed by `~/.claude/plugins/installed_plugins.json` on the user's machine. Claude Code surfaces "update available" only when these two version strings differ.
2. **vskill registry** — Cloudflare Worker (`verified-skill.com`) backed by KV + Prisma `SkillVersion`, polled by `vskill outdated`. Source of truth for cross-tool skill distribution.
3. **npm package** — `specweave/package.json` shipped as `npm i -g specweave`, checked by `installation-health-checker.ts`.

The `sw` Claude plugin currently has **three different version strings** for the same artifact:

| File | Version | Last bumped |
|---|---|---|
| `repositories/anton-abyzov/specweave/plugins/specweave/.claude-plugin/plugin.json` | `1.0.0` | frozen since 2026-04-15 |
| `repositories/anton-abyzov/specweave/.claude-plugin/marketplace.json` | `1.0.323` | bumped on every release |
| `repositories/anton-abyzov/specweave/package.json` | `1.0.581` | bumped on every release |

Claude Code reads `1.0.0` from the user's `installed_plugins.json` and never sees an update. **47 of 50** `plugins/specweave/skills/*/SKILL.md` files have **no `version:` frontmatter** at all. `specweave doctor` only checks the CLI npm version, so neither stale plugin nor stale skill is reported. `vskill outdated` walks `vskill.lock` only, so locally authored skills bypass it. Finally, `vskill submit` phantom-bumps the registry version when content is unchanged but never writes the new version back to the source `SKILL.md`, producing a fake "update available" right after publish.

This increment **bridges** (NOT unifies) the two existing update systems by:

- Hot-fixing the `plugin.json` lockstep bump and enforcing it in CI
- Stamping every plugin skill with a `version:` field
- Closing the vskill phantom-bump and version-write-back gap
- Adding two new `specweave doctor` checkers (plugin currency + skill currency)
- Tracking source-origin (locally authored) skills in `vskill outdated`

A separate Phase 2 increment (out of scope here) will add a session-start banner that surfaces these new doctor signals proactively.

## User Stories

### US-001: Plugin.json version stays in lockstep with marketplace.json + package.json (P1)
**Project**: specweave

**As a** SpecWeave maintainer publishing a new release
**I want** `plugin.json`, `marketplace.json`, and `package.json` to bump in lockstep automatically, with CI enforcing the alignment
**So that** Claude Code users receive update notifications instead of being silently pinned to `1.0.0`

**Background**: `plugin.json` has been frozen at `1.0.0` since 2026-04-15 while `marketplace.json` reached `1.0.323` and `package.json` reached `1.0.581`. Because Claude Code compares `installed_plugins.json` (which sources from `plugin.json`) to `marketplace.json`, users see "no updates" forever.

**Affected files**:
- `repositories/anton-abyzov/specweave/scripts/build/bump-version.sh` (extend to bump all three)
- `repositories/anton-abyzov/specweave/plugins/specweave/.claude-plugin/plugin.json` (one-shot hotfix to current `package.json` version)
- `repositories/anton-abyzov/specweave/scripts/validation/validate-versions.cjs` (NEW — CI lint)
- `repositories/anton-abyzov/specweave/.github/workflows/*.yml` (wire validate-versions into CI)

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Running `scripts/build/bump-version.sh patch` updates `package.json`, `marketplace.json`, AND `plugin.json` to the same SemVer string in a single atomic operation. Existing behavior for `package.json` + `marketplace.json` is preserved.
- [ ] **AC-US1-02**: A one-shot commit hot-fixes `plugins/specweave/.claude-plugin/plugin.json` from `1.0.0` to the current `package.json` version (≥ `1.0.581`). Commit message references this increment.
- [ ] **AC-US1-03**: `node scripts/validation/validate-versions.cjs` exits `0` when all three versions match, exits non-zero with a unified diff-style error message naming the offending file(s) when they drift.
- [ ] **AC-US1-04**: GitHub Actions runs `validate-versions.cjs` on every push and PR. The job is required for merge to `main`. Drift PRs fail CI within 60 seconds.
- [ ] **AC-US1-05**: After release, `~/.claude/plugins/installed_plugins.json` (after a `claude /plugin/update` or `specweave refresh-plugins`) reflects the new version, and `claude /plugin/list` shows "update available" before refresh.

**Test Plan**:
- Unit: `validate-versions.cjs` against fixtures (aligned, drifted-2-of-3, drifted-3-of-3, missing-file)
- Integration: run `bump-version.sh patch` in a tmp clone, assert all three files match
- E2E (manual gate, see Manual Verification): publish a dot-release, then run `claude /plugin/update sw@specweave` and verify the new version appears

---

### US-002a: vskill rejects phantom-bump publishes (contentHash gate) (P1)
**Project**: vskill-platform

**As a** skill author running `vskill skill publish` without changing content
**I want** the registry to refuse the publish with a clear "no changes detected" message
**So that** unchanged content does not advance the version, eliminating phantom "update available" signals downstream

**Background**: `check-updates/route.ts:111-347` already computes `contentHash` per `SkillVersion`. The publish path (`POST /api/v1/skills/publish` — same Worker) does NOT compare the incoming `contentHash` to the previous version's hash before allocating a new version row, so identical content silently bumps `1.0.2 → 1.0.3`. See memory `project_skill_version_publish_desync.md`.

**Affected files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/check-updates/route.ts` (helper extraction; lines 111–347 contain the existing hash computation)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/publish/route.ts` (add gate)
- `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` (no schema change; reuse `SkillVersion.contentHash`)

**Acceptance Criteria**:
- [ ] **AC-US2a-01**: `POST /api/v1/skills/publish` computes `contentHash` from the request payload using the SAME normalization rules as `check-updates/route.ts` (frontmatter-stripped, whitespace-normalized, sorted keys).
- [ ] **AC-US2a-02**: When the computed `contentHash` matches the latest `SkillVersion.contentHash` for the same `skillId + namespace`, the API returns HTTP `200` with body `{ status: "skipped", reason: "no changes detected", version: "<existing>" }` and does NOT insert a new `SkillVersion` row, does NOT increment KV cache version, does NOT bump certTier counters.
- [ ] **AC-US2a-03**: When `contentHash` differs, the existing publish path runs unchanged (new `SkillVersion` inserted, KV cache invalidated, version bump applied).
- [ ] **AC-US2a-04**: Rate-limit headers (`X-RateLimit-*`) and the existing 600 req/hr quota are unaffected. A skipped publish counts the same as a successful publish for rate-limiting (prevents abuse loops).
- [ ] **AC-US2a-05**: Database invariant (verified via integration test): for any (skillId, namespace), no two `SkillVersion` rows share the same `contentHash`.

**Test Plan**:
- Unit: contentHash normalization parity with check-updates helper (same input → same hash)
- Integration: publish identical payload twice, assert second response is `skipped` and no new DB row
- Integration: publish with a 1-char body change, assert version bumps and new row inserted

---

### US-002b: vskill writes registry version back to source SKILL.md after publish (P1)
**Project**: vskill

**As a** skill author who just ran `vskill skill publish` from my source repo
**I want** the new registry version written back into my source `SKILL.md` frontmatter
**So that** my source matches what the registry shows, and the next `vskill outdated` does not flag my own freshly published skill as out of date

**Background**: `submit.ts` parses the local `SKILL.md`, sends it to the registry, and on success prints the new version to stdout — but never writes that version back to the file. The next `outdated` poll sees source `version: 1.0.2` against registry `1.0.3` and lights up "update available." See memory `project_skill_version_publish_desync.md`.

**Affected files**:
- `repositories/anton-abyzov/vskill/src/commands/submit.ts` (post-publish writeback; preserve frontmatter ordering and any non-version fields)
- `repositories/anton-abyzov/vskill/src/lib/frontmatter.ts` (or equivalent — reuse existing parser/writer; do NOT introduce a second YAML library)

**Acceptance Criteria**:
- [ ] **AC-US2b-01**: After a successful publish (HTTP 2xx with `status: "published"` and a new version number), `submit.ts` rewrites the source `SKILL.md` frontmatter `version:` field to the registry version. All other frontmatter fields and ordering are preserved byte-for-byte where possible.
- [ ] **AC-US2b-02**: When the registry returns `status: "skipped"` (US-002a path), `submit.ts` does NOT modify the file and prints `"No changes — version unchanged at <X>"` to stdout.
- [ ] **AC-US2b-03**: If `SKILL.md` had no `version:` field, `submit.ts` adds one positioned after `description:` (or at end of frontmatter if `description:` absent).
- [ ] **AC-US2b-04**: `submit.ts` exits non-zero and leaves `SKILL.md` untouched if the writeback would produce invalid YAML (defensive parse-then-serialize round-trip check).
- [ ] **AC-US2b-05**: After `vskill skill publish` succeeds, immediately running `vskill outdated` in the same directory reports the skill as up to date.

**Test Plan**:
- Unit: frontmatter writeback preserves field order and quoting style across fixtures
- Integration: publish → read source file → assert version matches registry response
- Integration: publish "skipped" → assert source file mtime unchanged

---

### US-003: Every plugin skill has a version frontmatter field (P1)
**Project**: specweave

**As a** SpecWeave user inspecting installed plugin skills
**I want** every `plugins/specweave/skills/*/SKILL.md` to declare a `version:` in frontmatter
**So that** version-based update tooling has a value to compare against, and CI prevents the field from regressing

**Background**: 47 of 50 `SKILL.md` files in `plugins/specweave/skills/` have no `version:` frontmatter. The 3 that do exist by accident, not by convention.

**Affected files**:
- `repositories/anton-abyzov/specweave/plugins/specweave/skills/*/SKILL.md` (47 files — initial stamp)
- `repositories/anton-abyzov/specweave/scripts/validation/validate-skill-versions.cjs` (NEW — CI lint)
- `repositories/anton-abyzov/specweave/.github/workflows/*.yml` (wire lint into CI)

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Every `plugins/specweave/skills/*/SKILL.md` (currently 50 files) has a `version:` field in YAML frontmatter. Initial value is `1.0.0` for the 47 currently missing it; the 3 with existing values are left untouched.
- [ ] **AC-US3-02**: `version:` value is a valid SemVer string (`MAJOR.MINOR.PATCH`, optionally with prerelease/build per SemVer 2.0.0). Validator rejects bare integers, dates, or empty strings.
- [ ] **AC-US3-03**: `validate-skill-versions.cjs` walks `plugins/specweave/skills/*/SKILL.md`, exits non-zero listing any file missing or with malformed `version:`. Output names the offending file paths, one per line.
- [ ] **AC-US3-04**: GitHub Actions runs `validate-skill-versions.cjs` on every push and PR. Job is required for merge to `main`.
- [ ] **AC-US3-05**: Stamping is idempotent — re-running the bulk stamp script does NOT modify any file that already has a valid `version:`.

**Test Plan**:
- Unit: validator against fixtures (missing field, malformed value, valid SemVer, prerelease, build metadata)
- Integration: dry-run stamp script over the 50 files, assert exactly 47 modifications proposed; apply, then validator passes

---

### US-004: specweave doctor reports plugin currency (P1)
**Project**: specweave

**As a** developer running `specweave doctor` to diagnose my install
**I want** a "Plugin Currency" check that compares my installed Claude plugin versions against the marketplace
**So that** I know when to run `specweave refresh-plugins` or `claude /plugin/update`

**Background**: `installation-health-checker.ts:628-718` only checks the npm CLI version. There is no signal for stale Claude plugins. `~/.claude/plugins/installed_plugins.json` exposes installed versions; `marketplace.json` (fetched from the SpecWeave repo or local clone if present) exposes available versions.

**Affected files**:
- `repositories/anton-abyzov/specweave/src/core/doctor/checkers/plugin-currency-checker.ts` (NEW)
- `repositories/anton-abyzov/specweave/src/core/doctor/checkers/index.ts` (register new checker)
- `repositories/anton-abyzov/specweave/src/core/doctor/types.ts` (extend `CheckResult` only if needed; reuse existing shape)

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `specweave doctor` (text mode) prints a row labeled `"Plugin Currency"` showing one of: `pass` (all plugins current), `warn` (one or more outdated), or `skip` (no `installed_plugins.json` found, e.g., user is not on Claude Code).
- [ ] **AC-US4-02**: When `warn`, the output lists each outdated plugin as `<name>@<source>: installed=<X>, available=<Y>` and includes a `fixSuggestion` line: `"Run: specweave refresh-plugins"`.
- [ ] **AC-US4-03**: `specweave doctor --json` includes a `pluginCurrency` key with shape `{ status: "pass"|"warn"|"skip", outdated: [{ name, source, installed, available }], fixSuggestion?: string }`.
- [ ] **AC-US4-04**: When `~/.claude/plugins/installed_plugins.json` is missing or unreadable, the check returns `skip` (not `fail`), with a `reason` explaining why. `specweave doctor` exit code is unchanged by a `skip`.
- [ ] **AC-US4-05**: When the marketplace fetch fails (network error, 5xx), the check returns `warn` with `reason: "unable to verify"`, NOT `fail`. Doctor continues to other checks.
- [ ] **AC-US4-06**: Total wall-clock added to `specweave doctor` by this check is ≤500 ms in the warm-cache case and ≤2000 ms cold (KV miss). Measured via existing doctor timing harness.

**Test Plan**:
- Unit: checker against fixture pairs (all-current, one-outdated, missing-installed-file, malformed-marketplace, network-fail)
- Integration: end-to-end `specweave doctor` against a tmp HOME with seeded `installed_plugins.json`
- Performance: assert checker overhead under thresholds via timing harness

---

### US-005: specweave doctor reports skill currency via vskill outdated (P1)
**Project**: specweave

**As a** developer using vskill-published skills in my project
**I want** `specweave doctor` to surface vskill outdated results as a check row
**So that** I see all update signals (CLI, plugin, skill) in one command without having to remember `vskill outdated`

**Background**: `vskill outdated --json` already exists and is KV-cached (5 min). Embedding its output in `specweave doctor` is a thin shell-out, not a re-implementation.

**Affected files**:
- `repositories/anton-abyzov/specweave/src/core/doctor/checkers/skill-currency-checker.ts` (NEW)
- `repositories/anton-abyzov/specweave/src/core/doctor/checkers/index.ts` (register)

**Acceptance Criteria**:
- [ ] **AC-US5-01**: `specweave doctor` prints a row labeled `"Skill Currency"` showing one of: `pass` (all skills current), `warn` (outdated skills present), or `skip` (no `vskill.lock` in CWD or `vskill` binary not on PATH).
- [ ] **AC-US5-02**: When `warn`, output lists each outdated skill as `<namespace>/<name>: installed=<X>, available=<Y>` (max 10 lines, truncated with `"… +N more"`). `fixSuggestion`: `"Run: vskill update"`.
- [ ] **AC-US5-03**: `specweave doctor --json` includes a `skillCurrency` key mirroring the structure of `pluginCurrency` from US-004.
- [ ] **AC-US5-04**: When `vskill` is not on PATH, the check returns `skip` with `reason: "vskill CLI not installed"`. No fail.
- [ ] **AC-US5-05**: When `vskill outdated --json` exits non-zero or returns malformed JSON, the check returns `warn` with `reason: "unable to verify"`. Stderr from vskill is captured to `reason` (truncated to 200 chars).
- [ ] **AC-US5-06**: Total wall-clock added to `specweave doctor` by this check is ≤500 ms warm, ≤2000 ms cold.

**Test Plan**:
- Unit: parse-vskill-output helper against captured `vskill outdated --json` fixtures (current, outdated, error)
- Integration: end-to-end `specweave doctor` with a stubbed `vskill` binary on PATH (shell wrapper script)
- Negative: PATH without vskill → assert `skip`, not `fail`

---

### US-006: vskill outdated tracks locally-authored (source-origin) skills (P2)
**Project**: vskill

**As a** skill author who has both consumed and published skills in a project
**I want** `vskill outdated` to also poll my own published skills (not just lockfile entries)
**So that** I see when my source `SKILL.md` is behind the registry version (e.g., after another machine published a bump)

**Background**: `outdated.ts:53-110` walks `vskill.lock` only. Skills authored locally and published by the same user are NOT in the lockfile (they are sources, not installs), so their update status is invisible. Memory: `project_vskill_source_origin_update_tracking.md`.

**Affected files**:
- `repositories/anton-abyzov/vskill/src/commands/outdated.ts` (extend poll set)
- `repositories/anton-abyzov/vskill/src/lockfile.ts` OR new `vskill/src/authored.ts` (track locally authored skill paths; one approach to be chosen during plan phase)

**Acceptance Criteria**:
- [ ] **AC-US6-01**: After `vskill skill publish` succeeds, the source path is recorded as a "locally authored" skill (mechanism: a sibling `vskill.authored.json` or extending `vskill.lock` with a separate section — chosen during planning, MUST NOT mix with installed-skill entries).
- [ ] **AC-US6-02**: `vskill outdated` polls both lockfile-installed and locally-authored skills. Locally-authored skills are flagged distinctly in output (e.g., prefix `[authored]`).
- [ ] **AC-US6-03**: A locally-authored skill where source `SKILL.md` version equals registry version is reported as up to date (no false positives).
- [ ] **AC-US6-04**: A locally-authored skill where the source file no longer exists (deleted, moved) is removed from the authored list automatically on next `outdated` run, with a one-line stderr notice.
- [ ] **AC-US6-05**: A locally-authored skill that has never been published to the registry is silently skipped (no error, no warn). The case is rare — author published once, then deleted from registry — and is not worth surfacing.
- [ ] **AC-US6-06**: `vskill.authored.json` (or equivalent) is `.gitignore`-friendly (added to default `.gitignore` snippets that `vskill init` writes); contains no secrets; safe to delete (regenerated on next publish).

**Test Plan**:
- Unit: authored-list add/remove on publish/delete cycles
- Integration: publish skill A, run outdated → up to date; bump registry via direct API call, run outdated → flagged outdated with `[authored]` prefix
- Edge: source file deleted between publish and outdated → entry pruned, no crash

---

## Functional Requirements

### FR-001: Three-way version alignment is the contract for `sw@specweave`

`plugin.json.version`, `marketplace.json.plugins[name=sw].version`, and `package.json.version` MUST be byte-equal SemVer strings. CI enforces. The bump tool is the only sanctioned writer.

### FR-002: contentHash is the publish authority

The vskill registry rejects new `SkillVersion` rows whose `contentHash` matches the previous version. ContentHash normalization rules MUST be identical between `check-updates` and `publish` paths (extract to a shared helper).

### FR-003: Source SKILL.md is the version mirror

After successful publish, source `SKILL.md` frontmatter `version:` equals the registry value. After a `skipped` publish, source is unchanged.

### FR-004: doctor checks are read-only and additive

Both new checkers (`plugin-currency-checker`, `skill-currency-checker`) MUST be read-only. Failures are `warn` or `skip`, never `fail`. They MUST NOT change `specweave doctor`'s exit code semantics.

### FR-005: Graceful degradation everywhere

Missing `installed_plugins.json`, missing `vskill.lock`, missing `vskill` binary, network errors, malformed remote responses — every failure mode reports `skip` or `warn` with a human-readable `reason`. None blocks doctor from completing.

### FR-006: No new external services

This increment uses ONLY existing infrastructure: Cloudflare Worker, KV, Prisma, GitHub Actions, npm. No new endpoints, no new databases, no new dashboards.

## Success Criteria

| Metric | Target | Measurement |
|---|---|---|
| Plugin version drift (production) | 0 occurrences | CI green for 30 days post-merge |
| Plugin SKILL.md files missing `version:` | 0 / 50 | `validate-skill-versions.cjs` exit 0 |
| Phantom-bump publishes (vskill) | 0 / week | DB query: `SkillVersion` rows with same `contentHash` per (skillId, namespace) |
| `specweave doctor` time impact | <500ms warm, <2s cold added | Doctor timing harness |
| User-visible "update available" lag for `sw@specweave` | <24h after release | manual probe weekly |
| Source-skill `version:` desync after publish | 0 occurrences | Integration test in CI |

## Manual Verification Gates

The following require human verification (per CLAUDE.md):
- After release, run `claude /plugin/list` — verify `sw@specweave` shows the new version (or "update available" before refresh).
- Run `vskill skill publish` twice in a row on unchanged content — verify second run reports `"No changes — version unchanged at <X>"` and source `SKILL.md` is byte-identical between runs.
- Run `specweave doctor` on a fresh install with `vskill` not on PATH — verify "Skill Currency" reports `skip`, doctor exits 0.

## Out of Scope

- **SSE / push notifications to CLI** — CLI is short-lived; wrong transport. Polling-on-demand is correct.
- **Unified marketplace** (one registry for both Claude plugins and vskill skills) — massive cost, breaks installs.
- **Cross-marketplace conflict resolver** (same skill installed via both Claude plugin AND vskill) — out of scope; doctor will report both versions side-by-side without auto-resolving.
- **Session-start banner** surfacing doctor signals proactively — Phase 2 increment, depends on this foundation landing.
- **Web dashboard for plugin/skill currency** — not requested.
- **Telemetry** of plugin install state to verified-skill.com — privacy-sensitive, deferred.
- **Backfilling per-skill versions for non-`sw` plugins** — only `plugins/specweave/skills/*/SKILL.md` in scope.

## Dependencies

- **Existing**: vskill-platform `check-updates` API (already deployed); `vskill outdated --json` (already shipped); `installation-health-checker.ts` checker pattern (existing reference impl); GitHub Actions runner (already configured).
- **None new**: this increment introduces no new external dependencies.
- **Sibling memories** that informed this spec:
  - `project_vskill_version_confusion.md` — three version concepts (plugin / skill / CLI) must be labeled distinctly
  - `project_skill_version_publish_desync.md` — phantom-bump root cause
  - `project_vskill_source_origin_update_tracking.md` — locally-authored skill gap

## Cross-Project Coordination Notes

This increment touches three child repos. Suggested merge order (to be confirmed during planning):

1. `vskill-platform` (US-002a) — server-side gate must land first so `vskill` clients see the new behavior
2. `vskill` (US-002b, US-006) — once server gate is live, client writeback + authored tracking are safe
3. `specweave` (US-001, US-003, US-004, US-005) — last; its doctor checkers depend on `vskill outdated` behavior from step 2 being stable

Each project's PR is independent and gets its own CI run. No atomic cross-repo merge required.
