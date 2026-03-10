---
id: US-003
feature: FS-465
title: Test Case Management Panel (P0)
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 43
    url: https://github.com/anton-abyzov/vskill/issues/43
---

# US-003: Test Case Management Panel (P0)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** test cases to be the central organizing unit with a list+detail layout
**So that** I can manage, edit, and run individual test cases efficiently

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given the Tests panel is active, when viewing the layout, then a left sub-panel (280px) shows a scrollable list of test cases with status pills (pass/fail/pending) and sparkline charts showing recent pass-rate trend
- [ ] **AC-US3-02**: Given a test case is selected in the list, when viewing the right sub-panel, then it shows the selected case's editable prompt textarea and expected output textarea
- [ ] **AC-US3-03**: Given a test case is selected, when viewing its assertions section, then an inline assertion builder allows add, edit, delete, and drag-to-reorder operations on assertions
- [ ] **AC-US3-04**: Given a test case has been run, when viewing its detail, then last run results appear inline showing each assertion's pass/fail status with reasoning text
- [ ] **AC-US3-05**: Given a test case is selected, when clicking its "Run" button, then a single-case benchmark triggers via SSE and the workspace switches to the Run panel scoped to that case
- [ ] **AC-US3-06**: Given a test case is selected, when clicking "A/B Compare", then a skill-vs-baseline comparison runs for that single case
- [ ] **AC-US3-07**: Given the Tests panel is active, when clicking "+ Add Test Case", then a form appears for entering prompt, expected output, and assertions for a new case
- [ ] **AC-US3-08**: Given a test case has a prompt and expected output, when clicking "Suggest Assertions", then AI-generated assertions are proposed and can be accepted/rejected individually

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
