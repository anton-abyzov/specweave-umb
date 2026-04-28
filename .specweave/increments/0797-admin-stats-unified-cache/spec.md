---
increment: 0797-admin-stats-unified-cache
title: Admin dashboard reads from unified queue-stats KV cache
type: bug
priority: P2
status: completed
---

# 0797: Admin dashboard reads from unified queue-stats KV cache

## Problem

The admin `/admin/dashboard` cards drift from the public `/queue` and `/` (home) counters. Screenshots taken on 2026-04-27 show:

| Counter | Admin Dashboard | Queue / Home | Drift |
|---|---|---|---|
| Total Skills (admin) / Verified (queue, home) | 117,222 | 117,066 | 156 |
| Pending Review (admin) / Active (queue) | 2,514 | 2,501 | 13 |
| Total Submissions (admin) / Total (queue) | 115,318 | 115,306 | 12 |

Two separate root causes:

1. **Two KV blobs**: `/api/v1/admin/stats` writes its own KV key `dashboard:stats` (30s TTL) and re-runs five Prisma counts. `/queue` and `/` read from `submissions:stats-cache` (refreshed by the queue-stats cron). The two payloads tick at different times, producing the 12–13 row drift on submission counters.
2. **Different SQL filters**: admin's `totalSkills` column counts every `Skill WHERE NOT isDeprecated` (117,222), but queue/home's `verifiedSkills` filters down to `status IN (VERIFIED, CERTIFIED) AND NOT isDeprecated` (117,066). The 156-row gap is real (skills with non-verified statuses) but appearing as two contradicting numbers on adjacent admin pages reads as a bug.

This is the same architecture problem 0791-home-queue-stat-alignment fixed for the home ↔ queue pair. That increment closed without including the admin surface.

## Goal

Make `/admin/dashboard` source all four numeric cards (Total Skills, Pending Review, Approval Rate, Total Submissions) from the same `submissions:stats-cache` KV blob that queue and home read from. Three pages tick in lockstep, never drift between cron rounds. Tier distribution stays a live DB `groupBy` (admin-only, not in the public cache). The deprecated `dashboard:stats` KV key stops being written.

## Out of scope

- Renaming admin labels (Total Skills, Pending Review) — meaning is preserved.
- Renaming or repurposing the existing `published` / `active` / `verifiedSkills` fields — they retain their current semantics for queue/home.
- Backfilling or migrating the deprecated `dashboard:stats` KV blob — it expires in 30s.
- Changing the `/api/v1/admin/submissions/state-counts` endpoint (different concern, drives the State Distribution chart).

## User Stories

### US-001: Admin counts come from the queue cache
**Project**: vskill-platform

**As an** admin reviewing the dashboard
**I want** the four stat cards to read from the same cache that powers /queue and /
**So that** the three pages always show consistent numbers when I tab between them

**Acceptance Criteria**:
- [x] **AC-US1-01**: `QueueStats` interface gains four optional fields populated by the queue-stats cron — `totalSkillsAll: number` (all `Skill WHERE NOT isDeprecated`), `pendingReceived: number` (`Submission WHERE state = RECEIVED`), `publishedStrict: number` (`Submission WHERE state = PUBLISHED`), `rejectedStrict: number` (`Submission WHERE state = REJECTED`).
- [x] **AC-US1-02**: `EMPTY_QUEUE_STATS` includes all four new fields = 0 so freshness checks and consumers see a defined shape.
- [x] **AC-US1-03**: `computeQueueStats` populates `pendingReceived`, `publishedStrict`, `rejectedStrict` in the existing Phase 1 single-round-trip SQL via additional `COUNT(*) FILTER (WHERE state = ...)` projections — no new query, same 8s timeout.
- [x] **AC-US1-04**: `computeQueueStats` populates `totalSkillsAll` in the existing Phase 1b Skill query via an additional `COUNT(*)` projection alongside `avg_score` and `verified` — same 2s timeout, single round-trip preserved.
- [x] **AC-US1-05**: `ensureFreshStats` watchdog populates the same four new fields when it writes a degraded snapshot (mirrors the existing `verifiedSkills` carry-forward pattern), so 15-min watchdog ticks do not zero the admin numbers.

### US-002: Admin route reads the unified cache
**Project**: vskill-platform

**As a** platform operator
**I want** /api/v1/admin/stats to read from submissions:stats-cache instead of writing its own KV blob
**So that** there is one source of truth for the displayed counters

