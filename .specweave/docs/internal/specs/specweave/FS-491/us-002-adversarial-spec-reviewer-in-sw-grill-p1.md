---
id: US-002
feature: FS-491
title: "Adversarial Spec Reviewer in sw:grill (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** SpecWeave user running sw:grill before increment closure."
project: specweave
external:
  github:
    issue: 1539
    url: "https://github.com/anton-abyzov/specweave/issues/1539"
---

# US-002: Adversarial Spec Reviewer in sw:grill (P1)

**Feature**: [FS-491](./FEATURE.md)

**As a** SpecWeave user running sw:grill before increment closure
**I want** a new Phase 0 (Spec Compliance Interrogation) that adversarially verifies every AC against the implementation
**So that** spec drift, missing features, and misinterpretations are caught with adversarial framing before the existing code review phases

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given sw:grill is invoked, when Phase 0 runs, then it loads spec.md, extracts all ACs, and verifies implementation exists for each with adversarial framing ("prove this AC is satisfied")
- [x] **AC-US2-02**: Given Phase 0 completes, when it finds an AC not satisfied, then the finding includes: AC ID, expected behavior, actual behavior, and a pass/fail status
- [x] **AC-US2-03**: Given Phase 0 completes, when it finds functionality not traceable to any AC (scope creep), then it flags the extra functionality as a finding
- [x] **AC-US2-04**: Given Phase 0 runs, when grill-report.json is written, then it includes an `acCompliance` section with per-AC pass/fail results
- [x] **AC-US2-05**: Phase 0 always runs (not opt-in) and executes before existing Phase 1 (Context Gathering)

---

## Implementation

**Increment**: [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add Phase 0 (Spec Compliance Interrogation) to sw:grill
- [x] **T-004**: Extend grill-report.json Schema with acCompliance Section
