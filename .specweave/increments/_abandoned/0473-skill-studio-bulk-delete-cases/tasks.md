---
increment: 0473-skill-studio-bulk-delete-cases
title: "Skill Studio: Bulk Delete All Test Cases"
total_tasks: 2
completed_tasks: 2
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
---

# Tasks: Skill Studio Bulk Delete Cases

## User Story: US-001 - Bulk Delete All Test Cases

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Tasks**: 1 total, 1 completed

### T-001: Add Delete All button, confirmation modal, and empty state

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [x] completed

**Test Plan**:
- **Given** an admin is in edit mode with N eval cases loaded
- **When** they click "Delete All" and confirm the dialog
- **Then** all eval cases are removed, the empty state message appears, and they can still Save & Commit
- **And Given** they dismiss the dialog instead
- **Then** all cases remain intact

**Test Cases**:
1. **Unit**: `src/app/admin/evals/__tests__/page.test.tsx`
   - deleteAllButton_visibleInEditMode(): Delete All button renders only when editMode=true
   - deleteAllButton_hiddenOutsideEditMode(): Delete All button absent when editMode=false
   - deleteAllModal_opensOnClick(): Clicking Delete All sets showDeleteAllConfirm=true, modal appears
   - deleteAllModal_confirmsDeletesAllCases(): Confirming modal sets editedData.evals to []
   - deleteAllModal_cancelLeavesDataIntact(): Canceling modal leaves evals untouched
   - emptyState_showsAfterDeleteAll(): "No eval cases" message renders when evals array is empty
   - saveAfterDeleteAll_callsCommitWithEmptyArray(): Save & Commit works after evals cleared
   - **Coverage Target**: 90%

**Implementation**:
1. Add `showDeleteAllConfirm` boolean state to `AdminEvalsInner`
2. Add `deleteAllCases()` handler: sets `editedData.evals = []`, closes modal
3. Add `deleteAllBtnStyle` and `deleteConfirmBtnStyle` style constants
4. Add `emptyStateStyle` style constant
5. Render "Delete All" button in toolbar (edit mode only, between Save & Cancel)
6. Render confirmation modal using existing `modalOverlayStyle`, `modalStyle`, `modalTitleStyle`, `modalActionsStyle`; display case count in warning text
7. Replace card list render with conditional: if evals empty show "No eval cases" using `emptyStateStyle`, else show cards as before

---

## User Story: US-002 - Delete Individual Test Case

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Tasks**: 1 total, 1 completed

### T-002: Add per-case delete button to each eval card

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Status**: [x] completed

**Test Plan**:
- **Given** an admin is in edit mode with multiple eval cases
- **When** they click the delete button on a specific case card
- **Then** that case is removed immediately (no confirmation), remaining case IDs are unchanged, and other cases remain
- **And Given** the last case is deleted this way
- **Then** the empty state message appears
- **And Given** the admin clicks toolbar Cancel after deletions
- **Then** all deletions are reverted and original data is restored

**Test Cases**:
1. **Unit**: `src/app/admin/evals/__tests__/page.test.tsx`
   - perCaseDeleteBtn_visibleInEditMode(): Delete button renders on each card in editMode
   - perCaseDeleteBtn_hiddenOutsideEditMode(): Delete button absent when editMode=false
   - perCaseDelete_removesTargetCase(): Clicking delete on case index N removes only that case
   - perCaseDelete_preservesCaseIds(): Remaining cases retain original IDs (no renumbering)
   - perCaseDelete_lastCase_showsEmptyState(): Deleting last case triggers empty state
   - cancelAfterPerCaseDelete_revertsAllDeletions(): Toolbar Cancel restores original evals data
   - **Coverage Target**: 90%

**Implementation**:
1. Add `deleteCase(evalIndex: number)` handler: filters `editedData.evals` removing item at index
2. In the eval case card header, add a delete "x" button (using `removeAssertionBtnStyle`) only when `editMode === true`
3. Wire button `onClick` to `deleteCase(index)`
4. Verify empty state message from T-001 also covers the last-case deletion scenario (no additional code needed)
5. Verify existing `cancelEdit` handler already restores `editedData` (no changes needed)
