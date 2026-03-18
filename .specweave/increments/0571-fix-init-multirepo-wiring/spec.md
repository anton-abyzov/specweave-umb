---
increment: 0571-fix-init-multirepo-wiring
title: "Fix init multi-repo flow: wire question to real infrastructure"
type: feature
priority: P1
status: active
created: 2026-03-18
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix init multi-repo flow: wire question to real infrastructure

## Problem Statement

The `specweave init` command has broken multi-repo wiring. The post-scaffold repo-connect block runs AFTER git init, so the `!hasGit` check is always false for greenfield projects and `promptProjectSetup()` never fires. Dead code paths write config fields (`repository.structure`, `project.structureDeferred`) that nothing reads. The 1921-line `repository-setup.ts` is entirely orphaned. Users cannot set up multi-repo workspaces through init.

## Goals

- Fix execution order so repo-connect fires for greenfield projects
- Add a deferred multi-repo option that sets `multiProject.enabled` without requiring immediate repo cloning
- Wire the "Clone GitHub repos" path through existing `cloneReposIntoWorkspace()` and `scanUmbrellaRepos()`
- Clean up approximately 2400 lines of dead code
- Update next-steps messaging to guide multi-repo users toward `specweave get`

## User Stories

### US-001: Fix post-scaffold execution order (P0)
**Project**: specweave

**As a** developer running `specweave init` in a new directory
**I want** the repo-connect prompt to actually appear
**So that** I can configure my project structure during initialization

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a greenfield directory with no `.git`, when `specweave init` runs, then the post-scaffold block executes BEFORE `git init` so `!hasGit` is true and `promptProjectSetup()` fires
- [x] **AC-US1-02**: Given the dead multi-repo confirm question at init.ts:308-317, when init runs, then that code path is removed and no orphaned prompt appears
- [x] **AC-US1-03**: Given the dead config writes at init.ts:419-423 (`repository.structure: 'multiple'`, `project.structureDeferred: false`), when init runs, then those writes are removed (nothing reads them)
- [x] **AC-US1-04**: Given a single-repo project with no multi-repo intent, when `specweave init` runs, then the existing init flow is unchanged (no regressions)

---

### US-002: Add deferred multi-repo option (P1)
**Project**: specweave

**As a** developer who wants multi-repo but isn't ready to clone repos yet
**I want** a "Multiple repos (set up later)" option in the init flow
**So that** I can defer repo cloning while still marking my workspace as multi-project

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `promptProjectSetup()` in repo-connect.ts, when it renders options, then a 4th option "Multiple repos (set up later with `specweave get`)" appears alongside existing options
- [x] **AC-US2-02**: Given the user selects the deferred multi-repo option, when the selection is processed, then `multiProject.enabled` is set to `true` in config.json
- [x] **AC-US2-03**: Given the user selects the deferred multi-repo option, when the selection is processed, then a `repositories/` directory is created in the project root
- [x] **AC-US2-04**: Given the user selects the deferred multi-repo option, when config.json is written, then `umbrella.enabled` is NOT set (umbrella requires `childRepos` to be populated)
- [x] **AC-US2-05**: Given a CI or non-interactive environment, when `specweave init` runs, then the multi-repo option is skipped (existing non-interactive behavior preserved)

---

### US-003: Wire clone-repos to umbrella auto-setup (P1)
**Project**: specweave

**As a** developer who wants to clone repos during init
**I want** the "Clone GitHub repos" option to use real infrastructure and offer sync-setup
**So that** my workspace is fully configured with umbrella and external tool connections in one pass

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the user selects "Clone GitHub repos" during init, when repos are cloned, then existing `cloneReposIntoWorkspace()` is called which clones to `repositories/{org}/{name}/`
- [x] **AC-US3-02**: Given repos are successfully cloned, when cloning completes, then `scanUmbrellaRepos()` runs and auto-enables umbrella with `childRepos` populated in config.json
- [x] **AC-US3-03**: Given repo setup completes successfully, when the user is prompted "Connect external tools now?", then answering yes chains to `syncSetupCommand()`
- [x] **AC-US3-04**: Given a clone operation fails partway through, when the error occurs, then init continues without repos (non-fatal), a warning is shown, and the user is not blocked
- [x] **AC-US3-05**: Given the user declines the sync-setup prompt, when next-steps are shown, then `specweave sync-setup` appears in the next-steps list

---

### US-004: Update next-steps messaging for multi-repo (P1)
**Project**: specweave

