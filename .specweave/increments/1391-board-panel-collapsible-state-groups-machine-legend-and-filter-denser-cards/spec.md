# Board panel: collapsible state groups, machine legend and filter, denser cards

## Problem

Anton, November 18, 2026, on the Board panel of a project with 15 active increments, 8 of them blocked: "Rethink this. It could be improved. I believe we could have some kind of collapse panels for those types (active or blocked) and maybe some other optimizations. The color represents the machine, right? Same concept".

What the panel does today (app `a23f3593f`):

- **No way to fold anything.** The narrow panel is one long list: Active, In review, Planned, Done. Blocked work is spread through it and found only with the "Blocked only · N cards" switch or the "N blocked" button beside a heading (`apps/web/src/components/studio/shell/BoardPane.tsx:393-413`, `:454-464`).
- **The colored edge is unexplained.** It is the machine color of the card's lead thread, shown only when the project's threads run on more than one machine or the thread moved (`BoardCard.tsx:62-66`, `board.css` `.sws-board-card[data-machine-color]`). It uses the same `data-machine-color` token as the sidebar square (`MachineDot.tsx`) and the machine chip (`MachineChip.tsx`), so the colors already agree. Nothing on the board says so, a card with threads on two machines shows one color, and the board cannot be narrowed to a machine.
- **Cards are tall.** Number and age take a row, the title a second, the meter a third, each thread a fourth, and chips a fifth. Up to five pull request chips wrap onto a second chip row.
- **A card often has no action.** Start, Continue, Resume and Review and close appear only when the card has no thread at all (`BoardCard.tsx:61`). A card whose only thread is resolved offers nothing, while its increment view offers Continue (`boardIncrementModel.ts:200-228`).
- **Blocked reasons run together.** Example from Anton's screenshot: "New offline37profileattestation valid;113/148 exactartifactcopies recovered,35unresolved". The app strips nothing: the note is stored that way in the task ledger by the agent that blocked the task. Many writers do it, and the SpecWeave CLI sets no note limit that would explain it.

## Scope

In: the Board tab's list of cards in `repositories/anton-abyzov/specwithcode/apps/web`. Five foldable groups with Blocked first, a machine legend that is also a filter, a denser card with one action and one pull request chip, and a display-only repair of note punctuation. Client only.

Out: the contracts and the server (`projects.board` is unchanged); the increment view's layout (it gains only the note repair); the "Start a board for this project" state and the zero-increments sentence (`BoardPane.tsx:126-146`, `:421`), which increment 1387 is redesigning; drag to change state; any change to how agents write block notes (proposed as a follow-up below).

## Acceptance Criteria

