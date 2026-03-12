---
id: US-003
feature: FS-492
title: "Improved guard-clause error messages and relaxed post-scaffold guard (P2) — DESCOPED"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**Status**: Descoped — added by PM agent beyond the approved plan."
project: specweave
external:
  github:
    issue: 1546
    url: https://github.com/anton-abyzov/specweave/issues/1546
---

# US-003: Improved guard-clause error messages and relaxed post-scaffold guard (P2) — DESCOPED

**Feature**: [FS-492](./FEATURE.md)

**Status**: Descoped — added by PM agent beyond the approved plan. Guard clause messages already show umbrella root and suspicious segment. Post-scaffold guard `!hasGit && !hasRepos` matches the approved plan's "skip if .git or repositories/ exists". Can be addressed in a follow-up increment if needed.

---

## Acceptance Criteria

- [x] **AC-US3-04**: If the user selects "I have existing code here" or "Starting from scratch" in the project setup prompt, no repos are cloned (no regression) — implemented via `promptProjectSetup` defaulting to "existing"

---

## Implementation

**Increment**: [0492-init-project-resolution-redesign](../../../../../increments/0492-init-project-resolution-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
