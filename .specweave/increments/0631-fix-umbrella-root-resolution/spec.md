---
increment: 0631-fix-umbrella-root-resolution
title: "Fix Umbrella Root Resolution and Prevent Stale .specweave in Child Repos"
status: active
priority: P1
type: bug
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Umbrella Root Resolution and Prevent Stale .specweave in Child Repos

## Problem Statement

14+ code paths in the SpecWeave CLI bypass `resolveEffectiveRoot()` by constructing `.specweave/` paths directly from `process.cwd()`. When the CLI runs from a child repo inside an umbrella workspace, these paths resolve to the child repo instead of the umbrella root, creating stale `.specweave/` directories with orphaned state, logs, and reports in child repos. The dashboard specifically fails to display correct data because `dashboard.ts:24` uses `process.cwd()` directly. Additionally, `detectUmbrellaParent()` checks `config.repository.umbrellaRepo` (not set in config) instead of `config.umbrella.enabled` (set in config), creating inconsistent detection behavior.

## Goals

- Eliminate all `process.cwd() + '.specweave'` bypass patterns in favor of a single utility
- Dashboard correctly resolves and displays umbrella root data from any child repo
- Config-based umbrella detection is consistent across all code paths
- Comprehensive test coverage for root resolution functions
- Clean up existing stale `.specweave/` directories in child repos

## User Stories

### US-001: Dashboard Correctly Resolves Umbrella Root
**Project**: specweave

**As a** developer using an umbrella workspace
**I want** the dashboard to show correct increment data regardless of which child repo I run it from
**So that** I can monitor project progress without navigating to the umbrella root

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given an umbrella workspace with `umbrella.enabled: true`, when `specweave dashboard` is run from a child repo, then the dashboard reads increments from the umbrella root `.specweave/` directory
- [ ] **AC-US1-02**: Given an umbrella workspace, when `dashboard-server.ts addProject()` registers a project, then it uses the resolved umbrella root path for the project's `.specweave/` directory
- [ ] **AC-US1-03**: Given a standalone (non-umbrella) project, when `specweave dashboard` is run, then behavior is unchanged and uses `process.cwd()` as the project root

---

### US-002: State, Logs, and Reports Write to Umbrella Root
**Project**: specweave

**As a** developer using an umbrella workspace
**I want** all CLI operations to write state, logs, and reports to the umbrella root `.specweave/`
**So that** child repos stay clean and all data is centralized

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given an umbrella workspace, when any of the 14 identified modules (qa-runner, autonomous-executor, revert-wip-limit, logs, cross-linker, content-distributor, command-integration, notification-manager, schedule-persistence, log-aggregator, sync-audit-logger, permission-enforcer, sync-scheduled) resolve `.specweave/` paths, then they use the umbrella root, not `process.cwd()`
- [ ] **AC-US2-02**: Given an umbrella workspace, when a CLI command writes state files, then no new files are created under any child repo's `.specweave/` directory
- [ ] **AC-US2-03**: Given a `getSpecweavePath()` utility in `find-project-root.ts`, when called with no arguments, then it returns the resolved umbrella root's `.specweave/` directory path

---

### US-003: Config Flag Detection Is Consistent
**Project**: specweave

**As a** developer configuring an umbrella workspace
**I want** `detectUmbrellaParent()` to check the same config flag as `findUmbrellaRoot()`
**So that** umbrella detection works reliably without requiring `repository.umbrellaRepo` to be set

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given a config with `umbrella.enabled: true` but no `repository.umbrellaRepo`, when `detectUmbrellaParent()` is called, then it detects the umbrella parent using the `umbrella.enabled` flag
- [ ] **AC-US3-02**: Given a config with both `umbrella.enabled: true` and `repository.umbrellaRepo` set, when `detectUmbrellaParent()` is called, then it detects the umbrella parent (backward compatible)
- [ ] **AC-US3-03**: Given a standalone project config (no umbrella flags), when `detectUmbrellaParent()` is called, then it returns null

---

### US-004: Test Coverage for Umbrella Resolution Functions
**Project**: specweave

