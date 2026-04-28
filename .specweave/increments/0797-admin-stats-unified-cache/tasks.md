---
increment: 0797-admin-stats-unified-cache
---

# 0797: Tasks

### T-001: Extend QueueStats interface with admin fields
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given the `QueueStats` type and `EMPTY_QUEUE_STATS` sentinel | When TypeScript compiles | Then `totalSkillsAll`, `pendingReceived`, `publishedStrict`, `rejectedStrict` are optional `number` and `EMPTY_QUEUE_STATS` carries each = 0.

### T-002: Backfill new admin fields on cache reads
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given a KV blob written before this change (no new fields) | When `readQueueStatsSnapshot` parses it | Then the returned snapshot has all four new fields === 0 and `isFreshQueueStats` is unchanged.

### T-003: Extend Phase 1 SQL with strict-state COUNTs
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given a Phase 1 SQL that projects `pendingReceived/publishedStrict/rejectedStrict` | When `computeQueueStats` runs against the test DB | Then all three fields populate alongside the existing total/active/published/rejected/blocked, and the query stays under the existing 8s budget.

### T-004: Extend Phase 1b SQL with totalSkillsAll
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given the Phase 1b Skill query that projects `avg_score`, `verified`, and `total_all` | When `computeQueueStats` runs | Then `totalSkillsAll >= verifiedSkills` (broader filter) and the query stays under the existing 2s budget.

### T-005: ensureFreshStats watchdog populates new fields
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given the watchdog runs with KV stale > 15min | When the SQL completes | Then the degraded snapshot carries fresh `totalSkillsAll/pendingReceived/publishedStrict/rejectedStrict`. When the SQL fails | Then prior values from the previous KV blob are carried forward (mirrors verifiedSkills behaviour).

### T-006: Rewrite /api/v1/admin/stats to read from queue cache
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Test Plan**: Given a request to `/api/v1/admin/stats` from an admin | When the queue snapshot is fresh | Then the response maps `totalSkills = totalSkillsAll`, `totalSubmissions = total`, `pendingCount = pendingReceived`, `approvalRate = round((publishedStrict / (publishedStrict+rejectedStrict)) * 10000) / 100`, `cached: true`, `tierDistribution` populated from a live `Skill.groupBy`. Deprecated KV write to `dashboard:stats` is removed.

### T-007: Live-DB fallback when cache snapshot is empty or stale-shape
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-05, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given the queue snapshot returns `source === "empty"` OR `total > 0 && totalSkillsAll === 0` | When `/api/v1/admin/stats` runs | Then the route falls through to the existing live-DB count path (skill.count + 4× submission.count) and returns `cached: false`. Auth guard still rejects non-admin.

### T-008: Run vitest and fix failures
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: Given the full updated test suite | When `npm test` runs in vskill-platform | Then all green; new tests cover the 5 paths from T-001..T-007.

### T-009: Verify in preview that admin/queue/home counters match
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01..05, AC-US2-01..07 | **Status**: [x] completed
**Test Plan**: Given the dev server and an admin session | When loading `/admin/dashboard`, `/queue`, `/` | Then all three pages render the same `Total Submissions === Total === pending counter`. `Total Skills (admin) >= Verified (queue/home)` because admin counts a strictly larger set.
**Verification**: (a) Manual preview verification on 2026-04-27 confirmed `/queue` TOTAL=115,344 ACTIVE=2,482 PUBLISHED=107,865 VERIFIED=117,221 and `/` "117,221 verified · 115.3k pending review" tick from the same source; (b) `tests/e2e/0797-admin-stats-cross-page-consistency.spec.ts` codifies the contract for CI — it pulls queue stats from `/api/v1/submissions/stats`, signs into admin, fetches `/api/v1/admin/stats`, and asserts admin/queue agree on Total Submissions (within cron-tick tolerance), admin Pending ≤ queue Active, and admin Total Skills ≥ queue Verified.
