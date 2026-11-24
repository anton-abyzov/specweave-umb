<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=be6ee08acece081d5facbd4b9b355b2130171469 at=2026-11-19T16:08:41.257Z -->
# Review: 1390 T-09, round 4
Verdict: fix first
Reviewer context: fresh session; reviewed be6ee08acece081d5facbd4b9b355b2130171469.

1. Closed: apps/server/src/handoff/HandoffSetMoves.ts:865-875 matches offer ID and every ordered member path and commit against the stored incoming set. The restart test starts from an existing incoming record.
2. Closed: apps/server/src/handoff/HandoffReceiver.ts:649-665,685-688 requires both base and set capabilities before opening or acknowledging a remote offer.
3. Partly closed [high]: apps/server/src/handoff/HandoffSetMoves.ts:1008-1019 treats all worktree read errors as null and skips comparison. An edited, unreadable ignored file still passes the path allowlist at lines 1036-1044 and can be force-removed at lines 904-906,1158. Refuse cleanup on an unreadable or unverifiable file without reporting its contents.

Evidence: 814e3af78 changes only tests and their fixture. The assertions cover all three reported cases, but not a failed digest read. Git-object inspection only; no tests run.
