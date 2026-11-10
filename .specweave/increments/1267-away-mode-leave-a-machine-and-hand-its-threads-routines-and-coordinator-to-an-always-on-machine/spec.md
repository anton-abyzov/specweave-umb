# Away mode: leave a machine and hand its threads, routines and coordinator to an always-on machine

## Problem

Closing the M4's lid stalls its work. On November 9, 2026, the Instagram routine had to move to Ministorm (an always-on Linux box). The coordinator stopped with "Ministorm has to let the M4 manage its routines" and fell back to manual steps on both machines. See the screenshot `~/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-db80fffc-f757-4199-b969-525b70f9136b.png`.

The pieces exist, but nothing joins them, and the gaps are real (all in `specwithcode-dev`):

- **Threads:** `handOffMachine` (`apps/server/src/handoff/HandoffMoves.ts:861-917`) moves only running threads with handoff mode on. Queued threads and threads with handoff mode off stay behind. Queued messages never travel. The reason is only `manual` or `sleep`, and `document.machineRun` keeps just the last run.
- **Routines:** routines have no machine field. Coordinator-owned routines (`ownThread`) are copied to an armed standby without their run state (`apps/server/src/scheduledTasks/ScheduledTaskCopies.ts:72-90`). They rest there until that copy coordinates. Routines bound to a worker thread, and webhook routines, never move. Every non-legacy grant is refused routine changes (`apps/server/src/mcp/workGrantAccess.ts:439-454`), and no grant scope exists that allows them. That refusal is the blocker in the screenshot.
- **Coordinator:** a voluntary handover exists only as a person takeover behind a UI gate (10 minutes unreachable, `apps/web/src/studio/projectLink.ts:110-128`). That path never claims the worker epoch and never adopts remote workers. A sleeping lease does not trigger a takeover: the standby fires at least 5 minutes later (`apps/server/src/project/CoordinatorStandbyWatch.ts:86-182`).
- **Lid close:** the `suspend` hook gives 5 seconds, runs in the renderer, is dropped when no window exists (`apps/desktop/src/window/DesktopWindow.ts:1496`) and never checks the battery.
- **Grants:** missing grants show up mid-move as text, one thread at a time. No single preflight or request exists.
- **Bring back:** there is no bring-back action or summary. On wake nobody sees what happened.

## Scope

**In:**

- One Away action: an app menu item, a tray item, a rebindable hotkey, a command palette entry, and a `/away` and `$away` composer command (plus `/back`) that every harness resolves without a model turn.
- A remembered target machine.
- A preflight that lists, per item, what moves, what stays and why, and every missing grant or link with one request button.
- The move itself: threads (running, queued and handoff mode off), coordinators by planned handover, and routines with their run state and `brief.output` state files.
- A persisted Away session with a summary.
- Bring back.
- An optional trigger on sleep while on battery, with a grace period, run server-side.

**Out:**

- Moving webhook routines. Their URL is tied to the machine; they stay paused and are listed.
- Personal-assistant projects (refused today).
- Linking unlinked projects automatically. The preflight names the link step instead.
- Windows and Linux lid triggers. The trigger is macOS first; the manual action works on every platform.

## Acceptance Criteria

