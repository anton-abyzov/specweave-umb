---
increment: 0496-skill-studio-ui-polish
title: Skill Studio UI Polish & Editor AI Builder
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio UI Polish & Editor AI Builder

## Problem Statement

The Skill Studio Create Skill forms label the skill definition body as "System Prompt," which is confusing because the file is actually SKILL.md. The body content in both create forms and the SkillContentViewer renders as raw preformatted text rather than styled markdown. The description textarea is too short. The Editor page lacks an AI regenerate workflow for iterating on skill content. There is no visibility into whether the Skill-Creator tool is installed.

## Goals

- Align Create Skill form labeling with the SKILL.md convention already used in SkillContentViewer
- Add markdown preview capability to both create forms and the content viewer
- Improve form ergonomics (description textarea height)
- Enable AI-powered skill content regeneration directly from the Editor page
- Surface Skill-Creator installation status in the sidebar

## User Stories

### US-001: Rename "System Prompt" to "SKILL.md"
**Project**: vskill
**As a** skill author
**I want** the body textarea section labeled "SKILL.md" with a file icon badge and "Skill Definition" subtitle
**So that** the form labeling matches the actual file being created and is consistent with SkillContentViewer

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given CreateSkillInline is rendered, when the user views the body textarea card, then the heading reads "SKILL.md" (not "System Prompt") with a file icon badge matching SkillContentViewer's icon style
- [x] **AC-US1-02**: Given CreateSkillPage is rendered, when the user views the body textarea card, then the heading reads "SKILL.md" with the same file icon badge and "Skill Definition" subtitle
- [x] **AC-US1-03**: Given either create form, when the user views the heading, then a secondary subtitle "Skill Definition" appears below/beside the "SKILL.md" label

---

### US-002: Write/Preview Toggle for SKILL.md Body
**Project**: vskill
**As a** skill author
**I want** a segmented Write/Preview toggle in the SKILL.md card header
**So that** I can preview how the markdown body content will render before creating the skill

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given CreateSkillInline with the SKILL.md card visible, when the user sees the card header, then a segmented toggle with "Write" and "Preview" options is present, defaulting to "Write"
- [x] **AC-US2-02**: Given Write mode is active, when the user types in the textarea, then input works as before (no behavior change)
- [x] **AC-US2-03**: Given Preview mode is active, when the card body renders, then the body content is displayed as rendered markdown using renderMarkdown() with dangerouslySetInnerHTML, matching EditorPanel's preview pane styling
- [x] **AC-US2-04**: Given CreateSkillPage, when the user toggles to Preview, then the same markdown rendering behavior applies
- [x] **AC-US2-05**: Given the user switches between Write and Preview, then the body content is preserved (no data loss on toggle)

---

### US-003: Increase Description Textarea Height
**Project**: vskill
**As a** skill author
**I want** a taller description textarea with vertical resize support
**So that** I have more room to write meaningful descriptions without scrolling

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given CreateSkillInline, when the description textarea renders, then rows is 3 (was 2), minHeight is 72px, and CSS resize is set to "vertical"
- [x] **AC-US3-02**: Given CreateSkillPage, when the description textarea renders, then the same rows=3, minHeight=72px, and resize="vertical" are applied
- [x] **AC-US3-03**: Given either form, when the user drags the textarea resize handle vertically, then the textarea expands or contracts (no horizontal resize)

---

### US-004: Render SKILL.md Body as Markdown in SkillContentViewer
**Project**: vskill
**As a** skill consumer
**I want** the SKILL.md body rendered as styled markdown in SkillContentViewer
**So that** skill definitions are readable with proper headings, lists, code blocks, and tables

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given SkillContentViewer with a body containing markdown, when the component renders, then the body is displayed using renderMarkdown() with dangerouslySetInnerHTML instead of a raw `<pre>` block
- [x] **AC-US4-02**: Given a body with headings, bold, code blocks, lists, and tables, when rendered, then all markdown elements display correctly with styled HTML matching EditorPanel preview
- [x] **AC-US4-03**: Given a large body, when rendered as markdown, then maxHeight remains 400px with overflow-y auto scroll

---

