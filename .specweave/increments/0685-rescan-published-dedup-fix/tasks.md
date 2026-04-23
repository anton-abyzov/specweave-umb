# 0685 — Tasks

## Backend agent (this increment owner) — 5 tasks

### T-001: RED — assert rescan reuses existing submission, not inserts new
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given 3 `Skill` rows and 3 existing `Submission` rows linked via `skillId`,
- When POST `/api/v1/admin/rescan-published` runs,
- Then `db.submission.updateMany` is called with
  `where: { id: { in: [<the 3 existing sub ids>] } }, data: { state: "RECEIVED" }`,
- And `db.submission.createMany` is NOT called,
- And `mockSendBatch` is called once with 3 queue messages whose `submissionId`
  matches the existing sub IDs.
- File: `src/app/api/v1/admin/rescan-published/__tests__/route.test.ts`

### T-002: RED — assert orphan skills are counted, not created
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given 2 `Skill` rows where only 1 has a linked `Submission`,
- When POST runs,
- Then response contains `orphanedSkipped: 1` and `rescanned: 1`,
- And `db.submission.createMany` is NOT called,
- And `updateMany` is called only for the 1 skill with a linked submission.

### T-003: RED — assert no post-write readback is required
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given the in-flight `submission.findMany` (Phase 1.5) returns empty,
- When POST runs,
- Then `submission.findMany` is NOT called with `where.id.in` (i.e. no
  post-write readback pattern),
- And the route never errors when the second `findMany` call is removed from
  the mock. (We'll assert `mockSubmissionFindMany` is called with `skillId.in`
  filters only, never `id.in`.)

### T-004: GREEN — rewrite route.ts Phase 2 to reuse existing submissions
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Implement `findMany({ where: { skillId: { in } } })` → group by skillId
  (pick oldest via `orderBy: { createdAt: 'asc' }`) → `updateMany` to
  `RECEIVED` → audit events → enqueue.
- Add `rescanned` and `orphanedSkipped` fields to JSON; keep `created` as alias.
- Re-run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/admin/rescan-published/__tests__/route.test.ts` — all RED tests turn green.

### T-005: REFACTOR — remove readback mock path + partial-failure regression
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Remove the post-create readback branch in mocks (test simplification).
- Add regression test: `updateMany` succeeds, first `sendBatch` chunk rejects —
  response is `ok: true, errors: [...]`, audit events still written for all
  reused subs.
- Full suite green: `npx vitest run src/app/api/v1/admin/rescan-published/__tests__/route.test.ts`.

## Testing-integration agent (NOT this agent — contract only)

- Integration test coverage for the reuse path at the DB level (real Prisma
  client or closer harness). Scope in `__tests__/route.integration.test.ts`,
  `route.contract.test.ts`, `in-flight-dedup.test.ts`, `route.parallel.test.ts`.

## Testing-failure agent (NOT this agent — contract only)

- Failure-mode coverage: simulate DB timeouts, queue send failures, partial
  updateMany commits. Scope in `__tests__/post-create-persistence.test.ts`.

## Contract for testing agents

- Route accepts: `POST /api/v1/admin/rescan-published` with optional JSON
  body `{ dryRun?: boolean, limit?: number, trustTiers?: string[], skipExistingT2?: boolean }`.
- Invariant: **N eligible Skills produce exactly N queue messages**, regardless
  of whether each skill already has a Submission row under the unique key.
- Invariant: orphan Skills (no linked Submission) are skipped and surfaced via
  `orphanedSkipped` in the response, never silently inserted.
- Auth: `X-Internal-Key` header OR SUPER_ADMIN Bearer token.