- [ ] AC-01: `away.preflight({target})` returns an AwayPlan with one row per thread, routine and coordinator, each with an action (`move`, `handoff-ready`, `stay`, `pause`) and a reason, plus `missingGrants[]`. Each missing grant has a kind (`work-grant`, `routines`, `project-link`, `provider`, `secret-file`), a machine and a fix action. Nothing is changed.
- [ ] AC-02: A new work-grant capability `routines` lets a grantee's coordinator create, enable, disable and delete routines for projects in the grant. Without it, the existing `outside_grant_scope` refusal stays. The routine records the grant it was made under. Settings > Machines > Who can run work here shows and toggles it.
- [ ] AC-03: The one-button "Request access" sends every missing grant in the plan to the target as a single pending request. The target owner sees it on any device and approves it in one action. The plan re-runs when approval lands.
- [ ] AC-04: `away.start` moves every running or queued thread, with handoff mode on or off, through the existing move path with reason `away`, carrying the queued messages. A thread that cannot move (worktree set, local-only path, provider or model missing on the target, missing secret file) stays and is marked handoff-ready with a reason the summary shows. It is never stopped with a final user stop.
- [ ] AC-05: Each project whose coordinator is on this machine, and that has running work or enabled routines (per D-03), is handed to the target by a planned handover: target takeover at epoch+1, then supersede here, then worker epoch claim and remote worker adoption. At no point are both copies active.
- [ ] AC-06: Enabled routines move with their run state (`next_run_at`, `last_run_*`, `run_count`, `onceGeneration`) and `brief.output` files. The source copy is disabled (marked `paused-for-away`) before the target copy is enabled, and the enable step is acknowledged. No routine fires on both machines. An interval routine does not fire immediately on the target if the source ran it within its interval. Webhook routines are paused here and listed.
- [ ] AC-07: The Away session (target, trigger, start and finish times, and per-item results for threads, routines and coordinators) persists on the server. It survives a restart and an older server reading the file. One summary shows what moved, what stayed and why, on this machine and in any client.
- [ ] AC-08: "Bring back" reverses the session. It continues moved threads here, hands coordinators back, moves routines back with their state and re-enables routines paused for Away. It re-arms the target as this machine's standby. It never revokes a grant. Trigger and default behavior follow D-02.
- [ ] AC-09: The sleep trigger (off, on battery, or always) runs from the desktop main process to the local server, not the renderer. Within the 5-second suspend window it records an away intent on the target. The target starts the handover after the grace period, unless this machine reports back first, so a lid close with no window still moves work.
- [ ] AC-10: Entry points: File > "Leave This Machine…" and "Bring Work Back", tray items, the palette entries, the keybinding command `away.start` (default `mod+alt+l`) and the composer commands `/away`, `$away` and `/back`. All of them open the same plan and summary. The remembered target is preselected, and the default target is the first ready Linux or always-on machine.

