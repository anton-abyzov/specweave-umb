# A message typed in a remote thread reaches that thread

## Problem

On M4's project page, the composer of a thread that runs on Ministorm under Ministorm's coordinator took the user's text and sent it to M4's coordinator as "Regarding thread <id> on machine <env> (<title>):". The draft cleared, nothing was added to the thread on either machine, and the worker's question stayed open.

Evidence: three such turns on the M4 coordinator on November 2-3, 2026. `studio_thread_send` from M4 was refused with `outside_grant_scope` by `assertThreadWritable`, so that coordinator could not deliver them. `useRoutedThreadMessages` gets a null coordinator for a remote thread, so nothing showed where the user typed.

The same thread takes the same message directly from a thread link (no routing context) and from iPhone (`dispatch(command, on: ref.environmentId)`). Those use the user's own paired connection and the `orchestration:operate` scope; the work grant applies only to MCP callers.

## Scope

In: the project page's worker pane delivers into the thread on its own machine, visible on both machines; earlier relayed messages show in the thread they were typed in, with an honest note; the blocked note clears when the answer lands. Out: any change to work grants, MCP tools or per-machine coordinators.

## Acceptance Criteria

- [x] AC-01: A message typed in a remote thread on the project page is dispatched to that thread on its own machine, with no coordinator turn, and appears in its timeline on both machines.
- [x] AC-02: A remote thread's composer takes files and context the same way a local worker's does, and a failed send keeps the draft.
- [x] AC-03: A connection without the operate scope, or a machine that is not connected, says so and keeps the draft; nothing is sent anywhere else.
- [x] AC-04: A message an earlier version relayed appears in the thread it was typed in, on the machine that relayed it, with a note saying it went to the coordinator and not to this thread, linking to the coordinator.
- [x] AC-05: The work-grant refusal for another machine's coordinator is unchanged.
- [x] AC-06: The thread's blocked note clears once the answer is in that thread.
- [x] AC-07: Reproduced end to end headless with two real services.

## Approach

`apps/web/src/components/studio/ProjectWorkerPane.tsx`: the pane is always direct. `coordinatorBlocked` (#1067) and the relay branch go away, in favour of the path thread links and iPhone already use.

`packages/shared/src/routedMessage.ts`, `apps/web/src/studio/projectCoordinatorMessageDisplay.ts`, `apps/web/src/components/studio/ProjectRoutedReplies.tsx`: find relayed messages with `parseRoutedThreadReply`, matched on thread and machine so a colliding id on another machine does not match. New note kind `relayed`.

Rejected: letting the M4 coordinator send to Ministorm's threads, which removes the security boundary from project memory `orchestrator-per-machine-0969.md`. Rejected: disabling the composer with "open on that machine", which is worse than the direct path that already works.

## Decisions

### Asked
- D-00 Should the person's own paired device answer a thread on another machine? -> Yes (user, November 2, 2026): what they type in a thread runs in that thread on its machine, with attachments, on both machines. Another machine's agent stays refused (`outside_grant_scope`) unless granted. A connection without the operate scope, as on another person's machine, keeps "This connection cannot change threads."
### Defaulted (change any before sw-do)
- D-01 The user's own connection to their paired machine may answer that machine's thread, as thread links and iPhone already do. No server or grant change, so no product decision is needed.
### Open
- none

## Tasks

### T-01 Deliver from the worker pane to the thread's own machine
- AC: AC-01, AC-02, AC-03, AC-05 | Files: apps/web/src/components/studio/ProjectWorkerPane.tsx, apps/web/src/components/studio/ProjectWorkerPane.test.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: vp test run apps/web/src/components/studio/ProjectWorkerPane.test.tsx

### T-02 Show earlier relayed messages in their thread
- AC: AC-04 | Files: apps/web/src/studio/projectCoordinatorMessageDisplay.ts, apps/web/src/studio/projectCoordinatorMessageDisplay.test.ts, apps/web/src/components/studio/ProjectRoutedReplies.tsx, apps/web/src/types.ts | Test: vp test run apps/web/src/studio/projectCoordinatorMessageDisplay.test.ts

### T-03 Two-service headless proof
- AC: AC-01, AC-06, AC-07 | Files: scripts/studio-logical-projects/two-orchestrators.mjs | Test: STUDIO_TWO_ORCHESTRATORS_REMOTE_MESSAGE_ONLY=1 node scripts/studio-logical-projects/two-orchestrators.mjs

### T-04 Verify and close 1187
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 1187-a-message-typed-in-a-remote-thread-reaches-that-thread

## Notes

T-03's proof lives in `scripts/studio-logical-projects/two-orchestrators.mjs`, run with `STUDIO_TWO_ORCHESTRATORS_REMOTE_MESSAGE_ONLY=1`, not the separate script first named above. The full run stops earlier at its memory stage with or without this change. Relayed messages older than the coordinator's or thread's loaded history show no note until that history loads.
