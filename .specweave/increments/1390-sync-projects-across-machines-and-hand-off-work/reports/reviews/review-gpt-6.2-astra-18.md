FIX FIRST
Verdict: fix first

**Reviewed:** `anton-abyzov/specwithcode#683` at `486666d673a357090cb93f6b163e36098fc7afb4`, compared with `5e03d1bba8a8803b1b6ce5f1f00f76bc782ca710`. Increment `1390`, task `T-23`. Fresh review of the round 2 changes only.

**5 high blockers, 0 critical; 4 non-blocking follow-ups. Of 11 prior findings, 5 are fixed and 6 are partially fixed.** A prepared lease no longer launches a thread on replay, and the two directions of the version-pinned transfer test are real. The remaining release risk is letting the source run after the destination already started the work. An unreachable armed peer keeping its threads paused is correct and is not a finding.

## Round 1 findings at this head

Source and test citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`. “Red” means an assertion failed on the tests-only commit `dadb597a8`, before the production fixes. A test that also passes without the fix is identified as a guard, not red evidence.

| ID | Fixed? | Evidence at the reviewed head | Would the test fail without the fix? |
|---|---|---|---|
| T23-01 | Yes | `apps/server/src/away/AwayRunner.ts:668-680` rejects `sleep` before entering Leave. `apps/server/src/away/AwayRunner.test.ts:253-313` exercises both an empty store and an unfinished Leave, checks zero reads, saves and forks, and distinguishes manual Leave. | Yes. Old `start` succeeded instead of refusing. |
| T23-02 | Partly | An empty old heartbeat no longer releases a pending sleep takeover. The source matches the requested thread and epoch; the new receiver orders its answer against launch under the takeover lock (`apps/server/src/handoff/HandoffAutoContinue.ts:260-291`; `apps/server/src/handoff/HandoffReceiver.ts:1049-1077`). A positive answer can still lift an automatic-continuation fence before its replacement is saved: R2-01. | Yes. Mid-takeover, wrong-epoch and quiet-peer cases distinguish the old code (`apps/server/src/handoff/HandoffAutoContinue.test.ts:676-777`). They do not fail a source shell read after a positive answer. |
| T23-03 | Partly | Only sent leases are reconciled. The 501st pending sleep lease stays held on page one and is fenced on page two (`apps/server/src/handoff/HandoffAutoContinue.ts:216-226,267-284`; `apps/server/src/handoff/HandoffAutoContinue.test.ts:781-835`). Mixed-priority paging is not fair: follow-up 1. | Yes. The original 501st lease became active without being asked about; the all-ordinary coverage test saw only 500 IDs. Neither test mixes a full urgent page with an ordinary lease. |
| T23-04 | Partly | With the original epoch identifiable, the receiver finds the existing thread shell and records its receipt without launching. The old wake client keeps an unresolved thread held (`apps/server/src/handoff/HandoffReceiver.ts:631-672`; `apps/server/src/away/awayIntentRoute.ts:223-255`). The lookup still loses a continuation after an onward move and replica eviction: R2-04. | Yes for the reported cut. The old wake-client test failed by assertion (`apps/server/src/away/awayIntentRoute.test.ts:653-680`); it supplies the evidence result. The separate real-receiver test at `apps/server/src/handoff/handoffIncoming.test.ts:994-1027` needed the new method. Neither covers onward movement plus eviction. |
| T23-05 | Yes, for the reported first **destination launch** | Retired reasons return before the launch path; a prepared lease alone cannot authorize a launch. A manual retry still can (`apps/server/src/handoff/HandoffReceiver.ts:694-721`; `apps/server/src/handoff/handoffIncoming.test.ts:850-895`). The new refusal's **source-side** effect is a separate defect, R2-03. | Yes. On the old body, the same retired epoch launched after the earlier failure; the manual retry is a guard that already passed. |
| T23-06 | Partly | Binding and standby read failures no longer finalize an acting intent; a malformed **Away intents** file is an error (`apps/server/src/away/AwayIntents.ts:230-252,411-425,441-471`). A malformed **handoff** document still becomes a successful negative answer: R2-02. | Yes for the injected failures and corrupt intents file (`apps/server/src/away/AwayIntents.layer.test.ts:189-257`). The handoff route test injects `unresolved` rather than reading a malformed handoff document (`apps/server/src/away/awayIntentRoute.test.ts:716-746`). |
| T23-07 | Partly | A matching latest legacy intent gets its recorded success response; a failed list read gives an uncertain `503`. The fallback `409` still treats a compacted receipt as proof nothing happened (`apps/server/src/away/awayIntentRoute.ts:136-155`): R2-05. | Yes for replay with the latest record present: the old response was `409`, not `200` (`apps/server/src/away/awayIntentRoute.test.ts:786-827`). A genuinely fresh refusal already passed. No test compacts the acted record. |
| T23-08 | Partly | Settings distinguishes missing, nonempty and empty `pendingDisarm`, and withholds the guarantee for the first two (`apps/web/src/components/settings/HandoffModeSettings.tsx:135-141,241-260`). The actual list omits an outstanding legacy Away intent: follow-up 2. | Yes. The unknown and named-pending cases failed at the base; the confirmed case already passed (`apps/web/src/components/settings/HandoffModeSettings.test.tsx:165-197`). The tests supply the list. |
| T23-09 | Yes, for manual Leave | Only Ask and Do nothing are offered (`apps/web/src/components/settings/HandoffModeSettings.tsx:32-49,176-191`); the manual-session card respects the latter (`apps/web/src/components/away/awaySession.logic.ts:175-184`). A leftover sleep session is a separate display issue: follow-up 3. | Yes. The base still rendered automatic return on power (`apps/web/src/components/settings/HandoffModeSettings.test.tsx:154-163`). |
| T23-10 | Yes, for the missing two directions | The tagged sender checks a real refusal, local lease, resumed turn and destination launch count. In reverse, the current sender starts a manual move, loses either request or reply, suspends, and recovers epoch 2 against the tagged receiver with exactly one launch (`apps/server/src/handoff/handoffMove.compat.test.ts:94-114,250-330`). | Mixed: 6 of 10 cases failed by assertion. The fresh refusal, undelivered-then-refused resend and both manual recovery cases already passed. Those four are useful compatibility guards. One green case asserts an unsafe source state: R2-03. |
| T23-11 | Yes | `apps/server/src/handoff/handoffMove.test.ts` went from 1,738 lines to 898. The extracted drain suite is 341 lines, its shared fixture 641, and the separate compatibility suite 331. | Not a behavioral test. The original file fails the under-1,500-line check; each of these files passes it. |

## Blocking findings

### T23R2-01 [high] A positive continuation receipt clears the source hold before the permanent fence is saved

`apps/server/src/handoff/HandoffAutoContinue.ts:267-270,285-291`; `apps/server/src/handoff/HandoffMoves.ts:1275-1277,1296-1318`.

An armed old peer continued `T` while the source was silent. The source has an active lease plus `autoFence`. When the peer names the remote continuation, `planAnswer` counts `T` as settled and the caller removes the peer. If the source's next `getThreadShell(T)` fails once, the caller substitutes `null` and skips the permanent fence. In the **same heartbeat**, `fenceQuiet` sees no armed peer and clears `autoFence` (`apps/server/src/handoff/HandoffAutoContinue.ts:316-333,440-442`). The source now accepts a turn while the remote copy exists. The exact-head pure functions returned `disarm=true`, then `lift=["T"]`, with the source lease still `active`. The peer had answered; this is not the accepted silent-peer wait.

**Fix:** Persist the positive receipt and permanent thread fence by source ID before counting it toward disarm. If that write fails, retain the old hold. Shell lookup and interruption can retry without losing the receipt. Test one failed shell read immediately after a positive answer; the source turn gate must never open, including after restart.

### T23R2-02 [high] An undecodable handoff document produces `notStarted` for work that exists

`apps/server/src/handoff/HandoffModeStore.ts:46-54,70-85`; `apps/server/src/handoff/HandoffReceiver.ts:617-638,664-672,1094-1105`.

An earlier receiver launched `T`. After an update, its handoff file is present but is truncated or no longer decodes. The production reader converts that file to `EMPTY_HANDOFF_DOCUMENT` and caches it as a success. The new evidence reader finds no candidate, does not even query the existing thread shell, and returns `none`. The heartbeat includes the exact operation in `notStarted`; Away status can likewise list it as not continued and settled. Either answer can release the source. I exercised the production read branch with malformed JSON in memory. It succeeded with the empty document. A thrown-read test cannot detect this.

**Fix:** Distinguish an absent file from an unreadable existing file on the reconciliation path. Do not cache corruption as a valid empty document or overwrite it with a heartbeat. Use a strict read or an explicit unknown state; emit no negative receipt and leave the hold intact. Test invalid JSON **and** valid JSON with invalid schema through the real store and confirm recovery after the evidence is readable.

### T23R2-03 [high] The old sender resumes on the new receiver's “stays paused” reply

`apps/server/src/handoff/HandoffReceiver.ts:694-714`; `apps/server/src/handoff/previousRelease.handoffMoves.test.fixture.ts:585-593,714-729`; `apps/server/src/handoff/handoffMove.compat.test.ts:164-177`.

The destination has launched the continuation but not recorded its receipt. When its thread store cannot be read, the upgraded receiver returns a structured `409 fenced`. On **resend** the tagged sender keeps the hold; on a **first send** it interprets that same answer as definite, calls `releaseHold` and resumes the turn. The green compatibility test ends with one destination launch and an `active` source lease. The old implementation had already released after the earlier failure in that fixture; the new receiver cannot undo that. It **can** avoid releasing the hold the tagged sender acquired for this new attempt. The wire does not tell it which sender branch owns the request.

**Fix:** Return a positive receipt when it is proven and a definite refusal only for proven new work. For an unknown outcome, use a reply both tagged branches interpret as uncertain, for example an unstructured `503` without the legacy error-body fields (`apps/server/src/handoff/handoffPeers.ts:499-516`). Assert `handing-off`, no source resume and one destination launch on the first-send path, then prove a later readable receipt fences it.

### T23R2-04 [high] After an onward move, evicting the original replica makes an existing continuation disappear from Away status

`apps/server/src/handoff/handoffState.ts:615-636,667-684`; `apps/server/src/handoff/HandoffReceiver.ts:631-638,666,1104-1105`; `apps/server/src/away/awayIntentRoute.ts:244-255`.

A's sleep intent launched a thread on B at epoch 2, but B stopped before marking A's replica continued. B subsequently hands that thread to C at epoch 3. An onward move **alone is not enough** to lose it: while A's replica remains, the receiver still tries its original epoch. But the unmarked replica is in the first eviction group of the 500-entry cache. Once it is evicted, the Away status request supplies no epoch and the only remaining B record has the epoch-2 ID with an epoch-3 lease. The exact-head lookup found the record when passed epoch 2 and returned `[]` without it. Status then says `continuedThreadId: null` and `threadsSettled: true` for a done intent. The tagged wake client releases A's thread and resumes its queue while C owns the continuation (`apps/server/src/away/previousRelease.awaySleep.test.fixture.ts:388-414`).

**Fix:** Resolve from an immutable source-to-continuation identity or durable launch receipt that survives both an onward move and replica eviction. For older data, return unresolved if absence cannot be established. Add this combined case to the tagged wake test; A's queue must not resume.

### T23R2-05 [high] Compacting unrelated intents changes an acted replay into “Not accepted”

`apps/server/src/away/awayIntentRoute.ts:142-155`; `apps/server/src/away/AwayIntents.ts:63,366-373`.

Use the lost-acknowledgement replay from the compatibility test. A's request was acted on. Before redelivery after the update, 50 later intents from another source have settled on the old receiver. The global retention limit drops A's receipt even if its work is still on the destination. I ran the exact-head compaction and registration branches with the same parsed request: `200` with the receipt, `409` after compaction. The route checks neither the project takeover nor the thread continuation before issuing that refusal. On a first intent send with no older hold, the tagged sender processes the definite error by writing `send-failed` and releasing everything (`apps/server/src/away/previousRelease.awaySleep.test.fixture.ts:542-566`). This is the redelivery case, not a claim that an ordinary wake sends registration again.

**Fix:** Before a negative reply based on missing history, reconcile the requested work against durable project and thread evidence. If it already moved or the outcome cannot be established, preserve the old sender's hold and let status settle it. Keep a compact per-source receipt until safe to retire. Extend the existing lost-answer test with eviction by an unrelated source.

## Follow-up (non-blocking)

1. **Paging fairness.** `apps/server/src/handoff/HandoffAutoContinue.ts:213-226` rotates only urgent leases when there are at least 500. With 500 unresolved requests and one ordinary lease, the ordinary lease appeared on **0 of 20** pages in an in-memory probe. Reserve capacity for both groups and page operations rather than truncating a flattened list. This does not justify releasing an unanswered hold.
2. **Pending Away intent missing from Settings.** `apps/server/src/handoff/handoffState.ts:863-886` considers armed peers, auto-fences and pending thread takeovers, not the persisted `awaySession`. A source with only a pending legacy Away intent can therefore supply `[]` and display the guarantee at `apps/web/src/components/settings/HandoffModeSettings.tsx:135-141` while its old target is unreachable. Include that target until reconciliation. The display alone does not release work.
3. **Legacy return preference.** `apps/web/src/components/settings/HandoffModeSettings.tsx:39-46,176-191` displays saved `auto-on-power` as Ask. A leftover sleep session can still return automatically on external power (`apps/server/src/away/awaySleepRoute.ts:411-421`). Show the effective legacy behavior for that session or migrate the preference. Manual Leave is not affected.
4. **Existing oversized wiring file.** The round 2 layer additions at `apps/server/src/server.ts:805,821` grow that already oversized file by two lines to 1,681. The requested test-file split is complete; handle the wiring-file limit separately.

## Evidence and limits

The [PR gate passed at the exact reviewed head](https://github.com/anton-abyzov/specwithcode/actions/runs/44516732333/job/135545868110). The red comparison is [run 44512633934](https://github.com/anton-abyzov/specwithcode/actions/runs/44512633934). I checked the tagged sender's distinct first-send and resend branches, the tagged wake client's release rules, and the production storage and reconciliation call sites. `v1.0.378` is the fixture pin; the handoff and Away directories have no diff between that tag and `v1.0.383`.

Local checks used Git objects and isolated functions with synthetic in-memory inputs. They were not a full integration run. No application source was changed; no install, build, live database or two-machine run was used. Round 1's accepted entry points were not reopened.

- Prior review: `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t23/review-683-round-1.md`
- Worker report: `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t23/round-1-fixes-report.md`
- Red evidence: `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t23/red-round2-ci.txt`
- Green evidence: `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t23/green-round2-ci.txt`
