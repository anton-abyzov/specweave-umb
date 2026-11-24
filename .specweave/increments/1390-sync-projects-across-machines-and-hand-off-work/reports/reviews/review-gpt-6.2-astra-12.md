FIX FIRST
Verdict: fix first

Independent review of `anton-abyzov/specwithcode#683`, increment `1390`, task `T-23`. Reviewed commit: `5e03d1bba8a8803b1b6ce5f1f00f76bc782ca710`. Comparison tag: `v1.0.378` (`ea7ea1c1a2baf90abd7001b879893490670f2e98`).

**11 findings: 0 critical, 7 high, 3 medium, 1 low.** The desktop suspend event is now a notice, even without a window. The release blocker is what happens to work the previous release may already have started. An empty heartbeat is not a refusal, and a prepared lease is not a launch receipt.

All source citations below are at the reviewed commit, relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

## T23-01 [high] The public Away start still accepts a sleep trigger

`apps/server/src/away/AwayRunner.ts:624` and `:657-661`; `apps/server/src/away/AwayRpc.ts:35`; `packages/contracts/src/away.ts:558-562`. With no open session and one movable thread, the public `away.start` method accepts `trigger: "sleep"`, saves a new session and forks the normal Leave stages. The thread stage calls `moveThreads`, which sends the machine handoff with reason `away`, not `sleep` (`apps/server/src/away/AwayRunner.ts:455-464`, `:1161`). The new sleep check therefore never sees it. The updated desktop does not send this request; the server nevertheless accepts an explicitly sleep-originated start.

**Fix:** Refuse `sleep` at the start of the command, before resuming, planning or writing. Keep it decodable on historical sessions. Test this public method for no writes, no fork and no moves, alongside a successful manual Leave.

## T23-02 [high] A heartbeat releases the source while the old receiver can still finish

`apps/server/src/handoff/HandoffMoves.ts:1274-1289`; `apps/server/src/handoff/HandoffAutoContinue.ts:44-51`. A legacy sleep takeover reaches the destination, but its reply is lost. After the source upgrades, a heartbeat reaches the old receiver while the takeover is in progress. The receiver's heartbeat does not take the takeover lock and only reports a thread after `markContinued` (`apps/server/src/handoff/HandoffReceiver.ts:893-918`; the tagged receiver has the same ordering). The empty answer makes the source clear its pending request and restore its active lease. The old receiver can then finish, leaving both copies able to run. The same heartbeat is not proof that an auto-continuation already past its admission check has stopped.

**Fix:** Require an operation-specific negative acknowledgement that orders cancellation against the launch, or a positive receipt that fences the source. Keep an ambiguous legacy operation held and visible if the old peer cannot give that guarantee. Test a heartbeat between receipt and final recording, not just a request dropped before delivery.

## T23-03 [high] The source releases thread 501 without asking about it

`apps/server/src/handoff/HandoffMoves.ts:1263-1267`, `:1279-1289`; `apps/server/src/handoff/previousRelease.test.fixture.ts:57-69`. With 501 source records for one peer, only the first 500 leases go on the wire, but the reply is applied to all 501. If the last thread is a pending sleep takeover that already ran remotely, the source restores its local lease. The old peer only reports continuations for IDs it was asked about. An in-memory probe using the tagged heartbeat returned zero continuations for the first page and the existing remote thread ID when asked about the last thread explicitly.

**Fix:** Reconcile only the exact IDs sent. Page the remaining IDs fairly, and preserve each outstanding hold until its own operation is settled. Add a case with an acted-on thread just beyond the wire limit.

## T23-04 [high] A launched thread can be reported as never continued

`apps/server/src/away/awayIntentRoute.ts:139-145`, `:199-210`; `apps/server/src/handoff/HandoffReceiver.ts:780-798`, `:893-897`. The previous intent runner writes `done` **before** its thread hooks run (`apps/server/src/away/previousRelease.awayIntents.test.fixture.ts:258-278`). If the receiver stops after the continuation launches but before `markContinued`, the upgraded status route returns `continuedThreadId: null` and `threadsSettled: true`. The waking source releases that thread and resumes its queue (`apps/server/src/away/awaySleepRoute.ts:329-355`, `:234-239`). The remote thread already exists. This violates EC2-05 even if the interruption happened on the previous release.

