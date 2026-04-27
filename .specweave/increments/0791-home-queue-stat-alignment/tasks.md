---
increment: 0791-home-queue-stat-alignment
---

# 0791: Tasks

### T-001: Extend QueueStats with verifiedSkills field
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given the `QueueStats` interface | When TypeScript compiles | Then `verifiedSkills: number` is required and `EMPTY_QUEUE_STATS.verifiedSkills === 0`.

### T-002: Compute verifiedSkills in Phase 1b
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given a Phase 1b query that projects `avg_score` and `verified` | When `computeQueueStats` runs against the test DB | Then both fields are populated in <2s and the produced `QueueStats` carries `verifiedSkills > 0`.

### T-003: Backfill missing verifiedSkills on cache reads
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-04, AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given a KV blob written before this change (no `verifiedSkills`) | When `readQueueStatsSnapshot` parses it | Then the returned snapshot has `verifiedSkills === 0` and freshness scoring is unchanged.

### T-004: Hero badge prefers queue cache verifiedSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given queue snapshot with `verifiedSkills: 116118` | When `HeroHeading` renders | Then the badge shows `116,118 verified`. When the snapshot is degraded → falls back to `stats.verifiedCount`.

### T-005: Verify in preview that home and queue match
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01..05, AC-US2-01..04 | **Status**: [x] completed
**Test Plan**: Given the dev server | When loading `/` and `/queue` | Then the homepage badge number equals the queue API's `verifiedSkills` and both pending counters render the same `fmt(total)` string.
