---
increment: 0388-pattern-guided-llm-verdict
title: >-
  Pattern-Guided LLM Verdict: Fix massive false positive rate from documentation
  mentioning dangerous patterns
type: bug
priority: P1
status: active
created: 2026-02-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Bug Fix: Pattern-Guided LLM Verdict (False Positive Reduction)

## Overview

The current Tier 1 scanner auto-blocks submissions with ANY critical finding
(finalize-scan route, line 330: `if (tier1.criticalCount > 0)`). This causes
massive false positives because:

1. **Documentation mentioning dangerous patterns gets blocked.** A SKILL.md that
   says "Don't use eval()" or "Never call exec() with untrusted input" triggers
   CI-001/CE-001 as critical, then gets immediately BLOCKED without Tier 2 review.

2. **Inline backtick detection exists but only in the platform-side patterns.ts.**
   The crawl-worker's `scanner-patterns.js` lacks the inline code, markdown prose,
   spawn context, and CT-003 safe-reference downgrades that `patterns.ts` has. Since
   scans run on Hetzner VMs using the crawl-worker code, the production scanner
   misses all these mitigations.

3. **Negation context is undetected.** Lines like "Don't use eval()" or "Avoid
   exec()" contain negative framing that indicates the pattern is being warned
   against, not invoked. Neither scanner variant detects this.

4. **Critical findings bypass Tier 2 entirely.** The finalize-scan route blocks on
   `tier1.criticalCount > 0` before Tier 2 gets a chance to validate whether the
   criticals are real threats or documentation references.

### Root Cause

Three compounding issues:

- **Scanner parity gap**: `crawl-worker/lib/scanner-patterns.js` diverged from
  `src/lib/scanner/patterns.ts` — missing inline code detection, markdown prose
  downgrades, spawn/exec context analysis, and CT-003 safe reference handling.

- **No negation detection**: Neither scanner checks for negation words preceding
  a pattern match (e.g., "don't", "never", "avoid", "do not").

- **Tier 1 criticals auto-block without LLM validation**: `finalize-scan` and
  `process-submission` immediately BLOCKED on criticals, never routing them to
  Tier 2 for contextual validation.

## User Stories

### US-001: Sync crawl-worker scanner-patterns.js with platform patterns.ts
**Project**: vskill-platform

**As a** platform operator
**I want** the crawl-worker scanner patterns to have the same context-aware severity downgrades as the platform-side patterns
**So that** scans on Hetzner VMs produce the same false-positive-reduced results as the platform's local scanner

**Acceptance Criteria**:
- [x] **AC-US1-01**: `scanner-patterns.js` includes `isInsideInlineCode()` function matching `patterns.ts` logic
- [x] **AC-US1-02**: `scanner-patterns.js` includes `isMarkdownProseLine()` function and `MARKDOWN_PROSE_RE`
- [x] **AC-US1-03**: `scanner-patterns.js` includes spawn context detection (`isSpawnWithSafeTarget`, `isSpawnWithDangerousPattern`, `SAFE_SPAWN_TARGETS`)
- [x] **AC-US1-04**: `scanner-patterns.js` includes CI-005 context detection (`isCi005Import`, `isExecLikeWithSafeTarget`, `isExecLikeWithDangerousPattern`)
- [x] **AC-US1-05**: `scanner-patterns.js` includes CT-003 safe reference detection (`isCt003SafeReference`)
- [x] **AC-US1-06**: `scanContent()` in `scanner-patterns.js` applies all context-aware downgrades (inline code, markdown prose, CI-002, CI-005, CT-003) matching `patterns.ts`
- [x] **AC-US1-07**: `DOCUMENTATION_SAFE_PATTERNS` set in `scanner-patterns.js` matches the platform version (includes CI-002, CI-004, CI-005, DE-005, NA-003)
- [x] **AC-US1-08**: CI-002 severity in `scanner-patterns.js` pattern definition changes from "medium" to "low" (matches platform)
- [x] **AC-US1-09**: DE-005 severity changes from "medium" to "low" (matches platform)
- [x] **AC-US1-10**: NA-003 severity changes from "medium" to "low" (matches platform)

---

### US-002: Add negation context detection to both scanner variants
**Project**: vskill-platform

**As a** platform operator
**I want** the scanner to detect negation words preceding pattern matches (e.g., "Don't use eval()", "Never call exec()")
**So that** documentation warning against dangerous patterns is not flagged as a threat

