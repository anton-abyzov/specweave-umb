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

Out:
- The phone push schema (`packages/contracts/src/relay.ts`, `infra/relay`). Follow-up.
- Coordinator-to-coordinator messages across machines. This is an access change and waits on D-01.

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

- **D-01 (open, Anton's):** Allow a coordinator to queue a message to another machine's coordinator thread when both are members of the same linked project. Today `workGrantAccess.ts:297-310` refuses it, so an M5 problem can only reach M5's coordinator through the user. Until then AC-03 has the coordinator read and act on M5's threads where its grant allows, and name M5 in each step.

## Tasks

### T-01 Agents know their machine and name it in every step
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/currentTimeLine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/workGrantAccess.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/threadNotFoundHint.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/federatedProjectThreads.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/RuntimeInstructions.test.ts apps/server/src/project/ProjectWorkspaceService.test.ts apps/server/src/mcp/workGrantAccess.test.ts

### T-02 The window, the coordinator and its messages name their machines
- AC: AC-05, AC-06, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorConversation.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorReplySources.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectDomain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadLinkChip.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/StudioThreadLink.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarChrome.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/OrchestratorSwitcher.test.tsx src/studio/machineRowState.test.ts src/i18n/i18n.test.ts

### T-03 Cards, buttons and notifications name the machine they act on
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AccessRequestCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerPendingUserInputPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerPendingApprovalPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadErrorBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/FailureRecovery.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ProviderStatusBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorQuestionAnswers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/access/accessGate.ts, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/Weave/Components/AccessRequestCard.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/Weave/Components/ApprovalCard.swift, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/AccessRequestCard.test.tsx src/i18n/i18n.test.ts

### T-04 Review, merge, release
- AC: AC-10 | Files: none | Test: gh pr list --repo anton-abyzov/specwithcode --search "1427 in:title" --state merged --json number --jq length | grep -qv '^0$'
