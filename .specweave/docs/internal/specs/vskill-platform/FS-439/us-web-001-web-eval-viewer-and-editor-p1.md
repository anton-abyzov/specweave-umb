---
id: US-WEB-001
feature: FS-439
title: "Web Eval Viewer and Editor (P1)"
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As an** admin."
project: vskill-platform
related_projects: [vskill, specweave]
external:
  github:
    issue: 15
    url: "https://github.com/anton-abyzov/vskill-platform/issues/15"
---

# US-WEB-001: Web Eval Viewer and Editor (P1)

**Feature**: [FS-439](./FEATURE.md)

**As an** admin
**I want** a web page at `/admin/evals` that shows evals for one skill at a time with an edit mode and explicit Save button
**So that** I can review and refine eval definitions through a visual interface without touching the filesystem

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
- [x] **T-011**: Implement admin evals viewer page (read-only states)
- [x] **T-012**: Implement edit mode and Save & Commit flow