- [ ] AC-11: Pairing records each work grant as `own` (the same person's machines) or `team`. A grant is `own` while its coordinator also holds a management pairing on the worker (it joined that machine as its main machine) and the grant is not marked another person's; the worker checks this locally. Settings > Machines shows the kind ("Your machine" or "Shared"). (Changed from a fleet owner key, November 10, 2026: the management pairing is already the proof of one owner, and needs no new key.)
- [ ] AC-12: A routine's owner is its runner's copy: the copy on the machine whose coordinator holds the current epoch. Routines made under an `own` grant carry `grantedBy.kind = own` and count as the owner's. No separate owner column (per D-12).
- [ ] AC-13: Under an `own` grant, the other machine's work may change, run and delete a routine whose owner matches. `team` grants keep today's `grantedBy` rule. A routine made on the M4 can be edited from Ministorm's work and the reverse, with no setting changed by hand.
- [ ] AC-14: New `own` grants default to `routines: true`. Existing non-legacy grants between the same owner's machines are upgraded once with an audit line (per D-09). `team` grants stay off.
- [ ] AC-15: Coordinator-owned routines replicate from the runner to every linked `own` machine over the authenticated lease route, not only to the standby. An edit, run or delete made on a resting copy is forwarded to the runner under the `own` grant and returns with the next beat; the next beat never overwrites an unforwarded edit. If the runner is unreachable, the edit is refused with "Runner offline: <machine>. Run here first." A copied database row never fires (per D-12).
- [ ] AC-16: The runner is the copy whose coordinator holds the current epoch; only it fires (`ScheduledTaskCoordinatorGate`). Away, Bring back and Run here move it with the coordinator claim at epoch+1, in the AC-06 order and with run state. A routine never fires on two machines (per D-12).
- [ ] AC-17: When a routine's runner has been unreachable for more than 2 intervals, other machines show "Runner offline: <machine>" with a one-click Run here. Automatic failover only happens for routines opted in (per D-10).

## Approach

### Data and contracts (`packages/contracts`)

- `away.ts`: AwayPlan, AwaySession, AwayItemResult and AwayConfig `{ target, sleepTrigger: 'off' | 'on-battery' | 'always', graceMinutes, bringBack }`.
- RPCs `away.preflight`, `away.start`, `away.bringBack` and `away.snapshot`.
- Add `away` and `back` to `ThreadExecutionReason`, `TakeoverReason` and `HandOffMachineInput.reason`.
- Add `routines` to the work-grant policy.
- Store the config and session in `handoff-mode.json` as optional keys with decoding defaults, so older files still decode. Reuse `sleepTarget` as the Away target, so there is one remembered target.

### Server (`apps/server/src/away/`)

- `AwayPlanner`: composes the existing preflights (`HandoffMoves.preflight`, `listMachines`, project link state, standby armedFor and the grant policy) into one plan.
- `AwayRunner`: runs the session in three ordered stages, each idempotent and resumable from the persisted session:
  1. Coordinator handover per project, through a new planned handover in `ProjectLinkStandby` (lease kind `handover`). It reuses `takeoverLocked`, then `supersede`, `claim_epoch` and `RemoteWorkerAdoption.adopt`.
  2. Routines. Coordinator-owned routines ride the handover replica with their run state. Worker-bound routines go through the new grant-scoped transfer. Webhook routines are paused.
  3. Threads, through `handOffMachine`, extended to take queued and mode-off threads and to carry queue items.
- Away intent route for the sleep trigger. `CoordinatorStandbyWatch` gets a takeover on away intent after the grace period.
- Bring back: `continueHere` in bulk for `continuedOn` threads, a reverse planned handover, routines back, re-arm.

### Grants and request (`apps/server/src/fleet`, `apps/web/.../settings`)

- `routines` capability in `workGrantPolicy.ts` and `workGrantAccess.ts`, plus routine tools in `REMOTE_TOOL_ALLOWLIST`.
- One pending-request type `fleet-access` that lists the needed grants and links, approved on the target.

### Desktop

- `DesktopApplicationMenu.ts` and `ElectronTray.ts`: the menu and tray items.
- `DesktopHandoffSleep.ts`: battery check and a POST of the away intent from the main process. Forward `resume` and `unlock-screen` to drive the Bring back prompt.

### Web

- `AwayDialog` (plan, then move, then summary).
- `composerAppCommands.ts`: `/away`, `$away` and `/back`.
- Palette entry, keybinding, and settings rows under Moving work between machines.

### Rejected

- **A user-installed `$away` skill.** Skills are not shipped by the app and would be missing on a fresh Ministorm. The app command answers `$away` everywhere.
- **`startCoordinator`.** It leaves two active coordinators.
- **Stop-all before moving.** A user stop is final, so the work would not resume.
- **Running the sleep path in the renderer.** It is dropped when no window exists.

### Risks

- Suspend can cut the move. That is why the target finishes from its side and every stage is resumable.
- Every hop creates a new thread id and worktree. Bring back adds another hop; this is accepted and shown in the summary.
- An update idle-restart during Away. The runner holds the update idle lease while running.

## Decisions

### Asked
- D-01 Sleep trigger default → on battery, 2-minute grace (user, November 9, 2026)
- D-02 Bring back → ask on wake, one click (user)
- D-03 Which coordinators move → only projects with live work (user)
- D-08 Routine sync mechanism → B: owner-signed copies peer-to-peer, one runner lease per routine (user, November 10, 2026). Research: `routine-sync.html` in this folder.
- D-09 Routine permission between your own machines → on for new `own` grants, plus a one-time upgrade of existing same-owner grants with an audit line (user)
- D-10 Runner offline → show it, one-click Run here; automatic takeover only as a per-routine opt-in (user)
- D-12 Routine edits → single writer: only the runner's copy is written, edits on other machines are forwarded to it, and the runner is the coordinator epoch. This replaces the signed edit-anywhere copies of D-08 (user, November 10, 2026)

### Defaulted (change any before sw-do)
- D-04 One remembered target: reuse `HandoffConfig.sleepTarget`. Default suggestion is the first ready machine without a battery, otherwise the first ready machine.
- D-05 `$away` and `/away` are app composer commands, not a user-installed skill.
- D-06 Routines are always handed over with their run state. The source is disabled before the target is enabled. Webhook routines stay paused.
- D-07 Threads that cannot move are marked handoff-ready with a reason, never stopped.
- D-11 Git export of routines → none in 1267 (recommended default, not asked)

### Open
- none

## Tasks

### T-01 Contracts, config and session persistence
- AC: AC-01, AC-07 | Files: packages/contracts/src/away.ts, packages/contracts/src/handoffMode.ts, packages/contracts/src/threadExecution.ts, apps/server/src/handoff/handoffState.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/handoff/handoffState.test.ts packages/contracts/src/away.test.ts

### T-02 Routines grant capability and grant-scoped routine transfer
- AC: AC-02, AC-06 | Files: apps/server/src/fleet/workGrantPolicy.ts, apps/server/src/mcp/workGrantAccess.ts, apps/server/src/fleet/RemoteStudioMcpClient.ts, apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/mcp/workGrantAccess.test.ts apps/server/src/scheduledTasks/ScheduledTaskTransfer.test.ts

### T-03 Away planner and one-request access
- AC: AC-01, AC-03 | Files: apps/server/src/away/AwayPlanner.ts, apps/server/src/away/AwayAccessRequest.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/away/AwayPlanner.test.ts

### T-04 Planned coordinator handover
- AC: AC-05 | Files: apps/server/src/project/ProjectLinkStandby.ts, apps/server/src/project/CoordinatorLeaseRoute.ts, apps/server/src/project/CoordinatorStandbyWatch.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/project/CoordinatorPlannedHandover.test.ts

### T-05 Away runner: threads with queues, routines, session, Bring back
- AC: AC-04, AC-06, AC-07, AC-08 | Files: apps/server/src/away/AwayRunner.ts, apps/server/src/handoff/HandoffMoves.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/away/AwayRunner.test.ts

### T-06 Sleep trigger from the main process with grace
- AC: AC-09 | Files: apps/desktop/src/app/DesktopHandoffSleep.ts, apps/server/src/away/AwayIntentRoute.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/desktop/src/app/DesktopHandoffSleep.test.ts apps/server/src/away/AwayIntentRoute.test.ts

### T-07 Entry points and Away dialog
- AC: AC-10, AC-07 | Files: apps/desktop/src/window/DesktopApplicationMenu.ts, apps/desktop/src/electron/ElectronTray.ts, apps/web/src/components/away/AwayDialog.tsx, apps/web/src/studio/composerAppCommands.ts, packages/contracts/src/keybindings.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/web/src/studio/composerAppCommands.test.ts && node apps/web/tests/away-mode/verify.mjs /tmp/away-mode-report

### T-08 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17 | Files: none | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm typecheck && pnpm test

### T-09 Own-machine grant kind and owner key
- AC: AC-11, AC-14 | Files: packages/contracts/src/studioFleet.ts, apps/server/src/fleet/WorkGrants.ts, apps/server/src/fleet/workGrantPolicy.ts, apps/server/src/fleet/FleetWorkerGrants.ts, apps/web/src/components/settings/MachineWorkGrants.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run packages/contracts/src/studioFleet.workGrantRoutines.test.ts apps/server/src/fleet/FleetWorkerGrants.test.ts

### T-10 Routine owner field, backfill and own-owner rule
- AC: AC-13 | Files: packages/contracts/src/scheduledTask.ts, apps/server/src/scheduledTasks/ScheduledTaskStorage.ts, apps/server/src/mcp/routineOwnership.ts, apps/server/src/mcp/workGrantAccess.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/mcp/routineOwnership.test.ts apps/server/src/mcp/workGrantAccess.test.ts

### Design note for T-11 to T-13 (November 10, 2026, D-12)

Code on `main` already does half of D-08. For a linked project's coordinator-owned routines (`ownThread`):
- The coordinator sends them to its standby with every lease beat: `CoordinatorLease` → `RoutineCopies.snapshot` / `replace`, and planned handover carries them too.
- `ScheduledTaskCoordinatorGate` fires them only where the coordinator holds the current epoch. That means one runner, and a copied row never fires.
- Gaps:
  1. An edit made on the standby is overwritten by the next beat.
  2. Copies reach only the standby.
  3. Worker-bound routines never replicate.
  4. Resting copies show no runner or offline state.

D-12, single writer: the runner's copy is the only one written. An edit on a resting copy is forwarded to the runner over the `own` grant (T-09/T-10 allow it) and comes back with the next beat.
- No last-writer-wins, no conflict copies and no extra signatures: copies travel only over the authenticated, proof-bound lease route.
- The runner lease stays the coordinator epoch, with no new per-routine lease.
- Run here reuses the coordinator claim at epoch+1.
- If the runner is offline, edits are refused with "Runner offline: <machine>. Run here first."
- Replicas go to every linked `own` machine, not only the standby.

### T-11 Replicate to every own machine; forward edits to the runner
- AC: AC-12, AC-15 | Files: apps/server/src/scheduledTasks/ScheduledTaskCopies.ts, apps/server/src/scheduledTasks/RoutineForward.ts, apps/server/src/project/CoordinatorLease.ts, apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/scheduledTasks/ScheduledTaskRpc.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/scheduledTasks/RoutineForward.test.ts apps/server/src/scheduledTasks/ScheduledTaskCopies.test.ts

### T-12 Runner is the coordinator epoch; Away and Run here use it
- AC: AC-16, AC-06, AC-08 | Files: apps/server/src/scheduledTasks/ScheduledTaskCoordinatorGate.ts, apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts, apps/server/src/away/AwayRunner.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/scheduledTasks/ScheduledTaskTransfer.test.ts apps/server/src/away/AwayRunner.test.ts

### T-13 Runner offline and Run here
- AC: AC-17 | Files: apps/server/src/scheduledTasks/RoutineRunner.ts, apps/web/src/components/scheduledTasks/RoutineRunnerBadge.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm exec vp test run apps/server/src/scheduledTasks/RoutineRunner.test.ts
