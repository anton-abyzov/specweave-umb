---
increment: 0800-studio-tests-discoverability-and-readonly-run
status: planned
---

# Tasks — Studio Tests Discoverability + Read-only Run

TDD discipline: **RED → GREEN → REFACTOR**. Tests first; do not mark a task `[x]` until its tests pass.

Working dir for all paths below: `repositories/anton-abyzov/vskill/`.

---

### T-001: [RED] Vitest — split capability flags `canEdit` / `canRun`

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan** (Given/When/Then):
- **Given** a `skillInfo.origin === "installed"` and `evals.cases.length === 3`
- **When** `useSkillCapabilities(skillInfo, evals)` is called
- **Then** the returned object has `canEdit === false` AND `canRun === true`
- **Given** a `skillInfo.origin === "source"` and `evals.cases.length === 0`
- **When** the hook is called
- **Then** `canEdit === true` AND `canRun === false`

**Implementation hint**: Create `src/eval-ui/src/hooks/useSkillCapabilities.ts` (initially returning hard-coded values to make test fail). Add test at `src/eval-ui/src/hooks/__tests__/useSkillCapabilities.test.ts`.

---

### T-002: [GREEN] Implement `useSkillCapabilities` hook

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**: T-001 tests now pass.

**Implementation**:
```typescript
// src/eval-ui/src/hooks/useSkillCapabilities.ts
export function useSkillCapabilities(skill: SkillInfo, evals: SkillEvalsEnvelope) {
  const canEdit = skill.origin === "source";
  const canRun = evals.exists && evals.cases.length > 0;
  return { canEdit, canRun };
}
```

---

### T-003: [RED] Vitest — TestsPanel renders Run buttons for installed skills

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**:
- **Given** `<TestsPanel embedded={false} />` mounted with `canEdit=false, canRun=true, cases=[c1, c2]`
- **When** the panel renders
- **Then** each case row has a visible Run button (`getByTestId("eval-case-run-c1")`)
- **AND** "Run all" button is visible (`getByTestId("eval-cases-run-all")`)
- **AND** "Add Test Case" button is NOT in the DOM (`queryByText("Add Test Case")` is null)
- **AND** read-only banner is rendered with text matching `/Read-only/i`

**Implementation hint**: Add `src/eval-ui/src/components/__tests__/0800-readonly-run.test.tsx`. Use `@testing-library/react`.

---

### T-004: [GREEN] Split TestsPanel gates: keep Run, hide Edit/Add/Delete for installed

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..04 | **Status**: [x] completed
**Test Plan**: T-003 tests pass.

**Implementation** (in `TestsPanel.tsx`):
- Replace `isReadOnly` consumers with `canEdit` / `canRun` from `useSkillCapabilities`
- Line ~420 (Add Test Case): gate on `canEdit`
- Line ~651 (per-case Run): gate on `canRun` (NOT `canEdit`)
- Per-case Edit/Delete buttons: gate on `canEdit`
- Add read-only banner above case list when `!canEdit && evals.exists`:
  ```tsx
  {!canEdit && evals.exists && (
    <div role="status" data-testid="readonly-banner">
      Read-only — to author or modify tests, install this skill as source via <code>vskill plugin new</code>.
    </div>
  )}
  ```

---

### T-005: [RED] Vitest — EditorPanel "Run all" CTA in eval-cases section

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- **Given** EditorPanel mounted for a source skill with `cases.length > 0` and section open
- **When** the eval-cases section header renders
- **Then** "Run all" button visible (`getByTestId("editor-eval-cases-run-all")`)
- **When** clicked
- **Then** `window.location.search` matches `/tab=run&mode=benchmark&autorun=1/` (or pushState mock called with that path)
- **Given** source skill with `cases.length === 0`
- **Then** "Run all" button NOT rendered

---

### T-006: [GREEN] Add "Run all" CTA to EditorPanel eval-cases header

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05, AC-US2-06 | **Status**: [x] completed
**Test Plan**: T-005 tests pass.

**Implementation** (in `EditorPanel.tsx`):
- Inside the `<summary>` of `editor-eval-cases-section`, render a button when `canEdit && cases.length > 0`
- onClick: `setSearchParams({ tab: "run", mode: "benchmark", autorun: "1" })` (or equivalent URL helper)

---

### T-007: [RED] Vitest — RunDispatcherPanel autorun fires once

**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- **Given** `<RunDispatcherPanel mode="benchmark" />` with URL `?autorun=1`, evals load with 2 cases
- **When** mounted (and re-mounted under StrictMode double-invoke)
- **Then** `runAll("benchmark")` called exactly once
- **AND** URL is updated to remove `autorun` param
- **Given** URL has no `autorun` param
- **Then** `runAll` not called

