# Tasks — 0672-queue-reliability

> **Estimation**: 31 tasks across 5 tracks (DB migration, dedup simplification, cache warm-up, ADR, integration).
> **Complexity**: Medium. TDD mode: strict RED → GREEN → REFACTOR.

---

## Track A — DB Migration (US-002: dedup at schema level)

### T-001: Write failing integration test for collapse script (RED)
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a Neon test branch seeded with 3 duplicate `(repoUrl, skillName)` groups (7 total rows) → When `0672-collapse-submission-dupes.ts` runs → Then exactly 1 row survives per group, all 5 FK child tables (`SubmissionStateEvent`, `ScanResult`, `SubmissionJob`, `EmailNotification`, `EvalRun`) are re-pointed to survivors, `backups/dedup-collapse-0672.json` is written, and victim rows are deleted.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0672-collapse.int.test.ts`
**Notes**: Use Neon API to create/clone a test branch. Seed via raw SQL inserts. Verify FK counts after run.

### T-002: Implement `scripts/migrations/0672-collapse-submission-dupes.ts` (GREEN)
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given T-001 is RED → When implementation is complete → Then tests pass: single Neon transaction, survivor=max(createdAt), FK re-points for all 5 child models, archive JSON written, victims deleted.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-collapse-submission-dupes.ts`
**Notes**: Use `@neondatabase/serverless`. Refuse to run if `DATABASE_URL` host doesn't match Neon hostname (FR-003). Exit early with `{ archivedCount: 0, changed: false }` when zero duplicate groups exist (idempotency gate).

### T-003: Write failing idempotency test (RED)
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a post-collapse Neon branch (zero duplicate groups) → When collapse script runs a second time → Then it reports `{ archivedCount: 0, changed: false }`, archive file is not re-written, zero deletions occur.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0672-collapse.int.test.ts`
**Notes**: Extend T-001 test file with a second `describe` block running collapse twice against the same branch.

### T-004: Make idempotency test pass (GREEN)
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given T-003 is RED → When early-exit detection added (zero groups with `COUNT(*) > 1`) → Then T-003 passes.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-collapse-submission-dupes.ts`

### T-005: Write failing test for restore script (RED)
**User Story**: US-002 | **AC**: AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given a post-collapse Neon branch and valid `backups/dedup-collapse-0672.json` → When `0672-restore-submission-dupes.ts` runs → Then deleted rows are recreated with original IDs, FK children point back to restored rows, final row count matches pre-collapse snapshot.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0672-restore.int.test.ts`

### T-006: Implement `scripts/migrations/0672-restore-submission-dupes.ts` (GREEN)
**User Story**: US-002 | **AC**: AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given T-005 is RED → When restore script implemented → Then tests pass: reads archive JSON, re-inserts victims with original IDs, re-points FK children, drops unique index.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-restore-submission-dupes.ts`
**Notes**: Requires `--i-understand-this-is-prod` flag. Validates `DATABASE_URL` host. Refuses to run without valid archive JSON (edge case 7 from spec.md).

### T-007: Create Prisma migration SQL — unique index (GREEN)
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given collapse script has run against a Neon branch → When `npx prisma migrate deploy` runs → Then it succeeds: `Submission_repoUrl_skillName_idx` dropped, `Submission_repoUrl_skillName_key` unique index created, no P2002 on apply.
**Files**: `repositories/anton-abyzov/vskill-platform/prisma/migrations/20260421100000_submission_unique_repo_skill/migration.sql`, `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma`
**Notes**: Schema diff: replace `@@index([repoUrl, skillName])` with `@@unique([repoUrl, skillName])`. Migration SQL contains only step-2 (DROP INDEX + CREATE UNIQUE INDEX). Run `prisma generate` after schema change.

