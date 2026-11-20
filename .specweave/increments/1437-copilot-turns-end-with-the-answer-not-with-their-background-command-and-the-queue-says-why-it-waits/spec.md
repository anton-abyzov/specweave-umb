# Copilot turns end with the answer, not with their background command, and the queue says why it waits

## Problem

On M5, messages typed into a GitHub Copilot thread often sit in the queue behind a turn that shows "No new events for 4m" and "Can't steer now". Evidence and timelines: `reports/root-cause.md`.

1. **Copilot holds the turn open.** Copilot CLI 1.0.114 does not answer `session/prompt` while a shell it started in the background (`mode: "async"`) is alive. The app treats that prompt as the turn. In "GTA 6 livestream kit" on November 20, 2026, turn 30 wrote its answer after 17 seconds and stayed running for 13 minutes 39 seconds until Stop; turns 26 and 28 were silent for 461 s and 611 s the same way. Two typed messages waited 701 s and 632 s for that turn and were then held by Stop. Across M5, Copilot left a background command running in 4 turns, and all 4 stayed open until the command ended or Stop was pressed.
2. **A Copilot thread can never be steered.** ACP has no mid-turn message, and interrupt-and-restart was switched off for Copilot in 1146 because cancelling a prompt stops its background agents. Every message to a busy Copilot thread queues. On M5 (567 runs, November 16 to 20), 11 of 78 typed Copilot messages waited over 30 seconds, against 2 of 94 on Claude and Codex.
3. **The screen reads as a temporary stall.** "Can't steer now" is permanent on Copilot, each row still shows a disabled "Steer now", and "No new events" is in the warning colour while the provider waits on a command it could name.
4. **Stop makes it worse.** Stop is the only way out, and it holds the queue until Resume, although the turn had already answered.

## Scope

In: the Copilot ACP adapter tracks the background commands a turn started; a turn that has answered and only waits on them gives way to a queued message; Stop on such a turn does not hold the queue; Steer now on Copilot by interrupt-and-restart when no background agent is running (if D-02 is accepted and the probe allows it); the queue header and live row say what is true.

Out: mid-turn delivery inside a running Claude or Codex command (a steered message is read when the command returns); prompt text telling agents how to run watchers (the standing rule is to enforce in code); other ACP agents; the 45-minute silent-run watchdog.

## Acceptance Criteria

- [ ] AC-01: A recorded probe of Copilot CLI 1.0.114 in `--acp` mode answers, in `reports/copilot-acp-probe.md`: (a) whether a second `session/prompt` is accepted while one is open; (b) whether `session/cancel` on a prompt that only waits on a background command leaves that command running and its output readable by shell id in the next prompt, with the stop reason returned; (c) whether Copilot sends any update when a background command ends while no prompt is open; (d) how a Copilot background agent appears in session updates, and whether it survives the same cancel; (e) whether any update marks the end of the model's step while the prompt stays open.
- [ ] AC-02: The server knows which background commands a Copilot turn started and which are still running, from the tool results (`<command started in background with shellId: X>`, `<shellId: X completed ...>`, `<command with id: X stopped>`), and publishes them on the running turn.
- [ ] AC-03: A Copilot turn gives way to the queue when all of these hold: it has written an answer, no tool call, request or background agent is open, it has been quiet for 30 seconds, a background command it started is still running, and a message is waiting in the queue. The turn ends as completed, the background command keeps running, and the first queued message starts within 2 seconds. With an empty queue the turn stays open and Copilot reports the command's result itself, as today.
- [ ] AC-04: The prompt of the message that starts after AC-03 names the background commands still running and their shell ids. If the probe (AC-01 c) finds a signal for a command ending outside a prompt, the thread also gets one automatic delivery when it ends; if not, no wake is promised and the probe report says so.
- [ ] AC-05: Stop on a turn that has written its answer and only waits on a background command ends it without holding the queue. Stop on a turn that is still working holds the queue as today.
- [ ] AC-06: (Only if D-02 is accepted and AC-01 d gives a reliable way to see a running background agent.) On a Copilot thread with no background agent running, Steer now is enabled on a typed message: it cancels the current step and starts the message at once in the same session, and the queue order behind it is kept. With a background agent running it stays disabled and says "A background agent is running. Steering would stop it." Messages are never steered into a Copilot turn automatically.
- [ ] AC-07: Where a provider cannot steer this turn for a lasting reason, the queue header shows the reason in words ("Sends when this turn ends · GitHub Copilot can't take a message mid-turn") instead of "Can't steer now", and the rows show no Steer now button. A temporary reason (turn starting, saving its checkpoint) keeps the disabled button and its tooltip.
- [ ] AC-08: While a running turn is quiet and a background command it started is running, the live row says "Waiting on a background command (X) · 4m" in the normal colour. "No new events" stays for a quiet turn with nothing known to be running.
- [ ] AC-09: On M5 with the released build, in a Copilot thread that starts a 5-minute background command and answers, a message typed after the answer starts within 35 seconds of the answer, and the command is still running. Screenshots and the run rows are in `reports/`.

## Approach

