---
id: US-002
feature: FS-538
title: Add Mobile Keywords to Auto-Install Component Mapping (P1)
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user describing a mobile project in a prompt."
project: specweave
external_tools:
  ado:
    id: 208
  jira:
    key: SWE2E-279
---

# US-002: Add Mobile Keywords to Auto-Install Component Mapping (P1)

**Feature**: [FS-538](./FEATURE.md)

**As a** SpecWeave user describing a mobile project in a prompt
**I want** relevant keywords to be recognized by auto-install
**So that** React Native and Expo prompts install the frontend skill, and pure platform keywords are registered without installing phantom plugins

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a prompt containing "react native", when COMPONENT_MAPPING is checked, then it maps to `{ skills: ['frontend'], agents: [] }`
- [x] **AC-US2-02**: Given a prompt containing "expo", when COMPONENT_MAPPING is checked, then it maps to `{ skills: ['frontend'], agents: [] }`
- [x] **AC-US2-03**: Given a prompt containing any of "ios", "android", "mobile", "app store", "play store", when COMPONENT_MAPPING is checked, then it maps to `{ skills: [], agents: [] }`
- [x] **AC-US2-04**: Given a prompt containing "react native" and "ios", when auto-install runs, then it installs the frontend skill exactly once (no duplicates, no phantom plugins)

---

## Implementation

**Increment**: [0538-mobile-detect-test-fix](../../../../../increments/0538-mobile-detect-test-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
