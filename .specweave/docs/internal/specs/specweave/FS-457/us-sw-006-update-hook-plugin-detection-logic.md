---
id: US-SW-006
feature: FS-457
title: "Update Hook Plugin Detection Logic"
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** SpecWeave developer."
project: specweave
related_projects: [vskill]
external:
  github:
    issue: 1525
    url: "https://github.com/anton-abyzov/specweave/issues/1525"
---

# US-SW-006: Update Hook Plugin Detection Logic

**Feature**: [FS-457](./FEATURE.md)

**As a** SpecWeave developer
**I want** the `user-prompt-submit.sh` hook and `llm-plugin-detector.ts` to use suggest-only as the default path
**So that** the detection-to-installation flow respects consent by default

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-011**: Verify hook uses suggest-only path as the default code branch
- [ ] **T-012**: Verify VSKILL_REPO_PLUGINS in hook matches actual plugin directories
