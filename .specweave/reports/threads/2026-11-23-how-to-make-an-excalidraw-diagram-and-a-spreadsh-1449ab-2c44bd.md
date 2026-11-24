---
title: "How to make an Excalidraw diagram and a spreadsheet in SpecWithCode"
thread: "thread:delegated-task:command%3Amcp%3A0e842ec5-d023-44ab-bab9-2f0c26e73cc4%3Adelegate-task%3A7437b3e0-41f7-4c10-b5d1-814b346a09c8"
threadTitle: "How to make Excalidraw and spreadsheet artifacts"
savedAt: "2026-11-23T08:05:40.013Z"
date: November 23, 2026
machine: M5
installed: SpecWithCode 1.0.408 (latest release 1.0.409)
---

# How to make an Excalidraw diagram and a spreadsheet in SpecWithCode

**Short answer.** Spreadsheets are a built-in SpecWithCode artifact (`sheet_write` / `sheet_read`) and work in the installed 1.0.408. Releases 1.0.408 and 1.0.409 have no Excalidraw viewer or artifact: no release note, app source file or app tool mentions it, and the Whiteboard artifact from increment 1342 is still an unbuilt follow-up. The only places the app shows Excalidraw are lists of what is installed: Settings > Connections lists an `excalidraw` MCP server if one is configured, and the Skills settings list an Excalidraw skill if one is installed. Excalidraw diagrams come from the vskill skill `excalidraw-mcp`, which writes a `.excalidraw` file and a PNG. Both were made for real on M5 below.

| | Spreadsheet | Excalidraw diagram |
|---|---|---|
| Built into the app | Yes, a Sheet artifact | No, it comes from a skill |
| Tool or format | `sheet_write`, `sheet_read` → `.specweave/artifacts/<name>.sheet.json` | vskill `excalidraw-mcp` skill → `.excalidraw` file + PNG |
| Where it renders | The app's sheet viewer and the Artifacts shelf | excalidraw.com or the VS Code Excalidraw extension; the app shows the PNG, and opens `.excalidraw` as JSON text |
| Editing | Ask the agent (`merge: true`), or sort, resize, reorder, hide columns and Insert chart in the viewer | Ask the agent to change the skeleton and rebuild, or open the file at excalidraw.com |
| Export | Export HTML, Copy Markdown | `.excalidraw`, Obsidian `.excalidraw.md`, PNG |
| Minimum version | 1.0.309 for `sheet_write`; 1.0.407 for Export HTML; 1.0.408 for financial formulas (PMT and others) and `.xlsx` preview | Any version: the skill works outside the app |
| Works on M5 | Yes | Yes, after setup: install with `--force`, Python 3.10 or newer, Playwright |

## 1. Spreadsheet

### Prompts to copy

```text
Make a sheet called "monthly budget" with Category, Planned, Actual and Difference columns for Rent, Groceries, Transport, Subscriptions and Savings. Compute Difference and the totals with formulas, format money in USD, and add a bar chart of Actual spending.
```

```text
Update the "monthly budget" sheet: add a "Utilities" row with 150 planned and 165 actual, keep the totals as formulas, and check it with sheet_read.
```

```text
Make a loan sheet: $300,000 at 6.5% for 30 years. Show the monthly payment with PMT, total interest, and a line chart of the remaining balance by year.
```

### What happens

1. The agent calls `sheet_write` with tabs, cells (text starting with `=` is a formula), formats, styles and charts (bar, column, line, donut).
2. The app saves `.specweave/artifacts/<name>.sheet.json` in the project. The reply has a link that opens the sheet viewer. The sheet is also listed on the project's Artifacts shelf.
3. The agent calls `sheet_read` to see the computed values and any formula errors.
4. To edit, ask in chat. The agent writes again with `merge: true`, so only the cells you name change. In the viewer you can sort, resize, reorder and hide columns, and select a range and press **Insert chart**. Typing into cells by hand is not supported yet: the viewer's only text field is the chart title, and arrow keys only move the selection.
5. To export, press **Export HTML** (one self-contained file) or **Copy Markdown**. `sheet_write` cannot export `.xlsx` or CSV.

**Excel files.** From 1.0.408, opening an `.xlsx` file in the app's file viewer shows a read-only workbook preview. To get a real Excel file, ask: *"Write the same table to `budget.xlsx` with openpyxl, with totals as formulas."* The agent writes it with Python, and the app previews it.

### Verified on M5

- `sheet_write` through the installed 1.0.408 created `/Users/anton/Projects/github/specweave-umb/.specweave/artifacts/demo-monthly-budget.sheet.json`: 28 cells, 8 formulas, 1 chart, 0 errors.
- `sheet_read` returned Total Planned $4,170, Actual $4,245 and Difference ($75), all from formulas.
- The screenshot is the **Export HTML** output, not the in-app viewer. It was rendered headless from the app checkout at `9363b068a` (`exportSheetToStandaloneHtml`), not from the installed 1.0.408 bundle.
- A real `.xlsx` made with openpyxl went through the importer from the same checkout (`readXlsxWorkbook`). It returned 1 sheet, every cell and both `SUM` formulas, with no unsupported features.

![Sheet, light](/Users/anton/.specwithcode/m4/evidence/artifacts-howto/sheet-light.png)