**Acceptance Criteria**:
- [x] **AC-US2-01**: `/api/v1/admin/stats` calls `readQueueStatsSnapshot()` (or its cached wrapper) and maps the returned QueueStats fields onto the `DashboardStats` response — `totalSkills = totalSkillsAll`, `totalSubmissions = total`, `pendingCount = pendingReceived`, `approvalRate = computeApprovalRate(publishedStrict, rejectedStrict)`.
- [x] **AC-US2-02**: `approvalRate` retains its current decimal precision (`Math.round((published / decided) * 10000) / 100`) and returns `0` when `decided === 0`.
- [x] **AC-US2-03**: The route stops writing to `dashboard:stats` KV. The key is left to expire on its 30s TTL — no cleanup deploy needed.
- [x] **AC-US2-04**: Tier distribution (`Skill.groupBy({ by: certTier })`) remains a live DB query in the route — it is admin-only and not part of the queue/home cache contract.
- [x] **AC-US2-05**: When the queue cache snapshot is `source === "empty"` (cold start, KV unavailable), the route falls through to the existing live-DB count path (`prisma.skill.count`, `prisma.submission.count` × 4) so the admin dashboard never displays "—" or 0 across the board. (Note: stale-but-shaped snapshots — `freshness === "stale"` with all 0797 fields populated — are deliberately served from cache with `cached: false` rather than falling through to live DB. The carry-forward design ensures the admin/queue/home pages all see the same numbers even when degraded; falling through on stale would burn DB quota during a degraded-cron window without improving user-visible consistency.)
- [x] **AC-US2-06**: The `cached: boolean` flag in the response continues to reflect the source — `true` when read from KV/memory/DB cache, `false` when computed live by the fallback path.
- [x] **AC-US2-07**: `requireAdmin` auth guard is unchanged — no public endpoint changes.

### US-003: Backwards-compatible cache shape
**Project**: vskill-platform

**As a** platform operator
**I want** stale KV blobs (written by the previous deploy without the new fields) to upgrade gracefully
**So that** the admin dashboard does not show 0s in the window between deploy and the next cron tick

**Acceptance Criteria**:
- [x] **AC-US3-01**: `readQueueStatsSnapshot` backfills missing `totalSkillsAll`, `pendingReceived`, `publishedStrict`, `rejectedStrict` to `0` (mirrors the existing `backfillVerifiedSkills` pattern) so consumers can read the field unconditionally without TypeError.
- [x] **AC-US3-02**: When the admin route observes `totalSkillsAll === 0 && total > 0` in the snapshot (signal of a pre-0797 cache blob), it falls through to the live-DB path on every request until the next cron tick (≤30 min) repopulates the cache. Per-request DB cost is acceptable in this window because (a) it only triggers on the deploy → first-cron-tick gap, and (b) the alternative is rendering 0 across the board. The Skill table is never empty in production once seeded, so a 0 there is a true pre-0797 marker. (Note: an earlier draft also keyed on `pendingReceived === 0 && active > 0`, but `pendingReceived === 0` is a legitimate quiet-hour state and would force the slow path on every admin load — that clause was deliberately dropped before merge.)
- [x] **AC-US3-03**: The freshness watchdog (`isFreshQueueStats`) is unchanged — new fields do not affect freshness scoring.

## Test Plan

- **Unit (Vitest)**:
  - Extend `queue-stats-refresh.test.ts` to assert (a) the merged Phase 1 SQL projects `pendingReceived/publishedStrict/rejectedStrict`, (b) the merged Phase 1b SQL projects `totalSkillsAll`, (c) `EMPTY_QUEUE_STATS` carries the four new fields = 0, (d) `ensureFreshStats` watchdog populates the four fields and falls back to prior values on watchdog DB failure.
  - New `route.test.ts` for `/api/v1/admin/stats`: (a) reads from `readQueueStatsSnapshot` and maps fields correctly, (b) computes approvalRate with decimal precision, (c) falls back to live DB when snapshot is empty, (d) falls back to live DB when snapshot is pre-0797 shape, (e) auth guard rejects non-admin.
- **Integration**: existing `queue-stats-cache.test.ts` — verify backfill returns `0` for missing new fields without throwing.
- **E2E (Playwright)**: load `/admin/dashboard`, `/queue`, and `/` in the same test, assert all three counters render identical values (`Total Submissions === Total === pending counter from home if exposed`, and `Total Skills (admin) >= Verified (queue/home)` since admin counts a broader set).

## Risks

- **R-001**: Adding three FILTER COUNT clauses to Phase 1 SQL adds CPU work in PostgreSQL. Mitigated by all five clauses scanning the same indexed `state` column once — single sequential scan, sub-second on Neon's 115K-row Submission table.
- **R-002**: Pre-0797 cache blob shows 0s briefly after deploy. Mitigated by AC-US3-02 fallback → admin sees live numbers for ~30 min until next cron tick.
- **R-003**: A future cron failure that zeros `totalSkillsAll/pendingReceived` in a degraded write would silently flip admin to live-DB path on every load. Mitigated by `ensureFreshStats` watchdog carrying prior values forward (AC-US1-05) — same pattern proven for `verifiedSkills` in 0791.
