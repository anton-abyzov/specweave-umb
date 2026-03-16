---
increment: 0476-skill-metadata-alignment
title: Fix stale/inconsistent skill metadata display
type: bug
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix stale/inconsistent skill metadata display

## Problem Statement

Users see contradictory or stale information on skill detail pages due to three independent bugs:

1. **False OFFLINE badge** -- The repo health checker treats all non-ok HTTP responses and network errors identically as `OFFLINE`. A transient GitHub failure (rate limit 403/429, server 5xx, timeout) caches `OFFLINE` for 5 minutes, while the source link on the same page resolves fine. Users see "OFFLINE" next to a working repo link.

2. **Broken eval verdict mapping** -- The `ScanChip` status mapping in `page.tsx` only handles `EFFECTIVE -> PASS` and `DEGRADING -> FAIL`. The three remaining `EvalVerdict` values (`MARGINAL`, `INEFFECTIVE`, `ERROR`) all fall through to `"PENDING"`, so users see "PENDING 75/100 Marginal" -- a contradictory display mixing a real score with a pending status chip.

3. **Stale eval data from silent DB failures** -- `eval-store.ts` updates the `Skill` record (evalScore, evalVerdict, evalRunCount, lastEvalAt) via fire-and-forget `.catch()`. If the DB write fails silently, the skill detail page shows stale eval data with no indication of when the evaluation actually ran.

## Goals

- Eliminate false OFFLINE badges caused by transient GitHub API failures
- Show the correct verdict chip color for all five `EvalVerdict` enum values
- Surface eval freshness so users can assess data staleness
- Ensure eval DB updates are durable (not silently swallowed)

## User Stories

### US-001: Accurate repo health badge
**Project**: vskill-platform
**As a** user viewing a skill detail page
**I want** the repo health badge to only show OFFLINE when the repo genuinely does not exist (HTTP 404)
**So that** I am not misled about skill availability by transient GitHub failures

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a GitHub API response with status 404, when the repo health check runs, then the result status is `OFFLINE`
- [x] **AC-US1-02**: Given a GitHub API response with status 403 (rate limit), 429, or 5xx, when the repo health check runs, then the result status is `UNKNOWN` (not `OFFLINE`)
- [x] **AC-US1-03**: Given a network error or timeout during the GitHub API call, when the repo health check runs, then the result status is `UNKNOWN`
- [x] **AC-US1-04**: Given a cached `UNKNOWN` status, when the badge component renders, then no badge is displayed (component returns null)
- [x] **AC-US1-05**: Given a cached `UNKNOWN` result, when the KV TTL is checked, then it expires after 300 seconds (same as OFFLINE TTL) for quick retry

---

### US-002: Complete eval verdict chip mapping
**Project**: vskill-platform
**As a** user viewing eval results
**I want** the quality status chip to show the correct verdict (PASS / WARN / NEUTRAL / FAIL / ERROR) instead of "PENDING" for evaluated skills
**So that** the display is consistent with the actual evaluation outcome

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill with `evalVerdict = "EFFECTIVE"`, when the scan chip renders, then the status is `PASS` (green)
- [x] **AC-US2-02**: Given a skill with `evalVerdict = "MARGINAL"`, when the scan chip renders, then the status is `WARN` (amber)
- [x] **AC-US2-03**: Given a skill with `evalVerdict = "INEFFECTIVE"`, when the scan chip renders, then the status is `NEUTRAL` (gray)
- [x] **AC-US2-04**: Given a skill with `evalVerdict = "DEGRADING"`, when the scan chip renders, then the status is `FAIL` (red)
- [x] **AC-US2-05**: Given a skill with `evalVerdict = "ERROR"`, when the scan chip renders, then the status is `ERROR` (red) with the `scanColor` function returning the correct color
- [x] **AC-US2-06**: Given the `scanColor` helper, when called with `WARN`, `NEUTRAL`, or `ERROR`, then it returns the correct hex color (`#F59E0B`, `#6B7280`, `#EF4444` respectively)

---

### US-003: Eval freshness timestamp
**Project**: vskill-platform
**As a** user viewing a skill detail page
**I want** to see when a skill was last evaluated
**So that** I can assess whether the evaluation data is current

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a skill with `lastEvalAt` set, when the eval section renders, then a relative timestamp (e.g., "3d ago") appears inline after the run count
- [x] **AC-US3-02**: Given a skill with `lastEvalAt` is null (never evaluated), when the eval section renders, then no freshness timestamp is shown
- [x] **AC-US3-03**: Given the eval-store `storeEvalRun` function, when the Skill record DB update is performed, then the update is awaited (not fire-and-forget) so failures propagate
- [x] **AC-US3-04**: Given the eval-store `storeEvalRun` function, when the Skill record DB update fails, then the error is logged and re-thrown (caller can handle retry)

## Out of Scope

- Retry logic for failed eval DB updates at the caller level (callers already have error handling)
- Proactive re-checking of UNKNOWN repos (the 5-min TTL handles natural retry)
- Changing the KV fire-and-forget pattern for eval KV writes (KV is the hot cache, DB is durable)
- Historical eval trend charts or eval comparison UI
- Changes to the repo health API route's fallback behavior when `getCloudflareContext` fails

## Technical Notes

### Key Files
- `src/lib/repo-health-checker.ts` -- Add `UNKNOWN` status, only 404 maps to `OFFLINE`
- `src/lib/repo-health-store.ts` -- Extend `RepoHealthResult` type with `UNKNOWN`, set 5-min TTL
- `src/app/skills/[owner]/[repo]/[skill]/RepoHealthBadge.tsx` -- Hide badge for `UNKNOWN`
- `src/app/api/v1/skills/[owner]/[repo]/[skill]/repo-health/route.ts` -- Update fallback to `UNKNOWN`
- `src/app/skills/[owner]/[repo]/[skill]/page.tsx` -- Fix verdict-to-status mapping, add freshness timestamp, add `WARN`/`NEUTRAL`/`ERROR` to `scanColor`
- `src/lib/eval/eval-store.ts` -- Await Skill DB update instead of fire-and-forget
- `src/lib/__tests__/repo-health-checker.test.ts` -- Update TC-010 through TC-013 for new UNKNOWN status, add 404-only OFFLINE test

### Architecture Decisions
- **UNKNOWN hides the badge entirely** -- no badge is better than a misleading one. The existing pattern (line 59 returns null for falsy status) naturally supports this.
- **Only HTTP 404 = OFFLINE** -- one clean boundary. All other failures (403, 429, 5xx, network errors) produce UNKNOWN.
- **UNKNOWN uses same 5-min TTL** -- quick retry for transient failures, consistent with existing OFFLINE TTL.
- **KV write stays fire-and-forget** -- only the Skill DB update is promoted to awaited. KV is a hot cache and its loss is non-critical.

## Success Criteria

- Zero false OFFLINE badges when GitHub API is rate-limited or temporarily unavailable
- All five `EvalVerdict` values render with distinct, correct chip colors
- Eval freshness visible on every skill that has been evaluated
- No silent data loss from eval DB update failures
