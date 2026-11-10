# Add to machine for agents: unlinked-copy loop, clone timeout and no-origin worktrees

## Problem

From the New project review of November 10, 2026 (`.specweave/reviews/new-project-2026-11-10/report.html`), in the SpecWithCode app (`specwithcode-dev`). An agent that puts a project on another machine and starts work there can get stuck in ways it cannot leave:

1. Unlinked-copy loop. `studio_project_add_to_machine` returns a success-shaped result for a copy that is not linked, with `next: Launch there with studio_thread_launch {machine, machineProjectId}` (`apps/server/src/mcp/toolkits/project/addToMachine.ts:189`, and `:283` after a clone whose link failed). That launch is refused: a project with a logical project needs a member binding (`apps/server/src/fleet/RemoteWorkers.ts:827-831`). Passing `machineProjectId` also skips the auto-link (`apps/server/src/mcp/toolkits/project/remoteLaunch.ts:329-331`), and the failure hint sends the agent back to add-to-machine (`:373`), which returns the same copy.
2. Clone timeout. The target's `studio_project_clone` calls `cloneRepository(input)` with no options (`apps/server/src/mcp/toolkits/project/handlers.ts:1057`), so the 120-second default applies (`apps/server/src/sourceControl/SourceControlRepositoryService.ts:117`, `:425`) although the caller allows 10 minutes. A large repository cannot be added by an agent.
3. No resume. After "cloned, but registering failed", the next call clones into the same path and fails with "Destination path already exists and is not empty." (`SourceControlRepositoryService.ts:341`).
4. `studio_worktree_handoff` fails on a repository with no `origin`: `startFromOrigin` defaults to the server setting and the tool fetches origin unconditionally (`apps/server/src/mcp/WorktreeMcpService.ts:256-262`), ending in "Unable to fetch origin". A new local project hits this as soon as Use worktrees is on. `studio_thread_launch` already checks `remoteExists` first (`apps/server/src/orchestration-v2/ThreadLaunchService.ts:586-590`).
5. `studio_thread_migrate` interrupts the running turn (`apps/server/src/handoff/HandoffMoves.ts:832`) before it refuses for an unsettled child (`:847`) or a failed second checkpoint, leaving a stopped turn and "Hand it off again to resume that turn."
6. The receiving machine picks the local project by first match on the member list, with no reciprocity or ambiguity check (`apps/server/src/handoff/handoffState.ts:484-496`), unlike `isLogicalProjectBinding`.
7. "Take theirs" on a diverged repository is removed in the web client only (`apps/web/src/studio/addToMachineCopy.ts:103`); the server still honours it.
8. The web add-to-machine job lives in one browser's `localStorage`; closing it mid-clone leaves the copy unlinked, and a project that never appears is dropped with no message (`apps/web/src/components/AddToMachineJobRunner.tsx:193`).

## Scope

In: the eight defects above, on the server and in the web job runner.

Out: no-remote projects (1285); grant scope rules; the folder copy engine; provider session migration; a server-side job store for add-to-machine (the web job keeps `localStorage`, it only stops failing silently).

## Acceptance Criteria

