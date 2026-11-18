# Needs you only for decisions only the person can make

## Problem

On November 18, 2026 the m4 Threads pane listed four rows under Needs you, and the owner could not tell which of them really waited on them ("it shows as kind of blocked still, even though it should not be"). The diagnosis (`reports/diagnosis.md`) found four different signals behind them:

- **Integrations settings:** a real `ask_user` card for the owner, labelled only "Answer needed".
- **Rethink copies, sync and handing off work:** an acceptance gate written in the last report's `**Blockers:**` paragraph, labelled "Blocked".
- **Onboarding rethink:** the same kind of report blocker ("Blocked · 3 subagents"), plus a Files-scope question from its own subagent that the lead can settle, plus two subagent records that read "interrupted" after a worktree move.
- **Skills: find, install, update everywhere:** "Answer needed · Review 1399 Lane B skill rep…", which came from a stale card on a grandchild reviewer whose run had ended and whose lead had already merged. Inside the thread, the subagent "Skills rollout…" showed "Stopped" because its first run paused to move into its own worktree.

Three code paths cause this:

1. `aggregateProjectAttention` (`packages/client-runtime/src/state/projectAttention.ts`) lifts every descendant's open question to the root row, including a question from a worker's own subagent that only the lead needs to answer, and a card left open after the asker and its lead moved on.
2. `threadStatusWord` (`apps/web/src/studio/shellModel.ts`) says "Blocked" for a report blocker, though the attention it raises is a "Reply needed" decision. No row says what the decision is.
3. A delegated child whose run is interrupted by its own `studio_worktree_handoff` is finalized at once (`finalizeAppOwnedSubagent`, `apps/server/src/orchestration-v2/Orchestrator.ts`): the parent's record becomes `interrupted`, the parent is woken, and its timeline shows a "Stopped" card, while the continuation is already starting in the worktree.

The SpecWeave ledger is not a source: no row status reads a blocked task.

## Scope

In: which signals put a row under Needs you; the row's words for a report blocker and an open card; the plain-words ask on each Needs you row; the worktree-move pause for delegated children; clearing the stale card found here.

