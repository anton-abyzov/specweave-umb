---
id: US-006
feature: FS-455
title: "Auto-Activation Description Testing (P2)"
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 22
    url: https://github.com/anton-abyzov/vskill/issues/22
---

# US-006: Auto-Activation Description Testing (P2)

**Feature**: [FS-455](./FEATURE.md)

**As a** skill developer
**I want** to test how reliably my SKILL.md description triggers for sample prompts
**So that** I can optimize the description to reduce false positives and false negatives

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given I navigate to the activation test tab for a skill, when I enter sample prompts (one per line), then the system uses the LLM to evaluate whether each prompt would trigger the skill's SKILL.md description
- [x] **AC-US6-02**: Given sample prompts are evaluated, when results are displayed, then each prompt shows: activation likelihood (yes/no), confidence level, and reasoning explaining why it would or would not trigger
- [x] **AC-US6-03**: Given I mark prompts as "should activate" or "should not activate", when the test runs, then the report classifies results as true positive, true negative, false positive, or false negative
- [x] **AC-US6-04**: Given activation test results are ready, when I view the summary, then I see precision, recall, and an overall activation reliability score

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-012**: Implement activation tester endpoint and UI tab
