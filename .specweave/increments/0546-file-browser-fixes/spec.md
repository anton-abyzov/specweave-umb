---
increment: 0546-file-browser-fixes
title: vSkill Studio File Browser Fixes
type: feature
priority: P1
status: completed
created: 2026-03-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# vSkill Studio File Browser Fixes

## Problem Statement

The vSkill Studio local UI file browser (localhost:3162) has a usability bug and missing editor capabilities that slow down skill authoring. The file tree collapses every time a file is clicked because `onSelect` calls `setExpanded(false)`, forcing users to re-expand the tree repeatedly. Non-markdown/non-JSON files cannot be edited because the toolbar only renders for those two types. The Save button scrolls out of view on long files, and there is no keyboard shortcut for saving secondary files.

## Goals

- Fix the tree collapse bug so file navigation is seamless
- Enable editing for all common text file types (txt, yaml, toml, etc.)
- Provide a sticky save bar and Ctrl+S/Cmd+S shortcut so saving is always accessible
- Guard against accidental loss of unsaved edits on navigation

## User Stories

### US-001: File Tree Stays Expanded on File Selection
**Project**: vskill
**As a** skill author
**I want** the file browser tree to stay expanded when I click a file
**So that** I can navigate between files without re-expanding folders each time

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given an expanded folder in the file tree, when the user clicks a file inside that folder, then the folder remains expanded and the clicked file becomes the active selection
- [x] **AC-US1-02**: Given multiple nested folders are expanded, when the user clicks any file at any depth, then all previously expanded folders remain expanded

### US-002: Universal File Type Editing
**Project**: vskill
**As a** skill author
**I want** to edit any text file type in the secondary file viewer
**So that** I can modify txt, yaml, toml, and other common files without leaving Studio

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a file with a non-md/non-json extension (e.g., .txt, .yaml, .toml) is selected, when the viewer renders, then a toolbar is displayed with Edit, Save, Cancel buttons and file size
- [x] **AC-US2-02**: Given a markdown file is selected, when the viewer renders, then the toolbar shows Raw/Split/Preview mode toggles plus Edit/Save/Cancel (existing behavior preserved)
- [x] **AC-US2-03**: Given a JSON file is selected, when the viewer renders, then the toolbar shows Raw/Split/Preview mode toggles plus Edit/Save/Cancel (existing behavior preserved)
- [x] **AC-US2-04**: Given a non-md/non-json file is open and the user clicks Edit, when the editor activates, then the file content is editable in a plain text editor

### US-003: Sticky Save Bar and Keyboard Shortcut
**Project**: vskill
**As a** skill author
**I want** a persistent save bar and Ctrl+S shortcut when editing secondary files
**So that** I can save changes without scrolling to the top of a long file

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the secondary file editor is in edit mode, when the viewport scrolls, then a full-width sticky bar remains fixed at the bottom of the editor panel showing "Unsaved changes" text with Save and Cancel buttons
- [x] **AC-US3-02**: Given the secondary file editor has focus and is in edit mode, when the user presses Ctrl+S (Windows/Linux) or Cmd+S (macOS), then the file is saved
- [x] **AC-US3-03**: Given the secondary file editor is not in edit mode, when the user presses Ctrl+S/Cmd+S, then no save action occurs (shortcut is inactive)

### US-004: Unsaved Changes Guard on Navigation
**Project**: vskill
**As a** skill author
**I want** a warning when I navigate away from a file with unsaved changes
**So that** I do not accidentally lose my edits

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the secondary file editor has unsaved changes, when the user clicks a different file in the tree, then a confirm dialog appears with the message "You have unsaved changes. Discard?"
- [x] **AC-US4-02**: Given the confirm dialog is shown, when the user confirms, then changes are discarded and the newly selected file loads
- [x] **AC-US4-03**: Given the confirm dialog is shown, when the user cancels, then the editor stays on the current file with edits intact and the tree selection does not change

## Out of Scope

- Syntax highlighting for non-md/non-json files (future increment)
- Auto-save functionality
- Drag-and-drop file reordering in the tree
- File creation or deletion from the browser
- Primary editor (SKILL.md) changes -- this increment targets secondary files only

## Technical Notes

### Dependencies
- SkillFileBrowser.tsx -- file tree component with the expand bug
- SecondaryFileViewer.tsx -- viewer/editor for non-SKILL.md files
- EditorPanel.tsx -- parent panel, has existing Cmd+S pattern to reuse

### Constraints
- Must not change the primary SKILL.md editor behavior
- Keyboard shortcut must reuse the existing Meta key detection pattern from EditorPanel

### Architecture Decisions
- Sticky bar uses CSS `position: sticky; bottom: 0` inside the editor scroll container
- Unsaved changes guard uses `window.confirm()` for simplicity

## Non-Functional Requirements

- **Performance**: Sticky bar must not cause layout thrashing on scroll
- **Accessibility**: Save bar buttons must be keyboard-focusable; Ctrl+S/Cmd+S follows platform conventions
- **Compatibility**: Works in Chromium-based browsers (Studio runs on localhost via Vite dev server)

## Edge Cases

- **Empty file**: Editing an empty file shows an empty editor; saving preserves the empty content
- **Binary file selected**: Non-text files (e.g., .png) keep the existing preview/fallback behavior with no edit toolbar
- **Rapid file switching**: Clicking multiple files quickly while confirm dialog is open does not stack multiple dialogs
- **Large file**: Sticky bar remains visible regardless of file content length

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Tree expand state regression breaks folder toggle | 0.2 | 5 | 1.0 | Unit test expand/collapse state transitions |
| Ctrl+S conflicts with browser save-page shortcut | 0.3 | 3 | 0.9 | Use preventDefault() on the keydown handler |

## Success Metrics

- File tree stays expanded across 10 consecutive file clicks
- All text-based file types show toolbar and are editable
- Save bar visible when scrolled to bottom of a 500-line file
- Ctrl+S/Cmd+S saves file without triggering browser save dialog
