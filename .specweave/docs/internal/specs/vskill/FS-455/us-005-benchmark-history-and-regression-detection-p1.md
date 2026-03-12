---
id: US-005
feature: FS-455
title: "Benchmark History and Regression Detection (P1)"
status: completed
priority: P1
created: "2026-03-08T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 21
    url: "https://github.com/anton-abyzov/vskill/issues/21"
---

# US-005: Benchmark History and Regression Detection (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** skill developer
**I want** to view benchmark history across runs and see which assertions regressed or improved
**So that** I can track skill quality over time and catch regressions early

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given a skill has multiple benchmark runs in `evals/history/`, when I view the history tab, then I see a chronological list of runs with timestamp, model, and overall pass rate
- [x] **AC-US5-02**: Given I select two runs, when I view the diff, then assertions that changed from PASS to FAIL are highlighted as regressions, and FAIL to PASS as improvements
- [x] **AC-US5-03**: Given a new benchmark run completes, when an assertion that passed in the previous run now fails, then the UI displays a regression warning badge next to that assertion
- [x] **AC-US5-04**: Given history files exist, when I view a single run's detail, then I see the full benchmark result including per-case pass rates, assertion-level reasoning, and model info

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Implement history API endpoints with regression computation
- [x] **T-011**: Build history timeline and regression diff UI
