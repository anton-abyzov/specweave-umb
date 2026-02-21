---
id: US-003
feature: FS-276
title: Interactive Scope Selection
status: complete
priority: P1
created: 2026-02-21
project: vskill
external:
  github:
    issue: 1204
    url: https://github.com/anton-abyzov/specweave/issues/1204
---
# US-003: Interactive Scope Selection

**Feature**: [FS-276](./FEATURE.md)

developer choosing between project-level and global skill installation
**I want** a prompt asking whether to install to the current project or globally
**So that** I can make an informed decision about where skills live

---

## Acceptance Criteria

- [x] **AC-US3-01**: After agent selection, the CLI prompts "Install scope: (1) Project [recommended] or (2) Global?"
- [x] **AC-US3-02**: Project scope installs to `<project-root>/<agent.localSkillsDir>/`
- [x] **AC-US3-03**: Global scope installs to `<agent.globalSkillsDir>/`
- [x] **AC-US3-04**: When `--global` flag is provided, scope selection is skipped (global)
- [x] **AC-US3-05**: When `--yes` flag is provided, defaults to project scope (no prompt)

---

## Implementation

**Increment**: [0276-interactive-skill-installer](../../../../../increments/0276-interactive-skill-installer/spec.md)

