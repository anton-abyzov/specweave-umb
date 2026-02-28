---
id: US-003
feature: FS-388
title: Route Tier 1 critical findings to Tier 2 LLM for contextual validation
status: not-started
priority: P2
created: 2026-02-27
project: vskill-platform
external:
  github:
    issue: 1424
    url: https://github.com/anton-abyzov/specweave/issues/1424
---
# US-003: Route Tier 1 critical findings to Tier 2 LLM for contextual validation

**Feature**: [FS-388](./FEATURE.md)

platform operator
**I want** critical Tier 1 findings to be validated by the Tier 2 LLM before auto-blocking
**So that** false-positive criticals from documentation context do not cause incorrect blocks

---

## Acceptance Criteria

- [ ] **AC-US3-01**: `finalize-scan` route no longer auto-blocks on `tier1.criticalCount > 0` when Tier 2 results are present
- [ ] **AC-US3-02**: When Tier 2 is present and its verdict is PASS or CONCERNS with score >= 60, critical findings are treated as false positives and the submission proceeds normally
- [ ] **AC-US3-03**: When Tier 2 is present and confirms the threats (verdict FAIL or score < 40), the submission is BLOCKED as before with the critical violation reason
- [ ] **AC-US3-04**: When Tier 2 is absent/failed but all critical findings have severity "info" (downgraded by context), submission proceeds without blocking
- [ ] **AC-US3-05**: When Tier 2 is absent/failed and there are genuine (non-downgraded) critical findings, the submission is BLOCKED as before (safety fallback)
- [ ] **AC-US3-06**: The crawl-worker `submission-scanner.js` no longer early-exits T1 failures before running T2 when there are critical findings — it must still run T2
- [ ] **AC-US3-07**: Tier 2 prompt is enhanced to include the critical findings with their context lines, asking the LLM to classify each as "confirmed" or "false_positive"

---

## Implementation

**Increment**: [0388-pattern-guided-llm-verdict](../../../../../increments/0388-pattern-guided-llm-verdict/spec.md)

