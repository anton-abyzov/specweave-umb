# Tasks: Submission Deduplication and Repository Hierarchy

## Feature: Repository Model (US-002)

### T-001: Add Repository model to Prisma schema
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test**: Given schema change → When `prisma generate` runs → Then Repository model exists with (owner, name) unique constraint, Skill and Submission have optional repositoryId FK

### T-002: Create and run database migration
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test**: Given migration → When applied → Then Repository table exists, FK columns added, indexes created

### T-003: Implement URL normalization utility
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending
**Test**: Given various GitHub URL formats (with .git, trailing slash, /tree/main path) → When normalizeRepoUrl() → Then returns canonical `https://github.com/{owner}/{repo}` and extracts (owner, name)

### T-004: Implement Repository CRUD (findOrCreate, getByUrl)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [ ] pending
**Test**: Given a repoUrl → When findOrCreateRepository() → Then Repository record exists, subsequent calls return same record

## Feature: Submission Deduplication (US-001)

### T-005: Implement dedup check for single submission
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test**: Given existing PENDING submission for (repoUrl, skillName) → When new submission attempted → Then returns existing submission. Given VERIFIED skill → Then returns already-verified. Given REJECTED → Then allows new submission.

### T-006: Add dedup check to POST /api/v1/submissions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
**Test**: Given POST with duplicate (repoUrl, skillName) → When submission exists in active state → Then returns 200 with existing submission and `duplicate: true` flag

## Feature: Bulk Submit (US-003)

### T-007: Implement bulkCreateSubmissions() in submission-store
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test**: Given 5 skills (2 new, 2 pending, 1 verified) → When bulkCreateSubmissions() → Then creates 2 submissions, returns per-skill status

### T-008: Create POST /api/v1/submissions/bulk endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test**: Given bulk request with repoUrl + skills array → When POST → Then returns 200 with results array showing created/skipped/already-verified per skill

### T-009: Rate limit adjustment for bulk submit
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Test**: Given bulk request with 130 skills → When POST → Then completes within 30s, rate limit counts as 1 request (not 130)

## Feature: Discovery Enrichment (US-004)

### T-010: Implement enrichDiscoveryWithStatus()
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test**: Given discovered skills list → When enriched against DB → Then each skill has status field (new/pending/verified/rejected)

### T-011: Update discover endpoint to include per-skill status
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test**: Given discover request for repo with some verified skills → When response → Then each skill has status field

### T-012: Update submit page UI with status badges and bulk submit
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-04, AC-US4-02, AC-US4-03 | **Status**: [ ] pending
**Test**: Given discovery with mixed statuses → When rendered → Then verified skills show badge, are pre-deselected. When "Submit Selected" clicked → Then calls bulk endpoint.
