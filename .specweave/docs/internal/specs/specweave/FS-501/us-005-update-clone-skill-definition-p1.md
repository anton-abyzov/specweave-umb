---
id: US-005
feature: FS-501
title: Update Clone Skill Definition (P1)
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1551
    url: https://github.com/anton-abyzov/specweave/issues/1551
---

# US-005: Update Clone Skill Definition (P1)

**Feature**: [FS-501](./FEATURE.md)

**As a** developer
**I want** the clone.md skill definition to document the `--repo` flag
**So that** the LLM knows about the new capability and can use it correctly

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given the updated clone.md, when a user invokes `/sw-github:clone --repo owner/repo`, then the skill definition includes syntax examples and behavior description for the `--repo` flag
- [ ] **AC-US5-02**: Given the updated clone.md, when it documents `--repo`, then it lists all supported input formats (owner/repo, github.com/owner/repo, https://..., git@...)

---

## Implementation

**Increment**: [0501-single-repo-clone](../../../../../increments/0501-single-repo-clone/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-007**: Document --repo flag in plugins/specweave-github/commands/clone.md
