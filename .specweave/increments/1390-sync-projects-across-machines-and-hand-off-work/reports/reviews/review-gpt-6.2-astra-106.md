<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=d3a2baf4ce76565003a2d239d0d07f3600434d1a at=2026-11-20T02:44:02.799Z -->
# Review: 1390 AC-45, worker routines after handoff
Verdict: fix first

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed the seven-file delta from `f14c7880c17d3a7134707e3e78b3e2a5d0cfbe13` to `d3a2baf4ce76565003a2d239d0d07f3600434d1a` in `anton-abyzov/specwithcode#774`.

## [high] `apps/server/src/handoff/HandoffTurnGate.ts:124-126` admits source work after the destination accepts but its reply is lost

The source writes a `handing-off` lease before sending takeover. It sets the continuation only after receiving confirmation; an uncertain reply leaves the transfer open (`apps/server/src/handoff/HandoffTransferRunner.ts:364-377,413-430,928-944`). If the destination resumes the worker but its reply is lost, the source has a **readable** record with `continuedOn: null`. The new lookup returns `here`. A delivery to the source webhook then passes `hold` and runs the command check locally (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:345-353`; `apps/server/src/scheduledTasks/ScheduledTaskService.ts:836-843,1002-1016`). The turn gate already refuses this lease at `apps/server/src/handoff/HandoffTurnGate.ts:75-82`, but a command check needs no turn.

Treat an unresolved handoff lease as a wait, not `here`. Test a delivery while the destination is running and the source still lacks its receipt: zero checks and zero dispatches. Once the source learns the outcome, a confirmed move should rest and a confirmed cancellation should release the wait.

## [high] `apps/server/src/scheduledTasks/ScheduledTaskService.ts:1498-1510` discards a due occurrence while waiting for readable state

A worker's monthly routine is due at noon. The scheduler polls on time, cannot read the handoff file, and correctly leaves the occurrence due at lines 836-840. With the file still unreadable just after 12:10, the same occurrence enters the missed-slot branch (`apps/server/src/scheduledTasks/Schedule.ts:129-151`). It has no pending dispatch. The `wait` goes to `skipMissedRun`, which writes next month's date (`apps/server/src/scheduledTasks/ScheduledTaskSkips.ts:60-71`). Repairing the file at 12:11 to show the worker never moved does not recover the noon run. The same applies to a daily fixed-time slot.

Distinguish a slot observed on time and held for unreadable state from one first discovered after the machine was off. Test recovery across the ten-minute boundary; the original occurrence should run exactly once.

## Verified closures and evidence

A recorded move blocks all three admission paths before a command runs. Run now refuses with the hold reason before reserving its receipt; webhook-only routines still require an actual request (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1854-1895`). Coordinator-owned routines bypass the new lookup. For worker-bound routines, waiting on unreadable state is intentional and explicitly stated (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:343-353`; `apps/server/src/scheduledTasks/ScheduledTaskRunnerRecords.ts:28-31`).

Production and tests now call the same `scheduledTaskLayerOver` (`apps/server/src/orchestration-v2/runtimeLayer.ts:439-453,622`; `apps/server/src/server.ts:621,640`; `apps/server/src/scheduledTasks/ScheduledTaskRunner.serverGate.test.ts:95-100`). The supplied red log shows both original regressions; the green log names the reviewed head and reports 136 tests passing. Removing the gate from that builder fails all three gate tests. The typecheck logs have the same errors in 19 files. This was a read-only review of source and existing evidence, not a build or test rerun.
