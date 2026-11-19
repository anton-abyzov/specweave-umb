<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=7e365dd3bcd8d2e7fa1491ba328216c92db43fa9 at=2026-11-19T17:42:30.443Z -->
FIX FIRST
Verdict: fix first

Reviewed commit: `7e365dd3bcd8d2e7fa1491ba328216c92db43fa9`. Fresh-context, Git-object-only delta review. The exact round 3 order is fixed for upgraded peers: an unlink for L1 does not match B re-linked through C as L2. Three paths still violate that guarantee or its converse.

## [high] A delayed unlink removes the replacement link

`apps/server/src/project/ProjectLink.ts:808-825` selects B by machine and project, ignores the request's `member.linkId`, then records the ID from the *current* row. If two unlink requests target L1 and the second arrives after B returns as L2, the second removes L2 and advertises a removal for L2. Restarting between calls does not help. The contract carries the selector (`packages/contracts/src/projectLink.ts:365-370`). Check it under the lock before changing the list; a stale request must be a no-op, not an unlink of the replacement. The member-side leave also lacks an expected identity or link (`packages/contracts/src/projectLink.ts:355-364`).

## [high] A delayed link commit reverses a newer membership

`apps/server/src/project/ProjectLink.ts:720-723,744-769` treats every different operation ID as a replacement. A retry of the original L1 commit after L2 is active records a removal for L2 and restores L1. The write command ID includes the *current* settings revision (`apps/server/src/project/ProjectLink.ts:367-374`), so the original receipt does not fence the replay. Recognize retired operations before either write; persist the accepted transition so retry after restart cannot reverse it.

## [high] An unverified link ID can restore a removed member

`apps/server/src/project/ProjectLinkMembers.ts:163-171,218-230` verifies that the sender is listed, not that the advertised membership was accepted. Once A has removed B/L1, a listed peer's claim for B with a different ID is enough for A to store B again, without a new accept. Even without a dishonest peer, a delayed list for L1 passes if A learned B only at L2 and only remembers removing L2. An unequal ID establishes difference, not freshness. Require verifiable evidence of the replacement or reconciliation with the joining copy before overriding a removal.

## Other delta checks

Wire: the optional fields are compatible with ordinary struct decoding (`packages/contracts/src/logicalProject.ts:27-34,127-134`; `apps/server/src/handoff/linkedSyncWire.ts:120-130`). An ID-less removal does not match a tagged member. The reverse is asymmetric: an ID-bearing removal matches *any untagged* incarnation (`apps/server/src/project/linkMembership.ts:91-99`), so losing an ID on an old-peer round trip does not establish that the membership predates the removal. No mixed-version runtime test was run.

Handoff: `924571c24` deliberately keeps the existing destination coordinator active when work lands beside it (`apps/server/src/fleet/MachineHandoff.ts:1219-1226,1478-1482`). The standalone-join test checks the existing goal, active binding and separate received project (`apps/server/src/fleet/MachineHandoff.test.ts:1205-1214`). This agrees with AC-35.

Rebase: commit 1 removes main's two new tests of the retired coordinator handover along with the retired suite. Commit 7 retains main's `beforeRecordsRead` fixture field alongside `binding`. The nine other pre-existing patches are unchanged. No additional rebase blocker.

Red-test inspection, not execution: at `080b8f70a`, the test kit supplies the capability flag (`apps/server/src/project/ProjectLink.testkit.ts:328-344`). C has no prior removal to date its re-link; when A returns, the pre-fix adoption removes B by member key (`apps/server/src/project/ProjectLinkMembers.ts:177-191`). Both cross-peer clock cases therefore reach the membership assertion at `apps/server/src/project/LinkedMembershipSync.test.ts:231` with B missing. The same-peer test at line 244 is a control: A knows its own removal and dates the replacement after it. These tests do not deliver a stale direct unlink or replay a link commit.
