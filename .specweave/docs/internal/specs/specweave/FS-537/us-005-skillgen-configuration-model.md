---
id: US-005
feature: FS-537
title: SkillGen Configuration Model
status: not_started
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
project: specweave
external_tools:
  jira:
    key: SWE2E-274
  ado:
    id: 211
---

# US-005: SkillGen Configuration Model

**Feature**: [FS-537](./FEATURE.md)

**As a** SpecWeave user
**I want** skill generation behavior to be configurable via `config.json`
**So that** I can control detection, suggestion frequency, and declined patterns

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given a fresh project, when `skillGen` is absent from `config.json`, then defaults are applied: `detection: "on-close"`, `suggest: true`, `minSignalCount: 3`, `declinedSuggestions: []`
- [ ] **AC-US5-02**: Given `skillGen.minSignalCount` is set to 5, when signal collection runs, then only patterns observed in 5+ increments qualify for suggestion and display in `/sw:skill-gen`
- [ ] **AC-US5-03**: Given a pattern ID is in `skillGen.declinedSuggestions`, when the suggestion engine evaluates that pattern, then it is permanently excluded from console suggestions but still visible in `/sw:skill-gen`
- [ ] **AC-US5-04**: Given the `SkillGenConfig` type is added to `src/core/config/types.ts`, when TypeScript compilation runs, then there are zero type errors

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
