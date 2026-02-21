---
id: US-003
feature: FS-286
title: "Reduce Prompts with Smart Defaults (P1)"
status: completed
priority: P1
created: 2026-02-21T00:00:00.000Z
tldr: "**As a** CLI user installing skills
**I want** fewer prompts during the wizard
**So that** the install flow is faster and less tedious."
project: vskill
---

# US-003: Reduce Prompts with Smart Defaults (P1)

**Feature**: [FS-286](./FEATURE.md)

**As a** CLI user installing skills
**I want** fewer prompts during the wizard
**So that** the install flow is faster and less tedious

---

## Acceptance Criteria

- [x] **AC-US3-01**: Scope defaults to "Project" and method defaults to "Symlink" without prompting -- wizard skips steps 3 and 4
- [x] **AC-US3-02**: Only skills and agents are prompted (when applicable); scope and method use defaults
- [x] **AC-US3-03**: Summary shows defaults for scope and method before confirmation
- [x] **AC-US3-04**: New `--copy` flag forces copy method without prompt
- [x] **AC-US3-05**: Existing `--global` flag still forces global scope without prompt

---

## Implementation

**Increment**: [0286-vskill-install-ux](../../../../../increments/0286-vskill-install-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
