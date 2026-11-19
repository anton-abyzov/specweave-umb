<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=46a1994aa829104010b7cd0f35c93f75a1a71f75 at=2026-11-19T19:25:13.929Z -->
# Review: 1390 T-11 handoff batch delta
Verdict: ship
Reviewer context: fresh session, Git objects only. Reviewed `eafe8c5b..46a1994aa829104010b7cd0f35c93f75a1a71f75`.

1. Closed. `apps/server/src/handoff/HandoffTransferRunner.ts:854-872` checks disposition from the prepared shell and checkpoint, not the stored request. Lines 958-975 check the held shell before interruption.
2. Closed. `apps/server/src/handoff/HandoffBatch.ts:812-833` selects and reserves the name in one update. `apps/server/src/handoff/HandoffTransferStore.ts:124-134` holds the same permit from read through persistence. The second caller gets a different ID.

No new path found that moves or interrupts the wrong thread, loses a batch, or combines two batches.

## Follow-ups

An interrupted start after reservation but before planning can leave an empty reservation (`apps/server/src/handoff/HandoffBatch.ts:823-836,932-936`). A retry gets a fresh ID; it does not overwrite the reservation.
