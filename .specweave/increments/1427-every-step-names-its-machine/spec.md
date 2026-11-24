# 1427 Every step names its machine

Linked to 1390 (equal coordinators: every machine runs its own coordinator).

## Problem

Anton, November 19, 2026, 5:19 PM: "Make sure we never mix machines, and we are always clear where exactly we need to do it. It seems like I see it in the coordinator on the M5 machine, but the message was addressed to the Linux machine."

His screenshot showed the specweave coordinator with a "linux-mini" badge in the header. A reply was labelled "linux-mini · Claude Code · Opus 5.5" and was about Codex `token_expired` on M5. Its Blockers told him to fix M5 and then press Continue in "PS5 OBS", a chat on M5. The thread filter was set to linux-mini, and the sidebar footer read "linux-mini 1.0.384 → 1.0.393" above an unnamed "Restart to update".

What happened: the linux-mini coordinator wrote the reply. It relayed its own worker thread, "Codex token_expired on M5", which ran on linux-mini and looked into M5 from there. The window was showing linux-mini's coordinator. Nothing on screen said which machine the window was on, which machine wrote the reply, or that every step was for M5.

The audit (`reports/machine-clarity-audit.md`, app at `0ec9cd96`) found these gaps:

- **Window and coordinator.** Nothing visible says "this window is on M5" apart from "showing linux-mini's coordinator". The header tag is a bare machine name. "This machine", "this computer" and "this device" each mean different machines in different places.
- **Message attribution.** The reply label names the coordinator's machine but doesn't say so. User messages carry the same label. The `re:` chip, thread chips and relayed worker notes never name the thread's machine.
- **Agent instructions.** No agent is told which machine it is on, or to name the machine in each step the user must take. None is told what to do with another machine's problem. Error texts say "this machine", and coordinators quote errors exactly, so a relayed error points at the wrong machine.
- **Routing.** A coordinator cannot hand a problem to another machine's own coordinator. M5 refuses a send to its coordinator thread (`apps/server/src/mcp/workGrantAccess.ts:297-310`). The link dialog and one agent hint still describe a single main coordinator.
- **Action surfaces.** Notifications, phone pushes, access cards, question and approval cards, and the "Sign in again" and "Continue" buttons don't name the machine they act on.

## Scope

In:
- Agent instructions for coordinators and workers.
- Error texts that say "this machine".
- Message labels and chips in the coordinator conversation.
- The window and coordinator labels in the header, sidebar and switcher.
- Machine names on action cards, buttons, desktop notifications and toasts.
- The leftover single-coordinator copy.
- Coordinator messages between machines in the same linked project (D-01, T-05 to T-09).

Out:
- The phone push schema (`packages/contracts/src/relay.ts`, `infra/relay`). Follow-up F-01.

## Acceptance Criteria

- **AC-01:** Every coordinator and worker knows its own machine. The per-turn clock line reads "Current local time on <label>, the machine this agent runs on". The coordinator role says "You are the coordinator on <label>". Each machine has its own coordinator, and the reader may be on another machine's window.
- **AC-02:** Agent instructions require every step the user must take to start with the machine it is done on ("On M5: ..."). This covers Blockers too. A thread on another machine is named with its machine.
- **AC-03:** Asked about another machine's thread or failure, a coordinator reads it there with `studio_thread_read {machine}` and opens its answer with that machine's label. It continues or retries the thread itself with `studio_thread_send {machine}` where it is allowed to. It leaves the user only the step no agent can take, written "On <machine>: ...". A "this machine" in a tool result or error is rewritten as the label of the machine that wrote it.
- **AC-04:** Server error and hint texts name the machine:
  - the Codex expired-sign-in text (`CodexAdapterV2.ts:1214`);
  - the remote-worker access text (`RemoteWorkers.ts:394-397`);
  - the grant refusal "Ask this machine's coordinator" (`workGrantAccess.ts`), which becomes "Open <machine>'s coordinator";
  - `threadNotFoundHint.ts:35`, which no longer says a linked copy leaves coordinating to another machine.
- **AC-05:** The window says where it is and what it shows:
  - The sidebar header shows the window's machine by name.
  - When the coordinator shown is on another machine, the header tag reads "<machine>'s coordinator", visibly, with the window's machine next to it.
  - The switcher marks the window's own row "this window".
  - The sidebar's restart and update buttons name the machine they act on.
  - "This machine", "this computer" and "this device" are replaced by the machine's name wherever the window and the machine can differ.
- **AC-06:** Coordinator messages name machines:
  - The reply label reads "Coordinator on <machine> · <provider> · <model>".
  - A user message reads "To <machine>'s coordinator".
  - The `re:` chip, thread chips and "Message from <thread>" notes add " · <machine>" when that thread's machine differs from the coordinator's.
- **AC-07:** Action surfaces name their machine, in that machine's colour, when it is not the window's machine:
  - question and approval cards;
  - access request cards (web and iOS);
  - the "Sign in again" and "Continue" recovery buttons;
  - the provider status banner;
  - desktop notifications and toasts.
