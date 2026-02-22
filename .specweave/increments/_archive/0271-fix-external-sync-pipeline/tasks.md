# Tasks: Fix External Sync Pipeline

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Fix loadUserStoriesForIncrement

### T-001: Add deriveFeatureId fallback to loadUserStoriesForIncrement
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: Given spec.md has no feature_id in frontmatter or metadata.json → When loadUserStoriesForIncrement is called → Then it uses deriveFeatureId() to derive the feature ID and logs a warning

### T-002: Add spec.md parsing fallback when living docs folder missing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given living docs folder does not exist for the feature → When loadUserStoriesForIncrement is called → Then it parses user stories from spec.md body using regex and logs a warning

## Phase 2: Surface suppressed errors

### T-003: Add error logging to checkExistingIssue in ExternalIssueAutoCreator
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given metadata.json has invalid JSON → When checkExistingIssue is called → Then it logs a warning with the error message

### T-004: Add error logging to checkExistingGitHubIssue in sync-progress
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given metadata.json read fails → When checkExistingGitHubIssue is called → Then it logs a warning

### T-005: Add error logging to detectActiveIncrement in sync-progress
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given active-increment.json is missing or corrupt → When detectActiveIncrement is called → Then it logs a debug message

## Phase 3: Fix externalLinks format checking

### T-006: Add externalLinks check to ExternalIssueAutoCreator.checkExistingIssue
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given metadata.json has externalLinks.github.issueNumber → When checkExistingIssue is called → Then it returns the existing issue reference

### T-007: Add externalLinks check to sync-progress checkExistingGitHubIssue
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test**: Given metadata.json has externalLinks.github.issues → When checkExistingGitHubIssue is called → Then it returns true

## Phase 4: Verification

### T-008: Verify TypeScript compilation
**User Story**: US-001, US-002, US-003 | **Status**: [x] completed
**Test**: Given all edits are made → When TypeScript is compiled → Then no type errors
