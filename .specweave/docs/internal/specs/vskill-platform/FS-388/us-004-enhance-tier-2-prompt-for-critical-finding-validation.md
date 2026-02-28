---
id: US-004
feature: FS-388
title: Enhance Tier 2 prompt for critical finding validation
status: not-started
priority: P2
created: 2026-02-27
project: vskill-platform
external:
  github:
    issue: 1425
    url: https://github.com/anton-abyzov/specweave/issues/1425
---
# US-004: Enhance Tier 2 prompt for critical finding validation

**Feature**: [FS-388](./FEATURE.md)

platform operator
**I want** the Tier 2 LLM prompt to explicitly validate each critical Tier 1 finding
**So that** the LLM provides structured per-finding verdicts instead of just an overall assessment

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Both `tier2.ts` and `tier2-scan.js` user prompts include a "Critical Findings Validation" section when `criticalCount > 0`
- [ ] **AC-US4-02**: Each critical finding is listed with its pattern ID, matched text, and 3-line context window
- [ ] **AC-US4-03**: The LLM is instructed to classify each critical finding as "confirmed" (real threat) or "false_positive" (documentation/educational reference)
- [ ] **AC-US4-04**: The LLM response JSON includes a `criticalValidation` array with `{patternId, verdict: "confirmed"|"false_positive", reason}` entries
- [ ] **AC-US4-05**: The Tier 2 response parser extracts `criticalValidation` and exposes it in the Tier2Result type
- [ ] **AC-US4-06**: `finalize-scan` uses `criticalValidation` to determine if criticals are confirmed before blocking

---

## Implementation

**Increment**: [0388-pattern-guided-llm-verdict](../../../../../increments/0388-pattern-guided-llm-verdict/spec.md)

