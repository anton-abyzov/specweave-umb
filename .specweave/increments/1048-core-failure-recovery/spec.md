# 1048 Recover stranded subagents, failed starts and stalled queues

## Problem

Three user reports on October 24, 2026 share one cause: when a turn ends abnormally, orchestration leaves state that nothing ever settles, and the UI offers controls that cannot work.

1. **Stranded subagents.** After a parent thread stops on a token or usage limit or a provider failure, its subagents look hung. Screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-cb54cdff-def3-4f4a-89c2-fd56d95d05cf.png`: 1031 "Simplify settings across machines" has every run completed (the last at 05:04 UTC), yet 11 native subagents have reported `running` since 02:53-03:02 UTC. Research: `/tmp/core-recovery/research-subagents.md` (copied to `reports/`).
   - A native subagent row, its parent turn item and the child's runless root turn close only on a provider task event or on an in-fiber cascade for a failed, interrupted or cancelled run. Anything else waits for the next server start (`ProviderRuntimeRecoveryService`): a subagent launched by an earlier run, a background subagent whose parent turn completed before the process died, or a run settled outside its fiber.
   - The Claude adapter already knows these entries are dead (`subagentsFromEarlierProcesses`, `ClaudeAdapterV2.ts:3122-3125`) but never says so.
   - The parent is never told which subagents died, so a resumed parent neither reruns nor completes them.
   - A parent Stop sends delegated children a cause-less `thread.stop`, and the child's own limit resume stays armed (1013 follow-up).
   - The header chip prefers the parent's stale record over the child's own terminal run (`threadSubagents.ts:179`).
2. **Failed starts with no way forward.** Runs 29-32 of the completion-sweep thread and runs 6-8 of 1041 (`mcp:af724514-…`). Root cause: `/tmp/core-recovery/research-start-failures.md`.
   - The disk filled at 05:08:56 UTC, SQLite returned `SQLITE(14)`, and ingestion failed run 29 as class `unknown` ("sent no details") without interrupting the Claude turn. That turn ran unseen until 05:24:48.
   - Every new start hit `Claude provider turn … is still active.` and showed the generic "could not start this turn".
   - Failed starts left handoff markers `pending`. Run 33 then replaced the native session, killing the wake that carried the "Fresh review of 1047 patch" verdict. Its continuation marked five handoffs delivered without sending them, so run 34 started with no history.
   - The composer offers no Retry for failed runs, and nothing reads `retryable`.
3. **Queue controls that do nothing.** Screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-40b29ee1-fa43-4e94-bdd9-8585a6b98be8.png`: "Working for 2h 28m", "No new events for 2h 28m", 13 queued messages from other threads, each with Edit, Steer now and X. Research: `/tmp/core-recovery/research-queue.md`.
   - Steer now, X, drag and Discard ignore their result, so a refusal only reaches `console.warn`.
   - Steer now is disabled under the same condition that queued the rows (no running provider turn), with no explanation.
   - The queue cannot drain while any run blocks it, and no watchdog ends a live but silent run or a run stuck in `waiting`.
   - Every queued delivery bumps `thread.updatedAt`, which resets the watchdog, orphan and stall clocks.
   - Promote-to-steer cancels the queued row before the provider acknowledges the steer.
   - Stop on a hung live session waits on the provider with no deadline.

## Scope

In: server orchestration-v2 recovery paths (subagent settlement, Claude adapter process boundaries, ingestion and start failure handling, handoff markers, stall watchdog, queue commands), the parent continuation note, web queue drawer feedback and explanations, the subagent chip status, the composer Continue action for failed runs, tests, and headless fixture proof.

Out:
- 1031 settings feature files and its reviews: coordinate with its owner and start no duplicate review.
- 1047 account-change resume: separate increment, same owner. This increment preserves its review findings.
- 529 retry backoff policy.
- Disk cleanup: the hourly disk owner keeps it.
- New interrupt cause literals: older fleet peers decode `cause` as a closed set.
- Merge, release and service restart: the sole integration and release owner.
- EasyChamp product work.

## Acceptance Criteria

