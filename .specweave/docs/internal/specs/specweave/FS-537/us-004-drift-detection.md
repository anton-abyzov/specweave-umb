---
id: US-004
feature: FS-537
title: Drift Detection
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user."
project: specweave
external_tools:
  jira:
    key: SWE2E-273
  ado:
    id: 210
---

# US-004: Drift Detection

**Feature**: [FS-537](./FEATURE.md)

**As a** SpecWeave user
**I want** existing project-local skills to be checked for staleness during living docs sync
**So that** I am warned when skills reference modules or APIs that no longer exist

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given `.claude/skills/*.md` files exist and living docs sync runs via `living-docs-sync.ts`, when the drift detector compares skill content against current analysis output, then it identifies references to modules, files, or API surfaces that no longer appear in the analysis
- [x] **AC-US4-02**: Given drift is detected in one or more skills, when the check completes, then a console warning is printed listing each stale skill and what references are outdated
- [x] **AC-US4-03**: Given drift detection encounters an error, when the error occurs, then it logs the error and does not block living docs sync completion
- [x] **AC-US4-04**: Given no `.claude/skills/*.md` files exist, when living docs sync runs, then drift detection is skipped silently

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
