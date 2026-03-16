# Tasks: Fix init sync-setup command + brownfield repo onboarding

## Track A: Brownfield repo detection

### T-001: Add misplacedRepos to NextStepsContext
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given NextStepsContext type → When checking fields → Then `misplacedRepos?: string[]` exists

### T-002: Implement scanMisplacedRepos() in path-utils.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Test**: Given `repositories/my-repo/.git` exists → When `scanMisplacedRepos()` runs → Then returns `["my-repo"]`

### T-003: Export scanMisplacedRepos from init/index.ts barrel
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given barrel import → When importing `scanMisplacedRepos` → Then function is callable

### T-004: Call scanMisplacedRepos in init.ts and pass to showNextSteps
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-06 | **Status**: [x] completed
**Test**: Given init runs with 1-level repos → When showNextSteps called → Then misplacedRepos is populated

### T-005: Render misplaced-repos warning in next-steps.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given `misplacedRepos: ["my-repo"]` → When showNextSteps runs → Then warning with mkdir/mv shown

## Track B: sync-setup CLI command

### T-006: Write src/cli/commands/sync-setup.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08 | **Status**: [x] completed
**Test**: Given `.specweave/config.json` missing → When syncSetupCommand runs → Then exits with error message

### T-007: Register sync-setup in bin/specweave.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given `specweave sync-setup --quick` → When executed → Then exits 0 (not "unknown command")

### T-008: Write unit tests for scanMisplacedRepos
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01–AC-US2-06 | **Status**: [x] completed
**Test**: Given various filesystem layouts → When scanMisplacedRepos runs → Then correct names returned

### T-009: Write unit tests for syncSetupCommand
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07, AC-US1-08 | **Status**: [x] completed
**Test**: Given --quick flag → When syncSetupCommand runs → Then no prompts, exits 0

### T-010: Build, verify CLI works, commit and push
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: Given npm run build succeeds → When `specweave sync-setup --quick` runs → Then exits 0
