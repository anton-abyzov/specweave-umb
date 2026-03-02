---
id: US-002
feature: FS-295
title: "Enable multiProject Mode (P0)"
status: not_started
priority: P1
created: 2026-02-21
tldr: "**As a** developer running `--reorganize-specs`
**I want** `multiProject."
project: specweave
---

# US-002: Enable multiProject Mode (P0)

**Feature**: [FS-295](./FEATURE.md)

**As a** developer running `--reorganize-specs`
**I want** `multiProject.enabled` to be set to `true` in config.json automatically
**So that** living-docs sync and other SpecWeave features use per-project paths

---

## Acceptance Criteria

- [ ] **AC-US2-01**: `--reorganize-specs --execute` sets `multiProject.enabled = true` in `.specweave/config.json`
- [ ] **AC-US2-02**: If `multiProject.enabled` is already `true`, the config is not rewritten
- [ ] **AC-US2-03**: The dry-run output includes a line showing the config change that will be applied

---

## Implementation

**Increment**: [0295-multi-repo-docs-restructuring](../../../../../increments/0295-multi-repo-docs-restructuring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
