# Implementation Plan: vSkill Studio File Browser Fixes

## Overview

Four focused fixes to two existing React components in the eval-ui. No new files, no backend changes, no new dependencies. All changes are in `repositories/anton-abyzov/vskill/src/eval-ui/src/`.

## Architecture

### Component Map

```
EditorPanel.tsx  (parent — wires props, no changes needed)
  |
  +-- SkillFileBrowser.tsx        [MODIFY] remove setExpanded(false) on file select
  |     |
  |     +-- TreeItem (internal)   [NO CHANGE] — expand state is local, already correct
  |
  +-- SecondaryFileViewer.tsx      [MODIFY] toolbar for all types, sticky save bar, Ctrl+S, unsaved guard
  |
  +-- useSkillFiles.ts             [NO CHANGE] — selectFile stays as-is, guard lives in component layer
```

### Change 1: File Tree Collapse Bug (US-001)

**Root cause**: `SkillFileBrowser` line 238 — the `onSelect` callback wraps `onSelect(path)` with `setExpanded(false)`, collapsing the entire file browser panel every time a file is clicked.

**Fix**: Remove the `setExpanded(false)` call from the onSelect handler. The tree item's own folder expand state (`TreeItem` local `useState`) is independent and already correct — folders stay expanded because `TreeItem` only toggles on folder click, not file click.

```
// Before (line 238)
onSelect={(path) => { onSelect(path); setExpanded(false); }}

// After
onSelect={(path) => { onSelect(path); }}
```

Single-line change. The `expanded` state on `SkillFileBrowser` controls the panel's visibility (collapsed strip vs tree view), not individual folder states. Removing `setExpanded(false)` means the tree stays visible after file selection, which is the desired behavior.

### Change 2: Universal Toolbar (US-002)

**Current behavior**: The toolbar (view mode toggles + Edit/Save/Cancel + file size) only renders when `fileType !== "other"` (line 247). Files like `.txt`, `.yaml`, `.toml` get no toolbar and no edit capability.

**Fix**: Always render the toolbar. For `fileType === "other"`, render a simplified toolbar (no Raw/Split/Preview toggles, just file size + Edit/Save/Cancel). The view mode toggles remain exclusive to md/json since those are the only types with meaningful preview rendering.

Toolbar structure by file type:

| File Type | View Mode Toggles | File Size | Edit/Save/Cancel |
|-----------|-------------------|-----------|------------------|
| md        | Raw, Split, Preview | Yes     | Yes              |
| json      | Raw, Split, Preview | Yes     | Yes              |
| other     | (none)              | Yes     | Yes              |
| binary    | (no toolbar — existing binary fallback) | N/A | N/A |

Implementation: Remove the `fileType !== "other"` guard on the toolbar div. Wrap the view-mode toggle buttons in a `fileType !== "other"` conditional so they only appear for md/json.

### Change 3: Sticky Save Bar + Ctrl+S (US-003)

**Sticky save bar**: Add a `position: sticky; bottom: 0` bar inside the content area div (the one with `flex: 1, display: "flex", minHeight: 0`). The bar renders only when `editing === true`. It shows "Unsaved changes" text plus Save and Cancel buttons, styled consistently with the existing toolbar buttons.

Layout:

```
+----------------------------------+
|  Toolbar (top)                   |
+----------------------------------+
|                                  |
|  <textarea> (editing content)    |
|                                  |
+----------------------------------+
|  [Unsaved changes] [Save][Cancel]|  <-- sticky bottom bar
+----------------------------------+
```

The sticky bar sits inside the scroll container so it stays visible regardless of scroll position. It uses `background: var(--surface-1)` with a top border for visual separation.

**Ctrl+S / Cmd+S shortcut**: Add a `useEffect` hook in `SecondaryFileViewer` that registers a `keydown` listener on `document` (scoped to when `editing === true`). Pattern reused from `EditorPanel.tsx` line 127-138:

```typescript
useEffect(() => {
  if (!editing) return;
  const handler = (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      handleSave();
    }
  };
  document.addEventListener("keydown", handler);
  return () => document.removeEventListener("keydown", handler);
}, [editing, handleSave]);
```

The `e.preventDefault()` blocks the browser's native save-page dialog. The effect cleanup ensures the listener is removed when exiting edit mode or unmounting.

### Change 4: Unsaved Changes Guard (US-004)

