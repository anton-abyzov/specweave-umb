<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=517d02dc1e1975e6d60b1b59ac5be43c6fd5f0ad at=2026-11-19T18:26:38.878Z -->
# Review: 1390 T-09, round 8
Verdict: ship
Reviewer context: fresh session; Git objects only. Reviewed `517d02dc1e1975e6d60b1b59ac5be43c6fd5f0ad` against base `d3bf4d57e67156a2bdd74205648666dfebe5663e` and the preceding reviewed series. No new findings.

1. Closed (high). `apps/server/src/handoff/HandoffSetReceiver.ts:118-134` registers rollback before the second project lookup. `apps/server/src/handoff/HandoffReceiver.ts:455-457` uses the returned project, and line 484 stores its ID within the scope ending at line 493. The unlink regression at `apps/server/src/handoff/HandoffSetMoves.test.ts:539-564` requires both destination refs to be absent, no incoming replica or launch, and an active source lease. Without the fix the final frame can store the incoming replica before the unlink is observed, violating the test's postconditions. This is a source comparison, not a test execution.
2. Closed (medium). `apps/server/src/handoff/handoffPlan.test.ts:1090` and `apps/server/src/handoff/handoffPlan.test.ts:1119` require exact ordered equality with the four capabilities at line 1080. `apps/server/src/orchestration-v2/limitHandoffTrack.test.ts:583-588` independently requires the same four: v2, plan, track-start, worktree-set.

The range-diff preserves commits 1 and 3 through 14; commit 2 only gains track-start as context before worktree-set. No rebase regression found in the four requested files. The receiver is 1,495 lines, below the 1,500-line limit. No builds or tests run.
