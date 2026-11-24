FIX FIRST
Verdict: fix first

| Round 2 finding | Disposition | Evidence at the reviewed head |
|---|---|---|
| T23R2-01 | Fixed | `apps/server/src/handoff/HandoffAutoContinue.ts:270-305,493-520` saves the permanent fence by source ID before counting the answer. Failed persistence prevents disarm; a later shell-read failure cannot undo the write. |
| T23R2-02 | Fixed | `apps/server/src/handoff/HandoffModeStore.ts:55-65,81-98` distinguishes a missing file from invalid JSON or schema. A failed read is neither cached nor overwritten. `apps/server/src/handoff/HandoffReceiver.ts:745-759` returns unresolved rather than a negative receipt. |
| T23R2-03 | Fixed for the reported first-send and resend cases | `apps/server/src/handoff/HandoffReceiver.ts:781-803` returns a positive receipt for the matching launch, a definite refusal for proven absence, and an uncertain response otherwise. The first-send regression now checks the source lease, not just the destination launch count. |
| T23R2-04 | Fixed | `apps/server/src/handoff/HandoffReceiver.ts:690-752` and `apps/server/src/handoff/handoffState.ts:725-747` recover a launch by receipt or original continuation ID after an onward move. Missing evidence or an incomplete epoch scan cannot establish absence. |
| T23R2-05 | Fixed for compaction | `apps/server/src/away/AwayIntents.ts:366-394` retains each source's latest and latest done records. If an old release already evicted the record, `apps/server/src/away/awayIntentRoute.ts:202-229` consults work evidence before refusing. The tagged-source regression covers 51 later deliveries from a different machine (`apps/server/src/away/awayIntentRoute.test.ts:946-990`). |
| Round 2 follow-up 2 | Fixed | `apps/server/src/handoff/handoffState.ts:1014-1042` includes the persisted legacy sleep target until wake reconciliation or Bring back. This no longer depends on also having an armed peer or a pending thread takeover. |

## Blocking findings

### T23R3-01 [high] A cancellation count can resume a thread that the destination already continued

`apps/server/src/away/awaySleepRoute.ts:266-281` checks that the local hold began with this sleep session, then treats `cancelled > 0` as proof that nothing moved. The cancel request contains only the source environment ID. The reply does not identify a delivery or the work it cancelled.

Consider one legacy sleep request delivered twice. The first delivery acted and continued thread T; the second reached the old target before upgrade and is still waiting. The tagged receiver assigns a fresh intent ID to each delivery and replaces only **waiting** records, leaving the first done record intact (`apps/server/src/away/previousRelease.awayIntents.test.fixture.ts:133-165`). There was only one source session, so its hold has `since === sentAt` (`apps/server/src/away/previousRelease.awaySleep.test.fixture.ts:503-532`). On wake, before the second delivery acts, either receiver can cancel it and return `cancelled: 1`; the first delivery is unaffected (`apps/server/src/away/AwayIntents.ts:153-187`). The upgraded source skips status, clears the entire hold, resumes T's local queue and records “nothing moved” while T continues remotely (`apps/server/src/away/awaySleepRoute.ts:242-246,274-280,410-414`). This is on the changed AC-36 legacy recovery path; it requires neither an unreachable peer nor a manual override.

**Fix:** Treat the cancel count as proof that pending work was stopped, not that earlier deliveries never acted. Reconcile held items through status before releasing them. For the reverse version pairing, do not send a positive count to a legacy source when it could release previously moved work. The regression should seed one done and one waiting delivery for the same source session, then verify that wake fences T without resuming its queue. The current cancellation test seeds an *older local hold*, so it takes the other branch (`apps/server/src/away/awaySleepRoute.test.ts:403-437`).

## Follow-up (non-blocking)

The existing Away registration route returns authentication and grant errors before looking up replay evidence (`apps/server/src/away/awayIntentRoute.ts:344-358`; `apps/server/src/away/awayPeerCall.ts:158-176`). Unlike the changed takeover route, a transient grant-read failure there can still produce a definite `403` on redelivery. Track the unchanged early-return path separately. The compaction regression calls `recordIntent` directly and does not exercise that boundary (`apps/server/src/away/awayIntentRoute.test.ts:892-909`).

## What I verified

Fresh delta review of `anton-abyzov/specwithcode#683`, increment `1390`, T-23 / AC-36. Fetched head: `10d7c8f1e9c0b397a7a4e751d65901b4938a19c8`. Round 2 head: `486666d673a357090cb93f6b163e36098fc7afb4`. Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`. I traced the source and receiver paths through Git objects, including the tagged compatibility fixtures. No checkout, build, install or local test run.

**Red evidence:** `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t23/red-round2-ci.txt` is for `dadb597a8`, not this delta. The matching log is `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t23/red-round3-ci.txt`. Its tests-only commit `cd87dd7e8` and this branch's `76abede29` have the same stable patch ID, `d9b70cfaf1bb0f3af4023ce3cf126404c438a314`. The red jobs show the new assertions failing on premature disarm, corrupt-file negative answers, a released first-send lease, local queue resume after onward movement, `409` instead of `503` after compaction, and an empty pending-target list. Not every failure was behavioral: the retention layer fixture failed to decode before its assertion because its result lacked `detail` (`apps/server/src/away/AwayIntents.layer.test.ts:279-285`); the separate tagged replay assertion is the red evidence for R2-05.

**Head CI:** As of 10:03 a.m. EST on November 19, 2026, `PR Gate (server 3/3)` was still running. No check had failed; all other reported jobs had succeeded or been skipped. The blocking finding is a source trace, not an observed CI failure.
