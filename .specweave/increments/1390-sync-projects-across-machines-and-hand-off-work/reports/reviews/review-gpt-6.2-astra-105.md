<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=f14c7880c17d3a7134707e3e78b3e2a5d0cfbe13 at=2026-11-20T02:24:04.011Z -->
# Review: 1390 AC-45, worker-bound routines after handoff
Verdict: fix first
Reviewer context: fresh session, GPT-6.2 Astra. Three changed files, two high findings. Reviewed `anton-abyzov/specwithcode#774` at `f14c7880c17d3a7134707e3e78b3e2a5d0cfbe13` against `origin/main`.

## [high] `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:342` admits a moved worker's webhook

A worker can create a webhook bound to its own thread, with a command check (`apps/server/src/mcp/OrchestratorMcpService.ts:3145-3157`). After the worker moves, a delivery to its original URL returns from `hold` before the moved-thread lookup at line 352. The service can mark the run active and execute the check on the source before any agent turn (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:836-843,877,1002-1016`). Keeping the URL local need not admit the run. Check the bound worker before admitting a webhook; test a delivery after handoff with zero check invocations.

## [high] `apps/server/src/handoff/HandoffTurnGate.ts:112-116` treats unreadable state as an unmoved worker

If the source restarts after handoff and cannot read its handoff file, the cold store fails its read (`apps/server/src/handoff/HandoffModeStore.ts:55-65,81-89`). The live `continuedOn` converts that failure to `null`. The runner consequently returns no hold rather than waiting (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:350-356,369-374`), allowing a due worker-bound command check to run locally. Distinguish an unknown destination from a successful lookup with no move. Wait on unknown and retry once the state reads again.

## What the change fixes

The running server supplies `ServerEnvironment` outside the production orchestration layer (`apps/server/src/server.ts:621,640,964,1037`). The scheduler captures the live gate; the orchestrator and machine-limit handoff also receive it (`apps/server/src/orchestration-v2/runtimeLayer.ts:327,439-455,523,624`). No later default overrides it. The limit adapter uses only the pure refusal function. Coordinator-owned routines skip the new lookup; a readable record with no continuation still permits an otherwise eligible routine.

The supplied red run observed one fire with the exported layer set to `Layer.empty`; the green log names the reviewed head and reports 78 passing tests. The test verifies the exact rest message and zero fires with a real handoff file. Follow-up: it injects the exported gate into the testkit's own service composition (`apps/server/src/scheduledTasks/ScheduledTaskRunner.testkit.ts:386-397,426-431`), so deleting only the production provision at `runtimeLayer.ts:444` would not turn it red. Source and logs reviewed; no build or test rerun.
