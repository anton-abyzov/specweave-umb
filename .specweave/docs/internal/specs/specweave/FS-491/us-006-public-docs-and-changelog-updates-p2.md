---
id: US-006
feature: FS-491
title: "Public Docs and Changelog Updates (P2)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** SpecWeave user or evaluator reading public documentation."
project: specweave
external:
  github:
    issue: 1543
    url: "https://github.com/anton-abyzov/specweave/issues/1543"
---

# US-006: Public Docs and Changelog Updates (P2)

**Feature**: [FS-491](./FEATURE.md)

**As a** SpecWeave user or evaluator reading public documentation
**I want** the skills reference, tutorial script, and changelog updated to reflect all new quality-left capabilities
**So that** new features are discoverable and documented

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given docs-site/docs/reference/skills.md is updated, when a user reads the Quality & Testing section, then sw:debug appears with description and usage guidance
- [x] **AC-US6-02**: Given docs-site/docs/guides/youtube-tutorial-script.md is updated, when a user reads it, then a section on quality-left features (per-task gates, adversarial grill, debug skill) is present
- [x] **AC-US6-03**: Given CHANGELOG.md is updated, when a user reads it, then all 5 features from this increment are documented with version reference

---

## Implementation

**Increment**: [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Update skills.md Reference, Tutorial Script, and CHANGELOG
