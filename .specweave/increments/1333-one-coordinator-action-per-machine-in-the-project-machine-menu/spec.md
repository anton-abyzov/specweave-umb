# One coordinator action per machine in the project machine menu

## Problem

The project machine menu ("Runs on m4" chip) offered two coordinator items for the same machine, "Move coordinator to m1…" and "Start a coordinator on m1", with no way to tell them apart. Anton asked whether they are the same mechanism, whether the app can tell that m1 ever ran a coordinator, and why only m1 is offered (screenshot of November 14, 2026, `reports/screens/coordinator-menu-before-light.png`).

## Findings (code read on origin/main `b71ec48aef`)

**Both items change one record, the copy's coordinator binding** (`coordinatorBinding` in `packages/contracts/src/logicalProject.ts:95`: `epoch`, `state` active, transferring or transferred, `predecessor`, `successor`). They differ in what else happens:

| | Move coordinator to m1… | Start a coordinator on m1 |
|---|---|---|
| Calls | Machine handoff dialog: prepare, receive, ack (`apps/server/src/fleet/MachineHandoff.ts`) | `projectLink.startCoordinator` (`apps/server/src/project/ProjectLink.ts:1194`) |
| Carries | This coordinator's conversation bundle and Git state; m1's coordinator gets a start message with that context | Nothing. Only missing project notes from the replica are written |
| m1 after | Active, epoch + 1, `predecessor` = m4 (`MachineHandoff.ts:1137`). Project-folder mode reuses m1's project and its `project-coordinator:<id>` thread; worktree mode creates a new `machine-handoff:<operation>` project there and leaves the registered copy "transferred" with that successor (`MachineHandoff.ts:1343`) | Active, epoch + 1, no predecessor (`ProjectLink.ts:1234`) |
| m4 after | Transferred: its conversation stays as read-only history, and it gives way (superseded in `logicalCoordinators`, `apps/web/src/studio/projectDomain.ts:69`) | Unchanged. Both coordinators run, each keeps its own threads |
| Offered when | m1's copy only runs workers (role workers or independent) | m1's copy only runs workers, its binding is transferred, and m1's server reports `coordinatorPerMachine` (`projectCoordinatorMachine.ts:226`) |

**Can the app tell a coordinator was ever started there?** Yes, but not from the binding alone (corrected after the Muse review). A transferred binding is also what a copy gets when it joins as workers only (`ProjectLink.ts:622`), and a worktree-mode move leaves the registered copy transferred with a successor on its own machine (`MachineHandoff.ts:1343`). A copy really kept a coordinator when all three hold: its binding is transferred, its successor is on another machine, and its own coordinator thread exists in the synced thread list (the same test the workers-only notice already uses, `ProjectWorkspaceSurface.tsx:602`). `keptCoordinatorCopies` in `projectCoordinatorMachine.ts` applies it; no new state.

**m1 in Anton's menu:** m1's copy declares this logical project with a transferred binding, so both items appeared. m4's own member list (m4 and linux-mini, epoch 0) no longer lists m1. The menu still shows m1 because the sidebar groups copies by logical project id, from either side (`packages/client-runtime/src/state/projectGrouping.ts:277`). After this change m1 gets "Open coordinator on m1" only if its coordinator thread is in the synced list and its successor is another machine; otherwise it gets "Move coordinator to m1…".

**Why not linux-mini or m5:** linux-mini already runs its own coordinator (active binding), so a move there is refused by the server (`MachineHandoff.ts:1129`) and Start would only replay. Viewing it in "View this project on" is how it is opened. m5 has no copy of this project and is unreachable now, so the menu cannot list it; "Copy to another machine…" is the way to bring the project there.

## Scope

In: one coordinator item per other machine in the project machine menu, named by that machine's state; Open runs the kept coordinator and switches the view to it; the composer notice on a workers-only copy uses the same wording; translations; a headless fixture with before and after captures.