**As a** developer who just initialized a multi-repo workspace
**I want** next-steps to show relevant commands like `specweave get`
**So that** I know how to add repos to my workspace instead of seeing irrelevant `migrate-to-umbrella` suggestions

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `multiProject.enabled` is true in config.json, when `showNextSteps()` renders, then it shows `specweave get owner/repo` and `specweave get "org/*"` examples instead of `migrate-to-umbrella`
- [x] **AC-US4-02**: Given umbrella is already enabled with repos cloned, when `showNextSteps()` renders, then `migrate-to-umbrella` is hidden (existing behavior preserved)
- [x] **AC-US4-03**: Given a single-repo project without multiProject.enabled, when `showNextSteps()` renders, then `migrate-to-umbrella` still appears in next-steps (existing behavior preserved)

---

### US-005: Dead code cleanup (P2)
**Project**: specweave

**As a** maintainer of the specweave codebase
**I want** orphaned files and dead config field writes removed
**So that** the codebase is smaller, more navigable, and free of misleading code paths

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `repository-setup.ts` has zero production imports, when cleanup is applied, then the file (1921 lines) is deleted
- [x] **AC-US5-02**: Given `repository-setup.test.ts` tests only dead code, when cleanup is applied, then the test file is deleted
- [x] **AC-US5-03**: Given `resolve-structure.ts` is referenced but no longer needed, when cleanup is applied, then it is replaced with a deprecation stub that logs a warning and no-ops
- [x] **AC-US5-04**: Given all cleanup changes are applied, when the full test suite runs, then all existing tests pass with no regressions
- [x] **AC-US5-05**: Given types exported from deleted files, when cleanup is applied, then all needed type exports are preserved in types.ts (no compile errors)

## Out of Scope

- Rewriting the entire init flow or changing its overall architecture
- Adding new CLI commands (using existing `specweave get`, `specweave sync-setup`)
- Multi-repo workspace management beyond the init entry point
- GUI or TUI enhancements to the init wizard
- Changes to `specweave get` or `specweave sync-setup` internals

## Non-Functional Requirements

- **Compatibility**: Init flow works on macOS, Linux, and Windows path formats
- **Performance**: No measurable change to init execution time (dead code removal only reduces bundle size)
- **Security**: No user input reaches path resolution unsanitized (existing constraint preserved)
- **Accessibility**: CLI prompts use clear labels and are screen-reader compatible (existing inquirer behavior)

## Edge Cases

- **No git installed**: If git is not on PATH, the `!hasGit` check is true regardless of execution order -- repo-connect should still fire
- **Existing `.git` directory**: If user runs init in an existing git repo, `!hasGit` is false and post-scaffold block is skipped (correct behavior, unchanged)
- **Empty repositories/ directory**: If deferred multi-repo is selected but no repos are ever cloned, `repositories/` exists empty -- `specweave get` handles this
- **Partial clone failure**: If 3 of 5 repos clone but 2 fail, the 3 successful repos are kept, umbrella is set up with those 3, and warnings list the 2 failures
- **CI/headless environment**: All interactive prompts are skipped, defaults apply, no multi-repo question asked

## Technical Notes

### Dependencies
- `cloneReposIntoWorkspace()` -- existing function, no changes needed
- `scanUmbrellaRepos()` -- existing function, no changes needed
- `syncSetupCommand()` -- existing function, chained after repo setup
- `promptProjectSetup()` in repo-connect.ts -- modified to add 4th option

### Constraints
- Must not break existing single-repo init flow
- `umbrella.enabled` must only be set when `childRepos` are actually populated
- Deprecation stub for `resolve-structure.ts` must warn but not throw

### Architecture Decisions
- Deferred multi-repo uses `multiProject.enabled` (not `umbrella.enabled`) because umbrella requires populated `childRepos`
- Post-scaffold block moves before git init rather than removing the `!hasGit` guard, preserving the guard's intent for existing repos

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Execution order change breaks existing init for repos with `.git` | 0.2 | 8 | 1.6 | AC-US1-04 explicitly tests single-repo unchanged behavior |
| Deleted files have hidden imports not caught by static analysis | 0.1 | 6 | 0.6 | AC-US5-04 requires full test suite pass; AC-US5-05 verifies type exports |
| `resolve-structure.ts` deprecation stub breaks callers | 0.3 | 5 | 1.5 | Stub returns safe no-op values matching original return types |
| Clone failure handling leaves workspace in inconsistent state | 0.2 | 5 | 1.0 | AC-US3-04 requires non-fatal handling with warning; umbrella only set up for successful clones |

## Success Metrics

- `specweave init` in a greenfield directory shows `promptProjectSetup()` options (currently broken, must work)
- Deferred multi-repo creates `repositories/` and sets `multiProject.enabled` without `umbrella.enabled`
- Clone path produces working umbrella with `childRepos` populated
- Approximately 2400 lines of dead code removed (repository-setup.ts + dead config writes + dead prompts)
- All existing tests pass with zero regressions