### US-005: AI Regenerate on Editor Page
**Project**: vskill
**As a** skill author
**I want** a "Regenerate" button in the EditorPanel toolbar that opens a prompt input, calls /api/skills/generate?sse, and shows a diff of the result
**So that** I can iterate on skill content using AI without leaving the editor

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the EditorPanel toolbar, when rendered, then a "Regenerate" button with a sparkle icon appears next to the existing "AI Edit" button
- [x] **AC-US5-02**: Given the user clicks "Regenerate," when the panel opens, then a prompt textarea is displayed below the toolbar (or as an inline panel) for entering the regeneration prompt
- [x] **AC-US5-03**: Given the user submits a prompt, when the SSE call to /api/skills/generate?sse completes, then a diff view is shown using computeDiff + the same diff rendering pattern from SkillImprovePanel (line-by-line with green/red highlighting)
- [x] **AC-US5-04**: Given the diff is displayed, when the user clicks "Apply," then the editor content is replaced with the generated content and the diff panel closes
- [x] **AC-US5-05**: Given the diff is displayed, when the user clicks "Discard," then the generated content is discarded and the diff panel closes without changes
- [x] **AC-US5-06**: Given a regeneration is in progress, when the user clicks "Regenerate" again, then the current SSE stream is aborted (AbortController pattern) and a new generation starts
- [x] **AC-US5-07**: Given the regeneration, when the provider/model is resolved, then the current workspace config provider/model is used (no separate model picker)

---

### US-006: Skill-Creator Installation Check
**Project**: vskill
**As a** skill author
**I want** a status indicator in the left sidebar showing whether the Skill-Creator tool is installed
**So that** I know if I can use AI skill creation features and how to install the tool if missing

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the LeftPanel sidebar, when it renders, then it calls api.getSkillCreatorStatus() and displays a status indicator below the "New Skill" button area
- [x] **AC-US6-02**: Given the Skill-Creator is installed (status.installed === true), when the indicator renders, then a green dot with "Skill Creator installed" text is shown
- [x] **AC-US6-03**: Given the Skill-Creator is NOT installed (status.installed === false), when the indicator renders, then a yellow/amber warning dot with "Skill Creator not installed" text is shown, along with the install command displayed in a copyable code block
- [x] **AC-US6-04**: Given the install command is displayed, when the user clicks the code block or a copy button, then the command text is copied to the clipboard
- [x] **AC-US6-05**: Given the status check fails (network error), when the indicator renders, then the indicator is hidden (graceful degradation, no error shown)

## Out of Scope

- Backend API changes (all endpoints already exist)
- Markdown rendering library upgrade (reuse existing renderMarkdown.ts)
- State persistence of Write/Preview toggle across page navigation
- Separate model picker for the EditorPanel Regenerate feature
- Refresh/re-check button for Skill-Creator status (page reload is sufficient)
- Mobile/responsive layout adjustments

## Technical Notes

### Dependencies
- `renderMarkdown.ts` -- existing lightweight markdown-to-HTML utility
- `computeDiff` + `DiffLine` from `utils/diff.ts` -- existing diff utility
- `/api/skills/generate?sse` -- existing SSE endpoint for AI skill generation
- `/api/skill-creator-status` -- existing GET endpoint returning `{ installed, installCommand }`
- `api.getSkillCreatorStatus()` -- existing frontend API method

### Constraints
- All changes are frontend-only (React 19 + Vite + Tailwind CSS 4)
- renderMarkdown uses dangerouslySetInnerHTML; content is user-authored SKILL.md (trusted)
- maxHeight 400px with overflow scroll for all markdown preview containers
- Regenerate feature reuses existing AbortController pattern for SSE stream management

### Architecture Decisions
- Reuse SkillContentViewer's file icon badge + "Skill Definition" subtitle pattern for create form headers
- Reuse EditorPanel's segmented toggle pattern for Write/Preview in create forms
- Reuse SkillImprovePanel's diff view pattern (computeDiff + line-by-line rendering) for Regenerate results
- No new components needed for diff display; inline the pattern from SkillImprovePanel

## Success Metrics

- All 6 user stories pass acceptance criteria
- No visual regressions in existing Skill Studio pages
- Create forms, editor, and viewer show consistent SKILL.md labeling and markdown rendering
