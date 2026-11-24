FIX FIRST
Verdict: fix first

| Round 2 item | Disposition | Evidence at the reviewed head |
|---|---|---|
| T20R1-01: upgraded legacy destination | Fixed | `HandoffReceiver.ts:1143-1206` looks up the deterministic continuation before writing a negative verdict. A present thread yields a receipt; a lease with an unreadable thread yields an uncertain 503. `HandoffTransferRunner.ts:392-412,553-555` asks the recorded destination for status rather than repeating the legacy takeover. |
| Resume only after a successful pre-send release | Fixed | `HandoffTransferRunner.ts:225-237,787-801,825-843` propagates failure of either the terminal transition or the lease write. Neither the checkpoint error, unsettled child nor launcher-registration error resumes the interrupted turn on those failures. |

Reviewed `anton-abyzov/specwithcode#692` at `13badcb7944321e740765e766b79f682bb1078f8`, against `81840f2c0`. Handoff citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff`.

## Blocking findings

**High: a restarted source can replay the takeover without its launcher (AC-43 replay, AC-44 result delivery).** `HandoffTransferRunner.ts:848-862` persists `sent` with the checkpoint sequence, then saves the request containing the launcher in a second write. Stop the source between those writes, before any packet leaves. On restart, `HandoffTransferRunner.ts:577-592` re-registers the follow row, but reads the launcher's identity and reachable machines only from the absent second write. It sends the takeover without them. The destination starts a fresh continuation without a launcher (`HandoffReceiver.ts:906-926`).

For example, A can follow its worker to B, and B can reach C, but A cannot reach C. After that replay A still follows B. When B hands the idle continuation to C, `handoffFollow.ts:110-122` permits the move because the launcher is absent. A's follower stops without delivering the result. The terminal behavior is asserted in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/handoffFollower.test.ts:441-454`. This is a trace through the new replay path, not a local test run.

Persist the launcher, including the distinction between “no launcher” and “not recorded,” in the same transition as `sent`. Replay that value or recover it before dispatch. Test the cut immediately after `sent`: the replayed request must retain A, and B must refuse C before preparing or holding the thread.

## Follow-up (non-blocking)

None beyond the blocking replay case.

## What I verified

- Fetched the PR head and read the four-commit, six-file delta as Git objects. On an uninterrupted transfer, `HandoffTransferRunner.ts:697-705` checks the onward refusal before preparation or hold; `HandoffTransferRunner.ts:837-865` registers the follow and sends the named launcher. The existing assertions at `handoffOnward.test.ts:94-115,120-145` cover refusal before a checkpoint and one result on the normal path, not the cut between writes.
- Confirmed both red assertions in the raw log of job `135627234536`, run `44543325893`, commit `c3311a13a1b7d36885eb8a097fde56dae5936ed2`. The launched-thread case failed with `AssertionError: expected 'active' to be 'fenced' // Object.is equality`. The unreadable-thread case failed with `AssertionError: expected { holderEnvironmentId: 'env-a', …(5) } to match object { state: 'handing-off', epoch: 1 }`.
- On the requested head, all three server shards and typecheck were still running at inspection. No local checkout, build, install or test run; no PR comment or commit.
