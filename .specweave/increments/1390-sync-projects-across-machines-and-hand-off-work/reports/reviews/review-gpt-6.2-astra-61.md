<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=2cfa95cbafa6c858cad038a71779c21618544b1d at=2026-11-19T16:20:47.118Z -->
SHIP
Verdict: ship

Reviewed `2cfa95cbafa6c858cad038a71779c21618544b1d`, anton-abyzov/specwithcode#715, T-13. Fresh-context delta review. Paths below are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

1 (AC-37). Closed. `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:1828-1832,2110-2114` prunes expired holds for both the local fallback and track checks at final admission.

4 (AC-25). Closed. `apps/server/src/handoff/HandoffTransferRunner.ts:839-861` checks Off inside the lease update and finishes the unsent operation as stayed without interrupting.

7 (EC2-08). Closed. `apps/server/src/handoff/HandoffTransferRunner.ts:872-907` checks the held shell and releases a mismatch before interrupting run B. `apps/server/src/orchestration-v2/MachineLimitHandoff.ts:738-755,804-805` forwards the known provider reset on an untracked threshold move; `apps/server/src/handoff/HandoffTransferStore.ts:394-395` therefore allows reversal at reset.

6 (AC-39 follow-up). Closed. `apps/server/src/handoff/handoffPlan.ts:293-303` excludes unknown usage from reset ranking; `apps/server/src/orchestration-v2/limitHandoffTrack.ts:305-311` discards its reset even when it is the only evidence.

New blockers: none.

Evidence: `git range-diff` matched all four rebased patches unchanged; `git diff --check` passed for the 10-file delta. `c8102a37b` changes only four test suites and a fixture imported only by tests. Assertions cover expiry during peer check, Off between writes, B during preflight (running and idle), the threshold reset and unverified reset evidence. The fix commit also corrects the synthetic sibling run used by the expiry test. Tests inspected, not run.
