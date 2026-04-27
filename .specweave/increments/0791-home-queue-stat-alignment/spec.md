---
increment: 0791-home-queue-stat-alignment
title: "Align homepage hero counters with /queue stats (single KV source)"
type: bug
priority: P2
---

# 0791: Align homepage hero counters with /queue stats

## Problem

The homepage hero shows two counters — `116,118 verified · 112.8k pending review` — that visibly disagree with the `/queue` page's stat cards (`Total: 112,783`, `Published: 107,783`). Two separate root causes:

1. **Submission total drift** (fixed in this increment as a follow-on to the previous turn): home read `submissionTotal` from `platform:stats` KV while `/queue` read `total` from `submissions:stats-cache` KV. The two crons tick at slightly different times and write to different keys, so the visible numbers diverge by 1–2k between refreshes. Already addressed: home now reads queue cache for the submission total. Remaining work below.

2. **Verified-skill gap** (this increment's primary scope): home's "verified" badge sources `verifiedCount` from `platform:stats` (Skill table, `status IN (VERIFIED, CERTIFIED) AND NOT isDeprecated` → 116,118). `/queue` shows `Published` from the Submission state machine (`state IN (PUBLISHED, AUTO_APPROVED, VENDOR_APPROVED, EXPANDED)` → 107,783). The 8,335-row gap is real — registry has skills imported pre-submission-queue or via crawlers — but appearing as two contradictory counters on adjacent pages reads as a bug.

## Goal

Make the homepage hero and `/queue` stat cards source both numbers (verified-skill count and submission total) from a single KV cache, so they are guaranteed identical and never drift between cron ticks. Submission lifecycle counts (`Active`, `Published`, `Rejected`, `Blocked`) remain on `/queue` unchanged — they answer a different question.

## Out of scope

- Backfilling Submission rows for legacy/crawler-imported Skills.
- Renaming or removing the `/queue` page's existing `Published` stat (still useful for ops as a "publish-events" audit count).
- Changing the platform-stats cron's `verifiedCount` computation; it remains the source for `/api/v1/stats` consumers.

## User Stories

### US-001: Home and queue agree on verified-skill count
**Project**: vskill-platform

**As a** visitor reading the registry homepage
**I want** the "verified" number on the home page to match the verified-skill count surfaced by the queue stats
**So that** the two pages don't appear to contradict each other

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `QueueStats` interface gains a `verifiedSkills: number` field (Skill table count, `status IN (VERIFIED, CERTIFIED) AND NOT isDeprecated`).
- [ ] **AC-US1-02**: `computeQueueStats` populates `verifiedSkills` in the same Phase 1b round-trip that already queries Skill for `avgScore` — no extra DB query, no extra cron budget.
- [ ] **AC-US1-03**: The Phase 1b SQL is extended to a single statement returning both `avg_score` and `verified` columns; existing 2s `withDbTimeout` budget is preserved.
- [ ] **AC-US1-04**: When the new field is missing in a stale cache payload (older deploys), readers backfill `verifiedSkills ??= 0` so old KV blobs don't crash the page.
- [ ] **AC-US1-05**: `EMPTY_QUEUE_STATS` and the failure-sentinel snapshot include `verifiedSkills: 0`.

### US-002: Homepage badge reads from queue cache
**Project**: vskill-platform

**As a** visitor
**I want** the homepage badge to render from the queue-stats KV when available
**So that** both pages tick in lockstep

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `HeroHeading` (and `InlineStats` where applicable) prefer `queueSnap.stats.verifiedSkills` over `stats.verifiedCount` from `getHomeStats()` when the queue snapshot is fresh (`> 0`).
- [ ] **AC-US2-02**: Fallback to `stats.verifiedCount` when `queueSnap.stats.verifiedSkills` is `0` or the queue snapshot is degraded — homepage never renders an em-dash for a value that platform-stats can supply.
- [ ] **AC-US2-03**: `formatSearchPlaceholder` continues to floor the chosen count to thousands ("Search 116,000+ verified skills…") — placeholder math unchanged.
- [ ] **AC-US2-04**: Both reads (`getHomeStats` + `readQueueStatsSnapshot`) execute in `Promise.all` so the hero render path adds at most one round-trip latency, not two serial waits.

### US-003: Backwards-compatible cache shape
**Project**: vskill-platform

**As a** platform operator
**I want** the queue-stats KV blob to upgrade gracefully when the new field lands
**So that** a deploy doesn't show "0 verified" until the next cron tick

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When `readQueueStatsSnapshot` parses a cached blob that pre-dates `verifiedSkills`, it backfills the field from `_memQueueStats` if available, otherwise leaves it as `0` and lets the homepage fallback path use platform-stats.
- [ ] **AC-US3-02**: The freshness watchdog (`isFreshQueueStats`) is unchanged — `verifiedSkills` does not affect freshness scoring.

## Test Plan

- **Unit (Vitest)**: extend `queue-stats-refresh.test.ts` to assert the merged Phase 1b query path returns `{ avgScore, verifiedSkills }`, regression-guards a transient drop to 0, and that EMPTY snapshot carries `verifiedSkills: 0`.
- **Component (RTL)**: extend `HeroStats.test.tsx` (creating if absent) to assert: (a) when queue snapshot has `verifiedSkills: 116118`, badge renders `116,118`; (b) when queue snapshot is degraded, badge falls back to `stats.verifiedCount`.
- **E2E (Playwright)**: load `/` and `/queue` in the same test, scrape the badge text from `/` and the stat card text from `/queue`, assert both render the same number for verified count and submission total.

## Risks

- **R-001**: Adding a column-projection to the existing Skill `AVG(certScore)` query slightly increases query work. Mitigated by keeping it a single statement (one round-trip) and reusing the existing 2s budget; the COUNT runs against the same indexed `isDeprecated` partial.
- **R-002**: Stale KV blobs without `verifiedSkills` would render `0` if not handled. Mitigated by AC-US3-01 fallback.
