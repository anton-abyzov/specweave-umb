# Copilot turns end with the answer, not with their background command, and the queue says why it waits

## Problem

On M5, messages typed into a GitHub Copilot thread often sit in the queue behind a turn that shows "No new events for 4m" and "Can't steer now". Evidence and timelines: `reports/root-cause.md`.

1. **Copilot holds the turn open.** Copilot CLI 1.0.114 does not answer `session/prompt` while a shell it started in the background (`mode: "async"`) is alive. The app treats that prompt as the turn. In "GTA 6 livestream kit" on November 20, 2026, turn 30 wrote its answer after 17 seconds and stayed running for 13 minutes 39 seconds until Stop; turns 26 and 28 were silent for 460 s and 611 s the same way. Two typed messages waited 632 s and 562 s.
2. **A Copilot thread can never be steered.** ACP has no mid-turn message, and interrupt-and-restart was switched off for Copilot in 1146 because cancelling a prompt stops its background agents. Every message to a busy Copilot thread queues. On M5 (567 runs, November 16 to 20), 11 of 78 typed Copilot messages waited over 30 seconds, against 2 of 94 on Claude and Codex.
3. **The screen reads as a temporary stall.** "Can't steer now" is permanent on Copilot, each row still shows a disabled "Steer now", and "No new events" is in the warning colour while the provider waits on a command it could name.
4. **Stop makes it worse.** Stop is the only way out, and it holds the queue until Resume, although the turn had already answered.

## Scope

In: the Copilot ACP adapter tracks the background commands a turn started; a turn that has answered and only waits on them ends, and the queue drains; Stop on such a turn does not hold the queue; Steer now on Copilot by interrupt-and-restart when no background agent is running; the queue header and live row say what is true.

Out: mid-turn delivery inside a running Claude or Codex command (a steered message is read when the command returns); prompt text telling agents how to run watchers (the standing rule is to enforce in code); other ACP agents; the 45-minute silent-run watchdog.

## Acceptance Criteria

- [ ] AC-01: A recorded probe of Copilot CLI 1.0.114 in `--acp` mode answers, in `reports/copilot-acp-probe.md`: whether a second `session/prompt` is accepted while one is open; whether `session/cancel` on a prompt that only waits on a background command leaves that command running and its later output readable by shell id; and whether a background agent survives the same cancel.
- [ ] AC-02: The server knows which background commands a Copilot turn started and which are still running, from the tool results (`<command started in background with shellId: X>`, `<shellId: X completed ...>`, `<command with id: X stopped>`), and publishes them on the running turn.
- [ ] AC-03: A Copilot turn that has written its answer, has no tool call, request or background agent open, has been quiet for 15 seconds and has a background command still running ends as completed. Its background command keeps running. The next queued message starts within 2 seconds, and its prompt names the background commands still running.
- [ ] AC-04: When that background command ends later and nothing is running in the thread, the thread gets one automatic delivery ("Background command X finished") so the agent can report, as a queued message that follows the existing order rules. No delivery is made for a command the person stopped.
- [ ] AC-05: Stop on a turn in the state of AC-03 (before the 15 seconds, or while a background agent keeps it open) ends it without holding the queue. Stop on a turn that is still working holds the queue as today.
- [ ] AC-06: On a Copilot thread with no background agent running, Steer now is enabled on a typed message: it cancels the current step and starts the message at once in the same session, and the queue order behind it is kept. With a background agent running it stays disabled and says "A background agent is running. Steering would stop it." Messages are never steered into a Copilot turn automatically.
- [ ] AC-07: Where a provider cannot steer this turn for a lasting reason, the queue header shows the reason in words ("Sends when this turn ends · GitHub Copilot can't take a message mid-turn") instead of "Can't steer now", and the rows show no Steer now button. A temporary reason (turn starting, saving its checkpoint) keeps the disabled button and its tooltip.
- [ ] AC-08: While a running turn is quiet and a background command it started is running, the live row says "Waiting on a background command (X) · 4m" in the normal colour. "No new events" stays for a quiet turn with nothing known to be running.
- [ ] AC-09: On M5 with the released build, a Copilot thread that starts a 5-minute background command and answers ends its turn within 20 seconds of the answer, a message typed after that starts at once, and the command's result arrives as a later turn. Screenshots and the run rows are in `reports/`.

## Approach

