---
id: US-CLI-004
feature: FS-439
title: "Batch Generate Evals (P1)"
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As a** skill author."
project: vskill
related_projects: [vskill-platform, specweave]
external:
  github:
    issue: 11
    url: https://github.com/anton-abyzov/vskill/issues/11
---

# US-CLI-004: Batch Generate Evals (P1)

**Feature**: [FS-439](./FEATURE.md)

**As a** skill author
**I want** to run `vskill eval generate-all` to scaffold evals.json for every skill that lacks one
**So that** I can bootstrap eval coverage across an entire plugin repository in one command

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0439-skill-eval-infrastructure](../../../../../increments/0439-skill-eval-infrastructure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-004**: Implement skill scanner and eval command router
- [ ] **T-008**: Implement eval generate-all command
