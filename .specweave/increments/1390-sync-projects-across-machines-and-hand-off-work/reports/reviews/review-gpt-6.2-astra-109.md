<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c338ca9ccc8505b70090143c187b22920290fd22 at=2026-11-20T03:06:36.549Z -->
# Review: 1390 AC-45, worker routines after handoff
Verdict: fix first

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed all seven changed files in `anton-abyzov/specwithcode#774` at `c338ca9ccc8505b70090143c187b22920290fd22`, the PR body and rounds 105 through 108. The delta since round 108 is comment-only.

## [high] The comment and PR body promise more than the gate guarantees

`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1022-1026` says an in-flight check's prompt “is never sent.” Suppose the source is fenced during a passing check, but the handoff is cancelled before the check finishes. The send consults **current** state at lines 1231-1240. An active local lease without a continuation or another refusal permits the send (`apps/server/src/handoff/HandoffTurnGate.ts:103-123`). That is correct behavior, not a lost fence. The accurate claim is: “If the gate still refuses at send time, the scheduler does not send the prompt.”

The PR body's “Change” section also says the process starts “with no await in between.” Its own “Known limits” correctly identifies the awaited workspace access between admission and native process start (`apps/server/src/scheduledTasks/ScheduledTaskCheck.ts:31-39`; `apps/server/src/processRunner.ts:319-330`). Use “after the last project lookup, before entering the spawner” in the summary. The consumer table should name the current `threadHold` dependency and both `continuedOn` and `check`, not the removed `threadMovedTo` dependency.

Only the inaccurate wording blocks under criterion (f). No change to fence serialization or dispatch ordering is requested. The production composition supplies the live gate; the moved-worker, unresolved-handoff and cancellation paths match AC-45 within the accepted limits. Round 108 reports 157 passing tests on the unchanged executable code. No build or test was rerun for this read-only review.
