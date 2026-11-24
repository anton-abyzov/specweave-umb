<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=26fca28faa222e246b9ec9a2e38a17a2c8a9ef8d at=2026-11-20T03:00:07.947Z -->
# Review: 1390 AC-45, worker routine handoff
Verdict: fix first

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed `anton-abyzov/specwithcode#774`, delta `51c54521c1b4d81079b40a05634d294345c354c6` to `26fca28faa222e246b9ec9a2e38a17a2c8a9ef8d`. Two high findings.

## [high] `apps/server/src/scheduledTasks/ScheduledTaskService.ts:1021-1029` checks before workspace access, not before process creation

A worker's due routine with an existing workspace passes the gate and supplies `checkRoot` as `cwd` (`apps/server/src/scheduledTasks/ScheduledTaskCheck.ts:31-39`; `apps/server/src/processRunner.ts:319-330`). The [pinned Node spawner](https://unpkg.com/@effect/platform-node-shared@4.0.1/src/NodeChildProcessSpawner.ts) awaits `fs.access(options.cwd)` at line 117. It awaits that resolution at line 539 before calling its spawn helper at line 544; the native `NodeChildProcess.spawn` is at line 372. The repository patch to that dependency changes only pipe error handling.

If the handoff persists `handing-off` while workspace access is outstanding, the successful access resumes and starts `/bin/sh` on the source. There was no running check process when the fence landed. The regression counts entry to a mocked `ProcessRunner.run`, before this wait. Serialize native startup with the fence writer, and cover a fence during workspace access with a native spawn count of zero.

## [high] `apps/server/src/orchestration-v2/Orchestrator.ts:5873-5874` can enqueue the routine prompt after the last worker gate check

Take a routine with no command check, bound to a worker with an active run. The scheduler calls `sendToThread` with `mode: "queue"` immediately after its consult. The real sender reads thread records and calls `message.dispatch` (`apps/server/src/orchestration-v2/ThreadManagementService.ts:577,608-622`). Dispatch consults the worker gate again, **then** awaits the coordinator gate, which reads separate state (`apps/server/src/project/CoordinatorWakeGate.ts:254-258,281-295`). The handoff can persist its lease in that interval (`apps/server/src/handoff/HandoffTransferRunner.ts:928-946`; `apps/server/src/handoff/HandoffMoves.ts:258-267`).

When the coordinator check returns no refusal for the worker, dispatch takes the active-run queue branch, creates a local queued run and emits the routine's message with its text (`apps/server/src/orchestration-v2/Orchestrator.ts:6471-6477,6655-6661,6692-6700,6740-6747`). The existing turn was in flight; this new prompt was not yet in its queue. A later refusal to execute the queued turn does not undo the send. Serialize queue admission with the fence and test the resulting message count, not entry to the mocked sender.

## Verified

The previous project-lookup gap is closed. When the scheduler itself observes a late refusal, it records a scheduled occurrence as waiting and due, without incrementing its run count; the missed-slot branch retries a pending occurrence. A manual or webhook refusal carries the gate reason. Coordinator-owned routines bypass the worker gate, and an absent handoff record still permits work.

The supplied head-specific run passed 157 tests across nine files. The send mutation failed as expected. The server typecheck error diagnostics match main; no new build failure was identified. Source and existing evidence only, with no checkout, build or test rerun.
