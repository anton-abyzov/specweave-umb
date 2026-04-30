---
increment: 0813-scanner-webhook-path-filter-and-frontmatter-bump
title: "Webhook path-filter + frontmatter-driven version bumps"
type: bug
priority: P2
status: planned
created: 2026-04-30
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Webhook path-filter + frontmatter-driven version bumps

## Overview

Two follow-ups carried forward from increment 0811 plus a one-shot cleanup that has already been executed via direct SQL:

1. **Webhook path-filter (defense-in-depth).** The GitHub webhook fast-path currently fans out a scan job to *every* tracked skill in the pushed repo, regardless of whether the commit touched that skill. With repos like `anton-abyzov/vskill` carrying 67+ tracked skills, a single unrelated commit becomes 67 wasted enqueues. The 0811 content-hash gate makes those scans no-op at the registry layer, but the network round-trip + queue write are still spent. Filtering at webhook time eliminates the waste.
2. **Frontmatter-driven version bumps.** Today the scanner uses `deriveNextVersion(skill.currentVersion)` which is a blind semver patch bump (`x.y.z → x.y.(z+1)`) regardless of what the author wrote in `SKILL.md`. This produces the desync the user observed: registry advances, local SKILL.md frontmatter doesn't. Switching to "registry follows the frontmatter" puts authors in full control: bump `version:` in your SKILL.md to publish a new registry version. Don't bump → registry stays put, even if content changed.
3. **Residual phantom-row cleanup (already executed).** 750 `sha256:pending:` rows in 171 skills survived 0811's curl-based mass backfill because the recorded `gitSha` no longer has a fetchable `SKILL.md` (renamed/moved/deleted at source). Direct SQL was used to (a) delete pending rows for 97 skills that have at least one real-hash row remaining, and (b) for 82 "zero real" skills, keep the newest pending row, mark its `contentHash` as the sentinel `sha256:legacy:<gitSha>` (distinct from `pending:` so the live scanner doesn't try to recompute it on every run), delete the rest. Result: **0 `sha256:pending:` rows remain across the entire registry**.

## Problem

- **Webhook waste**: a push to `anton-abyzov/vskill` with a one-line agents.json regen enqueues a `scan-high` job for every tracked skill in that repo. Each consumer-side scan now correctly no-ops via 0811's content-hash gate, but the queue absorbs N redundant messages.
- **Author intent vs registry version**: with `deriveNextVersion`, the author has no control over registry version numbers. If they ship a real change, the registry blindly increments patch — even if the author intended a minor bump. Worse, the local SKILL.md frontmatter never reflects what the registry decided. Studio installs see "v1.0.0 (you) vs v1.0.1 (registry)" and prompt update — surprising the author who just authored both.
- **Residual phantoms**: the 750 leftover `sha256:pending:` rows confuse anyone querying the DB ("are these still bugs?") and the live scanner would keep trying to compare against them on every cron tick (always failing the equality check, doing pointless work).

## User Stories

### US-001: Webhook path-filter (P2)
**Project**: vskill-platform

**As an** ops operator
**I want** the GitHub webhook to enqueue a scan ONLY for skills whose path was actually modified in the push
**So that** an unrelated commit doesn't fan out N redundant queue messages

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `src/app/api/v1/webhooks/github/route.ts` parses `commits[].added/removed/modified` from the push payload and computes the union as a `Set<string>` of changed paths.
- [ ] **AC-US1-02**: For each tracked skill matching `repoUrl + branch`, compute the skill's directory (everything before `/SKILL.md` in `skill.skillPath`, defaulting to "" — the repo root — when `skillPath` is null/empty). The skill is "touched" if any changed path startsWith that directory.
- [ ] **AC-US1-03**: When `commits[]` is missing OR empty (e.g., huge-push truncation, or `commits` field omitted by GitHub), fall back to the existing behavior — enqueue all matching skills. This preserves correctness on the rare edge case.
- [ ] **AC-US1-04**: When `skill.skillPath` is null/empty (legacy rows), the skill's directory is `""` so any changed path matches → enqueue. Defensive default.
- [ ] **AC-US1-05**: Emit metric `webhook.skipped.path-mismatch` with skillId for each skill that matched repo+branch but did NOT match a changed path. Returned response includes `enqueued: <N>` (matches kept) AND `skipped: <M>` (matches filtered out).
- [ ] **AC-US1-06**: Vitest unit tests cover: (a) push touches one of three tracked skills → 1 enqueue + 2 skips, (b) push touches none of three tracked skills → 0 enqueues + 3 skips, (c) `commits[]` missing → fall back to enqueue-all, (d) `skillPath` null → enqueue, (e) the metric is emitted with the correct skillIds.

---

### US-002: Frontmatter-driven version bumps (P2)
**Project**: vskill-platform

