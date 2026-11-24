<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=51c54521c1b4d81079b40a05634d294345c354c6 at=2026-11-20T02:50:26.607Z -->
# Review: 1390 AC-45, worker routine admission during handoff
Verdict: fix first

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed the five-file delta from `d3a2baf4ce76565003a2d239d0d07f3600434d1a` to `51c54521c1b4d81079b40a05634d294345c354c6` in `anton-abyzov/specwithcode#774`.

## [high] `apps/server/src/scheduledTasks/ScheduledTaskService.ts:1009-1016` starts a local check after the handoff fence can change

A webhook for an idle worker passes `coordinatorHold` while its lease is local (`ScheduledTaskService.ts:836-844`). Before starting the check, the scheduler awaits the project lookup at line 1009. While that lookup is pending, the transfer runner can persist `handing-off` (`apps/server/src/handoff/HandoffTransferRunner.ts:924-946`). A turn on the source now receives a refusal (`apps/server/src/handoff/HandoffTurnGate.ts:108-115`). When the lookup returns, the scheduler calls `runScheduledTaskCheck` on the source without consulting or holding the thread gate. This is a new process starting after the fence, not a check that was already running when the handoff began.

Serialize command startup with the thread's handoff fence. Cover the ordering by suspending the final project lookup, persisting the handoff hold, and releasing the lookup; assert zero local process starts. The supplied regressions set the lease before delivering or polling, so neither exercises this ordering.

## Verified

For a stable record, the only path to `here` requires `gate.check` to return `null`; the live gate calls `turnRefusal` (`apps/server/src/handoff/HandoffTurnGate.ts:75-86,133-145`). Scheduled, manual and webhook execution share the hold before the check. Coordinator-owned routines bypass the thread lookup; an absent record allows a turn, and the cancellation test shows the retained due slot firing once. The accepted ten-minute missed-slot limit is not a blocker.

The supplied head-specific green log reports 138 passing tests across eight files. The typecheck error-file list matches main's 19 files. Source and existing evidence only; no build or test rerun.
