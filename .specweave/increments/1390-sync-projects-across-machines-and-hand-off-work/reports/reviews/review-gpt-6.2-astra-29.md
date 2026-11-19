FIX FIRST
Verdict: fix first

## Round 1 disposition

Fresh review of `anton-abyzov/specwithcode#692`, increment 1390, T-20, at `da173b02ebc817d24e6abf41310da1ae0cc42eb8`. Line references below are at that commit, relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff`, unless a release tag is specified.

| Round 1 | Disposition | Head evidence | Does the test fail without the fix? |
|---|---|---|---|
| T20R1-01 | Partial | `HandoffTransferRunner.ts:485-495` no longer releases on repeated empty heartbeats. The first status reply after the destination updates can still release the same unresolved hold. | Yes. `handoffTransferCompat.test.ts:175-190,287-310` covers elapsed time and source restart, not destination upgrade. |
| T20R1-02 | Fixed | `HandoffMoves.ts:723-737` reads the advertised capability. `HandoffTransferRunner.ts:536-553` retains the hold on probe failure and uses status, not takeover, for an old peer. | Yes. `handoffTransferCompat.test.ts:262-283` saw one takeover instead of zero before the fix. |
| T20R1-03 | Fixed | `HandoffTransferRunner.ts:208-214,358-366` requires a written terminal transition before releasing or resuming after refusal. | Yes on the supplied red baseline. `HandoffTransferRunner.test.ts:382-406` checks the open record, lease and turn gate across restart. See the fault-injection qualification below. |
| T20R1-04 | Fixed | `HandoffReceiver.ts:996-1011,1077-1090` restores `standing` if revocation fails and returns an uncertain 503 instead of a definite 409. | Yes on the supplied red baseline. `HandoffTransferRunner.test.ts:349-366` checks the surviving acceptance, source hold, single subsequent launch and source fence. |

## Blocking findings

**High · T20R1-01 · The destination upgrade turns missing legacy evidence into a false refusal (AC-43 / EC2-03).** `HandoffTransferRunner.ts:544-551` moves a stored request for an old destination onto the status-only path. Suppose that destination wrote the continuation's active lease and launched it, but failed to save `markContinued`. Those are separate writes in `v1.0.383:HandoffReceiver.ts:752-775,888-891`. The source correctly stays held while the peer is old.

After the peer updates, `HandoffReceiver.ts:1123-1143` checks the incoming continuation marker and the new transfer store, **not the existing continuation's lease or thread**. Neither checked record exists in this failure case. `HandoffTransferStore.ts:336-361` therefore writes `not-accepted`, and `HandoffReceiver.ts:1182-1186` returns it. `HandoffTransferRunner.ts:445-453,493-496` then activates the source. The refusal prevents a future takeover; it does not fence the continuation the old release already created. Both copies can accept work.

**Minimal fix:** Before creating a negative verdict for a legacy status query, check the durable lease and thread for the deterministic continuation ID under the incoming lock. Return a verified receipt if possible; if a launch may have occurred or the lookup fails, return uncertainty and retain the hold. Extend `handoffTransferCompat.test.ts:287-310` through a destination upgrade, preserving its old active lease and created thread but no `markContinued`. The next tick must not activate the source.

## Follow-up (non-blocking)

`HandoffTransferRunner.ts:743-746,769-783` suppresses release if writing `stayed` fails, but two pre-send callers still invoke `resume` unconditionally. The `handing-off` turn gate rejects the start (`HandoffTurnGate.ts:65-68`); I found no double execution on that path. Return whether release succeeded and call `resume` only on success, so no resume is attempted or promised while the hold remains.

## What I verified

I compared the ten fix-touched files between the round 1 and round 2 commits. Their contents at `f134d5f1` match the rebased parent `fccfe04a^`; unrelated main changes were excluded. I checked the seven named gates on umbrella `origin/main`, the pinned release's write order, and the changed replay and release paths. I did not reopen the accepted UI, stale-lease, window-lifetime or live-run scope.

The supplied red run `44539137622` records five failed tests across the four findings. Its commit changed the tests but not the in-memory store's write-failure hook. For T20R1-03 and T20R1-04 the red assertions therefore fail **before** proving how the old logic handles the injected write error. With the head's hook retained (`HandoffTransferStore.ts:160-171`), reverting only the respective production guard would fail the subsequent source-hold assertions: the old runner released after the failed write, and the old receiver returned a definite refusal after failed rollback. That last comparison is a code trace, not another test run.

GitHub reported the exact requested head, all three server shards, typecheck and the aggregate PR gate green. The upgraded-destination case above is not exercised by those regression assertions. No local builds, installs, test runs, commits, PR comments or live database access.
