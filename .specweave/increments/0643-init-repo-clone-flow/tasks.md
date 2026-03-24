# Tasks: Fix init repo cloning prompt flow

## Phase 1: TDD Red — Write failing tests

### T-001: Write test suite for init repo clone flow
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01 | **Status**: [x] completed

**Test Plan**:
- **File**: `tests/unit/cli/commands/init-repo-clone-flow.test.ts`
- **Tests**:
  - **TC-001**: clone-github sub-choice calls promptRepoUrlsLoop
    - Given user picks "Start empty" > "Clone from GitHub" in non-empty dir
    - When init processes the migration sub-choice
    - Then `promptRepoUrlsLoop` is called with `(targetDir, language)`
  - **TC-002**: clone-github prevents post-scaffold re-ask
    - Given user cloned repos via migration sub-menu
    - When init reaches post-scaffold section
    - Then `promptProjectSetup` is NOT called
  - **TC-003**: copy-local prevents post-scaffold re-ask
    - Given user copied local repo via migration sub-menu
    - When init reaches post-scaffold section
    - Then `promptProjectSetup` is NOT called
  - **TC-004**: brownfield with .git + empty repos/ shows prompt
    - Given dir has `.git/` and empty `repositories/`
    - When init reaches post-scaffold section
    - Then `promptProjectSetup` IS called
  - **TC-005**: populated repos/ skips prompt
    - Given dir has `repositories/some-org/some-repo`
    - When init reaches post-scaffold section
    - Then `promptProjectSetup` is NOT called
  - **TC-006**: greenfield (no .git) shows prompt
    - Given fresh empty dir with no `.git`
    - When init reaches post-scaffold section
    - Then `promptProjectSetup` IS called
  - **TC-007**: CI mode always skips prompt
    - Given `isCI = true`
    - When init runs
    - Then `promptProjectSetup` is NOT called
  - **TC-008**: umbrella No does not block child repo prompt
    - Given user says No to "Connect workspace root to GitHub?"
    - When init reaches post-scaffold with empty repos/
    - Then `promptProjectSetup` IS still called

**Dependencies**: None

## Phase 2: TDD Green — Implement fixes

### T-002: Add reposClonedInMigration state variable
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Dependencies**: T-001

### T-003: Handle clone-github sub-choice
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Dependencies**: T-002

### T-004: Replace !hasGit guard with repositories-emptiness check
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01 | **Status**: [x] completed

**Dependencies**: T-002

## Phase 3: Verify

### T-005: Run regression tests
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: all | **Status**: [x] completed

**Results**: 8/8 new tests pass, 107/107 regression tests pass (init.test.ts: 84, init-integration.test.ts: 13, repo-connect-loop.test.ts: 10). TypeScript compiles clean.

**Dependencies**: T-003, T-004
