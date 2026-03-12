---
id: US-003
feature: FS-442
title: "V2 Verdict Logic (P1)"
status: completed
priority: P1
created: "2026-03-06T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
external:
  github:
    issue: 24
    url: "https://github.com/anton-abyzov/vskill-platform/issues/24"
---

# US-003: V2 Verdict Logic (P1)

**Feature**: [FS-442](./FEATURE.md)

**As a** platform operator
**I want** the verdict computed from assertion pass rate (primary) and rubric delta (secondary)
**So that** eval verdicts reflect both "meets its own claims" and "better than no skill"

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `assertionPassRate >= 0.80` AND skill rubric overall > baseline rubric overall + 1, when computing verdict, then the result is `EFFECTIVE`
- [x] **AC-US3-02**: Given `assertionPassRate >= 0.60` AND skill rubric > baseline rubric, when computing verdict, then the result is `MARGINAL`
- [x] **AC-US3-03**: Given `assertionPassRate >= 0.40` (but not meeting EFFECTIVE or MARGINAL thresholds), when computing verdict, then the result is `INEFFECTIVE`
- [x] **AC-US3-04**: Given `assertionPassRate < 0.40`, when computing verdict, then the result is `DEGRADING`
- [x] **AC-US3-05**: Given an eval run with `methodologyVersion` null (V1), when displaying results, then the V1 verdict logic (deltaScore thresholds) is used unchanged
- [x] **AC-US3-06**: Given an eval run, when stored, then `EvalRun.methodologyVersion` is set to `2` for all new V2 runs

---

## Implementation

**Increment**: [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Implement verdict-v2.ts with four-tier verdict logic
