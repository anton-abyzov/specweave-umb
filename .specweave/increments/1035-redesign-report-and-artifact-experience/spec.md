# 1035 Redesign report and artifact experience

## Problem
The PS23 HTML report dominates the conversation with a long, stark document. Its expand button opens another right panel rather than a spacious reader. Generation choices and host rendering need separate fixes.

## Scope
In: HTML report inline presentation, focused viewer entry, authored report guidance and example, primary-source research, responsive evidence. Out: settings increment 1031, hosted publishing, provider enablement, releases, rewriting historical attachments.

## Acceptance Criteria
- [ ] AC-01: Research identifies the exact PS23 attachment and generation/rendering path, distinguishes verified Karpathy attribution from interpretation, and compares primary-source artifact and diagram approaches.
- [ ] AC-02: Inline HTML reports have a bounded preview, visible title and accessible Open report action; expansion opens one spacious viewer without adding a right panel.
- [ ] AC-03: Closing and reopening preserves the report's interactive state and conversation position; keyboard focus returns to the trigger and Escape closes the reader.
- [ ] AC-04: Generation guidance and a self-contained report example demonstrate readable type, outcome-first hierarchy, an accessible useful state diagram, responsive light/dark styles and content-preserving detail navigation.
- [ ] AC-05: Headless before/after captures and interaction checks cover desktop/mobile, dark/light, navigation, focus and retained sandbox boundaries; focused tests and production build pass. Review and PR are delivered to the existing merge owner; installed acceptance is identified separately.

## Approach
Reuse the existing viewer overlay instead of introducing another pane. Keep a stable iframe mount while moving its host into the overlay so controls and reading position survive. Bound the inline preview and make its noninteractive preview state explicit. Use existing theme tokens. Improve agent-facing generation guidance rather than overriding arbitrary authored HTML. SVG/semantic HTML for small state flows; existing Mermaid for Markdown architecture. Keep Claude hosted artifacts optional and separate.

## Decisions
### Defaulted
- D-01: Full-window reader with conversation folded by default for reports; conversation can be explicitly revealed.
- D-02: Preserve stored report bytes. A checked-in example improves future generation; no silent historical rewriting.
- D-03: No new diagram dependency for a small explanatory state flow.
### Open
- none

## Tasks
### T-01 Research and design
- AC: AC-01 | Files: docs/reports/report-experience.md | Test: primary-source and source-path review
### T-02 Implement report reader and authoring example
- AC: AC-02, AC-03, AC-04 | Files: apps/web/src/components/chat/HtmlRenderFrame.tsx, apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/files/BrowserDocumentFrame.tsx, apps/web/src/index.css, packages/shared/src/htmlRender.ts, apps/web/src/hooks/useHtmlRenderTheme.ts, docs/reports/report-example.html | Test: report-experience headless fixture and htmlRender focused tests
### T-03 Verify and close 1035
- AC: AC-05 | Files: README.md, CHANGELOG.md, AGENTS.md, apps/web/tests/report-experience/main.tsx, apps/web/tests/report-experience/vite.config.ts, apps/web/tests/report-experience/index.html, apps/web/tests/report-experience/fixture.css, apps/web/tests/report-experience/stubs.ts, docs/reports/report-experience.md | Test: headless interaction checks, focused tests, web production build, fresh-context review, specweave verify 1035
