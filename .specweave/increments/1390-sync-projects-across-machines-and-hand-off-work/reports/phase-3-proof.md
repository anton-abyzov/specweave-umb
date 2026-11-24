# Phase 3 proof on two real machines (1390 T-08)

Run on November 19, 2026, 12:13 AM to 1:23 AM Eastern, on the throwaway project `t08-handoff-proof` only. Machines: m4 (SpecWithCode 1.0.374), M1 (1.0.375), M5 (1.0.374). The owner chose M1 instead of the M5 for proofs 1 to 4 and 6, because a headless window cannot sign in to the M5 (it only has a Connect address). Proof 5 ran on m4 to M5 and again on m4 to M1.

Evidence folder: `/Users/antonabyzov/.specwithcode/m4/evidence/1390-phase-3-proof/`. File names below are relative to it. Code lines are at tag `v1.0.374` of the app repository.

| Proof | Verdict | Why, in one line |
|---|---|---|
| 1. Held thread counts as idle | Proven | A coordinator move m4 to M1 passed while a thread was held `handing-off` with its turn interrupted |
| 2. Held thread survives the move and continues | Cannot be shown with today's released code | No call holds a thread without handing it off; the held thread's record survived the move but nothing can continue it |
| 3. Started thread reports to the coordinator on the target | Fails | The worker finished on M1 after both moved; the M1 coordinator got no report |
| 4. Routine runs once on the target, never on the source | Fails | The routine rests on m4 after the move and does not exist on M1, so it runs nowhere |
| 5. Thread handed off alone reports to the coordinator on the source | Fails | Same on m4 to M5 and m4 to M1: the worker finished, the m4 coordinator got no report |
| 6. Window dies after the hold, and after the fence | Fails | After the fence: proven with limits. After the hold: the thread stays held with no way to continue or release it |

## Proof 1: a held thread counts as idle for the coordinator's move

**Done.** Control first: with worker `wA-worker` running on m4, I opened the move dialog on the M1 page in the headless window. It refused at 12:49 AM: "A thread is still working or waiting for you… Running work wA-worker" (`a-05`, `a-07`). After `wA-worker` was interrupted the move m4 to M1 passed (operation `b303309f`, transferring 12:53:20 AM, transferred 12:53:41 AM, `a-11-m4-move-timeline.txt`).

Then the real case. At 1:10:14 AM worker `wC-worker` was held by a thread handoff to M1 (lease `handing-off`, run interrupted at 1:10:14 AM) and stayed held (see proof 6). At 1:11:54 AM and 1:19:01 AM the idle check's own SQL returned no busy thread on m4 (`p1-10-m4-idle-with-held-thread.txt`). I then moved the coordinator m4 to M1 from the M1 page: the dialog's checks passed with no refusal (`p1-12`), binding went active, transferring at 1:19:53 AM, transferred at 1:20:00 AM (operation `869c02a3`, `p1-13-m4-binding-during-move.txt`). The held thread's record was unchanged after the move (lease `handing-off`, epoch 0).

**Observed.** Pass on both machines: m4 ran the source checks with the held thread present, M1 ran the destination checks (the held thread does not exist on M1). The check never reads the lease: it reads runs, runtime requests, effects and provider sessions (`apps/server/src/fleet/folderCopyPreparation.ts:96-100`). A held thread is idle to it only because its run is `interrupted` and its session is `ready`.

**Not shown.** A hold made by the hold-only call Phase 3 plans, because that call does not exist. A held thread whose turn ignores the interrupt would still have a running run and block the move.

**Verdict: proven.**

## Proof 2: a held thread survives the coordinator's move and continues on the target

**Done.** (a) `wC-worker`, held as above, through the coordinator move at 1:19:53 AM. (b) `wA-worker`, interrupted and idle, handed off m4 to M1 at 12:54:42 AM after the coordinator had moved, became `handoff:c0f59138…` on M1, and answered "DONEA" to "continue" by 12:55:25 AM (`p2-10-handoff-wA-after-coordinator-moved.json`). (c) For the 45 s settle window: worker `w2-stubborn-worker` ran a Python child that ignores signals; I handed it off to M5 at 12:31:10 AM (`p2-02-timeline.txt`).

