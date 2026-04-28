---
increment: 0798-admin-counters-match-queue-strict
title: "Admin counters use strict verified filter to match queue and home"
type: bug
priority: P2
status: active
created: 2026-04-28
---

# 0798: Admin counters use strict verified filter to match queue and home

## Problem

After 0797 deployed, the admin `/admin/dashboard` still visibly differs from `/queue` and `/`. Live production check at 02:25 UTC:

| Counter | Admin | Queue / Home | Gap | Reason |
|---|---|---|---|---|
| Total Skills (admin) / Verified (queue, home) | 117,411 | 117,381 | 30 | Admin counts `Skill WHERE NOT isDeprecated` (broad), queue counts `Skill WHERE status IN (VERIFIED, CERTIFIED) AND NOT isDeprecated` (strict). The 30 missing skills exist in the registry but are not yet verified. |
| Pending Review (admin) / Active (queue) | 3,068 | 3,042 | 26 | Admin counts `Submission WHERE state = RECEIVED` (narrow). Queue counts `state IN (RECEIVED, TIER1_SCANNING, TIER2_SCANNING)` (broader). Plus the live-DB-vs-cache-tick drift adds noise. |

0797 deliberately preserved both filters in the cache so admin could keep its "broader" counts. User feedback after deploy: that decision was wrong — they want **one number per metric across all three pages**, even if it means admin uses the strict filter.

A secondary issue uncovered by 0797: the new `totalSkillsAll` field stays at `0` in the prod cache because the Phase 1b Skill SQL keeps timing out. The watchdog carries `verifiedSkills` forward from prior values (so queue/home stay fresh) but `totalSkillsAll` has no prior to carry from. The admin route correctly detects the shape-stale state and falls through to live DB (per 0797 AC-US3-02), so admin shows correct numbers — they just don't match queue/home because of the broad/strict filter difference. After 0798, admin no longer reads `totalSkillsAll`, so the Phase 1b failure becomes irrelevant to the user-visible dashboard.

## Goal

Make `/admin/dashboard` show **the same number** as `/queue` and `/` for every shared metric: Total Skills, Pending Review, Total Submissions. Approval Rate stays admin-specific (computed from PUBLISHED/REJECTED strict states — those are populated reliably).

## Out of scope

- Removing `totalSkillsAll` / `pendingReceived` from the `QueueStats` interface — leave them defined for backwards-compat with the just-deployed shape; mark as unused-by-admin.
- Investigating the Phase 1b Skill SQL failure root cause — separate operational increment.
- Changing label text on the admin dashboard cards — labels stay (Total Skills, Pending Review, Approval Rate, Total Submissions); only the underlying numbers change.

## User Stories

### US-001: Admin "Total Skills" matches queue "Verified"
**Project**: vskill-platform

**As an** admin
**I want** the admin dashboard's "Total Skills" card to show the same number as the queue page's "Verified" card and the home page's verified badge
**So that** the three pages no longer appear to disagree

**Acceptance Criteria**:
- [x] **AC-US1-01**: `/api/v1/admin/stats` returns `totalSkills = snapshot.verifiedSkills` (strict filter: `status IN VERIFIED|CERTIFIED AND NOT isDeprecated`) instead of `snapshot.totalSkillsAll`.
- [x] **AC-US1-02**: When the admin route falls through to live DB (cold start, KV unavailable, or `verifiedSkills === 0` shape-stale), the live count uses the SAME strict filter: `prisma.skill.count({ where: { status: { in: ['VERIFIED', 'CERTIFIED'] }, isDeprecated: false } })`.
- [x] **AC-US1-03**: The numerical value rendered on `/admin/dashboard` for "Total Skills" equals the value rendered on `/queue` for "Verified" within the same cron tick (zero drift when both pages read from the same fresh cache).

### US-002: Admin "Pending Review" matches queue "Active"
**Project**: vskill-platform

