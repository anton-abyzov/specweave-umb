SHIP
Verdict: ship

| Item | Disposition | Evidence at the reviewed head |
|---|---|---|
| Round 3: restart drops the launcher (AC-43, AC-44) | Fixed | `HandoffTransferRunner.ts:875-897` writes the launcher, including its reachable machines, in the same `held` → `sent` transition as the checkpoint sequence. Replay uses that value at `599-621`; it does not depend on the later `pendingTakeover` write. Explicit `null` means nobody waits; only an absent field invokes compatibility recovery. |
| T-24: reviewer lock (AC-40) | Preserved | The same transition records the review marker. Both first send and replay use it (`HandoffTransferRunner.ts:272-275,303-311`). The receiver refuses a marked but unlocked takeover before applying a checkpoint or making a worktree, then checks again before selecting the launch model and routing (`HandoffReceiver.ts:756-761,788-805,833-843,983-1002`). |
| T-19: onward refusal (AC-44) | Preserved | `HandoffTransferRunner.ts:725-734` refuses an unreachable onward destination before preparation. The transfer record and lease hold come later, at `782-805`. |
| Replay identity and execution fence (AC-42, AC-43) | Preserved on the changed path | Replay addresses the recorded destination and operation. An existing launch returns its receipt; a new launch requires a persisted acceptance (`HandoffReceiver.ts:680-689,916-951,979-984`). |

## Blocking findings

None.

## Follow-up (non-blocking)

Strengthen the regression test for the *first* machine with a waiting launcher. `HandoffTransferRunner.test.ts:169-187` seeds B with A's launcher, loses the request, then removes `pendingTakeover` from an `unknown` transfer. B's separate thread record still names A, so the compatibility fallback at `HandoffTransferRunner.ts:603-611` could mask a future regression in the atomic write. A test that restarts directly from `sent`, with the waiting thread local and no launcher on the separate record, would distinguish the two repairs. The production transition itself contains the launcher.

## What I verified

- Reviewed `anton-abyzov/specwithcode#692` at `01149d99bde1241955f718cdf149f241f603960b`, from rebased round 3 baseline `a0d4c8fcc`, using fetched Git objects only. Handoff citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff`.
- Traced the three-machine assertions at `HandoffTransferRunner.test.ts:189-208`: same operation and launcher on replay, launcher retained on C, no peer call, hold or transfer on the declined onward move. Checked the review-only peer route at `handoffPeers.ts:642-645` and both receiver lock checks above.
- GitHub listed no run for rebased test-only commit `839adee2f`. The pre-rebase test-only commit `9fb2745fc` has the identical stable patch ID, `b1095a0fc7d337c0f26a62dffaaecc2dc34c5a56`. Its [CI run](https://github.com/anton-abyzov/specwithcode/actions/runs/44548131987) still had all three server shards running at inspection; the expected red assertion was not yet verified.
- [Reviewed-head checks](https://github.com/anton-abyzov/specwithcode/actions/runs/44548658715) were in progress. Typecheck passed; all three server shards were running. This verdict covers the delta, not the outstanding CI gate. No local checkout, build, install or suite run; no PR comment or commit.
