---
increment: 0488-skill-studio-status-ux
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001]
  US-002: [T-002, T-003]
  US-003: [T-004]
  US-004: [T-005]
total_tasks: 5
completed: 5
---

# Tasks: 0488-skill-studio-status-ux

## User Story: US-001 - Correct Empty-Assertions Case Status

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 1 total, 1 completed

### T-001: Guard empty assertions in benchmark-runner.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a test case with an empty assertions array
- **When** `runSingleCaseSSE` computes the case status
- **Then** `status` is `"fail"` and `pass_rate` is `0`

**Test Cases**:
1. **Unit**: `src/eval-server/benchmark-runner.test.ts`
   - `emptyAssertions_returnsFail()`: Call case status logic with `assertionResults = []`, expect `{ status: "fail", pass_rate: 0 }`
   - `allPassingAssertions_returnsPass()`: Regression — call with 2 passing assertions, expect `{ status: "pass" }`
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval-server/benchmark-runner.ts` line 94, change:
   `assertionResults.every((a) => a.pass) ? "pass" : "fail"`
   to:
   `assertionResults.length > 0 && assertionResults.every((a) => a.pass) ? "pass" : "fail"`
2. Run `npx vitest run benchmark-runner`

---

## User Story: US-002 - Sidebar Badge Uses Overall Pass Rate

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 2 total, 2 completed

### T-002: Extract computeBenchmarkStatus helper in api-routes.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill whose benchmark has `overall_pass_rate: 0`
- **When** `/api/skills` computes `benchmarkStatus`
- **Then** the status is `"fail"`, not `"pass"`; and given mismatched eval IDs the status is `"stale"`

**Test Cases**:
1. **Unit**: `src/eval-server/api-routes.test.ts` (or `computeBenchmarkStatus.test.ts`)
   - `passRate0_returnsFail()`: benchmark with `overall_pass_rate: 0` -> `"fail"`
   - `passRate1_returnsPass()`: benchmark with `overall_pass_rate: 1.0` -> `"pass"`
   - `staleEvalIds_returnsStale()`: benchmark case `eval_id` not in current evals -> `"stale"`
   - `noBenchmarkHasEvals_returnsPending()`: no benchmark, `hasEvals: true` -> `"pending"`
   - `noBenchmarkNoEvals_returnsMissing()`: no benchmark, `hasEvals: false` -> `"missing"`
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval-server/api-routes.ts`, extract the helper:
   ```ts
   function computeBenchmarkStatus(
     benchmark: BenchmarkResult | null,
     hasEvals: boolean,
     currentEvalIds: Set<number>
   ): "pass" | "fail" | "pending" | "missing" | "stale"
   ```
2. Logic order: missing -> pending -> stale (any case.eval_id not in currentEvalIds) -> pass (overall_pass_rate === 1.0) -> fail
3. Build `currentEvalIds` from `loadAndValidateEvals` result already fetched at line 198
4. Replace the inline ternary (lines 207-213) with a call to the helper
5. Run `npx vitest run api-routes`

---

### T-003: Add "stale" status to frontend types and STATUS_CONFIG

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the API returns `benchmarkStatus: "stale"`
- **When** the sidebar renders the skill card
- **Then** an orange "Stale" badge appears with no TypeScript errors

**Test Cases**:
1. **Type check**: `npx tsc --noEmit` passes with no errors after adding `"stale"` to union
   - **Coverage Target**: 100% (compile-time)

**Implementation**:
1. `src/eval-ui/src/types.ts` line 31: add `"stale"` to `benchmarkStatus` union
2. `src/eval-ui/src/styles/globals.css`: add `--orange-muted: rgba(251, 146, 60, 0.12);` next to `--orange`
3. `src/eval-ui/src/pages/SkillListPage.tsx` `STATUS_CONFIG`: add `stale: { bg: "var(--orange-muted)", text: "var(--orange)", dot: "var(--orange)", label: "Stale" }`
4. `src/eval-ui/src/components/SkillCard.tsx` `STATUS_CONFIG`: same entry as above
5. Run `npx tsc --noEmit` in eval-ui

---

## User Story: US-003 - Tests Panel Scroll Containment

**Linked ACs**: AC-US3-01, AC-US3-02
**Tasks**: 1 total, 1 completed

### T-004: Add max-height and overflow-y to prompt and expected-output sections

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** a prompt longer than 200px of rendered height
- **When** the case detail is displayed
- **Then** the prompt section has `maxHeight: 200` with `overflowY: "auto"` and is independently scrollable

**Test Cases**:
1. **Manual**: Open a case with 1000+ character prompt, verify prompt area scrolls independently and assertion rows stay visible below
2. **Manual**: Same check for expected-output section
   - **Coverage Target**: 100% of AC scenarios (manual verification)

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/TestsPanel.tsx` `CaseDetail` component:
   - Prompt display div (lines 279-293): add `maxHeight: 200, overflowY: "auto"` to the `style` prop
   - Expected-output display div (lines 315-329): same addition
2. Do NOT touch edit-mode `<textarea>` elements
3. Run `npx tsc --noEmit` in eval-ui to confirm no type errors

---

## User Story: US-004 - Distinct "Not Run" Assertion Indicators

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 1 total, 1 completed

### T-005: Replace solid gray circle with dashed-border "not run" indicator

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** an assertion with no result (not yet evaluated)
- **When** displayed in the Tests panel
- **Then** it shows a circle with a dashed border instead of a solid gray fill

**Test Cases**:
1. **Manual**: Before running evals, verify all assertion indicators show dashed border circles
2. **Manual**: After running evals, verify passing assertions show green check and failing show red X (regression check)
   - **Coverage Target**: 100% of AC scenarios (manual verification)

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/TestsPanel.tsx` around line 407, replace the `AssertionRow` "not run" `<span>`:
   - Remove: `style={{ background: "var(--surface-4)" }}`
   - Add: `style={{ border: "1.5px dashed var(--text-tertiary)", background: "transparent" }}`
2. Confirm the pass/fail branches (green check icon, red X icon) are unchanged
3. Run `npx tsc --noEmit` in eval-ui
