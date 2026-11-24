# Rich charts, interactive spreadsheets, documents, and portable Office artifacts

## Problem

SpecWithCode's 1342 Office sheet viewer (`packages/shared/src/officeSheet/`, `apps/web/src/components/office/`) and 1435 research (`1435-artifact-storage-and-portable-documents`) leave four concrete gaps for users who want Claude Code-grade interactive charts, polished spreadsheets, Word/Office documents, and portable outputs:

1. **Static, single-series charts**: `SheetChart` only draws static `bar`, `line`, and `donut` SVGs from a raw `labels` + `values` range—no interactive parameters/filters, no group-by aggregation (`sum`/`avg`/`count`/`min`/`max`), no sorting, and no smooth motion with accessible `prefers-reduced-motion` support.
2. **Read-only, rigid spreadsheet presentation**: `SheetView` has 15 basic formula functions, no column sorting, no interactive column width resizing, no column organization (reorder/hide-show without breaking formula addresses), and no row-group expand/collapse.
3. **Concurrent write hazard (identified in 1435)**: `OfficeArtifacts.ts` uses a process-local `Map` with no cross-process lock and no `expectedRevision` compare-and-set, and `SheetFileView.tsx` overwrites via `projects.writeFile` without checking if an agent or another window changed the file.
4. **No portable standalone export or Markdown embedding**: Users cannot export a `.sheet.json` (with its charts and formatted tables) to a self-contained, zero-CDN, private-by-default HTML file or safe Markdown summary, and wider Office/Word/Excalidraw/motion capabilities lack a concrete compatibility and loss-disclosure matrix.

Clean-room shipped-product evidence from Claude.app `6.28899.2` (`rea analyze-javascript-application`, evidence `ev_c1eeb43dcc62f2ff66fcde996b0a6e6831b831e4553254bab1f6e962c5b12a3f`) confirms local zero-CDN chart/table/diagram libraries (`chart.js`, `gridjs`, `mermaid`), dedicated Word and Slides file viewers, an embed runtime, and a clean separation between local data-only artifacts and external Office bridges.

## Scope

In (Slice 1 — implemented in this increment):
- **Compatibility & architecture matrix** (`reports/compatibility-and-architecture-matrix.md`): complete phased roadmap covering Sheets, Rich Charts, Word/Documents (`.doc.json` / `.docx`), Slides (`.pptx`), Excalidraw (`.excalidraw`), and local Motion/Video (`hyperframes` + `ffmpeg`), with honest native-format fidelity and conversion-loss disclosures.
- **Rich interactive charts** (`officeSheet` schema, engine, MCP `sheet_write`/`sheet_read`, `SheetChart.tsx`, `office.css`):
  - Group-by aggregation (`sum`, `avg`, `count`, `min`, `max`) over label/category + value ranges.
  - Interactive parameters/filters (category/filter values + `topN` limit) and sorting (`none`, `value-desc`, `value-asc`, `label-asc`, `label-desc`), both declarative in `.sheet.json` and interactive in the chart toolbar.
  - Smooth CSS/SVG motion transitions (`bar` grow, `line` draw, `donut` sweep) with strict `@media (prefers-reduced-motion: reduce)` and explicit `motion: "off"` support.
- **Interactive, polished spreadsheets** (`officeSheet` formula/model, `SheetView.tsx`):
  - Expanded pure, deterministic formula functions: `MEDIAN`, `AVERAGEIF`, `SUMIFS`, `COUNTIFS`, `IFNA`, `CONCAT`, `LEFT`, `RIGHT`, `LEN`, `LOWER`, `UPPER`, `TRIM`, `ROUNDUP`, `ROUNDDOWN`, `POWER`, `MOD`, `INDEX`, `MATCH`, `VLOOKUP`.
  - Interactive column sorting (preserving header row and `topBorder` summary rows), drag-to-resize column widths (`tab.widths`), column organization (display order `tab.columnOrder` and visibility `tab.hiddenColumns` without mutating formula coordinates), and row-group expand/collapse (`tab.rowGroups`).
