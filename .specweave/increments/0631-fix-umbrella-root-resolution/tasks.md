---
increment: 0631-fix-umbrella-root-resolution
title: "Fix Umbrella Root Resolution and Prevent Stale .specweave in Child Repos"
status: active
created: 2026-03-19
---

# Tasks

## US-004: Test Coverage for Umbrella Resolution Functions

### T-001: Write Failing Tests for Umbrella Resolution Functions (TDD Red)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given `tests/unit/utils/find-project-root.test.ts` extended with a `createUmbrellaTree()` helper → When the new `describe` blocks for `findUmbrellaRoot`, `resolveEffectiveRoot`, `getSpecweavePath`, and `detectUmbrellaParent` run → Then all new tests FAIL (red) because `getSpecweavePath` does not yet exist and `detectUmbrellaParent` still uses only `repository.umbrellaRepo`

---

## US-002: State, Logs, and Reports Write to Umbrella Root

### T-002: Add `getSpecweavePath()` Utility to `find-project-root.ts` (TDD Green)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given the failing test from T-001 for `getSpecweavePath()` → When the export `getSpecweavePath(startDir?: string): string` is added to `src/utils/find-project-root.ts` wrapping `resolveEffectiveRoot()` → Then `getSpecweavePath()` tests pass, returning `/umbrella/.specweave` when run from a child repo and `<cwd>/.specweave` in standalone mode

---

## US-003: Config Flag Detection Is Consistent

### T-003: Fix `detectUmbrellaParent()` Config Flag in `path-utils.ts`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-03
**Status**: [x] Completed
**Test**: Given a config with `umbrella.enabled: true` but no `repository.umbrellaRepo` → When `detectUmbrellaParent()` is called from a child repo directory → Then it detects and returns the umbrella parent (not null), matching `findUmbrellaRoot()` behavior; backward-compatible when both flags present; returns null when neither flag is set

---

## US-001: Dashboard Correctly Resolves Umbrella Root

### T-004: Fix Dashboard Root Resolution
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given an umbrella workspace with `umbrella.enabled: true` → When `specweave dashboard` is run from a child repo (`dashboard.ts:24` replaced with `resolveEffectiveRoot()`) and when `POST /api/projects` resolves via `findUmbrellaRoot(resolvedPath) || resolvedPath` in `dashboard-server.ts` → Then the dashboard reads increments from the umbrella root `.specweave/`; standalone mode is unchanged and uses `process.cwd()`

---

## US-002: State, Logs, and Reports Write to Umbrella Root (continued)

### T-005: Fix Pattern B Bypass Modules (Direct `path.join` Replacements)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given 6 modules that use `path.join(process.cwd(), '.specweave', ...)` directly → When `getSpecweavePath` is imported and the direct patterns are replaced in `qa-runner.ts:49`, `autonomous-executor.ts:244`, `revert-wip-limit.ts:18`, `logs.ts:26`, `cross-linker.ts:56`, `content-distributor.ts:85` → Then no new files are written to any child repo's `.specweave/` directory when CLI commands run from within an umbrella workspace

### T-006: Fix Pattern A Bypass Modules (`?? process.cwd()` Default Fallbacks)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given 7 modules using `?? path.join(process.cwd(), '.specweave')` as a default fallback → When `getSpecweavePath` is imported and the fallback patterns are replaced in `command-integration.ts:84`, `notification-manager.ts:81`, `schedule-persistence.ts:71`, `log-aggregator.ts:109`, `sync-audit-logger.ts:169`, `permission-enforcer.ts:132` (+ default param at line 364), `sync-scheduled.ts:48` → Then all state, log, and report writes resolve to the umbrella root when run from a child repo

### T-007: Verify Zero Bypass Patterns Remain
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given all 13 bypass fixes applied in T-005 and T-006 → When `grep -rn "process\.cwd().*\.specweave\|join(process\.cwd(), '\.specweave'" src/` is run in the specweave repo → Then zero matches are returned (dashboard.ts match also resolved via T-004), confirming complete elimination of bypass patterns

---

## US-005: Stale Child Repo .specweave Cleanup

### T-008: Clean Up Stale `.specweave/` Directories in Child Repos
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] Completed
**Test**: Given stale `.specweave/increments/` dirs in `repositories/anton-abyzov/vskill/` (0569, 0570, 0572) and `repositories/anton-abyzov/specweave/` (0576, 0590, 0593, 0595, 0599, 0605) → When each orphan increment ID is verified as present in the umbrella's `.specweave/increments/` (active or archive) before deletion → Then all 9 stale directories are removed, no child repo retains any `.specweave/increments/` subdirectory, and the umbrella archive retains every removed increment
