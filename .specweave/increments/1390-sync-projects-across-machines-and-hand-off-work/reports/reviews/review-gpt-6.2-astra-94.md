<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=495f12f1fb91552250d903df360472c45cd262e6 at=2026-11-19T19:31:58.004Z -->
# Review: 1390 T-22 link membership
Verdict: ship
Reviewer context: fresh session, static delta review of `495f12f1fb91552250d903df360472c45cd262e6`.

The prior finding is closed. `apps/server/src/project/ProjectLinkMembers.ts:229-239` preserves local relinks and accepts an incoming relink only for its sender. A third party listing the removed member cannot clear the legacy removal; lines 252-257 keep that member out. No incorrect removal, restoration or lost link found in the delta.
