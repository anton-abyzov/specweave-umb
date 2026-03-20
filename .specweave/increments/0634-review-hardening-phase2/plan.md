---
increment: 0634-review-hardening-phase2
---

# Architecture Plan: Review Hardening Phase 2

## Approach

Minimal changes to 6 existing files. No new files or dependencies.

## Files to Modify

| File | Changes |
|------|---------|
| `src/security/platform-security.ts` | Sanitize logged values; guard empty string |
| `src/security/platform-security.test.ts` | Add empty string + sanitization tests |
| `src/eval/verdict.ts` | Consolidate INEFFECTIVE; improve fallback recommendations |
| `src/eval/__tests__/verdict.test.ts` | NaN baselinePassRate test; DEGRADING high score test |
| `src/eval-ui/src/pages/workspace/RunPanel.tsx` | isNaN → !isFinite |
| `src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` | Infinity input test |

## Key Decisions

- **Sanitize helper**: Inline `String(v).replace(/[\x00-\x1f\x7f]/g, "").slice(0, 50)` — no separate function for 3 call sites
- **INEFFECTIVE consolidation**: Single `if (verdict === "INEFFECTIVE")` block with inner `score < 0.2` check
- **Skip exhaustiveness**: verdictExplanation has intentional catch-all behavior for edge combos like EFFECTIVE+0.3
- **Skip Partial<Record> tsconfig**: Would require codebase-wide fixes, not worth the scope
