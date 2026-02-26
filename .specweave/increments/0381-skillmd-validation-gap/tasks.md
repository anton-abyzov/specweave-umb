# 0381 — Tasks

## Phase 1: Discovery Source Verification

### T-001: Add GraphQL batch SKILL.md verification to discoverFromRepoSearch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given 5 repos found by topic search (3 with SKILL.md, 2 without) → When discoverFromRepoSearch completes → Then only 3 repos returned as candidates

Files: `src/lib/crawler/github-discovery.ts`

### T-002: Add GraphQL batch SKILL.md verification to discoverFromNpm
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given 4 npm packages with GitHub repos (2 with SKILL.md, 2 without) → When discoverFromNpm completes → Then only 2 repos returned as candidates

Files: `src/lib/crawler/github-discovery.ts`

### T-003: Extract shared GraphQL batch verification helper
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US4-01 | **Status**: [x] completed
**Test**: Given a list of repo fullNames → When batchVerifySkillMd called → Then returns Set of fullNames that have SKILL.md at HEAD. Given GraphQL 403/429 → When retry with backoff → Then succeeds or returns empty set (fail-closed)

Files: `src/lib/crawler/github-discovery.ts`

## Phase 2: Route-Level Defense-in-Depth

### T-004: Add SKILL.md validation to batch submission path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given batch submission with 3 skills (2 have SKILL.md, 1 does not) → When POST /api/v1/submissions with skills array → Then only 2 submissions created. Given batch where all skills lack SKILL.md → When POST → Then 422 returned

Files: `src/app/api/v1/submissions/route.ts`

## Phase 3: Internal Fallback Fix

### T-005: Restrict body-params fallback to non-internal requests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given internal request with skillName but discoverSkillsEnhanced returns empty → When POST /api/v1/submissions → Then 200 with empty submissions array (no submission created). Given external request with skillName that passed checkSkillMdExists → When discoverSkillsEnhanced skipped → Then fallback applies and submission created normally

Files: `src/app/api/v1/submissions/route.ts`

## Phase 4: Tests

### T-006: Unit tests for GraphQL batch verification helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: Given mock GraphQL responses → When batchVerifySkillMd called → Then correctly filters repos by SKILL.md existence. Given rate limit response → When backoff applied → Then retries and returns results or empty set

Files: `src/lib/crawler/__tests__/github-discovery.test.ts`

### T-007: Integration tests for route batch validation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given mocked checkSkillMdExists → When batch submission includes invalid skills → Then only valid skills create submissions

Files: `src/app/api/v1/submissions/__tests__/route.skillmd-check.test.ts`

### T-008: Integration tests for internal fallback restriction
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given internal request with zero discovery results → When POST /api/v1/submissions → Then no submission created and 200 returned

Files: `src/app/api/v1/submissions/__tests__/route.skillmd-check.test.ts`
