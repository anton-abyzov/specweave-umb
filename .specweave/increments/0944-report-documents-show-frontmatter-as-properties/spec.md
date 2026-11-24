# Report documents show frontmatter as properties

## Problem

Opening a Markdown report from a thread's artifacts (October 19, 2026, `~/Projects/github/studio-research-notes/project-join-handoff-pairing-2026-10-19.md`) showed its YAML frontmatter as one large serif paragraph above a repeated title. The artifact viewer, the Library viewer, the report's file pane and the linked-document reader rendered the file raw: the opening `---` became a rule and the closing `---` turned every `key: value` line into a setext heading. The report reader already parses flat frontmatter (`reportFrontmatter`), but those four viewers never used it. In tables, a file link labelled `~/…` printed its full path and then a second link chip, so long paths dominated the page.

## Scope

In: Markdown document rendering in the SpecWithCode viewers (`anton-abyzov/specwithcode-dev`): artifact viewer, Library viewer, report file pane, linked Markdown document reader; file-link label matching for `~/` labels. Out: report reader layout for worker replies, page measure and overlay layout, HTML reports, the report's content.

## Acceptance Criteria

- [ ] AC-01: A Markdown file with flat frontmatter opens with its title (frontmatter `title` or the opening `# heading`) as the page title, the other fields in the sans property table, and the body as written; the opening heading is not repeated and no `key: value` text appears as prose.
- [ ] AC-02: Frontmatter too rich for a table is shown as a YAML block, not as a rule and a heading; a file without frontmatter renders unchanged.
- [ ] AC-03: The artifact viewer, Library viewer, report file pane and linked-document reader all use the same document view.
- [ ] AC-04: A file link whose label is the home-relative form of its destination (`[~/a/b.md](file:///Users/me/a/b.md)`) renders as one compact link, not the full path plus a chip.
- [ ] AC-05: Long property values wrap inside their cell; the page has no horizontal overflow at 390, 1000 (with the thread rail) and 1440 px, in dark and light.

## Approach

`packages/shared/src/reportDocument.ts` gains `markdownDocument(text)` (pure) on top of `reportFrontmatter`. `ReportReader.tsx` exports `MarkdownDocumentView` and shares its property rows with `ReportDocumentView`; the four viewers render it. `index.css`: properties use the interface face, values wrap, body spacing under title and facts. `packages/client-runtime/src/markdownLinks.ts`: `isMarkdownFileLinkLabel` accepts `~/` labels.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Title, then property table, then body (the Claude desktop order already recorded in report-formatting memory); the report's own first paragraph stays first in the body rather than being lifted into a lead.
- D-02: Page measure (36rem) from PR #292 unchanged.

## Tasks

### T-01 Document view for Markdown files with frontmatter
- AC: AC-01, AC-02, AC-03, AC-05 | Files: packages/shared/src/reportDocument.ts, packages/shared/src/reportDocument.test.ts, packages/shared/src/threadReport.ts, apps/web/src/components/chat/ReportReader.tsx, apps/web/src/components/chat/MarkdownDocumentView.test.tsx, apps/web/src/components/chat/ThreadArtifacts.tsx, apps/web/src/components/chat/MarkdownDocumentReader.tsx, apps/web/src/components/studio/shell/LibraryFileViewer.tsx, apps/web/src/index.css | Test: vp test run packages/shared/src/reportDocument.test.ts apps/web/src/components/chat/MarkdownDocumentView.test.tsx

### T-02 Home-relative file link labels stay compact
- AC: AC-04 | Files: packages/client-runtime/src/markdownLinks.ts, packages/client-runtime/src/markdownLinks.test.ts | Test: vp test run packages/client-runtime/src/markdownLinks.test.ts

### T-03 Headless before/after evidence, PR, release and installed check
- AC: AC-01, AC-04, AC-05 | Files: ~/.specwithcode/m4/scratch/report-viewer-presentation/ | Test: node ~/.specwithcode/m4/scratch/report-viewer-presentation/shoot.mjs app.css

### T-04 Verify and close 0944
