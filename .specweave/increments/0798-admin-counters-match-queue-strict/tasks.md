---
increment: 0798-admin-counters-match-queue-strict
---

# 0798: Tasks

### T-001: Update admin route mapping (cache path)
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given a fresh queue snapshot | When `/api/v1/admin/stats` runs | Then `body.totalSkills === snap.stats.verifiedSkills`, `body.pendingCount === snap.stats.active`, `body.totalSubmissions === snap.stats.total`, `body.approvalRate === computeApprovalRate(publishedStrict, rejectedStrict)`. Shape-stale check no longer references totalSkillsAll/pendingReceived.

### T-002: Update admin route fallback (live-DB path)
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-02, AC-US2-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given the cache snapshot is empty or `verifiedSkills === 0` | When the live fallback runs | Then `prisma.skill.count` uses `{status IN VERIFIED|CERTIFIED, isDeprecated: false}` and `prisma.submission.count` for pending uses `{state IN RECEIVED, TIER1_SCANNING, TIER2_SCANNING}`. `body.cached === false`.

### T-003: Update admin route unit tests
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All US-1..US-4 | **Status**: [x] completed
**Test Plan**: Given existing 0797 admin route tests | When updated for 0798 mappings | Then "fresh snapshot" test asserts strict mappings, "live DB fallback" test asserts strict filters, "shape-stale pre-0797" test removed/rewritten, approvalRate tests unchanged.

### T-004: Build vskill-platform
**User Story**: US-001..US-004 | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: Given updated route + tests | When `npm run build && npm run build:worker` | Then both succeed and the new mapping is in `.open-next/server-functions/default/handler.mjs`.

### T-005: Deploy to production
**User Story**: US-001..US-004 | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: Given the worker bundle | When `npm run deploy` | Then verified-skill.com serves new admin route. Verify via public stats endpoint and (with admin auth via Chrome MCP) /api/v1/admin/stats — assert totalSkills === verifiedSkills.

### T-006: Verify in user's browser via Chrome MCP
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-03, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given user-authenticated Chrome | When navigating to /admin/dashboard, /queue, / | Then "TOTAL SKILLS" on admin === "VERIFIED" on queue === "X verified" on home, and "PENDING REVIEW" on admin === "ACTIVE" on queue.
