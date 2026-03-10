---
increment: 0473-skill-studio-bulk-delete-cases
title: "Skill Studio: Bulk Delete All Test Cases"
type: feature
priority: P1
status: planned
created: 2026-03-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio: Bulk Delete All Test Cases

## Overview

Add bulk "Delete All" and per-case delete buttons to the admin evals editor (`/admin/evals`) in vskill-platform so admins can delete all test cases at once or remove individual cases while editing.

This is a pure frontend change scoped to a single file (`src/app/admin/evals/page.tsx`). The existing commit API handles persisting changes to GitHub -- no backend modifications required.

## User Stories

### US-001: Bulk Delete All Test Cases (P1)
**Project**: vskill-platform

**As an** admin
**I want** to delete all test cases at once with a confirmation dialog
**So that** I can quickly clear out an entire eval suite when rebuilding tests from scratch

**Acceptance Criteria**:
- [x] **AC-US1-01**: A "Delete All" button appears in the toolbar next to "Save & Commit" and "Cancel" when in edit mode
- [x] **AC-US1-02**: The "Delete All" button is not visible when not in edit mode
- [x] **AC-US1-03**: Clicking "Delete All" opens a confirmation modal (reusing existing modal styles) before removing cases
- [x] **AC-US1-04**: Confirming the modal removes all eval cases from the edited data (sets evals array to empty)
- [x] **AC-US1-05**: Dismissing/canceling the confirmation modal leaves all cases intact
- [x] **AC-US1-06**: After deleting all cases, an empty state message ("No eval cases") is displayed
- [x] **AC-US1-07**: After deleting all cases, the user can still "Save & Commit" to persist the empty evals array to GitHub

---

### US-002: Delete Individual Test Case (P1)
**Project**: vskill-platform

**As an** admin
**I want** to delete individual test cases while editing
**So that** I can remove outdated or incorrect cases without affecting the rest of the suite

**Acceptance Criteria**:
- [x] **AC-US2-01**: Each eval case card shows a delete button when in edit mode
- [x] **AC-US2-02**: The per-case delete button is not visible when not in edit mode
- [x] **AC-US2-03**: Clicking the per-case delete button immediately removes that case from the edited data (no confirmation dialog)
- [x] **AC-US2-04**: Remaining case IDs are not renumbered after deletion (IDs stay as-is)
- [x] **AC-US2-05**: Deleting the last remaining case via per-case delete shows the empty state message
- [x] **AC-US2-06**: Clicking "Cancel" in the toolbar reverts all deletions, restoring the original eval data

## Functional Requirements

### FR-001: Delete All Confirmation Modal
The confirmation modal reuses the existing modal overlay and modal styles (`modalOverlayStyle`, `modalStyle`, `modalTitleStyle`, `modalActionsStyle`). It displays a warning message indicating the number of cases that will be deleted and provides "Confirm" and "Cancel" actions.

### FR-002: Per-Case Delete Button
Each eval case card displays a delete button (styled consistently with the existing assertion remove button pattern) in the card header area. The button is only rendered in edit mode.

### FR-003: Empty State
When the evals array is empty (either after deletion or if loaded empty), a message reading "No eval cases" is displayed in place of the card list. The toolbar remains visible so the user can commit or cancel.

## Success Criteria

- Admins can clear entire eval suites in 2 clicks (Delete All -> Confirm)
- Admins can remove individual cases in 1 click per case
- No regressions to existing edit, assertion, or commit functionality

## Out of Scope

- Backend/API changes (the existing commit endpoint handles any valid evals.json)
- Undo/redo beyond the existing Cancel button behavior
- Multi-select delete (select specific subset of cases)
- Drag-and-drop reordering of cases
- ID renumbering after deletion

## Dependencies

- Existing commit API at `/api/v1/admin/evals/commit` (no changes needed)
- Existing modal component styles in `page.tsx`