Dark theme: `/Users/anton/.specwithcode/m4/evidence/artifacts-howto/sheet-dark.png`

## 2. Excalidraw diagram

### One-time setup on each machine (not installed on M5)

On M5, neither part is present. `ensure_mcp.py` reports `excalidraw MCP: NOT available here.`, and the skill is not in `~/.claude/skills`.

1. On M5: install the skill into the project: `cd /Users/anton/Projects/github/specweave-umb && vskill install anton-abyzov/vskill --skill excalidraw-mcp --agent claude-code --force`. Use `--global` instead to install it for every project. **`--force` is needed today.** Without it, vskill's scanner refuses the skill with `Blocking findings in 1 bundled file(s): scripts/ensure_mcp.py: CI-003 system() call (line 31); CI-003 system() call (line 53)`. A `--dry-run` passes, so it does not show this. Tested in `/Users/anton/.specwithcode/m4/scratch/2026-11-23-artifacts/install-test`: with `--force`, all 14 files landed in `.claude/skills/excalidraw-mcp`.
2. On M5: make sure Python 3.10 or newer is on hand. macOS's own `python3` is 3.9.6 and fails (see below). `uv` is installed and fetches 3.12 on demand.
3. For the PNG preview, the render script needs Playwright with Chromium and network access to esm.sh. `uv run --with playwright` covers Playwright. Chromium was already cached on M5.
4. Optional, for the live drawing in chat: `claude mcp add --transport http --scope user excalidraw https://mcp.excalidraw.com`. This registers the server for Claude Code on this machine; a new thread then sees the `mcp__excalidraw__*` tools. This check did not test how other providers pick it up. The file and the PNG are made without it.

### Prompts to copy

```text
Use Excalidraw: draw our checkout flow (Web app → Orders API → Payments, and Orders API → Database) and save it as docs/diagrams/checkout-flow.excalidraw. Lint it, render a PNG next to it and show me the PNG. Run the skill's Python scripts with uv run --python 3.12 (the macOS python3 is too old), and add --with playwright for the render.
```

```text
Update docs/diagrams/checkout-flow.excalidraw: add a "Notifications" box below Payments with an arrow labelled "receipt", re-lint, re-render the PNG.
```

```text
Draw this architecture as an Obsidian Excalidraw drawing (.excalidraw.md) in dark mode.
```

### What happens

1. The agent writes a skeleton JSON file and runs `excalidraw_lint.py`. The linter catches labels that overflow, shapes that collide and arrows that miss.
2. `excalidraw_build.py scene.json -o out.excalidraw` writes the real file. `--obsidian` writes an `.excalidraw.md` instead, and `--dark` makes a dark drawing.
3. `excalidraw_render.py out.excalidraw -o out.png` renders the file headless with Excalidraw's own `exportToSvg`, loaded from esm.sh, so it needs a network connection.
4. To edit, ask the agent to change the drawing and rebuild it, or open the `.excalidraw` file at excalidraw.com or in the VS Code extension. Saving a shareable link (`export_to_excalidraw`) uploads the drawing to excalidraw.com publicly, so the skill asks first.

### Verified on M5, with two problems

- **System Python fails.** macOS ships Python 3.9.6, and `excalidraw_build.py` stops with `TypeError: write_text() got an unexpected keyword argument 'newline'`, because that argument needs Python 3.10 or newer. It works with `uv run --python 3.12 --no-project python scripts/excalidraw_build.py ...`. This is a bug in the skill and should get its own fix.
- **Lint caught a cramped label.** The first layout failed lint with `R10-ARROW-LABEL: e1: label 'POST /order' ~97px on a 112px path`. Wider spacing let lint pass, but the label still touched the arrowhead in the PNG. Shortening it to "order" fixed that. Looking at the PNG is part of the check.
- The build produced 15 elements in `/Users/anton/.specwithcode/m4/scratch/2026-11-23-artifacts/checkout-flow.excalidraw`. The render needed `uv run --with playwright` and passed.

![Excalidraw checkout flow](/Users/anton/.specwithcode/m4/evidence/artifacts-howto/checkout-flow.png)

## Files

- `/Users/anton/Projects/github/specweave-umb/.specweave/artifacts/demo-monthly-budget.sheet.json`
- `/Users/anton/.specwithcode/m4/evidence/artifacts-howto/sheet-light.png`, `sheet-dark.png`, `sheet-light.html`, `sheet-dark.html`
- `/Users/anton/.specwithcode/m4/scratch/2026-11-23-artifacts/demo-budget.xlsx`
- `/Users/anton/.specwithcode/m4/scratch/2026-11-23-artifacts/flow.skeleton.json`, `checkout-flow.excalidraw`, `checkout-flow.png`

## Sources

- `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/tools.ts`, the `sheet_write` and `sheet_read` tools
- `repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.tsx`, the viewer: Insert chart, Export HTML, Copy Markdown
- `repositories/anton-abyzov/specwithcode/apps/web/src/components/files/hostFilePreview.ts`, which previews `.xlsx` and has no `.excalidraw` entry
- Release notes 1.0.406 to 1.0.409: Sheets features and native `.xlsx` preview, with no mention of Excalidraw
- Increment 1342 `spec.md`, which lists Whiteboard as a follow-up, out of scope
- `repositories/anton-abyzov/vskill/skills/excalidraw-mcp/SKILL.md` 1.2.0
