---
id: US-003
feature: FS-486
title: Selective Apply of Eval Changes
status: not_started
priority: P1
created: 2026-03-11
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 74
    url: https://github.com/anton-abyzov/vskill/issues/74
---

# US-003: Selective Apply of Eval Changes

**Feature**: [FS-486](./FEATURE.md)

**As a** skill author
**I want** to choose which eval changes to apply when I click Apply
**So that** I maintain control over my test suite

---

## Acceptance Criteria

- [ ] **AC-US3-01**: When the user clicks Apply, the system saves the improved SKILL.md content AND computes merged evals from the selected eval changes (adds inserted, modifies replaced, removes deleted)
- [ ] **AC-US3-02**: Unchecked eval changes are ignored during apply; only checked changes are merged into the evals file
- [ ] **AC-US3-03**: The merged evals are saved via the existing PUT /evals endpoint
- [ ] **AC-US3-04**: If SKILL.md save succeeds but evals save fails, the SKILL.md change is kept and an error message is shown; the user can retry the evals save
- [ ] **AC-US3-05**: If no eval change checkboxes are checked, only the SKILL.md content is saved (existing behavior preserved)

---

## Implementation

**Increment**: [0486-smart-ai-edit](../../../../../increments/0486-smart-ai-edit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-006**: Implement mergeEvalChanges Utility
- [ ] **T-007**: Extend applyAiEdit -- Merge and Save Evals with Error/Retry
