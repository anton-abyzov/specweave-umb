# Readable report tables

## Problem

A Markdown report's comparison table is unreadable in the document reader. Five prose-heavy columns sit in a frame about 670 px wide inside a reader about 1380 px wide, and identifiers break into two- to four-character pieces (`sw:` / `gril` / `l`, "intervie" / "w"). Evidence: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-3f4ae815-383c-4812-922a-76f34149dd94.png` (installed 1.0.105) and the read-only research at `/Users/antonabyzov/.specwithcode/m4/evidence/report-readability-20261027/findings.md`.

The causes are in `apps/web/src/index.css` (main `0d085d49f4`):

- The whole report page, tables included, is capped at the prose measure (`.report-document-page`, line 1218; `--report-measure: 36rem`, line 712).
- The report table rule replaces the chat table's `min-width: max-content` with `min-width: 100%` (line 1499).
- Report cells use `white-space: normal; overflow-wrap: anywhere` (line 1521), and in the expanded state the chat rule's `overflow-wrap: anywhere` (line 1845) applies. With `anywhere`, a column's minimum width is one character, which the chat table's own comment (line 1802) warns against.
- The report frame is `overflow: hidden` (line 1494).

Agents also write dense comparisons as tables of paragraphs, which no layout can make readable.

A second report shows the same rules on a table of file paths (screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-8465dc78-6cec-4486-ac4f-912e8976371d.png`, "Home cleanup and remaining work"). Its four columns are two of absolute paths, which render as file-link chips, then Bytes and a prose Reason. Measured on the actual report (`/Users/antonabyzov/.specwithcode/m4/evidence/home-cleanup-20261027-final/report.md`, read locally, never staged in the repo) on main:

- The frame stays at the prose measure (574 px) while the table is 851 px, so it scrolls even in a 1966 px reader.
- Reason gets the leftover 80 px, so every row is 195 px tall.
- The page scrolls sideways at 390 px.
- The chips are not the cause: each is 18 px tall, `inline-flex`, with no min-height or aspect ratio.
- The left clip in the screenshot is the frame scrolled sideways: by trackpad, by find, or by the browser revealing a focused chip (339 px at 390 px). At `scrollLeft` 0 the first column is whole.

Head `2a59a6dcbb` (the fix for the first screenshot) removed the word splits and the sideways page scroll, but its 60rem cap still left Reason 116 to 139 px wide and rows 130 to 173 px tall.

## Scope

In:

- Report tables in the document reader and in every viewer that shows a report page (report reader, Library, Files shelf, linked file pane).
- The agent presentation guidance for comparisons.

Out:

- Chat-reply tables.
- HTML reports.
- Pane resizing.
- Rewriting existing reports.
- The `html-report` skill outside this repo.
- Installed acceptance (it follows a release).

## Acceptance Criteria

- [ ] AC-01: A report table cell wraps only between words. A column never narrows below its longest word, and inline code in a cell breaks only at its own spaces, so a command wraps but no identifier, path or word splits across lines, at 2400, 1440, 1100 and 390 px and at 200% zoom.
- [ ] AC-02: A report table uses the reader's width beyond the prose measure, up to the room beside the outline, centered on the page. Paragraphs keep the prose measure. A cell's text wraps by 28rem and never narrows below 14rem (or 30% of a narrow reader), so no line in a table grows long and a prose column beside wide file chips stays a line or two tall. A file chip or token longer than 28rem keeps its whole width.
- [ ] AC-03: A table that does not fit its room scrolls horizontally inside its frame. The page never scrolls sideways. The scroll region can be reached with the keyboard, shows a visible focus ring, and scrolls with the arrow keys.
- [ ] AC-04: Nothing about the content changes. Copy as Markdown and Copy as CSV return the same cell text, file links in cells stay links, and the expand control and light and dark themes still work.
- [ ] AC-05: The agent presentation guidance tells agents to write a comparison as a table of short cells, with each item's detail in a section below it.
- [ ] AC-06: The home cleanup table (two columns of path chips, Bytes, Reason) fits without scrolling when the reader has room, with rows of at most 48 px. With the thread open at 1440 px and at 200% zoom its rows are at most 70 px, and at 390 px at most 140 px. In every view the first and last columns are fully reachable, the arrow keys scroll to the last column, no chip is truncated and the page does not scroll sideways.

## Approach

1. In `apps/web/src/index.css`, report cells use `white-space: normal; overflow-wrap: normal; word-break: normal` in both expand states, with no truncation. Inline code in a table renders each word as its own box (`InsideMarkdownTable` context in `MarkdownTable.tsx`, read by the inline code renderer in `ChatMarkdown.tsx`). In a report cell the boxes are `nowrap` and the code wraps normally, so code breaks only at its spaces, never at a dash or slash. The boxed code carries `data-path-wrap`. Conversation find already joins such text, and report find (`findTextRanges`) now joins it too, so both finds still match a phrase across the boxes. Report find otherwise keeps its rules: it still searches diagram text, counts overlapping matches and keeps document order. The frame's border and radius move from the table container to its scroll root. Keyboard focus draws an outline on the scroll root, because the root's `overflow: hidden` clips the viewport's ring utilities and the viewport's scroll fades mask its edges. `.report-document-page` gets `min-width: 0`, so beside the outline a table with a long value scrolls in its frame instead of widening the page.
2. The reader body (`.report-reader-body`, and the linked file pane `[data-report-file-pane]`) becomes an inline-size query container named `report-reader`. Inside it, every report table container becomes a one-track grid, `minmax(max-content, 1fr)`, with `justify-content: center`. Its scroll root's `max-width` is the room: `100cqi - outline - 2 × page inline padding`. A small table keeps the page width, a wide one grows to its natural width up to the room, and both stay centered on the page.

   Chrome ignores `max-width` on table cells when sizing columns (probe at `/Users/antonabyzov/.specwithcode/m4/scratch/report-tables-1102/probe2.mjs`), and ignores `calc-size()` in a cell's `min-width`. So each th and td wraps its content in one box, `<span class="chat-markdown-cell">` (`ChatMarkdown.tsx`). In chat the box is `display: contents` and changes nothing. In a report it is a block with `min-width: calc-size(max-content, min(size, 14rem, 30cqi))` and `max-width: calc-size(min-content, max(size, 28rem))`, which Chrome honors on a block inside a cell. The box is a span so selection copy serializes cells as before (a `DIV` would add a line break between cells).
3. `STUDIO_PRESENTATION_INSTRUCTIONS` in `apps/server/src/provider/RuntimeInstructions.ts`: "comparisons a table" becomes a table of short cells with each item's detail below it. The length cap in the test is raised for that sentence alone.
4. Regression fixture: `apps/web/tests/report-readability` gains a comparison document modeled on the first screenshot (five columns, a two-column table, a long-token table and a two-column command table) and a home cleanup document: the second screenshot's table, sanitized, with the same columns, cell lengths and path chips, home folder moved to `/Users/example`. `verify.mjs` checks word, code-token and identifier integrity, frames between the page width and the room, lines no longer than 28rem unless one word is, untruncated chips, first and last columns reachable, row heights, prose widths, page versus frame scroll, keyboard scrolling to the last column with an unmasked focus ring, and copy output (Markdown and CSV distinct). It runs at 2400, 1440 (thread open and hidden), 1100 and 390 px and at 200% zoom, light and dark.

Rejected:

- Smaller type for tables. Readability gets worse.
- Breaking identifiers to avoid scrolling. That is the defect.
- A full-width page with each prose child capped. It changes every viewer's layout.
- Centering with transforms. They give fractional offsets and blurry text.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 (superseded by D-05): Tables of one or two columns stay at the prose measure.
- D-02: Long digests and URLs in table code stay whole and scroll inside the frame, instead of wrapping. Reversible.
- D-03: New increment, child of 1035 (closed). Report reader styling has no open owner. 1074 stays separate.
- D-04: Inline code in a table cell wraps at its own spaces, not only as a whole. CSS alone cannot stop a break after a hyphen, so the renderer boxes each word, only inside tables (chat-reply tables included, with no visual change there). Copy, prose code and find are unchanged; find joins the boxes as it joins a wrapped path. Without it, a two-column table of commands scrolled even with a wide reader (fresh review M1). Reversible.
- D-05: Frames grow to the room for every report table, and each cell's box bounds its lines (28rem) instead of the frame being capped by column count. The column-count caps kept the home cleanup table at 960 px, so its Reason column stayed 116 to 139 px and rows 130 to 173 px. The 28rem box keeps a label and paragraph table from producing long lines, which was D-01's reason. Reversible.
- D-06: The floor for a cell's text is 14rem (30% of a narrow reader). With a 10rem floor the five-column comparison still scrolled at 1440 px with the thread open, with 130 px rows. With 14rem it scrolls there with 86 px rows (it fit at `2a59a6dcbb`), and the home cleanup table's rows are 65 px. Reversible.
### Open
- none

## Known limits

- The word-split check in `verify.mjs` reads one text node at a time, so a word split across a `<wbr>` or across bold and plain text is not detected.
- The expand toggle changes nothing visible in a report: both states get the same cell rules. Chrome already ignored the collapsed state's cell caps before this change.
- External link text keeps its per-character break hints, so a long URL in a cell wraps.
- Library, Files shelf and ThreadArtifacts viewers share these rules. A fresh review probed the reader and the linked pane, but the fixture drives only the reader.
- At 390 px, focusing a file chip in a column past the frame's edge scrolls the frame to reveal it (364 px for the Destination chip). That is the browser's focus reveal, the same as on main; the first column comes back with the arrow keys or a scroll.
- `calc-size()` needs Chrome 129 or later; Electron 44 ships Chrome 140. A browser without it drops both box limits, and cells size as at `2a59a6dcbb`.
- HTML reports are out of scope and unchanged: the app shows them sandboxed and does not restyle them. The home cleanup `report.html` sets `td,code{overflow-wrap:anywhere}` and `.report{max-width:1000px}` itself, so in the app its paths split mid-name (`concert_v` / `2_workflow.js`) and Bytes splits (`14,95` / `1`) in 12 to 14 of 14 code cells, with 51 px rows wide and 136 to 170 px at 390 px, where its own page scrolls sideways (`/Users/antonabyzov/.specwithcode/m4/evidence/1102-readable-report-tables/screenshot-8465dc78/html-path/`). The `html-report` skill template has no such rule; the agent added it. A guidance line for the skill (outside this repo) is proposed in the report, not made here.

## Tasks

### T-01 Report table layout
- AC: AC-01, AC-02, AC-03, AC-04, AC-06 | Files: apps/web/src/index.css, apps/web/src/components/MarkdownTable.tsx, apps/web/src/components/ChatMarkdown.tsx, apps/web/src/components/ChatMarkdown.output.test.tsx, apps/web/src/components/chat/reportOutline.ts, apps/web/src/components/chat/reportOutline.test.ts, apps/web/src/components/find/conversationFind.logic.ts | Test: headless `apps/web/tests/report-readability/verify.mjs`, `vp test run apps/web/src/components/ChatMarkdown.output.test.tsx`, web production build

### T-02 Comparison guidance for agents
- AC: AC-05 | Files: apps/server/src/provider/RuntimeInstructions.ts, apps/server/src/provider/RuntimeInstructions.test.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/server/src/provider/RuntimeInstructions.test.ts`

### T-03 Table regression fixture and evidence
- AC: AC-01, AC-02, AC-03, AC-04, AC-06 | Files: apps/web/tests/report-readability/hostFiles.ts, apps/web/tests/report-readability/verify.mjs | Test: `node apps/web/tests/report-readability/verify.mjs /Users/antonabyzov/.specwithcode/m4/evidence/1102-readable-report-tables/<head>` (headless, 2400/1440/1100/390 px, 1440 px with the thread hidden, 200% zoom, light and dark)

### T-05 Correct table-row test typing
- AC: AC-04 | Files: apps/web/src/components/ChatMarkdown.output.test.tsx | Test: focused output test and web typecheck; exact-head review

### T-04 Verify and close 1102
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: `specweave verify 1102`, fresh-context review, `specweave complete 1102` after installed acceptance on the release that carries it