- **Revision-guarded conflict-safe persistence**:
  - Content-hash `revision` (`sha256` prefix) + cross-process lockfile in `OfficeArtifacts.ts` and optional `expectedRevision` compare-and-set in `writeSheetArtifact` / `sheet_write` / `sheet_read`.
  - Conflict detection in `SheetFileView.tsx` (reads current file before save or detects mismatch, shows non-destructive conflict banner to reload or overwrite).
- **Portable standalone HTML & safe Markdown export**:
  - Pure `exportSheetToStandaloneHtml` (single-file, zero-CDN, zero-`<script>`, strict HTML escaping, safe links, `prefers-reduced-motion` respected) and `exportSheetToMarkdown` (GFM tables + chart data summaries) wired to toolbar actions in `SheetView.tsx`.

Out (tracked in phased roadmap for Slice 2 & Slice 3):
- Native `.docx` / `.xlsx` binary import/export and `.doc.json` Word editor (Slice 2 — requires explicit loss-disclosure pipeline preserving original native files).
- Editable `.excalidraw` whiteboard viewer/editor and local HyperFrames MP4/WebM motion export bridge (Slice 3).
- Hosted public sharing, external document upload, auth/grant changes, data migrations, or destructive deletions (explicitly prohibited by 1342/1320 and user instructions).

## Acceptance Criteria

- [ ] AC-01: Compatibility & functionality matrix is saved in `reports/compatibility-and-architecture-matrix.md` covering Sheets, Charts, Word/Docs, Slides/PPTX, Excalidraw, and Motion/HyperFrames with REA evidence and honest native-format loss disclosures.
- [ ] AC-02: `SheetChart` supports `groupBy` (`sum`/`avg`/`count`/`min`/`max`), `sort` (`none`/`value-desc`/`value-asc`/`label-asc`/`label-desc`), `topN`, `filter` parameters, and `animate` / `prefers-reduced-motion: reduce` in both schema validation, pure `chartSeries` computation, MCP `sheet_write`/`sheet_read`, and interactive `SheetChart.tsx` controls.
- [ ] AC-03: Pure formula engine supports the 19 added functions (`MEDIAN`, `AVERAGEIF`, `SUMIFS`, `COUNTIFS`, `IFNA`, `CONCAT`, `LEFT`, `RIGHT`, `LEN`, `LOWER`, `UPPER`, `TRIM`, `ROUNDUP`, `ROUNDDOWN`, `POWER`, `MOD`, `INDEX`, `MATCH`, `VLOOKUP`) with strict determinism, cycle/step-budget safety, and zero I/O.
- [ ] AC-04: `SheetView` supports interactive column sorting (preserving header & summary rows), drag-to-resize column widths, column reorder & hide/show (`columnOrder`/`hiddenColumns` without breaking cell addresses), and row-group expand/collapse (`rowGroups`), persisted safely when writable.
- [ ] AC-05: `OfficeArtifacts.ts` enforces cross-process lockfile serialization and `expectedRevision` compare-and-set (returning a conflict error instead of silently overwriting), and `SheetFileView.tsx` surfaces concurrent-edit conflicts cleanly.
- [ ] AC-06: Pure `exportSheetToStandaloneHtml` and `exportSheetToMarkdown` produce private-by-default, zero-CDN, XSS-safe standalone HTML (no `<script>`, safe links, reduced-motion CSS) and clean GFM Markdown, wired to toolbar actions in `SheetView.tsx`.
- [ ] AC-07: Unit tests cover new formulas, chart group-by/filter/sort, conflict-safe writes, and HTML/Markdown exporters; full typecheck/tests pass inside `specweave-studio checks copy`; headless screenshot evidence is captured; independent cross-family adversarial review (GPT-6.2 Sol) is completed.

## Approach