1. Probe first (T-01). The app bundle of the CLI is compressed, so the answers must come from a live `copilot --acp` session in a scratch folder with a throwaway data directory. Observed today, once: a background command was alive 17 seconds after Stop; the provider log keeps no `session/cancel` line or stop reason, so the probe must capture both. If a second prompt is accepted mid-turn, AC-03 and AC-06 use it instead of cancel. If cancel kills background commands, AC-03 stops and D-01 returns to the user before any code. No Copilot background agent has run on M5 (its five `subagent` items are the app's own advisor and delegated threads), so AC-06 waits on AC-01 d.
2. `apps/server/src/orchestration-v2/Adapters/copilotBackgroundCommands.ts` (new): parse the three tool-result forms into `started`, `ended`, `stopped` per shell id. Wired through the existing flavor hooks (`extractBackgroundTaskId`, `extractBackgroundTaskCompletion`) in `AcpRegistryAdapterV2.ts`, so the adapter's `BackgroundWork` report carries them. `AcpAdapterV2.ts` is 8,683 lines; new logic goes in the new file.
3. Ending the turn: a new flavor option, `settlePromptWaitingOnBackgroundCommands`, read where the adapter already settles prompts with background work. The orchestrator asks the adapter to give way when a queued run exists; when the conditions of AC-03 hold, the adapter sends `session/cancel`, takes the prompt's stop reason as a normal end, and finalizes the run as completed. An optional wake (AC-04) reuses `backgroundWorkNotification`.
4. `apps/server/src/orchestration-v2/Orchestrator.ts`: a stop request for a run whose adapter reports "answered, waiting on background" completes it instead of holding the queue.
5. `CommandPolicy.ts`: Copilot's interrupt-and-restart stays off as a capability. A per-turn check allows a person's promote-to-steer when the active run has no open subagent item. `resolveMessageDispatchIntent` is unchanged, so sends still queue.
6. `packages/client-runtime/src/state/threadWorkflows.ts`: `steerUnavailableReason` returns a kind (`temporary` or `lasting`) with the words; the workflow state carries the turn's running background commands. `QueuedRunsControl.tsx` and `MessagesTimeline.tsx` render AC-07 and AC-08. New phrases go in all eight `apps/web/src/i18n/phrases/*.ts` files.

Rejected: ending the turn on a timer with an empty queue (it would drop Copilot's own report when the command ends, and the app may have no signal to replace it); telling Copilot in its instructions to detach watchers (prose the app cannot enforce, and the agent followed Copilot's own tool advice); switching interrupt-and-restart back on for every Copilot turn (stops background agents, the reason it was turned off in 1146); a shorter silent-run watchdog (would also end turns that are really working).

Risks: giving way may cut off a Copilot that was about to write more without a tool call. Measured on M5: in 304 places where a Copilot turn continued after an assistant message with nothing open, 4 pauses were 15 to 22 s and none longer, so the window is 30 s, and it applies only with a background command running and a message waiting. AC-01 e may replace the timer with a real signal. The parsing depends on Copilot's result wording; an unrecognized form leaves today's behaviour.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-03 Stop on a turn that has already answered and only waits on a background command does not hold the queue.
- D-04 Quiet window is 30 seconds. With an empty queue the turn stays open so Copilot can report the result itself.
### Open
- D-01 (user) May the app end a Copilot turn that has answered and only waits on its own background command, as soon as a message is waiting? Recommended: yes, automatically. The command keeps running; the agent's own report of its result may be lost unless the probe finds a signal.
- D-02 (user) May Steer now be offered on Copilot as a manual press when no background agent is running? It discards the step in progress and partly reverses 1146. Recommended: yes, manual only. This is what shortens the 8 of 11 typed waits that sat behind a turn that was really working.

## Tasks

### T-01 Probe Copilot CLI over ACP and record the answers
- AC: AC-01 | Files: .specweave/increments/1437-copilot-turns-end-with-the-answer-not-with-their-background-command-and-the-queue-says-why-it-waits/reports/copilot-acp-probe.md | Test: test -s .specweave/increments/1437-copilot-turns-end-with-the-answer-not-with-their-background-command-and-the-queue-says-why-it-waits/reports/copilot-acp-probe.md

### T-02 Track a Copilot turn's background commands
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/copilotBackgroundCommands.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/copilotBackgroundCommands.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/Adapters/copilotBackgroundCommands.test.ts

### T-03 An answered turn that only waits on a background command gives way to the queue
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts

### T-04 Stop on an answered turn does not hold the queue
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts

### T-05 Steer now on Copilot when no background agent is running (after D-02)
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/CommandPolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/CommandPolicy.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/CommandPolicy.test.ts src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts

### T-06 Queue header and rows say why a message waits
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/threadWorkflows.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/threadWorkflows.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/QueuedRunsControl.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/QueuedRunsControl.dom.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts | Test: pnpm --dir apps/web exec vp test run src/components/chat/QueuedRunsControl.dom.test.tsx

### T-07 Live row names the background command a quiet turn waits on
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/liveActivity.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/liveActivity.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts | Test: pnpm --dir apps/web exec vp test run src/components/chat/liveActivity.test.ts src/components/chat/MessagesTimeline.test.tsx

### T-08 Installed check on M5, verify and close
- AC: AC-09 | Files: .specweave/increments/1437-copilot-turns-end-with-the-answer-not-with-their-background-command-and-the-queue-says-why-it-waits/reports/installed-check.md | Test: specweave verify 1437