Out: iOS and Android rows (they mirror `ThreadAttention` and keep today's behaviour; recorded as an open gap); answering any of the owner's real questions; an agent-readable list of a finished child's open cards in the parent's wake text (follow-up).

## Acceptance Criteria

- [ ] AC-01: A question card (`ask_user`, kind user_input) raised by a thread whose report goes to a parent agent (a worker's own subagent or a provider-native child) no longer puts the root row under Needs you while the asker or its lead is working: the root row is under Working and says "Waiting for subagents". Once the lead has completed a turn that started after the asker's last run ended, the card no longer counts in Needs you rows, counts or alerts. When the lead is gone or archived, its turn since then failed or was stopped, or it has not run since, nobody else will answer, so the card still puts the root under Needs you. A pending card still holds back a service update either way (`liveQuestionThreads.ts`): the update would close it.
- [ ] AC-02: Command approvals, sign-ins, held queues and plans from any descendant still put the root under Needs you, and a card on a coordinator's own worker (the 1402 shape) still reads "Answer needed".
- [ ] AC-03: A quiet worker whose last report has a non-empty `**Blockers:**` paragraph reads "Reply needed · <the ask>" instead of "Blocked", where the ask is the paragraph's first sentence in plain text (markdown, a leading "Still yours …:" style lead-in and links removed, capped with an ellipsis). The full paragraph stays in the hover.
- [ ] AC-04: A row whose own open card asks a question reads "Answer needed · <prompt>", where the prompt is the card's header and its option labels ("Release: Ship now or Wait for review"), or "N questions: <headers>" for a card with several questions, including a card a service update reopened (`update-reopen:`). The prompt comes from a new optional, capped `prompt` field on the thread shell's pending request summary, so an older server or client simply shows "Answer needed".
- [ ] AC-05: When a delegated child moves itself into a worktree with a continuation prompt, its parent's subagent record stays running: no "interrupted" receipt, no parent wake and no "Stopped" card. The child's next run's end delivers the result as usual. A move without a continuation prompt keeps today's behaviour, so the parent still hears the child stopped. A continuation that never runs (failed to queue, cancelled before it started, or lost to a restart) releases the result as "interrupted" once a 60-second wait ends, rechecked up to three times if that recheck fails, so the parent is never left waiting.
- [ ] AC-06: The subagent status reads a child whose activity started after its parent's terminal record as running, not Stopped, and keeps the record when nothing ran after it (`subagentExecutionStatus`, pinned by a test; the code already does this).
- [ ] AC-07: The stale Lane B reviewer card no longer counts anywhere, and the remaining real questions are listed for the owner, not answered. The card's own row stays pending until it is dismissed with the local CLI credential (a proof limit).

## Approach

1. Client attention (`projectAttention.ts`): split a pending person request by kind. For kind "answer" on a thread where `reportsToParentAgent` holds, look up the asker's parent shell in the index already built. Classify as `lead` (wait) or `settled` (drop) from the asker's runtime and `latestRun.completedAt` against the lead's `latestRun.startedAt` and runtime. `observeProjectThread` takes the verdict so the observation drops the request; `aggregateProjectAttention` adds "Waiting for subagents" to `root.waits` for `lead`. Rows, counts, chips and the "requests from subagents" expander all read these roots, so no second rule is needed.
2. Wording (`shellModel.ts`, new `packages/shared/src/attentionAsk.ts`): `blockerAsk(text)` makes the plain ask; `threadStatusWord` returns `Reply needed · <ask>` for a blocker and `Answer needed · <prompt>` for an own card with a prompt. "Reply needed" and "Answer needed" already exist in every locale file; the ask itself is the agent's own words.
3. Prompt (`packages/contracts/src/orchestrationV2.ts`, `apps/server/src/orchestration-v2/ProjectionStore.ts`, new `apps/server/src/orchestration-v2/pendingQuestionPrompt.ts`, `pendingQuestionPrompt` in `packages/shared/src/attentionAsk.ts`): optional `prompt` (at most 160 characters) on `OrchestrationV2PendingRuntimeRequestSummary`, for ask_user cards only. The SQL shell path reads the `user_input_request` turn item through `node_id` (indexed) and joins it only when its `requestId` is the pending request's; the projection path finds the same item in `projection.turnItems`.
4. Worktree move (`WorktreeMcpService.ts`, `Orchestrator.ts`): the handoff's `thread.metadata.update` carries a server-only `continuesInWorktree` when a continuation prompt is given; the interrupt it records then uses `WORKSPACE_MOVE_CONTINUES_MESSAGE`. `finalizeAppOwnedSubagent` holds the result while the result run's interrupt is that message, no later run exists, and less than `WORKSPACE_MOVE_CONTINUATION_WAIT_MS` (60 seconds) has passed; a held result is rechecked when the wait ends (again every 5 seconds, three tries in all, if the recheck fails), and server recovery rechecks after a restart. A queued continuation is itself a later run, so `delegatedTaskProgress` keeps the task working until it ends.
5. Client status (`models.ts` `subagentExecutionStatus`): unchanged; a test pins that a child whose activity started after the receipt reads running.

Rejected: classifying cards by their text (unreliable); a time-based expiry for stale cards (a card waits for its lead's next turn instead); queueing the continuation before the binding (a failed binding would then run the continuation in the old folder); an unbounded hold for the worktree move (a continuation that failed to queue would leave the parent waiting for ever).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: A worker's subagent's question is its lead's to settle while the lead can: the lead answers it or relays a real decision in its own report. With no lead working or due to run, it stays the person's. The owner's rule already applies this to report blockers ("a child's report that an agent reads is not a message to the person").
- D-02: Reuse "Reply needed", "Answer needed" and "Waiting for subagents" rather than adding row words, so no locale file changes.
### Open
- none

## Tasks

### T-01 Subagent questions wait on their lead
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectAttention.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectAttention.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx | Test: `node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/state/projectAttention.test.ts`

### T-02 Plain-words ask on Needs you rows
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/packages/shared/src/attentionAsk.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/attentionAsk.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/pendingQuestionPrompt.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionSettlement.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionStore.slowQueries.fixture.ts | Test: `node node_modules/vite-plus/bin/vp test run packages/shared/src/attentionAsk.test.ts apps/web/src/studio/shellModel.test.ts apps/server/src/orchestration-v2/ProjectionSettlement.test.ts`

### T-03 A worktree move is a pause, not a stop
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/WorktreeMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/DelegatedCompletionDelivery.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/subagentResume.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/WorktreeMcpService.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/SelectionRestart.integration.test.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/DelegatedCompletionDelivery.test.ts packages/client-runtime/src/state/subagentResume.test.ts`

### T-04 Clear the stale card and list the real questions
- AC: AC-07 | Files: .specweave/increments/1412-needs-you-only-for-decisions-only-the-person-can-make/reports/cards.md | Test: `specweave-studio db query "SELECT thread_id, archived_at FROM orchestration_v2_projection_threads WHERE thread_id LIKE '%1399-lane-b-review-1'"` shows the reviewer archived, so the card counts nowhere

### T-05 Review, merge, release and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1412-needs-you-only-for-decisions-only-the-person-can-make/reports/review-muse.md | Test: `specweave verify 1412-needs-you-only-for-decisions-only-the-person-can-make`