**As an** admin
**I want** the admin dashboard's "Pending Review" card to show the same number as the queue page's "Active" card
**So that** the in-flight submission count is consistent across pages

**Acceptance Criteria**:
- [x] **AC-US2-01**: `/api/v1/admin/stats` returns `pendingCount = snapshot.active` (broader filter: `state IN RECEIVED, TIER1_SCANNING, TIER2_SCANNING`) instead of `snapshot.pendingReceived`.
- [x] **AC-US2-02**: When the admin route falls through to live DB, the live pending count uses the same broader filter: `prisma.submission.count({ where: { state: { in: ['RECEIVED', 'TIER1_SCANNING', 'TIER2_SCANNING'] } } })`.
- [x] **AC-US2-03**: TIER1_SCANNING and TIER2_SCANNING submissions ARE pending action (being scanned right now) — surfacing them under "Pending Review" is correct semantics.

### US-003: Shape-stale fallback simplified
**Project**: vskill-platform

**As a** platform operator
**I want** the admin route's stale-cache fallback to only fire when truly necessary
**So that** admin requests hit the cache the moment it's available, not after a 30-min cron tick wait

**Acceptance Criteria**:
- [x] **AC-US3-01**: The shape-stale check `(s.totalSkillsAll ?? 0) === 0 || (s.pendingReceived ?? 0) === 0` is removed from the admin route — the route no longer reads those fields, so they cannot trigger the fallback.
- [x] **AC-US3-02**: The admin route now reads from cache whenever `snap.source !== 'empty'` AND `s.verifiedSkills > 0` AND `s.total > 0`. (Both fields are reliably populated by 0791-era code, so this is the correct freshness gate.)
- [x] **AC-US3-03**: When the cache snapshot is `source === 'empty'` (true cold start), the route falls through to the live-DB path which uses the same strict/active filters as the cache.

### US-004: approvalRate stays admin-specific
**Project**: vskill-platform

**As an** admin
**I want** the approval rate to keep using strict PUBLISHED/REJECTED states for the math
**So that** the percentage reflects only completed decisions, not in-flight retries

**Acceptance Criteria**:
- [x] **AC-US4-01**: `approvalRate = computeApprovalRate(snapshot.publishedStrict, snapshot.rejectedStrict)` — unchanged from 0797.
- [x] **AC-US4-02**: When `publishedStrict + rejectedStrict === 0`, `approvalRate === 0` — unchanged.

## Test Plan

- **Unit (Vitest)** — extend `src/app/api/v1/admin/stats/__tests__/route.test.ts`:
  - replace the "maps fresh queue snapshot fields" assertion: `body.totalSkills === snapshot.verifiedSkills` and `body.pendingCount === snapshot.active`.
  - replace the live-DB fallback test: assert `prisma.skill.count` is called with the strict filter `{ status: { in: ['VERIFIED', 'CERTIFIED'] }, isDeprecated: false }` and `prisma.submission.count` for pending uses the broad active filter.
  - delete or rewrite the shape-stale-pre-0797 test (no longer applicable).
  - keep approvalRate decimal-precision test as-is (still uses `publishedStrict`/`rejectedStrict`).
- **E2E (Playwright)** — extend `tests/e2e/0797-admin-stats-cross-page-consistency.spec.ts` (or fork into `0798-*`):
  - assert `admin.totalSkills === queue.verifiedSkills` (zero gap, not just within tolerance)
  - assert `admin.pendingCount === queue.active`

## Risks

- **R-001**: Admins lose visibility of the ~30 unverified-but-not-deprecated skills. Mitigation: if anyone needs that count, expose via a separate /api/v1/admin/raw-counts endpoint in a future increment. Not surfaced today, no UX regression.
- **R-002**: TIER1/TIER2_SCANNING counted as "pending" might inflate the number visually. Mitigation: those states ARE pending action — the label is accurate. Queue page already shows them under "Active" without complaints.
