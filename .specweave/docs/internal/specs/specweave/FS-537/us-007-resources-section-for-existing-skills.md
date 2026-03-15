---
id: US-007
feature: FS-537
title: Resources Section for Existing Skills
status: not_started
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave skill user."
project: specweave
external_tools:
  jira:
    key: SWE2E-276
  ado:
    id: 346
---

# US-007: Resources Section for Existing Skills

**Feature**: [FS-537](./FEATURE.md)

**As a** SpecWeave skill user
**I want** each SKILL.md to link to its public documentation
**So that** I can quickly find detailed docs for any skill I am using

---

## Acceptance Criteria

- [ ] **AC-US7-01**: Given all 26 SKILL.md files in `plugins/specweave/skills/`, when a `## Resources` section is appended to each, then each section contains a link to the corresponding page on verified-skill.com
- [ ] **AC-US7-02**: Given a SKILL.md already has a `## Resources` section, when the update runs, then existing content is preserved and not duplicated
- [ ] **AC-US7-03**: Given the new skill-gen SKILL.md (from US-003), when it is generated, then its `## Resources` section links to the new docs page created in US-006

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
