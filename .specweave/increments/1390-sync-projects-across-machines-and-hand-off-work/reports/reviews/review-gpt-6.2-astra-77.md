<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=65bb5f1f65fb42731bf7aed2ed1439c9e14b5e7f at=2026-11-19T17:44:21.165Z -->
FIX FIRST
Verdict: fix first

Reviewed commit: `65bb5f1f65fb42731bf7aed2ed1439c9e14b5e7f`. Fresh reviewer, Git objects only.

1. [high] The extraction drops the second linked-project check. `apps/server/src/handoff/HandoffReceiver.ts:453-457` resolves the project before `sets.take`, then uses that same snapshot to store the replica at lines 481-488. If the project is unlinked while member refs are landing, the old `replicateOne` re-read the link after landing and refused; the new path can record success against the unlinked project. Restore that check inside the landing finalizer's scope. Arrival validation also moved before repository-root resolution. The lock and Git-error mapper remain in place; the reverse import at `apps/server/src/handoff/HandoffSetReceiver.ts:15` is type-only.

2. [medium] `apps/server/src/handoff/handoffPlan.test.ts:1032-1034` and `:1063-1065` now accept arbitrary extra capabilities, not only the new set capability. Even a response that omits the set capability and advertises an unrelated one passes both checks. Assert the exact three expected capabilities at both sites.

No separate fence, replay, definite-refusal release or target-evidence regression found. The v2 gate still precedes offer registration (`apps/server/src/handoff/HandoffReceiver.ts:611-619`); recovery compares the offer and each ordered member path and commit (`apps/server/src/handoff/HandoffSetMoves.ts:865-875`).
