<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=fdf3d2b60ce682d8ed995ced0d0bb85a9e4a0924 at=2026-11-19T19:28:05.876Z -->
# Review: 1390 link membership delta
Verdict: fix first
Reviewer context: fresh session, Git objects only. Head: `fdf3d2b60ce682d8ed995ced0d0bb85a9e4a0924`.

## [high] `apps/server/src/project/ProjectLinkMembers.ts:228-253` lets a third party restore a removed legacy member

A third machine's relink timestamp can erase the local legacy removal before `mayList` checks it. An offered entry with no generation then passes as never removed and is persisted at lines 276-299. Keep the local removal for admission until the member itself returns with a qualifying link or a new accept succeeds. This violates the direct-return rule even though exact unlink matching and refusal of a generationless commit were fixed at `apps/server/src/project/linkMembership.ts:179-183,228-237`.
