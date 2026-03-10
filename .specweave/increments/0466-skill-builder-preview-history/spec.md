---
increment: 0466-skill-builder-preview-history
title: 'Skill Builder: MD Preview & Per-Case History'
type: feature
priority: P1
status: completed
created: 2026-03-09T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Skill Builder: MD Preview & Per-Case History

## Problem Statement

The Skill Builder workspace (localhost:3162) has two usability gaps. First, the SKILL.md editor's "Preview" pane renders the markdown body as a raw `<pre>` block instead of formatted HTML, making it no better than reading the source. Skill authors cannot visually verify their documentation without leaving the editor. Second, the TestsPanel shows only the latest run result for each test case. Viewing a case's execution history requires switching to the HistoryPanel (Ctrl+4), breaking the editing flow. Both issues slow down the skill authoring iteration loop.

## Goals

- Render SKILL.md body as proper HTML (headers, bold, italic, lists, code blocks, links, tables) in the preview pane
- Provide per-test-case execution history directly within the TestsPanel detail view
- Keep implementation lightweight with no heavy external dependencies
- Maintain visual consistency with existing UI patterns

## User Stories

### US-001: Custom Markdown Renderer Utility
**Project**: vskill
**As a** skill author
**I want** a lightweight markdown-to-HTML renderer available in the eval-ui codebase
**So that** markdown content can be rendered as formatted HTML without adding heavy external dependencies

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given markdown text with headers (h1-h3), bold, italic, and inline code, when renderMarkdown() is called, then it returns correct HTML with appropriate styling for each element
- [x] **AC-US1-02**: Given markdown text with fenced code blocks (triple backticks), when renderMarkdown() is called, then it returns a styled `<pre><code>` block preserving whitespace and formatting
- [x] **AC-US1-03**: Given markdown text with unordered lists (- item) and ordered lists (1. item), when renderMarkdown() is called, then it returns properly indented list HTML
- [x] **AC-US1-04**: Given markdown text with links ([text](url)), when renderMarkdown() is called, then it returns `<a>` tags with `target="_blank"` and `rel="noopener noreferrer"`
- [x] **AC-US1-05**: Given markdown text with pipe-separated tables, when renderMarkdown() is called, then it returns a styled `<table>` with proper `<thead>` and `<tbody>` sections
- [x] **AC-US1-06**: Given empty or undefined input, when renderMarkdown() is called, then it returns an empty string without errors

---

### US-002: Real Markdown Preview in EditorPanel
**Project**: vskill
**As a** skill author
**I want** the SKILL.md editor preview pane to render the markdown body as formatted HTML
**So that** I can visually verify my skill documentation looks correct while editing

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a SKILL.md with markdown body content, when the preview pane is visible (Side-by-Side or Preview mode), then the body renders as formatted HTML (not raw monospace text) using dangerouslySetInnerHTML with the renderMarkdown utility
- [x] **AC-US2-02**: Given the user is typing in the raw editor, when the content changes, then the preview pane updates in real time to reflect the rendered markdown
- [x] **AC-US2-03**: Given a SKILL.md with frontmatter fields and allowed-tools, when the preview pane renders, then the frontmatter cards and allowed-tools pills remain unchanged and appear above the rendered body
- [x] **AC-US2-04**: Given a SKILL.md with no body content (frontmatter only), when the preview pane renders, then no body section appears and no errors occur

---

### US-003: Per-Case Execution History in TestsPanel
**Project**: vskill
**As a** skill author
**I want** to see a test case's execution history directly within the TestsPanel detail view
**So that** I can track how a specific test case has performed over time without switching panels

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a selected test case in TestsPanel, when the CaseDetail view renders, then a collapsible "Execution History" section appears below the LLM Output section, collapsed by default
- [x] **AC-US3-02**: Given the user expands the Execution History section, when history data is available, then it fetches via api.getCaseHistory() and displays the last 10 runs showing: timestamp, model, run type badge, pass rate percentage, duration, token count, and per-assertion pass/fail with reasoning
- [x] **AC-US3-03**: Given 2 or more history entries exist for a test case, when the Execution History section is expanded, then a MiniTrend sparkline is displayed showing the pass rate trend over time
- [x] **AC-US3-04**: Given the Execution History section is expanded, when the user looks at the bottom of the history list, then a "View full history" link is visible that switches the active panel to the HistoryPanel (Ctrl+4)
- [x] **AC-US3-05**: Given the user expands the Execution History section, when the API call is in progress, then a loading spinner is shown; when no history exists, then a "No history for this case" message is displayed

---

### US-004: Shared History Display Utilities
**Project**: vskill
**As a** developer maintaining the eval-ui codebase
**I want** the history display utilities (passRateColor, shortDate, fmtDuration, MiniTrend) to be shared between HistoryPerEval and the new CaseDetail history section
**So that** there is no code duplication and both views stay visually consistent

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the shared utilities (passRateColor, shortDate, fmtDuration, MiniTrend), when extracted to a shared module, then both HistoryPerEval.tsx and the CaseDetail history section import from the same source
- [x] **AC-US4-02**: Given the shared utilities are extracted, when HistoryPerEval is rendered, then its visual output is identical to before the extraction (no visual regression)
- [x] **AC-US4-03**: Given the CaseDetail history section and the HistoryPerEval expanded detail, when both display the same run entry, then the visual treatment (colors, formatting, spacing) is consistent between them

## Out of Scope

- Handling relative links (e.g., `./examples/foo.md`) in the markdown renderer
- Adding react-markdown, remark, or other heavy markdown parsing libraries
- Syntax highlighting within code blocks (plain monospace is sufficient)
- Backend or API changes (all endpoints and types already exist)
- Editing or deleting history entries from the UI
- Full markdown spec compliance (e.g., nested blockquotes, footnotes, HTML passthrough)

## Technical Notes

### Source Material
- **renderMarkdown()**: Port from `vskill-platform/src/app/components/eval/EvalCaseCard.tsx` lines 34-56, extending with table support and link target attributes
- **getCaseHistory API**: Already exists at `eval-ui/src/api.ts` line 97
- **CaseHistoryEntry type**: Already defined at `eval-ui/src/types.ts` line 138
- **History endpoint**: `/api/skills/:plugin/:skill/history/case/:evalId` in `eval-server/api-routes.ts`
- **History UI patterns**: `HistoryPerEval.tsx` contains passRateColor, shortDate, fmtDuration, MiniTrend to extract

### Constraints
- No new npm dependencies -- custom renderer only
- dangerouslySetInnerHTML is acceptable (local dev tool, no XSS risk)
- History limited to last 10 runs inline to keep detail view responsive

### Key Files
- `src/eval-ui/src/pages/workspace/EditorPanel.tsx` -- preview pane modification
- `src/eval-ui/src/pages/workspace/TestsPanel.tsx` -- CaseDetail history section
- `src/eval-ui/src/components/HistoryPerEval.tsx` -- utilities to extract
- `src/eval-ui/src/utils/parseFrontmatter.ts` -- existing frontmatter parser (unchanged)

## Success Metrics

- Skill authors can read rendered SKILL.md documentation in the preview pane without leaving the editor
- Test case execution trends are visible inline without panel switching
- Zero new external dependencies added
- All existing tests continue to pass with no visual regressions in HistoryPerEval