**Observed.** (a) The held record survived the move intact, but it cannot continue: a new handoff is refused with `busy`, "A handoff of this thread did not finish; it stays paused until the other machine answers." (`apps/server/src/handoff/HandoffMoves.ts:782-789`), and a message to it fails to dispatch (`p6-24-window-B-retry-handoff.txt`). (b) A thread handed off after the move does continue on the target. (c) The turn ended 3 s after the interrupt (run `interrupted` at 12:31:12 AM), so no turn outlived 45 s. In code, a turn that does not end in 45 s only logs "Handoff interrupted a turn that did not end in time" (`HandoffMoves.ts:514`) and the move carries on with the turn still running; the hold is not released.

**Missing piece.** A hold-only call (planned `handOff.session` or similar) that holds and interrupts without a takeover, and a matching continue-on-target call. The smallest thing that would make this provable: that call plus a test-only way to keep a turn alive past the interrupt.

**Verdict: cannot be shown with today's released code.**

## Proof 3: a thread the coordinator started reports to the coordinator on the target

**Done.** The m4 coordinator started `wA-worker` (agent, MCP). The coordinator moved m4 to M1 (12:53:41 AM). `wA-worker` was handed off m4 to M1 (12:54:56 AM) and finished there at 12:55:25 AM.

**Observed.** At 1:00 AM and 1:01 AM the M1 coordinator (`project-coordinator:mcp:f4efd07f…`) had nothing after 12:54:20 AM: no "Worker … finished" message (`p3-01-m1-coordinator-no-report.txt`). Locally the same report arrives 45 s after a worker ends (`p5-00-baseline-local-wake.txt`).