- [x] AC-01: Dead native subagents settle from evidence. When a Claude query process opens, every subagent from an earlier process becomes terminal in that run: its parent row, its parent turn item, the child's runless root turn and the child's open items. A periodic sweep settles open native subagent state on a thread that has no blocking run and no live provider process for that provider thread, after two consecutive sweeps. A subagent whose process is alive, or whose completion is buffered, is never touched. Evidence: review.md (sweep two-verdict, liveness gate), review-r2.md F-11 accepted (unknown liveness counts as live), R2-02 and review-r4.md R3-03 fixed; SubagentSettlement/StrandedSubagents tests in #678 CI 40117544633.
- [x] AC-02: Cause is kept. A subagent ended by a person's Stop settles `cancelled` with "Stopped by you". One ended by a limit, provider error or process exit settles `interrupted`, naming the cause (for example "Stopped when Claude's usage limit ended the parent's session"). A parent Stop sends its delegated children a stop that disarms their automatic limit resume. A parent outage leaves the children's own recovery armed. No new cause literal. Evidence: review.md F-01 fixed in r2-fixes.md (system vs person Stop intent, no cause literal), R2-02 fixed and retained in review-r4.md.
- [x] AC-03: The parent can recover the work. The parent's next provider turn is told once which subagents an outage interrupted, with their titles, so it can rerun or finish them. This includes an automatic limit resume, a provider retry and a Continue. Subagents a person stopped are listed as stopped, not to rerun. A child whose final answer was recorded before its process died settles `completed` with that answer and is not re-run. Repeated sweeps or restarts produce no duplicate notes and no duplicate executions. Evidence: review-r2.md R2-04 and F-07 (completed answer kept), review-r4.md R3-01 fixed (note in next prompt, four-turn no-duplicate regression).
- [x] AC-04: The UI tells the truth. The subagents chip, the composer "N subagents" strip and the timeline group show a child's terminal run, or its settled row, over a stale parent record. After AC-01 settles them, the strip leaves "working". Evidence: T-03 threadSubagents.test.ts; headless-r2/strip-settled-* and strip-stopped-* captures, headless-r2/checks.json.
- [x] AC-05: Ingestion storage failures stop the provider turn. When provider events cannot be stored, the run interrupts its provider turn before failing, so no native turn keeps running unobserved. The failure is classified as a local storage failure, with its own message naming disk space or the database instead of "the provider … sent no details". Evidence: review.md "What holds up" (RunExecutionService interrupts before failed terminal), lane-f-receipt.md `local_storage` code and message; StartFailureRecovery.test.ts.
- [x] AC-06: A start that finds the previous native turn still active does not fail with the generic message. When no run owns that turn, the start interrupts it, waits a bounded time and then starts. When the turn belongs to a live run, the run queues behind it. If the start still cannot proceed, the failure names "the previous turn is still running" with a stable code. Evidence: review-r2.md R2-03 fixed (requeue behind live owner), review-r4.md R3-02 fixed (owner-ends-before-requeue race), lane-f-receipt.md `previous_turn_active`.
- [x] AC-07: Handoff delivery is truthful. A start that fails before the prompt is offered rolls its `pending` handoff markers back. A continuation turn that sends no prompt text marks no handoff delivered. A run following failed starts therefore resumes the same native session with its history. Evidence: review.md "What holds up" (rollback before prompt, promptless continuation marks nothing); StartFailureRecovery.test.ts.
- [x] AC-08: Failed runs offer a way forward. A run that failed with class `provider_error`, `unknown` or local storage shows Continue in the composer. Continue resumes in the same native session with "Continue where you left off." (never resending the brief) and releases the failure hold on the queue. The error banner's "Retry the turn" text matches an actual action. Evidence: T-05 ThreadErrorBanner.test.tsx (Continue on a failed run, hold release); headless-r2/failure-* captures; r4-failure-hold-green.log 12/12 (a run behind a failed owner stays held).
- [x] AC-09: Queue controls report outcomes. Steer now, X, drag and Discard show the server's exact refusal next to the drawer. They are disabled, with a reason, when the viewer cannot operate the thread or the machine is disconnected. Promote-to-steer keeps the queued row until the provider accepts the steer and restores it when the steer fails, so nothing is dropped or delivered twice. Evidence: review-r2.md R2-01 and F-03/F-05 fixed, retained in review-r4.md; headless-r2/refusal-* and disconnected-*; contrast fix df528f6c3e green in CI 40117544633.
- [x] AC-10: The queue explains itself. The drawer says who queued each row (sender thread, or you) and why it waits: the turn is busy and not steerable, held after Stop, held after a failure, or held behind a usage limit. A disabled Steer now names the reason. Automatic deliveries waiting in the queue are visible as read-only rows ("delivers after this turn"), and their relative order is preserved. Evidence: headless-r2/checks.json not-steerable (named disabled reason), stopped, failure and usage-limit cases, busy rows; QueuedRunsControl.dom.test.
- [x] AC-11: Stalled live runs end. Quiet time is measured from the run's provider activity, not `thread.updatedAt`, in the watchdog, the orphan check and the client stall chip. A running run with no provider event for 45 minutes, no open tool, subagent, request or thread wait, and a live session is interrupted with a system reason, so delivery and continuation rules apply and the queue drains. A run stuck in `waiting` past its checkpoint deadline is settled. Stop on a hung live session settles locally after a 30-second interrupt deadline. Evidence: review.md (activity clocks, live_silent 45 min on second sweep, 30 s Stop deadline), review-r2.md F-02 fixed and F-09 accepted; lane-q-receipt.md negative control.
- [x] AC-12: Recovery is proven by fault and restart tests:
  - parent limit failure with background native subagents from the same run and from an earlier run;
  - the process exiting after a completed parent turn;
  - a new process opening with earlier-process subagents;
  - nested delegated, then native, children;
  - Stop versus outage cause;
  - the sweep run twice (no duplicates);
  - an ingestion storage failure;
  - a still-active start;
  - handoff rollback;
  - queue command refusals;
  - a live-silent stall.

  A headless fixture (headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, reports open never) records the drawer and subagent strip states at 390 and 1280 px in light and dark to `/Users/antonabyzov/.specwithcode/m4/evidence/core-failure-recovery-1048/`. Evidence: review-r2.md F-04 fixed (CoreFailureRecovery.integration.test.ts, 10 tests), headless-r2/checks.json 48/48 headless (28 drawer, 20 strip); review-r4.md SHIP; #678 stage 2 server shards 5,916 and 5,395 tests, 0 failed.