**Fix:** Reconcile the deterministic continuation ID against durable launch/thread evidence before reporting an individual thread settled. Return its existing ID without launching anything; if its outcome cannot be established, keep the source held. Test the cut after launch and before `markContinued` with the old wake client.

## T23-05 [high] A failed launch authorizes a first launch on replay

`apps/server/src/handoff/handoffState.ts:693-704`; `apps/server/src/handoff/HandoffReceiver.ts:756-782`, `:812-818`. The receiver saves `document.threads[continuationId]` before calling `launch`. If launch fails before creating the thread, the error path cleans up the grant origin, not that record. A repeat of the same retired sleep epoch now passes the “already began” check and reaches `launch` again. If the transient error has cleared, this is the first actual launch, not recovery of a previously running thread. The reviewed verdict helper returned `proceed` with just a prepared record; the test at `apps/server/src/handoff/handoffIncoming.test.ts:283-292` explicitly expects that result from an empty record.

**Fix:** Distinguish prepared, launched and proven-not-launched. For retired reasons, reconstruct an existing receipt or return unresolved; never invoke launch based only on the prepared lease. A failed launch followed by the same epoch must produce zero new launches.

## T23-06 [high] Unreadable state becomes a successful negative answer

`apps/server/src/away/AwayIntents.ts:399-405`, `:214-230`; `apps/server/src/away/awayIntentRoute.ts:187-198`. A transient failure reading project bindings is converted to an empty list. The drain then persists an `acting` intent as `cancelled` when it had no evidence either way. Separately, a failed read of the handoff document is converted to no incoming threads: even a fully recorded remote continuation can be reported as null and settled. The old source releases on that answer. The failing-store test at `apps/server/src/away/awayIntentRoute.test.ts:379-391` exercises neither production fallback.

**Fix:** Propagate failed reads as an unresolved check. Do not write a terminal intent or return a successful negative status without readable authoritative state. Test an already-acted intent with the first binding or handoff-document read failing, then succeeding.

## T23-07 [high] Re-delivery of an acted-on intent gets a definite “not accepted”

`apps/server/src/away/awayIntentRoute.ts:76-85`, `:153-162`; `apps/server/src/away/awayIntentRoute.test.ts:291-320`. The registration endpoint checks the caller and body but never consults the intent store. Submit the same body after the old receiver acted and the receiver updated: even though cancel/status can report `done`, the POST answers `409 Not accepted`. The test demonstrates those conflicting answers for the same source and body. The legacy wire has no sender-supplied operation ID (`packages/contracts/src/away.ts:245-255`); the receiver cannot distinguish a duplicate from a fresh identical request by inspecting the payload. This is a replay case, not a claim that the ordinary wake path re-registers the intent.

**Fix:** Reject provably new work without starting it. If the request might repeat a recorded operation, preserve the old sender's hold and return the recorded outcome or an answer that leads it to query status. Test both a fresh refusal and re-delivery across the update after a lost acknowledgement.

## T23-08 [medium] Settings promises zero moves before the peer confirms

`apps/web/src/components/settings/HandoffModeSettings.tsx:121-125`, `:226-235`; `packages/contracts/src/handoffMode.ts:413-425`. “Closing the lid moves nothing” remains on screen even when the same view lists an unreachable armed machine. Such a machine can still continue the thread on silence. A snapshot from an older server omits `pendingDisarm`; `?? []` hides the warning but still shows the guarantee. All eight catalogs contain the three new strings. Translation coverage is not the problem.

**Fix:** Distinguish unsupported/unknown, waiting for named machines, and confirmed disarmed. State the guarantee only in the confirmed case. While waiting, say that the old machine may still continue a thread and that this copy will pause. Assert that the guarantee is **absent** in both unconfirmed states.

## T23-09 [medium] Manual Away offers automatic return on power that cannot run

