<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=eafe8c5b53cbe1a80d07f79795fd6512dffbe3ba at=2026-11-19T19:12:53.519Z -->
# Review: 1390 T-11 rebase delta
Verdict: fix first
Reviewer context: fresh session, Git objects only. Reviewed `eafe8c5b53cbe1a80d07f79795fd6512dffbe3ba` against `0b80025bb` and the previously approved series.

## [high] apps/server/src/handoff/HandoffTransferRunner.ts:853-867 checks the planned disposition instead of the current one

An automatic move is admitted to resume run R. If R finishes normally after planning but before preparation, it is still the latest run, but its current disposition is ready. The explicit or persisted resume value overrides the fresh checkpoint in the admission comparison. The post-hold check at lines 963-968 also uses that stale value when there is no active run. Main would refuse this move; the rebased runner can move a finished thread for resumption. Compare the trigger with the independently derived current disposition before using the planned disposition for the transfer.

## [high] apps/server/src/handoff/HandoffBatch.ts:809-816 does not reserve the window's batch ID

Two overlapping machine-handoff requests with the same window ID can both read it as unused before either finishes its peer capability check. In `apps/server/src/handoff/HandoffTransferRunner.ts:1145-1168` the second write takes its own entry and replaces the first batch's rows and operation list at that ID. Even a retry for the same thread can replace the list with an empty one because its transfer is already open. Allocate or reject the duplicate in the same store update that creates the batch.

The worktree-set gate remains in place. The extracted receiver text helpers have identical values and logic and only type imports.