Extend the existing 1342 Office owners in place without duplicating editors or adding heavy CDN dependencies:
1. `packages/shared/src/officeSheet/`:
   - `model.ts`: extend `SheetChart` (optional `aggregate`, `sort`, `topN`, `filterColumn`, `filterValues`, `animate`), `SheetTab` (optional `columnOrder`, `hiddenColumns`, `rowGroups`), and `sheetContentRevision()` helper. Keep strict validation and backwards compatibility with existing `.sheet.json` files.
   - `formula.ts`: add the 19 pure functions to the closed function dispatch table while preserving the 5M step limit and depth 64 guard.
   - `chart.ts`: extend `chartSeries` to apply optional filter, group-by aggregation, sorting, and `topN` deterministically.
   - `export.ts`: new pure module for `exportSheetToStandaloneHtml` (with inline theme CSS, SVG charts, and `@media (prefers-reduced-motion: reduce)`) and `exportSheetToMarkdown`.
2. `apps/server/src/project/OfficeArtifacts.ts` & `OfficeArtifactService.ts` & `apps/server/src/mcp/toolkits/office/`:
   - Add cross-process `.lock` file acquisition (matching `DesignStore.ts`) and `revision` return + `expectedRevision` compare-and-set check.
   - Expose new chart/tab fields and `expectedRevision` / `revision` in `sheet_write` and `sheet_read`.
3. `apps/web/src/components/office/`:
   - `SheetChart.tsx` & `office.css`: interactive filter pills, sort toggle, aggregation badge, smooth SVG animations disabled under `prefers-reduced-motion: reduce`.
   - `SheetView.tsx` & `SheetFileView.tsx`: column sort headers, drag resize handles, "Columns" organizer popover (reorder + hide/show), row-group expand/collapse gutter chevrons, "Export HTML" / "Copy Markdown" buttons, and revision-conflict banner on concurrent edit.

## Decisions

### Asked
- none (authorized under user's phased implementation directive from accepted research 1435)
### Defaulted (change any before sw-do)
- D-01: Keep `.sheet.json` data-only and zero-CDN; use pure CSS/SVG motion with `@media (prefers-reduced-motion: reduce)` rather than external JS runtime scripts in exported HTML (reversible).
- D-02: Implement revision guard via deterministic content hash (`sha256` 16-hex prefix) + cross-process lockfile so existing `.sheet.json` files need zero schema migration (reversible).
- D-03: Scope Slice 1 to rich charts, interactive spreadsheets, conflict-safe saves, and portable HTML/Markdown export; track Word/DOCX, native XLSX, Excalidraw, and HyperFrames video bridge as Slice 2/3 in the matrix (reversible).
### Open
- none

## Tasks

### T-01 Author compatibility & functionality matrix with REA evidence
- AC: AC-01 | Files: [.specweave/increments/1438-rich-charts-interactive-spreadsheets-documents-and-portable-office-artifacts/reports/compatibility-and-architecture-matrix.md] | Test: test -s .specweave/increments/1438-rich-charts-interactive-spreadsheets-documents-and-portable-office-artifacts/reports/compatibility-and-architecture-matrix.md

### T-02 Extend officeSheet model, formula engine, chart aggregation/filter/sort, and portable exporters
- AC: AC-02, AC-03, AC-06 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/model.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formula.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/chart.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/export.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/index.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/officeSheet.test.ts] | Test: pnpm --filter @specweave-studio/shared test src/officeSheet/officeSheet.test.ts

### T-03 Add cross-process lockfile and expectedRevision compare-and-set to OfficeArtifacts and MCP office tools
- AC: AC-02, AC-05 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/project/OfficeArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/OfficeArtifacts.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/OfficeArtifactService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/officeTools.test.ts] | Test: pnpm --filter @specweave-studio/server test src/project/OfficeArtifacts.test.ts src/mcp/toolkits/office/officeTools.test.ts

### T-04 Upgrade SheetChart, SheetView, SheetFileView, and office.css for interactive charts, spreadsheet UX, conflict guard, and portable export
- AC: AC-02, AC-04, AC-05, AC-06 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetChart.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetFileView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/office.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.test.tsx] | Test: pnpm --filter @specweave-studio/web test src/components/office/SheetView.test.tsx

### T-05 Verify full checks, capture headless visual proof, run cross-family GPT-6.2 Sol review, merge, and request release
- AC: AC-07 | Files: [.specweave/increments/1438-rich-charts-interactive-spreadsheets-documents-and-portable-office-artifacts/reports/verification-and-review.md] | Test: specweave-studio checks run -- pnpm typecheck

