# Model changes keep one thread

## Problem

On November 2, 2026, a user running a thread on Opus 5.5 picked Muse Wonder 1.0 in the composer and sent "switch to the cheapest model" while the turn ran. They expected the thread to carry on as one thread with a different model. They got a delegated child thread instead.

Evidence from the thread's stored state, with no fallback involved (no `limit-fallback:` message):

- The composer queued the message as run 2 on `muse/muse-wonder-1.0` at 21:16:12 UTC.
- Steer now promoted it at 21:16:21 (`inputIntent: promoted_queued_to_steer`). `dispatchQueuedMessagePromoteToSteer` passes `projection.thread.modelSelection`, so the row's Muse pick was dropped and the words went into the Opus turn. The thread never moved to Muse.
- Opus read the words as an order, and the only working route it had was `delegate_task`. `studio_thread_configure` on its own running thread releases the session the turn runs on, which is an agent's Stop of itself.
- The child's opening "Message from" looked garbled, but the brief stored was clean. `relayAttentionText` builds the folded view from sentences it takes for a request to the user. `/\?/` matched the `?` ternaries of a script in the brief, and bare imperatives ("Decide the structure", "confirm messages") matched a brief addressed to an agent. "Founders, Inc. confirm" also split at the abbreviation.

## Scope

In: Steer now on a row with another model; an agent's own in-thread switch; a timeline marker for same-provider switches; the folded relay view. Out: resuming a native session across providers (no provider supports it); a new wire event; transcript pointers for drivers other than Claude and Codex.

## Acceptance Criteria

- [x] AC-01: A folded message addressed to the receiving agent (from its parent, its coordinator or itself) shows no extracted text. Its body stays one click away and Copy keeps the original bytes.
- [x] AC-02: In any folded relay, code never counts as a request to the user: a `?` counts only at a sentence's end, and a code-like sentence or an abbreviation split ("Inc.") is never shown as one.
- [x] AC-03: Steer now on the user's queued row whose provider or model differs from the running turn stops that turn and runs the row next on its picked model, in the same thread, with the queue not held and the pick kept.
- [x] AC-04: A row differing only in options, an agent's row and an automatic delivery still steer as before.
- [x] AC-05: The queue row names the row's model when it differs and says "Run now" with a tooltip saying this turn stops, on web and mobile.
- [x] AC-06: `studio_thread_configure` with `continueWith` queues that text on the new model. Called by a thread on itself mid-turn, it leaves the turn running and the next turn runs on the new model in the same thread.
- [x] AC-07: A cross-provider `studio_thread_configure` by a thread on its own running turn without `continueWith` is refused with a message naming `continueWith`, instead of stopping the agent's own turn.
- [x] AC-08: The agent instructions and `delegate_task` description say a model change is not a delegation; a new thread only when the user asks for one.
- [x] AC-09: Same-provider model changes show the "Switched model" divider before the first message on the new model. A run cancelled before it started never counts, and cross-provider switches keep their one handoff row.
- [x] AC-10: A user pick or agent switch during a limit fallback clears the mark and is not undone at the limit reset; returning home still works when no pick intervened.

## Approach

**What crosses providers.** A native session cannot resume across providers. The next turn opens a fresh native session seeded with a handoff: retained messages up to `STUDIO_CONTEXT_HANDOFF_TOKEN_CAP` (default 16,000 tokens, byte cap 64,000) plus the transcript paths of the thread's Claude and Codex sessions, which the new agent reads with its own file tools when it needs more. When no history fits, it receives paths only (`POINTER_HANDOFF_FLOOR` 4,096 bytes). A same-provider change keeps the native session where the adapter's transition allows, so it costs no handoff. The handoff is plain text, so a provider without the `studio-code` tools still continues; it only lacks orchestration tools. Muse has had them since at least November 2, 2026 (`studio-code.chrome_*` calls in the incident's child).

Files: `apps/web/src/studio/workerMessagePresentation.ts`, `apps/web/src/components/studio/RelayedMessage.tsx`, `apps/web/src/components/chat/MessagesTimeline.tsx`, `apps/server/src/orchestration-v2/Orchestrator.ts`, `packages/client-runtime/src/state/threadWorkflows.ts`, `apps/web/src/components/chat/QueuedRunsControl.tsx`, `apps/mobile/src/features/threads/ThreadQueueControl.tsx`, `apps/server/src/mcp/toolkits/thread/*`, `apps/server/src/mcp/OrchestratorMcpService.ts`, `apps/server/src/provider/StudioOrchestrationInstructions.ts`, `apps/server/src/mcp/toolkits/orchestrator/tools.ts`.

Decisions: the stop on promote is a plain `run.interrupt` without `holdQueue`, so the queue runs on. The marker is derived on the client from runs, because a persisted item would need a `contextHandoffId` it does not have and a wire change older clients could not read.

Risks: Stopping a turn drops the completion wakes owed by its delegated tasks, as any Stop does. The new label says the turn stops.

## Decisions

### Asked
- D-01 Thread stays one thread when its model changes; a new thread stays explicit → stated by the user.
### Defaulted (change any before sw-do)
- D-02 Steer now with another model stops the turn at once rather than refusing the steer → matches the click's "now"; the label says so.
- D-03 Options-only differences keep steering → an effort change is not worth stopping a turn.
- D-04 The folded brief shows no preview → the title already names it, and a preview could be code.
### Open
- none

## Tasks

### T-01 Clean the folded relay view
- AC: AC-01, AC-02 | Files: apps/web/src/studio/workerMessagePresentation.ts, apps/web/src/components/studio/RelayedMessage.tsx, apps/web/src/components/chat/MessagesTimeline.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/workerMessagePresentation.test.ts apps/web/src/components/studio/RelayedMessage.test.tsx

### T-02 Steer now runs another model's row in the same thread
- AC: AC-03, AC-04 | Files: apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts

### T-03 The queue row says what will happen
- AC: AC-05 | Files: packages/client-runtime/src/state/threadWorkflows.ts, apps/web/src/components/chat/QueuedRunsControl.tsx, apps/mobile/src/features/threads/ThreadQueueControl.tsx | Test: node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/state/threadWorkflows.test.ts

### T-04 An agent switches its own thread
- AC: AC-06, AC-07, AC-08 | Files: apps/server/src/mcp/toolkits/thread/tools.ts, apps/server/src/mcp/toolkits/thread/handlers.ts, apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/provider/StudioOrchestrationInstructions.ts, apps/server/src/mcp/toolkits/orchestrator/tools.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/OrchestratorMcpBetweenTurns.test.ts apps/server/src/mcp/toolkits/core.test.ts

### T-05 Same-provider switch marker
- AC: AC-09 | Files: packages/client-runtime/src/handoff.ts, apps/web/src/components/chat/MessagesTimeline.tsx | Test: node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/handoff.test.ts

### T-06 Pick during a fallback survives the reset
- AC: AC-10 | Files: apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts

### T-07 Verify and close 1182
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10 | Files: .specweave/increments/1182-model-changes-keep-one-thread/spec.md | Test: specweave verify 1182-model-changes-keep-one-thread
