# Architecture Plan: Skill Studio Bulk Delete Cases

## Scope

Pure frontend change in a single file: `repositories/anton-abyzov/vskill-platform/src/app/admin/evals/page.tsx`. No API changes, no new files, no database changes.

## Component Design

### Existing Architecture (unchanged)

```
AdminEvalsPage (Suspense wrapper)
  └── AdminEvalsInner
        ├── State: evalsData, editedData, editMode, showDiff, ...
        ├── Toolbar (skill name, count, edit/save/cancel buttons)
        ├── Eval case cards (map over evals array)
        │     └── Card header, prompt, expected output, assertions
        └── Diff preview modal (modalOverlayStyle reuse)
```

### Additions

```
AdminEvalsInner
  ├── NEW state: showDeleteAllConfirm (boolean)
  ├── Toolbar
  │     └── NEW: "Delete All" button (visible only in editMode, between Save & Cancel)
  ├── Eval case cards
  │     └── Card header
  │           └── NEW: per-case delete "x" button (visible only in editMode)
  ├── NEW: Empty state message ("No eval cases") when evals array is empty
  └── NEW: Delete All confirmation modal (reuses modalOverlayStyle, modalStyle, etc.)
```

## State Changes

| State Variable | Type | Purpose |
|---|---|---|
| `showDeleteAllConfirm` | `boolean` | Controls visibility of the Delete All confirmation modal |

No other new state is needed. Per-case delete operates directly on `editedData` (same pattern as `removeAssertion`). The existing `cancelEdit` handler already restores original data by discarding `editedData`.

## Handler Additions

### `deleteAllCases()`
- Sets `editedData.evals` to empty array `[]`
- Closes confirmation modal (`showDeleteAllConfirm = false`)

### `deleteCase(evalIndex: number)`
- Filters `editedData.evals` to remove the case at `evalIndex`
- Same immutable update pattern as existing `removeAssertion`

## UI Changes

### 1. Delete All Button (Toolbar)

Position: After "Save & Commit", before "Cancel" in the edit mode toolbar. Style: Reuse `removeAssertionBtnStyle` pattern (transparent bg, red border/text) but sized to match toolbar buttons (`cancelBtnStyle` padding). This creates a `deleteAllBtnStyle` constant.

### 2. Delete All Confirmation Modal

Reuses existing modal infrastructure: `modalOverlayStyle`, `modalStyle`, `modalTitleStyle`, `modalActionsStyle`. Content: warning text showing case count ("This will delete N eval cases. This action cannot be undone."). Actions: "Delete All" (red/destructive button) and "Cancel" (existing `cancelBtnStyle`).

### 3. Per-Case Delete Button (Card Header)

Position: Right side of card header (after name input/span). Style: Reuse `removeAssertionBtnStyle` exactly -- same small red "x" pattern already used for assertion removal. Only rendered when `editMode === true`.

### 4. Empty State

When `(editMode ? editedData?.evals : evalsData.evals)` is empty, render "No eval cases" message in place of the card list. Styled with `loadingStyle`-like muted text. Toolbar remains visible above so commit/cancel are still accessible.

## Style Additions

| Constant | Description |
|---|---|
| `deleteAllBtnStyle` | Red destructive toolbar button (transparent bg, red border, red text, toolbar-sized padding) |
| `deleteConfirmBtnStyle` | Red confirmation button for modal (solid red bg, white text) |
| `emptyStateStyle` | Centered muted text for "No eval cases" message |

All other styles are reused from existing constants (`modalOverlayStyle`, `modalStyle`, `modalTitleStyle`, `modalActionsStyle`, `cancelBtnStyle`, `removeAssertionBtnStyle`).

## Data Flow

```
User clicks "Delete All" → showDeleteAllConfirm = true → modal appears
  ├── "Confirm" → editedData.evals = [] → showDeleteAllConfirm = false → empty state shows
  └── "Cancel" → showDeleteAllConfirm = false → no data change

User clicks per-case "x" → editedData.evals filtered → card removed from list
  └── If last case removed → empty state shows

User clicks toolbar "Cancel" → editedData = null, editMode = false → original data restored
User clicks "Save & Commit" → existing commit flow handles any valid evals array (including empty)
```

## Constraints

- No ID renumbering after deletion (spec explicitly out of scope)
- Per-case delete has no confirmation dialog (spec: "immediately removes")
- Delete All requires confirmation (spec: "opens a confirmation modal")
- All deletions are client-side state only until committed via existing API
- Cancel reverts all changes including deletions (existing behavior of `cancelEdit`)

## Risk Assessment

Low risk. All changes are additive to existing patterns:
- State management follows established immutable update pattern
- Modal reuses existing overlay/modal styles
- Delete button reuses existing remove button pattern
- No API surface changes -- existing commit endpoint accepts any valid evals.json
- Cancel/revert already works by discarding editedData

## Domain Delegation

No domain skill delegation needed. This is a contained UI change in a single file using existing React inline style patterns. No component library, no routing changes, no state management library, no design system involvement.