- **AC-08:** The link dialog says each machine keeps its own coordinator. No user-facing copy says a joining coordinator stops or becomes read-only history.
- **AC-09:** The headless coordinator fixture shows a remote coordinator viewed from another window: header, labels, chips and a card. It is checked light and dark at 1280 and 390 px.
- **AC-10:** Reviewed by another model family, merged on green CI, and released through `request-release.sh`.

Coordinator messages (D-01; design in `reports/coordinator-messages-design.md`):

- **AC-11:** A coordinator sends a message to one other machine's coordinator with `studio_coordinator_message {machine, kind, subject, text, userStep?, refs?, replyTo?}`. Kinds are `problem`, `finding`, `request` and `reply`. Text is at most 1,500 characters, the subject 120, the step 200 and refs 8. A longer text is refused with "Put the detail in a report and reference it." A retry with the same `clientRequestId` delivers one message.
- **AC-12:** The receiver admits a message only when all of these hold: the caller's machine is a member of the same linked project (`linkedCopyFor`); its grant covers the project and is not revoked or expired; and both machines advertise `coordinator-message.v1`. Personal assistant projects are refused. Each refusal names both machines ("M5 no longer takes messages from linux-mini…"). `studio_thread_send` to another machine's coordinator thread is still refused, and once messages ship its refusal points at `studio_coordinator_message`.
- **AC-13:** A message is stored as a queued message on the receiver's coordinator thread. It never interrupts or steers a turn.
  - The agent reads it in a fixed frame that names the sender's coordinator, says it is another agent's report and not the user's words, and lists refs with the call that reads each.
  - A turn it starts runs on the receiver's own sign-ins and rules. Nothing runs under the sender's grant.
  - A message never answers a pending question, approval or access card, and never counts as the user's consent.
- **AC-14:** Big context is pulled, never pushed. Each kind of ref has its own read:
  - thread refs: `studio_thread_read {machine}`;
  - report refs: `studio_coordinator_message_read`, in pages of 8,000 characters up to 256 KB;
  - file refs: `studio_file_transfer` `get`.

  A read is answered only for refs the message named, under the same admission as AC-12.
- **AC-15:** Messages stay quiet:
  - **Repeats:** a repeat with the same key merges into the earlier message while the receiving agent has not read it. The merged message shows a count and the newest text, starts no new wake, and the sender is told it merged.
  - **Rate:** a direction carries at most 6 messages per hour per project. More are folded into one digest, except a `problem` with a step.
  - **Read-only grants:** they send only `finding` and `reply`.
  - **Replies:** a reply cannot be replied to, and a turn woken by a message may send that machine only a reply. A reply to a `finding` wakes no model.
  - **Settle:** the wake waits the 45-second settle window.
- **AC-16:** The thread list item reports `waiting` (open questions, approvals and sign-ins), so a coordinator learns another machine's thread facts by a live read. A message never claims, moves or releases a thread. "Please take this thread" is a Hand off.
- **AC-17:** An undelivered message waits in the sender's outbox for up to 24 hours. It is retried on reconnect and on each linked sync pass. The sender's agent is told when the receiver is offline. The outgoing row shows Queued, Delivered, Read, Answered or "Not delivered: M5 was offline for 24 hours".
- **AC-18:** How messages look:
  - **Receiving window:** a message reads "From linux-mini's coordinator" in linux-mini's colour, with the kind, subject and text. Its reference chips name each thread's machine and live status. It is never labelled "Message from a worker" and never hidden as a wake.
  - **Step:** a step reads "On M5: …" in a box, shown once, on the receiving machine.
  - **Sending window:** the conversation shows "To M5's coordinator" with its state, and the answer under it.
  - **Links and filter:** each side's row links to the other, and both sides can filter to "Messages between coordinators".
- **AC-19:** Only a message with a step notifies. The desktop notification title is "On <machine>: <step>", and the body names the sending coordinator and the project. It fires once per message; a merged repeat does not fire again. A message without a step never reaches the phone.
- **AC-20:** The headless coordinator fixture shows an incoming message with a step, a merged repeat, a reply and the sender's outgoing row. It is checked light and dark at 1280 and 390 px.

## Approach

Labels come from data the web app already has:
- `primaryEnvironmentId` for the window's machine;
- `project.environmentId` for the coordinator shown;
- `executionMachineId ?? environmentId` and `threadLocation(...)` for a thread;
- `source.environmentId` for reply sources;
- `useMachineNickname` for names, with `machineColorProps` for colour.

The server learns its own label the same way `studio_machine_list` reads `local.label` (`apps/server/src/fleet/RemoteWorkers.ts:768`). New phrases go in all eight catalogs. The catalogs are already over 1,500 lines, so new words go in the existing per-feature phrase files where those exist.

The prompt text stays short. The concise style block has a test cap (`RuntimeInstructions.test.ts:388`), so raise it only by what the new clause needs.

## Decisions

