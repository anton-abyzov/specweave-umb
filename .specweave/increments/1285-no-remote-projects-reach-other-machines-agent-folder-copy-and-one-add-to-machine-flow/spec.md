# No-remote projects reach other machines: agent folder copy and one Add to machine flow

## Problem

From the New project review of November 10, 2026 (`.specweave/reviews/new-project-2026-11-10/report.html`), in the SpecWithCode app (`specwithcode-dev`). A project made with New project has no Git remote until it is published. Until then:

1. Agents have no route to another machine. `studio_thread_launch` with `machine` fails and hints "call studio_project_add_to_machine" (`apps/server/src/mcp/toolkits/project/remoteLaunch.ts:373`). That tool refuses: "has no git remote another machine could clone. Push it to a remote first, or pass cloneUrl." (`apps/server/src/mcp/toolkits/project/addToMachine.ts:113-116`), and `cloneUrl` is rejected together with `projectId` (`:138-139`).
2. `studio_file_transfer` refuses folders and points at a UI flow an agent cannot start: "Move folders with Handoff > Copy files" (`apps/server/src/mcp/toolkits/fileTransfer/files.ts:77`). The folder copy engine exists (`apps/server/src/fleet/folderTransfer/`) and is reachable only from the browser.
3. The same label does two things. "Add to another machine…" in the project menu opens `HandoffShare`, which offers "Review files to transfer" for a no-remote project (`apps/web/src/components/studio/HandoffShare.tsx:239`, `:309`). In the Run on picker it opens `AddToMachineDialog`, which lists the machine as addable (`apps/web/src/studio/addToMachine.ts:170-174`) and then ends in "Push it to GitHub or another host first." (`apps/web/src/components/chat/AddToMachineDialog.tsx:303`).
4. Plain Add for a project with a remote sends tracked files only and does not say so: `HandoffShare.tsx:194-195` hard-codes `copyIgnored: false, secrets: []`. The next thread migrate then fails its preflight with "no .env" (`apps/server/src/handoff/handoffPreflight.ts:70-72`), which names no remedy.
5. `studio_machine_list` computes why a project does not match a machine and drops it (`apps/server/src/fleet/RemoteWorkers.ts:778`).

## Scope

In: an agent route that puts a no-remote or non-Git project on another machine through the existing folder copy engine and links it; the Run on picker offering the folder copy instead of a dead end; a visible note on plain Add that ignored files and secrets stay behind, with the way to send them; remedy text on the "not linked here" and "no <path>" refusals; the match reason in `studio_machine_list`.

Out: changes to the folder copy engine's classification or wire format; sending secrets without the owner's approval card; grant scope rules (linked/listed machines still refuse agent adds); the unlinked-copy loop and clone timeout (1287); creating a project directly on a remote machine (1288).

## Acceptance Criteria

- [ ] AC-01: `studio_project_add_to_machine` on a project with no Git remote, or one that is not a Git repository, copies the project folder to the target through the folder copy engine, registers it there and links it as a member. The result reports `linked: true`, the destination path and a count of files left out (secrets, rebuildable folders).
- [ ] AC-02: The agent copy never sends secret files (`.env*`, key files). The result lists their paths and says to send each with `studio_file_transfer`, which keeps its owner approval card.
- [ ] AC-03: The agent copy refuses, without writing anything, when the destination folder exists and is not empty, when the target lacks the folder copy capability (message says to update SpecWithCode there), and when team rules block folder copy.
- [ ] AC-04: The refusal at `addToMachine.ts:113-116` and the hint at `remoteLaunch.ts:373` no longer suggest `cloneUrl` for a project that is given by `projectId`; a launch on a machine without the project names the one call that will work.
- [ ] AC-05: In the Run on picker, "Add to another machine…" on a no-remote project opens the folder copy review (the same one the project menu opens) instead of the "Push it to GitHub" blocker.
- [ ] AC-06: Plain Add of a project with a remote shows, before the user confirms, that ignored files and secrets stay on the source and offers "Copy ignored files" and "Include secrets" in place. The defaults stay off.
- [ ] AC-07: The receiver refusals "this project is not linked here" (`apps/server/src/handoff/HandoffReceiver.ts:298`) and "no <path>" (`handoffPreflight.ts:70-72`) each end with the action that fixes them (Link… or add to machine; send the file with `studio_file_transfer` or Copy local files).
- [ ] AC-08: `studio_machine_list` returns the reason a project does not match a machine next to `match`.
- [ ] AC-09: Existing behaviour holds for a project with a remote: clone, register, link; `addToMachine.test.ts`, `HandoffShare.test.tsx` and `AddToMachineDialog.test.tsx` pass with copy-only updates.

