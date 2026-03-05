---
id: US-WEB-002
feature: FS-439
title: "GitHub Commit from Web Editor (P1)"
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As an** admin."
project: vskill-platform
related_projects: [vskill, specweave]
external:
  github:
    issue: 16
    url: https://github.com/anton-abyzov/vskill-platform/issues/16
---

# US-WEB-002: GitHub Commit from Web Editor (P1)

**Feature**: [FS-439](./FEATURE.md)

**As an** admin
**I want** to commit edited evals.json directly to the main branch from the web editor with a diff preview
**So that** I can update eval definitions in the source repository without leaving the browser

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0439-skill-eval-infrastructure](../../../../../increments/0439-skill-eval-infrastructure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Implement GitHub eval content client
- [x] **T-010**: Implement platform API routes for eval editor
- [x] **T-012**: Implement edit mode and Save & Commit flow
