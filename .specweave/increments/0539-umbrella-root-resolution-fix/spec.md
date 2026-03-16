---
increment: 0539-umbrella-root-resolution-fix
title: Fix umbrella root resolution in 3 artifact-creation paths
type: bug
priority: P1
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: Umbrella root resolution in artifact-creation paths

## Problem Statement

In umbrella mode (`umbrella.enabled: true`), three code paths create `.specweave/` artifacts (state files, logs, increment reports) inside child repos instead of the umbrella root. This happens because they use `process.cwd()` directly instead of the existing `resolveEffectiveRoot()` utility.

When a user runs SpecWeave commands from a child repo directory (e.g., `repositories/anton-abyzov/specweave/`), files land in the child's `.specweave/` instead of the umbrella root's `.specweave/`. This causes state fragmentation: the umbrella root cannot find state written by these paths, and child repos accumulate stale `.specweave/state/` directories.

Additionally, `src/hooks/platform.ts` contains a duplicate `findProjectRoot()` implementation instead of re-exporting from the canonical `utils/find-project-root.ts`, creating a maintenance risk where fixes to one copy don't reach the other.

## Goals

- All `.specweave/` artifact writes resolve to the umbrella root when umbrella mode is active
- Eliminate the duplicated `findProjectRoot()` in platform.ts
- Zero behavior change for single-repo (non-umbrella) projects

## User Stories

### US-001: Spec detector resolves to umbrella root
**Project**: specweave

**As a** developer working in a child repo of an umbrella project
**I want** the spec detector to read specs from the umbrella root's `.specweave/docs/internal/specs/`
**So that** living docs and spec detection work correctly regardless of which child repo is my CWD

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given CWD is a child repo inside an umbrella project, when `detectSpecsByFeatureId()` runs, then it reads from `<umbrella-root>/.specweave/docs/internal/specs/` (not `<child-repo>/.specweave/docs/internal/specs/`)
- [x] **AC-US1-02**: Given CWD is a single-repo project (no umbrella), when `detectSpecsByFeatureId()` runs, then it reads from `<project-root>/.specweave/docs/internal/specs/` (existing behavior preserved)

---

### US-002: Active increment manager resolves to umbrella root
**Project**: specweave

**As a** developer working in a child repo of an umbrella project
**I want** the active increment manager to read/write state in the umbrella root
**So that** increment activation state is consistent across all child repos

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given CWD is a child repo inside an umbrella project, when `ActiveIncrementManager` is constructed without an explicit `rootDir`, then `stateFile` points to `<umbrella-root>/.specweave/state/active-increment.json`
- [x] **AC-US2-02**: Given an explicit `rootDir` is passed to the constructor, then that value is used as-is (no override)
- [x] **AC-US2-03**: Given CWD is a single-repo project, when `ActiveIncrementManager` is constructed without `rootDir`, then `stateFile` points to `<project-root>/.specweave/state/active-increment.json`

---

### US-003: Activation tracker resolves to umbrella root
**Project**: specweave

**As a** developer working in a child repo of an umbrella project
**I want** the skill activation tracker to write state to the umbrella root
**So that** activation records are centralized and not scattered across child repos

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given CWD is a child repo inside an umbrella project, when `getStatePath()` is called without a `projectRoot` argument, then it returns a path under `<umbrella-root>/.specweave/state/`
- [x] **AC-US3-02**: Given an explicit `projectRoot` is passed, then that value is used as-is
- [x] **AC-US3-03**: Given CWD is a single-repo project, when `getStatePath()` is called without arguments, then it returns a path under `<project-root>/.specweave/state/`

---

### US-004: Deduplicate platform.ts findProjectRoot
**Project**: specweave

**As a** maintainer of the SpecWeave codebase
**I want** `platform.ts` to re-export `findProjectRoot` from `utils/find-project-root.ts`
**So that** there is a single canonical implementation and fixes propagate automatically

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `src/hooks/platform.ts`, then it does not contain its own `findProjectRoot()` function body -- it re-exports from `utils/find-project-root.ts`
- [x] **AC-US4-02**: Given any existing caller of `platform.findProjectRoot()`, then it continues to work with the same signature and return values (no breaking change)

## Out of Scope

- Auditing all other `process.cwd()` uses across the codebase (only the 3 identified paths are in scope)
- Changing the `resolveEffectiveRoot()` logic itself
- Adding umbrella awareness to hooks that already work correctly
- Modifying config loading or umbrella detection logic

## Technical Notes

### Dependencies
- `src/utils/find-project-root.ts` -- canonical source of `resolveEffectiveRoot()`, `findProjectRoot()`
- Already used by 15+ other call sites in the codebase

### Constraints
- Must not change behavior for single-repo projects
- `ActiveIncrementManager` constructor must remain backward-compatible (explicit `rootDir` still honored)
- `platform.ts` re-export must preserve the same function signature

### Architecture Decisions
- Use `resolveEffectiveRoot()` (not `findProjectRoot()` or `getProjectRoot()`) because it handles the umbrella-vs-single-repo decision: returns umbrella root when inside umbrella, project root otherwise

## Non-Functional Requirements

- **Performance**: `resolveEffectiveRoot()` does a filesystem walk-up; already used in 15+ hot paths, so no measurable regression
- **Compatibility**: Works on Windows, macOS, Linux path formats (inherited from existing utility)

## Edge Cases

- CWD is the umbrella root itself: `resolveEffectiveRoot()` returns CWD, same as `process.cwd()` -- no behavioral change
- CWD is outside any SpecWeave project: `resolveEffectiveRoot()` falls back to `process.cwd()` -- same as current behavior
- `.specweave/config.json` is missing or malformed: `resolveEffectiveRoot()` falls back to `process.cwd()` -- graceful degradation
- Explicit `rootDir`/`projectRoot` passed to constructors: bypass resolution entirely, use the explicit value

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Callers of platform.ts findProjectRoot break after dedup | 0.1 | 5 | 0.5 | Re-export preserves exact same signature; test with existing callers |
| resolveEffectiveRoot adds latency in tight loops | 0.1 | 2 | 0.2 | Already used in 15+ paths without issue; fs walk is cached by OS |

## Success Metrics

- All 3 fixed call sites resolve to umbrella root when CWD is a child repo
- Zero regressions in single-repo mode (existing tests pass)
- platform.ts has no duplicate findProjectRoot body
- TDD test coverage >= 90% for changed files