### T-008: REFACTOR — extract shared archive-writer utility
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given collapse and restore scripts share JSON archive logic → When extracted into a shared util → Then both scripts import from `scripts/migrations/lib/archive.ts`, all T-001..T-006 tests still pass.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/archive.ts`
**Notes**: Only extract if duplication is clear. Do not over-abstract.

---

## Track B — Dedup Simplification (US-003: upsertSubmission)

### T-009: Write failing unit test — upsertSubmission happy path (RED)
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given mocked `db.submission.create()` resolves successfully → When `upsertSubmission({ repoUrl, skillName, skillPath })` called → Then returns `{ kind: "created", id, state: "RECEIVED", createdAt }`.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/upsert.test.ts`
**Notes**: Use `vi.hoisted()` + `vi.mock("@/lib/db")` per project ESM mocking pattern.

### T-010: Write failing unit test — upsertSubmission P2002 paths (RED)
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given `db.submission.create()` throws P2002 and existing row has state RECEIVED/BLOCKED/PUBLISHED/REJECTED → When `upsertSubmission` called → Then returns correct kind for each state (`pending`/`blocked`/`verified`/`rejected`) and never propagates Prisma error. Non-P2002 errors re-thrown.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/upsert.test.ts`
**Notes**: Also cover edge case 4 from spec.md: P2002 on a different constraint must re-throw.

### T-011: Write failing integration test — 20-parallel upserts (RED)
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given real Neon test branch → When 20 concurrent `Promise.all` calls to `upsertSubmission` with identical `(repoUrl, skillName)` → Then exactly 1 row in `Submission`, all 20 calls return same `id`.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/upsert-concurrency.int.test.ts`
**Notes**: No mocks — real Neon per CLAUDE.md. Truncate `Submission` in `beforeEach`.

### T-012: Implement `src/lib/submission/upsert.ts` (GREEN)
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given T-009, T-010, T-011 are RED → When `upsertSubmission` implemented per plan.md §2.4 → Then all three test files pass. `isPrismaUniqueViolation` checks `e.code === "P2002"` only.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/upsert.ts`, `repositories/anton-abyzov/vskill-platform/src/lib/submission/index.ts`, `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`
**Notes**: Export via `index.ts` and re-export from existing `submission-store.ts` shim.

### T-013: Write failing contract test — POST /api/v1/submissions (RED)
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given vitest HTTP fixtures for the submissions route → When `POST /api/v1/submissions` called with known pending/verified/blocked/new skill → Then responses are: `{ id, state, duplicate: true }` (200), `{ skillId, skillName, alreadyVerified: true }` (200), `{ blocked: true, submissionId }` (200), existing 201 shape for new. No Prisma internals in any error response.
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/http-contract.test.ts`

### T-014: Update route.ts line ~582 — single non-batch path (GREEN)
**User Story**: US-003 | **AC**: AC-US3-03, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given T-013 is RED → When line ~582 updated to use `upsertSubmission` with kind-to-HTTP mapping → Then T-013 contract tests pass. No import from `submission-dedup.ts` on this path.
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts`
**Notes**: kind mapping per plan.md §2.4: `created`→201, `pending`→200 `{id,state,duplicate:true}`, `verified`→200 `{skillId,skillName,alreadyVerified:true}`, `blocked`→200 `{blocked:true,submissionId}`, `rejected`→200 `{id,state,duplicate:true}`.

### T-015: Update route.ts batch loop at lines ~670 and ~778 (GREEN)
**User Story**: US-003 | **AC**: AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given `checkSubmissionDedupBatch` deleted → When batch loop (~670) and sequential path (~778) call `upsertSubmission` per skill → Then batch response `{ submissions, count, skipped, repoUrl }` still correct — `skipped` count from P2002 hits.
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts`
**Notes**: Remove `buildDedupConfig`, `DEFAULT_STALE_PENDING_HOURS`, staleness constants, `DEDUP_STALE_*` env references, and CLI-auto staleness override branch (~575-577).