1. Probe first (T-01). The app bundle of the CLI is compressed, so the answers must come from a live `copilot --acp` session in a scratch folder with a throwaway data directory. Observed today, once: a background command survived Stop for at least 17 seconds. If the probe shows a second prompt is accepted mid-turn, AC-06 uses it instead of cancel and D-02 is reopened. If the probe shows cancel kills background commands, AC-03 stops and D-01 returns to the user before any code.
2. `apps/server/src/orchestration-v2/Adapters/copilotBackgroundCommands.ts` (new): parse the three tool-result forms into `started`, `ended`, `stopped` per shell id. Wired through the existing flavor hooks (`extractBackgroundTaskId`, `extractBackgroundTaskCompletion`) in `AcpRegistryAdapterV2.ts`, so the adapter's `BackgroundWork` report carries them. `AcpAdapterV2.ts` is 8,683 lines; new logic goes in the new file.
3. Ending the turn: a new flavor option, `settlePromptWaitingOnBackgroundCommands`, read where the adapter already settles prompts with background work. When the conditions of AC-03 hold, the adapter sends `session/cancel`, takes the prompt's `cancelled` stop reason as a normal end, and finalizes the run as completed. The wake in AC-04 reuses `backgroundWorkNotification`.
4. `apps/server/src/orchestration-v2/Orchestrator.ts`: a stop request for a run whose adapter reports "answered, waiting on background" completes it instead of holding the queue.
5. `CommandPolicy.ts`: Copilot's interrupt-and-restart stays off as a capability. A per-turn check allows a person's promote-to-steer when the active run has no open subagent item. `resolveMessageDispatchIntent` is unchanged, so sends still queue.
6. `packages/client-runtime/src/state/threadWorkflows.ts`: `steerUnavailableReason` returns a kind (`temporary` or `lasting`) with the words; the workflow state carries the turn's running background commands. `QueuedRunsControl.tsx` and `MessagesTimeline.tsx` render AC-07 and AC-08. New phrases go in all eight `apps/web/src/i18n/phrases/*.ts` files.

Rejected: telling Copilot in its instructions to detach watchers (prose the app cannot enforce, and the agent followed Copilot's own tool advice); switching interrupt-and-restart back on for every Copilot turn (stops background agents, the reason it was turned off in 1146); a shorter silent-run watchdog (would also end turns that are really working).

Risks: a turn ended at 15 seconds may cut off a Copilot that was about to write more without a tool call; the quiet window and "has written an assistant message" guard limit this, and the probe measures the longest gap between an answer and a follow-up chunk. The parsing depends on Copilot's result wording; an unrecognized form leaves today's behaviour.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A Copilot turn that has answered and only waits on a background command ends on its own after 15 quiet seconds, without a button. The command keeps running and its result arrives as a later turn.
- D-02 Steer now on Copilot is a manual press only, offered when no background agent is running. It discards the step in progress. Sends to a busy Copilot thread still queue.
- D-03 Stop on a turn that has already answered does not hold the queue.
- D-04 Quiet window is 15 seconds; the wake after a background command ends is one automatic delivery per command.
### Open
- none

## Tasks

### T-01 Probe Copilot CLI over ACP and record the answers
- AC: AC-01 | Files: .specweave/increments/1437-copilot-turns-end-with-the-answer-not-with-their-background-command-and-the-queue-says-why-it-waits/reports/copilot-acp-probe.md | Test: test -s .specweave/increments/1437-copilot-turns-end-with-the-answer-not-with-their-background-command-and-the-queue-says-why-it-waits/reports/copilot-acp-probe.md

### T-02 Track a Copilot turn's background commands
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/copilotBackgroundCommands.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/copilotBackgroundCommands.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/Adapters/copilotBackgroundCommands.test.ts

### T-03 End an answered turn that only waits on a background command, and wake when it ends
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts

### T-04 Stop on an answered turn does not hold the queue
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts

### T-05 Steer now on Copilot when no background agent is running
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/CommandPolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/CommandPolicy.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/CommandPolicy.test.ts src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts

### T-06 Queue header and rows say why a message waits
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/threadWorkflows.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/threadWorkflows.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/QueuedRunsControl.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/QueuedRunsControl.dom.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts | Test: pnpm --dir apps/web exec vp test run src/components/chat/QueuedRunsControl.dom.test.tsx

### T-07 Live row names the background command a quiet turn waits on
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/liveActivity.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/liveActivity.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.test.tsx | Test: pnpm --dir apps/web exec vp test run src/components/chat/liveActivity.test.ts src/components/chat/MessagesTimeline.test.tsx

### T-08 Installed check on M5, verify and close
- AC: AC-09 | Files: .specweave/increments/1437-copilot-turns-end-with-the-answer-not-with-their-background-command-and-the-queue-says-why-it-waits/reports/installed-check.md | Test: specweave verify 1437
