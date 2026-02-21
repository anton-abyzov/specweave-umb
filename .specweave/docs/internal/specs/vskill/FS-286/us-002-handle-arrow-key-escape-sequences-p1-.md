---
id: US-002
feature: FS-286
title: "Handle Arrow Key Escape Sequences (P1)"
status: completed
priority: P1
created: 2026-02-21T00:00:00.000Z
tldr: "**As a** CLI user
**I want** arrow key presses to be silently ignored
**So that** pressing up/down/left/right does not produce garbage output or break the prompt."
project: vskill
---

# US-002: Handle Arrow Key Escape Sequences (P1)

**Feature**: [FS-286](./FEATURE.md)

**As a** CLI user
**I want** arrow key presses to be silently ignored
**So that** pressing up/down/left/right does not produce garbage output or break the prompt

---

## Acceptance Criteria

- [x] **AC-US2-01**: ANSI escape sequences (ESC [ A/B/C/D for arrow keys) are detected and ignored in `promptCheckboxList`
- [x] **AC-US2-02**: ANSI escape sequences are detected and ignored in `promptChoice`
- [x] **AC-US2-03**: Other common escape sequences (home, end, delete) do not produce errors

---

## Implementation

**Increment**: [0286-vskill-install-ux](../../../../../increments/0286-vskill-install-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
