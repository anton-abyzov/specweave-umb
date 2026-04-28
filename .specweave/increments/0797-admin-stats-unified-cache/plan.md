---
increment: 0797-admin-stats-unified-cache
---

# 0797: Implementation Plan

## Architecture Decisions

### AD-1: Extend QueueStats with admin-required fields, do not introduce a new cache

The queue-stats cron (`refreshQueueStats`) already runs every 30 min and writes a comprehensive snapshot to `submissions:stats-cache`. Reusing that single cache is strictly better than maintaining a separate admin cache:
- One cron tick → one write → one read on every page → guaranteed consistency.
- Phase 1 SQL already scans the `Submission.state` column once for five FILTER COUNTs; adding three more (RECEIVED-only, PUBLISHED-only, REJECTED-only) reuses the same sequential scan in PostgreSQL.
- Phase 1b SQL already scans `Skill WHERE NOT isDeprecated` for `AVG(certScore)` and `COUNT(... WHERE status verified)`; adding a third bare `COUNT(*)` projection (totalSkillsAll) reuses the same scan.
- No new KV key, no new cron, no new DB row.

Rejected: a separate `dashboard:stats` cache fed by its own cron. That is the current architecture and is the source of the drift.

### AD-2: Strict-state vs broad-state counters live side-by-side in the cache

Admin needs strict `state = PUBLISHED` for approval-rate math, while queue/home use broad `state IN (PUBLISHED, AUTO_APPROVED, VENDOR_APPROVED, EXPANDED)` for the public "Published" counter. These are different questions with different correct answers — the cache carries both, named distinctly:

| Field | Filter | Used by |
|---|---|---|
| `published` | `state IN (PUBLISHED, AUTO_APPROVED, VENDOR_APPROVED, EXPANDED)` | /queue Published card, telemetry |
| `publishedStrict` | `state = PUBLISHED` | admin approval-rate numerator |
| `rejected` | `state IN (REJECTED, TIER1_FAILED, DEQUEUED)` | /queue Rejected card |
| `rejectedStrict` | `state = REJECTED` | admin approval-rate denominator (with publishedStrict) |
| `active` | `state IN (RECEIVED, TIER1_SCANNING, TIER2_SCANNING)` | /queue Active card |
| `pendingReceived` | `state = RECEIVED` | admin Pending Review card |
| `verifiedSkills` | `Skill WHERE status IN (VERIFIED, CERTIFIED) AND NOT isDeprecated` | home/queue Verified card |
| `totalSkillsAll` | `Skill WHERE NOT isDeprecated` | admin Total Skills card |

Naming convention: the un-suffixed name keeps its current meaning (broad/public). Admin variants get `Strict` (state) or `All` (broader skill filter).

Rejected: changing the existing `published`/`active` semantics — would silently shift the queue page numbers and is out of scope.

### AD-3: Admin route falls back to live-DB on stale-shape cache

A pre-0797 KV blob lacks the four new fields. Backfill in `readQueueStatsSnapshot` returns `0`. The admin route detects "snapshot has total > 0 but totalSkillsAll === 0" → treats this as a shape-stale signal → falls through to the existing live-DB path for that single request. Next cron tick (≤30 min) repopulates the blob and the route returns to the cache path.

This avoids the alternative — block deploy on the cache being warm — and keeps the admin dashboard correct from the moment the deploy lands.

### AD-4: Tier distribution stays out of the cache

The admin dashboard's tier distribution chart (`Skill.groupBy({ by: certTier })`) is admin-only and the data shape (Record<string, number>) does not fit cleanly into the QueueStats interface used by public pages. Keeping it as a separate live DB query in the route:
- Avoids polluting the public cache contract.
- The `groupBy` runs against an indexed table (115K rows) and returns in ~50ms — a non-issue for an admin-only page that loads on click.

## File Map

| File | Change |
|---|---|
| `src/lib/cron/queue-stats-refresh.ts` | Extend `QueueStats` interface (4 new optional fields); extend Phase 1 SQL with 3 FILTER COUNTs; extend Phase 1b SQL with `totalSkillsAll` COUNT; carry-forward seed for new fields; same in `ensureFreshStats` watchdog. |
| `src/lib/queue/queue-stats-cache.ts` | Extend `EMPTY_QUEUE_STATS` with 4 new fields = 0; `backfillVerifiedSkills` → `backfillAdminFields` (or add a sibling fn) backfilling all four. |
| `src/app/api/v1/admin/stats/route.ts` | Rewrite: read `readQueueStatsSnapshot()`, map fields, compute approvalRate from strict counts; live-DB fallback on empty snapshot or shape-stale cache; tier distribution kept as separate live query; stop writing `dashboard:stats` KV. |
| `src/app/api/v1/admin/stats/__tests__/route.test.ts` | New test file: snapshot mapping, approvalRate decimal precision, fallback paths, auth guard. |
| `src/lib/cron/__tests__/queue-stats-refresh.test.ts` | Extend: 4 new fields populated in compute, EMPTY shape, watchdog carry-forward. |
| `src/lib/queue/__tests__/queue-stats-cache.timeout.test.ts` (or new sibling) | Extend: backfill returns 0 for missing new fields. |

## Sequence

1. **Cache shape first** — extend interface + EMPTY + backfill; keep cron writing old shape (nothing reads new fields yet). Tests pass with new fields = 0.
2. **Cron writes new fields** — extend Phase 1 + 1b SQL; watchdog populates same. Existing readers untouched (new fields ignored). Verify in dev with logs.
3. **Admin route flips** — replace internal counts with `readQueueStatsSnapshot()` + mapping + live-DB fallback. Stop writing `dashboard:stats`.
4. **Test surface** — admin route unit tests, e2e cross-page assertion.

## Backwards Compatibility

- Pre-0797 cache blob (lacking new fields): admin route detects shape-stale and falls through to live DB → admin dashboard continues to show real numbers, just not from cache for ~30 min until next cron tick.
- Pre-0797 deploy reading post-0797 cache: ignores new fields (TypeScript optional), no break.
- Deprecated `dashboard:stats` KV: left to expire naturally. No reader after this deploy.

## Open Questions

None — the architecture mirrors 0791 which is in production.
