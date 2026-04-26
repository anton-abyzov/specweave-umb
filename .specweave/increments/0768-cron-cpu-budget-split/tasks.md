# 0768 — Tasks

## T-001: Refactor scheduled() into cohort dispatcher
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given `controller.cron === "*/10 * * * *"`, when `scheduled()` runs, then the light cohort path is taken (covers ensureFreshStats + healthchecks + recovery). Given `controller.cron === "5,15,25,35,45,55 * * * *"`, then the heavy cohort path is taken (covers refreshPlatformStats + refreshQueueStats + cache warmups + enrichment + reconcile + discovery). Given an unknown cron string, default to the light cohort.

## T-002: Register the second cron schedule in wrangler.jsonc
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given `wrangler.jsonc` has `"crons": ["*/10 * * * *", "5,15,25,35,45,55 * * * *"]`, when the worker is deployed, then `wrangler deploy` output lists both schedules and `wrangler triggers deploy` exits 0.

## T-003: Add unit test for cohort dispatcher
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Vitest spec instantiates `scheduled()` with mocked controller variants and asserts which cron tasks fire, by mocking each refresh function and tracking invocations.

## T-004: Deploy + capture wrangler tail evidence both cohorts run
**User Story**: US-001 | **AC**: AC-US1-05 | **Status**: [x] completed
**Test Plan**: After `bash scripts/push-deploy.sh origin main`, `wrangler tail` shows `[cron] runLightCohort completed` and `[cron] runHeavyCohort completed` within one 10-min window.

## T-005: Playwright verify rejectionBreakdown populated
**User Story**: US-001 | **AC**: AC-US1-06 | **Status**: [x] completed
**Test Plan**: `https://verified-skill.com/api/v1/submissions/stats` returns `rejectionBreakdown.no_skillmd > 0` (or any sub-key non-zero). `/queue?filter=rejected` shows at least one reason pill.
