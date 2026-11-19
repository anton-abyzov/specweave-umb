FIX FIRST
Verdict: fix first

Reviewed `anton-abyzov/specwithcode#702`, increment 1390, T-10, at `b8f2bda15ee37f046525ff062b5c9d47bf4a1a63`. The plan can select a target on the wrong track or a known depleted account, mark unmeasured work movable, and restart a settled thread whose unsaved files were selected to move.

| AC | Change | Test at the reviewed head | Red before fix |
|---|---|---|---|
| AC-17 | Groups, ticks and reasons to stay | Manual grouping, pending actions, broken folders, no coordinator or routine | Yes: empty plan instead of grouped rows |
| AC-19 | Unsaved idle and finished threads are selected | Settled/completed, waiting/stopped and waiting/failed map to Ready | Yes: null instead of an unsaved row. Settled after a limit stop is missing. |
| AC-20 | Manual project-folder row counts files and source-only branches | Folder work ticked by hand and excluded automatically | Yes: null instead of a folder-work row. Applying files is T-11. |
| AC-22 | Account wording and manual versus automatic eligibility | Shared, different, stale and unknown readings | Yes: evidence assertions in the shared rule and planner |
| AC-34 | Measures a negotiated Git bundle; over-limit work stays | Scratch-ref lifetime, file/count/bundle limits and growth wording | Yes: wrong sizes, missing ref and resolve instead of reject. No unknown-measure gate. |
| AC-38 | Receiver checks link, grant, track, sign-in and usage before replication | Shared-pool fallback, empty track, stale reading, copy-free receiver | Yes for policy assertions; the receiver integration case errored before its assertions. |
| AC-41 | Per-thread Resume, Ready or Stays for manual and automatic starts | Limit stop, ten-minute boundary, threshold off, healthy sibling and repeat window | Yes: null instead of expected dispositions. Some exclusion tests already passed against the stub. |
| EC2-04 / EC2-09 | Distinct `handoff.plan` capability and `check` route | Pinned `v1.0.383` request bodies in both directions; missing route and simulated `handoff.v2`-only peers | Capability and target-answer assertions failed. The source-refusal integration case errored before its assertions. |

## Blocking findings

1. **High · AC-38: A tracked thread qualifies on a target with no matching track.** `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffReceiver.ts:624` passes `null` when the linked target project uses a fixed model. `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:202` then tries the source model, even though the request names Daily. With that model installed, an allowed account and fresh usage at 15%, the result was `failures: []`, `automatic: true`. Only an untracked source thread should take this fallback. The off-track test supplies `[]`, not the `null` the receiver actually sends.

2. **High · AC-38: The source can change a Daily thread into a Complex thread.** `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:783` infers the track from the model slug, with Complex always first. A Daily task using a model listed on both tracks is reported as Complex. A receiver with room only on Complex can then confirm the move. Carry the actual routing decision; if it is unavailable and membership is ambiguous, do not authorize an automatic move.

3. **High · AC-22, AC-38: A pool the source already exhausted can be called a different account.** `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/packages/shared/src/machineFallback.ts:287` checks the depleted fingerprint list only when the target driver matches the thread's last driver. Suppose a track exhausted accounts A and B on different providers and stopped on A. The target offers B with a recent low reading taken before exhaustion. With B in `sourceFingerprints`, the function still reported `different-account` and `automatic: true`. Fingerprints already include the provider driver in their hash. Honor an exact match anywhere in the depleted list, then try the next eligible account.

4. **High · AC-19, AC-41: Moving a settled thread's files can restart its turn.** `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:681` derives Resume from the last run ending after the unsaved-work exception admits a settled thread. For a manually selected settled thread with `unsaved: true` and `runEnding: "usage-limit"`, the actual row was `group: "unsaved"`, `ticked: true`, `disposition: "resume"`. The owner selected files from a finished thread, not another turn. Return Ready on this path and retain Resume for a thread actually being continued after its limit stop.

5. **High · AC-17, AC-34: An unmeasured item is ticked and movable.** `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:658` checks limits only for non-null measurements; the folder-work path does the same at line 720. A thread with an 11 MB changed file, a successful target check and `measure: null` gets a selectable row with no size instead of waiting for measurement. Rechecking at execution cannot correct what the selection screen already promised. Require a completed measure for rows that carry repository data, or model the pending state explicitly and disable selection.

## Follow-up (non-blocking)

- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:449`: A duplicate measurement of the same operation/thread can lose the exclusive ref race and then delete the winner's ref in `finally`. Delete only a ref this invocation acquired, using the expected commit as the deletion guard. The current cleanup test covers a failure *after* acquisition.
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:437`: The skipped-file list is capped at 200, so 20,500 ordinary changed files can be reported as 20,200. Line 442 likewise reports the limit plus one byte for an oversized historical blob, rather than its size. Both still refuse the item; use an uncapped counter and the actual blob size for the explanation.
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.test.ts:943`: The old-target case constructs `unknownCheckPath` directly. Removing the peer client's HTTP 404 mapping would leave it green. Drive a fixture 404 through the peer client and assert the resulting row.

## What I verified

- Read T-10, its Files and Test, all seven ACs and the November 19 amendments. Reviewed only `13badcb7944321e740765e766b79f682bb1078f8..b8f2bda15ee37f046525ff062b5c9d47bf4a1a63`: four commits, 17 changed files. `git diff --check` passed.
- Compared `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t10/red.log` with the tests and stubs in `93f7b7a34`. All four test files collected. **38 failures were assertion failures, two were `TypeError`s at the receiver call before an assertion, and 51 tests passed.** The log establishes genuine pre-fix red coverage, not the claim that all 40 failed on their own assertions.
- Executed the reviewed policy functions in memory from Git objects. Confirmed the null-track result, ambiguous source track, depleted-fingerprint misclassification and settled-thread Resume. Traced the missing-measure branch and both capability checks at the pinned head. The pinned release fixture covers both wire directions; the transfer-record-only peer is simulated.
- No checkout, build, install, full suite, PR comment or source edit. No final-head suite result is claimed. The known stack conflict and missing CI are not findings.