**Cause in code.** The report only goes to top-level threads that an agent started through MCP: `createdBy === "agent" && creationSource === "mcp"` (`apps/server/src/project/LaunchedWorkerWake.ts:124-129`). The continuation on M1 is created as `createdBy: "system"`, `creationSource: "server"` (`apps/server/src/handoff/HandoffReceiver.ts:793-794`). The launcher is found from the thread's first user message, which must come from an agent (`LaunchedWorkerWake.ts:171-173`). A continuation's first message comes from the system ("Continue where you left off", seen on `wD-worker`'s continuation in proof 5). Here `wA-worker` was idle when handed off, so its finishing run on M1 was started by my own "continue" message, not by the system. The coordinator on M1 is also a different thread id from the one that launched the worker.

**A fix would have to** carry the launcher across the handoff (the source's coordinator thread, mapped to the new coordinator id after a move) and let the wake accept continuation threads.

**Verdict: fails.**

## Proof 4: a routine the coordinator owns runs once on the target and never on the source

**Done.** The m4 coordinator created routine `t08-routine` (every 60 s, owned by the coordinator, its check appends a line to `/tmp/t08-routine-fires.log`). Sampled the routine row every second through the move.

**Observed.** m4 ran it at 12:48:42, 12:50:04, 12:51:23 and 12:52:26 AM. The slot due at 12:53:26 AM, during `transferring`, waited. After `transferred` m4 rested it with "Not run on this machine: another machine runs this project's coordinator." No m4 run from 12:52:26 AM to 1:04 AM. On M1 at 12:55:43 AM and 1:01:07 AM: no routine row for the project and no log file (`p4-01`, `p4-02`, `p4-03`). After the coordinator moved back to m4, m4 ran it again from 1:05:16 AM.

**Cause in code.** Routines owned by the coordinator are excluded from transfer: `isTransferredRoutine` is `task.ownThread !== true && …` (`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:112-113`), and the coordinator move carries no routine code. The gate rests it on any machine that is not the active coordinator (`ScheduledTaskCoordinatorGate.ts:83-85`).

**Not shown.** The cases "falls due between steps 3 and 5" and "the first answer to turning it on is lost" need a transfer for these routines first.

**A fix would have to** move coordinator-owned routines with the coordinator (stage on the target, turn on, turn off on the source), and only then can the lost-answer case be tested.

**Verdict: fails.**

## Proof 5: a thread handed off without its coordinator reports to the coordinator on the source

**Done.** Baseline: `w5-worker` finished on m4 and the m4 coordinator got "Worker … finished: completed" at 12:15:28 AM. Then, twice, a worker the m4 coordinator started was handed off alone while the coordinator stayed on m4:

- m4 to M5: `w5b-worker` handed off at 12:16:21 AM, finished on M5 at 12:21:30 AM. No report on m4 at 12:28 AM (`p5-04`, `p5-06`, `p5-07`).
- m4 to M1: `wD-worker` handed off at 1:13:55 AM while running, resumed on M1 by itself and answered "DONED" at 1:15:04 AM. No report on m4 at 1:18:06 AM (`p5r-02-handoff-wD.txt`, `p5r-03-m4-no-report-three-minutes-after-finish.txt`).

**Observed.** It fails the same way on both pairs. The m4 record shows the lease `fenced`, `continuedOn` the other machine, and nothing that follows the continuation.

**Cause in code.** On the source the run ends `interrupted`, and only `completed` or `failed` runs report (`LaunchedWorkerWake.ts:120-121`, `:178`). On the target the continuation is a system thread (`HandoffReceiver.ts:793-794`), so the wake skips it (`LaunchedWorkerWake.ts:124-129`). Nothing records a remote follower for a thread handoff; that exists only for `studio_thread_launch` with a machine.

**A fix would have to** make the target report the continuation's end back to the source coordinator (or register a follower at handoff time), keyed by the source thread id.

**Verdict: fails.**

## Proof 6: the driving window dies

**After the fence, before the acknowledgement (proven with limits).** I started a move M1 to m4 (operation `fe3f78b1`) at 1:04:07 AM and killed my headless window by PID the moment m4's binding changed, at 1:04:16 AM (`p6-03-kill-after-fence-timeline.txt`). State right after: m4 `active`, epoch 2; M1 `transferring`, epoch 1, fence written, no acknowledgement (`p6-07`, `p6-08`). Exactly one active coordinator. Messages to threads in the M1 project were refused. A window with a fresh profile and only an m4 sign-in showed no recovery card, only "Previous coordinator … Read only · Offline" (`p6-09`). A second window on the old sign-ins but with no handoff pointer in its storage (`p6-11`) showed "Finish handing off t08-handoff-proof to m4. The handoff stopped partway." (`p6-12`). Its menu showed "m1 Handing off the coordinator…" and "m4 Coordinator" (`p6-13`). Pressing "Finish handoff" at 1:07:53 AM finished it: the card was gone by 1:08:16 AM and M1 read `transferred` at 1:08:59 AM, the time of my read, not of the change (`p6-14`, `p6-15`). Release ("keep it here") was not pressed.

The point tested: my kill fired on the first change seen on m4, which was the destination already `active` at epoch 2. I did not catch the earlier moment where the fence is written on the source and the destination has not yet taken over, so "exactly one coordinator" is shown only for the point after the destination took over.

What this shows: recovery runs from the server's binding, not from the dead window's stored pointer. What it does not show: a window with no sign-in on the source can recover; it needs sign-ins on both machines. My recovering window reused the dead window's sign-ins, because only one M1 sign-in was allowed.

**After the hold.** At 1:10:10 AM I started a thread handoff of `wC-worker` to M1 and killed the window at 1:10:14 AM, the moment the lease became `handing-off` (`p6-21-kill-after-hold-timeline.txt`). The thread stayed `handing-off` with `pendingTakeover: null` and no continuation on M1, still so at 1:20 AM (`p6-22`). A fresh window's handoff retry was refused `busy` at 1:12:35 AM, and a message to it failed (`p6-24`). Nothing releases it: the resend path needs a `pendingTakeover` (`HandoffMoves.ts:684-689`), the heartbeat skips records without one (`:1348`), and new handoffs are refused (`:782-789`). The m4 trace confirms the cause: the `handoffMode.handOff` call started at 1:10:11.351 AM and ended `Interrupted` ("All fibers interrupted without error") 2.8 s later, when the window died (`p6-25-m4-trace-handoff-cut-by-window-death.txt`). The client's disconnect cut the server's handoff between the hold and the takeover. Still held at 1:28 AM.

**A fix would have to** run the hold-to-takeover sequence so that a dropped client cannot cut it, or write `pendingTakeover` before the hold, and give the user a release for a hold with no takeover.

**Verdict: fails** (after the fence proven, after the hold fails).

## How each handoff was made, and run ids

- Coordinator moves: the move dialog in my headless window (M1 page "Continue here", or m4 page "Continue here" for the move back). Operations `b303309f` (m4 to M1), `fe3f78b1` (M1 to m4, window killed), `869c02a3` (m4 to M1 with a held thread).
- Thread handoffs to M5 (`w5b-worker`, `w2-stubborn-worker`): the m4 coordinator's `studio_thread_migrate` tool, asked in one-line messages (`rig/msgs/p5-migrate.txt`, `p2-migrate.txt`).
- Thread handoffs to M1 (`wA-worker`, `wC-worker`, `wD-worker`): the `handoffMode.handOff` call over the window's own connection (`rig/msgs/handoff-*.json`).

| Thread | Source run (m4) | End on m4 | Continuation | Its run |
|---|---|---|---|---|
| `w5-worker` | `…0c1864d9…:ordinal:1` | completed 12:14:42 AM | none (baseline) | none |
| `w5b-worker` | `…6b332a78…:ordinal:1` | interrupted 12:16:20 AM | `handoff:8265e4a3…` on M5 | completed 12:21:30 AM |
| `w2-stubborn-worker` | `…410f8723…:ordinal:1` | interrupted 12:31:12 AM | `handoff:d1a42c88…` on M5 | not followed |
| `wA-worker` | `…f20cf13f…:ordinal:1` | interrupted 12:50:16 AM | `handoff:c0f59138…` on M1 | `ordinal:1` completed 12:55:25 AM |
| `wC-worker` | `…67be90d6…:ordinal:1` | interrupted 1:10:14 AM | none, held | none |
| `wD-worker` | `…ad889629…:ordinal:1` | interrupted 1:13:53 AM | `handoff:75d77330…` on M1 | `ordinal:1` completed 1:15:04 AM |

Run ids are `run:thread:<thread id, URL-encoded>:ordinal:<n>`.

## What this means for the Phase 3 design

**Holds as written.** The idle check passes with a held, interrupted thread (proof 1). The fence and acknowledgement recover from a window that has sign-ins on both machines, without the dead window's handoff pointer, and no second active coordinator appeared at the point tested (proof 6, after the fence). The routine gate waits during `transferring` and rests after `transferred`.

**Needs a change.**

- Step 4 (routines): coordinator-owned routines must move with the coordinator. Today they stop everywhere.
- Worker reports (proofs 3 and 5): a continuation thread must keep its launcher and report to the current coordinator, wherever it runs.
- The hold (proofs 2 and 6): the hold-only call must not depend on the client staying connected, and a held thread needs an explicit continue and release.
- Recovery needs sign-ins on both machines. The design should say what a window with only one does.

**Failure states the table lacks.**

- Thread `handing-off` with no `pendingTakeover`: stuck forever, no release.
- A Git setting the app does not run with (here `lfs.<url>.access`, written when the repository was pushed over HTTPS) blocks the move's fast-forward until removed (`p6-04-move-back-git-setting-warning.png`).
- After a merely refused or cancelled move, the window shows "Finish handing off… The handoff stopped partway" from its stored pointer while the server binding is still `active` (`p6-00`).
- On arrival, the new coordinator starts a worker on its own to "continue the handoff" even when the handoff has no assignment (seen on both machines).
- The idle check matches ancestor folders too: a busy thread in the "No project" scratch project, rooted above the project folder, would block the move.

## Sign-ins

M1 sign-in `2f58744d-a693-4999-8739-b595acc25f0f`, issued 12:45:14 AM, revoked 1:21:48 AM; `specweave-studio auth session list` on M1 then showed it absent. m4 sign-ins `4869a868-e914-41bb-a2be-7d182e99a105` and `999d1fce-48d0-464c-b805-e18abb5a37ca` revoked 1:21:38 AM; the m4 session list then showed no T-08 session (`cleanup-01-m4-sessions.txt`). No sign-in was made on the M5.

**Incident.** While checking M1 for leftover headless sign-ins I revoked five that belonged to another thread's "1419 headless check" windows, not to mine (`INCIDENT-m1-sign-ins-revoked-by-mistake.txt`). I stopped at once. No project, thread, grant or setting changed.

## Cleanup

Done on November 19, 2026, 2:15 AM to 2:20 AM Eastern, after the owner's go-ahead. Each item was checked by a read on its own machine (`cleanup-01` to `cleanup-05`).

| Item | Action | Check |
|---|---|---|
| Project on m4 (`mcp:fbb5c7be…`) | `specweave-studio project remove … --force`, 2:15:40 AM | Row `deleted_at` set, 0 open threads, 0 routines |
| Project on M1 (`mcp:f4efd07f…`) | Same, 2:16:06 AM | Row `deleted_at` set, 0 open threads, 0 routines |
| Project on M5 (`mcp:ddb15547…`) | Same, through the app's bundled CLI, 2:18:44 AM | Row `deleted_at` set, 0 open threads, 0 routines |
| Routine `t08-routine` | Deleted on m4, 1:21 AM | 0 routine rows on all three machines |
| Project folders | Removed on m4 and M1 after `worktree owners --path` exit 1; on M5 moved to the Trash (`~/.Trash/t08-handoff-proof-scratch-20261119`) because the shell refused `rm -rf` | `ls` of each old path: no such file |
| m4 sign-ins `4869a868…`, `999d1fce…` | Revoked, 1:21 AM | m4 session list: none with the T-08 label or these ids |
| M1 sign-in `2f58744d…` | Revoked, 1:21 AM | M1 session list: absent (read again 2:16 AM) |
| M5 sign-ins | None was made | M5 session list: no T-08 or headless sign-in since 12:00 AM |
| Saved browser storage | Profiles and pairing files deleted on m4 | `rig/profile-*` and `rig/private` absent; no process uses them |
| Headless windows | Stopped by PID | No process with a `rig/profile-` path |
| Repository `anton-abyzov/t08-handoff-proof-20261119` | Deleted (not archived), with its handoff branch | GitHub API returns 404 |
| `/tmp/t08-routine-fires.log` | Removed on m4; never existed on M1 | `ls`: no such file on both |
| Scratch threads on M1 (`mcp:ee477243…`) and M5 (`mcp:2df2b7f8…`) | Archived; no tool an agent can call deletes a thread | Thread reads show `archived: true` |

**Left in place.**

- m4's `handoff-mode.json` still holds the handoff records of five deleted threads, including `wC-worker` in `handing-off`. Removing them means editing the app's live state file, which I did not do.
- `machine-handoffs` records (`source-`, `destination-`, `context-`) for operations `b303309f`, `fe3f78b1` and `869c02a3` on m4 and M1.
- The two archived scratch threads and their scratch folders.
- The rig folder on m4 (`~/.specwithcode/m4/scratch/2026-11-19-1390-phase-3-proof/rig/`), which holds only scripts and the message files this report names.
- The five sign-ins of the other check revoked by mistake (see Incident) cannot be restored; that check's windows connect again on their own.