## Approach

Base: specwithcode-dev `origin/main` `2e95e09ae`, in scratch worktree `/tmp/core-recovery/tree`. Lanes are worked in their own scratch worktrees and combined on branch `fix/core-failure-recovery-1048`. Delivery goes to the bound integration owner, with no merge, release or restart from this lane.

1. **Subagent settlement (AC-01 to AC-04).** Extract the child-aware cleanup in `ProviderRuntimeRecoveryService.ts:450-600` into a shared `SubagentSettlement.ts` helper that takes a cause and a status. Call it from three places:
   - the Claude adapter's `openQuery`, for `subagentsFromEarlierProcesses`, emitted inside the new run;
   - `RunExecutionService.writeFinalRunEvents`, extended to inherited background items;
   - a new sweep in `StaleRunWatchdog`, gated on two consecutive verdicts and on no live adapter process (`liveProcessRunsBackgroundWork`, exposed through an optional adapter method).

   Each settlement appends the interrupted work to the latest started run's `restartCancelledBackgroundWork`, which `RestartBackgroundNote` delivers to the next provider turn, so no new note mechanism is needed. A person's Stop marks work "stopped". `stopDelegatedTasks` disarms limit resume on children. Chip status falls back to the child's terminal run.
2. **Start failures (AC-05 to AC-08).**
   - The ingestion-failure path calls `interruptTurn` (as `OrphanedRuns.ts:360-385` does).
   - `ProviderFailure.causeMessage` maps `PersistenceSqlError`/`ENOSPC` to class `local_storage`, and the "still active" `ProviderAdapterProtocolError` to `previous_turn_active`.
   - `ProviderTurnStartService` handles the still-active case.
   - `ContextHandoffDelivery` rolls markers back on a failed start and skips marking on a continuation.
   - Web `resumableRunId` covers failed runs, and `ThreadErrorBanner` gets Continue.
3. **Queue (AC-09 to AC-11).**
   - `QueuedRunsControl` reads each command's result and shows the error.
   - Row actions are gated on `canOperateThread` and connection state.
   - Drawer rows carry the reason.
   - `dispatchQueuedMessagePromoteToSteer` cancels only after the steer effect is accepted.
   - Quiet time uses run activity.
   - `orphanedRunKind` gets a live-silent cutoff.
   - `waiting` runs get a checkpoint deadline.
   - `ProviderTurnControlService.interrupt` gets a deadline, then settles locally.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Native subagents cannot be restarted individually, because they live inside the provider process. The remedy is to settle them truthfully and tell the parent, which reruns or finishes them in its next turn. Delegated children keep their own run-based recovery.
- D-02 A person's Stop is final for every descendant, and an outage never is. No cause literal is added. Stop intent is carried by the existing `user` cause and the delegated stop path.
- D-03 Live-silent cutoff: 45 minutes of no provider event, with nothing open. Interrupt deadline: 30 seconds. Both are conservative constants beside the existing watchdog ones.
- D-04 Code is written in scratch worktrees from `origin/main` and delivered through the bound integration owner, as 1047 did. This lane does no merge, release or restart.
- D-05 The live 1031 subagents are not edited by hand. The settings owner is told they are dead, and AC-01 settles them once installed.
### Open
- none

