# Quiet coordinator wake-ups for project workers

## Problem

On November 6, 2026 the user asked the coordinator once about PR #1430 and then got five coordinator replies in a row ("is still running", "No change: ...", "web build passed"). The worker `1209 skill authoring (app worktree)` was watching CI. Its runs 11 to 16 were self-wakes: a PR watch "checks failed" notice, a finished background command, a finished delegated review. `apps/server/src/project/LaunchedWorkerWake.ts:59` (`observeRun`) sends the launcher "Worker ... finished: completed" after every completed run of a top-level worker, so each intermediate turn woke the coordinator, and in Results only each wake-up's status-only reply was shown in full.

## Scope

In: the local launched-worker wake (`LaunchedWorkerWake`) only fires once the worker is really done, debounced; the web coordinator conversation in Results only folds a wake-triggered status-only reply into a one-line "Checked <worker>" row. Out: the delegated-task wake path, remote worker wakes (`fleet/remoteWorkerMatching.ts`), source-thread links on replies (increment 1244), mobile rendering.

## Acceptance Criteria

- [ ] AC-01: A completed or failed worker run wakes its launcher only when, after a settle window, that run is still the worker's latest run, no run is active or queued, and no PR watch, subagent, monitor or workflow still holds the worker's completion; a burst of runs produces one wake, from the last run.
- [ ] AC-02: A cancelled run never wakes the launcher, and a later run that reports nothing (cancelled, interrupted, or queued and held for a person) does not suppress the wake of the run before it. A worker held by a PR watch that ends without a run (the PR merged) still wakes the launcher.
- [ ] AC-03: In Results only, a coordinator reply to a worker wake that only reports status (still running, no change, waiting) renders as one collapsed line "Checked <worker>" that opens the reply on click; a wake turn with no reply shows nothing; replies to the user and substantive replies (failures, questions, merged, blocked) render unchanged; Folded steps and Everything render unchanged.
- [ ] AC-04: Regression tests replay the November 6 case: runs 11 to 15 completing in a burst with a PR watch active produce no wake; and the three status-only replies from the screenshot collapse in Results only.

## Approach

`LaunchedWorkerWake.observeRun`: sleep a settle window (`WAKE_SETTLE`, 45 seconds; failed runs keep their 90 second fallback grace), then re-read the worker shell. Skip when a later run reports for itself (completed, failed, active, or queued and not held for a person), when `activeRunId` is set, or when `threadHasQueuedTurnStart` is true. When `backgroundWorkHoldsCompletion(shell.pendingBackgroundTasks)` holds (PR watches surface there as monitors), re-check every 2 minutes, for at most 12 hours, because a merged PR ends its watch without another run. Accepted risk: the wait is in memory, so a server restart inside it drops that run's wake (failed runs already had this with their 90 second grace). The wake command id stays per run, so retries cannot duplicate. Rejected: a per-thread timer map, because re-reading the shell after the sleep already gives "the last run of a burst reports".

Web: `coordinatorActivity.ts` gains a pure `checkedWakeReplies` that pairs each wake message (filtered from view by `isWorkerCompletionWake`) with the last reply of the run it started, and classifies the run as status-only: its last reply has a "still running/no change/waiting" phrase, and no reply of the run has a question, "you", failure, block, merge, decision, limit or sign-in words, or attachments. Replies announcing a new thread stay whole, consecutive checked replies about the same worker thread merge into one line with a count, and nothing folds while Find is open. `CoordinatorConversation.tsx` renders those replies as a collapsed row in Results only. 1244 will add a `re:` source label to reply headers in the same file; this change keeps its edit to one branch in the message renderer so the two merge cleanly.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 settle window 45 seconds → long enough for a PR watch or task wake to start the next run (the observed gaps were 1 to 40 seconds), short enough to keep reports prompt.
- D-02 status-only detection is a text heuristic on wake-triggered replies only → it can miss some acknowledgements but never hides a reply the user asked for.
### Open
- none

## Tasks

### T-01 Wake the launcher only when the worker is done
- AC: AC-01, AC-02, AC-04 | Files: apps/server/src/project/LaunchedWorkerWake.ts, apps/server/src/project/LaunchedWorkerWake.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && npx vitest run src/project/LaunchedWorkerWake.test.ts

### T-02 Fold status-only wake replies in Results only
- AC: AC-03, AC-04 | Files: apps/web/src/studio/coordinatorActivity.ts, apps/web/src/studio/coordinatorActivity.test.ts, apps/web/src/components/studio/CoordinatorConversation.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && npx vitest run src/studio/coordinatorActivity.test.ts

### T-03 Verify and close 1245
- AC: AC-01, AC-02, AC-03, AC-04 | Files: reports/ | Test: specweave verify 1245
