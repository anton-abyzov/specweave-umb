---
id: US-005
feature: FS-367
title: Timeout/Error Classification
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1316
    url: https://github.com/anton-abyzov/specweave/issues/1316
---
# US-005: Timeout/Error Classification

**Feature**: [FS-367](./FEATURE.md)

platform operator
**I want** processing failures classified by root cause
**So that** I can identify systemic issues (e.g., GitHub API outage vs AI model failures)

---

## Acceptance Criteria

- [x] **AC-US5-01**: Timeout errors distinguished from other failures via error message pattern matching
- [x] **AC-US5-04**: Consumer catch block classifies timeout vs other before calling `recordTimeout()` or `recordFailed()`

---

## Implementation

**Increment**: [0367-stuck-submission-detection](../../../../../increments/0367-stuck-submission-detection/spec.md)

