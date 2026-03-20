---
total_tasks: 8
completed_tasks: 0
---

# Tasks: Plugin Caching Review Follow-up

## Phase 1: Extract & Refactor

### T-001: Extract shared semver sort utility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given non-numeric version segments (e.g. "1.0.0-beta") -> When sorted -> Then NaN segments treated as 0, numeric versions sort descending correctly
**Files**: NEW `utils/semver-sort.ts`, UPDATE `utils/plugin-copier.ts`, `dashboard/server/data/plugin-scanner.ts`

### T-002: Add logging to remaining catches in plugin-copier.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test Plan**: Given empty catch blocks at lines ~170, 421, 428, 572, 599, 637, 823, 848 -> When errors occur -> Then consoleLogger.debug or .warn is called
**Files**: `utils/plugin-copier.ts`

### T-003: Add logging to remaining catches in other files
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Test Plan**: Given empty catches in plugin-scanner, cleanup-stale-plugins, refresh-plugins, claude-plugin-enabler -> When errors occur -> Then debug/warn logging fires
**Files**: `dashboard/server/data/plugin-scanner.ts`, `utils/cleanup-stale-plugins.ts`, `cli/commands/refresh-plugins.ts`, `cli/helpers/init/claude-plugin-enabler.ts`

## Phase 2: Safety & Correctness

### T-004: Fix TOCTOU + symlink check in Phase 2.5
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test Plan**: Given stale version dir -> When cleanup runs -> Then dir is renamed before deletion (atomic) AND symlinks are detected and skipped
**Files**: `utils/cleanup-stale-plugins.ts`

### T-005: Fix settings backup (reuse content, timestamped name)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**Test Plan**: Given corrupt settings.json -> When backup created -> Then uses already-read content (no re-read) AND filename includes timestamp
**Files**: `cli/helpers/init/claude-plugin-enabler.ts`

### T-006: Fix chalk leaking into errors array
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] pending
**Test Plan**: Given plugin install failure in quiet mode -> When errors returned -> Then errors array has plain text, console output has chalk formatting
**Files**: `cli/commands/refresh-plugins.ts`

## Phase 3: Type Design & Scope

### T-007: Type design improvements
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [ ] pending
**Test Plan**: Given validatePluginCache -> When returning result -> Then type is discriminated union. Given refreshPluginsCommand -> When exported -> Then uses named RefreshResult type.
**Files**: `utils/plugin-copier.ts`, `cli/commands/refresh-plugins.ts`, `utils/cleanup-stale-plugins.ts`

### T-008: Expand doctor check to all marketplaces
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [ ] pending
**Test Plan**: Given multiple marketplace caches exist -> When doctor runs -> Then all marketplaces scanned for stale version dirs
**Files**: `core/doctor/checkers/plugins-checker.ts`
