---
id: US-SW-001
feature: FS-457
title: "Default to Suggest-Only Mode"
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** SpecWeave user."
project: specweave
related_projects: [vskill]
external:
  github:
    issue: 1521
    url: "https://github.com/anton-abyzov/specweave/issues/1521"
---

# US-SW-001: Default to Suggest-Only Mode

**Feature**: [FS-457](./FEATURE.md)

**As a** SpecWeave user
**I want** plugin auto-loading to suggest plugins instead of installing them silently
**So that** I maintain control over what gets installed in my project

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Flip suggestOnly default in llm-plugin-detector.ts
- [ ] **T-002**: Flip suggestOnly default in user-prompt-submit.sh