## Approach

1. Server: add a service entry point that runs a folder copy source-to-destination without a browser session (the engine's RPCs require browser scopes, `packages/contracts/src/clientRpcPermissions.ts:255-295`). Reuse `MachineHandoff` offer, `destinationService` approve and apply, with the selection fixed to "everything except secrets and rebuildable folders" and conflicts fixed to refuse. Then `linkCopy` as today.
2. `addToMachine.ts`: when `identity == null`, take the copy route instead of failing. Keep the existing-copy check first.
3. Texts: `remoteLaunch.ts` hint, `HandoffReceiver.ts`, `handoffPreflight.ts`, tool descriptions in `project/tools.ts` and `fileTransfer/tools.ts`.
4. `RemoteWorkers.ts:778`: keep `reason` in the row; extend the contract with an optional field.
5. Web: `DraftMachinePicker.tsx` routes a no-remote project to `ProjectMachineHandoff` with the copy intent; `HandoffShare.tsx` gains the two toggles and the note, passing them to the job.

Rejected: making `studio_file_transfer` accept directories (it would duplicate the copy engine without reconcile, backups or undo). Rejected: auto-publishing to GitHub to get a remote (the owner did not ask for a repository).

Risks: an agent-started copy has no preview step, so it must refuse on any conflict rather than choose; large folders need the existing entry cap and disk check to surface as tool errors.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The agent copy excludes rebuildable folders and secrets and refuses on a non-empty destination.
- D-02 The new behaviour lives in `studio_project_add_to_machine`, not a new tool.
- D-03 Grant scope "linked" or "listed" keeps refusing agent adds, as today.
### Open
- none

## Tasks

### T-01 Headless folder copy entry point on the server
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/agentCopy.ts, apps/server/src/fleet/folderTransfer/agentCopy.test.ts | Test: bun run --cwd apps/server test agentCopy

### T-02 add_to_machine takes the copy route for no-remote projects
- AC: AC-01, AC-02, AC-03, AC-04, AC-09 | Files: apps/server/src/mcp/toolkits/project/addToMachine.ts, apps/server/src/mcp/toolkits/project/addToMachine.test.ts, apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/mcp/toolkits/project/remoteLaunch.ts, apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts | Test: bun run --cwd apps/server test addToMachine remoteLaunch

### T-03 Remedies in refusals and the machine list reason
- AC: AC-07, AC-08 | Files: apps/server/src/handoff/HandoffReceiver.ts, apps/server/src/handoff/handoffPreflight.ts, apps/server/src/fleet/RemoteWorkers.ts, packages/contracts/src/orchestratorMcp.ts, apps/server/src/mcp/toolkits/fileTransfer/files.ts | Test: bun run --cwd apps/server test handoffPreflight RemoteWorkers

### T-04 Run on picker opens the folder copy for no-remote projects
- AC: AC-05, AC-09 | Files: apps/web/src/components/chat/DraftMachinePicker.tsx, apps/web/src/components/chat/AddToMachineDialog.tsx, apps/web/src/components/chat/AddToMachineDialog.test.tsx, apps/web/src/studio/addToMachine.ts, apps/web/src/studio/addToMachine.test.ts | Test: bun run --cwd apps/web test AddToMachineDialog addToMachine

### T-05 Plain Add says what stays behind and offers to send it
- AC: AC-06, AC-09 | Files: apps/web/src/components/studio/HandoffShare.tsx, apps/web/src/components/studio/HandoffShare.test.tsx | Test: bun run --cwd apps/web test HandoffShare

### T-06 Two-machine check
- AC: AC-01, AC-05 | Files: apps/web/tests/folder-copy/verify.mjs | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node apps/web/tests/folder-copy/verify.mjs
