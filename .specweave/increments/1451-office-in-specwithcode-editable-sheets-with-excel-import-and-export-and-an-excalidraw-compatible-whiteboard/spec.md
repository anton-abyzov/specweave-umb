# Office in SpecWithCode: editable sheets with Excel import and export, and an Excalidraw-compatible whiteboard

## Problem

On November 23, 2026 the owner asked where the editor is for sheets and diagrams. There is none. In 1.0.408/409 a Sheet (`sheet_write`, `.specweave/artifacts/<name>.sheet.json`) opens in a viewer: you can sort, resize, reorder and hide columns and insert a chart, but you cannot type into a cell, format, add rows, undo, or export to Excel (only Export HTML and Copy Markdown). `.xlsx` files preview read-only. Excalidraw has no support in the app at all: a `.excalidraw` file opens as JSON text, and diagrams come only from the vskill `excalidraw-mcp` skill, which needs `--force` to install and Python 3.10 (evidence: `.specweave/reports/threads/2026-11-23-how-to-make-an-excalidraw-diagram-and-a-spreadsh-1449ab-2c44bd.md`). Increment 1342 named all of this as follow-ups (cell editing, undo, xlsx/CSV import and export, Whiteboard).

Claude desktop ships Sheets and Whiteboards that a person edits directly beside the chat (1342 `reports/research-notes.md`). The owner wants the same inside the SpecWithCode desktop app on macOS, Windows and Linux: files that open in Excel and Excalidraw unchanged, the editing hotkeys people already know, and Word documents too.

## Scope

