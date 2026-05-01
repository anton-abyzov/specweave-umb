---
increment: 0819-skill-versionless-rows-fix
title: Skill Versionless Rows Fix
type: bug
priority: P1
status: ready_for_review
created: 2026-05-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Versionless Rows Fix

## Overview

A user reported that Skill Studio's detail panel for `gitroomhq/postiz-agent/postiz` shows "No versions found" even though the skill is `VERIFIED` with `currentVersion: "1.0.0"`. The bug reproduces directly against the platform: `GET /api/v1/skills/gitroomhq/postiz-agent/postiz/versions` returns `{"versions":[],"count":0}`. Skill Studio is rendering the platform's response faithfully — the data itself is wrong.

**Root cause** — `src/app/api/v1/admin/rebuild-index/route.ts:130` calls `db.skill.upsert(...)` with `currentVersion: "1.0.0"` but never creates a paired `SkillVersion` row. The architecture invariant in `src/lib/skill-update/outbox-writer.ts:18` already bans raw `skillVersion.create()` outside the outbox writer, but it does NOT enforce the symmetric invariant that every `Skill` row must have at least one paired `SkillVersion`. Any code path that materializes a Skill from the discovery index (sourced from the `skills.sh` crawler) without a publish event therefore produces an orphan row that the UI cannot render.

This is a structural bug, not a one-off data fault: closing it requires both (a) preventing the class going forward and (b) remediating existing orphans in production. The increment touches two repos — primary work in `vskill-platform`, plus a small Skill Studio copy change in `vskill` so unversioned skills surface as "discovered, no published version yet" instead of the misleading "No versions found."

## User Stories

### US-001: Pair-write helper for Skill + first SkillVersion (P1)
**Project**: vskill-platform

**As a** platform developer writing code that creates new `Skill` rows
**I want** a single helper that atomically writes the Skill plus its first `SkillVersion` through the existing outbox path
**So that** no caller can accidentally produce a Skill row without a paired version, and the existing outbox/UpdateEvent invariants stay intact

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new file `src/lib/skills/create-skill-with-version.ts` exports `createSkillWithVersion(db, upsertArgs, versionInput, source)` that wraps `db.skill.upsert` and `writeSkillVersionWithOutbox` inside one `db.$transaction`.
- [x] **AC-US1-02**: The helper routes the version write through `writeSkillVersionWithOutbox` (existing helper at `src/lib/skill-update/outbox-writer.ts:81`) with `bumpSource: "discovery-backfill"` and `source: "admin"` — it never calls `db.skillVersion.create()` directly.
- [x] **AC-US1-03**: The helper returns `{ skill, skillVersion, eventId, payload }` so callers can drive the post-commit publish via `publishOutboxEventAfterCommit` without re-querying.
- [x] **AC-US1-04**: When the Skill row already exists with at least one `SkillVersion`, the helper detects this (pre-check on `skillVersion.count`) and skips the version write — re-running it is a no-op (idempotent).
- [x] **AC-US1-05**: When `writeSkillVersionWithOutbox` throws inside the transaction, the Skill upsert rolls back: a unit test asserts the Skill row does not exist after a forced outbox failure.
- [x] **AC-US1-06**: A unit test exercises the happy path against a mocked `OutboxTx` and asserts both `skill.upsert` and `skillVersion.create` were called with the expected arguments in the same transaction context.
- [x] **AC-US1-07**: The helper preserves the existing `contentHash` non-empty invariant from `publish.ts:660` — when no real content hash is available, it passes `sha256("")` (well-defined non-empty hash) flagged by `bumpSource: "discovery-backfill"`.

---

### US-002: Refactor rebuild-index admin route to use the pair-write helper (P1)
**Project**: vskill-platform

