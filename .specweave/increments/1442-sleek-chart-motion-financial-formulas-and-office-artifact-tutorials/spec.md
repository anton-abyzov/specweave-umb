# Sleek chart motion, financial formulas and Office artifact tutorials

## Problem

Increment 1438 shipped rich charts, an interactive sheet viewer and native `.xlsx`/`.docx` previews in app PRs #802 and #808. Anton looked at the result on November 22, 2026 and asked for a thorough review, sleeker animations, proof with charts and financial formulas, and tutorials with a narrated video.

Three gaps, read from `main` at `b7d49c635`:

1. **Motion is thinner than 1438 promised.** The 1438 spec names "bar grow, line draw, donut sweep". `apps/web/src/components/office/office.css` has one 220 ms fade on the whole plot and a width transition on bars. Rows are keyed `label:index`, so a sort remounts every row instead of moving it. Nothing reacts to the pointer except a native `<title>`.
2. **No financial functions.** `packages/shared/src/officeSheet/formula.ts` has 34 functions and none of `PMT`, `NPV`, `IRR`, `XNPV`. An imported workbook that uses them shows only Excel's cached numbers, and a `.sheet.json` cannot hold a loan schedule or an investment case that recomputes. The file is also 1,586 lines, over the repository's 1,500-line rule.
3. **No proof or teaching material.** There is one screenshot from November 20, no capture of the shipped build, no written tutorial and no video.

## Scope

In:
- A multi-agent review of all of 1438 (both PRs) on Claude Fable 5.2 at high effort, saved as a report, with confirmed defects fixed here or listed as open.
- Chart motion in the app and in the standalone HTML export: bars grow in sequence, columns rise from the baseline, the line draws itself over a soft area fill, the donut sweeps and its total counts up, rows glide to their new place on sort and filter, and the hovered mark stands out. All of it off under `prefers-reduced-motion: reduce` and under `animate: false`.
- 17 financial functions in a new module: `PMT`, `IPMT`, `PPMT`, `PV`, `FV`, `NPER`, `RATE`, `NPV`, `IRR`, `MIRR`, `XNPV`, `XIRR`, `CUMIPMT`, `CUMPRINC`, `SLN`, `EFFECT`, `NOMINAL`, plus the `#NUM!` error they need. Dates are Excel serial numbers or ISO `YYYY-MM-DD` text, which is what the `.xlsx` import produces.
- `formula.ts` back under 1,500 lines.
- Headless screenshots, a written tutorial and a narrated video.

Out:
- Multi-series, stacked, scatter and waterfall charts; inline cell editing; `.xlsx` and `.docx` export; `.doc.json`; Excalidraw. They stay on the 1438 roadmap.
- Date functions (`DATE`, `EDATE`, `YEARFRAC`), depreciation beyond `SLN`, bond functions, array formulas. Listed in the tutorial as not supported.
- Hosted sharing, uploads, auth or grant changes, migrations, deletions.
- Publishing the video anywhere.

## Acceptance Criteria

- [x] AC-01: `reports/review-fable-5.2.md` holds the review of #802 and #808: five dimensions, each finding verified by a second agent, with file and line, and a disposition (fixed here, open, refuted) for every finding.
- [x] AC-02: In the app a bar chart grows its bars in sequence, a column chart rises from the zero line (downward for negative values), a line chart draws its line and fades in an area fill, and a donut sweeps clockwise while its total counts up. The entry plays once per mount, not on selection or unrelated re-renders.
- [x] AC-03: Changing a chart's sort or filter moves bar rows to their new place instead of remounting them, and hovering a mark dims the others.
- [x] AC-04: With `prefers-reduced-motion: reduce`, or `animate: false` on the chart, no chart animation or transition runs and the final state shows at once, in the app and in the exported HTML. The export stays free of `<script>` and of network requests.
- [x] AC-05: The 17 financial functions return Excel's documented results to 1e-6 relative on the reference cases in `formulaFinance.test.ts`, return `#NUM!` when a solver does not converge or an argument is out of domain, propagate argument errors, charge the step budget for every pass over their cash flows, and never loop past a fixed iteration cap.
- [x] AC-06: `XNPV` and `XIRR` accept dates as serial numbers and as ISO `YYYY-MM-DD` text, so an imported `.xlsx` with date cells recomputes.
- [x] AC-07: `packages/shared/src/officeSheet/formula.ts` is under 1,500 lines and every pre-existing formula test still passes.
- [x] AC-08: Focused tests, web and server typecheck and the web build pass in the checks copy; PR CI is green; a cross-family review (GPT-6.2 Sol) ends in ship; the PR is merged and a release is requested.
- [x] AC-09: Headless screenshots of the four chart types, a loan schedule and an investment case with their formulas, a native `.xlsx` preview and one reduced-motion capture are saved under `reports/screenshots/`, each labelled with the build it shows.
- [x] AC-10: `reports/tutorial.md` teaches charts, spreadsheet tools, financial formulas and exports with the screenshots, and lists what is not supported. A narrated video (ElevenLabs voice, real-app capture, motion graphics) is saved under `reports/video/` and not published.