- [ ] AC-01: `studio_project_add_to_machine` never returns a `next` that launch will refuse. For an unlinked copy it retries the link; if the link still fails it returns a failure that states the problem and the one action that resolves it (the user's Link… or removing the stale member), with no launch instruction.
- [ ] AC-02: `studio_thread_launch` with `machineProjectId` naming an unlinked copy of the same repository attempts the link before refusing, and its refusal does not point back at add-to-machine when that would return the same copy.
- [ ] AC-03: An agent-started clone on the target runs up to 10 minutes; the caller's timeout and the target's agree. A clone that exceeds it fails with the elapsed time and removes its partial folder.
- [ ] AC-04: A retry after "cloned, registering failed" registers and links the existing clean clone at that path instead of cloning again. A folder holding a different repository or local changes is still refused.
- [ ] AC-05: `studio_worktree_handoff` on a repository with no `origin` branches from the local base when `startFromOrigin` was not passed, and reports `startedFromOrigin: false`. With `startFromOrigin: true` passed explicitly it fails with a message that names the missing remote and the option to drop.
- [ ] AC-06: `studio_thread_migrate` checks unsettled children and anything else it can refuse on before interrupting the running turn. A handoff that fails after the interrupt resumes the turn on the source automatically.
- [ ] AC-07: The receiver resolves the local project with the same reciprocal binding rule as launches, and refuses with "more than one project here lists this source" when two match.
- [ ] AC-08: The server refuses "take theirs" for a diverged repository in the add-to-machine consolidate path, whatever the client sends.
- [ ] AC-09: The web job runner shows a toast when it gives up on a job ("<project> was cloned on <machine> but is not linked: <reason>") and resumes pending jobs on the next app start in that browser.
- [ ] AC-10: `addToMachine.test.ts`, `remoteLaunch.test.ts`, `WorktreeMcpService.test.ts`, `migrate.test.ts` and `AddToMachineJobRunner.test.tsx` gain a case for each item and all existing cases pass.

## Approach

1. `addToMachine.ts`: one result builder for linked and unlinked; unlinked goes through `linkCopy` once more, then fails with `linkProblem`. Detect an existing clean clone of the same origin at the destination before cloning.
2. `remoteLaunch.ts`: drop the `machineProjectId === undefined` condition for the link attempt when the named project is a copy of this repository.
3. `handlers.ts:1057`: pass the agent clone timeout through to `cloneRepository`.
4. `WorktreeMcpService.ts`: `GitWorkflowService` does not expose `remoteExists`; add it there (it wraps `GitVcsDriver.remoteExists`) and use it only when the input left `startFromOrigin` unset.
5. `HandoffMoves.ts`: move the children check ahead of `interruptRun`; on failure after the interrupt, queue a resume of the interrupted turn.
6. `handoffState.ts`: `linkedLocalProject` uses `isLogicalProjectBinding` and returns an ambiguity result.
7. `reconcile.ts`: reject `moveHead: "take-theirs"` when the heads diverged and the operation is a consolidate.
8. `AddToMachineJobRunner.tsx`: toast on the dropped path; do not keep `attempted` across a reload.

Rejected: letting launch auto-add a project to a machine (the owner decides where copies live).

Risks: item 6 can newly refuse a handoff that worked by luck with stale member lists; the refusal must name the stale entry.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Agent clone timeout is 10 minutes, matching the caller.
- D-02 An unlinked copy is a failure for agents, not a success with a warning.
- D-03 The add-to-machine job stays in the browser.
### Open
- none

## Tasks

### T-01 add_to_machine: no refusing next, resume an existing clone
- AC: AC-01, AC-04, AC-10 | Files: apps/server/src/mcp/toolkits/project/addToMachine.ts, apps/server/src/mcp/toolkits/project/addToMachine.test.ts | Test: bun run --cwd apps/server test addToMachine

### T-02 Launch links an unlinked copy; clone timeout
- AC: AC-02, AC-03, AC-10 | Files: apps/server/src/mcp/toolkits/project/remoteLaunch.ts, apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/handlers.test.ts | Test: bun run --cwd apps/server test remoteLaunch handlers

### T-03 Worktree handoff without an origin
- AC: AC-05, AC-10 | Files: apps/server/src/git/GitWorkflowService.ts, apps/server/src/mcp/WorktreeMcpService.ts, apps/server/src/mcp/WorktreeMcpService.test.ts | Test: bun run --cwd apps/server test WorktreeMcpService

### T-04 Migrate refuses before interrupting; reciprocal project match
- AC: AC-06, AC-07, AC-10 | Files: apps/server/src/handoff/HandoffMoves.ts, apps/server/src/handoff/HandoffMoves.test.ts, apps/server/src/handoff/handoffState.ts, apps/server/src/handoff/handoffState.test.ts, apps/server/src/handoff/HandoffReceiver.ts | Test: bun run --cwd apps/server test HandoffMoves handoffState

### T-05 Server refuses take-theirs on a diverged repository
- AC: AC-08 | Files: apps/server/src/fleet/folderTransfer/reconcile.ts, apps/server/src/fleet/folderTransfer/reconcile.test.ts | Test: bun run --cwd apps/server test reconcile

### T-06 Web job runner reports and resumes
- AC: AC-09, AC-10 | Files: apps/web/src/components/AddToMachineJobRunner.tsx, apps/web/src/components/AddToMachineJobRunner.test.tsx | Test: bun run --cwd apps/web test AddToMachineJobRunner