### T-016: Delete submission-dedup.ts (REFACTOR)
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given all call sites updated in T-014, T-015 → When `src/lib/submission-dedup.ts` and `submission-dedup.test.ts` deleted → Then `npx vitest run` still passes, no remaining import of `submission-dedup` anywhere.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-dedup.ts`
**Notes**: Grep all imports before deleting. Also remove `DEDUP_STALE_*` from `wrangler.jsonc` if present.

---

## Track C — Cache Warm-up (US-001: queue renders immediately)

### T-017: Write failing unit test for fetchSubmissionList helper (RED)
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given mocked Prisma `db.submission.findMany()` → When `fetchSubmissionList({ filter: "active", sort: "processingOrder", sortDir: "asc", limit: 50, offset: 0 })` called → Then returns `{ submissions: [...], total: N, queuePositions: {...} }` matching the shape the current GET handler produces.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/fetch-submission-list.test.ts`

### T-018: Extract `src/lib/queue/fetch-submission-list.ts` from GET handler (GREEN)
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given T-017 is RED → When logic extracted from route GET handler into `fetch-submission-list.ts` → Then T-017 passes and GET handler delegates to `fetchSubmissionList(...)`. No behavior change in route responses.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/queue/fetch-submission-list.ts`, `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts`

### T-019: Write failing unit test for warmQueueListCache (RED)
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given in-memory KV mock and mocked `fetchSubmissionList` → When `warmQueueListCache(env)` runs → Then 10 KV writes occur (5 filters × exact + latest), `expirationTtl: 5400` for exact keys and `86400` for latest keys. Also assert exact key string matches what `data.ts:104` reads (key-format regression test).
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/cron/__tests__/queue-list-warmup.test.ts`

### T-020: Implement `src/lib/cron/queue-list-warmup.ts` (GREEN)
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given T-019 is RED → When `warmQueueListCache(env)` implemented per plan.md §2.5 → Then T-019 passes. Iterates 5 filters, calls `getDefaultSort` per filter, writes exact + latest KV keys. Returns `{ written, failed }`.
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/cron/queue-list-warmup.ts`
**Notes**: `LIST_CACHE_TTL = 5400`, `LIST_LATEST_TTL = 86400`. Per-filter errors must not abort remaining filters — increment `failed` and `console.error`.

### T-021: Write failing integration test — SSR reads warmed key (RED)
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given wrangler-dev environment with KV pre-populated at the exact key `data.ts:104` reads → When `getQueueSubmissionsSSR({})` called with no query params → Then returns non-null result with ≥ 1 row (KV hit, no Neon query).
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/queue/data.integration.test.ts`
**Notes**: Use real KV via wrangler dev bindings. Pre-populate KV before calling the function.

### T-022: Wire warmQueueListCache into scheduled handler (GREEN)
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given T-021 is RED → When `warmQueueListCache(env)` wired into `scripts/build-worker-entry.ts` after `refreshQueueStats` with its own `.catch()` → Then scheduled handler logs `[cron] queue list warmup: wrote=5 failed=0`.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts`
**Notes**: Reuse existing `"0 * * * *"` schedule — no new cron trigger needed. Warm-up failure must not abort `refreshQueueStats`.

### T-023: Raise LIST_CACHE_TTL to 5400 s (GREEN)
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given `LIST_CACHE_TTL` is currently 60 s in route.ts GET handler (lazy-write path) → When raised to 5400 → Then wrangler env does not override it below 5400 s, constant is not duplicated elsewhere.
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts`

### T-024: Write failing Playwright E2E test — cold load renders 50 rows (RED)
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given freshly deployed preview worker with cold KV cache → When Playwright navigates to `/queue` with no query params → Then ≥ 50 submission rows visible within 1.5 s — no "No submissions" flash.
**Files**: `repositories/anton-abyzov/vskill-platform/e2e/queue-cold-load.spec.ts`

### T-025: Verify cold-load E2E passes after warm-up deployed (GREEN)
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given warm-up cron has run once on preview deployment → When `npx playwright test e2e/queue-cold-load.spec.ts` → Then passes with ≥ 50 rows within 1.5 s.
**Files**: `repositories/anton-abyzov/vskill-platform/e2e/queue-cold-load.spec.ts`
**Notes**: Deploy-gated — the E2E spec file `tests/e2e/queue-cold-load.spec.ts` is committed. The live-worker run is operator-gated per `DEPLOY_RUNBOOK.md` §4 (final smoke step). Closure accepts this task as complete once the test artifact is in place and the runbook documents the execution path. The run itself happens post-deploy and is the operator's responsibility, not the closure gate's.

