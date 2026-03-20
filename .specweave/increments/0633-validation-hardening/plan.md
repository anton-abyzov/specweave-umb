---
increment: 0633-validation-hardening
---

# Architecture Plan: Validation Hardening

## Approach

Minimal changes to 6 existing files. No new files, no new dependencies, no architectural changes. All changes are localized bug fixes and type tightening.

## Files to Modify

| File | Changes |
|------|---------|
| `src/security/platform-security.ts` | Add `console.warn` to `safeNumber`/`validateEnum` fallback paths; `ReadonlySet` on validation sets |
| `src/security/platform-security.test.ts` | Fix fixture default; add logging assertions |
| `src/eval/verdict.ts` | Add recommendation branches for MARGINAL, EMERGING, INEFFECTIVE[0.2-0.7) |
| `src/eval/__tests__/verdict.test.ts` | Add NaN input tests; add recommendation tests |
| `src/eval-ui/src/pages/workspace/RunPanel.tsx` | `APPROX_COST_PER_CALL` → `Partial<Record>`; NaN guard in `formatComparisonScore` |
| `src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` | Add NaN input test for `formatComparisonScore` |

## Key Decisions

- **console.warn over structured logger**: The codebase has no logging framework; `console.warn` is consistent with existing patterns.
- **ReadonlySet**: Prevents accidental `.add()/.delete()/.clear()` at type level. No runtime cost.
- **Recommendation branches inserted before default**: Maintains existing branch ordering (specific → general).
- **Partial<Record>**: Makes undefined access type-visible without changing runtime behavior.
