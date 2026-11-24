# Run on: add a project to another machine

## Problem

To work on a project from another paired machine today, the user sets the folder up there by hand, then links it. The user wants a "Run on" picker like the reference screenshots: machines that have the project, plus "Add to another machine ›", which clones and provisions the project on the chosen machine with a progress strip in the composer. When the destination already has a folder for the project, the app must consolidate it smartly instead of overwriting.

## Scope

In: the Run on menu in the composer (DraftMachinePicker), the "Add to another machine" dialog, clone with progress and Cancel, provisioning (ignored-file copy, secrets with an explicit tick), smart consolidation of an existing folder, registering the result as a linked member of the logical project (0948), and switching Run on to the new machine.

Out: two-way coordinator ownership (0969), thread handoff (0967), and machines that are not paired.

## Acceptance Criteria

- [ ] AC-01: Run on lists the machines that have this project (with type icon, online state and current marker), then "Add to another machine ›" with paired machines that lack it. Offline, needs-grant and needs-sign-in machines show that state and a fix action instead of being selectable. The Workspace section (current checkout, new worktree, previous worktree) stays.
- [ ] AC-02: When a paired machine has an unlinked folder of the same repository, the menu shows "Has a copy at <path> · Link" for it instead of offering a clone.
- [ ] AC-03: The dialog shows source machine and path, an arrow, destination machine and folder; Clone over SSH or HTTPS with the URL; Folder on <machine>; "Copy ignored files" with the note that folders git ignores whole (node_modules and similar) are left out; secret-like files (.env*) listed and unticked by default. Buttons Cancel and "Clone to <machine>".
- [ ] AC-04: Before cloning, the destination runs `git ls-remote` on the URL; a failure shows a sign-in fix message for that machine and does not start.
- [ ] AC-05: The composer shows a progress strip "Cloning <name> · Receiving objects · N% · size | speed" with Cancel; Cancel stops the clone and removes the partial folder.
- [ ] AC-06: Existing folder, same repository: link it, fast-forward when behind, never overwrite when diverged (import theirs as `swc/from-<machine>/<branch>`), copy only missing ignored files, and resolve file conflicts with keep mine, take theirs or keep both. Every change is undoable through folderTransfer undo.
- [ ] AC-07: Existing folder of a different repository, or a non-empty non-git folder: refuse and suggest another path.
- [ ] AC-08: On success the destination project is registered as a linked member of the logical project and Run on switches to it; a new thread there starts in the new folder.
- [ ] AC-09: Headless screenshots of the menu, dialog, progress strip and consolidation review in light and dark; a two-server test (local) proving clone, link and the consolidation cases.
- [ ] AC-10: Every machine has a short nickname of at most 16 characters that the user can rename from Settings → Connections and from the Run on menu. It is stored against the machine's environmentId (never the host name), defaults to the current short name, and is shared with paired machines over the fleet so M4, the Minis and the phone show the same name. One exported helper, `machineNickname(environmentId)`, returns it for thread rows, the coordinator switcher, notices and the phone.
- [ ] AC-11: Run on shows, for each thread, the execution machine the orchestrator chose, and lets the user pick another machine before the thread's first turn; after the first turn it is shown read-only.
- [ ] AC-12: Consolidation never links folders by name. The same repository is proven by a matching remote URL plus an explicit user action (Link), and the link records the source root mapping (environmentId, workspaceRoot).
- [ ] AC-13: Tests prove a rename propagates to a second server, a rename made while the peer is offline applies on reconnect, and conflicting renames resolve last writer wins. Native headless screenshots show the rename dialog and the Run on menu.

## Approach

Reuse apps/server/src/fleet/folderTransfer: apply.ts (cloneRepository step), classify.ts and secrets.ts (ignored and secret-like files), reconcile.ts (pure planner: RowStatus same/fast-forward/ahead/diverged/dirty/conflict/new/only-here, Choice keep-mine/take-theirs/leave-both/keep-both, PlanInput.clone), destinationScan.ts (find existing folders), undo.ts, transferGrant.ts (grant prerequisites). Clone progress comes from `git clone --progress` parsed on the destination and streamed over the fleet channel. ProjectCloneTracker.ts and ProjectEnvironmentService.ts already track clones; extend rather than duplicate. Linking uses the 0948 logicalProject members list.

## Decisions

### Asked

- None.

### Defaulted

- D-01: Secret-like files are never copied without an explicit tick (matches #486).
- D-02: A diverged existing folder is never rewritten; theirs is imported under `swc/from-<machine>/`.
- D-03: The default destination folder mirrors the source path relative to home.
- D-04: Nicknames live in each server's settings as `machineNicknames` (environmentId → name, updatedAt), so clients and the phone receive them on the existing settings stream. Servers exchange the whole map with each paired machine (management token, settings-write scope) after a change and every minute, merging last writer wins; an empty name means "use the default".

## Tasks

### T-01 Run on menu groups and states
- AC: AC-01, AC-02 | Files: apps/web/src/components/chat/DraftMachinePicker.tsx | Test: component tests

### T-02 Add to another machine dialog
- AC: AC-03, AC-04 | Files: new AddToMachineDialog.tsx, server pre-check RPC | Test: component and server tests

### T-03 Clone with progress and cancel
- AC: AC-05 | Files: folderTransfer apply.ts, ProjectCloneTracker.ts, composer progress strip | Test: server tests with a local bare repo

### T-04 Smart consolidation of an existing folder
- AC: AC-06, AC-07 | Files: folderTransfer reconcile.ts, destinationScan.ts, review UI | Test: planner and apply tests per case

### T-05 Register member and switch Run on
- AC: AC-08 | Files: logicalProject link path, DraftMachinePicker | Test: server test

### T-06 Evidence
- AC: AC-09 | Files: two-server script, screenshots | Test: headless Playwright, two local servers

### T-07 Machine nicknames: storage and fleet sync
- AC: AC-10, AC-13 | Files: contracts settings, shared machineNicknames.ts, server fleet/MachineNicknameSync.ts | Test: merge tests; two-server propagation, offline-then-reconnect and last-writer-wins tests

### T-08 Nickname helper and Rename UI
- AC: AC-10, AC-13 | Files: apps/web/src/studio/machineNickname.ts, RenameMachineDialog, Settings → Connections, Run on menu, label call sites | Test: helper and component tests, headless screenshots; notify 0967, 0969, 0970

### T-09 Per-thread execution machine in Run on
- AC: AC-11, AC-12 | Files: DraftMachinePicker, Run on menu, link path | Test: component tests

### T-10 Verify and close 0966
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
