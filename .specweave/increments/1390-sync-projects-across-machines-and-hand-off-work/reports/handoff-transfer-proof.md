# Two-machine proof of the new handoff's failure cases (1390 T-08)

Run on November 19, 2026, 6:42 PM to 7:01 PM Eastern (23:42 to 00:01 UTC), on the throwaway project `t08-handoff-proof` only, between m4 and the M5.

| Machine | Served version | How it was read |
|---|---|---|
| m4 | 1.0.395 (service). The desktop app shell still reads 1.0.384; every case ran on the service. | `specweave-studio --version` at 23:41 UTC: `v1.0.395` |
| M5 | 1.0.395 (the app runs its own server; the M5 has no background service) | A worker on the M5 read its server's own `~/.specwithcode/userdata/server-runtime.json` at 00:07:53 UTC: `serverVersion 1.0.395`, server started 23:33:13 UTC (`c2-06-m5-acceptance-times-and-version.txt`). The app bundle also reads `1.0.395`. `fleet update --status` answers "This machine installs updates through its SpecWithCode app, not a background service". |
| M1 | 1.0.392, not used | `fleet update m1 --status`: `serverVersion 1.0.392`, `waiting-for-quiet` |

Both machines in every case served 1.0.395, which holds app commit `cbfda3c9` (#747). Code lines below are at tag `v1.0.395` of the app repository.

Evidence folder: `/Users/antonabyzov/.specwithcode/m4/evidence/1390-t08-handoff-transfer/`. File names below are relative to it. Rig scripts (not evidence): `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t08-handoff-transfer/rig/`.

| Case | Verdict | Why, in one line |
|---|---|---|
| 1. Proof 5 repeated (AC-44) | Proven | A worker handed off alone woke its launcher on m4 once, 0.4 s after it finished on the M5 |
| 2. Window killed after the hold, and after the send (AC-43) | Proven | Every kill left the server to finish the move; a fresh window read the batch. No kill landed after the target's receipt |
| 3. Crossed sends, two starts for one thread (AC-42) | Proven | A pull from the M5 crossed a send to the M5 and both landed; two starts made one operation and one continuation |
| 4. Legacy sleep settings (AC-36) | Cannot be shown | The saved settings started nothing, but the sleep notice route only takes the desktop's own bearer |
| 5. A due routine while its worker moves (AC-45) | Fails | The slot during the move ran once, on m4, but the routine then kept firing on m4 every minute instead of resting |
| 6. Typing on a formerly transferred member (AC-35) | Cannot be shown | No formerly transferred member exists (option B); typing on m4 went to m4's coordinator |

## Setup

- m4 project `mcp:043443f2-c7b6-43e7-a3e8-7ac92cd78c74` (`origin: "automated"`), created at 22:01 UTC on 1.0.384, folder `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t08-handoff-transfer/t08-handoff-proof` with one commit.
- Option A (a coordinator move on the old version before the update) was not possible: at 22:02 UTC the M5 refused to link the copy, "One of the two machines is on a version from before every machine ran its own coordinator" (`packages/contracts/src/projectLink.ts:589`, present from v1.0.391, absent at v1.0.384), so the M5 was already past the migration (`a-01-option-a-link-refused.txt`). It left an unlinked copy on the M5 (`e7e14159-…`).
- After m4 updated, `studio_project_add_to_machine` linked an M5 copy at 23:41 UTC: project `68955fdb-08f0-4c12-a9f8-e7ef7c17cc81`, `linked: true`, folder `/Users/anton/.specwithcode/m4/scratch/2026-11-19-1390-t08-handoff-transfer/t08-handoff-proof-linked`.
- Headless windows A, B and C on m4 (full Chromium, headless), each with its own one-time pairing (labels "1390 T-08 handoff proof window A/B/C"). Window A had `orchestration:read`, `orchestration:operate`, `settings:write` and `filesystem:read`; B and C had the first two.
- Every move was started with `handoffBatch.start` over the window's own WebSocket, the call the Hand off dialog makes, with `start: "manual"`, destination the M5, and model `codex / gpt-5.6-luna` on the M5 (its Claude account was at 100% until 9 PM Eastern).
- Workers on m4 ran `claude-haiku-5-5` and slept 150 to 400 s in one foreground shell call, so each was mid-turn when handed off.

## Case 1: a worker handed off alone reports to its launcher on the source (AC-44)

**Done.** A top-level launcher thread `t08-c1-launcher` (`mcp:d1a94c85-…`, agent, MCP) started worker `t08-c1b-worker` (`mcp:051a65f0-…`) on m4 (`c1-04-m4-threads.txt`). While the worker slept, window A handed it off alone to the M5 at 23:46:53 UTC (batch `b41d6efb`… for the first try, see below; this run's operation `6a38846c`). The launcher stayed on m4.

**Observed.**

- The follower row came before the send: `handoff-follow:eeb3ce58…` with `callerThreadId` = the launcher and `awaiting: "continuation"` was written at 23:46:59.968, while the record still read `held`. The record read `sent` (with `launcher` set) at 23:47:00.178 (`c1-07-m4-transfer-and-follower-timeline.log`).
- The continuation `handoff:eeb3ce588f8767639cb7c26d1b76ca4f` resumed on the M5 at 23:47:00 and finished `completed` at 23:47:35.797, replying "DONE1".
- At 23:47:36.211, m4's launcher got exactly one message: "Remote worker [t08-c1b-worker](…) on M5 finished: completed." (`c1-05-m4-launcher-messages.txt`). The follower row then read `state: idle`, `deliveredRunIds` holding that one run, and `handoff.woke.at` 23:47:36.353 (`c1-06-m4-follower-row.json`).
- At 00:01:05 UTC, 13.5 minutes later, there was still one wake (`c1-09-m4-launcher-messages-later.txt`).

**Not shown.**

- The launcher's machine offline when the result came, then reconnecting. That needs m4 off the network or restarted, which this run does not do.
- A replayed receipt. Nothing re-sent this takeover. The single wake after 13.5 minutes, with `deliveredRunIds` recorded, is consistent with the replay guard (`RemoteWorkerFollower.ts:503-545`) but does not exercise it.

**Note on the first try.** The first worker, `t08-c1-worker`, was launched by this proof's own thread, which is a delegated subagent (`c1-03-first-launcher-is-subagent.txt`). Its handoff recorded `launcher: null` and no follower (`c1-02-m4-transfer-record.json`). That is by design, not a defect: `launcherOf` skips a subagent launcher (`apps/server/src/handoff/handoffFollow.ts:270-274`, "A delegated child is not woken"). The proof above uses a top-level launcher.

**Verdict: proven.**

## Case 2: the driving window dies after the hold, and after the send (AC-43)

**Done.**

- **After the hold.** Window B sent `handoffBatch.start` for `t08-c2b-worker` (`mcp:f71647b4-…`). A watcher read m4's `handoff-transfers.json` every 50 ms and sent SIGKILL to window B's eight processes (its node process and Chromium, by PID) the moment the record read `held`: held at 23:53:00.907, killed at 23:53:00.908 (`c2-02-kill-after-hold-timeline.log`).
- **After the send.** Window C did the same for `t08-c2c-worker` (`mcp:fccd5e54-…`) and was killed the moment the record read `sent`: sent at 23:53:38.882, killed at 23:53:38.896 (`c2-05-kill-after-send-timeline.log`).
- **Later after the send.** Window E did the same for `t08-c2d-worker` (`mcp:52a2dd5f-…`), with the kill delayed 0.25 s past `sent`: sent at 00:08:55.838, killed at 00:08:56.213 (`c2-07-kill-250ms-after-send-timeline.log`).
- **Fresh window.** Window A, which had not started any of these moves, read the batch with `handoffBatch.read`.

**Observed.**

- **After the hold.** With window B gone, the server carried on: `sent` at 23:53:06.473 and `resumed` at 23:53:07.624. Window A read batch `41c6d967…` as finished at 23:53:08.384, with the row `resumed` and continuation `handoff:090594d5…` (`c2-03-fresh-window-reads-batch.json`). The m4 run is `interrupted` and the thread is `fenced` on m4.
- **After the send.** The record reached `resumed` at 23:53:39.223, 0.33 s after the kill. The M5 stamped its acceptance at 23:53:39.078, 0.18 s after the kill (`c2-06-m5-acceptance-times-and-version.txt`).
- **Later after the send.** The record reached `resumed` at 00:08:57.142. The M5 stamped its acceptance at 00:08:56.873, 0.66 s after the kill (`c2-08-m5-acceptance-c2d.txt`). Both kills therefore fell after the send and before the target's receipt; the server finished both moves anyway.
- **On the M5.** The M5's own record (`/Users/anton/.specwithcode/userdata/handoff-transfers.json`, read on the M5 at 23:54:35) holds one acceptance per lineage, each `verdict: accepted`, `launched: true`, for every thread moved so far (`c2-04-m5-acceptances.txt`). Nothing ran on both machines: each source run ended `interrupted` and each source thread is `fenced`.
- **Batch with a thread that does not move.** Batch `01b8a152…` named `t08-c2a-worker` and the already moved `t08-c1-worker`. The first row came back `resumed`. The second came back `ready`, "Already continued on Anton M5MAX PROLED.", with the same continuation id as before and no second operation (`c2-01-partial-batch-result.json`).

**Not shown.**

- **A kill after the target's receipt.** Two tries (at `sent`, and 0.25 s after it) both fell before the M5's acceptance, which came 0.18 s and 0.66 s after the kill. The M5's acceptance cannot be watched from m4 closely enough to time a kill between it and the source's `resumed`.
- **A cut by restarting either machine.** Not done; restarting an app is not allowed in this run.
- **"Resume here" for a hold that was never sent.** No hold stayed unsent: the server finished every move on its own.
- **A batch with a row that fails.** The second row was a no-op, not a failure, so this is not a partly successful batch in the AC's sense.

**Verdict: proven** (a closed window after the hold and after the send cuts nothing; a kill after the target's receipt was not hit).

## Case 3: crossed sends, and two starts for one thread (AC-42)

**Done.**

- **Two starts.** For `t08-c3-dup-worker` (`mcp:a5a01375-…`), mid-turn, window A fired two `handoffBatch.start` calls 17 ms apart (23:54:22.046 and 23:54:22.063).
- **Crossed sends, first try.** I started `t08-c3-m5-worker` on the M5 and asked a worker there to hand it to m4 with `studio_thread_migrate`, while window A handed `t08-c3-m4-worker` from m4 to the M5 at 23:55:17. The M5 leg never started: the worker answered "ERROR: studio_thread_migrate is missing", because the tool is a coordinator's (`c3-06-m5-send-not-startable.txt`).
- **Crossed sends, second try.** The M5 to m4 leg was started as a pull from m4, the window's "Continue here" call. At 00:07:17.094 window A sent `t08-c3y-worker` (`mcp:9225e62c-…`) from m4 to the M5. 5 ms later, window D (pairing with `source-control:write`) called `handoffMode.continueHere` for the M5 continuation `handoff:253e0442…` of `t08-c3-m4-worker`, which m4 listed among its incoming copies. A first attempt from window A was refused: "The authenticated token is missing required scope: source-control:write." (`c3-08-crossed-push-and-pull.txt`).

**Observed.**

- **Two starts.** One call came back `resumed` and the other `ready`, "Already continued on Anton M5MAX PROLED.", both naming continuation `handoff:3bd44164…`. m4 holds one operation (`337aa3fe`, epoch 1) for that lineage. The two batches name it once as `resumed` and once as `ready` (`c3-01-two-starts-one-thread.txt`, `c3-04-m4-records-for-dup-thread.txt`). One start won, and the other got the same receipt.
- **Crossed sends, both landed.** The push to the M5 went held 00:07:19.580, sent 00:07:20.933, `resumed` 00:07:21.624 as `handoff:009093ae…` (`c3-11-push-timeline-during-pull.log`). The pull from the M5 finished at 00:07:18.576, inside the push's window, as `handoff:462f42dd…` on m4 (`c3-09-crossed-push-and-pull-window-D.txt`, `c3-10-pulled-thread-on-m4.txt`).
- **Both histories kept.** On the M5 the pulled thread's copy now reads `executionState: fenced`, and its history runs m4 (epoch 0), the M5 from 23:55:21.200 (epoch 1), then m4 by `continue-here` from 00:07:18.434 (epoch 2). Its last reply "DONE3M4" is kept (`c3-12-m5-copy-after-pull.txt`).

**Not shown.**

- **Crossed pushes.** A push started on the M5 itself needs a window signed in to the M5 or the M5's coordinator, and this run has neither. The M5 to m4 leg here is a pull started on m4.
- **Duplicate creation and reordered packets.** Both need hand-built `POST /api/handoff/v1/takeover` calls carrying a work grant. Per the owner's instruction these are not attempted.

**Verdict: proven** (crossed sends and two starts for one thread; duplicate creation and reordered packets not shown).

## Case 4: legacy sleep settings start nothing (AC-36)

**Done.**

- **The settings.** With worker `t08-c4-worker` mid-turn on m4, window A saved Away settings with `away.updateConfig` (the Settings call): target the M5 with `sleepTrigger: "always"` at 23:48:42, then `sleepTrigger: "on-battery"` at 23:48:46. Both saves succeeded and the snapshot echoed them (`c4-01-sleep-notices.txt`).
- **The sleep notice.** I tried to send `POST /api/away/v1/sleep` (`{"onBattery":false}` and `{"onBattery":true}`) and `POST /api/coordinator/v1/suspend` on m4. These are the routes the desktop main process calls on suspend (`apps/desktop/src/app/DesktopHandoffSleep.ts:100-127`).
- **The watch.** I read m4's transfer records, the worker's handoff record, `away-intents.json` and the worker's run every 20 s for two minutes.
- **The restore.** Settings went back to the original target none and `on-battery` at 23:51:16 (`c4-03-settings-restored.json`).

**Observed.**

- **No notice could be sent.** The routes take only this machine's desktop bearer with `access:write` (`apps/server/src/away/awaySleepRoute.ts:657-664`, `project/CoordinatorSuspendRoute.ts:26-32`). The CLI that could issue such a bearer refused while the service runs: "Issuing a bearer access token would need to open its live database, which this CLI does not do while the service runs." So my POSTs went out with no bearer at all and each answered `401 {"error":"unauthorized"}`. That shows only that an unauthenticated call is refused. I did not read the desktop's own token (no Keychain reads), so no sleep notice reached the server's sleep handler.
- **Nothing moved.** With the legacy settings saved, nothing started: the transfer count stayed 3, the worker got no handoff record, and no `away-intents.json` appeared. The worker ran on and finished `completed` on m4 at 23:52:32 (`c4-02-two-minutes-with-legacy-settings.txt`, `c4-04-m4-worker-run-final.json`).
- **Settings at the end.** Re-read at 00:10:04 UTC: target none, `sleepTrigger: "on-battery"`, as before the case (`cleanup-01-m4-away-settings-final.txt`).
- **In code.** The sleep handler answers `skipped` and records nothing whatever the saved trigger (`awaySleepRoute.ts:432-438`).

**Not shown.**

- **The sleep notice itself.** It needs the desktop bearer.
- **A real lid close, and power events.** Not done, by instruction.
- **The renderer fallback with no window open.**
- **A received `sleep` or `auto-takeover` start answered "not accepted".** It needs a hand-built takeover with a work grant.
- **A hold authorized before the lid closed, staying recoverable.**

**Verdict: cannot be shown** (the saved settings alone start nothing; the sleep notice could not be sent).

## Case 5: a routine falls due while its worker moves (AC-45)

**Done.** Worker `t08-c5-worker` (`mcp:74d54983-…`) created routine `t08-c5-routine` (`scheduled-task:eb57e419-…`, every 60 s, bound to the worker's thread, not coordinator-owned). Its check appends a line with the time and host name to `/tmp/t08-c5-routine-fires.log` and exits 1, so no agent turn runs. It fired once on m4 at 23:56:51. Window A then handed the worker off to the M5 timed for the next slot, which was due at 23:57:51.026:

| Time (UTC) | Record state |
|---|---|
| 23:57:49.988 | `held` |
| 23:57:51.360 | `sent` |
| 23:57:51.892 | `resumed` on the M5, continuation `handoff:0ca58206…` |

(`c5-03-m4-transfer-timeline.log`)

**Observed.**

- **The slot during the move ran once, on m4.** It fired at 23:57:55, after the record read `resumed`. Nothing ran on the M5.
- **The routine did not rest after its thread left.** It fired again on m4 at 23:58:57, and kept firing every minute until I deleted it at 00:06 UTC: `run_count` 9, `last_run_status: succeeded`, no rest note, no runner row, 9 lines in the fire log, all from m4 (`c5-01-m4-routine-timeline.txt`, `c5-06-m4-routine-final.json`, `c5-04-m4-fire-log.txt`). The m4 handoff record of the worker says the thread moved: `lease.state: fenced`, `continuedOn` "Anton M5MAX PROLED" at 23:57:51.854 (`c5-02-m4-handoff-mode-record.txt`).
- **The M5 got no copy.** It has no routine for the project (`list_scheduled_tasks` "returned none") and no fire log, read at 00:00:48 UTC.

AC-45 wants a routine bound to a worker that moved to rest with "Its thread was handed off to {machine}". It kept running on m4.

**Cause in code.**

- The gate does rest such a routine when `deps.threadMovedTo(task.threadId)` names a machine (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:350-355`).
- `threadMovedTo` reads `turnGate.continuedOn`, and answers null when the gate has none (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1972`, `:1986-1989`).
- `HandoffTurnGate` is a `Context.Reference` whose default value has no `continuedOn` (`apps/server/src/handoff/HandoffTurnGate.ts:36-43`). Only the live `HandoffTurnGate.layer` adds it (`:112-116`).
- The scheduler is built without that layer: `layerScheduledTaskProvided` provides thread launch, thread management, secret requests, the project coordinator, `ProcessRunner`, the coordinator role and `CoordinatorWakeGate`, but not `HandoffTurnGate.layer` (`apps/server/src/orchestration-v2/runtimeLayer.ts:432-445`). The live gate is given only to the orchestrator's group (`:327`) and to `MachineLimitHandoff` (`:513`) (`c5-05-turn-gate-wiring-v1.0.395.txt`).
- The routine is not coordinator-owned, which would skip that check (`ScheduledTaskRunner.ts:350`). `ownThread` is persisted in the run policy (`ScheduledTaskStorage.ts:269`), and this routine's policy holds only `modelPinned` and `check`.
- No other non-test code at the tag provides `HandoffTurnGate` (full grep in `c5-05-turn-gate-wiring-v1.0.395.txt`).
- So `threadMovedTo` is always null in the running server, and a worker's routine never rests after its worker moves. This wiring is read from code and matches what was observed; no patched build was run to confirm it.

**Not shown.**

- **"Move the routine too".** The string is not in the code at this release (`git grep -i "move the routine"` finds nothing).
- **A runner move and its steps.** No runner move ran: only Away drives one, and this routine has no runner row. So the due slot during a runner move, concurrent edits and a lost reply to turning it on are not shown.

**Verdict: fails.**

## Case 6: typing on a formerly transferred member (AC-35)

**Done.**

- **Typing on m4.** Window A typed on m4's coordinator through `projects.coordinatorSend` (the composer's call) at 23:57:00.
- **The binding.** I read m4's project row.

**Observed.**

- **The send stayed on m4.** It created m4's coordinator `project-coordinator:mcp:043443f2-…` (`created: true`, routing `saved` to its own model), and the reply "COORD-M4" came from a run on m4 at 23:57:10 (`c6-02-m4-coordinator-send.json`, `c6-03-m4-coordinator-messages.txt`). Nothing routed the send to the M5.
- **m4's binding.** It reads `{"epoch":0,"state":"active"}` with both members listed. The M5 member has `linkId` `46541bd9…` and its own coordinator id `project-coordinator:68955fdb-…` (`c6-01-m4-binding.json`).
- **The migration marker.** `ownership` is null on m4. The project was made on 1.0.384 as an unlinked single member, so no equal-coordinator migration marker was written for it.

**Not shown.**

- **A formerly transferred member.** None exists. Option A was impossible (see Setup), and the old move is gone from 1.0.395.
- **Typing on the freshly added M5 member.** It needs a window signed in to the M5, and a headless window cannot sign in there.
- **An old peer reconnecting with a superseding binding.** Both machines were on 1.0.395 and no linked project spans an older one, so it did not happen naturally. Nothing was triggered.

**Verdict: cannot be shown** (typing on m4 goes to m4's coordinator; the formerly transferred member, typing on the M5 and the old peer are not shown).

## Run ids

| Thread (m4) | Source run end on m4 | Continuation on the M5 | Operation |
|---|---|---|---|
| `t08-c1-worker` `mcp:9b29fb05…` | interrupted | `handoff:a211c3d2…` | `02303cd9` |
| `t08-c1b-worker` `mcp:051a65f0…` | interrupted | `handoff:eeb3ce58…`, completed 23:47:35 | `6a38846c` |
| `t08-c2a-worker` `mcp:dc075627…` | interrupted | `handoff:55cb41a8…` | `31c6f0a2` |
| `t08-c2b-worker` `mcp:f71647b4…` | interrupted | `handoff:090594d5…` | `d4247149` |
| `t08-c2c-worker` `mcp:fccd5e54…` | interrupted | `handoff:a341c29a…` | `57ef41d8` |
| `t08-c3-dup-worker` `mcp:a5a01375…` | interrupted | `handoff:3bd44164…` | `337aa3fe` |
| `t08-c3-m4-worker` `mcp:62a9f1ae…` | interrupted | `handoff:253e0442…` | `dd461453` |
| `t08-c5-worker` `mcp:74d54983…` | interrupted | `handoff:0ca58206…` | `1cd3c143` |
| `t08-c2d-worker` `mcp:52a2dd5f…` | interrupted | resumed on the M5 | `932aa3e9` |
| `t08-c3x-worker` `mcp:f0b53ee5…` | interrupted | `handoff:dfa2acc8…` | `2556b8f5` |
| `t08-c3y-worker` `mcp:9225e62c…` | interrupted | `handoff:009093ae…` | `38ddaf27` |
| `handoff:462f42dd…` (pulled back from the M5) | none | it is the continuation on m4 of `handoff:253e0442…` | continue-here, epoch 2 |
| `t08-c4-worker` `mcp:ef22bca2…` | completed on m4 | none | none |
| `t08-c1-launcher` `mcp:d1a94c85…` | completed on m4 | none | none |

On the M5, started directly: `t08-m5-version` `mcp:a9b5f7b6…` (reads and the migrate attempt) and `t08-c3-m5-worker` `mcp:36bb5dc7…`.

## Sign-ins

All on m4, one-time pairings exchanged by headless windows, revoked at 00:12 UTC, November 20, 2026, by exact id (`cleanup-03-m4-sign-ins.txt`). The m4 session list then showed no session with the T-08 label. No sign-in was made on the M5 or M1. No bearer was issued: the CLI refused (case 4).

| Window | Session | Scopes |
|---|---|---|
| A | `7102b186-16ed-4db2-8005-3e48139ed6bd` | orchestration read and operate, settings write, filesystem read |
| B (killed) | `a1a8a5af-ffd0-4fe8-8470-cc6c6239150a` | orchestration read and operate |
| C (killed) | `95bc8c4f-f3c2-42e8-ba71-e243deb92b33` | orchestration read and operate |
| D | `e02b460e-2eec-4130-b91c-8260f46dcfc3` | orchestration read and operate, source-control write |
| E (killed) | `a3fbea62-322c-403c-ad44-61866fb342ea` | orchestration read and operate |

## Cleanup

Done on November 20, 2026, 12:06 AM to 12:14 AM UTC (7:06 PM to 7:14 PM Eastern on November 19).

| Item | Action | Check |
|---|---|---|
| Routine `t08-c5-routine` (`scheduled-task:eb57e419-…`) on m4 | `delete_scheduled_task`, 00:06 UTC | `deleted: true`; the project then had 0 routines |
| m4 project `mcp:043443f2-…` and its threads | `specweave-studio project remove … --force --confirm "t08-handoff-proof"`, 00:13:14 UTC | Row `deleted_at` 00:13:16.851Z, 0 open threads, 0 routines (`cleanup-04-m4-project-removed.txt`) |
| m4 project folder | No process had a file open in it; moved to `~/.Trash/t08-handoff-proof-m4-20261120` | `ls` of the old path: No such file or directory (`cleanup-05-m4-folders-and-files.txt`) |
| Unlinked M5 copy `e7e14159-7056-4ed3-a7f5-3e638db93854` | Removed with the M5 app's bundled CLI `/Applications/SpecWithCode.app/Contents/Resources/cli/specwithcode project remove … --force`; folder moved to the M5's `~/.Trash/t08-handoff-proof-unlinked-20261120` | "Removed project e7e14159-…"; `ls` of the old path: No such file or directory (`cleanup-02-m5-unlinked-copy.txt`) |
| Linked M5 copy's folder | Moved to the M5's `~/.Trash/t08-handoff-proof-linked-20261120` | The M5 worker's next run failed with "Thread folder is missing … /Users/anton/.specwithcode/m4/scratch/2026-11-19-1390-t08-handoff-transfer/t08-handoff-proof-linked" |
| m4 Away settings changed in case 4 | Restored at 23:51:16 UTC | Re-read at 00:10:04 UTC: target none, `on-battery` |
| Headless windows A to E and the background watchers | Stopped by PID (window node and Chromium PIDs, watcher PIDs 21608, 68209, 86871) | No process with a `t08-handoff-transfer/rig/profile-` path or `killwatch.py` left |
| Saved browser storage and pairing files | `rig/private` and `rig/profile-A` to `profile-E` moved to the m4 Trash | Absent from the rig folder |
| `/tmp/t08-c5-routine-fires.log`, `/tmp/t08-page.png`, `/tmp/t08-find.png` on m4 | Moved to the m4 Trash | Never existed on the M5 |

**Left in place.**

- **The linked M5 copy, project `68955fdb-08f0-4c12-a9f8-e7ef7c17cc81` ("t08-handoff-proof (m4)"), and its threads.** The threads are `t08-m5-version` `mcp:a9b5f7b6…`, `t08-c3-m5-worker` `mcp:36bb5dc7…` and the continuations listed under Run ids. `project remove` on the M5 failed. Its message was cut by my `tail` to a stack trace (`projectRemoveMutation`), and the only thread that could run there then lost its folder, so the reason was not read. No agent tool reaches that project now, so removing it is the owner's: on the M5, sidebar > Automated > t08-handoff-proof > Delete, or `specwithcode project remove 68955fdb-08f0-4c12-a9f8-e7ef7c17cc81 --force --confirm "t08-handoff-proof"` in a terminal there.
- **The M5's Trash folders.** `~/.Trash/t08-handoff-proof-unlinked-20261120` and `~/.Trash/t08-handoff-proof-linked-20261120`.
- **Handoff and follower records of the deleted threads, on both machines.** m4 keeps them in `handoff-transfers.json` (transfers, batches), `handoff-mode.json` and `remote-workers.json` (the follower `handoff-follow:eeb3ce58…`). The M5 keeps nine acceptances in `handoff-transfers.json`. Removing them means editing the apps' live state files, which I did not do.
- **Late notices from `t08-m5-version` (seen after cleanup, outside the six cases).** Between 00:15 and 00:17 UTC on November 20, m4 delivered four "finished: completed" notices for this plain remote worker, one per turn. The worker had no new run, its last run (11) ended `failed`, and its follower row `rwt:mcp:99f063a9…` stayed at `updatedAt` 00:14:08.465Z with `lastWakeRunId` run 9 and each of runs 1 to 11 once in `deliveredRunIds`. The notices carry no run id, so I could not tell a late delivery from a repeat. Not shown: which run each notice came from. A fifth notice, for `t08-c3-m5-worker`, came at 00:16 UTC although its row `rwt:mcp:bfe4fe4e…` last changed at 23:55:36 UTC with one run delivered, which fits notices queued while this thread was busy and handed over one per turn. This row is not a handoff follower, so case 1 is unaffected.
- **The rig folder on m4.** `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t08-handoff-transfer/rig/` holds only scripts, logs and message files; `step-list.md` sits beside it.
