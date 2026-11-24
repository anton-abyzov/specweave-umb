# 1451 parity: Claude desktop vs SpecWithCode (Sheets, Whiteboard, Documents)

November 23, 2026. Increment 1451, T-01 (AC-13). Clean-room: behaviour and architecture only. No code, assets or prompts copied.

## Method

- Target: `/Applications/Claude.app` version `6.28899.6` (the 1342 pass saw 5.11492.5). `app.asar` sha256 `4407fe8e7abe8452785b327ca68a6d0393c7c924391d94bccc73feef34e4c060`, `ion-dist.asar` sha256 `f0a85d25778a59c4ee8018c6c00500ed4a687a85ec5ca61f129b54265afe86d4`.
- Static only. REA 6.4.0 `analyze-javascript-application` on `app.asar` (`--integrity-policy record-and-continue`): Evidence `ev_0bb017a2d5ba38dfd9f32330dd3f9892d58a30536814551fae5ac1ac88052289`, 1,099 source files parsed, record at `~/.specwithcode/m4/scratch/2026-11-23-1451-rea/rea-app.json` (128 MB). Both ASARs were also extracted with `@electron/asar` to the same scratch folder (`app/`, `ion/`) and searched with grep from user-visible strings inward. The app was not launched; no credentials were read.
- Bundle paths below are relative to that scratch folder: `app/` = `app.asar`, `ion/` = `ion-dist.asar`. Message IDs are i18n keys in `ion/i18n/en-US.json`.
- SpecWithCode column: tag `v1.0.409` (released November 23, 2026), read with `gh api` at the tag: `apps/web/src/components/office/SheetView.tsx` (1,087 lines), `apps/web/src/components/files/hostFilePreview.ts`, `apps/web/src/components/files/OfficeDocumentPreview.tsx`, plus the 1451 spec's Problem section. The local checkout (1.0.330) was not touched.
- Public docs: [Sheets](https://support.claude.com/en/articles/18324300-get-started-with-claude-sheets), [Whiteboards](https://support.claude.com/en/articles/18324319-get-started-with-claude-whiteboards), [Docs](https://support.claude.com/en/articles/16923645-get-started-with-claude-docs), [Docs keyboard shortcuts](https://support.claude.com/en/articles/17458093).
- Hotkey references: [Excalidraw HelpDialog.tsx](https://raw.githubusercontent.com/excalidraw/excalidraw/master/packages/excalidraw/components/HelpDialog.tsx), [Excalidraw actions/shortcuts.ts](https://raw.githubusercontent.com/excalidraw/excalidraw/master/packages/excalidraw/actions/shortcuts.ts), [Google Sheets shortcuts](https://support.google.com/docs/answer/181110), [Excel shortcuts](https://support.microsoft.com/en-us/office/keyboard-shortcuts-in-excel-1798d9d5-842a-42b8-9c99-9b7213f0040f).

## Architecture findings

**Observed**

- Only two artifact types ship on disk: `app/resources/frame/types/slides.artifact.json` and `design.artifact.json` (manifest: `key`, `title`, `contract` 0.2.47, icon, tint, `artifact.prod.slug` UUID, `capabilities` with downloads, comments, room, db rules, mcp servers with named tools, feature flags). No `sheets`, `whiteboards` or `docs` manifest or folder.
- No spreadsheet engine or canvas library: zero non-i18n hits for `VLOOKUP`, `XLOOKUP`, `SUMIFS`, `roughjs`, `perfect-freehand` in `app/` or `ion/`. ProseMirror is present in the web bundle (84 files, for example `ion/assets/v1/cb3b658f1-fSJiZ6R2.js`), which is the composer editor and does not by itself show a Docs runtime.
- No Excalidraw or tldraw code. `excalidraw` appears once, as the `mcp.excalidraw.com` connector colour (`ion/assets/v1/c6d7d9bc6-R-Wu8EMG.js`); `tldraw` once, as a directory connector slug (`ion/assets/v1/ce76a1b9c-DtrC2aK1.js`).
- Sheets and Whiteboards are behind feature flags `sheets` and `whiteboards` (menu items "Claude Sheets" `+D5NDvRxBD`, icon Spreadsheet; "Claude Whiteboards" `N/mdsGoaWd`, icon Shapes) in `ion/assets/v1/c16f7df8c-BCJj0iYm.js`. A policy key `artifactsWhiteboardEnabled` (available since 6.6395.0, "public-undocumented", execution "server") is in `app/.vite/build/index.pre.js`. A telemetry event `frame_whiteboard_send` is in `app/resources/frame/shell/frame-shell-broker.js`.
- Docs, presentation, design and dashboard artifacts are told apart by server artifact slug UUIDs in the generic frame shell `app/resources/frame/shell/frame-shell-chrome.js`; a sheet product is detected the same way in `ion/assets/v1/shared-36-BYpoDCvt.js`.
- The frame runtime contract `app/resources/frame/runtime/contracts/0.2.96/index.json` lists capabilities a type can use, including `artifact`, `db`, `room`, `comments`, `downloads`, `mcp`, `paste`, `files`, `dictation`.
- One shared download menu in `frame-shell-chrome.js` labels formats: pptx, docx ("Editable .docx document" `3oKSHKnqBI`), xlsx ("Editable .xlsx spreadsheet" `CwU4POtknp`), csv ("Table data as plain text"), png, jpg, svg, pdf, html.
- Docs menu in the same file: Version history (`TkEsocawnt`), Export as Word (.docx) (`875ftL6j6E`), Export as PDF (`fNDQsG+UPR`), Export as Markdown (`l+2DTg5RQg`), Export to Google Docs (`sEX1rg+foX`), Notion.
- i18n only (no JS file uses it in the desktop bundle): "The document changed while you were restoring, so nothing was saved" (`I5bpYENFVB`), "Save as .csv file" (`iFjsFH3nb1`, used in `ion/assets/v1/c368fdb57-BsWNEijO.js`, context not read).
- Admin toggles: Sheets "spreadsheets with formulas and formatting that they and Claude edit together" (`o8wacF2+GU`); Docs "docs their team reads, comments on, and edits in place while Claude keeps them current" (`q5H9yU61S9`); "Claude Docs is off in your connectors, so Claude can't send this Doc from a task" (`vmp/2Nsotk`).
- `app/resources/bundled-skills/` ships `docx`, `xlsx`, `pptx`, `pdf` skills (file generation in the code sandbox), separate from the live artifact types.

**Inferred**

- High confidence: the Sheets, Whiteboards and Docs runtimes are fetched from the server and run inside the frame shell; they are not bundled (no manifests, no engines, no canvas code on disk). A slug alone would not prove this, since Slides has a slug and ships on disk.
- Medium confidence: types opt into download formats through `capabilities.downloads` (Slides declares `{}` and its formats are not visible).
- Medium confidence: the agent writes to these artifacts through the type's MCP-style tool list and `db`/`room` capabilities, and Docs is also exposed as a connector (`vmp/2Nsotk`). Tool names are not on disk.

**Unknown**

- Whether the server-side Whiteboard runtime is Excalidraw-based. The desktop bundle has no Excalidraw code, and the help page says boards cannot be imported from a file and export only as PNG, so no `.excalidraw` file format is exposed either way.
- Sheets formula engine and function count, and Sheets and Whiteboards hotkeys (not documented, not on disk).

## Parity table

Gap: **in 1451** = an AC covers it; **follow-up** = out of 1451 scope; **proposed add to AC-nn** = small, not yet in an AC; **none** = no gap.

### Sheets

| Behaviour or hotkey | Claude desktop | SpecWithCode 1.0.409 today | 1451 plan | Gap | Evidence (Claude) |
|---|---|---|---|---|---|
| Runtime | Server-delivered type, flag `sheets` | Bundled `SheetView` (viewer) | Bundled editor | none | `ion/assets/v1/c16f7df8c-BCJj0iYm.js` |
| Type in cells, formula bar | Yes; person and Claude in the same cells | No; formula bar shows, read-only | AC-01 | in 1451 | Sheets help page |
| Enter/Tab/Esc/F2/double-click/Delete | Not documented | No | AC-01 | in 1451 | not on disk |
| Arrow, Home/End, Page Up/Down navigation | Not documented for Sheets (a generic table view has them, `/gTTiQ7m9P` in `ion/assets/v1/shared-107-D8fgcL1q.js`) | Arrows only (`SheetView.tsx:360`) | AC-02 | in 1451 | not on disk for Sheets |
| Shift+arrow, Cmd/Ctrl+arrow, Cmd/Ctrl+A/C/X/V/Z/Y/B/I/U | Not documented | No | AC-02 | in 1451 | not on disk |
| Shortcut list Cmd/Ctrl+/ | Not documented for Sheets (Docs has it) | No | AC-02 | in 1451 | Docs shortcuts page |
| Formulas, cross-tab | Yes; formulas stay visible | Engine computes, read-only | AC-01 | in 1451 | Sheets help page |
| Function count | Not stated | Own engine | keep | none | Sheets help page |
| Formatting (bold, fill, number formats, borders) | Yes, floating format bar | Shows formats, no editing | AC-03 | in 1451 | Sheets help page; 1342 screenshots |
| Conditional formatting | Yes | No | Out | follow-up | Sheets help page |
| Dropdowns, checkboxes, person/date chips | Yes | No | Out | follow-up | Sheets help page |
| Merge, wrap, font size | Yes (1342 screenshots) | No | Not named | follow-up | 1342 `research-notes.md` |
| Insert/delete rows and columns, reference rewrite | Yes | No | AC-03 | in 1451 | Sheets help page |
| Tabs add/rename/delete | Yes | Tabs shown, not editable | AC-03 | in 1451 | Sheets help page |
| Sort, resize, reorder, hide columns | Yes | Has | keep | none | 1342 notes |
| Charts (bar, line, pie) | Yes | Has (Insert chart) | keep | none | Sheets help page |
| Undo/redo | Restore in version history; toast "Claude updated N cells, Undo" | No | AC-03 | in 1451 | Sheets help page; 1342 notes |
| Version history | Yes; restore drops later edits | No (git only) | Not named | follow-up | Sheets help page |
| Paste from Excel/Google Sheets | Yes | No | AC-04 | in 1451 | Sheets help page |
| Import CSV, Excel | Yes | `.xlsx` opens read-only in `SheetView` (`OfficeDocumentPreview.tsx`); no import into a Sheet | AC-06 | in 1451 | Sheets help page |
| Import Google Sheets | Yes | No | Out | follow-up | Sheets help page |
| Export .xlsx | Yes | No | AC-05 | in 1451 | `CwU4POtknp` in `frame-shell-chrome.js`; help page |
| Export .csv | Yes | No in the UI (Export HTML, Copy Markdown; the `OfficeDocumentPreview.tsx` header comment also claims CSV/TSV, but `SheetView.tsx` has no CSV action) | AC-05 | in 1451 | Sheets help page |
| Export PDF | Not yet | No | Out | none (parity) | Sheets help page |
| Open .xlsx and save back to the same file | No (import, then export) | No | AC-06 | in 1451 (ahead of Claude) | Sheets help page |
| Agent writes, landing highlight | Edits "outlined as they land"; red frame with a "Claude" tag | `sheet_write` replaces the file; no highlight | Not named | follow-up | Sheets help page; 1342 notes |
| Live co-editing, comments, sharing | Yes | No | Out | follow-up | Sheets help page |
| Pivot tables, macros, protected ranges | No | No | Out | none | Sheets help page |
| Size | At least 200,000 filled cells | Not measured | Not named | follow-up (perf check) | Sheets help page |

### Whiteboard

| Behaviour or hotkey | Claude desktop | SpecWithCode 1.0.409 today | 1451 plan | Gap | Evidence (Claude) |
|---|---|---|---|---|---|
| Runtime | Server-delivered type, flag `whiteboards` | None; `.excalidraw` opens as JSON text | Embedded Excalidraw, lazy chunk, offline | in 1451 | `c16f7df8c-BCJj0iYm.js`, `index.pre.js` |
| File format | Unknown, not exposed (no file import, PNG export only); no Excalidraw code in the desktop bundle | n/a | Plain `.excalidraw` (AC-08) | in 1451 (ahead) | bundle search; Whiteboards help page |
| Elements | Shapes, arrows, sections, pictures, videos; 1342 screenshots add sticky notes, pen, emoji | n/a | Excalidraw set: shapes, arrow, line, pen, text, image, frame, sticky note (N) | in 1451; emoji and video: follow-up | Whiteboards help page; 1342 notes |
| Sections | Yes | n/a | Excalidraw frames (F) | in 1451 | Whiteboards help page |
| Tool hotkeys | Not documented | n/a | AC-07 | in 1451 | not on disk |
| AC-07 hotkey list | n/a | n/a | Lists "D duplicate" | **spec error**: in Excalidraw D is diamond, duplicate is Cmd/Ctrl+D | Excalidraw `actions/shortcuts.ts` |
| Undo/redo, duplicate, group, zoom, Space-drag pan, ? help | Not documented | n/a | AC-07 | in 1451 | not on disk |
| Keys stay inside the editor | n/a | n/a | AC-07 | in 1451 | n/a |
| Autosave, conflict banner | Live server state | n/a | AC-09 | in 1451 | Whiteboards help page |
| Theme follows app | Unknown | n/a | AC-09 | in 1451 | n/a |
| Export PNG | Yes (Share > Export > PNG) | n/a | AC-09 | in 1451 | Whiteboards help page |
| Export SVG, file | No | n/a | AC-09 (SVG, `.excalidraw`) | in 1451 (ahead) | Whiteboards help page |
| Import from file | No | n/a | Any `.excalidraw` opens (AC-08) | in 1451 (ahead) | Whiteboards help page |
| Send to Lucid, Miro, Zoho Vani | Yes | n/a | Out | follow-up | Whiteboards help page |
| Board to doc or deck | Yes | n/a | Not named | follow-up | Whiteboards help page |
| Agent drawing | Claude draws shapes, arrows, sections; "Describe a change" box; drag a region to ask Claude | vskill `excalidraw-mcp` skill only | `whiteboard_write`/`whiteboard_read` (AC-10) | in 1451; on-canvas prompt and region ask: follow-up | Whiteboards help page; 1342 notes |
| Dictation, sketch input | Yes | n/a | Out | follow-up | Whiteboards help page |
| Live co-editing, follow a teammate | Yes | n/a | Out | follow-up | Whiteboards help page |
| Version history | Not documented | n/a | Not named | follow-up | Whiteboards help page |

### Documents

| Behaviour or hotkey | Claude desktop | SpecWithCode 1.0.409 today | 1451 plan | Gap | Evidence (Claude) |
|---|---|---|---|---|---|
| Runtime | Server-delivered "doc" type, told apart by slug | `.docx` read-only structured preview (`OfficeDocumentPreview.tsx`, no raw HTML) | Tiptap editor (AC-11) | in 1451 | `frame-shell-chrome.js` |
| Rich text: headings, lists, tables, links, images | Yes, plus doc tabs | Read-only | AC-11 | in 1451 (doc tabs: follow-up) | Docs help page |
| Text keys: Cmd+B/I/U, Cmd+Shift+S or X strike, Cmd+E code, Cmd+K link | Yes | No | AC-11 (B/I/U, links) | in 1451; code and strike keys: proposed add to AC-11 | Docs shortcuts page |
| Block keys: Cmd+Option+0-6 headings, Cmd+Shift+7/8/9 lists, Cmd+Shift+B quote, Cmd+Option+C code block, Tab/Shift+Tab indent | Yes | No | Not named | proposed add to AC-11 | Docs shortcuts page |
| Undo/redo Cmd+Z, Cmd+Shift+Z or Cmd+Y | Yes | No | Not named (Tiptap default) | proposed add to AC-11 | Docs shortcuts page |
| `/` block menu, `@` mention, `:` emoji | Yes | No | Not named | follow-up | Docs shortcuts page |
| Shortcut list Cmd/Ctrl+/ or ? | Yes | No | Not named | proposed add to AC-11 | Docs shortcuts page |
| F6 / Cmd+F6 toolbar focus | Yes | No | Not named | follow-up | Docs shortcuts page |
| Comments Cmd+Option+M | Yes | No | Out | follow-up | Docs shortcuts page |
| Autosave | Yes | No | Not named (AC-11 says Save) | proposed add to AC-11 | Docs help page |
| Export .docx | Yes | No | AC-11 | in 1451 | `875ftL6j6E` in `frame-shell-chrome.js` |
| Export PDF | Yes | No | AC-11 (`printToPDF`) | in 1451 | `fNDQsG+UPR` in `frame-shell-chrome.js` |
| Export Markdown | Yes | No | Not named | proposed add to AC-11 (cheap) | `l+2DTg5RQg` in `frame-shell-chrome.js` |
| Export to Google Docs, Notion | Yes | No | Out | follow-up | `sEX1rg+foX` in `frame-shell-chrome.js` |
| Open an existing .docx and save back | No file import documented (Google Doc copy only) | Preview only | AC-11 | in 1451 (ahead) | Docs help page |
| Version history, restore | Menu item and restore-conflict text in bundle; help page lists it only in a limitation | No | Not named | follow-up | `TkEsocawnt` (JS), `I5bpYENFVB` (i18n only) |
| Agent edits | Nothing locked; changes attributed; Claude says what changed; @Claude in a comment | n/a | `doc_write`/`doc_read` | in 1451; attribution and @Claude: follow-up | Docs help page |
| Comments, roles, sharing | Viewer, Commenter, Editor | No | Out | follow-up | Docs help page |
| Charts and diagrams in a doc | Yes, static | No | Not named | follow-up | Docs help page |
| Mobile editing | iOS and Android view and edit | Read-only views | Out | follow-up | Docs help page |

## Standard hotkeys people will expect

**Excalidraw** (built into the embedded editor; source: HelpDialog.tsx and actions/shortcuts.ts above). Tools: H hand, V or 1 select, R or 2 rectangle, D or 3 diamond, O or 4 ellipse, A or 5 arrow, L or 6 line, P or 7 draw, T or 8 text, 9 image, E or 0 eraser, F frame, K laser, N sticky note, B fill, I eyedropper, Q tool lock. Editor: Cmd/Ctrl+D or Alt-drag duplicate, Cmd/Ctrl+G group, Cmd/Ctrl+Shift+G ungroup, Cmd/Ctrl++ and - zoom, Cmd/Ctrl+0 reset zoom, Shift+1 fit all, Shift+2 zoom to selection, Cmd/Ctrl+/ or Cmd/Ctrl+Shift+P command palette, Alt+Z zen mode, Alt+R view mode, Alt+Shift+D dark mode, ? shortcut help, Shift+H and Shift+V flip, Cmd/Ctrl+[ and ] layer back and forward, to back and front Cmd+Alt+[ and ] on macOS or Ctrl+Shift+[ and ] elsewhere, Cmd/Ctrl+Shift+L lock element, Cmd/Ctrl+Shift+V paste as plain text, Cmd/Ctrl+F search, Cmd/Ctrl+' grid, Alt+S snap, Alt+/ stats, Cmd/Ctrl+Z undo, Cmd/Ctrl+Shift+Z redo, Space-drag or wheel pan.

**Excel** (Windows keys; macOS swaps Ctrl for Cmd where noted by Microsoft): arrows, Shift+arrows, Ctrl+arrows to the data edge, Ctrl+Shift+arrows, Tab/Shift+Tab, Enter/Shift+Enter, Esc, F2 edit, Delete clear, Home, Ctrl+Home, Ctrl+End, Page Up/Down, Ctrl+A, Shift+Space row, Ctrl+Space column, Ctrl+C/X/V, Ctrl+Alt+V paste special, Ctrl+Z, Ctrl+Y, Ctrl+B/I/U, Ctrl+D fill down, Ctrl+R fill right, Alt+Enter new line in cell (Option+Return on macOS), F4 absolute reference, Alt+= AutoSum (Shift+Cmd+T on macOS), Ctrl+; date, Ctrl+Shift+; time, Ctrl+Shift+1/4/5 number, currency, percent, Ctrl+- delete and Ctrl+Shift+= insert cells, Ctrl+F find, Ctrl+H replace, Ctrl+K link, Shift+F11 new sheet, Ctrl+Page Down/Up next and previous sheet, Ctrl+` show formulas.

**Google Sheets** (Ctrl on Windows/Linux, Cmd on macOS): navigation and editing as Excel, plus Ctrl+/ shortcut list, Ctrl+Shift+V paste values only, Ctrl+Enter fill selection, Alt+Shift+1-4 borders top/right/bottom/left, Alt+Shift+7 or Ctrl+Shift+7 outer border, Alt+Shift+6 remove borders, Ctrl+H replace (Cmd+Shift+H on macOS), Shift+F11 new sheet, Alt+Down/Up next and previous sheet (Option on macOS).

## Key gaps (sent to the lanes)

Sheets lane:
1. Claude Sheets: editable cells, cross-tab formulas, format bar, insert/delete, tabs, paste from Excel/Google, xlsx and csv export. All are in 1451 ACs. Our open-and-save-back of `.xlsx` is ahead of Claude.
2. Claude marks the range the agent is writing ("edits outlined as they land", red frame with a "Claude" tag) and toasts "Claude updated N cells, Undo". Not in 1451; follow-up unless cheap with the undo stack.
3. Follow-ups: conditional formatting, dropdowns, checkboxes, merge, wrap, version history, Google Sheets import. Claude has no PDF export either.
4. Claude's Sheets hotkeys are server-side and undocumented; use the Excel and Google Sheets list in parity.md as the AC-02 target. The 1.0.409 `OfficeDocumentPreview.tsx` header comment claims CSV/TSV export that `SheetView.tsx` does not have.

Whiteboard lane:
1. Claude's whiteboard format is not exposed: no file import, PNG export only, no Excalidraw code in the desktop bundle. Plain `.excalidraw` with PNG and SVG export puts 1451 ahead.
2. AC-07 says "D duplicate". In Excalidraw D is the diamond tool and duplicate is Cmd/Ctrl+D (or Alt-drag); test the real keys.
3. Claude elements: shapes, arrows, sections, images, video; sticky notes, pen, emoji in screenshots. Excalidraw has frames (F) and sticky notes (N); emoji and video are follow-ups.
4. Claude agent UX: a "Describe a change" box on the canvas and drag-a-region-to-ask. Follow-up. Send to Lucid/Miro and board-to-doc are follow-ups.

Documents lane:
1. Claude Docs exports .docx, PDF, Markdown, Google Docs, Notion. 1451 covers .docx and PDF; Markdown is a cheap proposed add.
2. Claude Docs documents a full shortcut set (support article 17458093): Cmd/Ctrl+/ or ? list, Cmd+B/I/U, Cmd+E code, Cmd+K link, Cmd+Option+0-6 headings, Cmd+Shift+7/8/9 lists, Cmd+Shift+B quote, Tab indent. Proposed add to AC-11 along with autosave.
3. Follow-ups: version history with restore, doc tabs, attributed agent edits, comments, `/` and `@` menus.
4. Claude has no import of an existing .docx; our open-and-save-back is ahead.

## Note for the 1451 owner

The spec's T-01 test expects `.specweave/increments/1451-office-in-specwithcode-editable-sheets-with-excel-import-and-export-and-an-excalidraw-compatible-whiteboard/reports/parity.md`. This task was read-only, so the report lives at `~/.specwithcode/m4/evidence/1451-office/parity/parity.md`; copy it there when recording T-01.
