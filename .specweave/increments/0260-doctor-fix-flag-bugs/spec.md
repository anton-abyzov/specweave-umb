---
increment: 0260-doctor-fix-flag-bugs
title: "Doctor --fix flag not working for PluginsChecker and lockfile integrity"
type: bug
priority: P1
status: planned
created: 2026-02-20
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Doctor --fix flag not working for PluginsChecker and lockfile integrity

## Overview

The `specweave doctor --fix` command has two bugs that prevent auto-remediation:

1. **PluginsChecker ignores `fix` option** -- The `check()` method receives `_options: DoctorOptions` (underscore = unused). None of its private methods accept or act on the `fix` flag. Fixable issues (stale state, stale cache, empty marketplace, missing core plugin) only emit suggestion text.

2. **Lockfile integrity fix only changes suggestion text** -- In `InstallationHealthChecker.checkLockfileIntegrity()`, when `fix=true` and hash mismatches are found, lines 269-271 merely change `fixSuggestion` to a different string instead of executing `specweave refresh-plugins`. The other three checks in the same class correctly perform fix actions.

## Root Cause

- **Bug 1**: `PluginsChecker` was implemented as read-only. The `_options` underscore prefix masked the oversight.
- **Bug 2**: Lockfile integrity check treats `fix` as a display toggle, not an action trigger.

## User Stories

### US-001: PluginsChecker fix support (P1)
**Project**: specweave

**As a** developer running `specweave doctor --fix`
**I want** plugin-related issues to be auto-remediated
**So that** I don't have to manually run suggested commands

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `fix=true` and invalid local state file detected, delete the corrupt state file
- [x] **AC-US1-02**: When `fix=true` and stale global cache detected (>24h), delete the stale cache file
- [x] **AC-US1-03**: When `fix=true` and marketplace empty or core plugin missing/incomplete, run `specweave refresh-plugins` via execSync
- [x] **AC-US1-04**: The `_options` parameter is renamed to `options` and `fix` is properly extracted and passed to private methods

---

### US-002: Lockfile integrity auto-fix (P1)
**Project**: specweave

**As a** developer running `specweave doctor --fix`
**I want** lockfile hash mismatches and missing skills to trigger `specweave refresh-plugins` automatically
**So that** the fix flag actually fixes things instead of just changing suggestion text

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `fix=true` and hash mismatches detected, execute `specweave refresh-plugins` via execSync
- [x] **AC-US2-02**: When `fix=true` and missing skills detected, execute `specweave refresh-plugins` via execSync
- [x] **AC-US2-03**: On successful fix, return status `warn` with message indicating fix was applied
- [x] **AC-US2-04**: On failed fix (execSync throws), return status `fail` with error message

## Functional Requirements

### FR-001: Consistent fix behavior
All doctor checkers that emit `fixSuggestion` must, when `fix=true`, attempt to perform the suggested action automatically. Text-only suggestions are only acceptable when the fix is unsafe or requires user judgment.

### FR-002: execSync for plugin refresh
Plugin-related fixes that require `specweave refresh-plugins` must use `execSync` with `stdio: 'pipe'` to capture output, same pattern used in `doctor.ts` CLI action handler (line 64).

## Success Criteria

- `specweave doctor --fix` resolves all auto-fixable plugin and lockfile issues without manual intervention
- All existing tests continue to pass
- New tests cover fix mode for both PluginsChecker and lockfile integrity

## Out of Scope

- Adding fix support to other checkers (EnvironmentChecker, GitChecker, etc.)
- Changing the CLI action handler in `doctor.ts`
- Modifying the `DoctorOptions` interface

## Dependencies

- `specweave refresh-plugins` command must be functional (already implemented)
- `plugin-copier.ts` utility functions (already implemented)