---

### T-008: [GREEN] Implement autorun in RunDispatcherPanel

**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: T-007 tests pass.

**Implementation** (in `RunDispatcherPanel.tsx`):
```tsx
const autorunRef = useRef(false);
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  if (params.get("autorun") !== "1") return;
  if (!evals.exists || evals.cases.length === 0) return;
  if (autorunRef.current) return;
  autorunRef.current = true;
  runAll("benchmark");
  params.delete("autorun");
  window.history.replaceState(null, "", `?${params.toString()}`);
}, [evals.exists, evals.cases.length]);
```

---

### T-009: [RED] Vitest — Overview "N tests" chip

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-06, AC-US2-07 | **Status**: [x] completed
**Test Plan**:
- **Given** OverviewPanel for any skill with `evals.exists && cases.length === 5`
- **When** rendered
- **Then** chip with text "5 tests" visible (`getByTestId("overview-tests-chip")`)
- **When** clicked
- **Then** URL search becomes `?tab=run&mode=benchmark`
- **Given** `evals.exists === false`
- **Then** chip NOT rendered

---

### T-010: [GREEN] Add "N tests" chip to Overview

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-06, AC-US2-07 | **Status**: [x] completed
**Test Plan**: T-009 tests pass.

---

### T-011: [RED] Playwright — full E2E flow

**User Story**: US-001, US-002 | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test Plan** (`e2e/0800-tests-discoverability.spec.ts`):
- **Test A** (source skill, Edit Run-all → autorun):
  1. Navigate to a source skill detail page
  2. Click `[data-testid="detail-tab-edit"]`
  3. Expand `[data-testid="editor-eval-cases-section"]`
  4. Click `[data-testid="editor-eval-cases-run-all"]`
  5. Assert URL has `tab=run&mode=benchmark&autorun=1`
  6. Assert benchmark dispatch fires (network mock or wait for results UI)
  7. Assert URL post-dispatch no longer has `autorun=1`

- **Test B** (Overview chip → Run):
  1. Navigate to skill with evals
  2. Click `[data-testid="overview-tests-chip"]`
  3. Assert URL `?tab=run&mode=benchmark`

- **Test C** (installed skill, read-only Run):
  1. Navigate to an installed skill that ships evals
  2. Click `[data-testid="detail-tab-run"]`
  3. Assert `[data-testid="readonly-banner"]` visible
  4. Assert no `[data-testid="add-test-case-button"]`
  5. Click `[data-testid="eval-case-run-..."]` for first case
  6. Assert run dispatched (network or UI signal)

---

### T-012: [GREEN] Wire all components — verify all unit + e2e tests pass

**Status**: [x] completed
**Test Plan**: `npx vitest run` (all green) + `npx playwright test e2e/0800-*.spec.ts` (all green)

---

### T-013: [REFACTOR] Consolidate capabilities + remove dead `isReadOnly` references

**Status**: [x] completed
**Test Plan**: All existing tests still pass.

**Implementation**:
- Search for remaining `isReadOnly` references across `src/eval-ui/`; replace with `canEdit` / `canRun`
- Remove unused imports
- Verify `RightPanel.tsx:402` migrated cleanly

---

### T-014: Restore per-case 2x2 pass/fail visualization on Run tab (US-003)

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..07 | **Status**: [x] completed
**Test Plan**:
- **Given** RunPanel mounted in benchmark mode for a skill with at least one case AND prior history
- **When** the case row renders
- **Then** a `PerCaseHistory` block is rendered immediately below the `RunCaseCard` with `data-testid="run-case-history-<id>"`
- **AND** the block contains the existing `CaseHistorySection` UI (split-lane Skill | Baseline grid + per-assertion pass/fail icons + MiniTrend)
- **Given** a case with NO prior history
- **Then** the block renders nothing (returns null) so the row stays compact
- **Verified**: existing 25 RunPanel.test.tsx tests still pass after wiring

**Implementation summary**:
- `TestsPanel.tsx` — added `export` to `useCaseHistory`, `HistoryEntryCard`, `CaseHistorySection` (3 keyword additions; no behavior change for existing callers)
- `RunPanel.tsx` — added `Fragment` import + small `PerCaseHistory` component that calls `useCaseHistory` once per case and renders `<CaseHistorySection>` with the fetched entries; rendered immediately after each `<RunCaseCard>` in the benchmark mode `cases.map` loop
- No new component files created — reused existing `CaseHistorySection`/`HistoryEntryCard` that were dead code (gated on `!embedded`, with TestsPanel only ever rendered embedded)
- Net effect: the 2x2 split-lane pass/fail grid the user remembered from the pre-0792 Tests tab is back, surfaced on the Run tab in Benchmark mode for both source AND installed skills