`apps/web/src/components/settings/HandoffModeSettings.tsx:157-175`; `apps/server/src/away/awaySleepSession.ts:543-550`; `apps/server/src/away/awaySleepRoute.ts:413-421`, `:434-438`. The changed description applies “When this machine wakes” to leaving by hand, and offers “Bring back automatically on power.” Manual Leave saves `trigger: "manual"` (`apps/server/src/away/AwayRunner.ts:621-626`). The wake store only returns a session with `trigger: "sleep"` and a sleep record. After a normal Leave, waking on external power returns `none` before reaching automatic Bring back. Manual Leave itself still moves the work; the new promise about returning it is false.

**Fix:** Show only options the manual Leave flow honors, keeping legacy wake reconciliation separate. If automatic return is intended for manual sessions, test that path explicitly rather than reusing the sleep-session description.

## T23-10 [medium] The compatibility tests do not prove takeover refusal or authorized recovery

`apps/server/src/handoff/handoffIncoming.test.ts:254-270` exercises the current verdict function, not the tagged takeover sender's handling of a refusal. `apps/server/src/away/awaySleepRoute.test.ts:164-184` calls the previous release's **sleep** trigger in the test named “a move authorized before the lid close”; its remote result is supplied by the stub at `:49-72`. A regression that released a real user's move on suspend could leave this test green. The same-version lost-request test at `apps/server/src/handoff/handoffMove.test.ts:907-928` is useful, but has no lid close or version change.

**Fix:** Keep the genuine pinned heartbeat and Away intent cases. Add the tagged takeover sender against the current receiver and assert the resulting source lease, run and destination launch count. In the reverse direction, start a manual transfer, interrupt it at a known boundary, deliver suspend, and verify recovery of the same epoch against the tagged receiver. EC2-09 needs positive evidence of those outcomes, not just the presence of the tag string.

## T23-11 [low] The handoff test grows past the file-size limit

`apps/server/src/handoff/handoffMove.test.ts:931-961`. This file grew from 1,695 to 1,738 lines. Eleven changed files are at least 1,500 lines at the reviewed head: this test, the eight phrase catalogs, the Settings search index and the IPC contract. The other ten were already oversized and shrank. The production moves service is 1,498 lines.

**Fix:** Split the oversized handoff test around shared fixture helpers and a focused drain suite. Do not count reductions to previously oversized files as compliance with an absolute limit; handle those existing exceptions separately from T-23.

## Disposition of the four reported limits

- **An armed peer never answers:** not an AC-36 defect by itself. Keeping the affected work paused is the specified safe outcome; do not add a timeout that silently releases it.
- **An old peer stays awake behind a partition and continues once:** not independently fixable by the upgraded source. EC2-05 allows a visibly pending upgrade with the protective hold intact. Premature release and the unconditional UI promise are defects (T23-02, T23-03, T23-08).
- **Interrupted after launch but before recording:** blocks AC-36. Already-started work is reported as absent (T23-04).
- **Same epoch after a failed launch:** blocks AC-36. A prepared record is sufficient to start new work for a retired reason (T23-05).

## Evidence and scope

The PR gate, typecheck, server and web checks reported success at the requested SHA. I compared the pinned fixture bodies to the tag and executed the tagged heartbeat and reviewed verdict/drop functions in memory. Those probes confirmed the missing 501st receipt and the `proceed` verdict with a prepared record. No application build, installation, full-suite rerun, live database or two-machine run was used.

The ordinary suspend path (`apps/desktop/src/app/DesktopHandoffSleep.ts:137-151`) sends only a notice. The sleep endpoint returns `skipped` without writing or sending (`apps/server/src/away/awaySleepRoute.ts:426-432`). The pinned tests genuinely exercise the old heartbeat's arming and clearing rules and the old Away sender's interpretation of a new-intent refusal. I traced the manual dialog, coordinator migration command, Continue here, usage-limit adapter and manual Leave to their non-sleep entry points; the change does not remove them. This is not a live end-to-end pass for those flows. Coordinator standby takeover and delivery of a worker's result to its launcher were not reviewed.
