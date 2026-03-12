---
id: US-002
feature: FS-515
title: "Update drifted plugin metadata (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill plugin author."
project: vskill
---

# US-002: Update drifted plugin metadata (P1)

**Feature**: [FS-515](./FEATURE.md)

**As a** vskill plugin author
**I want** marketplace sync to update existing entries when version or description has changed in plugin.json
**So that** marketplace.json stays accurate without manual edits

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given plugin `mobile` exists in marketplace.json with version `2.3.0` and its `.claude-plugin/plugin.json` now has version `2.4.0`, when the user runs `vskill marketplace sync`, then the marketplace.json entry for `mobile` is updated to version `2.4.0`
- [x] **AC-US2-02**: Given plugin `skills` exists in marketplace.json with description `"old desc"` and its `.claude-plugin/plugin.json` now has description `"new desc"`, when the user runs `vskill marketplace sync`, then the marketplace.json entry for `skills` is updated to `"new desc"`
- [x] **AC-US2-03**: Given a plugin exists in marketplace.json and its `.claude-plugin/plugin.json` has identical name, version, and description, when the user runs `vskill marketplace sync`, then the entry is left unchanged and reported as unchanged in the output

---

## Implementation

**Increment**: [0515-vskill-marketplace-sync](../../../../../increments/0515-vskill-marketplace-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: TDD REFACTOR -- full suite, build, smoke test
