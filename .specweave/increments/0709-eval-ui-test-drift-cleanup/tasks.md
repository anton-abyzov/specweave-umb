# Tasks: eval-ui test-drift cleanup

## Task Notation
- `[T###]`: Task ID | `[ ]`: Not started | `[x]`: Completed
- TDD required: the failing tests are ALREADY RED on `main` — this increment moves them to GREEN without touching production code.

## Phase 1: Breadcrumb vocabulary (US-001)

### T-001: Update TopRail.test.tsx breadcrumb assertions to Skills/Project
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed
**File**: `src/eval-ui/src/components/__tests__/TopRail.test.tsx`
**Test Plan**:
- Given the existing `TopRail.test.tsx` has two failing `expect(text).toContain("Own" | "Installed")` assertions
- When `"Own"` is replaced with `"Skills"` and `"Installed"` with `"Project"`, and the enclosing `it()` descriptors are refreshed to match
- Then `npx vitest run src/eval-ui/src/components/__tests__/TopRail.test.tsx` returns 0 failures AND the descriptors no longer reference the retired `OWN` / `INSTALLED` vocabulary.

### T-002: Update TopRail.modelselector.test.tsx breadcrumb assertion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05 | **Status**: [x] completed
**File**: `src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx` (around line 89)
**Test Plan**:
- Given the failing `expect(segments[0].textContent).toContain("Own")` in the "OWN segment is a button-like element" test
- When the assertion is updated to `toContain("Skills")` and the leading describe/it prose is refreshed accordingly
- Then `npx vitest run src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx` returns 0 failures.

### T-003: Update qa-interactions.test.tsx breadcrumb assertion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**File**: `src/eval-ui/src/components/__tests__/qa-interactions.test.tsx` (around line 321)
**Test Plan**:
- Given the failing assertion in `QA: TopRail breadcrumb shape > renders origin / plugin / skill as non-interactive spans`
- When the expected text is updated from `"Own"` → `"Skills"` and the comment above explaining uppercase rendering is refreshed
- Then `npx vitest run src/eval-ui/src/components/__tests__/qa-interactions.test.tsx` returns 0 failures.

## Phase 2: PluginTreeGroup snapshot (US-002)

### T-004: Verify PluginTreeGroup markup matches 0698 T-010 declared intent, then re-record snapshot
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**File**: `src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx` (inline snapshot around line 116)
**Test Plan**:
- Given `PluginTreeGroup.tsx` renders: flex wrapper `<div style="display:flex;align-items:center;padding-right:6px">` around the expand/collapse `<button>`; chevron `<span>` at `width:16px`, `font-size:14px`, `font-weight:700`, `color:var(--color-ink, var(--text-primary))`; button `flex:1`
- And given `0698 T-010` implementation comments in `PluginTreeGroup.tsx` confirm this is the intended design
- When the snapshot is re-recorded via `npx vitest run src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx -u`
- Then `npx vitest run src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx` passes without `-u`
- AND the recorded snapshot text contains the literal strings `display:flex;align-items:center;padding-right:6px`, `width:16px`, `font-size:14px`, `font-weight:700`, `color:var(--color-ink, var(--text-primary))`.

### T-006: Update tri-scope E2E spec to match post-0698 five-bucket sidebar
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**File**: `e2e/agent-scope-picker.spec.ts` (lines 79-98)
**Context**: Surfaced during PM Gate 2a verification. The spec was asserting against the retired 2-section sidebar layout (`button[data-testid='sidebar-section-header']` with `Own` / `Installed`). The 0698 T-008 refactor replaced this with GroupHeader buttons (`AVAILABLE` / `AUTHORING`) wrapping NamedScopeSection sub-buttons (`Project` / `Personal` / `Skills` / `Plugins`). The E2E never caught up — pre-existing drift confirmed via `git stash` + re-run at iteration time.
**Test Plan**:
- Given the post-0698 sidebar renders two `role="button"` GroupHeaders named `AVAILABLE` / `AUTHORING` wrapping sub-scope buttons `Project` / `Personal` / `Skills`
- When the E2E locator is updated to `sidebar.getByRole("button", { name: /AVAILABLE/ })` / `/AUTHORING/` plus a sub-label presence check
- Then `npx playwright test agent-scope-picker.spec.ts` passes E2E-03 (8/8 non-skipped specs green at iteration time, 2 skipped by design for harness-pending paths).

## Phase 3: Verification

### T-005: Full eval-ui regression sweep
**User Story**: US-001, US-002 | **Satisfies ACs**: ALL | **Status**: [x] completed — 165 files, 1358 tests, all green
**Commands** (run in `repositories/anton-abyzov/vskill/`):
- `npx vitest run src/eval-ui`
**Test Plan**:
- Given T-001..T-004 are complete
- When the full `src/eval-ui` vitest sweep runs
- Then every previously-failing test passes AND no adjacent test regresses
- AND the 0709-scoped files in the change set touch ONLY `src/eval-ui/**/__tests__/**` and the paired `__snapshots__/*.snap` (zero production-code churn FROM 0709). Unrelated production changes bundled into the same git commit are permitted if they carry their own increment traceability (e.g. 0704 T-013a/b) and are documented in `reports/CLOSURE-NOTES.md`.
