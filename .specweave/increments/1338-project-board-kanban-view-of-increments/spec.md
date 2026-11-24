# Project board: a Kanban view of increments in the SpecWithCode project panel

## Problem

Anton, November 14, 2026: "Is there an easy way to see the dashboard, like a Kanban board for a project, in case we use SpecWeave? Think about having a link to it ... maybe navigating directly from the SpecWithCode desktop application to it."

A board exists, but nobody reaches it from the app.

## Findings (November 14, 2026; CLI 3.1.21, app origin/main `4fdded03c`)

- **CLI.** `specweave dashboard` serves a local web app whose home page is a Work board with Backlog, In progress, Blocked, Review and Done columns and a detail panel (`repositories/anton-abyzov/specweave/src/dashboard/client/src/pages/work/WorkBoardPage.tsx`, rebuilt in 1150). It reads `metadata.json`, `spec.md`, `ledger.jsonl` and `.specweave/intents/board.jsonl`. `GET /api/work` for this project answered in 0.62 s with 684 items (11 backlog, 71 active, 37 blocked, 7 review, 558 done). It refreshes on file changes and every 15 s and calls GitHub only from the Connections page buttons; the old "dashboard polling burns the rate limit" note is stale. Capture: `reports/screens/cli-dashboard-work-board.png`.
- **CLI, other.** `specweave cards --md` prints one increment's checklist, `specweave project show` prints the hub, `specweave status` prints counts. None is a board, and there is no `board` or `ui` command.
- **App.** The plan card, AC chips and `LinkIncrementDialog` read increments through `projects.threadIncrementProgressRead` and `projects.incrementsList` (`apps/server/src/project/ThreadIncrementProgress.ts:832`: folder names from one readdir, each `metadata.json` parsed once until it changes). The list returns id, title and status only. The project panel has Threads, Designs, Library, PRs and Routines tabs (`apps/web/src/studio/projectPaneModel.ts`). Nothing lists all increments by state and nothing links to the CLI dashboard.
- **Docs.** spec-weave.com `docs/guides/dashboard.md` describes the CLI dashboard and its Work board.

Gaps: the board needs a terminal command and a browser tab; it looks like another product; its cards do not know the app's threads or pull requests; cards clip their text at 1600 px.

## Options considered

Mockups: `reports/board-options.html`.

- **A. Link out.** A "Board" menu item starts `specweave dashboard` and opens the browser. Smallest, but needs the CLI and a second server and has no threads or PRs. Rejected.
- **B. Board tab in the project panel.** Picked. One click, same look as the rest of the app, cards can carry PRs, threads and reports, works on every machine and on the phone's web view through the same RPC.
- **C. `specweave board`.** A terminal command that prints counts and a link into B. Follow-up, after B exists.

## Scope

In (first slice): a read-only Board tab in the project panel for projects that use SpecWeave, with Planned, Active, In review and Done columns built from files; search; a card opens its spec and its pull requests; a Board item in the project's More menu; headless captures.

Out, as follow-ups: thread chips on cards (from `thread_increment_links`) and report links; a Board link on the plan card and thread rows; `specweave board` in the CLI with a link into the app; refresh on file change instead of on open and on a timer; drag to change state; the intent board (`.specweave/intents/board.jsonl`); archived increments (`.specweave/archive`); other machines' checkouts.

## Acceptance Criteria

- [ ] AC-01: `projects.board` returns, for the project's planning root, one card per increment folder with id, title, status, column, task counts (total, done or skipped), a blocked flag, last update and up to 5 pull request links taken from the ledger. Columns: Planned (planned, backlog), Active (active, in-progress, paused), In review (ready_for_review, or not completed with every task done or skipped), Done (completed). Abandoned increments are left out. It reads files only: no network, no CLI.
- [ ] AC-02: The Done column returns the newest 30 by default (up to 300 on request) with the full count; other columns return every card. A query matches words in the folder name or title.
- [ ] AC-03: A board of 1,500 increments answers in under 1 s the first time and under 150 ms when nothing changed, measured in a test on a temp folder. Unchanged files are not re-read (mtime and size cache).
- [ ] AC-04: A project that uses SpecWeave shows a Board tab after Designs. Expanded, the panel shows four columns; in the narrow panel, the same cards as a list grouped Active, In review, Planned, Done. Each card shows id, title, progress, age, a Blocked mark and PR chips. A project without SpecWeave shows no Board tab (superseded by AC-08).
- [ ] AC-05: Clicking a card opens its `spec.md` in the app's file viewer; a PR chip opens the pull request; "Show more" pages a long column 40 at a time; "Show older" asks for more Done cards; the search box filters as typed.
- [ ] AC-06: The project's More menu has a Board item that opens the panel on the Board tab, expanded.
- [ ] AC-07: Headless captures of the Board tab, expanded and narrow, light and dark, with a 700-increment fixture, saved in `reports/screens/`.

- [ ] AC-08: Anton, November 14, 2026: "if the board is not enabled, the user could enable it". A code project without SpecWeave shows the Board tab with "Start a board for this project" and the same Set up SpecWeave control as project settings; after setup the cards appear. The personal project and a server too old to say have no tab.
- [ ] AC-09: "Make sure it's all clickable ... redirect to the appropriate thread ... not always a one-to-one mapping." A card with one thread opens that thread and keeps a Spec chip; a card with several or none opens its spec; every thread is its own line that opens it, most urgent first, three shown with "N more threads"; an open card with no thread has Start, Continue or Review and close, which puts a request in the coordinator's composer. Progress is the task meter and count plus each thread's state (Working, Answer needed ...).
- [ ] AC-10: "use the appropriate colors to show on which machine it's executed, and if there was a transition ... visualize it." When the project's threads run on more than one machine, each thread line names its machine in that machine's color and the card's leading edge takes the color of its lead thread's machine; a thread that moved shows "→ machine" (always, even on one machine) with the move in the tooltip. Threads served by other machines are included.
- [ ] AC-11: Anton on the `specweave dashboard` capture: "Why is it looking so weird ... make sure it's all consistent. The style must be consolidated." The local dashboard uses the Weave tokens and fonts the website and the app use (canvas `#f8f7f9` light, `#16131d` dark, iris accent, Schibsted Grotesk and JetBrains Mono bundled locally), follows the system dark mode, makes no external request, and its own headless board check still passes.

