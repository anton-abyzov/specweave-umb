FIX FIRST
Verdict: fix first

`anton-abyzov/specwithcode#690`, increment `1390`, task `T-24`, round 2. Reviewed `3f161e9403f0effd2ad2b516be8843f5722efbfb` in a fresh OpenAI reviewer session. All six original failure cases are fixed. One new high-severity blocker: a takeover explicitly identified as a review can still launch unlocked if the final checkpoint no longer identifies it as one.

## Round 1 disposition

Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at the reviewed commit. Red lines refer to `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t24/red/round1.txt`.

| Finding | Disposition and head evidence | Fails without fix? |
|---|---|---|
| T24R1-01 | Fixed. `apps/server/src/handoff/HandoffReceiver.ts:660-661,734-740` returns on a lost reviewer, before the receiver lease at `:796` or launch at `:817`. | Yes, red line 14: one launch instead of zero. The head test also checks no lease or continuation. |
| T24R1-02 | Fixed. `apps/server/src/orchestration-v2/reviewFallbackLock.ts:65-69,82-85,104-114` filters the coordinator candidate and checks the actual command selection. `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:674-680` wraps both limit and failed-to-open paths. | Yes, red line 33: selected the author's unlisted Opus model instead of waiting. |
| T24R1-03 | Fixed. `apps/server/src/handoff/handoffReviewLock.ts:109-115,263-269` refuses an unknown title-derived family at departure, including self, and rechecks the title even with explicit `null` at arrival. | Yes, red line 72: the self departure succeeded. |
| T24R1-04 | Fixed for the reported downgrade. `apps/server/src/handoff/handoffPeers.ts:526-533,599-617` sends marked checkpoints and takeovers only to dedicated paths. A stale positive cache cannot make the previous release accept either as ordinary work. | Yes, red line 186: one ordinary replication after downgrade. The head test checks both paths with the same warm cache and ordinary replication as a control (`apps/server/src/handoff/handoffPeers.test.ts:399-434`). |
| T24R1-05 | Fixed. `apps/server/src/handoff/handoffReviewLock.ts:272-295` selects only from listed models. Neither a requested nor a stored model fills an empty catalog. | Yes, red line 88: empty failure list instead of the provider refusal. Head coverage includes takeover and an ordinary-thread control. |
| T24R1-06 | Fixed. `apps/server/src/handoff/handoffReviewLock.ts:143-154,203-206,295` and `apps/server/src/orchestration-v2/reviewFallbackLock.ts:86-92` give carried options precedence on the compatible model; the wrapper also covers failed-to-open fallback. | Yes, red lines 112 and 140: arrival selected `low` rather than `high`; fallback omitted the carried effort. |

## Blocking findings

### T24R2-01 [high] A marked takeover accepts an unlocked checkpoint

`apps/server/src/handoff/HandoffMoves.ts:838-849,858-866` uses the final checkpoint's sequence but the **first** shell's review identity. Each `prepare` reads the shell again (`:488-497`). For a running, title-only `Adversarial review:` thread, a rename between those reads produces a final checkpoint with the new title and `reviewLock: null` (`:335-352`). That checkpoint replaces the replica title and lock (`apps/server/src/handoff/handoffState.ts:557-589`). The sender still correctly marks the takeover `review: true`.

The receiver drops that evidence: `apps/server/src/handoff/handoffRoute.ts:181-186` routes the marked operation to ordinary takeover; `apps/server/src/handoff/HandoffReceiver.ts:734-740` rejects only `refused`. The new title and null lock return `unlocked` (`apps/server/src/handoff/handoffReviewLock.ts:263-269`). With Claude requested and available, the receiver writes the lease and launches Claude without review routing (`apps/server/src/handoff/HandoffReceiver.ts:796-817,823,837`). This involves two current-version machines, not a previous-release copy. The dedicated-route test checks forwarding to a stand-in receiver, not this disagreement.

**Minimal fix:** Make the review operation require a `locked` receiver decision. Reject `unlocked` before workspace preparation and at the final decision before the lease; never substitute the requested model. Keep the operation's review identity across both source checkpoint reads, refusing if they disagree. Cover a marked takeover of an ordinary-titled, lockless final checkpoint with the real receiver: expect “Review stays here”, no launch, no receiver lease and no continuation.

## Follow-up (non-blocking)

One cleanup case: `apps/server/src/handoff/HandoffReceiver.ts:688-714,734-736` can apply the checkpoint in place or materialize a worktree before the final live refusal. No continuation runs, but the receiver's workspace can change. The regression changes sign-ins on the settings read, so it stops at the earlier check (`apps/server/src/handoff/handoffReviewLock.test.ts:798-810`). Cover loss during materialization separately and account for any changes left behind.

## What I verified

- Resolved the head with `gh pr view 690 --json headRefOid`. The supplied `3f161e9425` is not a prefix of that commit. Read the Git objects, compared against `b19c465fb0554403a8dc6bea249420199f554bb3`, and scoped findings to the T-24 delta. Checked AC-40 and the accepted EC2-04 amendment on umbrella `origin/main`.
- All seven named regression tests failed on the tests-only rebased build `5f8b7f65f`, Actions run `44532755124`. That is not a run on the literal round 1 SHA. Exact-head `Checks` run `44535021037` succeeded, including all three server shards. `git diff --check` passed.
- Checked the previous release's unknown-path rejection, both current transport paths, the persisted replay request, the final receiver lease/launch ordering and the two fallback branches. The new blocker is a source trace, not a live two-machine reproduction. No builds, installs, source edits, PR comments or live database access.
