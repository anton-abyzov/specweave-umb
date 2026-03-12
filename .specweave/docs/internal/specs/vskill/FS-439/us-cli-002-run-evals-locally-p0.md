---
id: US-CLI-002
feature: FS-439
title: "Run Evals Locally (P0)"
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As a** skill author."
project: vskill
related_projects: [vskill-platform, specweave]
external:
  github:
    issue: 9
    url: "https://github.com/anton-abyzov/vskill/issues/9"
---

# US-CLI-002: Run Evals Locally (P0)

**Feature**: [FS-439](./FEATURE.md)

**As a** skill author
**I want** to run `vskill eval run <plugin>/<skill>` to grade each eval case's assertions against LLM output
**So that** I can measure whether my skill works correctly and identify failing assertions

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0439-skill-eval-infrastructure](../../../../../increments/0439-skill-eval-infrastructure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Implement assertion judge and benchmark writer
- [x] **T-006**: Implement eval run command
