---
id: US-003
feature: FS-295
title: "Verify Living-Docs Sync Post-Reorganization (P1)"
status: not_started
priority: P1
created: 2026-02-21
tldr: "**As a** developer who just reorganized specs
**I want** `specweave sync-progress` to work correctly with the new per-project folder structure
**So that** future increments sync living docs to the right project folder."
project: specweave
---

# US-003: Verify Living-Docs Sync Post-Reorganization (P1)

**Feature**: [FS-295](./FEATURE.md)

**As a** developer who just reorganized specs
**I want** `specweave sync-progress` to work correctly with the new per-project folder structure
**So that** future increments sync living docs to the right project folder

---

## Acceptance Criteria

- [ ] **AC-US3-01**: After reorganization, `specweave sync-progress` finds and updates specs in per-project folders
- [ ] **AC-US3-02**: New increments created after reorganization have their living docs placed in the correct project folder based on `**Project**:` field
- [ ] **AC-US3-03**: The `specweave living-docs` builder recognizes the multi-project folder structure

---

## Implementation

**Increment**: [0295-multi-repo-docs-restructuring](../../../../../increments/0295-multi-repo-docs-restructuring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
