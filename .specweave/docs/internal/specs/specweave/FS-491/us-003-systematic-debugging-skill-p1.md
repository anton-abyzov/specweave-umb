---
id: US-003
feature: FS-491
title: "Systematic Debugging Skill (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** SpecWeave user encountering a difficult bug."
project: specweave
external:
  github:
    issue: 1540
    url: https://github.com/anton-abyzov/specweave/issues/1540
---

# US-003: Systematic Debugging Skill (P1)

**Feature**: [FS-491](./FEATURE.md)

**As a** SpecWeave user encountering a difficult bug
**I want** a dedicated sw:debug skill with a 4-phase systematic debugging methodology
**So that** I follow a disciplined investigation process instead of ad-hoc trial-and-error

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a user invokes /sw:debug with a bug description, when Phase 1 (Root Cause Investigation) runs, then it systematically gathers evidence: error messages, stack traces, recent changes, and affected code paths
- [x] **AC-US3-02**: Given Phase 1 completes, when Phase 2 (Pattern Analysis) runs, then it identifies recurring patterns, similar past bugs, and potential root cause hypotheses
- [x] **AC-US3-03**: Given Phase 2 completes, when Phase 3 (Hypothesis Testing) runs, then it tests each hypothesis with minimal, targeted experiments and captures results
- [x] **AC-US3-04**: Given Phase 3 completes, when Phase 4 (Implementation) runs, then it implements the verified fix with tests proving the bug is resolved
- [x] **AC-US3-05**: Given 3 consecutive fix attempts fail, when the next attempt would start, then the skill stops and questions the architectural assumptions (escalation protocol)
- [x] **AC-US3-06**: The SKILL.md includes an anti-rationalization table with 8+ entries mapping common excuses to rebuttals (e.g., "quick fix for now" -> rebuttal)
- [x] **AC-US3-07**: The SKILL.md defines red flags that trigger escalation: "quick fix for now", "skip the test", "one more attempt", "it works on my machine"

---

## Implementation

**Increment**: [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Create sw:debug SKILL.md with 4-Phase Debugging Methodology
