FIX FIRST
Verdict: fix first

**Reviewed:** `anton-abyzov/specwithcode#681`, commit `9ab5a0042218d06ecd75a3130e7011a0762a46ec`, against base `dec99407cd2befd34377e341659547d845b01451`. T-19, AC-44, and the November 19, 2026 amendments EC2-01 and EC2-09. Eight changed files; 10 findings: 0 critical, 6 high, 2 medium, 2 low.

The ordinary one-hop path has a stable continuation ID and a stable wake command ID for a given row and run. It queues the wake before recording it as sent, and the orchestrator consults its command receipt on replay. That protects a repeat of the **same** wake. It does not protect a result that was never registered, a follower that stops early, or a different run selected after reconnect.

### T19-01 [high] A second handoff breaks the route back to the original launcher

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffFollow.ts:114-128,150-156`

Move a running worker from A to B, then from B to C before it finishes. B's continuation was created as `system`/`server` (`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffReceiver.ts:775-795`). The second registration requires `agent`/`mcp`, finds no launcher, and writes no row. A sees B's interrupted run and waits for another run **on B**; it never learns that C finished. A's lease heartbeat also skips an already-forwarded thread. Fix: retain the original result destination independently of execution ownership. Follow or relay a durable onward receipt under the same logical delivery identity. Test A to B to C with A offline and exactly one wake on A after reconnect.

### T19-02 [high] Reconnecting can skip a completed result permanently

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkerFollower.ts:184-191,632-659,679-687`

A goes offline before observing the first run. On B, the handed-off job completes and a second message is queued. On reconnect the selector picks the queued message over the completed job. Cancel that message after the follower pins it: `passedRunId` advances to the second run, excluding the completed first run forever. I ran the exact selector from this commit in memory: `[job: completed, followup: queued]` selected `followup`; after cancellation, passing `followup` returned `undefined`. The 20-run read limit can also hide an earlier completion entirely. Fix: preserve the first outstanding result in run order, distinguish its fallback from unrelated later messages, and recover beyond a single recent-runs page. Add this cancellation sequence to the reconnect test.

### T19-03 [high] The launcher's own wait can acknowledge an interruption as final

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/remote.ts:359-367`; `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkers.ts:1336-1363`

The follower has pinned run R. The launcher waits on R and gets `interrupted` before the follower processes the same transition. `waitRemote` calls `noteFinished`, which changes the matching row to `idle` and puts R in `deliveredRunIds`. The follower exits on an idle row; startup does not restart that follow. A later successful continuation run on B produces no wake. Fix: make manual observation use the same handoff state transition as the follower. An interruption, cancellation, or rollback is not an acknowledgement of the worker's result. Exercise the public wait before allowing the follower to process the stop.

### T19-04 [high] A takeover can succeed without its required durable follow row

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffFollow.ts:128-140,205-220`; `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.ts:552-570,872-874`

If the remote-worker file cannot be written at registration and confirmation, both errors are logged and swallowed. The takeover is still sent, its receipt fences the source, and the source clears `pendingTakeover`. After storage recovers, there is no row for startup to resume; the normal heartbeat skips records with `continuedOn` set (line 1285). The worker can finish without ever notifying its launcher. A failed launcher lookup is likewise treated as “no launcher.” Fix: distinguish an ineligible thread from a failed lookup or write. For an eligible worker, require durable registration before sending, or persist a repair obligation before accepting the transfer as complete.

### T19-05 [high] Restart can send a second completion for unrelated work

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkerFollower.ts:447-461,793-806,1014-1019`

Let R1 fail and notify its launcher. Later someone sends an unrelated message directly on B; R2 completes. If A restarts within the two-day failed-run recheck window, `recheckFailed` reopens the delivered row for R2 solely because the latest run ID differs. The launcher gets a second completion, under a different command ID, for work it did not send. Same-command deduplication cannot suppress it. Fix: close a handoff's delivery obligation once acknowledged. Follow a replacement only with evidence it is a fallback for the outstanding run; do not reopen delivered handoffs for an arbitrary later run.

### T19-06 [high] Neither compatibility direction is pinned to a release

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffFollow.test.ts:87-131,239-242,443-446`

The receiver comes from the current tree. Its read and wait tools are handwritten; no previous sender is exercised. The fake returns every recent run regardless of `runLimit`, and returns idle for an explicitly requested nonexistent run. The published `v1.0.380` (`2bd4cef142db11b50cb52a529f421241630a7dd4`) caps the run list and reports `run_not_found` in the latter case. Thus this fixture can pass recovery paths that a released peer cannot take. Fix: pin the release tag and commit, and exercise both directions with its handlers or fixtures checked against them. Require zero premature wakes and one real wake from new source to old target. For old source to new target, check the accepted **no-regression** baseline: upgrading only the receiver does not repair the old sender's missing follow row. Do not count that direction as a successful proof 5.

### T19-07 [medium] The launcher's project shows “Working” when no run exists

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkerFollower.ts:632-644`; `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/web/src/studio/remoteWorkerCards.ts:27-33`

When a continuation arrives idle, the persisted row is `following` with `lastStatus: "idle"`. The server does not expose the handoff's `awaiting` field in the card projection. The reachable card therefore says “Working” indefinitely, even though no message has started a run. Fix: expose and render “Waiting for handoff” or “Waiting for first run,” reserving “Working” for an observed run. Keep both waiting states nonterminal and silent.

### T19-08 [medium] The replay test counts call IDs, not persisted launcher messages

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffFollow.test.ts:427-435,490-507`; `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/remoteWorkers.testkit.ts:175-185,269-277`

The “restart” invokes `resume` on the same follower. The send mock appends every call, even duplicates, and does not record the destination thread. Two attempted sends to a wrong destination, or two persisted messages with the same submitted ID, would still pass its set-size assertion. The negative checks wait for an in-memory poll count using 10 ms sleeps, not persisted transitions; a delayed runner can hit the fixed retry ceiling. Fix: restart the relevant service scopes over preserved fixture storage, drive the target restart as well as the source restart, and drain `OrchestrationEffectWorkerV2` or await persisted events. Assert zero early notifications and exactly one message on the original launcher after duplicate delivery and the send-before-bookkeeping crash window.

### T19-09 [low] The touched moves module exceeds the requested line limit

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.ts:1569-1576`

The file was already 1,563 lines at the PR base and is 1,576 at this head; all seven other changed files are under 1,500. T-19 anticipated call sites in this oversized file, but the explicit size check still fails. Fix: rebase onto the corresponding extraction if available, or extract a cohesive helper and verify the resulting file is under 1,500 lines.

### T19-10 [low] New tests copy machine-specific fixture names into the public diff

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffFollow.test.ts:67-69,314-316`; `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkerFollower.test.ts:503-504`

The additions repeat `env-m4`, `env-m1`, and `m1` from the shared test world instead of naming machines by role. These are fixture literals, not credentials; no personal absolute path was added. Fix: parameterize the shared fixture with neutral `source` and `target` IDs so the new tests do not depend on these names.

**Verification evidence:** The [PR gate](https://github.com/anton-abyzov/specwithcode/actions/runs/44491232113) passed at the exact reviewed SHA. The two-machine proof in the increment is the original failure, not a passing rerun. No local red-then-green result was available: `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t19/gate-1.log` ended before the command ran, and `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t19/gate-2.log` was waiting for the gate. No install, build, or edit to the reviewed checkout was performed.
