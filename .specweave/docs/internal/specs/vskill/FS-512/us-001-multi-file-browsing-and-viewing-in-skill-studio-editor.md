---
id: US-001
feature: FS-512
title: "Multi-File Browsing and Viewing in Skill Studio Editor"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
---

# US-001: Multi-File Browsing and Viewing in Skill Studio Editor

**Feature**: [FS-512](./FEATURE.md)

**As a** skill developer
**I want** to browse and view all files in a skill directory from the editor panel
**So that** I can inspect evals, history, drafts, and other supporting files without leaving Skill Studio

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill is selected in the workspace, when the editor panel loads, then a collapsible file tree strip appears at the top of the editor panel, collapsed by default, showing the currently active file path (SKILL.md)
- [x] **AC-US1-02**: Given the file tree strip is collapsed, when the user clicks the expand control, then the strip expands to show all files in the skill directory as a hierarchical tree with folders and files
- [x] **AC-US1-03**: Given the file tree is expanded, when the user clicks a .md file (not SKILL.md), then the editor area shows raw text on the left and rendered markdown preview on the right, both read-only
- [x] **AC-US1-04**: Given the file tree is expanded, when the user clicks a .json file, then the editor area shows raw text on the left and pretty-printed formatted JSON on the right, both read-only
- [x] **AC-US1-05**: Given the file tree is expanded, when the user clicks a file that is not .md or .json, then the editor area shows raw text content in read-only mode
- [x] **AC-US1-06**: Given the file tree is expanded, when the user clicks SKILL.md, then the editor returns to the standard editable view with all existing functionality (edit, save, AI Edit, Regenerate) intact
- [x] **AC-US1-07**: Given the user navigates to a different skill in the sidebar, then the file browser state resets and the editor shows SKILL.md for the newly selected skill
- [x] **AC-US1-08**: Given the backend cannot read a requested file (permissions error, missing after list, binary content), when the user clicks that file, then an explicit error message is displayed in the editor area explaining why the file cannot be shown
- [x] **AC-US1-09**: Given a file in the skill directory exceeds 1MB, when the user requests that file via the API, then the server returns a 413 status with a "file too large" error message
- [x] **AC-US1-10**: Given a file content is between 500KB and 1MB, when displayed in the editor, then a warning banner appears at the top stating the content has been truncated for display
- [x] **AC-US1-11**: Given a file contains null bytes in its first 8KB, when requested via the API, then the server returns a response with `binary: true` flag and no content, and the frontend displays a "binary file -- cannot display" message
- [x] **AC-US1-12**: Given the file tree strip is visible, when the user clicks a refresh button in the strip, then the file list is re-fetched from the backend and the tree is updated
- [x] **AC-US1-13**: Given the backend receives a file read request with path traversal characters (e.g., `../`), when the resolved path falls outside the skill directory, then the server returns a 403 status with "access denied" error
- [x] **AC-US1-14**: Given a new backend endpoint `GET /api/skills/:plugin/:skill/files` exists, when called, then it returns a JSON array of all file paths relative to the skill directory root
- [x] **AC-US1-15**: Given a new backend endpoint `GET /api/skills/:plugin/:skill/files/*` exists, when called with a valid relative file path, then it returns the file content as text with metadata (size in bytes, binary flag)

---

## Implementation

**Increment**: [0512-skill-studio-multifile-editor](../../../../../increments/0512-skill-studio-multifile-editor/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Backend file-list and file-read endpoints
- [x] **T-002**: Frontend types and API client methods
- [x] **T-003**: useSkillFiles hook
- [x] **T-004**: SkillFileBrowser component
- [x] **T-005**: SecondaryFileViewer component
- [x] **T-006**: EditorPanel integration
