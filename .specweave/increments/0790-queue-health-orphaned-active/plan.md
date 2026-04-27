---
increment: 0790-queue-health-orphaned-active
title: "Fix queue-health oldestActive reporting state-desync orphans"
---

# Implementation Plan: 0790 — queue-health orphaned-active

## Architecture

**Strictly contained** in `src/app/api/v1/queue/health/route.ts`. No worker changes, no schema changes, no migrations. The fix narrows the existing `oldestActive` query and adds a parallel `orphanedActive` count query.

## Files Modified

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/queue/health/route.ts` | Add `OLDEST_ACTIVE_FRESHNESS_MS` constant; narrow the `oldestActive` Prisma query with `updatedAt: { gte: ... }`; run a parallel orphaned-count query; surface `orphanedActive` field; reject stale-shape cache reads |

## Files Created

None — extending the existing test file at `src/app/api/v1/queue/health/__tests__/route.test.ts`.

## AC-by-AC implementation

### US-001 — Filter oldestActive to recently-touched rows

Add the constant + narrow the where clause via `updatedAt: { gte: freshnessCutoff }`.

### US-002 — Surface orphaned-active count

Run `db.submission.count` + `findFirst` with `updatedAt: { lt: freshnessCutoff }` in parallel via `Promise.all`. Both wrapped in `withDbTimeout(..., 4_000)`.

### US-003 — Cache invalidation

Validate the parsed cached body has `"orphanedActive" in parsed` before returning. Pre-deploy cache entries fall through to recompute and the new shape replaces them within 30s (TTL).

### US-004 — Tests

Three new TCs in `__tests__/route.test.ts`:
- `oldestActive null when all active rows are stale`
- `orphanedActive.count reflects stale-row count`
- `cached response without orphanedActive triggers recompute`

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Real queue stalls (5-30 min) hidden by 6h freshness window | None | 6h is well above scan completion times (typically <1 min); real stalls show up in `oldestActive` long before 6h |
| Orphan count query slow on large `Submission` table | Low (today) | Existing `Submission` indexes are `@@index([state])` and `@@index([state, priority, createdAt])` — there is **no `(state, updatedAt)` composite**. At current row counts the queries run in a few ms, but if the orphan pile grows large the detection query slows down precisely when needed. Follow-up increment should add `@@index([state, updatedAt])`. Out of scope here — this hotfix is route-only, no schema migrations |
| Cache shape mismatch causes 30s of recomputation | Acceptable | One-time cost on deploy; cache TTL is 30s anyway |
| Existing tests break due to new where-clause shape | Low — additive | Mocks in existing tests typically don't over-specify the where clause |

## Test Strategy

- **Unit (vitest)**: 3 new TCs in `__tests__/route.test.ts`
- **Regression**: full `src/app/api/v1/queue/health/__tests__/` suite must pass

## Rollout

Single CF Worker deploy via `wrangler deploy`. The 30s cache TTL means stale-shape responses self-heal within 30s. No coordination with VMs needed.
