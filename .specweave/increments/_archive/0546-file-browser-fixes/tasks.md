# Tasks: vSkill Studio File Browser Fixes

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

---

## US-001: File Tree Stays Expanded on File Selection

### T-001: Remove setExpanded(false) from file select handler in SkillFileBrowser
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed

**Implementation Details**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/SkillFileBrowser.tsx`
- Line ~238: change `onSelect={(path) => { onSelect(path); setExpanded(false); }}` to `onSelect={(path) => { onSelect(path); }}`
- The `expanded` state controls panel visibility (collapsed strip vs tree), not folder open/close — removing the call keeps the panel visible after file selection

**Test**: Given an expanded folder in the file browser, when the user clicks a file inside it, then the folder remains expanded and the browser panel stays visible (not collapsed)

**Test File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SkillFileBrowser.test.tsx`
- TC-001: Given browser in expanded state with a folder open, when `onSelect` fires for a child file, then the browser's `expanded` state remains `true`
- TC-002: Given multiple nested folders are expanded, when any file at any depth is clicked, then all previously expanded folders remain expanded (TreeItem local state unchanged)

**Dependencies**: None

---

## US-002: Universal File Type Editing

### T-002: Render toolbar for all non-binary file types in SecondaryFileViewer
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] Completed

**Implementation Details**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/SecondaryFileViewer.tsx`
- Remove the `fileType !== "other"` guard that wraps the entire toolbar div
- Wrap the Raw/Split/Preview toggle buttons in `{(fileType === "md" || fileType === "json") && (...)}` so they only appear for md/json
- File size display and Edit/Save/Cancel buttons remain visible for all non-binary types
- The existing binary fallback path (no toolbar) is unchanged

**Test**: Given a `.txt` file is selected in the viewer, when the component renders, then a toolbar appears with Edit, file size, Save, and Cancel buttons but without Raw/Split/Preview toggles

**Test File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SecondaryFileViewer.test.tsx`
- TC-001: Given `fileType === "other"`, when component renders in view mode, then toolbar is visible with Edit button
- TC-002: Given `fileType === "md"`, when component renders, then toolbar shows Raw/Split/Preview toggles (existing behavior preserved)
- TC-003: Given `fileType === "json"`, when component renders, then toolbar shows Raw/Split/Preview toggles (existing behavior preserved)
- TC-004: Given `fileType === "other"` and user clicks Edit, when edit mode activates, then content is editable in a plain textarea

**Dependencies**: None

---

## US-003: Sticky Save Bar and Keyboard Shortcut

### T-003: Add sticky save bar and Ctrl+S/Cmd+S shortcut to SecondaryFileViewer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed

**Implementation Details**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/SecondaryFileViewer.tsx`
- Wrap the textarea in a div with `overflow: auto; flex: 1` to create a scroll context for sticky positioning
- Inside that wrapper, after the textarea, add a sticky bar: `<div style={{ position: "sticky", bottom: 0, background: "var(--surface-1)", borderTop: "1px solid var(--border)", display: editing ? "flex" : "none", ... }}>Unsaved changes <button onClick={handleSave}>Save</button> <button onClick={handleCancel}>Cancel</button></div>`
- Add `useEffect` for Ctrl+S/Cmd+S: registers `keydown` on `document` when `editing === true`, calls `e.preventDefault()` + `handleSave()`, cleaned up on unmount or when `editing` becomes false
- Pattern reused from EditorPanel.tsx lines 127-138

**Test**: Given the secondary file editor is in edit mode and the viewport is scrolled to the bottom of a long file, when the user views the editor panel, then a sticky bar is fixed at the bottom showing "Unsaved changes" with Save and Cancel buttons

**Test File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SecondaryFileViewer.test.tsx`
- TC-005: Given `editing === true`, when component renders, then sticky bar is present in the DOM with Save and Cancel buttons
- TC-006: Given `editing === false`, when component renders, then sticky bar is not visible
- TC-007: Given `editing === true`, when user presses Ctrl+S, then `handleSave` is called and `preventDefault` is invoked (keyboard event not propagated to browser)
- TC-008: Given `editing === false`, when user presses Ctrl+S, then no save action occurs

**Dependencies**: T-002

---

## US-004: Unsaved Changes Guard on Navigation

### T-004: Add dirty state callback and navigation guard via EditorPanel
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] Completed

**Implementation Details**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/SecondaryFileViewer.tsx`: add `onDirtyChange?: (dirty: boolean) => void` prop; call it with `true` when editing starts or content changes, with `false` when saved or cancelled
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/EditorPanel.tsx`: add `secondaryDirty` state (`useState(false)`); pass `onDirtyChange={setSecondaryDirty}` to `SecondaryFileViewer`; wrap `selectFile` as `wrappedSelectFile = (path) => { if (secondaryDirty && !window.confirm("You have unsaved changes. Discard?")) return; selectFile(path); }` and pass `wrappedSelectFile` to `SkillFileBrowser.onSelect`
- `window.confirm()` is modal/blocking — rapid clicking is naturally prevented

**Test**: Given the secondary file editor has unsaved changes, when the user clicks a different file in the tree, then a confirm dialog appears with "You have unsaved changes. Discard?" and navigation only proceeds if confirmed

**Test File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/EditorPanel.test.tsx`
- TC-001: Given `secondaryDirty === true`, when a new file is selected in SkillFileBrowser, then `window.confirm` is called with the exact message "You have unsaved changes. Discard?"
- TC-002: Given confirm returns `true` (user confirms), when navigation proceeds, then `selectFile` is called with the new path
- TC-003: Given confirm returns `false` (user cancels), when dialog is dismissed, then `selectFile` is NOT called and the current file remains active
- TC-004: Given `secondaryDirty === false`, when a new file is selected, then `window.confirm` is NOT called and `selectFile` fires directly

**Dependencies**: T-002, T-003
