---
id: US-002
feature: FS-537
title: Suggestion Engine
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user."
project: specweave
external_tools:
  jira:
    key: SWE2E-271
  ado:
    id: 208
---

# US-002: Suggestion Engine

**Feature**: [FS-537](./FEATURE.md)

**As a** SpecWeave user
**I want** to see a brief suggestion when a pattern has been observed across 3+ increments
**So that** I know when a recurring convention is ready to be codified as a skill

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given `skillGen.suggest` is `true` in config and a signal has `incrementIds.length >= skillGen.minSignalCount` and `declined` is false and `generated` is false, when increment closure completes signal collection, then exactly one suggestion is printed to console
- [x] **AC-US2-02**: Given a qualifying suggestion exists, when it is printed, then the format is a single console log line containing the pattern name, increment count, and the command `/sw:skill-gen`
- [x] **AC-US2-03**: Given `skillGen.suggest` is `false` in config, when increment closure completes, then no suggestion is printed
- [x] **AC-US2-04**: Given multiple patterns qualify, when the suggestion engine runs, then only the pattern with the highest confidence score is suggested (max 1 per closure)
- [x] **AC-US2-05**: Given a suggestion is printed, when the signal is updated, then `suggested` is set to `true` on that signal entry

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