**Acceptance Criteria**:
- [x] **AC-US2-01**: Both `patterns.ts` and `scanner-patterns.js` include a negation detection function that checks for negation words within a window before the match position
- [x] **AC-US2-02**: Negation words detected include at minimum: "don't", "do not", "never", "avoid", "should not", "shouldn't", "must not", "mustn't", "warning", "caution", "beware"
- [x] **AC-US2-03**: When a pattern match is preceded by a negation word on the same line, the finding severity is downgraded to "info"
- [x] **AC-US2-04**: Negation detection does NOT downgrade DCI-abuse patterns (same exclusion as inline code)
- [x] **AC-US2-05**: Negation detection applies to all non-DCI patterns regardless of whether they are in DOCUMENTATION_SAFE_PATTERNS
- [x] **AC-US2-06**: `"Don't use eval()"` produces severity "info" (not "critical")
- [x] **AC-US2-07**: `"Never call exec() with user input"` produces severity "info" (not "critical")
- [x] **AC-US2-08**: `eval(userInput)` (no negation) remains severity "critical"

---

### US-003: Route Tier 1 critical findings to Tier 2 LLM for contextual validation
**Project**: vskill-platform

**As a** platform operator
**I want** critical Tier 1 findings to be validated by the Tier 2 LLM before auto-blocking
**So that** false-positive criticals from documentation context do not cause incorrect blocks

**Acceptance Criteria**:
- [x] **AC-US3-01**: `finalize-scan` route no longer auto-blocks on `tier1.criticalCount > 0` when Tier 2 results are present
- [x] **AC-US3-02**: When Tier 2 is present and its verdict is PASS or CONCERNS with score >= 60, critical findings are treated as false positives and the submission proceeds normally
- [x] **AC-US3-03**: When Tier 2 is present and confirms the threats (verdict FAIL or score < 40), the submission is BLOCKED as before with the critical violation reason
- [x] **AC-US3-04**: When Tier 2 is absent/failed but all critical findings have severity "info" (downgraded by context), submission proceeds without blocking
- [x] **AC-US3-05**: When Tier 2 is absent/failed and there are genuine (non-downgraded) critical findings, the submission is BLOCKED as before (safety fallback)
- [x] **AC-US3-06**: The crawl-worker `submission-scanner.js` no longer early-exits T1 failures before running T2 when there are critical findings — it must still run T2
- [x] **AC-US3-07**: Tier 2 prompt is enhanced to include the critical findings with their context lines, asking the LLM to classify each as "confirmed" or "false_positive"

---

### US-004: Enhance Tier 2 prompt for critical finding validation
**Project**: vskill-platform

**As a** platform operator
**I want** the Tier 2 LLM prompt to explicitly validate each critical Tier 1 finding
**So that** the LLM provides structured per-finding verdicts instead of just an overall assessment

**Acceptance Criteria**:
- [x] **AC-US4-01**: Both `tier2.ts` and `tier2-scan.js` user prompts include a "Critical Findings Validation" section when `criticalCount > 0`
- [x] **AC-US4-02**: Each critical finding is listed with its pattern ID, matched text, and 3-line context window
- [x] **AC-US4-03**: The LLM is instructed to classify each critical finding as "confirmed" (real threat) or "false_positive" (documentation/educational reference)
- [x] **AC-US4-04**: The LLM response JSON includes a `criticalValidation` array with `{patternId, verdict: "confirmed"|"false_positive", reason}` entries
- [x] **AC-US4-05**: The Tier 2 response parser extracts `criticalValidation` and exposes it in the Tier2Result type
- [x] **AC-US4-06**: `finalize-scan` uses `criticalValidation` to determine if criticals are confirmed before blocking

## Functional Requirements

### FR-001: Scanner parity
Both `scanner-patterns.js` (crawl-worker) and `patterns.ts` (platform) must produce
identical severity classifications for the same input. The crawl-worker JS is the
production scanner — it must have feature parity with the TS version.

### FR-002: Negation context window
The negation detection scans backwards from the match position on the same line,
looking for negation words within a 60-character window. This prevents matching
negations from distant parts of the same line while catching common patterns like
"Don't use eval()" or "Avoid calling exec()".

### FR-003: Critical-to-Tier-2 routing
When Tier 1 produces critical findings, the pipeline must still run Tier 2 (if
available) before making a BLOCKED decision. The Tier 2 LLM validates each
critical finding individually. Only confirmed criticals trigger auto-block.

### FR-004: Backward compatibility
- Genuinely malicious skills (actual eval/exec calls, not documentation mentions) must
  still be detected and blocked
- DCI-abuse patterns must never be downgraded by negation or inline code detection
- When Tier 2 is unavailable AND there are real critical findings, the safety
  fallback remains BLOCKED

## Success Criteria

- Documentation-style SKILL.md files that mention `eval()`, `exec()`, `.ssh/`,
  `AWS_SECRET_ACCESS_KEY` etc. in educational/warning context score PASS
- Actually malicious skills with real `eval(userInput)` calls still score FAIL/BLOCKED
- The crawl-worker scanner produces equivalent results to the platform scanner
- False positive rate for documentation-mentioning skills drops by > 80%

## Out of Scope

- Rewriting the scanner from regex to AST-based (future enhancement)
- Changing the overall scoring weights or thresholds
- Modifying the blocklist entry creation logic
- UI changes to the admin dashboard

## Dependencies

- No external dependencies — all changes within vskill-platform
