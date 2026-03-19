---
increment: 0541-vskill-stale-file-cleanup
title: Vskill Stale File Cleanup
status: completed
priority: P1
type: fix
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Vskill Stale File Cleanup

## Problem Statement

The umbrella repo accumulates orphaned lockfiles from two sources:

1. **`skills-lock.json`** -- a legacy pre-vskill format that no code references anymore. Stale entries (e.g., `remotion-best-practices`) persist at the umbrella root with no mechanism to remove them.

2. **`vskill.lock` in child repos** -- when `installPlugin()` in `plugin-copier.ts` calls `getProjectRoot()`, it finds the nearest `.specweave/config.json`. In umbrella repos this is correct (umbrella root), but prior bugs caused child repos under `repositories/` to receive their own orphaned `vskill.lock` files that are never updated or read.

There is no cleanup mechanism for either case, so stale files accumulate indefinitely and can confuse `specweave doctor` diagnostics.

## Goals

- Eliminate all `skills-lock.json` files (dead format, no code references)
- Detect and remove orphaned `vskill.lock` files in umbrella child repos
- Surface stale-file issues via `specweave doctor` for visibility
- Auto-clean during `specweave refresh-plugins` so stale files do not persist after plugin operations
- Protect against corrupting concurrent writes via mtime guard

## User Stories

### US-001: Legacy Lockfile Removal
**Project**: specweave
**As a** SpecWeave CLI user
**I want** `skills-lock.json` files to be automatically detected and removed
**So that** dead lockfile artifacts do not accumulate in my project tree

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a project tree containing one or more `skills-lock.json` files at any depth, when cleanup runs, then all `skills-lock.json` files are deleted
- [x] **AC-US1-02**: Given a `skills-lock.json` with mtime less than 5 seconds ago, when cleanup runs, then the file is skipped to avoid corrupting a concurrent write
- [x] **AC-US1-03**: Given no `skills-lock.json` files exist in the project tree, when cleanup runs, then the function returns a result with `removedCount: 0` and no errors

### US-002: Orphaned Child-Repo Lockfile Cleanup
**Project**: specweave
**As a** developer using an umbrella repo
**I want** orphaned `vskill.lock` files in child repos to be detected and removed
**So that** only the umbrella root lockfile is authoritative

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given an umbrella repo with `vskill.lock` at the umbrella root and a `vskill.lock` inside `repositories/org/child-repo/`, when cleanup runs, then the child-repo `vskill.lock` is removed and the umbrella root `vskill.lock` is preserved
- [x] **AC-US2-02**: Given a child-repo `vskill.lock` with mtime less than 5 seconds ago, when cleanup runs, then the file is skipped and a warning is emitted
- [x] **AC-US2-03**: Given a non-umbrella project (no `umbrella.enabled` in config), when cleanup runs, then no `vskill.lock` files are touched

### US-003: Doctor Command Integration
**Project**: specweave
**As a** developer running `specweave doctor`
**I want** stale lockfile issues reported in the health check output
**So that** I can see and fix lockfile hygiene problems

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `skills-lock.json` files exist in the project tree, when `specweave doctor` runs, then a warning check result is returned listing each file path
- [x] **AC-US3-02**: Given orphaned `vskill.lock` files exist in child repos, when `specweave doctor` runs, then a warning check result is returned listing each orphaned path
- [x] **AC-US3-03**: Given `specweave doctor --fix` runs, when stale lockfiles are detected, then they are removed and the check result reports the count of removed files
- [x] **AC-US3-04**: Given no stale lockfiles exist, when `specweave doctor` runs, then the check returns status `pass` with message "no stale lockfiles"

