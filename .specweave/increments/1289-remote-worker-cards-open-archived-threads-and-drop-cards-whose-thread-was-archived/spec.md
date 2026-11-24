# Remote worker cards: open archived threads and drop cards whose thread was archived

## Problem

On linux-mini (Minisforum), the specweave project's Threads pane shows five cards above "Needs you" and "Working": "Why m4 update took 15+ min", "Create Instagram DfXhJlPAEB4 routine on m4", "Install iOS build 38 on iPhoneA", "Install iOS build 38 on iPhone 16", "Install latest iOS on Duo". Each says `m4`, `Done`, and has an "Open on m4" button. Clicking any of them opens a page that says "Thread not found. m4 has no such thread. It may have been removed, or the link is out of date." (photos `~/Downloads/IMG_0137.HEIC`, `~/Downloads/IMG_0138.HEIC`, November 10, 2026, 23:19).

The cards are intended: they are the workers the linux-mini coordinator started on m4 (`RemoteWorkerCards`, served by `workersForProject` in `apps/server/src/fleet/RemoteWorkers.ts`, newest 50 rows that are not `disposed`). The click is a bug, and the cards outliving their threads is a second one:

1. All five threads still exist on m4 but are archived there (m4 `orchestration_v2_projection_threads`: `archived_at` set between November 9 and November 10, `deleted_at` null). A machine's live thread list leaves out archived threads. `ThreadRouteView` only renders a conversation when the thread is in that live list, so an archived thread on a connected machine resolves to `missing`, and `threadRouteProblem` reports it as "Thread not found".
2. PR #114 (`5dd5941299`, November 10) changed `remoteWorkerReachableHere` to offer "Open on m4" whenever m4's thread list has loaded, on the stated assumption that an archived thread's "page still opens". It does not. Before #114 the same card wrongly said "Connect m4 in Settings > Machines to open it here".
3. A finished worker's row is never disposed when its thread is archived on the other machine, so settled work stacks at the top of the Threads pane with no way to clear it.

## Scope

In: the worker card and the thread page in `apps/web`, for a worker whose thread is archived or deleted on a connected machine. Out: changing what the server keeps in the remote worker store, the conversation-inline cards' placement, archived threads opened from anywhere else in the app.

## Acceptance Criteria

- [ ] AC-01: In the Threads pane, a remote worker card whose thread is archived on its machine is not shown, once that machine's archived list has loaded. A card whose thread is still live there is unchanged.
- [ ] AC-02: A remote worker card under the coordinator reply that started it stays after its thread is archived, and its button reads "Open archived thread on {machine}".
- [ ] AC-03: Opening a thread that is archived on a connected machine never shows "Thread not found". The page says "This thread is archived on {machine}" with an Unarchive button; Unarchive restores it and the conversation opens on the same page.
- [ ] AC-04: "Thread not found" appears only when the machine's live and archived lists have both answered without the thread. A worker card whose thread is in neither list shows "Removed on {machine}" and no Open button.
- [ ] AC-05: While the machine's archived list has not answered, the card keeps its current state and the thread page says "Opening thread...", not "Thread not found".

## Approach

1. `apps/web/src/studio/remoteWorkerCards.ts`: replace `remoteWorkerReachableHere` with a pure `remoteWorkerOpenState(worker, liveThreads, archivedThreads)` returning `live | archived | removed | checking | unreachable`. `visibleRemoteWorkers` takes the archived ids and drops `archived` for the Threads pane only.
2. `apps/web/src/components/studio/RemoteWorkerCards.tsx`: read the worker machine's archived threads with `useArchivedThreadSnapshots` (`apps/web/src/lib/archivedThreadsState`) and render per state. First confirm that hook loads for a remote environment; if it only loads the local one, extend it to take an environment id rather than adding a second fetch.
3. `apps/web/src/components/ThreadRouteView.tsx`, `apps/web/src/components/ThreadRouteProblem.tsx`, `apps/web/src/studio/threadRouteProblem.ts`: add an `archived` kind fed by the same archived list, with Unarchive through `useThreadActions().unarchiveThread`. `missing` requires both lists to have answered.

Rejected: disposing the row on the launching machine when the remote thread is archived. It needs the follower to watch archive events across machines, and it would also remove the card from the coordinator conversation, where it is history. Rejected: reverting #114. It brings back the wrong "Connect m4 in Settings" text.

Risk: the archived list of a machine with thousands of archived threads. Reuse the existing paged state; do not fetch per card.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 An archived worker's card leaves the Threads pane but stays in the coordinator conversation → yes (reversible).
- D-02 The thread page offers Unarchive instead of a read-only view of the archived conversation → yes (reversible; a read-only view needs a new server read).
### Open
- none

## Tasks

### T-01 Card open state from live and archived lists
- AC: AC-01, AC-02, AC-04, AC-05 | Files: [apps/web/src/studio/remoteWorkerCards.ts, apps/web/src/studio/remoteWorkerCards.test.ts, apps/web/src/components/studio/RemoteWorkerCards.tsx, apps/web/src/components/studio/RemoteWorkerCards.test.tsx, apps/web/src/components/studio/shell/ThreadsPane.tsx] | Test: `bun run --cwd apps/web test src/studio/remoteWorkerCards.test.ts src/components/studio/RemoteWorkerCards.test.tsx`

### T-02 Thread page for an archived thread on another machine
- AC: AC-03, AC-04, AC-05 | Files: [apps/web/src/studio/threadRouteProblem.ts, apps/web/src/studio/threadRouteProblem.test.ts, apps/web/src/components/ThreadRouteProblem.tsx, apps/web/src/components/ThreadRouteView.tsx] | Test: `bun run --cwd apps/web test src/studio/threadRouteProblem.test.ts`

### T-03 Headless check on a two-machine fixture
- AC: AC-01, AC-03 | Files: [apps/web/tests/handoff-mode/verify.mjs] | Test: headless run of the fixture with one archived remote worker thread: no card in the Threads pane, the thread link shows the archived page, Unarchive opens the conversation; screenshots saved to files
