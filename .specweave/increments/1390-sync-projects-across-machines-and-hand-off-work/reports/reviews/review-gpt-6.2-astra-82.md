<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c0009433a2ae369487a59258d1c462283b8a1fc0 at=2026-11-19T18:51:17.701Z -->
# Review: 1390 T-22 equal coordinators, round 5
Verdict: fix first
Reviewer context: fresh session, Git objects only. Reviewed `c0009433a2ae369487a59258d1c462283b8a1fc0` in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`. Citations are relative to that repository at that commit.

## [high] 1. Delayed unlink: closed for two known generations, not for a release-relayed replacement

`apps/server/src/project/LinkedMembershipSync.test.ts:419-431` explicitly establishes a receiver listing live L2 without its generation after a legacy relay. Before it learns L2's generation, a delayed L1 unlink passes `apps/server/src/project/linkMembership.ts:156-168`: the receiver treats L2 as zero and checks link-ID disagreement only for equal positive generations. `apps/server/src/project/ProjectLink.ts:842-851` removes L2. A higher claimed generation is likewise not proof that the unlink names the listed membership. Refuse ambiguous destructive requests unless the membership being ended is confirmed.

## [high] 2. Delayed commit: closed for a known L2, not for a removal without a generation

`apps/server/src/project/linkMembership.ts:207-210` rejects the original counted L1 commit before any write when counted L2 is active (`apps/server/src/project/ProjectLink.ts:745-752`). But a delayed generationless commit for an already removed legacy member still returns `add`: a generationless removal counts as zero, below the minimum threshold of one (`apps/server/src/project/linkMembership.ts:83-92,203-211`). The kept copy re-adds the member and clears its dated removal without a new accept (`apps/server/src/project/ProjectLink.ts:782-793`; `apps/server/src/project/linkMembership.ts:245-256`). Treat a matching dated removal as a refusal when a commit cannot prove a later acceptance.

## [high] 3. Unverified member list: open

`apps/server/src/project/ProjectLinkMembers.ts:164-172` verifies that the sender is listed, not that the absent member accepted a new link. A listed peer's claim above the locally recorded removal passes `apps/server/src/project/linkMembership.ts:116-124` and is added and persisted at `apps/server/src/project/ProjectLinkMembers.ts:228-235,255-271`. The generation orders honest messages but does not authenticate another member's acceptance. Verify that acceptance before crossing a recorded removal.

## Rebase and compatibility

`git range-diff` matched all 14 previous commits. Only the retired-phrase catalog's integration with Phase 3 and its patch context differed. The accepted handoff change is patch-identical (`924571c24` to `b478a2286`); the handoff implementation and project command validator are unchanged between reviewed heads. No handoff coordinator regression found. The generation fields are optional, not a wire decoding break; release `v1.0.390` does not carry them. Mixed-version semantics are unsafe as described above.

## Follow-ups

Add coverage at the interval before the legacy-relayed member is enriched, not just after sync converges (`apps/server/src/project/LinkedMembershipSync.test.ts:431-435`). No tests or builds were run, as requested.
