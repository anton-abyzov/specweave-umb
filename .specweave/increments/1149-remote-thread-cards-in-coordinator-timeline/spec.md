# Remote thread cards in coordinator timeline

## Problem

In the coordinator conversation, cards for workers the coordinator started on another machine (the Ministorm Linux machine on October 30, 2026) render after every message. They sit pinned under the newest message and above the composer, so a message sent later appears above work that started a day earlier. Opening one ("Open on Ministorm") leaves the project page for a full-page thread with no visible way back to the coordinator. Evidence: the two October 31, 2026 screenshots in the M4 coordinator, and `CoordinatorConversation.tsx` rendering `RemoteWorkerCards` after the message list.

## Scope

In: the Threads pane machine column and machine filter (follow-up request, same release); place each remote worker card under the reply of the turn that started it; send the launch time from the server; show only still-active, unplaceable workers above the live activity; open a remote worker's thread in the project's side pane beside the coordinator. Out: a group-by-machine toggle (rejected by the judge pass: it fights the status sections, so "Waiting on you" would stop leading); provider or fleet changes.

## Acceptance Criteria

- [x] AC-01: A remote worker card renders under the last reply of the turn whose window contains its launch time, and a later message renders after it.
- [x] AC-02: Workers launched in one turn keep launch order; a worker of a turn with no reply yet shows above the live activity.
- [x] AC-03: A settled worker with no loaded turn or no launch time (older server) is not stacked at the end; an active one shows above the live activity.
- [x] AC-04: The server sends `launchedAt` from the stored launch time; the field is optional so older servers still decode.
- [x] AC-05: Opening a remote worker from the coordinator opens it in the project's side pane, so the coordinator stays beside it.
- [x] AC-06: In the Threads pane, each row's machine sits in one aligned column beside the age instead of the end of the meta line; a pane narrower than 360 px keeps the icon and the name's first letters.
- [x] AC-07: When threads run on more than one machine, the sort menu offers "Machine" with each machine's open-thread count; choosing one narrows the list per project (remembered), shows an "On <machine>" pill, and Show all undoes it.

## Approach

`StudioFleetRemoteWorker.launchedAt` (optional) filled from `launchStartedAt` in `RemoteWorkers.workersForProject`. Pure rule `placeRemoteWorkers` in `apps/web/src/studio/remoteWorkerCards.ts`. `CoordinatorConversation` renders `RemoteWorkerCardList` after each anchored row and the live strip above the run activity. `projectPaneThread` accepts `scope.remoteThreads`, which `ProjectWorkspaceSurface` fills from the project's remote workers. Rejected after a judge pass: a standalone timestamped row (splits a turn) and a folded bottom strip (keeps the wrong order). `updatedAt` is not a fallback anchor because it moves on every status change.

## Decisions

### Asked
- D-01 placement → anchored where launched, no bottom stack (user)
### Defaulted (change any before sw-do)
- D-02 unplaceable settled workers → only in the Threads pane list
### Open
- none

## Tasks

### T-01 Anchor remote worker cards in the coordinator timeline
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/contracts/src/studioFleet.ts, apps/server/src/fleet/RemoteWorkers.ts, apps/web/src/studio/remoteWorkerCards.ts, apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/RemoteWorkerCards.tsx | Test: npx vp test run --project unit src/studio/remoteWorkerCards.test.ts

### T-02 Open remote worker threads beside the coordinator
- AC: AC-05 | Files: apps/web/src/studio/projectPaneThreads.ts, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: npx vp test run --project unit src/studio/projectPaneThreads.test.ts

### T-04 Machine column and filter in the Threads pane
- AC: AC-06, AC-07 | Files: apps/web/src/studio/threadMachineFilter.ts, apps/web/src/components/studio/shell/ThreadsPane.tsx, apps/web/src/components/studio/shell/shell.css | Test: npx vp test run --project unit src/studio/threadMachineFilter.test.ts src/components/studio/ProjectWorkspace.test.tsx

### T-03 Verify and close 1149
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: apps/web/tests/project-workspace/remote-cards-check.mjs | Test: headless remote-cards-check.mjs against serve.mjs
