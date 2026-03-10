---
id: US-007
feature: FS-465
title: Edit-Test-Iterate Tight Loop (P0)
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 47
    url: https://github.com/anton-abyzov/vskill/issues/47
---

# US-007: Edit-Test-Iterate Tight Loop (P0)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** the edit-test-iterate workflow to be seamless
**So that** failed assertions guide me directly to improvements without manual context switching

---

## Acceptance Criteria

- [ ] **AC-US7-01**: Given a test case has a failed assertion, when clicking "Fix with AI" on that assertion, then the workspace switches to the Editor panel with the SkillImprovePanel open and pre-populated with the failing assertion context (eval_id and failure details)
- [ ] **AC-US7-02**: Given an AI improvement has been generated, when clicking "Apply & Rerun", then the improved SKILL.md content is saved to disk and the failing test case immediately re-runs via SSE
- [ ] **AC-US7-03**: Given multiple iterations have occurred, when viewing the Run panel or WorkspaceHeader, then an iteration counter shows progress (e.g., "Iteration 3: 4/5 passing")
- [ ] **AC-US7-04**: Given all assertions pass for all test cases, when viewing the workspace, then a celebration state renders with a "Run Final A/B Comparison" call-to-action button

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
