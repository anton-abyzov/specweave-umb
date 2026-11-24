# Office artifacts: sheets, whiteboards, data, slides and dashboards on one shared design system

## Problem

SpecWithCode can show a report, an HTML page or an inline visual, but it has no working documents. A person who asks for a budget, a financial statement, a comparison table with charts, a process map or a deck gets a Markdown table or a one-off HTML page: nothing recalculates, nothing can be edited in place, and a chart is a picture.

On November 10 to 13, 2026 the Claude desktop app shipped Sheets, Whiteboards and Data artifacts, plus Meetings in beta, next to Slides and Design. The owner asked (November 14, 2026) for the same class of artifacts in SpecWithCode, on one design that every project can reuse, with charts that are easy to make from the app, usable by any model with Claude as the default, and both powerful and safe.

Evidence is in `reports/research-notes.md`: the public posts, the owner's eight screenshots, the two finance posts and what the shipped Claude desktop bundle contains.

## What the shipped Claude app shows (clean-room findings)

Read with REA 6.4.0 from `/Applications/Claude.app` 5.11492.5, bundle files only. No code, asset or prompt is copied; this is behaviour only.

Observed:

- An artifact type is a small versioned app. The bundle ships two, `slides` and `design`, each with a manifest (`<type>.artifact.json`), a page, a runtime and its own agent instructions file.
- The manifest declares what the type may use: downloads, comments, a shared room, a small database with read and write rules per path, assets, the user's profile, named connector tools (Slides lists two Google Drive tools) and feature flags. A type with no entry for a capability does not get it.
- One artifact is content files only (Slides keeps an index file and one file per slide). The agent writes those files; the runtime is read-only to it.
- Artifact pages run inside a separate frame shell with a broker between the page and the app.
- Bundled chart, table and diagram libraries exist for generic HTML artifacts.

Inferred (medium confidence): Sheets, Whiteboards and Data follow the same type contract. Their names are in the web bundle, their runtimes are not, so they are delivered from Anthropic's servers at run time.

Unknown: the sheet formula engine, the whiteboard document format, live data refresh and everything server-side in Meetings.

Answer to "does REA work for this": yes for the architecture (type, manifest, capabilities, content files, per-type agent instructions, broker), which is what we need to design ours. No for the Sheets and Whiteboard internals, because they are not on disk. We do not need them: ours is built from the behaviour in the screenshots.

## Product design

One family, "Office artifacts". Each artifact is a JSON file in the project, rendered by SpecWithCode's own viewer, made and changed through MCP tools that every provider gets.

| Kind | What it is | Slice |
|---|---|---|
| Sheet | Workbook with tabs, formulas, number formats, dropdown chips, links and charts bound to ranges | 1 (this increment) |
| Dashboard (Data) | Tiles (number, chart, table) fed by sheets or by saved read-only connection queries, with source and refresh time on each tile | 2 |
| Whiteboard | Canvas with sections, shapes, sticky notes, arrows and a legend | 3 |
| Slides | 16:9 deck from the same blocks (text, table, chart, image) | 4 |
| Meetings | Not a call bot. A meeting is an input: a transcript the assistant turns into a sheet, board or notes | later, own increment |

Shared by every kind:

- File: `.specweave/artifacts/<slug>.<kind>.json`, with `v`, `kind`, `title`, optional `designSystem` id and the content. It is a project file, so it shows on the artifacts shelf and in the Library, travels with the project and needs no hosted page (reports stay in SpecWithCode).
- One theme resolver. An artifact names a design system (`.specweave/design/systems/<id>/system.json`); the resolver turns its colour and type tokens into the variables every Office renderer uses (surface, text, grid line, accent, chart series). With no system named, the app theme is used. A sheet, its charts, a dashboard and a deck in one project therefore look like one product, and another project reuses the same system by id.
- Charts are one block type (`bar`, `line`, `donut`) bound to a range, used by sheets now and by dashboards and slides later. A chart title is a sentence that states the finding.
- Tools are provider-neutral: `sheet_write` and `sheet_read` now; `whiteboard_*`, `dashboard_*`, `slides_*` later. `sheet_read` returns computed values and errors so any model can check its own work. Nothing depends on a Claude-only feature. Claude stays the default because the project's default model is unchanged.
- In the app: a card in the reply, an entry on the shelf, a viewer with a formula bar, tabs and charts, and "Insert chart" on a selected range.

Personal finance (the two X posts): that feature is a read-only bank connection plus small cards (donut with legend, budget bars, bills list, calendar heat view). It is not code in artifacts. In SpecWithCode it belongs to Percy and the personal data permission as one more read-only source per machine; its cards are the chart blocks above. A bank aggregator needs a contract and a server-held secret, so the first step there is statement import (CSV, OFX) into a sheet. Own increment.

## Security design

Rule: an Office artifact is data, never code. Power comes from the tools and the formula language; safety comes from the app enforcing every limit, the same for every model.