- **D-01 (decided by Anton, November 19, 2026):** A coordinator may send a message to another machine's coordinator when both are members of the same linked project. Today `workGrantAccess.ts:297-310` refuses this, so an M5 problem can only reach M5's coordinator through the user.

  Anton: "Yes, I believe it's recommended because we need to do a handoff, and that could be one of the things. Think about this: it should not be overcrowded, or think on how to share the big messages, because the context could be what you wish. Maybe sharing even information about threads."

  The design comes first: what a message carries, how large context and thread facts travel, and how the receiving window shows it without crowding. The design is in `reports/coordinator-messages-design.md`, with mockups. It was asked for on Fable 5.2, which had hit its weekly limit, so it ran on Opus 5.5. T-01 does not widen any grant.

  A message informs and never steers. It is admitted behind the linked-project membership and grant checks, and the receiver acts on it only as its own turn. Big context stays on the sender and is read page by page on demand. Repeats merge, each direction has a rate cap, and only a message with a step for the user notifies.
- **D-02 (default, November 19, 2026):** A message without a step for the user never reaches the phone. This is the design's recommendation, so the phone only alerts when there is something to do. Anton can change it.
- **D-03:** A read-only grant sends only `finding` and `reply`. A `problem` or `request` can lead the receiver to retry or interrupt its own threads, and a machine that may only read should not cause that.

## Tasks

### T-01 Agents know their machine and name it in every step
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/currentTimeLine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/workGrantAccess.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/threadNotFoundHint.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/federatedProjectThreads.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/RuntimeInstructions.test.ts apps/server/src/project/ProjectWorkspaceService.test.ts apps/server/src/mcp/workGrantAccess.test.ts

### T-02 The window, the coordinator and its messages name their machines
- AC: AC-05, AC-06, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorConversation.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorReplySources.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectDomain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadLinkChip.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/StudioThreadLink.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarChrome.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/OrchestratorSwitcher.test.tsx src/studio/machineRowState.test.ts src/i18n/i18n.test.ts

### T-03 Cards, buttons and notifications name the machine they act on
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AccessRequestCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerPendingUserInputPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerPendingApprovalPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadErrorBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/FailureRecovery.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ProviderStatusBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorQuestionAnswers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/access/accessGate.ts, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/Weave/Components/AccessRequestCard.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/Weave/Components/ApprovalCard.swift, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/AccessRequestCard.test.tsx src/i18n/i18n.test.ts

### T-04 Review, merge, release
- AC: AC-10 | Files: none | Test: gh pr list --repo anton-abyzov/specwithcode --search "1427 in:title" --state merged --json number --jq length | grep -qv '^0$'

Runs last. It covers every 1427 PR (T-01 to T-03 and T-05 to T-08), and it is not done until all of them are merged and released, whatever its test says.

### T-05 Coordinator messages: contract, wire and receiver
- AC: AC-11, AC-12, AC-13, AC-15 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/coordinatorMessage.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/coordinatorMessageWire.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffWire.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPeers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffRoute.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageReceiver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageReceiver.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerRoute.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/CoordinatorMessageReceiver.test.ts

### T-06 Coordinator messages: tools, outbox, reads on demand and instructions
- AC: AC-11, AC-12, AC-14, AC-16, AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/coordinatorMessage, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageOutbox.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageOutbox.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpThreadList.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/workGrantAccess.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/workGrantAccess.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspaceRpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestratorMcp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/federatedProjectThreads.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPeers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffRoute.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/coordinatorMessageWire.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/CoordinatorMessageReceiver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffWire.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffMove.test.fixture.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffTransfer.test.fixture.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitHandoffPreflight.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/CoordinatorMessageOutbox.test.ts apps/server/src/mcp/toolkits/coordinatorMessage apps/server/src/mcp/workGrantAccess.test.ts apps/server/src/provider/RuntimeInstructions.test.ts

Starts after T-05 and T-01 are merged.

### T-07 Coordinator messages in the conversation on both machines
- AC: AC-18, AC-20 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/useCoordinatorMessages.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorMessageCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorMessages.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorMessages.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCoordinatorMessageDisplay.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorActivity.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorConversation.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/coordinatorMessages.test.ts src/studio/coordinatorActivity.test.ts src/i18n/i18n.test.ts

Starts after T-02 and T-06 are merged.

### T-08 A message with a step notifies, naming the machine
- AC: AC-19 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorMessages.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/coordinatorMessages.test.ts

Starts after T-03 and T-07 are merged.

### T-09 A real message between two linked machines
- AC: AC-11, AC-12, AC-13, AC-15, AC-17, AC-18 | Files: .specweave/increments/1427-every-step-names-its-machine/reports | Test: test -f .specweave/increments/1427-every-step-names-its-machine/reports/coordinator-message-live-run.md

This is recorded on released builds, on two machines that share a linked project. The run shows each of these:
- one machine reports a failed thread on the other;
- that machine's coordinator retries the thread and shows "On <machine>: …";
- a repeat merges;
- a message to an offline receiver queues and is delivered on reconnect;
- a revoked grant refuses.

## Follow-ups

- **F-01:** The phone push names the machine to act on ("On M5: sign in to Codex"). An optional `machineLabel` goes on the push payload and into the relay's alert text (`packages/contracts/src/relayAgentMachine.ts`, `infra/relay/src/agentActivity/agentActivityAlerts.ts`). This is outside 1427's Scope.
