<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=9f4f13151fa1849bccd1915dc3c48ab65f843d42 at=2026-11-19T16:29:17.592Z -->
SHIP
Verdict: ship
Reviewer context: fresh session, round 4 delta at `9f4f13151fa1849bccd1915dc3c48ab65f843d42`.

Closed: `apps/server/src/handoff/HandoffTransferRunner.ts:585-616` checks batch support before legacy settlement. When the destination lacks batch support, the accepted transfer remains unknown with its sequence intact; no transfer status query or repeat takeover is sent.

Folder journal: `apps/server/src/handoff/HandoffBatch.ts:911` and `:1117` pass the row writer for new and recovered batches. Line 442 requires it. The PR body explicitly documents both callers and the absence of a default. No new blocker in the four-file delta.

Evidence: `75889e290` changes only `apps/server/src/handoff/HandoffBatchRecovery.test.ts`. The case at line 565 asserts zero status calls and launches across both downgrade stages, then one Ready launch after batch support returns. Inspected, not run.