**As a** maintainer
**I want** comprehensive tests for `findUmbrellaRoot()`, `resolveEffectiveRoot()`, `detectUmbrellaParent()`, and `getSpecweavePath()`
**So that** regressions in root resolution are caught before release

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given a test suite for `find-project-root.ts`, when tests run, then `findUmbrellaRoot()` is tested with umbrella-enabled config, standalone config, and missing config scenarios
- [ ] **AC-US4-02**: Given a test suite, when tests run, then `resolveEffectiveRoot()` is tested returning umbrella root when umbrella is enabled and cwd when it is not
- [ ] **AC-US4-03**: Given a test suite, when tests run, then `detectUmbrellaParent()` is tested with `umbrella.enabled`, `repository.umbrellaRepo`, both flags, and neither flag
- [ ] **AC-US4-04**: Given a test suite, when tests run, then `getSpecweavePath()` is tested returning the correct `.specweave/` path for both umbrella and standalone modes

---

### US-005: Stale Child Repo .specweave Cleanup
**Project**: specweave

**As a** developer using an umbrella workspace
**I want** orphaned `.specweave/` directories in child repos to be removed
**So that** there is no confusion about which `.specweave/` directory is authoritative

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given stale `.specweave/increments/` directories exist in `repositories/anton-abyzov/vskill/` (increments 0569, 0570, 0572), when cleanup is performed, then those directories are deleted
- [ ] **AC-US5-02**: Given stale `.specweave/increments/` directories exist in `repositories/anton-abyzov/specweave/` (increments 0576, 0590, 0593, 0595, 0599, 0605), when cleanup is performed, then those directories are deleted
- [ ] **AC-US5-03**: Given cleanup is performed, when verified against the umbrella archive, then all deleted increments have matching entries in the umbrella's `.specweave/increments/` (active or archived)

## Out of Scope

- Adding a CLI command to auto-detect and clean stale child `.specweave/` dirs (future increment)
- Refactoring the umbrella config schema itself (would be a breaking change)
- Addressing any other `process.cwd()` usages outside the 14 identified modules
- Dashboard UI redesign or feature additions

## Non-Functional Requirements

- **Performance**: `getSpecweavePath()` must add no measurable overhead (single function call wrapping existing `resolveEffectiveRoot()`)
- **Compatibility**: Changes must not break standalone (non-umbrella) mode — all existing paths must work identically
- **Security**: No user input reaches path resolution unsanitized (internal paths only)

## Edge Cases

- **No config.json exists**: `getSpecweavePath()` falls back to `process.cwd() + '/.specweave'`
- **Umbrella root unreachable**: If `resolveEffectiveRoot()` returns cwd (umbrella not found), all modules still function correctly in standalone mode
- **Nested umbrella detection**: Only one level of umbrella resolution is supported — a child repo cannot itself be an umbrella parent
- **Concurrent writes**: Multiple CLI processes writing to umbrella `.specweave/state/` simultaneously must not corrupt state (existing behavior, no regression)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Missed bypass pattern in untested module | 0.3 | 4 | 1.2 | Grep for all `process.cwd()` + `.specweave` patterns after fix |
| Breaking standalone mode | 0.2 | 8 | 1.6 | Test both umbrella and standalone in AC-US1-03, AC-US3-03 |
| Stale cleanup deletes active data | 0.1 | 9 | 0.9 | Verify each orphan exists in umbrella archive before deletion (AC-US5-03) |

## Technical Notes

### Dependencies
- `find-project-root.ts` — core module, new `getSpecweavePath()` added here
- `resolveEffectiveRoot()` — existing function, already handles umbrella detection
- `findUmbrellaRoot()` — checks `config.umbrella.enabled`
- `detectUmbrellaParent()` — currently checks `config.repository.umbrellaRepo`, needs to also check `umbrella.enabled`

### Constraints
- Must not change function signatures of existing public APIs
- `getSpecweavePath()` is a new export, additive only

### Key Files
- `src/utils/find-project-root.ts` — new utility + config flag fix
- `src/cli/commands/dashboard.ts` — primary fix target
- `src/cli/commands/dashboard-server.ts` — addProject() fix
- 12 additional modules listed in US-002 AC-US2-01

## Success Metrics

- Zero `process.cwd()` + `.specweave` bypass patterns remain in codebase (verified by grep)
- Dashboard shows correct data when run from any child repo in umbrella workspace
- Test coverage for `find-project-root.ts` umbrella functions reaches 90%+
- No stale `.specweave/` directories remain in child repos
