---
id: US-004
feature: FS-486
title: "Workspace State for Eval Changes"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** developer."
project: vskill
external:
  github:
    issue: 75
    url: "https://github.com/anton-abyzov/vskill/issues/75"
---

# US-004: Workspace State for Eval Changes

**Feature**: [FS-486](./FEATURE.md)

**As a** developer
**I want** the workspace state to track eval change suggestions and checkbox states
**So that** the UI can render and the apply logic can compute the merge correctly

---

## Acceptance Criteria

- [x] **AC-US4-01**: `WorkspaceState` is extended with `aiEditEvalChanges` (array of eval change objects) and `aiEditEvalSelections` (map of change index to boolean)
- [x] **AC-US4-02**: New reducer actions handle: setting eval changes from the API response, toggling individual change selections, select-all/deselect-all, and clearing on discard
- [x] **AC-US4-03**: The `submitAiEdit` function in WorkspaceContext sends current evals to the API and dispatches eval changes from the response

---

## Implementation

**Increment**: [0486-smart-ai-edit](../../../../../increments/0486-smart-ai-edit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Extend workspaceTypes.ts -- New State Fields and Action Types
- [x] **T-009**: Extend workspaceReducer.ts -- Handle New Actions
- [x] **T-010**: Extend WorkspaceContext -- submitAiEdit Sends Evals and Dispatches Changes
