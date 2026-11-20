<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=9b1949d17f2e81891fe862d4e0ba86c9a8060f7a at=2026-11-20T03:17:20.983Z -->
# Review: 1390 AC-45 worker routine admission, PR body
Verdict: ship

Reviewer context: fresh session, unchanged head. No remaining false statement found in the current PR body.

The revised wording distinguishes a handoff observed at admission from one recorded before process start (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1019-1035`). It also correctly limits the `here` fallback to the continuation lookup: `check` can still refuse admission (`apps/server/src/handoff/HandoffTurnGate.ts:76-87`). Both prior findings are resolved. Historical test results were not rerun.
