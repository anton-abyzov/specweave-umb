---
increment: 0709-eval-ui-test-drift-cleanup
title: "eval-ui test-drift cleanup"
generated: "2026-04-24"
source: manual
version: "1.0"
status: ready
---

# Rubric — eval-ui test-drift cleanup

Minimal contract for a test-only hygiene increment. Two blocking criteria
that together guarantee the increment achieved its stated goal without
side effects. One advisory criterion for snapshot fidelity.

## Blocking criteria

### R-001 [blocking] — All 7 ACs pass
**Evaluator**: sw:code-reviewer (spec-compliance section) + Gate 0 automated validator
**Pass condition**: Every AC in spec.md (`AC-US1-01..05`, `AC-US2-01..02`) is checked `[x]` in spec.md AND the scoped `npx vitest run` on the four touched test files exits 0.
**Evidence**: `reports/code-review-report.json` spec-compliance section + `spec.md` AC checkboxes.
**Status**: PASS (per code-review-report.json: "7/7 ACs pass"; all ACs checked; scoped sweep 30/30 green)

### R-002 [blocking] — Zero production-code churn attributable to 0709
**Evaluator**: sw:code-reviewer (tests/logic reviewers) + manual git diff inspection
**Pass condition**: Diff filtered to files owned by this increment touches ONLY `src/eval-ui/**/__tests__/**` and `src/eval-ui/**/__snapshots__/**`. Production files (`TopRail.tsx`, `PluginTreeGroup.tsx`, etc.) are NOT modified by this increment. Any production code in the bundled commit must be attributed to a different increment in `reports/CLOSURE-NOTES.md`.
**Evidence**: `reports/CLOSURE-NOTES.md` ("0709 scoped diff (test-only, zero production churn)" section) + code-review-report.json logic reviewer confirmation ("No TS type changes", "No defects in the test logic").
**Status**: PASS (0709-scoped diff touches only 3 `__tests__/*.test.tsx` + 1 `__snapshots__/*.snap`; production churn in bundled commit is 0704 T-013a/b, documented in CLOSURE-NOTES.md)

## Advisory criteria

### R-003 [advisory] — PluginTreeGroup snapshot mirrors declared 0698 T-010 design intent
**Evaluator**: Manual review + string-literal check
**Pass condition**: The re-recorded snapshot contains all six tokens from the current `PluginTreeGroup.tsx:83-119`: `padding-right:6px`, `width:16px`, `font-size:14px`, `font-weight:700`, `color:var(--color-ink, var(--text-primary))`, flex wrapper.
**Evidence**: `grep -o` against the snap file (run during T-004) returned all 6 canonical tokens.
**Status**: PASS