**Where the guard lives**: The guard must intercept file selection before the `selectFile` callback fires. Since `SecondaryFileViewer` does not control file selection (that flows through `SkillFileBrowser` -> `EditorPanel` -> `useSkillFiles.selectFile`), the guard needs to be at the `EditorPanel` level where both components are wired.

**Approach**: `SecondaryFileViewer` exposes an `editing` + dirty state via a new `hasUnsavedChanges` prop callback or by lifting the `editing` state up. The simpler approach: `SecondaryFileViewer` accepts an `onBeforeNavigate` callback that the parent calls before switching files. But since the parent doesn't know about the viewer's internal edit state, the cleanest approach is:

1. `SecondaryFileViewer` exposes `hasUnsavedChanges` via a callback prop `onDirtyChange?: (dirty: boolean) => void` that fires whenever `editing` state or content changes.
2. `EditorPanel` tracks `secondaryDirty` state.
3. `EditorPanel` wraps `selectFile` to check `secondaryDirty` and show `window.confirm("You have unsaved changes. Discard?")` before proceeding.

This keeps the confirm dialog at the orchestration layer (EditorPanel) where file selection routing already happens, and avoids coupling SkillFileBrowser to the viewer's edit state.

```
EditorPanel
  secondaryDirty: boolean (from SecondaryFileViewer callback)
  |
  wrappedSelectFile = (path) => {
    if (secondaryDirty && !window.confirm("You have unsaved changes. Discard?")) return;
    selectFile(path);
  }
  |
  passes wrappedSelectFile to SkillFileBrowser.onSelect
```

When the user cancels the dialog, `selectFile` is not called, so the tree selection and viewer stay on the current file. When confirmed, the viewer unmounts/remounts with the new file content, resetting `editing` to `false`.

## Technology Stack

- **Framework**: React 18 (existing)
- **Language**: TypeScript (existing)
- **Build**: Vite (existing)
- **New dependencies**: None

## Architecture Decisions

- **`window.confirm()` for unsaved guard**: Simple, blocking, no custom modal needed. Spec explicitly calls for this approach. Covers the edge case of rapid switching (confirm is modal, blocks further clicks).
- **`position: sticky` for save bar**: Native CSS, no JS scroll listener needed, no layout thrashing. Works inside the existing flex container.
- **Keyboard shortcut on `document`**: Matches EditorPanel's existing pattern. Scoped via `editing` guard so it's inactive when not editing.
- **Dirty state lifted to EditorPanel**: Keeps SkillFileBrowser unaware of edit state. Single responsibility — browser navigates, viewer edits, parent orchestrates.

## Implementation Phases

### Phase 1: Tree Fix (US-001)
- One-line fix in SkillFileBrowser.tsx

### Phase 2: Universal Toolbar (US-002)
- Restructure toolbar conditional in SecondaryFileViewer.tsx

### Phase 3: Sticky Bar + Shortcut (US-003)
- Add sticky bar JSX + styles
- Add useEffect keydown handler

### Phase 4: Unsaved Guard (US-004)
- Add `onDirtyChange` prop to SecondaryFileViewer
- Track `secondaryDirty` in EditorPanel
- Wrap `selectFile` with confirm guard

## Testing Strategy

- **Unit tests**: Vitest + React Testing Library for each component
  - SkillFileBrowser: verify expanded state persists after file click
  - SecondaryFileViewer: toolbar renders for all file types, sticky bar visibility, keyboard shortcut fires save
- **Integration test**: EditorPanel wiring — confirm dialog blocks/allows navigation
- **Manual verification**: Scroll behavior of sticky bar on a long file (CSS position:sticky)

## Technical Challenges

### Challenge 1: Sticky Bar Inside Flex Layout
**Problem**: `position: sticky` requires a scrolling ancestor. The content area uses `flex: 1, minHeight: 0` which creates a scroll context only if `overflow: auto` is set.
**Solution**: Wrap the textarea and sticky bar in a div with `overflow: auto; flex: 1` so the bar sticks to the bottom of that scroll container.

### Challenge 2: Ctrl+S Conflict with Browser Save
**Problem**: Ctrl+S triggers the browser's "Save Page" dialog.
**Solution**: `e.preventDefault()` in the keydown handler. Already proven in EditorPanel.

### Challenge 3: Rapid File Switching During Confirm
**Problem**: User clicks multiple files while confirm dialog is open.
**Solution**: `window.confirm()` is modal/blocking — no further click events fire until it's dismissed. This is a built-in safeguard.
