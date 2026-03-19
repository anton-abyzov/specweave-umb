---
increment: 0539-umbrella-root-resolution-fix
generated: 2026-03-15
test_mode: TDD
---

# Tasks: Fix umbrella root resolution in 3 artifact-creation paths

## US-001: Spec detector resolves to umbrella root

### T-001: Write failing test for spec-detector umbrella root resolution
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test**: Given a new test file at `tests/unit/core/specs/spec-detector-root.test.ts` with `resolveEffectiveRoot` mocked to `/umbrella-root` → When vitest runs → Then the assertion that `specsFolder` starts with `/umbrella-root` fails RED (proves `process.cwd()` is still used)

### T-002: Fix spec-detector.ts to use resolveEffectiveRoot()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test**: Given `resolveEffectiveRoot()` is mocked to return `/umbrella-root` → When `detectSpecsByFeatureId("FS-001")` runs → Then the resolved specs folder path is `/umbrella-root/.specweave/docs/internal/specs` (not `<child-cwd>/.specweave/...`); and when no umbrella is active (mock returns CWD) → Then path uses that CWD (single-repo behavior preserved)

---

## US-002: Active increment manager resolves to umbrella root

### T-003: Write failing test for ActiveIncrementManager umbrella root resolution
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given a new test file at `tests/unit/core/increment/active-increment-manager-root.test.ts` with `resolveEffectiveRoot` mocked to `/umbrella-root` → When vitest runs → Then the assertion that `stateFile` contains `/umbrella-root` fails RED (proves `process.cwd()` is still the default)

### T-004: Fix active-increment-manager.ts to use resolveEffectiveRoot()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given `resolveEffectiveRoot()` mocked to `/umbrella-root` → When `new ActiveIncrementManager()` is called with no args → Then `stateFile` is `/umbrella-root/.specweave/state/active-increment.json`; When called with explicit `rootDir: "/explicit"` → Then `stateFile` is `/explicit/.specweave/state/active-increment.json` (explicit value wins); When single-repo (mock returns `/project`) → Then `stateFile` is `/project/.specweave/state/active-increment.json`

---

## US-003: Activation tracker resolves to umbrella root

### T-005: Write failing test for activation-tracker umbrella root resolution
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given a new test file at `tests/unit/core/skills/activation-tracker-root.test.ts` with `resolveEffectiveRoot` mocked to `/umbrella-root` → When vitest runs → Then the assertion that `getStatePath()` returns a path under `/umbrella-root` fails RED (proves `process.cwd()` fallback is still used)

### T-006: Fix activation-tracker.ts to use resolveEffectiveRoot()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given `resolveEffectiveRoot()` mocked to `/umbrella-root` → When `getStatePath()` is called with no arguments → Then it returns `/umbrella-root/.specweave/state/skill-activations.json`; When called with explicit `projectRoot: "/explicit"` → Then it returns `/explicit/.specweave/state/skill-activations.json`; When single-repo (mock returns `/project`) → Then returns `/project/.specweave/state/skill-activations.json`

---

## US-004: Deduplicate platform.ts findProjectRoot

### T-007: Write failing test for platform.ts re-export identity
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test**: Given a new test file at `tests/unit/core/hooks/platform-dedup.test.ts` that imports `findProjectRoot` from both `platform.ts` and `utils/find-project-root.ts` → When vitest runs → Then the assertion that they are the same function reference fails RED (proves platform.ts still has its own body)

### T-008: Replace duplicate findProjectRoot in platform.ts with re-export
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test**: Given `src/hooks/platform.ts` with the inline function body removed and `export { findProjectRoot } from '../utils/find-project-root.js'` added → When `platform.findProjectRoot === canonicalFindProjectRoot` is asserted → Then it is true (same reference); When called with a path containing `.specweave/config.json` → Then it returns the correct project root (identical behavior to canonical)

### T-009: Run full test suite GREEN — verify no regressions
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test**: Given all four source changes are applied → When `npx vitest run` executes across the new test files and the full existing suite → Then all tests pass GREEN with zero regressions, and coverage for the four changed files meets the 90% target
