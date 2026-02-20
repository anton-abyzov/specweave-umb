# Tasks

### T-001: Increase queue batch timeout
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test**: Given wrangler.jsonc → When deployed → Then max_batch_timeout is 30

### T-002: Add timeout wrapper to queue consumer
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test**: Given processSubmission takes > 25s → When consumer runs → Then timeout caught, message retried

### T-003: Add Tier 2 LLM timeout
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test**: Given AI.run takes > 8s → When tier2 runs → Then falls back to tier1 scoring

### T-004: Add stuck submission recovery to cron
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**Test**: Given submission stuck in TIER1_SCANNING for 10 min → When cron runs → Then re-enqueued or marked FAILED

### T-005: Fix slug collision with repo-scoped slugs
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test**: Given two repos with skill "frontend-design" → When both published → Then both exist as separate skills

### T-006: Add KV list cursor pagination
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
**Test**: Given > 1000 skill keys → When getPublishedSkillsList called → Then all returned via cursor

### T-007: Smart crawler dedup (per-skill)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test**: Given repo with 10 skills, 8 already verified → When crawler submits → Then only 2 new submitted

### T-008: Add queue status observability endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test**: Given stuck submissions exist → When GET /api/v1/admin/queue/status → Then returns stuck count and stats

### T-009: Add rate limit to discover endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] pending
**Test**: Given 21st discover request from same IP → When called → Then 429 returned

### T-011: Authenticated users get higher rate limits
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test**: Given authenticated user → When 11th submission in 1 hour → Then allowed (limit is 30/hour, not 10)

### T-010: Deploy and verify all fixes
**User Story**: ALL | **Status**: [ ] pending
**Test**: Given all changes deployed → When queue runs → Then stuck items recover, new submissions dedup properly