- [ ] AC-01: **Groups.** The board has five groups: Blocked, Active, In review, Planned, Done. Blocked is derived on the client: every card for which `boardCardBlocked` is true (paused, or a blocked task; never a Done card) is listed in Blocked and not in its state group, and carries a label with that state ("Active", "In review", "Planned"). The Blocked heading counts those cards. Each state heading counts the server's count for that column minus its blocked cards, so the five counts add up to the server's total. With no blocked card the Blocked group is not rendered.
- [ ] AC-02: **Folding.** Each group heading is an `h3` holding one button with a chevron, the name and the count; `aria-expanded` says its state. Pressing it hides the group's cards and its "Show more" or "Show older" button. Folded groups are remembered in local storage per machine connection and project (`environmentId:projectId`) and are restored after a reload. Every group is open until the person folds it.
- [ ] AC-03: **Search.** While a search is typed, every group that has a match is shown open and its button is `aria-disabled`, the rule the Threads list uses (`ThreadsPane.tsx:934-952`). Clearing the search restores the remembered folds.
- [ ] AC-04: **Removed.** The "Blocked only" switch, its note line, its turning itself off, and the "N blocked" button beside a heading are gone. `boardFilterLabel` and the filter state are deleted, not left unused.
- [ ] AC-05: **Layouts.** In the stacked list (a panel under 720 px, or any width with the increment view open beside it) the groups stack in the order of AC-01. Side by side (720 px and wider, view closed) Blocked is a band across the top with its cards in columns of at least 240 px, and Active, In review, Planned and Done stay as columns in that order. A folded column becomes a rail 36 px wide with its name and count written vertically; the other columns share the freed width. A folded Blocked band is its heading alone. Nothing scrolls sideways at 360 px.
- [ ] AC-06: **Keyboard and the increment view.** Up and Down move between the cards on screen in visual order, Blocked first, and never land in a folded group. The view's previous and next step through the same list. Closing the view returns focus to its card, or to its group's heading button when the card is not on screen. Opening an increment by a link or by going back, when its group is folded, unfolds that group and remembers it. A card that changes group while its view is open (it becomes blocked, or unblocked) unfolds nothing.
- [ ] AC-07: **The edge means the machine.** A card's leading edge shows the color of every machine a thread of the card runs on, resolved threads left out, in the card's thread order, as up to three stacked segments. It appears under the same condition as today: the project's threads run on more than one machine, or a thread moved. The colors come from `data-machine-color`, the token the sidebar square and the machine chip use. Every machine on the edge is also named in text on the card, so color is never the only sign.
- [ ] AC-08: **Legend.** When the edge condition of AC-07 holds, a "Runs on" row under the search lists each machine that has a card: its color square (`MachineDot`), its name and its card count, with a tooltip that says cards with a thread on that machine carry the color on their edge. When the condition does not hold the row is not rendered.
- [ ] AC-09: **Machine filter.** The legend entries are toggle buttons (`aria-pressed`), one at a time, with "All" first. "No thread" is offered for cards outside Done that have no unresolved thread, and only once every thread has said which increment it works on. A chosen machine narrows every group to the cards the edge rule of AC-07 puts on that machine, and each heading then counts the cards it shows. The choice is not remembered between visits. It clears itself when its machine has no card left. Until the threads have answered, a status line says "Reading threads…" and counts are not shown on the entries. While a machine is chosen the Done group says its count covers only the done increments loaded so far, beside "Show older".
- [ ] AC-10: **Denser card.** Number and title share the first line (title up to two lines) with the state label of AC-01 and the age at the right. The meter and the task count ("6/15") share one line. A card shows at most two thread lines, unresolved first, then "N more threads", which expands in place. Everything else is one row: the blocked chip, "rest can continue", the pull request chip, the action. In the board fixture at a 400 px panel, the card with one thread, tasks and one pull request is at least 25% shorter than the same card at `a23f3593f`; both heights are recorded by `verify.mjs`.
- [ ] AC-11: **One action.** Every card outside Done has at most one action button, at the right of its last row, chosen by the rule the increment view already uses (`viewPrimaryAction`): "Open thread" when a thread on it can be opened (it opens the first such thread in the card's order); otherwise Start, Continue, Resume, Review and close, Plan the tasks or Plan it with the coordinator, which put the same request in the coordinator's composer as today. The request buttons appear only once the threads have answered and only when the person can send. A card whose threads are all resolved or on an unreachable machine gets the request button. Thread lines still open their own threads.
- [ ] AC-12: **Pull requests.** A card with one pull request shows one chip with its number, which opens it. A card with several shows one chip "N PRs" that opens a menu listing each number, with its state word (Open, Draft, Merged, Closed) when a thread of the project reports it and no word otherwise. The menu works from the keyboard and closes with Escape without closing the increment view. No contract field is added.
- [ ] AC-13: **Readable reasons.** One function prepares a block or pause reason for display, on the card and in the increment view: it collapses runs of whitespace and adds a space after a comma or semicolon that is directly followed by a letter or digit. It leaves digit groups ("1,234"), text inside backticks and tokens that contain "://" alone, and it never splits a word, so "T-64", "HTTPX" and "1.0.343" are unchanged. Reasons wrap inside long words and clamp at two lines on the card. Unit tests use made-up strings only.
- [ ] AC-14: **Proof.** `apps/web/tests/project-board/verify.mjs` passes against the new board, with checks for the group order and counts, a fold surviving a reload, the machine filter, the action on a resolved-thread card and the pull request menu. Headless captures, light and dark, of the narrow panel, the wide panel with a folded column, the split view, 390 px and a filtered board are saved in this increment's `reports/screens/`. The design-token guard, the focused tests, the web typecheck and the web build pass.

## Approach

Design and mockup: `reports/board-groups-mockup.html`.

1. `apps/web/src/studio/projectBoardModel.ts` (pure, tested first): `BOARD_GROUPS` and `BoardGroupId` ("blocked" plus the four columns); `boardGroups(cards)` and `boardGroupCounts(counts, groups)`; `boardCardMachines(threads)` for the edge and the filter; `boardMachineOptions(cards, threadsByIncrement)`; `boardNoteText(note)`; `boardPullRequestChip(urls)`. `boardBlockedCounts` and `boardFilterLabel` go.
2. `BoardPane.tsx`: groups replace columns in the render loop; fold state through `useLocalStorage` with a schema, keyed `environmentId:projectId` (new key `studio:project-board-folded:v1`); the search rule; the walk, the arrow keys and the focus return read groups; an effect on the open increment's id unfolds its group. Group rendering moves to a new `BoardGroupSection.tsx` and the legend to `BoardMachineLegend.tsx`, so the pane stays near its present size. Lines 126-146 and the sentence at 421 are not edited.
3. `BoardCard.tsx` and `BoardThreads.tsx`: the dense anatomy, the state label, edge segments, `viewPrimaryAction` for the action, the pull request chip and menu (`components/ui/menu`), `boardNoteText` on reasons. `BoardIncrementView.tsx` gains `boardNoteText` on the blocker and pause reasons, nothing else.
4. `board.css` (and the two rules in `board-view.css` that name columns): group headings, the band, rails, the dense card, the legend. Tokens only.
5. Tests: `projectBoardModel.test.ts`, `BoardPane.test.tsx`, `BoardPane.view.test.tsx`, the fixture `tests/project-board/mocks.tsx` and `verify.mjs`.

Rejected:

- **Keeping the switch and adding folds.** Two ways to find blocked work, and the heading would still read "Active 15, 8 blocked". Anton asked for Blocked as a type of its own.
- **A blocked card in both groups.** Counts stop adding up, and the card walk and focus return need a card to be in one place.
- **A fifth column for Blocked in the wide panel.** Five columns at 720 px are 130 px each. A band keeps the four columns in the order work moves.
- **Splitting squeezed words.** Any rule that splits "offline37profileattestation" also breaks "T-64", "HTTPX", version numbers and hashes. The board repairs punctuation only and says so.
- **Pull request states on every chip.** The card carries URLs only; states are known for pull requests a thread links. Showing all states needs a contract field and a server read.
- **Remembering the machine filter.** A board that opens narrowed, with cards missing, reads as lost work. Folds are remembered because a folded heading still shows its count.

Risks: 1387 will render the real `BoardCard` with sample data and edit two regions of `BoardPane.tsx`; the card's props change here (it gains `pullRequestStates` and `stateLabel`), and its thread has the note. `verify.mjs` pins the old strings and `[data-column]`; it is updated in the same change. The fold effect of AC-06 must key on the open id alone, or a refresh that moves a card would unfold a group the person closed.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Blocked is a group and the "Blocked only" switch goes. This reverses 1338 D-06 ("Blocked stays a state on the card and a filter") on Anton's November 18 request.
- D-02 Every group starts open; nothing is folded for the person.
- D-03 Folds are remembered per project and machine connection, not globally as the Threads list does, because boards differ in size from project to project.
- D-04 The machine filter is not remembered between visits.
- D-05 The edge shows every machine with an unresolved thread on the card (up to three), not only the lead thread's. A thread on an unreachable machine counts: its line already names that machine in its color.
- D-06 Several pull requests open a menu on the card instead of opening the increment view.
- D-07 In the wide panel a folded column becomes a rail; folds mean the same in every layout.
- D-08 Note repair is punctuation only. Follow-up, not built here: `specweave task block` warns on a note with squeezed words, and the sw-do skill tells agents to write block notes as plain sentences.
### Open
- none

## Review

Reviewer: Muse Wonder Full (`muse-wonder-full-1.0`) at xhigh, on the spec and mockup before the build and on the exact head before the merge.

## Tasks

### T-01 Board model: groups, counts, machines, note text, pull request chip
- AC: AC-01, AC-07, AC-09, AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectBoardModel.test.ts

### T-02 Pane: foldable groups, remembered folds, search rule, keyboard and focus
- AC: AC-01, AC-02, AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardGroupSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.view.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/BoardPane.test.tsx src/components/studio/shell/BoardPane.view.test.tsx

### T-03 Card: dense anatomy, state label, one action, pull request chip, readable reasons
- AC: AC-10, AC-11, AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardThreads.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardIncrementView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/board.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/BoardPane.test.tsx

### T-04 Machine edge segments, legend and filter
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardMachineLegend.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/board.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/BoardPane.test.tsx

### T-05 Wide layout: Blocked band and folded rails
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/board.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/board-view.css | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/project-board/verify.mjs

### T-06 Fixture verifier and captures
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/main.tsx | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/project-board/verify.mjs && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json

### T-07 Pull request, exact-head review, merge and release request
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx | Test: cd repositories/anton-abyzov/specwithcode && gh pr view --json state,mergedAt

### T-08 Verify and close 1391
- AC: AC-14 | Files: .specweave/increments/1391-board-panel-collapsible-state-groups-machine-legend-and-filter-denser-cards/spec.md | Test: specweave verify 1391-board-panel-collapsible-state-groups-machine-legend-and-filter-denser-cards
