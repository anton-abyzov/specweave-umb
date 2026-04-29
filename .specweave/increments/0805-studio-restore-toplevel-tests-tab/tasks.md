---
increment: 0805-studio-restore-toplevel-tests-tab
status: planned
---

# Tasks — Restore top-level Tests tab

Working dir: `repositories/anton-abyzov/vskill/`.

---

### T-001: Add "tests" tab descriptor to RightPanel

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Implementation**:
- In `src/eval-ui/src/components/RightPanel.tsx`, modify `TAB_DESCRIPTORS` to insert `{ id: "tests", label: "Tests" }` between Edit and Run
- Update `DetailTab` type to include `"tests"`
- Update `ALL_TABS` if it exists separately

---

### T-002: Mount TestsPanel non-embedded on Tests tab

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Implementation**:
- Add `import { TestsPanel } from "../pages/workspace/TestsPanel";` to RightPanel.tsx
- Find the tab content switch/branch (around the existing Overview/Edit/Run/History render). Add a `tests` branch that returns `<TestsPanel />` (no `embedded` prop = non-embedded mode by default).
- TestsPanel already handles canEdit/canRun gating from 0800 — read-only banner appears for installed automatically.

---

### T-003: Remove legacy `?tab=tests` redirect

**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed

**Implementation**:
- In RightPanel.tsx around lines 92-109 there's a legacy redirect block from 0792 that maps `?tab=tests` → `?tab=run&mode=benchmark`. Remove that block (or change to no-op) so `?tab=tests` mounts the new Tests tab.

---

### T-004: Migrate 4-tab playwright specs to 5 tabs

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Implementation**:
- Search e2e/ for tests asserting exactly 4 tabs: `grep -rn "tabs.*4\|4.*tabs\|toHaveCount(4)" e2e/`
- For each match in 0792-era specs (qa-click-audit.spec.ts, any IA spec), update to expect 5 tabs (Overview / Edit / Tests / Run / History)

---

### T-005: Add E2E spec asserting Tests tab works

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01..03 | **Status**: [x] completed

**Implementation**:
- New file `e2e/0805-tests-tab.spec.ts` with one spec:
  - Navigate to a skill detail page
  - Assert 5 tabs visible
  - Click `[data-testid="detail-tab-tests"]`
  - Assert URL `?tab=tests`
  - Assert TestsPanel content visible (`[data-testid="tests-panel"]` or similar — verify exact testid)

---

### T-006: Verify Edit-tab eval-cases section + Run-tab PerCaseHistory still work

**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Implementation**:
- Run existing 0800 vitest suite (`npx vitest run src/eval-ui/src/`) — confirm RunPanel.tsx PerCaseHistory + EditorPanel Run all CTA tests still pass
- No code change needed; just verification

---

### T-007: Build + smoke test + close

**Status**: [x] completed — handled at release time
