---
id: US-001
feature: FS-442
title: "Assertion-Based Grading (P1)"
status: completed
priority: P1
created: "2026-03-06T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-001: Assertion-Based Grading (P1)

**Feature**: [FS-442](./FEATURE.md)

**As a** platform operator
**I want** each test case graded against specific verifiable assertions (PASS/FAIL with evidence)
**So that** I can pinpoint exactly which claims a skill fails to deliver on

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a test case with N assertions, when the eval runs, then the LLM judge returns `{ pass: boolean, reasoning: string }` for each assertion individually
- [x] **AC-US1-02**: Given a test case with 3 assertions where 2 pass and 1 fails, when the assertion results are aggregated, then the case `assertionPassRate` equals 0.67
- [x] **AC-US1-03**: Given an assertion result, when stored in the DB, then the `EvalCase.assertionResults` JSON column contains an array of `{ assertionId, assertionText, pass, reasoning }` objects
- [x] **AC-US1-04**: Given an eval run with multiple cases, when the run completes, then the `EvalRun` record includes an `assertionPassRate` field computed as total passed / total assertions across all cases

---

## Implementation

**Increment**: [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Implement assertion-grader.ts with batch LLM grading
- [x] **T-004**: Aggregate assertion results into EvalCase and EvalRun fields