### US-004: Refresh-Plugins Cleanup Hook
**Project**: specweave
**As a** developer running `specweave refresh-plugins`
**I want** stale lockfiles cleaned automatically during plugin refresh
**So that** plugin operations leave a clean project state

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `skills-lock.json` exists at the project root, when `specweave refresh-plugins` runs, then the legacy file is removed before plugin installation proceeds
- [x] **AC-US4-02**: Given an umbrella repo with orphaned child-repo `vskill.lock` files, when `specweave refresh-plugins` runs, then orphaned locks are removed
- [x] **AC-US4-03**: Given verbose mode is enabled, when cleanup removes files during refresh, then each removed file path is logged to the console

## Out of Scope

- Modifying `getProjectRoot()` or `resolveEffectiveRoot()` behavior -- the current resolution logic is correct for the umbrella root case
- Hash validation of lockfile entries against installed plugins -- delegated to existing `checkLockfileIntegrity()` in `InstallationHealthChecker`
- Cleanup of `~/.claude/` global state -- this increment only handles project-tree lockfiles
- Cleanup of `.specweave/` directories in child repos (tracked in separate increment per `project_umbrella_increment_placement_bug.md`)

## Technical Notes

### Dependencies
- `find-project-root.ts` -- `findUmbrellaRoot()`, `getProjectRoot()`, `resolveEffectiveRoot()`
- `cleanup-stale-plugins.ts` -- existing cleanup module to extend with new functions
- `installation-health-checker.ts` -- existing doctor checker class to extend with new methods
- `refresh-plugins.ts` -- existing command to wire cleanup into

### Constraints
- Cleanup must not delete files with mtime < 5 seconds to protect concurrent writes
- `skills-lock.json` deletion is aggressive (any depth in project tree)
- `vskill.lock` child-repo deletion only applies when `umbrella.enabled: true` in config
- All new functions must be testable in isolation (no global state dependencies)

### Architecture Decisions
- New cleanup logic added to `cleanup-stale-plugins.ts` as exported functions (not a new module) to consolidate stale-artifact cleanup in one place
- Doctor integration via new methods in `InstallationHealthChecker` class following existing patterns (`checkLegacyCommandsDirs`, `checkStaleCacheDirs`)
- Refresh-plugins integration via a single cleanup call at the start of `refreshPluginsCommand()` before plugin processing begins

## Non-Functional Requirements

- **Compatibility**: Works on macOS, Linux, and Windows path formats; handles symlinked `repositories/` directories
- **Performance**: Cleanup completes in under 500ms for typical umbrella repos (fewer than 20 child repos)
- **Reliability**: Never corrupts an active write (mtime guard); always returns a result object even on partial failure

## Edge Cases

- **No `.specweave/` directory**: Cleanup returns early with success and zero removals
- **Deeply nested `skills-lock.json`**: Found and removed at any depth (e.g., `repositories/org/repo/sub/skills-lock.json`)
- **Read-only filesystem**: Cleanup catches permission errors, reports them in the result, and continues with remaining files
- **Concurrent `refresh-plugins` execution**: mtime < 5s guard prevents deletion of files being actively written
- **Umbrella root `vskill.lock` missing**: Child-repo orphan detection still works; absence of umbrella lock does not prevent child cleanup
- **Symlinked child repos**: Resolve symlinks to avoid deleting through symlinks into unexpected directories

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Accidental deletion of active `vskill.lock` during concurrent plugin install | 0.2 | 6 | 1.2 | mtime < 5s guard skips recently modified files |
| `skills-lock.json` name collision with unrelated file in a child project | 0.1 | 4 | 0.4 | File is a dead format with no references; any collision is itself stale |
| Doctor check adds noise for non-umbrella users | 0.3 | 2 | 0.6 | Child-repo check gated behind `umbrella.enabled` config flag |

## Success Metrics

- Zero `skills-lock.json` files remain after `specweave doctor --fix` or `refresh-plugins`
- Zero orphaned `vskill.lock` files in child repos after cleanup
- `specweave doctor` reports `pass` for the new stale-lockfile check on a clean project
- All new code covered by unit tests with Given/When/Then structure (TDD)
