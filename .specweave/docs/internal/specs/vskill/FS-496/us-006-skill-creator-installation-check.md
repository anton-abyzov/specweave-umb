---
id: US-006
feature: FS-496
title: "Skill-Creator Installation Check"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
---

# US-006: Skill-Creator Installation Check

**Feature**: [FS-496](./FEATURE.md)

**As a** skill author
**I want** a status indicator in the left sidebar showing whether the Skill-Creator tool is installed
**So that** I know if I can use AI skill creation features and how to install the tool if missing

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given the LeftPanel sidebar, when it renders, then it calls api.getSkillCreatorStatus() and displays a status indicator below the "New Skill" button area
- [x] **AC-US6-02**: Given the Skill-Creator is installed (status.installed === true), when the indicator renders, then a green dot with "Skill Creator installed" text is shown
- [x] **AC-US6-03**: Given the Skill-Creator is NOT installed (status.installed === false), when the indicator renders, then a yellow/amber warning dot with "Skill Creator not installed" text is shown, along with the install command displayed in a copyable code block
- [x] **AC-US6-04**: Given the install command is displayed, when the user clicks the code block or a copy button, then the command text is copied to the clipboard
- [x] **AC-US6-05**: Given the status check fails (network error), when the indicator renders, then the indicator is hidden (graceful degradation, no error shown)

---

## Implementation

**Increment**: [0496-skill-studio-ui-polish](../../../../../increments/0496-skill-studio-ui-polish/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Fetch and display Skill-Creator installation status in LeftPanel sidebar
- [x] **T-009**: Copy install command to clipboard on code block click
