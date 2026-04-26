# Tasks: Re-score activation-tester disagreements as warnings

## Phase 1: TDD RED — write failing tests first

### T-001: RED test — auto-classified scope_warning bucket

**Description**: Add a vitest case in `__tests__/activation-tester.test.ts` that exercises the `scope_warning` verdict path.

**References**: AC-US1-01, AC-US1-03, AC-US1-04

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval/__tests__/activation-tester.test.ts`
- **Test**: `TC-001`
  - **Given**: an `ActivationPrompt` with `expected="auto"`, `SkillMeta` with name `hello-skill` and no tags
  - **When**: `testActivation` runs with a mock LlmClient that returns `{related: false}` (Phase 1) then `{activate: true, confidence: "high", reasoning: "..."}` (Phase 2)
  - **Then**: result `.verdict === "scope_warning"`, `.classification === "FP"`, `summary.scopeWarnings === 1`, `summary.fp === 0`, `summary.tp === 0`

**Status**: [x] completed

### T-002: RED test — auto-classified drift_warning bucket

**Description**: Add a vitest case for the `drift_warning` verdict path.

**References**: AC-US1-02, AC-US1-03, AC-US1-04

**Test Plan**:
- **File**: same as T-001
- **Test**: `TC-002`
  - **Given**: an `ActivationPrompt` with `expected="auto"`, `SkillMeta` provided
  - **When**: `testActivation` runs with mocks returning `{related: true}` then `{activate: false, confidence: "high", reasoning: "..."}`
  - **Then**: `.verdict === "drift_warning"`, `.classification === "FN"`, `summary.driftWarnings === 1`, `summary.fn === 0`

**Status**: [x] completed

### T-003: RED test — manual disagreement still counts as FP

**Description**: Add a vitest case proving manual `+`/`!`-equivalent labels (autoClassified=false) keep strict scoring.

**References**: AC-US2-01, AC-US2-02

**Test Plan**:
- **File**: same as T-001
- **Test**: `TC-003`
  - **Given**: an `ActivationPrompt` with explicit `expected="should_not_activate"` (not "auto")
  - **When**: `testActivation` runs with mock returning `{activate: true, ...}` (Phase 1 is skipped because not auto)
  - **Then**: `.verdict === "ok"`, `.classification === "FP"`, `summary.fp === 1`, `summary.scopeWarnings === 0`

**Status**: [x] completed

### T-004: RED test — precision denominator excludes warnings

**Description**: Mixed result set proving precision/recall denominators exclude warning verdicts.

**References**: AC-US1-04

**Test Plan**:
- **File**: same as T-001
- **Test**: `TC-004`
  - **Given**: 2 prompts — one auto-classified scope_warning (Phase 1 says no, Phase 2 says yes), one manual `should_activate` that activates (real TP)
  - **When**: `testActivation` runs with appropriately ordered mocks
  - **Then**: `summary.tp === 1`, `summary.fp === 0`, `summary.scopeWarnings === 1`, `summary.precision === 1.0` (not 0.5)

**Status**: [x] completed

## Phase 2: TDD GREEN — implement the scoring engine

### T-005: Extend types and add `computeVerdict()` helper

**Description**: Modify `activation-tester.ts` to introduce the `Verdict` type, extend `ActivationResult` and `ActivationSummary`, and add a pure helper `computeVerdict(autoClassified, expected, activate)`.

**References**: AC-US1-01, AC-US1-02, AC-US1-03

**Implementation Details**:
- Add `export type Verdict = "ok" | "scope_warning" | "drift_warning";`
- Extend `ActivationResult` with `verdict: Verdict`.
- Extend `ActivationSummary` with `scopeWarnings: number; driftWarnings: number;`
- New helper function `computeVerdict(autoClassified: boolean, expected: ..., activate: boolean): Verdict` — returns non-`"ok"` only when `autoClassified === true`.

**Status**: [x] completed

### T-006: Wire verdict into `testActivation` happy + error paths

**Description**: In `testActivation` (lines ~150 and ~165), set `verdict` on every result via `computeVerdict`.

**References**: AC-US1-01, AC-US1-02

**Implementation Details**:
- Happy path: after computing `classification`, also compute `verdict` and include in the `ActivationResult`.
- Error path (try-catch fallback): set `verdict: "ok"` (errors aren't classifier disagreements).

**Status**: [x] completed

### T-007: Update `computeSummary()` to count warnings and exclude them from fp/fn

**Description**: Tighten the `tp/tn/fp/fn` counts to skip warning-verdict results, and add the new warning counts.

**References**: AC-US1-04, AC-US1-03

**Implementation Details**:
- `scopeWarnings = results.filter(r => r.verdict === "scope_warning").length`
- `driftWarnings = results.filter(r => r.verdict === "drift_warning").length`
- `fp = results.filter(r => r.classification === "FP" && r.verdict === "ok").length` (and same for fn)
- `tp/tn` are unchanged in semantics (only "should_*" → matching activate produces them; verdict is always "ok" for those rows since computeVerdict only flags disagreements).

**Status**: [x] completed

## Phase 3: UI rendering

### T-008: Add yellow warning styles + warning-aware row badge

**Description**: Update `ActivationPanel.tsx` so result rows with `verdict !== "ok"` render a yellow pill instead of the red FP/FN badge.

**References**: AC-US3-01

**Implementation Details**:
- Extend `CLASSIFICATION_STYLES` map (currently 4 entries TP/TN/FP/FN) with `SCOPE_WARNING` and `DRIFT_WARNING` mapped to `var(--yellow-muted)` / `var(--yellow)`.
- Where the row pill is rendered, prefer `result.verdict !== "ok"` to pick a label like "scope warn" or "drift warn"; fall back to `classification` when verdict is `"ok"`.

**Test Plan**: Manual smoke (covered by T-012).

**Status**: [x] completed

### T-009: Render warnings sub-row in confusion matrix

**Description**: Add a small "Warnings: N scope, M drift" row beneath the existing 4-cell confusion matrix.

**References**: AC-US3-02

**Implementation Details**:
- Use `activationSummary.scopeWarnings` and `activationSummary.driftWarnings`.
- Place beneath the existing `<ConfusionCell>` grid (~line 353-356).
- Render even when both are 0 (label "Warnings: 0 scope, 0 drift" — consistent layout).

**Status**: [x] completed

### T-010: Filter "Incorrect" callout to exclude warnings

**Description**: The red "Incorrect" list at the top of the panel should only include `classification ∈ {FP, FN}` AND `verdict === "ok"`.

**References**: AC-US3-03

**Implementation Details**:
- Locate the current filter that builds the "Incorrect" list.
- Add the additional `r.verdict === "ok"` predicate.

**Status**: [x] completed

### T-011: Tooltip strings on warning pills

**Description**: Hovering a yellow warning pill reveals the actionable explanation.

**References**: AC-US3-04

**Implementation Details**:
- Scope: "Description claims broader scope than name+tags suggest. Either narrow the description or add explicit `+` prefix to confirm intended scope."
- Drift: "Description omits intent that classifier inferred from name+tags. Description may need to mention this case explicitly."
- Use the existing tooltip mechanism on the panel (look for `title=` or wrapped tooltip components — match existing patterns).

**Status**: [x] completed

## Phase 4: Verification

### T-012: Build + smoke test

**Description**: Rebuild the eval-ui bundle, launch the studio, and exercise the three prompt forms on `hello-skill`.

**References**: All ACs (end-to-end check).

**Test Plan**:
- `cd repositories/anton-abyzov/vskill && npx vitest run src/eval/__tests__/activation-tester.test.ts` — all green.
- `cd repositories/anton-abyzov/vskill && npx vitest run` — full suite, no regressions.
- `cd repositories/anton-abyzov/vskill && npm run build:eval-ui` — clean build.
- Launch studio (`npx vskill studio` from the umbrella) on a workspace containing `hello-skill`.
- Trigger tab → "how are you today?" (no prefix) → expect yellow scope-warning, no FP count.
- Trigger tab → "+how are you today?" → expect green TP.
- Trigger tab → "!how are you today?" → expect red FP.

**Status**: [x] completed

### T-013: Update tasks/spec checkboxes after closure

**Description**: After all tasks pass, mark `[x]` on every task and every AC; verify via discipline check.

**References**: All ACs.

**Status**: [x] completed

### T-014: Sync living docs

**Description**: Run `specweave sync-living-docs 0775-activation-disagreement-warnings` to refresh the docs surface.

**Status**: [x] completed