- S-01 Data only. Sheet, whiteboard, slides and dashboard files are validated against a schema and drawn by the app's own components. No HTML, no script, no `eval`, no template strings. Unknown fields are dropped on read.
- S-02 Formula interpreter. Pure, no I/O, a closed function list. Limits: 200,000 cells per workbook, 2,000 characters per formula, nesting depth 64, an evaluation step budget per workbook. A cycle yields `#CYCLE!`; an unknown function `#NAME?`. No function reads a file, a URL, the clock of another machine or another workbook.
- S-03 Files. Tools write only `.specweave/artifacts/` in the caller's own project. The server builds the path from a slug; a caller never passes a path. Writes are atomic, capped at 2 MB, refused in plan mode and in approval-required threads without approval, the same as report saving. One project cannot read another project's artifacts.
- S-04 Links. Only `http`, `https` and `mailto`, opened through the existing external-link path. No `javascript:`, `file:` or `data:`.
- S-05 Code artifacts stay separate. A page with script (`html_render`, a future app artifact) runs in the existing sandboxed frame with an opaque origin: scripts and forms only, no same-origin, no access to the app, cookies, storage, project files, other threads or the network by default.
- S-06 Capabilities are declared and granted. A code artifact that needs more names it: network hosts, a read-only connection tool, a folder. The host broker checks the sender frame, validates each request against a schema and checks the grant before acting. A changed artifact that asks for more is asked again.
- S-07 One prompt style. Every grant uses the in-thread access card (`AccessRequestCard`, raised by `AccessGate.ensureAccess`): the subjects with their scope, a one-line reason, Deny, Allow for this session, Always allow on this machine, and where to take it back in Settings. New subject kinds: artifact network host, artifact data source, artifact folder. Nothing is granted silently, and no model can grant for itself.
- S-08 Never reachable from an artifact: secrets and environment variables, Keychain, provider tokens, the app database, the shell, other projects. Live data reaches a dashboard only through the server, which runs a saved read-only tool call with the viewer's grant and keeps credentials on the server side.
- S-09 Import and export. Spreadsheet import runs in a worker with size and expansion limits; macros and external links are dropped. CSV export guards against formula injection.
- S-10 Same for every model. Enforcement lives in the server and the renderer, never in a prompt. Every provider gets the same tools, limits and prompts; runtime instructions only describe them.
- S-11 Meetings, when planned: explicit consent of everyone recorded, local transcript, no silent capture.

Slice 1 implements S-01 to S-04 and S-10 in full. S-05 already holds for `html_render`. S-06 to S-09 and S-11 are the design for later slices and ship with the first feature that needs them.

## Scope

In (slice 1):

- Sheet document model, formula engine and number formats in shared code.
- Chart blocks bound to ranges, drawn as SVG.
- `sheet_write` and `sheet_read` MCP tools for every provider.
- Sheet card in the reply, shelf and Library entry, viewer with tabs, formula bar, formatted cells, dropdown chips, links and charts.
- "Insert chart" from a selected range in the viewer.
- Shared Office theme resolver fed by a design system.
- Runtime instructions and docs for the tools.

Out (named follow-ups, each its own increment): cell editing by hand, undo history, xlsx and CSV import and export, comments and sharing, Whiteboard, Slides, Dashboard with live connections and the capability grants (S-06, S-07), statement import and a finance source for Percy, Meetings, iOS and Android renderers.

Skip for good: a hosted share page, a call-joining bot, copying any Claude runtime.

## Acceptance Criteria

- [ ] AC-01: A workbook with several tabs evaluates formulas with cell and range references, references to another tab, arithmetic, comparison, text joining and the functions SUM, AVERAGE, MIN, MAX, COUNT, COUNTA, COUNTIF, SUMIF, IF, AND, OR, NOT, ROUND, ABS and IFERROR. Errors show as `#DIV/0!`, `#NAME?`, `#REF!`, `#VALUE!` and `#CYCLE!` and spread to dependents.
- [ ] AC-02: A three-statement example (income statement, balance sheet, cash flow across four quarters) computes the right totals, and changing one input changes every dependent total.
- [ ] AC-03: Number formats render currency, percent, thousands separators, fixed decimals and negative amounts in parentheses.
- [ ] AC-04: The formula limits of S-02 hold: an over-limit workbook or formula is refused with a message that names the limit, and evaluation always ends.
- [ ] AC-05: `sheet_write` creates or replaces a sheet artifact in `.specweave/artifacts/` of the caller's project, validates it, refuses paths outside that folder, plan mode and oversize input, and returns the file and a summary. `sheet_read` returns the computed values and errors of a range.
- [ ] AC-06: The two tools are offered to every provider with the same schema, and no code path depends on the provider.
- [ ] AC-07: A sheet made by a tool call shows as a card in the reply and as a Sheet on the artifacts shelf, and opens in the viewer with tabs, a formula bar that shows the selected cell's formula, column letters and row numbers.
- [ ] AC-08: A bar, line or donut chart bound to a range draws from the computed values, shows value labels, and redraws when the source cells change.
- [ ] AC-09: In the viewer, selecting a range and choosing Insert chart adds a chart to the sheet and saves it to the file.
- [ ] AC-10: The viewer takes its colours and type from the shared Office theme: the artifact's design system when it names one, otherwise the app theme, in light and dark.
- [ ] AC-11: Links open only for `http`, `https` and `mailto`; a file with script or unknown fields renders as plain data.
- [ ] AC-12: Headless screenshots of the card, the viewer with a financial statement and the chart tab, light and dark, are in `reports/`.

