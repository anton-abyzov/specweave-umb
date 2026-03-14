---
id: US-001
feature: FS-524
title: "Clarify specweave validate-jira help description"
status: completed
priority: P2
created: 2026-03-14
tldr: "**As a** CLI user."
project: specweave
related_projects: [vskill, vskill-platform]
---

# US-001: Clarify specweave validate-jira help description

**Feature**: [FS-524](./FEATURE.md)

**As a** CLI user
**I want** the `validate-jira` command help text to specify what resources it validates and creates
**So that** I understand what the command does before running it

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given I run `specweave validate-jira --help`, when I read the command description, then it reads "Validate Jira connection, project, and issue-type configuration; create missing issue types if needed" instead of the current generic "Validate Jira configuration and create missing resources"

---

## Implementation

**Increment**: [0524-cross-project-help-text-fixes](../../../../../increments/0524-cross-project-help-text-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
