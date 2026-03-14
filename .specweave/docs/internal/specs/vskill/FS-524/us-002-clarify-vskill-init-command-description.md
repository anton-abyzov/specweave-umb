---
id: US-002
feature: FS-524
title: "Clarify vskill init command description"
status: completed
priority: P2
created: 2026-03-14
tldr: "**As a** CLI user."
project: vskill
related_projects: [specweave, vskill-platform]
---

# US-002: Clarify vskill init command description

**Feature**: [FS-524](./FEATURE.md)

**As a** CLI user
**I want** the `vskill init` help text to clearly state what the command does and that the lockfile update is optional
**So that** the ambiguous "(optional)" phrasing is removed

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given I run `vskill init --help`, when I read the command description, then it reads "Detect installed AI agents and optionally update the lockfile" instead of the current "Show detected AI agents and update lockfile (optional)"

---

## Implementation

**Increment**: [0524-cross-project-help-text-fixes](../../../../../increments/0524-cross-project-help-text-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
