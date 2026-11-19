<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c0ab4187d59bfb58598c86634ad9599dfa665a8c at=2026-11-19T15:20:04.444Z -->
SHIP
Verdict: ship

Reviewed commit: `c0ab4187d59bfb58598c86634ad9599dfa665a8c`. No production file changed since round 5.

AC-44 blocker closed: `apps/server/src/handoff/handoffFollow.test.ts:160-195` checks that the original refused row stays disposed with no delivered runs, the distinct accepted row records exactly `[run.id]`, and the only kept message targets the launcher with `wakeOf(accepted?.id, run.id)`. A wake from the refused row can no longer satisfy the test.
