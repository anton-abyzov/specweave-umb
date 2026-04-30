---
increment: 0811-fix-scanner-phantom-skill-versions
title: "Fix scanner phantom SkillVersion bumps"
type: bug
priority: P1
status: planned
created: 2026-04-30
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix scanner phantom SkillVersion bumps

## Overview

The skill-update scanner at `src/lib/skill-update/scanner.ts` creates a new `SkillVersion` row on every new HEAD SHA in the source repo, regardless of whether the skill's own files actually changed. This produces phantom version bumps when unrelated commits land (e.g., regenerating `agents.json`, refactoring studio UI). The fake `sha256:pending:<gitSha[0:12]>` placeholder makes every commit look like fresh content, so the existing per-version dedup guard is defeated.

User-visible symptom: `anton-abyzov/vskill/remotion-best-practices` shows three published versions (v1.1.0, v1.1.1, v1.1.2) on verified-skill.com but the local SKILL.md frontmatter is still `1.1.0` and the file content is byte-identical across all three "versions".

## Problem

Three parallel research agents converged on the same diagnosis:

1. **`scanner.ts:189`** — `deriveNextVersion(skill.currentVersion)` does a pure semver patch bump with no content gate.
2. **`scanner.ts:194`** — `contentHash = \`sha256:pending:${result.sha.slice(0,12)}\`` synthesizes a hash from the git commit SHA. Different commit → different "pending" hash → looks like new content even when the SKILL.md bytes are identical.
3. **GitHub webhook fast-path** also enqueues scans for ALL tracked skills in the repo on any push, regardless of which paths changed (defense-in-depth opportunity, out of scope here — fixing #2 alone solves the bug).

Evidence:
- v1.1.0 has REAL `contentHash`: `8eda5a1a756612335be32b3ec18e54fba1c5c05db96a833be8647f072b3652a3` (matches local SKILL.md SHA-256).
- v1.1.1 carries placeholder `sha256:pending:ed27afff4dbb` — exactly matches commit `ed27aff` "chore: regenerate agents.json after build" which did NOT touch `skills/remotion-best-practices/`.
- v1.1.2 carries placeholder `sha256:pending:0bd4b5e59d0e` — exactly matches commit `0bd4b5e` "0809: studio copied-skill source link + repo chip in byline" which also did NOT touch `skills/remotion-best-practices/`.
- `git show <commit>:skills/remotion-best-practices/SKILL.md | shasum -a 256` returns the same `8eda5a1a7566...` for all four commits since `f685af5` (the legitimate v1.1.0 publish).

## User Stories

### US-001: Real content-hash gate (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** the scanner to skip patch bumps when the skill's own files have not changed
**So that** registry version history reflects real content changes, not unrelated repo commits

**Acceptance Criteria**:
- [ ] **AC-US1-01**: After detecting a new HEAD SHA (existing idempotency guards pass), `scanner.ts` fetches `<skillPath>` (default `SKILL.md`) at that SHA from `raw.githubusercontent.com`, computes SHA-256 of the content, and stores the real digest as `contentHash` (no `sha256:pending:` prefix).
- [ ] **AC-US1-02**: Before calling `deriveNextVersion` + `writeSkillVersionWithOutbox`, the scanner queries the most recent existing `SkillVersion` for this skill (newest first) and compares its `contentHash` against the freshly computed one. If they match → no bump. Skill row is updated to advance `lastSeenSha` + `lastCheckedAt` only.
- [ ] **AC-US1-03**: When the previous row's `contentHash` starts with `sha256:pending:` (legacy phantom), the scanner falls back to the existing `gitSha` equality check (already covered by lines 161–171) plus a real-vs-real-hash comparison after backfill — both protections reinforce the dedup.
- [ ] **AC-US1-04**: When raw fetch fails (non-2xx, network error), scanner logs the failure and FALLS THROUGH to the legacy bump-with-pending-hash path — we never block update detection on a transient GitHub outage. Metric `scanner.contentfetch.failed` emitted.
- [ ] **AC-US1-05**: When `skill.skillPath` is null/empty (legacy rows), scanner defaults to `SKILL.md` at repo root.
- [ ] **AC-US1-06**: Vitest unit tests cover: (a) same content → no bump, (b) different content → bump with real hash, (c) fetch error → fallback to old behavior, (d) legacy-pending previous row → still dedups correctly when the new fetch matches the legacy fetch, (e) first-ever publish (no previous SkillVersion) → bump with real hash.

---

### US-002: Backfill endpoint to clean phantom rows (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** an admin endpoint that walks `SkillVersion` rows with `sha256:pending:` placeholders and collapses adjacent identical content
**So that** existing phantom rows for affected skills (starting with `anton-abyzov/vskill/remotion-best-practices`) reflect reality after the fix ships

**Acceptance Criteria**:
- [ ] **AC-US2-01**: New endpoint `POST /api/v1/admin/skills/{skillId}/backfill-content-hashes`. Auth: `requireAdmin`. Body optional: `{ dryRun?: boolean }` (defaults to `false`).
- [ ] **AC-US2-02**: Walks all `SkillVersion` rows for the skill in chronological order. For each row whose `contentHash` starts with `sha256:pending:`, fetches the SKILL.md at the row's `gitSha` from `raw.githubusercontent.com`, computes real SHA-256, and updates the row's `contentHash`.
- [ ] **AC-US2-03**: After all hashes are real, scans for adjacent rows with identical `contentHash` (sorted by `createdAt` ascending). Collapses by deleting the LATER duplicate(s) and resets `Skill.currentVersion` to the version of the surviving earliest distinct row. Updates `Skill.lastSeenSha` to the gitSha of the deleted-LATEST so the scanner doesn't re-bump on the next tick.
- [ ] **AC-US2-04**: Returns `{ scanned: N, recomputed: N, deleted: N, finalCurrentVersion: "x.y.z", finalLastSeenSha: "<sha>" }`.
- [ ] **AC-US2-05**: When `dryRun: true`, no DB writes happen — endpoint returns the same shape with planned changes.
- [ ] **AC-US2-06**: Idempotent: a second invocation on a clean skill is a no-op (`scanned: N, recomputed: 0, deleted: 0`).
- [ ] **AC-US2-07**: Vitest unit tests cover: (a) dry run, (b) phantom collapse on `remotion-best-practices`-shaped fixture, (c) idempotent re-run, (d) admin auth required.

---

### US-003: Production verification (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** post-deploy proof that scanner no longer creates phantom versions and that `remotion-best-practices` is back to a single legitimate v1.1.0 row
**So that** the user's reported discrepancy is closed and Studio's "current version" matches the registry

**Acceptance Criteria**:
- [ ] **AC-US3-01**: After deploy, run the backfill endpoint against `anton-abyzov/vskill/remotion-best-practices`. Result: `currentVersion = "1.1.0"`, exactly one SkillVersion row remains, `lastSeenSha` matches the current vskill repo HEAD.
- [ ] **AC-US3-02**: Trigger the next scanner pass (or wait for the `*/10` cron). Verify NO new phantom row was created for `remotion-best-practices` despite vskill repo HEAD being unchanged. Metric `scanner.contenthash.dedup.hits` increments.
- [ ] **AC-US3-03**: Playwright e2e: `GET /api/v1/skills/anton-abyzov/vskill/remotion-best-practices/versions` returns exactly 1 version with `version: "1.1.0"` and a real (non-`pending:`) contentHash.

## Success Criteria

- All vitest tests pass on alerts AND scanner paths.
- `npx tsc --noEmit` produces zero errors on 0811 paths.
- Production: `anton-abyzov/vskill/remotion-best-practices` API returns 1 version after backfill.
- Studio at `localhost:3162` and verified-skill.com both show `v1.1.0` for `remotion-best-practices` after deploy + backfill.
- Worker version recorded in increment closure notes.

## Out of Scope

- Webhook path-filter (only enqueue scans for affected skill paths). The content-hash gate alone fixes the bug; path-filter is a defense-in-depth layer for a future increment.
- UI banner to surface "registry version differs from local" — handled separately by the existing skill-update UI.
- Mass backfill of every skill in the registry. We only backfill on demand per skill (starting with `remotion-best-practices`) to avoid a long-running operation in the closure window.
- Writing the bumped version back to source SKILL.md on publish (a different desync path covered by `project_skill_version_publish_desync.md`).

## Dependencies

- 0807 (alerts pipeline) and 0808 (alerts follow-ups) shipped — no overlap.
- `scanner.ts`, `outbox-writer.ts`, `requireAdmin`, raw.githubusercontent.com fetch path — all already in repo.
