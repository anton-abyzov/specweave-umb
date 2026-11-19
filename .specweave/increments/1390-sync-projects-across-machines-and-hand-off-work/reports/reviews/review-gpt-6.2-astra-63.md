<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=ec7b9344fed5b6cd7fae6ab0c0ac6bd8ca123717 at=2026-11-19T16:23:21.153Z -->
SHIP
Verdict: ship
Reviewer context: fresh session, round 6, T-09.

AC-18/AC-41: closed. `apps/server/src/handoff/HandoffSetMoves.ts:1000-1006` checks each segment with `lstat`. Only ENOENT is absent; links, unexpected types and other errors preserve the checkout. Lines 1045-1051 require matching readable digests for a present regular file. No new blocker.

Evidence: `21edbba6f` changes only `apps/server/src/handoff/HandoffSetMoves.test.ts`. All three regressions assert retry refusal and preservation of the link: dangling leaf, identical-content leaf target and linked parent. Git objects inspected; tests not run. Reviewed `ec7b9344fed5b6cd7fae6ab0c0ac6bd8ca123717`.
