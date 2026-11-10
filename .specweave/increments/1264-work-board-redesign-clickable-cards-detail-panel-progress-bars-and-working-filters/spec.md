# Work board redesign: clickable cards, detail panel, progress bars and working filters

## Problem

On November 10, 2026 Anton opened the SpecWeave dashboard (`specweave dashboard`, Work board page) on the specweave-umb project and called it unreadable. His screenshot shows:

- Card titles and descriptions are cut off at the right edge of every column.
- Each column's scrollbar sits on top of its cards.
- Only the title text of a card opens anything, and what opens is a small form with two numbers. The spec, acceptance criteria, tasks, evidence and ledger history need a second page.
- Progress is a 3px line with 12px text.
- The page has three filters (agent, done window, text). There is no filter by state, verification, type or priority, no sort, and the filters reset the headline numbers' meaning: the tiles count every item while the columns count the filtered ones.
- An increment lands in Blocked for a stale claim with no reason shown, so "33 blocked" cannot be checked against the files.
- Acceptance criteria count only ticked checkboxes, so an increment whose tasks are all done still reads 0/7.

## Scope

In: the Work board page of the local dashboard (client and its `/api/work` data), a detail panel, filters, a list view, motion, and the headless end-to-end check.

Out: the other dashboard pages (Timeline, Evidence, Project hub and the diagnostics pages), tracker sync, and any change to how increment state is stored.

## Acceptance Criteria

- [ ] AC-01: At 1440px and 1024px widths no card text is clipped by its column, and no scrollbar overlaps a card. At 390px the page does not scroll sideways outside the board.
- [ ] AC-02: Clicking anywhere on a card, or pressing Enter on it, opens a detail panel for that item. The panel's address (`?item=`) reopens the same panel after a reload, and Escape closes it.
- [ ] AC-03: For an increment the detail panel shows the rendered spec, every acceptance criterion with its state, every task with status, owner and evidence, the verification report, the agents and models that worked on it, the ledger timeline, the latest handoff and the folder path on disk.
- [ ] AC-04: Every card shows a task progress bar at least 6px tall with the percentage and done/total counts. Each column header and the page header show aggregate progress for the visible items.
- [ ] AC-05: The board filters by text, state, agent, verification, type, priority and done window, and sorts by update time, ID and progress. Filters live in the address, a "Clear" control resets them, and every count on the page (tiles, column headers, result count) is computed from the same filtered set.
- [ ] AC-06: A ledger event, a spec edit or a verify report written on disk changes the open board and the open detail panel within 8 seconds, without a reload.
- [ ] AC-07: Every card in Blocked states why (paused, blocked tasks or stale claims, with counts), and the state of each card equals what `projectIncrement` derives from `metadata.json` and `ledger.jsonl`.
- [ ] AC-08: Acceptance-criteria counts on cards and in the panel use the ledger-derived status (`deriveAcStatus`), the same rule `specweave verify` uses.
- [ ] AC-09: Cards, panel, progress bars and counters animate with Motion; with `prefers-reduced-motion: reduce` nothing moves and all content is still present.
- [ ] AC-10: A list view shows the same filtered items as rows with sortable columns, and a column of the board renders at most 40 cards until "Show more" is pressed, so 500 increments stay responsive.
- [ ] AC-11: Moving an item to another state still works by drag and drop and by a keyboard-reachable control, and creating an intent, recording a setup and linking a session still work.

## Approach

1. Server: `projectIncrement` adds `type`, `priority`, `project`, `createdAt`, `path`, `stateReason` and ledger-derived ACs. `getIncrementDetail` adds the ledger `timeline`, per-AC covering tasks and the folder path. No new store; every read is from the increment folder.
2. Client model: `pages/work/board-model.ts` holds pure filter, sort, group and aggregate functions, unit-tested under `tests/unit/dashboard/`.
3. Client UI: `pages/work/` gets the board page, card, detail panel, list view, a small markdown renderer and its stylesheet. `WorkPage.tsx` is replaced; the Sessions route keeps its content in `SessionsPage.tsx` and opens the same panel.
4. Motion: the `motion` package (Motion for React) for layout, presence, springs and counters, inside `MotionConfig reducedMotion="user"`.
5. Graphics: vector artwork drawn in code (weave backdrop, empty states, progress ring), so it is sharp at any zoom and follows the brand tokens. No raster assets are added to the npm package.
6. `tests/dashboard/work-board.e2e.mjs` is updated to drive the new board headless and save screenshots.

Rejected: a virtualised list library (a 40-card page per column is enough and keeps layout animation simple); a markdown dependency (the spec subset is small and the package should not grow).

Risk: the bundle grows by the Motion runtime. It ships prebuilt in `dist/dashboard` and loads only in the dashboard.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 State rules stay as they are (stale claims count as Blocked); the card now states the reason.
- D-02 The per-card state dropdown moves into the detail panel; drag and drop stays on the card.
- D-03 Artwork is code-drawn vector, not generated raster: no Kie.ai key exists on this machine, and vector suits a data screen.
### Open
- none

## Tasks

### T-01 Projection: filter fields, state reason, derived ACs, timeline
- AC: AC-03, AC-07, AC-08 | Files: src/dashboard/server/data/work-projection.ts, src/dashboard/work-types.ts, tests/unit/dashboard/work-board.test.ts | Test: npx vitest run tests/unit/dashboard/work-board.test.ts

### T-02 Board model: filter, sort, group, aggregate
- AC: AC-05, AC-10 | Files: src/dashboard/client/src/pages/work/board-model.ts, tests/unit/dashboard/board-model.test.ts | Test: npx vitest run tests/unit/dashboard/board-model.test.ts

### T-03 Board page, cards, filters, list view and motion
- AC: AC-01, AC-04, AC-05, AC-09, AC-10, AC-11 | Files: src/dashboard/client/src/pages/work/WorkBoardPage.tsx, src/dashboard/client/src/pages/work/work-board.css | Test: npm run build && node tests/dashboard/work-board.e2e.mjs

### T-04 Detail panel
- AC: AC-02, AC-03, AC-06 | Files: src/dashboard/client/src/pages/work/DetailPanel.tsx, src/dashboard/client/src/pages/work/Markdown.tsx | Test: npm run build && node tests/dashboard/work-board.e2e.mjs

### T-05 Headless check, before and after screenshots, release
- AC: AC-01, AC-02, AC-06, AC-09 | Files: tests/dashboard/work-board.e2e.mjs, CHANGELOG.md | Test: node tests/dashboard/work-board.e2e.mjs