## Approach

1. `packages/contracts/src/projectBoard.ts`: `ProjectBoardInput`, `ProjectBoardCard`, `ProjectBoardResult`; `projects.board` added to the project workspace RPC group, the client permission table, authorization and instrumentation, the same places as `projects.incrementsList`.
2. `apps/server/src/project/ProjectBoard.ts`: `readProjectBoard(root, input)`. Folder names from one readdir; `metadata.json` through the existing cache; `spec.md` task headings and the ledger fold only for increments that are not completed, plus the Done cards actually returned (for their PR links), each cached by mtime and size. Done cards sort by `metadata.updated`, so no extra stat for the 500+ closed ones. Served by `ThreadIncrementProgressService`.
3. `apps/web/src/studio/projectBoardModel.ts` (pure: grouping, order, labels, paging) and `apps/web/src/components/studio/shell/BoardPane.tsx`; `board` added to `PROJECT_PANE_TABS`, hidden unless the project read reports `specweave`. The query refetches when the tab opens and every 30 s while it is visible.
4. More menu item in `ProjectMoreMenu.tsx`.
5. Fixture under `apps/web/tests/project-board/` for the captures.
6. Follow-ups after Anton's review of the first slice: `BoardThreads.tsx` joins threads to increments with the hooks the thread list uses (`useProjectThreadIncrementProgress` for this machine, `useSidebarThreadPlans` for the others) and `threadLocation` for where each runs; board styles moved to `shell/board.css`. In the specweave repository `src/styles/brand-tokens.css` now maps `--sw-brand-*` onto `design/weave/weave.css`, and the bundled fonts are the website's.

Rejected: embedding the CLI dashboard in a web view (second server, CLI dependency, different look); extending `projects.incrementsList` (older clients page it by 300 and its shape is used by the link dialog); a Blocked column (Anton asked for Planned, Active, In review, Done; blocked is a mark on the card).

Risks: `ProjectWorkspaceSurface.tsx` is already 2,400 lines, so the pane and its data hook live in their own files and the surface gains only the tab wiring. The shared ProjectWorkspace test fixture answers unknown queries with a project read, so the new hook needs its own mock there.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Native Board tab (option B) over linking out to the CLI dashboard → default.
- D-02 Four columns as Anton listed them; blocked and paused are marks on a card, not columns → default.
- D-03 No drag to change state; a card's actions open things or draft a request for the coordinator, and state still changes through the CLI and agents → default.
- D-05 The CLI dashboard stays as the terminal user's board and is restyled, not removed; the app's Board tab is the board for app users → default.
- D-04 Tab order: Threads, Designs, Board, Library, PRs, Routines → default. Designs stays right after Threads, which an existing test pins.
### Open
- none

## Tasks

### T-01 Board contract, file reader and RPC
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectBoard.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspaceRpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoard.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoard.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgressService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgress.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectWorkspace.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/feat-1338-project-board/repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectBoard.test.ts

### T-02 Board tab, cards and More menu item
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectPaneModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectPaneBar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectPaneBar.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectMoreMenu.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectMoreMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/panes.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/feat-1338-project-board/repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectBoardModel.test.ts src/components/studio/shell src/components/studio/ProjectWorkspace.threads.test.tsx src/themeContrastClasses.test.ts src/designTokens.guard.test.ts

### T-03 Headless captures of the board
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/index.html, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/fixture.css | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/feat-1338-project-board/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/project-board/vite.config.ts && node apps/web/tests/project-board/verify.mjs /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1338-project-board-kanban-view-of-increments/reports/screens

### T-05 Board cards open threads, show machines, offer setup
- AC: AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardThreads.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/board.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/panes.css, repositories/anton-abyzov/specwithcode/apps/web/src/index.css, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/vite.config.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/feat-1338-project-board/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/project-board/vite.config.ts && node apps/web/tests/project-board/verify.mjs /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1338-project-board-kanban-view-of-increments/reports/screens && cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectBoardModel.test.ts src/components/studio/shell/BoardPane.test.tsx src/designTokens.guard.test.ts

### T-06 Local dashboard on the Weave design system
- AC: AC-11 | Files: repositories/anton-abyzov/specweave/src/styles/brand-tokens.css, repositories/anton-abyzov/specweave/src/styles/brand-fonts.css, repositories/anton-abyzov/specweave/src/styles/fonts, repositories/anton-abyzov/specweave/src/dashboard/client/src/styles/globals.css, repositories/anton-abyzov/specweave/src/dashboard/client/src/pages/work/work-board.css, repositories/anton-abyzov/specweave/src/dashboard/client/src/pages/project-hub.css, repositories/anton-abyzov/specweave/docs-site/src/css/weave-bridge.css, repositories/anton-abyzov/specweave/scripts/e2e/brand-parity.mjs | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/feat-1338-project-board/repositories/anton-abyzov/specweave && npm run build:dashboard && node tests/dashboard/work-board.e2e.mjs

### T-04 Verify and close 1338
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: .specweave/increments/1338-project-board-kanban-view-of-increments/spec.md | Test: specweave verify 1338-project-board-kanban-view-of-increments
