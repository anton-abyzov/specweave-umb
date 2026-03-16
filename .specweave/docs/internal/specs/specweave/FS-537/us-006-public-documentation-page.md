---
id: US-006
feature: FS-537
title: Public Documentation Page
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** potential SpecWeave user."
project: specweave
external_tools:
  jira:
    key: SWE2E-275
  ado:
    id: 345
---

# US-006: Public Documentation Page

**Feature**: [FS-537](./FEATURE.md)

**As a** potential SpecWeave user
**I want** a docs page explaining the skill generation feature
**So that** I can understand how to use pattern detection and skill codification

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given the file `docs-site/docs/skills/extensible/skill-generation.md` is created, when the Docusaurus site builds, then the page renders without errors at the expected URL path
- [x] **AC-US6-02**: Given the docs page exists, when `docs-site/sidebars.ts` is checked, then the page is registered in the Skills section sidebar
- [x] **AC-US6-03**: Given the docs page content, when reviewed, then it covers: signal detection lifecycle, configuration options, `/sw:skill-gen` usage, drift detection, and the signal schema
- [x] **AC-US6-04**: Given the project README, when the Skills section is checked, then skill-gen is mentioned with a link to the docs page

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
