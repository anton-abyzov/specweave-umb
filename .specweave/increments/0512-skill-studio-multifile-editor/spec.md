---
increment: 0512-skill-studio-multifile-editor
title: Skill Studio Multi-File Editor
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio Multi-File Editor

## Problem Statement

The Skill Studio editor currently shows only SKILL.md content. Skills are multi-file directories containing SKILL.md, evals/evals.json, evals/history/*.json, draft.json, and other files. Users have no way to browse or view these supporting files from within the editor, forcing them to use external tools to inspect skill directory contents.

## Goals

- Enable users to browse all files in a skill directory from the editor panel
- Provide appropriate viewing modes per file type (editable markdown, read-only JSON preview, read-only markdown preview, raw text)
- Maintain all existing SKILL.md editing functionality unchanged
- Keep the file browser compact and non-intrusive via a collapsible strip

## User Stories

### US-001: Multi-File Browsing and Viewing in Skill Studio Editor
**Project**: vskill

**As a** skill developer
**I want** to browse and view all files in a skill directory from the editor panel
**So that** I can inspect evals, history, drafts, and other supporting files without leaving Skill Studio

**Acceptance Criteria**:
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

## Out of Scope

- Editing files other than SKILL.md (all secondary files are read-only)
- Creating, renaming, or deleting files from the file tree
- Real-time file watching or auto-refresh when files change on disk
- Syntax highlighting for code files (plain monospace text is sufficient)
- Collapsible JSON tree viewer (pretty-printed indentation only)
- Drag-and-drop file operations
- File search or filtering within the tree

## Technical Notes

### Dependencies
- Existing `resolveSkillDir()` in `eval-server/skill-resolver.ts` for skill directory resolution
- Existing `EditorPanel.tsx` component for UI integration point
- Existing `WorkspaceContext` for editor state management
- Existing `renderMarkdown()` utility for markdown preview of non-SKILL.md files

### Constraints
- File read endpoint must validate resolved paths stay within skill directory (path traversal protection)
- Maximum file size served by API: 1MB (return 413 for larger files)
- Frontend display truncation at 500KB with warning banner
- Binary file detection via null byte scan of first 8KB of file content

### Architecture Decisions
- File list fetched once on skill selection, cached in component state; manual refresh via button
- Two new backend endpoints added to existing `api-routes.ts` router registration
- File tree state is local to the current skill selection; resets on skill navigation
- Secondary file viewer is a separate read-only component from the SKILL.md editor

## Non-Functional Requirements

- **Performance**: File list endpoint responds in under 100ms for directories with up to 200 files; file read endpoint responds in under 50ms for files under 500KB
- **Accessibility**: File tree items are keyboard-navigable with Enter to open; expanded/collapsed state uses aria-expanded attribute
- **Security**: All file read requests validated against path traversal; resolved path must be a descendant of the skill directory after normalization with `path.resolve()`
- **Compatibility**: Works in all browsers supported by existing Skill Studio UI (Chrome, Firefox, Safari, Edge latest versions)

## Edge Cases

- **Empty skill directory**: File tree shows only SKILL.md; if SKILL.md is also missing, tree shows "No files found" message
- **Deeply nested directories**: File tree renders nested folders with indentation; no artificial depth limit
- **Large directories**: File list endpoint returns all entries without pagination; expected max approximately 50 files per skill directory
- **Symlinked files**: Follow symlinks and serve content; path traversal check applies to the resolved real path
- **Concurrent file deletion**: If a listed file is deleted before the user clicks it, the read endpoint returns 404 and the UI shows an error message
- **Files with special characters in names**: URL-encode file paths in API requests; backend decodes and resolves safely

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Path traversal bypass via encoded sequences | 0.2 | 9 | 1.8 | Use `path.resolve()` + startsWith check against skill dir after normalization |
| Large history directories slow down file list | 0.3 | 3 | 0.9 | File list is a flat recursive readdir; no content reading involved |
| Binary file detection false positives | 0.1 | 2 | 0.2 | Only check first 8KB; text files rarely contain null bytes |

## Success Metrics

- Users can view any file in a skill directory without leaving Skill Studio
- SKILL.md editing workflow remains unchanged with zero regressions
- File tree loads in under 200ms for typical skill directories (5-20 files)
- Zero path traversal vulnerabilities in the new endpoints
