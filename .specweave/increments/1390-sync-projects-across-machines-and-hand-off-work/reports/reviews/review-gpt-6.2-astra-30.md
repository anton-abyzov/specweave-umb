SHIP
Verdict: ship

## Round 3 disposition

`anton-abyzov/specwithcode#681`, increment 1390, T-19. Reviewed commit: `80007a6129b61415fd994be186bb4797e8af38d1`. Fresh reviewer: `gpt-6.2-astra`. Source and test citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

| Finding | Disposition at head | Does the test fail without the fix? |
|---|---|---|
| T19R3-01: listed peer without a grant | **Fixed.** The launcher probes each peer for this project; a failed request, grant refusal or missing link excludes the peer from the reach list (`apps/server/src/handoff/handoffFollow.ts:132-166,188-196`). The middle machine rejects an excluded destination before holding the worker (`apps/server/src/handoff/HandoffMoves.ts:712-717,726-729`). | **Yes.** The tests-only head advertised the ungranted peer and failed the reach-list assertion. The regression checks the list and one completion on the permitted route; the separate out-of-list test checks refusal with an unchanged lease (`apps/server/src/handoff/handoffOnward.test.ts:94-115,120-145`). |
| T19R3-02: earlier success replaces a stopped run | **Fixed.** Candidates starting before the recorded stop are excluded. If only the stopped run's start is known, the selector requires a strictly later start under the thread's no-overlap invariant. A status-only candidate is not enough to report completion (`apps/server/src/fleet/handoffDelivery.ts:152-176,189-198`). | **Yes.** Two selector tests failed and the follower regression timed out before the fix. The latter now checks zero wakes across repeated reads after interruption, then exactly one failure wake after the real replacement runs (`apps/server/src/fleet/handoffDelivery.test.ts:95-125`; `apps/server/src/fleet/handoffFollowerRoute.test.ts:272-305`). The changed `report` to `unsure` assertion tests missing ordering evidence, not a weaker expectation for the known-time case. |
| T19R3-03: same-machine replacement strands the remote launcher | **Fixed.** A self-target with a remote launcher is refused even when another model was selected. Hand-back to the launcher remains allowed (`apps/server/src/handoff/handoffFollow.ts:110-122`). The refusal precedes preparation and the hold (`apps/server/src/handoff/HandoffMoves.ts:706-717,726-729`). | **Yes, by reaching the wrong branch.** The unfixed path entered local replication and failed with `TypeError: receiver.replicate is not a function`; it did not reproduce a lost wake end to end. At head the test checks the refusal reason, active lease at epoch 1, no checkpoint or successor, and no new launch or follow row (`apps/server/src/handoff/handoffOnward.test.ts:150-174`). |

## Blocking findings

None. All three prior findings are fixed. No new failure meeting the round-four convergence rule was found in the two-commit delta.

## Follow-up (non-blocking)

**Low: require a result for the requested thread before advertising reach.** At `apps/server/src/handoff/handoffFollow.ts:154-163`, `results: []` counts as a successful probe because there are no failures to inspect. The wire schema accepts an empty array (`apps/server/src/handoff/handoffWire.ts:189-199`), but the reviewed receiver emits one result per requested thread (`apps/server/src/handoff/HandoffReceiver.ts:483-490`). No lost result on the current receiver was demonstrated. As a defensive check, require a result matching `shell.id` and test the empty response.

## What I verified

- Read round three against the AC-44 and EC2-01 gates. Compared the seven changed files between `59d702bb77d85f5f6ece19d2fbd1738cc2a291f7` and the reviewed head, using Git objects rather than the checked-out branch. Traced the production preflight through the worker credential and the receiver's project-link and grant checks.
- Confirmed that [red run 44537769755](https://github.com/anton-abyzov/specwithcode/actions/runs/44537769755) failed at tests-only head `52d7c3a02867ceb75743b67f7a43a243d2898a87`. Matched the five failures in `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t19/red-ci-r3/red-summary.txt` to the assertions above.
- Confirmed the PR head and [green run 44539883155](https://github.com/anton-abyzov/specwithcode/actions/runs/44539883155) both name `80007a6129b61415fd994be186bb4797e8af38d1`. All three server shards, fleet, typecheck and the aggregate PR gate passed. Used existing CI evidence; no local suite, build, install or live two-machine run. No app edits, commits, PR comments or live database access.
