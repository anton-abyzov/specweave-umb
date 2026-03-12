---
id: US-002
feature: FS-479
title: "Skill Studio Documentation (P1)"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** skill author."
project: specweave
---

# US-002: Skill Studio Documentation (P1)

**Feature**: [FS-479](./FEATURE.md)

**As a** skill author
**I want** documentation for the Skill Studio IDE
**So that** I can use it to develop, test, and improve my skills locally

---

## Acceptance Criteria

- [x] **AC-US2-01**: Page exists at `docs/skills/skill-studio.md` with frontmatter
- [x] **AC-US2-02**: Documents quick start: `npx vskill studio` launches the local Vite React UI
- [x] **AC-US2-03**: Documents all 6 workspace panels: Editor, Tests, Run, Activation, History, Dependencies
- [x] **AC-US2-04**: Documents A/B benchmarking and model comparison features
- [x] **AC-US2-05**: Documents the skill improvement workflow (iterate, test, compare)
- [x] **AC-US2-06**: Documents creating skills inline within the Studio
- [x] **AC-US2-07**: Includes keyboard shortcuts reference
- [x] **AC-US2-08**: Lists relevant CLI commands (`vskill studio`, `vskill eval`)
- [x] **AC-US2-09**: Docusaurus build passes with the new page included

---

## Implementation

**Increment**: [0479-docs-skills-studio-install](../../../../../increments/0479-docs-skills-studio-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: [P] Read vskill Studio source and create skill-studio.md