Out: the server mechanisms (unchanged); the Copy to another machine dialog and its access:write fix (thread "One simple flow to bring a project to another machine"); grants (1326/1327); Settings > Machines buttons; repairing m4's member list for m1.

## Acceptance Criteria

- [ ] AC-01: For each other machine the menu shows at most one coordinator item, even with several copies there: "Open coordinator on X" when a copy on X kept a coordinator conversation it can run again (transferred to another machine, its coordinator thread exists, X can start one), "Move coordinator to X…" when X only runs workers otherwise, and none when any copy on X already runs its own coordinator. "Start a coordinator on X" is gone.
- [ ] AC-02: "Open coordinator on X" runs that coordinator again (same `projectLink.startCoordinator`) and, once it runs, the page shows X. On failure the page stays and the error toast says why. A click while a start for the project is already running does nothing; that start's own toast reports.
- [ ] AC-03: The composer notice on a workers-only copy names the same action ("Run X's coordinator again"), and one start per project still runs at a time across both.
- [ ] AC-04: Headless before and after captures of Anton's menu (m1 workers only with a kept coordinator, linux-mini with its own, m4 viewed), light and dark, saved in `reports/screens/`.

## Approach

`OrchestratorSwitcher.tsx` builds one list of coordinator actions from the copies it already receives; `useStartCoordinator` resolves true or false so the switcher can show the opened copy. Moving to a machine that kept a coordinator stays possible through "Copy to another machine…", whose dialog asks where the coordinator runs (decision_copy_to_another_machine_flow). No new state, RPC or setting.

Rejected: a separate "Open" item for machines that already run a coordinator (duplicates the view list); keeping Move next to Open for the same machine (two conversations for one place, the confusion Anton reported).

## Reviews

- GPT-6.1 Sol: NOT YET at `1411bea865` (a slow start pulled the page back), SHIP at `0a52a41150`. Round 3 on `8f4e73daa9` could not be sent: linux-mini's address answered as a different machine.
- muse-wonder-full-1.0 (Max): NOT YET at `0a52a41150` (one blocker and four should-fix items, all fixed in `8f4e73daa9`), SHIP at `8f4e73daa9`. Reports are in `reports/review.md` and `reports/reviews/`.
- Merged as `550427fbcd` (PR #383); release requested on November 14, 2026.

Follow-ups left open (all low, from Muse round 2):
- `keptCoordinatorCopies` checks only the direct successor; `coordinatorElsewhere` follows the whole chain. Not reproduced.
- A superseded coordinator copy has role workers, so its machine still gets Move; the handoff then refuses with a conflict.
- The failure toast shows a reason only for an Error with a message; any other cause says "Retry it."

## Decisions

### Asked
- D-01 Merge Move and Start into one item labelled by state → yes, "Open coordinator on m1" when one exists, "Move coordinator to m1" otherwise (Anton, November 14, 2026).
### Defaulted (change any before sw-do)
- D-02 A machine that runs its own coordinator gets no item; viewing it opens it → default.
- D-03 Open switches the view to that machine after it starts → default.
### Open
- none

## Tasks

### T-01 One coordinator action per machine in the switcher
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCoordinatorMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/OrchestratorSwitcher.test.tsx src/studio/projectCoordinatorMachine.test.ts src/i18n/i18n.test.ts

### T-02 Composer notice uses the same action
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.test.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/CoordinatorBlockedNotice.test.tsx src/components/studio/ProjectWorkspace.threads.test.tsx

### T-03 Headless before and after captures
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/main.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/coordinator-menu/vite.config.ts && node apps/web/tests/coordinator-menu/verify.mjs /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1333-one-coordinator-action-per-machine-in-the-project-machine-menu/reports/screens

### T-04 Verify and close 1333
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1333-one-coordinator-action-per-machine-in-the-project-machine-menu/spec.md | Test: specweave verify 1333-one-coordinator-action-per-machine-in-the-project-machine-menu
