# 0685 — Implementation Plan

## Approach

**Reuse existing `Submission` rows** instead of inserting new ones.
This mirrors how `src/app/api/v1/admin/reenqueue/route.ts` handles
state-based bulk requeue: find → `updateMany` → enqueue. The readback
step disappears naturally because we already know the IDs *before* we
write.

### Why reuse beats createManyAndReturn

Codex suggested either the reuse path or `createManyAndReturn` (atomic
insert + return). Prisma 6.19.2 ships `createManyAndReturn`, so the
atomic option is technically available. But it does **not** solve
Finding 1 — `createManyAndReturn` still respects the unique index and
would either throw P2002 or (with `skipDuplicates`) return fewer rows
than inserted, re-creating the same "silent drop" problem. Reuse is
the right fix for both findings at once.

## Files Changed

### Modified

1. `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts`
   - Replace Phase 2 (`createMany` + readback) with:
     1. `findMany` on `Submission` filtered by `skillId IN (filteredSkillIds)`
        ordered by `createdAt asc`, selecting `id, repoUrl, skillName, skillPath, skillId`.
     2. Group by `skillId` (pick the oldest submission row per skill — the one
        linked during publish). Skills without any submission in the result set
        are the **orphan** case.
     3. `updateMany` on the resolved submission IDs: `state = RECEIVED`.
     4. Audit events (unchanged call shape, but `submissionId` comes from the
        reused rows).
     5. Enqueue from the in-memory reused rows (no readback).
   - Response payload: add `rescanned` (primary metric) and `orphanedSkipped`
     fields. Keep `created` as an alias for `rescanned` for backward compat.
   - Add a structured `console.warn` when orphans are skipped.

2. `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/__tests__/route.test.ts`
   - Keep existing auth / dry-run / batching / blocklist / enqueue-chunking
     tests (they still apply at the response-shape level).
   - Replace the "creates submissions via createMany" assertions with
     "resets existing submissions via updateMany" assertions.
   - Add test: Skill with no linked submission → `orphanedSkipped` incremented,
     NOT inserted via createMany.
   - Add test: bulk updateMany succeeds but a queue chunk rejects →
     response still 200, `errors[]` populated, audit events still written.

### Not touched

- `prisma/schema.prisma` — unique key stays.
- `src/lib/submission/publish.ts` — publish contract is the reason we can reuse.
- Sibling test files (integration, contract, in-flight-dedup, parallel,
  post-create-persistence) — owned by other agents in this team.

## Fallback for residual readback risk

Because the new primary path does **not** read back after writing, AC-US2-01
is satisfied structurally. If a future refactor reintroduces a post-write
read, the fallback shall be: on readback failure, fall back to the
pre-write ID list, still enqueue, emit a compensating audit event, and log
a `console.error` — never 500 with stranded `RECEIVED` rows.

## TDD Order

1. **RED**: Write failing assertions in `route.test.ts`:
   - `updateMany` is called with the *existing* submission IDs.
   - `createMany` is **not** called when every skill has a linked submission.
   - `orphanedSkipped` reflects skills with no linked submission.
2. **GREEN**: Rewrite Phase 2 of `route.ts` to the reuse pattern; run tests.
3. **REFACTOR**: Only if vitest is green — tidy response-shape assertions,
   drop the readback mock, simplify error handling.

## Rollout / Risk

- Route is admin-only; no public traffic.
- If the response shape change breaks an admin CLI (`created` → `rescanned`),
  mitigation: keep both fields populated with the same value for one release.
- No migration, no env var changes, no deploy step beyond the usual OpenNext
  build.
