---
id: US-001
feature: FS-531
title: "Progressive Skill vs Baseline Summary (P1)"
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** skill developer running a benchmark comparison."
project: vskill
---

# US-001: Progressive Skill vs Baseline Summary (P1)

**Feature**: [FS-531](./FEATURE.md)

**As a** skill developer running a benchmark comparison
**I want** a running summary of skill avg, baseline avg, delta, and preview verdict that updates as each case completes
**So that** I can monitor quality trends during execution without waiting for the full run to finish

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a comparison is running and 0 cases have completed, when the ComparisonPage renders, then a "Comparing..." placeholder is shown with a progress bar displaying "0/N cases"
- [x] **AC-US1-02**: Given K of N cases have completed via SSE events, when a new case-complete event arrives, then the summary bar updates to show the current skill avg, baseline avg, and rubric delta computed client-side from accumulated results
- [x] **AC-US1-03**: Given K of N cases have completed, when the summary bar renders, then a preview verdict label is displayed using the same tier logic as the final verdict (EFFECTIVE / MARGINAL / INEFFECTIVE / EMERGING / DEGRADING)
- [x] **AC-US1-04**: Given all N cases have completed (done SSE event), when the summary bar renders, then it matches the final verdict bar exactly with no visual jump or flicker

---

## Implementation

**Increment**: [0531-benchmark-comparison-ux](../../../../../increments/0531-benchmark-comparison-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add EMERGING to EvalVerdict type and update computeVerdict logic
- [x] **T-002**: Create shared verdict-styles.ts module
