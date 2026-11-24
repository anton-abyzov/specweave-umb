FIX FIRST
Verdict: fix first

Reviewer context: fresh cross-family review of `anton-abyzov/specwithcode#692`, T-20, round 1. Reviewed commit: `f134d5f195fe75f8ab76686375c10cb8f24619cc`. Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

## Blocking findings

1. **High, AC-43 / EC2-03: two empty heartbeats do not prove a legacy takeover never launched.** `apps/server/src/handoff/HandoffTransferRunner.ts:458-469` releases after 200 seconds. In the actual `v1.0.383` receiver, `apps/server/src/handoff/HandoffReceiver.ts:775-806` launches the continuation before line 889 persists `markContinued`. If that last write fails, the destination can be running the turn while both heartbeats report no continuation. Raising the replica epoch stops future requests, not a thread already launched. The source then becomes active too. Fix: retain the legacy hold on empty heartbeats; accept a positive receipt, but require durable evidence that rules out the continuation before releasing. Test a launch followed by failure to persist `markContinued`, not just a delayed packet.

2. **High, AC-48 / EC2-04: recovery sends a v2 takeover to a known pre-v2 receiver.** `apps/server/src/handoff/HandoffTransferRunner.ts:502-505` dispatches a stored request without capability negotiation; lines 251-260 add the operation ID and trigger. This is not just a downgrade race: `apps/server/src/handoff/handoffTransferCompat.test.ts:260-279` expects `v1.0.383` to launch a takeover it never received before the upgrade. Lines 72-87 show it silently drops the operation ID. Fix: gate replay as well as first dispatch on `handoff.v2`; an old peer may confirm an existing continuation, but must never receive a takeover to create one. Reverse the pinned test to assert zero takeover calls to the old peer and that the source stays held when the result is unknown.

3. **High, AC-43: a failed terminal write can release the source and leave a live replay.** `apps/server/src/handoff/HandoffTransferRunner.ts:201-205` ignores failure to persist `failed`; lines 339-341 then release the lease and resume the source. For example, the destination refuses the first send because its grant was withdrawn, and writing the terminal transfer record fails while the separate lease write succeeds. Once the grant and storage recover, lines 947-962 replay the still-`sent` operation even though the source lease is active. The destination can now launch without stopping the resumed source. Fix: require a successful durable terminal transition before release or resume. Inject failure only on that terminal write and verify the source stays held across restart.

4. **High, AC-43: a failed receiver rollback is returned as a definite refusal.** `apps/server/src/handoff/HandoffReceiver.ts:963-980,994-1003` clears `standing` on a pre-creation launch failure, then ignores failure to persist `revokeAcceptance`. The source can release on the resulting 409, although the receiver still has a durable `accepted`, `launched: false` record. A duplicate after the project is unpaused follows lines 648-650 and can launch the continuation while the source is active. Fix: return an uncertain response if the revocation cannot be committed. Extend the paused-project test to fail the revocation write and assert that the source keeps its hold.

## Follow-up (non-blocking)

None.

## What I verified

I checked the exact PR head, the T-20 criteria on umbrella `origin/main`, and the pinned release implementation. GitHub reported success for all three server shards and typecheck. I did not run builds or tests in the read-only checkout or access a live database.

The ordering test observes the transfer record at the hold and at network dispatch; moving either write later would fail its assertions. The window-close test interrupts the requesting fiber while the send is suspended, then requires a destination launch and source fence. Manual pull and push reach the same source lock. The pinned cases cover both wire directions, but the replay case explicitly expects the old-peer launch prohibited by this gate. The blockers above were verified by tracing exact-head code and the pinned release, not by a live two-machine run.