**As a** platform operator running the admin rebuild-index route
**I want** new Skill rows materialized from the discovery index to also get their first `SkillVersion` written automatically
**So that** the bug class is closed at its origin and `gitroomhq/postiz-agent/postiz`-shaped orphans cannot be re-created on the next rebuild

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/app/api/v1/admin/rebuild-index/route.ts` no longer calls `db.skill.upsert(...)` directly for the create branch. Instead it pre-checks with `db.skill.findUnique({ where: { name: skill.slug }, select: { id: true } })`.
- [x] **AC-US2-02**: When the pre-check returns `null` (new Skill), the route calls `createSkillWithVersion(...)` from US-001 with version inputs synthesized from the index entry: `version: skill.currentVersion`, `gitSha: lastSeenSha ?? "discovery:" + sha256(repoUrl).slice(0,40)`, `contentHash: sha256("")`, `certTier`/`certMethod`/`certifiedAt` from the index entry.
- [x] **AC-US2-03**: When the pre-check returns an existing row, the update branch's behavior is unchanged — those rows already have versions from earlier publishes, so no version is written.
- [x] **AC-US2-04**: An integration test runs the rebuild-index route against a seeded KV index containing one new entry and asserts that after the route returns successfully, `db.skillVersion.count({ where: { skillId: <new skill id> } })` is exactly `1`.
- [x] **AC-US2-05**: An integration test runs rebuild-index twice in a row against the same index and asserts no duplicate `SkillVersion` rows are created (idempotency at the route level).
- [x] **AC-US2-06**: `src/lib/submission/publish.ts:300` is intentionally not modified — its existing pairing via `writeSkillVersionWithOutbox` (line 676) is already correct. A comment in the refactor PR description notes this as a deliberate non-change.

---

### US-003: Architecture invariant test forbidding bare Skill writes (P1)
**Project**: vskill-platform

**As a** platform maintainer reviewing future PRs
**I want** CI to fail when someone introduces a new code path that writes a `Skill` row without going through the pair-write helper
**So that** the structural invariant "every Skill row has at least one SkillVersion" is enforced by the test suite, not by code-review vigilance alone

**Acceptance Criteria**:
- [x] **AC-US3-01**: A new file `src/lib/skills/__tests__/architecture-skill-pair.test.ts` exists, mirroring the walk + allowlist + comment-stripped regex pattern in `src/lib/skill-update/__tests__/architecture.test.ts`.
- [x] **AC-US3-02**: The test forbids the regex `/\b(?:tx|prisma|db|client|trx)\.skill\.(?:create|upsert)\s*\(/` everywhere under `src/` except the allowlist.
- [x] **AC-US3-03**: The allowlist is exactly: `lib/skills/create-skill-with-version.ts` (the helper itself) and `lib/submission/publish.ts` (already pairs in same txn). Test files are excluded by extension.
- [x] **AC-US3-04**: Running `npx vitest run src/lib/skills/__tests__/architecture-skill-pair.test.ts` passes against the post-US-002 codebase.
- [x] **AC-US3-05**: Manually injecting `db.skill.upsert(...)` into any non-allowlisted file under `src/` causes the test to fail with a message naming the offending file and line.
- [x] **AC-US3-06**: The test strips line/block comments before scanning (so commented-out examples in docs/comments don't trigger false positives), matching the existing `architecture.test.ts` behavior.

---

### US-004: Backfill admin route for existing versionless Skill rows (P1)
**Project**: vskill-platform

**As a** platform operator with orphan Skill rows already in production
**I want** an authenticated admin endpoint that scans for Skills with zero `SkillVersion` rows and synthesizes a `v1.0.0` row through the pair-write helper
**So that** I can remediate the existing `gitroomhq/postiz-agent/postiz`-shaped orphans without redeploying the rebuild-index route or running ad-hoc scripts against production

**Acceptance Criteria**:
- [x] **AC-US4-01**: A new route `POST /api/v1/admin/backfill-versionless-skills` exists at `src/app/api/v1/admin/backfill-versionless-skills/route.ts`, mirroring the shape of `src/app/api/v1/admin/backfill-versions/route.ts` (auth, dryRun, batch/cursor, error array, jsonResponse helper).
- [x] **AC-US4-02**: Authentication accepts either `hasInternalAuth(request)` (X-Internal-Key header) OR `requireAdmin(request)` (super-admin JWT). Unauthenticated requests get the same 401/403 shape the existing admin routes return.
- [x] **AC-US4-03**: Query param `dryRun=true` reports planned changes (`scanned`, `updated`, `skipped`, `errors`) without writing any `SkillVersion` rows or emitting any `UpdateEvent` rows.
- [x] **AC-US4-04**: Query param `batch=N` controls the batch size, default `100`, clamped to `1..500` (matches `backfill-versions` semantics).
- [x] **AC-US4-05**: The route finds Skills with zero paired `SkillVersion` rows. For each, it synthesizes a version via `createSkillWithVersion`-style inputs derived from Skill columns: `version: skill.currentVersion`, `gitSha: skill.lastSeenSha ?? "discovery:" + sha256(skill.repoUrl).slice(0,40)`, `contentHash: <KV cache or sha256("")>`, `certTier`/`certMethod`/`certifiedAt` from the Skill row. The write goes through `writeSkillVersionWithOutbox` with `bumpSource: "discovery-backfill"`, `source: "admin"`.
- [x] **AC-US4-06**: The synthetic `SkillVersion.createdAt` is set to `skill.certifiedAt ?? skill.createdAt` (NOT `now()`) so chronology is honest and the `/api/v1/skills/check-updates` query (`orderBy: { createdAt: "desc" }, distinct: ["skillId"]` at `route.ts:250`) does not flag the synthetic row as a "newer than nothing" update for lockfile holders.
- [x] **AC-US4-07**: The route is idempotent: running it twice does not create duplicate versions. Skills that already have ≥1 `SkillVersion` are counted in `skipped`, not `updated`.
- [x] **AC-US4-08**: When KV cache (`skillmd:${id}`) has the original SKILL.md content, the route uses its `sha256` for `contentHash`. When the cache misses, it falls back to `sha256("")` and relies on `bumpSource: "discovery-backfill"` as the explicit "this is degraded" flag.
- [x] **AC-US4-09**: Pagination uses an `id` cursor on the Skill table; one batch processes up to `batch` Skills then returns. Subsequent calls with `?cursor=<lastId>` resume.
- [x] **AC-US4-10**: The response shape is `{ dryRun, scanned, updated, skipped, errors: [{ kind: "synthesis" | "write", id, message }] }` — matches the established admin-route convention.
- [x] **AC-US4-11**: An integration test seeds three Skills (one with versions, two without), runs `dryRun=true` and asserts `scanned: 3, updated: 0, skipped: 1, errors: []` plus no `SkillVersion` writes occurred.
- [x] **AC-US4-12**: An integration test runs the route without `dryRun`, asserts `updated: 2, skipped: 1`, then runs it again and asserts `updated: 0, skipped: 3` (idempotency at the route level).
- [x] **AC-US4-13**: An integration test asserts that for each backfilled Skill, the synthetic `SkillVersion.createdAt === skill.certifiedAt` (chronology mitigation per AC-US4-06).

---

### US-005a: Versions route surfaces unversioned Skills distinctly (P1)
**Project**: vskill-platform

**As a** Skill Studio user looking at a discovered-but-unpublished skill
**I want** the `/versions` endpoint to distinguish "Skill exists but has no published version yet" from "Skill not found"
**So that** the UI can render an honest, informative message and the failure mode of the underlying bug is observable from the wire

**Acceptance Criteria**:
- [x] **AC-US5a-01**: When the route `GET /api/v1/skills/[owner]/[repo]/[skill]/versions` finds a Skill row but `count(SkillVersion) === 0`, it returns HTTP 200 with body `{ versions: [], count: 0, unversioned: true, currentVersion: <skill.currentVersion> }`.
- [x] **AC-US5a-02**: When the Skill itself does not exist, the route still returns HTTP 404 with the existing not-found shape — the "unversioned" branch is only for rows that exist on the Skill table.
- [x] **AC-US5a-03**: When the Skill has ≥1 `SkillVersion`, the response shape is unchanged from today — no `unversioned` field is emitted in the happy path (additive only on the orphan branch).
- [x] **AC-US5a-04**: A unit test for the route covers all three branches: orphan (200, `unversioned: true`), normal (200, `unversioned` absent, `count > 0`), not-found (404).
- [ ] **AC-US5a-05**: After the US-004 backfill runs in production, `curl https://verified-skill.com/api/v1/skills/gitroomhq/postiz-agent/postiz/versions` returns `count >= 1` and no `unversioned` flag — captured as an E2E test step.

---

### US-005b: Skill Studio detail panel renders unversioned state honestly (P2)
**Project**: vskill

**As a** Skill Studio user opening a discovered-but-unpublished skill
**I want** the detail panel to say "Discovered — no published version yet (currentVersion: X)" instead of "No versions found"
**So that** I understand the skill is real but not yet published, rather than thinking the data is missing or broken

**Acceptance Criteria**:
- [x] **AC-US5b-01**: `src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx:595` reads the `unversioned` flag from the `/versions` response (per US-005a).
- [x] **AC-US5b-02**: When `unversioned === true`, the panel renders the string `Discovered — no published version yet (currentVersion: {currentVersion})`, substituting the value from the response payload.
- [x] **AC-US5b-03**: The new branch is identifiable from tests via `data-testid="skill-detail-unversioned"`. The existing "No versions found" branch keeps `data-testid="skill-detail-no-versions"` so older tests still pass.
- [x] **AC-US5b-04**: When `unversioned` is `false` or absent and `count > 0`, the panel renders the existing version list (unchanged behavior).
- [x] **AC-US5b-05**: A Vitest snapshot test for `SkillDetailPanel` covers the three states: `unversioned: true`, normal versions list, error/empty.
- [ ] **AC-US5b-06**: A Playwright E2E test in the eval-ui project (or `vskill-platform/tests/e2e/0819-versionless-skills.spec.ts` driving Studio via its proxy) opens the studio, searches for a known unversioned skill, opens the detail panel, and asserts `data-testid="skill-detail-unversioned"` is visible.

## Functional Requirements

### FR-001: Single pair-write call site for new Skill rows
All code paths that create a new `Skill` row MUST go through `createSkillWithVersion()` so the first `SkillVersion` is written in the same transaction. Existing publish flows that already pair correctly (`src/lib/submission/publish.ts`) are exempt because they are already correct — the architecture test allowlists them explicitly.

### FR-002: Outbox routing preserved
The new helper does not introduce a second SkillVersion write path. It composes `db.skill.upsert` with the existing `writeSkillVersionWithOutbox` so the UpdateEvent is created, the `eventId` is a ULID, and the post-commit publish flow remains the caller's responsibility.

### FR-003: Backfill remediation route
A gated admin route remediates existing orphans without requiring redeployment of the rebuild path. The route is idempotent, supports dryRun, and respects existing chronology so the `/check-updates` endpoint does not trigger spurious notifications.

### FR-004: Wire-level observability of unversioned state
The `/versions` endpoint distinguishes "Skill exists, no versions yet" (200 + `unversioned: true`) from "Skill not found" (404). This exists so the failure mode is observable on the wire and the UI can render a useful message even before backfill runs.

### FR-005: Architecture invariant enforcement
A CI test forbids new bare `db.skill.create|upsert` callers outside an explicit allowlist. The test mirrors the existing `outbox-writer` architecture test.

## Success Criteria

- After deploy + backfill: `GET https://verified-skill.com/api/v1/skills/gitroomhq/postiz-agent/postiz/versions` returns `{ count: 1, versions: [{ version: "1.0.0", ... }], unversioned: false }` (or omits `unversioned`).
- After deploy + backfill: querying any other previously-orphan Skill returns `count >= 1`.
- Skill Studio detail panel shows the v1.0.0 row for `gitroomhq/postiz-agent/postiz` (not the "No versions found" message).
- Running the rebuild-index route after the fix never produces a Skill row without at least one paired `SkillVersion`.
- Architecture test `architecture-skill-pair.test.ts` passes in CI; manually injecting a bare `db.skill.upsert(...)` into a non-allowlisted file fails the test.
- Backfill route runs idempotently — second run reports `updated: 0, skipped: <total>`.
- `/api/v1/skills/check-updates` does NOT emit spurious update notifications to lockfile-holding clients after the backfill (verified by chronology test in AC-US4-13).

## Out of Scope

- Backfilling `SkillVersion.content` (full SKILL.md text) for orphans — the synthetic row stores `contentHash` only. Content can be repopulated later by re-running the publish flow if a real release lands.
- Changing the discovery crawler (`skills.sh` / `lib/crawler/github-discovery.ts`) — the bug is at the materialization boundary, not at discovery.
- Migrating the `bumpSource` enum or adding UI filters for the new `discovery-backfill` value — additive only.
- Renaming or refactoring `src/lib/submission/publish.ts` — already correct, intentionally untouched.
- A separate notification-suppression flag on synthetic versions — the chronology mitigation (`createdAt = certifiedAt`) is sufficient for this increment.
- UI change to the public `verified-skill.com/skills/[owner]/[repo]/[skill]/versions` page — only the API and the Skill Studio panel are in scope.

## Dependencies

- Existing helper `writeSkillVersionWithOutbox` at `src/lib/skill-update/outbox-writer.ts:81` (consumed by US-001).
- Existing `hasInternalAuth` and `requireAdmin` helpers (consumed by US-004).
- Existing `parseSemver` and `jsonResponse`/`errorResponse` helpers from `backfill-versions` route (mirrored by US-004).
- Existing architecture test pattern at `src/lib/skill-update/__tests__/architecture.test.ts` (mirrored by US-003).
- Prisma schema fields used in synthesis: `Skill.currentVersion`, `Skill.lastSeenSha`, `Skill.repoUrl`, `Skill.certTier`, `Skill.certMethod`, `Skill.certifiedAt` (all already present per `prisma/schema.prisma:214`).
- Skill Studio component path `src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx:595` in the `vskill` repo (touched by US-005b).
