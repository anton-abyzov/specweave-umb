---
id: US-002
feature: FS-487
title: "Progress UI for AI Operations"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 80
    url: "https://github.com/anton-abyzov/vskill/issues/80"
---

# US-002: Progress UI for AI Operations

**Feature**: [FS-487](./FEATURE.md)

**As a** skill developer
**I want** to see ProgressLog-style feedback during AI Edit, Generate Evals, and Auto-Improve
**So that** I know the system is working and can see elapsed time and current phase

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given AI Edit is submitted in the AiEditBar, when the generation is in progress, then a ProgressLog component appears below the input showing phase transitions and elapsed time
- [x] **AC-US2-02**: Given Auto-Improve is triggered in the SkillImprovePanel, when the improvement is running, then a ProgressLog component appears showing progress phases and elapsed time
- [x] **AC-US2-03**: Given Generate Evals is triggered, when generation is in progress, then a ProgressLog component appears showing progress phases and elapsed time
- [x] **AC-US2-04**: Given Generate Skill (AI-assisted creation) is triggered, when generation is in progress, then a ProgressLog component appears showing progress phases and elapsed time
- [x] **AC-US2-05**: Given an AI operation completes successfully, then the ProgressLog collapses and the result (diff view, generated evals, etc.) is displayed as before

---

## Implementation

**Increment**: [0487-skill-studio-execution-observability](../../../../../increments/0487-skill-studio-execution-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Make ProgressLog component work without evalId
- [x] **T-005**: Add ProgressLog and Cancel to AiEditBar
- [x] **T-006**: Add ProgressLog to SkillImprovePanel
- [x] **T-007**: Add ProgressLog to TestsPanel (generate-evals) and CreateSkillPage (generate-skill)