## Approach

1. Review first, in parallel with the build: a Workflow of five reviewers and five verifiers pinned to `b7d49c635`, read-only.
2. `packages/shared/src/officeSheet/formulaFinance.ts` (new): pure functions over plain numbers, and one `evaluateFinancial(name, args, spend)` entry. `formula.ts` hands it each argument as a value or as the filled cells of a range in reading order, and adds a `default:` branch. Solvers: Newton with a guarded step, then bisection on a bracket, 100 iterations at most, each pass charged to the step budget.
3. Bring `formula.ts` under the limit by moving the tokenizer and parser to `formulaParser.ts`. No behaviour change.
4. `SheetChart.tsx`, `office.css`: per-mark index and count as CSS custom properties drive staggered keyframes; `pathLength="1"` draws the line; one masked sweep reveals the donut; a small hook moves reordered rows (first, last, invert, play) with the Web Animations API; a count-up hook for the donut total. Both hooks do nothing under reduced motion.
5. `export.ts`: the same motion as CSS only.
6. Evidence: a demo `.sheet.json` (loan schedule, investment case, revenue charts) and a generated `.xlsx`, captured headless against a build of the merged commit, and against the installed release once it carries the change.
7. Tutorial and video: script locked first, ElevenLabs narration, real-app capture, HyperFrames for titles and callouts, rendered locally.

Rejected: a charting library (Chart.js, Recharts). The viewer and the export must share one renderer with no scripts in the export, and the current SVG is 450 lines. Rejected: the View Transitions API for reorder, since it snapshots the whole document.

Risks: SVG geometry transitions differ between Chromium and Safari, so entry motion uses transforms and dash offsets only. A release may not carry the change in time; captures then say "merged build".

## Decisions

### Asked
- none. Anton's November 22 message sets the work, and his standing approval of the same day (`feedback_use_recommended_options.md`) covers choices with a recommended option.
### Defaulted (change any before sw-do)
- D-01: Motion stays CSS and SVG with two small hooks, no animation library (reversible).
- D-02: Add `#NUM!` as an error code instead of folding solver failures into `#VALUE!`, to match Excel (reversible).
- D-03: Dates for `XNPV`/`XIRR` are serial numbers or ISO text; no date functions in this increment (reversible).
- D-04: The video is made and saved locally and is not posted; posting needs Anton's yes (reversible).
- D-05: Images and B-roll come from real-app capture and HyperFrames. No paid image or video generation unless a title card needs it, and then it is reported (reversible).
### Open
- none

## Tasks

### T-01 Review all of 1438 with Fable 5.2 and record every finding
- AC: AC-01 | Files: [.specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/review-fable-5.2.md] | Test: test -s .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/review-fable-5.2.md

### T-02 Financial functions in a new module, parser split, #NUM!
- AC: AC-05, AC-06, AC-07 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formulaFinance.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formulaFinance.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formulaParser.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formula.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/formula.test.ts] | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/officeSheet/formulaFinance.test.ts packages/shared/src/officeSheet/formula.test.ts

### T-03 Chart motion in the app
- AC: AC-02, AC-03, AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetChart.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/chartMotion.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/office.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetChart.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.tsx] | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/office/SheetChart.test.tsx apps/web/src/components/office/SheetView.test.tsx

### T-04 The same motion in the standalone HTML export
- AC: AC-04 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/export.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/export.test.ts] | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/officeSheet/export.test.ts

### T-05 Fix confirmed review findings that belong in this PR
- AC: AC-01 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet, repositories/anton-abyzov/specwithcode/apps/web/src/components/office, repositories/anton-abyzov/specwithcode/apps/web/src/components/files, repositories/anton-abyzov/specwithcode/apps/server/src/design/import, repositories/anton-abyzov/specwithcode/apps/server/src/project] | Test: grep -c "fixed in" .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/review-fable-5.2.md

### T-06 Checks, cross-family review, merge and release request
- AC: AC-08 | Files: [.specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/delivery.md] | Test: test -s .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/delivery.md

### T-07 Headless screenshots of charts, financial sheets and the native preview
- AC: AC-09 | Files: [.specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/screenshots] | Test: ls .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/screenshots/*.png

### T-08 Written tutorial and narrated video
- AC: AC-10 | Files: [.specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/tutorial.md, .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/video] | Test: test -s .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/tutorial.md && ls .specweave/increments/1442-sleek-chart-motion-financial-formulas-and-office-artifact-tutorials/reports/video/*.mp4
