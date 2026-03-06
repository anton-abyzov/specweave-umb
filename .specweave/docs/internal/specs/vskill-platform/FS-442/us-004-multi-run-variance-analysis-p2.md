---
id: US-004
feature: FS-442
title: "Multi-Run Variance Analysis (P2)"
status: completed
priority: P1
created: 2026-03-06T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-004: Multi-Run Variance Analysis (P2)

**Feature**: [FS-442](./FEATURE.md)

**As a** platform operator
**I want** each test case run N times with mean/stddev computed per assertion
**So that** I can detect flaky tests and non-discriminating assertions

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given trigger `SUBMISSION`, when eval runs, then each test case executes 1 time (N=1, fast path)
- [x] **AC-US4-02**: Given trigger `REGRESSION`, when eval runs, then each test case executes 3 times (N=3)
- [x] **AC-US4-03**: Given trigger `REVERIFY`, when eval runs, then each test case executes 5 times (N=5)
- [x] **AC-US4-04**: Given N runs of a test case, when aggregating, then the system computes mean and stddev of each assertion's pass rate (1=pass, 0=fail across runs)
- [x] **AC-US4-05**: Given an assertion with pass rate stddev > 0.3 across runs, when the eval completes, then the assertion is flagged as `flaky: true` in the variance data
- [x] **AC-US4-06**: Given an assertion that passes in ALL runs across ALL test cases, when the eval completes, then the assertion is flagged as `nonDiscriminating: true`
- [x] **AC-US4-07**: Given multi-run data, when stored, then `EvalRun.varianceData` JSON column contains `{ perAssertion: [{ assertionId, mean, stddev, flaky, nonDiscriminating }], totalRuns }`

---

## Implementation

**Increment**: [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Implement variance-analyzer.ts
- [x] **T-011**: Implement eval-engine-v2.ts with multi-run orchestration
