---
increment: 0388-pattern-guided-llm-verdict
title: Architecture Plan
---

# Architecture Plan: Pattern-Guided LLM Verdict

## Overview

This fix addresses three layers of the scan pipeline: the crawl-worker scanner
(production), the platform scanner (backup/local), and the finalize-scan routing
logic. Changes flow bottom-up: scanner patterns first, then routing logic.

## Architecture Decisions

### AD-001: Port missing functions to scanner-patterns.js

**Decision**: Copy the context-aware detection functions from `patterns.ts` to
`scanner-patterns.js` and integrate them into `scanContent()`.

**Rationale**: The crawl-worker runs on Hetzner VMs as pure JS. The two scanners
diverged — the TS version got inline code detection, markdown prose downgrades,
spawn context, CI-005 context, and CT-003 safe references, but the JS version
was never updated. Since the crawl-worker is the production scanner, this parity
gap is the primary cause of false positives.

**Files**:
- `crawl-worker/lib/scanner-patterns.js` — add functions, update `scanContent()`

### AD-002: Add negation detection as a new shared concern

**Decision**: Implement `isNegatedContext()` in both scanner files. The function
checks for negation words within a 60-character lookback window on the same line,
preceding the match position.

**Rationale**: A regex-only approach cannot distinguish "Don't use eval()" from
"eval(userInput)". Simple lookback for negation words is lightweight, high-precision,
and avoids NLP complexity. The 60-char window handles typical sentence patterns
without false-matching distant negations.

**Implementation**:
```
NEGATION_WORDS = ["don't", "do not", "never", "avoid", "should not", "shouldn't",
  "must not", "mustn't", "warning", "caution", "beware", "not recommended",
  "do NOT", "NEVER", "AVOID"]

function isNegatedContext(line, matchStart):
  lookback = line.substring(max(0, matchStart - 60), matchStart).toLowerCase()
  return NEGATION_WORDS.some(word => lookback.includes(word))
```

**Files**:
- `src/lib/scanner/patterns.ts` — add `isNegatedContext()`, apply in `scanContent()`
- `crawl-worker/lib/scanner-patterns.js` — add `isNegatedContext()`, apply in `scanContent()`

### AD-003: Remove critical auto-block, route to Tier 2

**Decision**: In `finalize-scan` route, remove the `if (tier1.criticalCount > 0)`
immediate BLOCKED path. Instead, check if Tier 2 validated the criticals. In the
crawl-worker `submission-scanner.js`, remove the early T1-fail exit when criticals
are present (still run T2).

**Rationale**: The current logic blocks on any critical, never giving Tier 2 a
chance to validate. After scanner context downgrades (inline code, negation, prose),
many criticals become "info" severity. We only auto-block when:
1. There are remaining non-downgraded criticals AND
2. Either Tier 2 confirms them OR Tier 2 is unavailable (safety fallback)

**Files**:
- `src/app/api/v1/internal/finalize-scan/route.ts` — replace critical auto-block
- `crawl-worker/sources/submission-scanner.js` — remove early T1-fail exit for criticals

### AD-004: Enhance Tier 2 prompt for critical validation

**Decision**: When `criticalCount > 0`, add a "Critical Findings Validation" section
to the Tier 2 user prompt listing each critical finding with context. Ask the LLM to
return a `criticalValidation` array classifying each as "confirmed" or "false_positive".

**Rationale**: The existing Tier 2 prompt gives an overall verdict but doesn't
specifically address individual findings. With explicit per-finding validation, the
LLM's decision is structured and auditable.

**Files**:
- `src/lib/scanner/tier2.ts` — update prompt, parse `criticalValidation`
- `crawl-worker/lib/tier2-scan.js` — mirror the same changes

## Component Diagram

```
SKILL.md → [Crawl Worker VM]
              ├─ tier1-scan.js → scanner-patterns.js (52 patterns + context downgrades + negation)
              │                    ├─ isInsideInlineCode()     [NEW]
              │                    ├─ isMarkdownProseLine()    [NEW]
              │                    ├─ isNegatedContext()       [NEW]
              │                    ├─ isSpawnWithSafeTarget()  [NEW]
              │                    ├─ isCt003SafeReference()   [NEW]
              │                    └─ ...                      [NEW]
              ├─ tier2-scan.js → CF AI REST API
              │                    └─ Enhanced prompt with criticalValidation [CHANGED]
              └─ submission-scanner.js
                   └─ Remove early T1-fail exit for criticals [CHANGED]

Results → [Platform: finalize-scan]
              ├─ Store T1 result
              ├─ Check criticals:
              │    ├─ T2 present + criticalValidation → use per-finding verdicts
              │    ├─ T2 absent + all criticals downgraded → proceed normally
              │    └─ T2 absent + real criticals → BLOCKED (safety fallback)
              └─ Continue normal flow (T1 FAIL/PASS/CONCERNS paths)
```

## File Change Summary

| File | Change Type | Description |
|------|------------|-------------|
| `crawl-worker/lib/scanner-patterns.js` | Major | Port all context-aware functions from patterns.ts, add negation detection |
| `src/lib/scanner/patterns.ts` | Minor | Add negation detection function |
| `src/lib/scanner/tier2.ts` | Moderate | Enhanced prompt with criticalValidation |
| `crawl-worker/lib/tier2-scan.js` | Moderate | Mirror tier2.ts prompt changes |
| `src/app/api/v1/internal/finalize-scan/route.ts` | Moderate | Replace critical auto-block with Tier 2 routing |
| `crawl-worker/sources/submission-scanner.js` | Minor | Remove early T1-fail exit for criticals |

## Risk Mitigation

1. **Security regression**: Genuine malicious skills could slip through if Tier 2
   incorrectly marks criticals as false positives. Mitigated by: safety fallback
   (T2 unavailable → BLOCKED), DCI patterns exempt from negation/inline downgrades,
   and auto-block threshold (2 failures) still applies.

2. **Scanner parity drift**: The JS and TS scanners could diverge again. Mitigated by:
   adding a cross-scanner parity test that runs the same inputs through both and
   compares results.

3. **LLM prompt stability**: The enhanced Tier 2 prompt could cause unexpected LLM
   behavior. Mitigated by: keeping the existing JSON format, adding criticalValidation
   as optional (parser defaults to empty array if missing).
