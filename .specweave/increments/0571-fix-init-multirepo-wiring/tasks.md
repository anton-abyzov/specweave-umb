---
increment: 0571-fix-init-multirepo-wiring
generated: 2026-03-18
total_tasks: 13
coverage_target: 90
---

# Tasks: Fix init multi-repo flow

## US-001: Fix post-scaffold execution order

### T-001: Move post-scaffold block before git init in init.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed
**Test**: Given a greenfield directory with no `.git`, when `specweave init` runs the reordered flow, then `promptProjectSetup()` is called before `git init` executes, confirming `hasGit` is false at the time the check runs

### T-002: Remove dead multi-repo confirm question from init.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed
**Test**: Given the dead confirm prompt at init.ts lines 308-317 (`isMultiRepo` question), when the file is edited, then no `confirm()` call for "multiple repos" exists before the post-scaffold block

### T-003: Remove dead config writes (repository.structure, project.structureDeferred)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] completed
**Test**: Given the dead config writes at init.ts lines 419-423, when they are removed, then grep for `repository.structure` and `structureDeferred` in init.ts returns zero matches

### T-004: Write unit tests for execution order and single-repo non-regression
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed
**Test**: Given `tests/unit/cli/commands/init-multirepo.test.ts`, when TC-003 (greenfield fires promptProjectSetup) and TC-004 (existing project skips it) run, then both pass with vi.hoisted mocks verifying call order

---

## US-002: Add deferred multi-repo option

### T-005: Wire deferred multi-repo to multiProject.enabled in config
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04
**Status**: [x] completed
**Test**: Given user selects the deferred multi-repo path during init, when the config batch-update runs, then config.json contains `multiProject: { enabled: true }` and does NOT contain `umbrella.enabled` or `repository.structure`

### T-006: Create repositories/ directory for deferred multi-repo
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] completed
**Test**: Given user selects the deferred multi-repo option, when init completes, then `repositories/` directory exists under the project root and is empty (no repos cloned)

### T-007: Preserve CI/non-interactive behavior (no multi-repo prompt in CI)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05
**Status**: [x] completed
**Test**: Given `isCI = true` or `process.stdin.isTTY = false`, when init runs, then `promptProjectSetup()` is not called and no multi-repo prompt appears

### T-008: Write unit tests for deferred multi-repo config and directory creation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed
**Test**: Given init-multirepo.test.ts, when TC-001 (multiProject.enabled written), TC-002 (repositories/ created), and CI-skip tests run, then all assertions pass and config.json snapshot shows no umbrella.enabled

---

## US-003: Wire clone-repos to umbrella auto-setup

### T-009: Wire "Clone GitHub repos" path through cloneReposIntoWorkspace and scanUmbrellaRepos
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [x] completed
**Test**: Given user selects "Clone GitHub repos" and provides repo URLs, when cloning succeeds, then `cloneReposIntoWorkspace()` is called placing repos at `repositories/{org}/{name}/`, followed by `scanUmbrellaRepos()` populating `childRepos` in config.json; when cloning fails partway, then init continues non-fatally and shows a warning without blocking

### T-010: Add optional sync-setup chain after multi-repo setup
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-05
**Status**: [x] completed
**Test**: Given isMultiRepo is true and repos are set up, when the confirm prompt "Connect external tools now?" appears and user accepts, then `syncSetupCommand()` is dynamically imported and called; when user declines, then `syncSetupCommand()` is NOT called and init completes normally

### T-011: Write unit tests for clone wiring and sync-setup chain
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given init-multirepo.test.ts, when TC-005 (sync-setup offered) and TC-006 (sync-setup skipped) run with vi.hoisted mocks for cloneReposIntoWorkspace, scanUmbrellaRepos, and syncSetupCommand, then all pass; when clone-failure mock is used, then init resolves successfully with warning output

---

## US-004: Update next-steps messaging for multi-repo

### T-012: Add isMultiRepo to NextStepsContext and update next-steps.ts conditional
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed
**Test**: Given NextStepsContext with `isMultiRepo: true` and `isUmbrella: false`, when `showNextSteps()` renders, then output contains `specweave get owner/repo` examples and does NOT contain `migrate-to-umbrella`; given `isMultiRepo: false` and `isUmbrella: false`, then `migrate-to-umbrella` still appears; given `isUmbrella: true`, then `migrate-to-umbrella` is hidden

---

## US-005: Dead code cleanup

### T-013: Delete repository-setup.ts and its test file, replace resolve-structure.ts with deprecation stub
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] completed
**Test**: Given repository-setup.ts (1921 lines) and repository-setup.test.ts are deleted and resolve-structure.ts is replaced with a ~25-line stub, when `npx vitest run` executes, then all remaining tests pass with zero regressions; when `resolveStructureCommand()` is called, then it returns `{ success: false, message: containing 'deprecated' }` and logs a deprecation warning; given grep for type exports from the deleted file, then all needed types are present in types.ts with no compile errors
