---
increment: 0775-activation-disagreement-warnings
title: Re-score activation-tester disagreements as warnings (fix hello-skill FP)
type: bug
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Re-score activation-tester disagreements as warnings

## Overview

The vskill studio Trigger tab currently flags broad-scope skills (e.g., `hello-skill` whose description says "activate for every user message") as False Positives even when the skill activates exactly as described. The 2-phase classify-then-evaluate design is intentional per increment 0472: Phase 1 (`classifyExpectation`) sees only `name + tags` so the LLM can't rubber-stamp the description; Phase 2 (`testActivation`) sees the description. Their disagreement is the design's signal — but currently it is scored as FP/FN, which is misleading on broad-scope skills.

This increment re-scores **auto-classified** disagreements as warnings (`scope_warning` / `drift_warning`) instead of FP/FN. **Manual-labeled** prompts (prefixed `+` or `!`) keep strict FP/FN scoring — the user's hand-labeled ground truth is treated as authoritative.

## User Stories

### US-001: Auto-classified disagreement → warning, not failure (P1)
**Project**: vskill

**As a** skill author testing activation in vskill studio
**I want** broad-scope skills (descriptions like "activate for every message") to NOT be flagged as red False Positives when the auto-classifier disagrees with the description
**So that** I get an accurate picture of activation quality and an actionable hint instead of a misleading failure metric

**Acceptance Criteria**:
- [x] **AC-US1-01**: Auto-classified prompt where Phase 1 says `should_not_activate` and Phase 2 says `activate=true` produces a result with `verdict === "scope_warning"` and is excluded from `summary.fp`.
- [x] **AC-US1-02**: Auto-classified prompt where Phase 1 says `should_activate` and Phase 2 says `activate=false` produces a result with `verdict === "drift_warning"` and is excluded from `summary.fn`.
- [x] **AC-US1-03**: `ActivationSummary` exposes `scopeWarnings: number` and `driftWarnings: number` counts.
- [x] **AC-US1-04**: Precision = `tp / (tp + fp)` and Recall = `tp / (tp + fn)` — both denominators exclude warnings (warnings are a third bucket).

### US-002: Manual labels remain strict (P1)
**Project**: vskill

**As a** skill author who explicitly typed `+` or `!` prefix on a test prompt
**I want** any disagreement with my hand-labeled ground truth to register as a real FP or FN
**So that** I can catch real activation regressions when I have a strong opinion about expected behavior

**Acceptance Criteria**:
- [x] **AC-US2-01**: Non-auto-classified prompt (autoClassified=false) where `expected="should_not_activate"` and `activate=true` produces `verdict === "ok"` and `classification === "FP"`, counted in `summary.fp`.
- [x] **AC-US2-02**: Non-auto-classified prompt (autoClassified=false) where `expected="should_activate"` and `activate=false` produces `verdict === "ok"` and `classification === "FN"`, counted in `summary.fn`.

### US-003: UI surfaces warnings with author-actionable copy (P2)
**Project**: vskill

**As a** skill author looking at the Trigger tab
**I want** scope/drift warnings to render as a yellow pill with a clear explanation, distinct from red FP/FN failures
**So that** I can act on them by either narrowing the description or adding an explicit `+`/`!` prefix

**Acceptance Criteria**:
- [x] **AC-US3-01**: Result row badge color is yellow (`var(--yellow)` family) when `verdict !== "ok"`, replacing the red FP/FN badge for that row.
- [x] **AC-US3-02**: Confusion-matrix area shows a `Warnings: N scope, M drift` row beneath the existing 4 cells.
- [x] **AC-US3-03**: The "Incorrect" callout list at the top of the panel only includes results where `classification ∈ {FP, FN}` AND `verdict === "ok"` — warnings do not appear in the failure list.
- [x] **AC-US3-04**: Hovering a warning pill reveals an actionable tooltip: scope → "Description claims broader scope than name+tags suggest. Either narrow the description or add explicit `+` prefix to confirm intended scope." drift → "Description omits intent that classifier inferred from name+tags. Description may need to mention this case explicitly."

## Functional Requirements

### FR-001: Verdict type and scoring helper
Add `Verdict = "ok" | "scope_warning" | "drift_warning"` to `activation-tester.ts`. Add `computeVerdict(autoClassified, expected, activate): Verdict` helper. Only auto-classified results can return a non-"ok" verdict.

### FR-002: Backward-compatible result and summary shape
- `ActivationResult` gains `verdict: Verdict` (existing fields including `classification` unchanged).
- `ActivationSummary` gains `scopeWarnings: number`, `driftWarnings: number`. Existing `tp`/`tn`/`fp`/`fn` counts now exclude warning verdicts.

### FR-003: SSE pass-through
`/activation-test` route in `src/eval-server/api-routes.ts` already calls `sendSSEDone(res, { ...summary, description })` — new fields propagate to the UI without a route change.

### FR-004: UI rendering
- `CLASSIFICATION_STYLES` map gains `SCOPE_WARNING` and `DRIFT_WARNING` entries with yellow tones.
- Result row badge selection prefers `verdict !== "ok"` over `classification`.
- Confusion-matrix region renders a warnings sub-row.
- Incorrect-callout list filters `classification ∈ {FP, FN}` AND `verdict === "ok"`.

## Success Criteria

- All RED tests in `__tests__/activation-tester.test.ts` go GREEN after implementation.
- Existing vitest suite passes with no regressions.
- `npm run build:eval-ui` succeeds.
- Local studio smoke test on `hello-skill`:
  - Prompt `how are you today?` (no prefix → auto) → yellow scope-warning pill, precision N/A or 0/0, no FP count.
  - Prompt `+how are you today?` → green TP pill, precision 100%.
  - Prompt `!how are you today?` → red FP pill, precision 0%.

## Out of Scope

- Behavioral testing via `claude -p` (path 3 in the synthesis — separate followup).
- `## Test Cases` parser to ingest author-labeled fixtures from SKILL.md (path 2 — separate followup).
- Cross-skill confusion matrix on the registry.
- Cohen's-kappa per-skill metric.
- Active-learning queue for ambiguous cases.
- Server route shape changes — none needed.
- vskill-platform changes — out of scope (different codebase, different design).

## Dependencies

- Increment `_archive/0472-activation-auto-classify` — preserves its design intent.
- vskill repo at `repositories/anton-abyzov/vskill/`.
- Existing `LlmClient` mock pattern in `__tests__/activation-tester.test.ts`.
