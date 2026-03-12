---
id: US-004
feature: FS-498
title: "Read-Only Mode for Installed Skills"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 94
    url: https://github.com/anton-abyzov/vskill/issues/94
---

# US-004: Read-Only Mode for Installed Skills

**Feature**: [FS-498](./FEATURE.md)

**As a** skill developer
**I want** installed skills to open in a read-only view when selected
**So that** I do not accidentally modify or benchmark consumed copies

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given an installed skill is selected, when the detail panel renders, then the SKILL.md content is shown in read-only mode
- [x] **AC-US4-02**: Given an installed skill is selected, when the detail panel renders, then benchmark run buttons are disabled or hidden
- [x] **AC-US4-03**: Given an installed skill is selected, when the detail panel renders, then eval editing controls are disabled or hidden
- [x] **AC-US4-04**: Given a source skill is selected, when the detail panel renders, then all editing and benchmarking controls remain fully functional

---

## Implementation

**Increment**: [0498-studio-skill-origin-classification](../../../../../increments/0498-studio-skill-origin-classification/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Thread `origin` into `WorkspaceProvider` and expose `isReadOnly`
- [x] **T-007**: Disable run buttons in `RunPanel` for installed skills
- [x] **T-008**: Disable editing controls in `EditorPanel` for installed skills
- [x] **T-009**: Disable eval controls in `TestsPanel` and add "Read-only" badge to `DetailHeader`