## Tasks

### T-01 Shared subagent settlement and adapter process boundary
- AC: AC-01, AC-02 | Files: apps/server/src/orchestration-v2/SubagentSettlement.ts, apps/server/src/orchestration-v2/ProviderRuntimeRecoveryService.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, apps/server/src/orchestration-v2/RunExecutionService.ts, apps/server/src/orchestration-v2/ThreadManagementService.ts, apps/server/src/orchestration-v2/Orchestrator.ts | Test: vitest run apps/server/src/orchestration-v2/SubagentSettlement.test.ts apps/server/src/orchestration-v2/ProviderRuntimeRecoveryService

### T-02 Stranded-subagent sweep and parent continuation note
- AC: AC-01, AC-03 | Files: apps/server/src/orchestration-v2/StaleRunWatchdog.ts, apps/server/src/orchestration-v2/RestartBackgroundNote.ts, apps/server/src/orchestration-v2/ProviderAdapter.ts | Test: vitest run apps/server/src/orchestration-v2/StrandedSubagents.test.ts

### T-03 Subagent status in the web
- AC: AC-04 | Files: apps/web/src/studio/threadSubagents.ts, packages/shared/src/orchestrationV2PendingBackgroundWork.ts | Test: vitest run apps/web/src/studio/threadSubagents.test.ts

### T-04 Ingestion storage failure, still-active start and handoff markers
- AC: AC-05, AC-06, AC-07 | Files: apps/server/src/orchestration-v2/RunExecutionService.ts, apps/server/src/orchestration-v2/ProviderFailure.ts, apps/server/src/orchestration-v2/ProviderTurnStartService.ts, apps/server/src/orchestration-v2/ContextHandoffDelivery.ts, packages/shared/src/orchestrationV2ThreadError.ts | Test: vitest run apps/server/src/orchestration-v2/StartFailureRecovery.test.ts

### T-05 Continue for failed runs
- AC: AC-08 | Files: apps/web/src/components/ChatView.tsx, apps/web/src/components/chat/ThreadErrorBanner.tsx | Test: vitest run apps/web/src/components/chat/ThreadErrorBanner.test.tsx

### T-06 Queue command outcomes, reasons and safe promote
- AC: AC-09, AC-10 | Files: apps/web/src/components/chat/QueuedRunsControl.tsx, packages/client-runtime/src/state/threadWorkflows.ts, apps/server/src/orchestration-v2/Orchestrator.ts | Test: vitest run apps/web/src/components/chat/QueuedRunsControl.test.tsx packages/client-runtime/src/state/threadWorkflows.test.ts

### T-07 Stalled live runs, waiting deadline and Stop deadline
- AC: AC-11 | Files: apps/server/src/orchestration-v2/StaleRunWatchdog.ts, apps/server/src/orchestration-v2/OrphanedRuns.ts, apps/server/src/orchestration-v2/ProviderTurnControlService.ts, apps/server/src/orchestration-v2/EffectWorker.ts, packages/client-runtime/src/state/models.ts | Test: vitest run apps/server/src/orchestration-v2/StaleRunWatchdog.test.ts apps/server/src/orchestration-v2/OrphanedRuns.test.ts

### T-08 Fault and restart suite plus headless fixture
- AC: AC-12 | Files: apps/server/src/orchestration-v2/CoreFailureRecovery.integration.test.ts, apps/web/tests/core-recovery/ | Test: node apps/web/tests/core-recovery/verify.mjs

### T-09 Fresh review and routed delivery
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12 | Files: .specweave/increments/1048-core-failure-recovery/reports/review.md | Test: test -s .specweave/increments/1048-core-failure-recovery/reports/review.md

### T-10 Verify and close 1048
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12 | Files: .specweave/increments/1048-core-failure-recovery/spec.md | Test: specweave verify 1048-core-failure-recovery

### T-11 Fix verified round-2 recovery findings
- AC: AC-01, AC-02, AC-03, AC-06, AC-09, AC-12 | Files: apps/server/src/orchestration-v2/ | Test: npx vp test run apps/server/src/orchestration-v2

### T-12 Preserve folder policy during recovery preparation
- AC: AC-03, AC-12 | Files: apps/server/src/project/ProjectEnvironmentRuntime.ts, apps/server/src/project/ProjectEnvironmentRuntime.test.ts | Test: npx vp test run apps/server/src/project/ProjectEnvironmentRuntime.test.ts