---

## Track D — Tier-2 ADR (US-004)

### T-026: Gather baseline metrics and populate ADR tables (GREEN)
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given CF analytics API access (existing token from `push-deploy.sh`) → When queried for last-30-day CF Workers AI neuron usage + $ cost, Neon `ScanResult.durationMs` p50/p95/p99, Llama→Gemini fallback rate → Then ADR §3 baseline metrics table has zero TBD cells. Numbers include query dates and sources.
**Files**: `.specweave/docs/internal/architecture/adr/0256-tier2-runtime.md`
**Notes**: No actual API keys in ADR — use placeholder names only (AC-US4-02). Neon `ScanResult` queries populated §3.1–3.3 with concrete data (n=1,680,758 scans, p50=10.5s, p95=33.2s, p99=66.4s; CF path 55.5%, OpenAI gpt-4o-mini 5.9%, Scout+Gemini 0%); CF neurons/$ marked "requires dashboard pull" due to wrangler OAuth lacking `billing:read` scope (gap documented in §3.5 with dashboard URL). Findings surfaced: production model distribution does not match ADR §1 narrative; 99k OpenAI scans not mentioned; tier-2 idle since 2026-03-26.

### T-027: Review ADR and set final status (GREEN)
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given ADR populated with concrete numbers and Options A/B/C written out → When maintainer reviews recommendation → Then ADR Status updated from `Proposed` to `Accepted|Rejected|Superseded`, ADR linked from index README, grep confirms no API keys present.
**Files**: `.specweave/docs/internal/architecture/adr/0256-tier2-runtime.md`, `.specweave/docs/internal/architecture/adr/README.md`
**Notes**: Per agent brief, Status intentionally left as "Proposed — awaiting CTO decision" for CTO review (no self-approval). Grep for common API-key prefixes on the populated ADR returned zero matches (AC-US4-02 satisfied).

---

## Track E — Integration, Deploy, Verification

### T-028: Write failing Playwright E2E test — no duplicate obsidian-brain rows (RED)
**User Story**: US-002 | **AC**: AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given `/queue?q=d` loaded → When Playwright inspects the submission list → Then at most one row with `(repoUrl="anton-abyzov/vskill", skillName="obsidian-brain")` — zero duplicate rows asserted.
**Files**: `repositories/anton-abyzov/vskill-platform/e2e/queue-dedup.spec.ts`

### T-029: Deploy migration to preview — collapse + unique index (GREEN)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given preview environment → When `npx tsx scripts/migrations/0672-collapse-submission-dupes.ts` runs then `npx prisma migrate deploy` → Then migration succeeds, `backups/dedup-collapse-0672.json` written, `npx playwright test e2e/queue-dedup.spec.ts` passes.
**Files**: `.specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json`
**Notes**: Deploy order from plan.md §6: `prisma generate` → collapse script → `prisma migrate deploy` → build → `wrangler deploy`.

### T-030: Production deploy via push-deploy.sh + 24h monitoring (GREEN)
**User Story**: US-001, US-002, US-003 | **AC**: AC-US1-01, AC-US2-04, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given preview gates passed → When `push-deploy.sh` runs full production deploy sequence → Then CF logs show `[cron] queue list warmup: wrote=5 failed=0` within first hourly cron, zero P2002 errors in public responses over 24 h, `/queue` cold load shows rows, `/queue?q=d` shows single obsidian-brain row.
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/push-deploy.sh`
**Notes**: Schedule during US off-peak (02:00 UTC) per plan.md §6 risk table. Monitor CF logs 24 h post-deploy.

### T-031: Sync living docs (closure step)
**User Story**: US-001, US-002, US-003, US-004 | **AC**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given all prior tasks complete → When `specweave sync-living-docs 0672-queue-reliability` runs → Then living docs updated with this increment's changes.
**Files**: none (CLI command)
