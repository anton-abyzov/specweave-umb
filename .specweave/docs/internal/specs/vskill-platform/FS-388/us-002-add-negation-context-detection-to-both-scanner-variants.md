---
id: US-002
feature: FS-388
title: Add negation context detection to both scanner variants
status: complete
priority: P2
created: 2026-02-27
project: vskill-platform
external:
  github:
    issue: 1423
    url: https://github.com/anton-abyzov/specweave/issues/1423
---
# US-002: Add negation context detection to both scanner variants

**Feature**: [FS-388](./FEATURE.md)

platform operator
**I want** the scanner to detect negation words preceding pattern matches (e.g., "Don't use eval()", "Never call exec()")
**So that** documentation warning against dangerous patterns is not flagged as a threat

---

## Acceptance Criteria

- [x] **AC-US2-01**: Both `patterns.ts` and `scanner-patterns.js` include a negation detection function that checks for negation words within a window before the match position
- [x] **AC-US2-02**: Negation words detected include at minimum: "don't", "do not", "never", "avoid", "should not", "shouldn't", "must not", "mustn't", "warning", "caution", "beware"
- [x] **AC-US2-03**: When a pattern match is preceded by a negation word on the same line, the finding severity is downgraded to "info"
- [x] **AC-US2-04**: Negation detection does NOT downgrade DCI-abuse patterns (same exclusion as inline code)
- [x] **AC-US2-05**: Negation detection applies to all non-DCI patterns regardless of whether they are in DOCUMENTATION_SAFE_PATTERNS
- [x] **AC-US2-06**: `"Don't use eval()"` produces severity "info" (not "critical")
- [x] **AC-US2-07**: `"Never call exec() with user input"` produces severity "info" (not "critical")
- [x] **AC-US2-08**: `eval(userInput)` (no negation) remains severity "critical"

---

## Implementation

**Increment**: [0388-pattern-guided-llm-verdict](../../../../../increments/0388-pattern-guided-llm-verdict/spec.md)