In:
- **Sheet editor.** Type in cells and the formula bar, Excel hotkeys, formatting bar, insert and delete rows and columns, tabs (add, rename, delete), undo and redo, copy and paste with Excel and Google Sheets (TSV and HTML clipboard), a New sheet button.
- **Excel compatibility.** Open any `.xlsx` in the editor and save it back as `.xlsx`; import `.xlsx` and `.csv` into a Sheet; export a Sheet as `.xlsx` (formulas and cached values, number formats, bold/italic/fill, column widths, several tabs) and `.csv`.
- **Whiteboard.** A Whiteboard artifact stored as a standard `.excalidraw` file, edited in the embedded Excalidraw editor (MIT) with all of Excalidraw's own tools and hotkeys, autosave with conflict handling, theme follows the app, export PNG, SVG and `.excalidraw`, fully offline. Any `.excalidraw` file in a project opens in it. Agent tools `whiteboard_write` and `whiteboard_read` for every provider.
- **Word documents.** Open a `.docx` in a rich-text editor (the app's existing Tiptap), save back to `.docx`, New document, export `.docx` and PDF; agent tools `doc_write` and `doc_read`.
- **Behaviour parity check against Claude desktop** with REA (clean-room: behaviour only, no code, assets or prompts copied).

Out (named follow-ups): real-time co-editing between people, comments and sharing, Slides and Data/Dashboard artifacts, mobile editors (iOS/Android keep the read-only views), Excel macros, pivot tables and conditional formatting, `.xls`/`.doc` legacy formats.

## Acceptance Criteria

- [ ] AC-01: In a Sheet a person can select a cell, type a value or a formula (Enter commits and moves down, Tab moves right, Esc cancels, F2 or double-click edits in place, Delete/Backspace clears), and the result recalculates and is saved to the file; the change survives an app restart.
- [ ] AC-02: Sheet hotkeys work on macOS (Cmd) and Windows/Linux (Ctrl): arrows and Shift+arrows, Cmd/Ctrl+arrow to the data edge, Cmd/Ctrl+A, C, X, V, Z, Shift+Z / Y, B, I, U, Home/End, Page Up/Down; an in-app shortcuts list (Cmd/Ctrl+/) shows them. Each is covered by a Playwright test.
- [ ] AC-03: The formatting bar sets bold, italic, underline, alignment, fill, number format (number, currency, percent, text, decimals) and borders; rows and columns can be inserted and deleted and formulas referring to moved cells update; tabs can be added, renamed and deleted; undo/redo covers every edit.
- [ ] AC-04: Copying a range to Excel or Google Sheets and pasting from them keeps values and the grid shape (TSV plus HTML table on the clipboard).
- [ ] AC-05: Export a Sheet as `.xlsx` opens in Microsoft Excel and LibreOffice with the same values, formulas, number formats, styles, widths and tabs; export `.csv` gives one tab's values. A round trip (Sheet → xlsx → import) keeps cells, formulas and formats; checked by a test against LibreOffice headless recalculation.
- [ ] AC-06: Opening a `.xlsx` file from the project opens it in the editor; Save writes a valid `.xlsx` back to the same path (features the editor does not model are kept or the person is told before saving); importing `.csv` and `.xlsx` into a new Sheet works from the Artifacts shelf.
- [ ] AC-07: A New whiteboard button creates `.specweave/artifacts/<name>.excalidraw`; it opens in the embedded Excalidraw editor with Excalidraw's tools and hotkeys (V, R, D, O, A, L, P, T, E, H, 1-9/0, Cmd/Ctrl+Z, Shift+Z, D duplicate, Alt-drag, Shift-constrain, Cmd/Ctrl+G group, ?, zoom keys, Space-drag pan); typing in the editor never reaches the app's own shortcuts.
- [ ] AC-08: The whiteboard file is byte-compatible with excalidraw.com: a file saved by the app opens there unchanged, and a file made there opens and saves in the app without losing elements, files (images) or app state that Excalidraw itself keeps.
- [ ] AC-09: Whiteboard edits autosave (debounced) with a revision check; a change on disk while editing shows the same reload/keep banner as Sheets; theme follows the app (light/dark); export PNG, SVG and `.excalidraw` work; the editor loads and draws with no network (fonts and assets bundled).
- [ ] AC-10: `whiteboard_write` takes a skeleton (shapes with labels, arrows with from/to, text, zones), lays out bound text and arrow bindings correctly (no empty boxes), and `whiteboard_read` returns elements and labels; both work for every provider and are listed in the agent instructions.
- [ ] AC-11: A `.docx` opens in a rich-text editor (headings, bold/italic/underline, lists, links, tables, images); Save writes a `.docx` that Word and LibreOffice open with the same content; New document and Export PDF work; `doc_write`/`doc_read` tools exist.
- [ ] AC-12: The editors build and pass their tests on macOS, Windows and Linux CI (windows-tests label), and the desktop app on each OS opens a sheet, a whiteboard and a document (headless captures in `reports/`).
- [ ] AC-13: A parity report from REA on the installed Claude desktop lists each Sheet and Whiteboard behaviour and hotkey with ours beside it; every gap is either fixed here or named as a follow-up.
- [ ] AC-14: Security: files are parsed as data only (no HTML, script or eval from file content; Excalidraw embeddables and links off by default, images only as data URLs from the file), zip inputs are size- and entry-bounded like the existing OOXML reader, and new third-party code is listed in `THIRD_PARTY_NOTICES.md`.

## Approach

Three lanes that touch separate folders, built in parallel in app-made worktrees on m4 (Use worktrees is on there; the M5 checkout is held by 1448).

- **Lane S (sheets):** extend the existing viewer, keeping its formula engine, charts and design system. `packages/shared/src/officeSheet/` gains an edit model (cell input, structural ops with reference rewriting, an undo stack of patches); `apps/web/src/components/office/SheetView.tsx` is split (it is near the 1,500-line limit) into grid, editor, formatting bar and keyboard modules. xlsx writing is our own on `jszip` (already a dependency) next to the existing reader `apps/server/src/design/import/xlsxImport.ts`; a server RPC writes files through the same guarded host-file path as the preview.
- **Lane W (whiteboard):** embed `@excalidraw/excalidraw` (MIT) lazily in its own chunk; serve its fonts and assets from the app bundle (`EXCALIDRAW_ASSET_PATH`), never a CDN; keep `serializeAsJSON` output as the file. Keyboard events stay inside the editor's container. Agent tools port the skeleton builder from vskill `skills/excalidraw-mcp/scripts/excalidraw_build.py` to TypeScript on the server so the file is correct without a browser.
- **Lane D (documents):** reuse Tiptap (already a dependency); `.docx` read via the existing `docxImport.ts`, write via a new OOXML writer on `jszip`; PDF through Electron's `printToPDF`.
- Shared: file routing (`apps/web/src/components/files/hostFilePreview.ts`), Artifacts shelf kinds and New buttons, agent instructions (`docs/internals/agent-instructions.md`).

Rejected: a third-party spreadsheet (Univer, Fortune-sheet) would drop our formula engine, charts and theming and add megabytes; SheetJS from npm is outdated, its current build is off-registry; writing our own whiteboard would never match Excalidraw's hotkeys and details.

Risks: Excalidraw bundle size (lazy chunk, measure); CSP and fonts offline; xlsx fidelity for files with features we do not model (keep unknown parts on save, warn); Windows clipboard formats.

## Review

Adversarial review on Gemini 4 Neon, then GPT-6.2 Sol (decision_adversarial_reviewer_model.md).

## Decisions

### Asked
- D-01 Build editors inside SpecWithCode, Excel- and Excalidraw-compatible, plus Word → yes, plan and implement fully (owner, November 23, 2026).
### Defaulted (change any before sw-do)
- D-02 Whiteboard = embedded Excalidraw editor (MIT), file format = plain `.excalidraw` (reversible).
- D-03 Sheet editor extends our own SheetView; the `.sheet.json` format stays the source for agent sheets, `.xlsx` is edited in place when the person opens one (reversible).
- D-04 Our own xlsx/docx writers on jszip, no new spreadsheet library (reversible).
- D-05 Build on m4 in three parallel worktrees, one PR per lane, release after each merge (reversible).
### Open
- none

## Tasks

### T-01 REA parity pass on Claude desktop
- AC: AC-13 | Files: .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/parity.md | Test: test -s .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/parity.md

### T-02 Sheet edit model: cell input, structural ops with reference rewrite, undo stack
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/edit.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/edit.test.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/packages/shared exec vitest run src/officeSheet/edit.test.ts

### T-03 Sheet editor UI: in-cell and formula-bar editing, hotkeys, formatting bar, tabs, shortcuts list
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/, repositories/anton-abyzov/specwithcode/apps/web/tests/office-sheets/ | Test: node repositories/anton-abyzov/specwithcode/apps/web/tests/office-sheets/shoot.mjs .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/sheets

### T-04 Clipboard interop with Excel and Google Sheets
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/sheetClipboard.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/sheetClipboard.test.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/web exec vitest run src/components/office/sheetClipboard.test.ts

### T-05 xlsx and csv writer, import, open-and-save-back for .xlsx files
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/design/import/xlsxExport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/design/import/xlsxExport.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/files/hostFilePreview.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/server exec vitest run src/design/import/xlsxExport.test.ts

### T-06 Whiteboard editor: embedded Excalidraw, offline assets, autosave, conflicts, theme, export
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/, repositories/anton-abyzov/specwithcode/apps/web/tests/office-whiteboard/ | Test: node repositories/anton-abyzov/specwithcode/apps/web/tests/office-whiteboard/shoot.mjs .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/whiteboard

### T-07 whiteboard_write and whiteboard_read tools
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/whiteboard.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/whiteboard.test.ts, repositories/anton-abyzov/specwithcode/docs/internals/agent-instructions.md | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/server exec vitest run src/mcp/toolkits/office/whiteboard.test.ts

### T-08 Word documents: Tiptap editor, docx writer, PDF export, doc tools
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/document/, repositories/anton-abyzov/specwithcode/apps/server/src/design/import/docxExport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/document.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/server exec vitest run src/design/import/docxExport.test.ts

### T-09 Artifacts shelf: New sheet, whiteboard, document; import; routing by file type
- AC: AC-06, AC-07, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/nativeArtifacts.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/web exec vitest run src/components/studio/shell

### T-10 Security and notices
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/THIRD_PARTY_NOTICES.md, .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/security.md | Test: grep -q excalidraw repositories/anton-abyzov/specwithcode/THIRD_PARTY_NOTICES.md

### T-11 Cross-platform CI and desktop captures on macOS, Windows, Linux
- AC: AC-12 | Files: .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/ | Test: gh pr checks --repo anton-abyzov/specwithcode

### T-12 Review, merge, release, verify and close
- AC: AC-01, AC-05, AC-08, AC-12 | Files: .specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/review.md | Test: specweave verify 1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard
