# Move a thread to another project

## Problem

A thread started in the wrong project (an EasyChamp audit launched from SpecWeave on October 19, 2026, then cancelled) can only be cancelled and retyped by hand. The user wants to stop such a thread and move it to the right project, expecting it to restart there from scratch.

## Scope

In: SpecWithCode (`anton-abyzov/specwithcode-dev`) contracts, server orchestration, client runtime, the thread menus, a move dialog and banners. Out: moving to a project on another machine, carrying file changes, attachments, provider sessions or memory; agent-initiated moves (the "Aide routes work to projects" increment 0945 owns routing new work).

## Acceptance Criteria

- [ ] AC-01: "Move to another project…" in the sidebar and thread header menus opens a dialog that lists the other active projects on the same machine, prefills the thread's opening request (editable), and states what carries over (nothing) and what happens to the original.
- [ ] AC-02: Moving creates a fresh thread in the target project with that project's settings and folder, no messages, provider session, files, worktree, memory or credentials from the source, linked back with `movedFrom`.
- [ ] AC-03: The source is recorded as moved first (`movedTo`), then archived with its queue discarded, its running turn and delegated tasks stopped; afterwards it refuses new turns, so nothing it held runs against the wrong project. Its history, linked pull requests and project stay where they were.
- [ ] AC-04: "Start it there now" sends the opening request in the new thread only after the source is stopped; it defaults on for work that was running and off for stopped or cancelled work, which then waits in the new thread's composer.
- [ ] AC-05: Coordinators, provider-native subagents, a thread already moved, the same project, an archived/paused/missing target and non-user callers are refused with a reason; delegated tasks move as ordinary threads. A retry with the same command id resumes the move without a second thread.
- [ ] AC-06: Both threads show a banner linking to the other. The original is archived, so the new thread's link opens it once it is restored and leads to Archived settings until then. Older servers do not offer the action.

## Approach

Client command `thread.move-to-project` is routed in `ws.ts` to `ThreadMoveService` (orchestration-v2): validate, `ThreadLaunchService.launch` the target (root workspace), internal `thread.project-move.record` for target then source (source side archives through the existing archive mutation), `thread.stop` plus delegated-task stop, optional `sendToThread`. `message.dispatch` refuses a thread with `movedTo`. Capability `threadProjectMove`. Web: `threadMove.logic.ts`, `ThreadMoveDialog.tsx`, menu item in `threadActionMenu.logic.ts`, banners in `ChatView.tsx`.

## Decisions

### Asked
- none
### Defaulted
- D-01: Move = restart: a new thread, never a re-pointed one, so provenance and old run events stay in the source project.
- D-02: Same machine only; another machine uses handoff.
- D-03: Model comes from the target project's default; runtime mode from the target project's saved mode.

## Tasks

### T-01 Contracts, orchestrator record command and moved-thread guard
- AC: AC-02, AC-03, AC-05 | Files: packages/contracts/src/orchestrationV2.ts, packages/contracts/src/environment.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/ProjectionStore.ts | Test: vp test run apps/server/src/orchestration-v2/ThreadMoveService.test.ts

### T-02 ThreadMoveService and server wiring
- AC: AC-02, AC-03, AC-04, AC-05 | Files: apps/server/src/orchestration-v2/ThreadMoveService.ts, apps/server/src/orchestration-v2/ThreadMoveService.test.ts, apps/server/src/ws.ts, apps/server/src/orchestration-v2/runtimeLayer.ts | Test: vp test run apps/server/src/orchestration-v2/ThreadMoveService.test.ts apps/server/src/orchestration-v2/ThreadStop.test.ts

### T-03 Client command, menus, dialog and banners
- AC: AC-01, AC-04, AC-06 | Files: packages/client-runtime/src/operations/commands.ts, packages/client-runtime/src/state/threadCommands.ts, apps/web/src/components/ThreadMoveDialog.tsx, apps/web/src/components/threadMove.logic.ts, apps/web/src/components/threadActionMenu.logic.ts, apps/web/src/components/ChatView.tsx | Test: vp test run apps/web/src/components/threadMove.logic.test.ts packages/client-runtime/src/operations/threadOpeningRequest.test.ts

### T-04 PR, merge and installed runtime check
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: installed service reports threadProjectMove; move a scratch thread end to end

### T-06 Closure review fixes: original link and target runtime mode
- AC: AC-02, AC-06 | Files: apps/server/src/orchestration-v2/ThreadMoveService.ts, apps/web/src/components/ChatView.tsx, scripts/studio-verify/thread-move.mjs | Test: vp test run apps/server/src/orchestration-v2/ThreadMoveService.test.ts; headless thread-move.mjs

### T-05 Verify and close 0947