**As an** author
**I want** the registry to follow the `version:` field in my SKILL.md
**So that** I'm in full control of when the registry advances and Studio doesn't surprise me with "update available" prompts I didn't initiate

**Acceptance Criteria**:
- [ ] **AC-US2-01**: After fetching the new SKILL.md (the same fetch already added in 0811), `scanOneSkill` parses the frontmatter `version:` via `readFrontmatterVersion` from `src/lib/skill-md/inject-version-if-missing.ts`.
- [ ] **AC-US2-02**: When `frontmatterVersion > skill.currentVersion` (semver-aware compare): use `frontmatterVersion` as the new `SkillVersion.version`. Bump proceeds.
- [ ] **AC-US2-03**: When `frontmatterVersion === skill.currentVersion` AND content changed (real hash differs from latest row's hash): SKIP the bump. Advance `lastSeenSha + lastCheckedAt` so we don't re-check on every cron tick. Emit metric `scanner.bump.skipped.no-frontmatter-bump` with skillId.
- [ ] **AC-US2-04**: When `frontmatterVersion < skill.currentVersion` (downgrade attempt — content advanced via a fork or revert): SKIP the bump, log warning, emit metric `scanner.bump.rejected.downgrade`. Don't advance lastSeenSha (so a future correction is still detected).
- [ ] **AC-US2-05**: When the SKILL.md has no frontmatter `version:` field at all (legacy or hand-rolled skills): fall back to the existing `deriveNextVersion` behavior to preserve backward compatibility. Emit metric `scanner.bump.fallback.no-frontmatter`.
- [ ] **AC-US2-06**: Vitest unit tests cover: (a) frontmatter > current → bump uses frontmatter, (b) frontmatter == current with content change → skip + lastSeenSha advanced, (c) frontmatter < current → reject + lastSeenSha NOT advanced, (d) no frontmatter version → fall back to deriveNextVersion.

---

### US-003: Residual phantom-row cleanup (P1, ALREADY EXECUTED)
**Project**: vskill-platform (registry DB)

**As an** ops operator
**I want** evidence that the 0811 backfill curl loop's residual 750 phantom rows are now gone
**So that** the registry has zero `sha256:pending:` rows and queries don't return confusing legacy state

**Acceptance Criteria**:
- [x] **AC-US3-01**: Phase A executed: skills with at least one real-hash row had all `sha256:pending:` rows deleted, `Skill.currentVersion` + `lastSeenSha` reset to the latest real row. **Result**: 97 skills, 169 rows deleted.
- [x] **AC-US3-02**: Phase B executed: skills with ONLY pending rows had the newest pending row preserved (its `contentHash` rewritten from `sha256:pending:<gitSha>` to `sha256:legacy:<gitSha>`), all other pending rows deleted, `Skill.currentVersion` + `lastSeenSha` reset to the survivor. **Result**: 82 skills, 601 rows deleted, 82 sentinels created.
- [x] **AC-US3-03**: Post-cleanup: `SELECT count(*) FROM "SkillVersion" WHERE "contentHash" LIKE 'sha256:pending:%'` returns **0**.
- [x] **AC-US3-04**: All operations ran inside `BEGIN/COMMIT` transactions. FK `ScanResult_skillVersionId_fkey` is `ON DELETE SET NULL` and there were 0 ScanResults pointing at pending rows pre-cleanup, so no audit trail was disturbed.

## Success Criteria

- All vitest tests pass on scanner + webhook paths (≥ 0811's 176/176 baseline).
- `npx tsc --noEmit` zero errors on 0813 paths.
- Production verification: a deliberate webhook push that doesn't touch a skill's path produces `enqueued:0, skipped:N` response.
- Production verification: a deliberate frontmatter-version-unchanged content edit does NOT bump the registry version.
- Registry-wide invariant: `sha256:pending:` row count remains 0 after deploy + first cron tick.
- Worker version recorded in increment closure notes.

## Out of Scope

- **Commit-back-to-source**: when the scanner detects a content change without a frontmatter bump, we deliberately do NOT push a frontmatter bump back to the source repo. Authors stay in control. (A future increment could add this as opt-in via GitHub App write scope.)
- **Multi-file content hash**: only `SKILL.md` is hashed. Sibling assets (images, scripts) under the skill directory are not part of the content hash. Future enhancement.
- **Bulk admin endpoint for legacy sentinel rows**: 82 `sha256:legacy:` rows now exist as a one-shot artifact. They're inert (the live scanner correctly bumps when real content lands). No further cleanup is required.

## Dependencies

- 0811 shipped — content-hash gate + raw.githubusercontent.com fetch path are in place.
- `readFrontmatterVersion` helper at `src/lib/skill-md/inject-version-if-missing.ts:42`.
- Existing `enqueueScanHigh` + `SCAN_HIGH_QUEUE` binding.
- `WEBHOOK_DEDUP_DO` continues to handle anti-replay before any path filtering.