## Approach

All product paths are under `repositories/anton-abyzov/specwithcode/`.

1. `packages/shared/src/officeSheet/`: `model.ts` (schema, limits, A1 helpers, validation), `formula.ts` (tokenizer, parser, evaluator, dependency order, cycle detection), `format.ts` (number formats), `chart.ts` (chart block, series from a range), `theme.ts` (Office theme from a design system or the app theme), `index.ts`. No new dependency: the engine is about 600 lines and a closed function list is a security property (S-02). Rejected: HyperFormula (GPL or paid licence), SheetJS and Univer (size, and a larger surface than slice 1 needs).
2. `apps/server/src/mcp/toolkits/office/`: `tools.ts`, `handlers.ts`, `handlers.test.ts`, following the report toolkit. Register in `McpHttpServer.ts` and add the names to the presentation map, the tool list test, the read-only lists (`sheet_read` only) and the instructions.
3. `apps/web`: `components/office/SheetView.tsx` (grid, formula bar, tabs), `SheetChart.tsx` (SVG), `SheetCard.tsx`; a `sheet` kind in `threadArtifacts.ts` and `studio/projectArtifacts.ts` with icon, label and body case; file recognition by the `.sheet.json` suffix; i18n phrases. The viewer reads with `projects.readFile` and Insert chart saves with `projects.writeFile`.
4. Docs: `docs/internals/agent-instructions.md` and the runtime instructions.

Risks: the web tests run under the React Compiler from `apps/web`; every `tx()` string needs phrases; a new tool name must be added in about nine places or `core.test.ts` fails.

## Review

Adversarial review by Meta Muse Wonderful (`muse-wonder-1.0`), asked for by the owner: one round on the security design, then the PR at its exact head.

## Decisions

### Asked
- D-01 Does REA work for this? → Yes for architecture, no for the server-delivered Sheets and Whiteboard internals (owner asked, answered above).
- D-02 Any model must be able to build these, Claude primary (owner, November 14, 2026) → provider-neutral MCP tools, project default model unchanged.
- D-03 Charts easy to make from the app (owner) → chart blocks plus Insert chart in the viewer, in slice 1.

### Defaulted (change any before sw-do)
- D-04 Artifacts are project files under `.specweave/artifacts/` → reaches the shelf and travels with the project (reversible).
- D-05 Own formula engine, closed function list → no new dependency (reversible; an engine can be swapped behind `evaluateWorkbook`).
- D-06 Meetings is not built as a call-joining bot → transcript as input, own increment (reversible).
- D-07 Finance is a Percy data source, starting with statement import → own increment (reversible).
- D-08 Slice order: Sheet, Dashboard, Whiteboard, Slides (reversible).

### Open
- none

## Tasks

### T-01 Sheet model, formula engine and number formats
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/model.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formula.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/format.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/index.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formula.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/format.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/officeSheet

### T-02 Chart blocks and the shared Office theme
- AC: AC-08, AC-10 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/chart.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/theme.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/chart.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/theme.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/officeSheet

### T-03 sheet_write and sheet_read tools for every provider
- AC: AC-05, AC-06, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/handlers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/core.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/claudeReadOnlyMcpTools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.ts, repositories/anton-abyzov/specwithcode/docs/internals/agent-instructions.md | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/mcp/toolkits

### T-04 Sheet card, shelf kind and viewer
- AC: AC-07, AC-08, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetChart.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/threadArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadArtifacts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/artifactShelf.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/office src/studio/projectArtifacts.test.ts

### T-05 Insert chart from a selected range
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/insertChart.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/insertChart.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/office

### T-06 Headless screenshots, light and dark
- AC: AC-12 | Files: .specweave/increments/1342-office-artifacts-sheets-whiteboards-data-slides-and-dashboards-on-one-shared-design-system/reports/ | Test: ls .specweave/increments/1342-office-artifacts-sheets-whiteboards-data-slides-and-dashboards-on-one-shared-design-system/reports/*.png

### T-07 PR, Muse Wonderful review, merge and release request
- AC: AC-06 | Files: .specweave/increments/1342-office-artifacts-sheets-whiteboards-data-slides-and-dashboards-on-one-shared-design-system/reports/review.md | Test: gh pr view --repo anton-abyzov/specwithcode --json state,mergedAt

### T-08 Verify and close 1342
- AC: AC-12 | Files: .specweave/increments/1342-office-artifacts-sheets-whiteboards-data-slides-and-dashboards-on-one-shared-design-system/reports/ | Test: specweave verify 1342-office-artifacts-sheets-whiteboards-data-slides-and-dashboards-on-one-shared-design-system
