# Machine clarity audit, November 19, 2026

Five read-only readers, one dimension each, on app repository `repositories/anton-abyzov/specwithcode` at origin/main `0ec9cd96`. Prompted by Anton's 5:19 PM screenshot: the linux-mini coordinator's reply about Codex `token_expired` on M5.

## window-vs-coordinator

**Answers** (origin/main `0ec9cd96`)

1. Nothing visible and always on says "this window is on X". The window's machine is `primaryEnvironmentId`, the server the UI loaded from (`apps/web/src/connection/desktopLocal.ts:47-48`). Its name appears in only two places. One is the account menu header, as the raw label rather than the nickname (`apps/web/src/components/account/AccountMenu.tsx:240`). The other is the footer name, and only when Connect is unavailable (`apps/web/src/components/account/accountMenuModel.ts:50`).
2. Showing another machine's coordinator is barely marked as remote. The header tag appears only when the shown machine is not the primary (`apps/web/src/components/studio/ProjectWorkspaceSurface.tsx:1813-1835`). Its visible text is just the machine name: "On " is screen-reader only (`:1831`) and "not this computer" is a tooltip (`:1818`). The composer chip says "On {machine}" for the shown machine whether it is local or remote (`apps/web/src/components/studio/OrchestratorSwitcher.tsx:201,211`). The switcher menu has no row state for "this window" (`apps/web/src/studio/machineRowState.ts:138-180`). Send takes the remote machine's colour but never its name (`apps/web/src/components/studio/CoordinatorComposer.tsx:217-229`). The switcher is mounted only in the composer row (`ProjectWorkspaceSurface.tsx:2137`), not in the header.
3. "Restart to update" and "Update now" act on this desktop app and its local service. The button exists only in Electron (`apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx:120`), reads its state from `window.desktopBridge` (`apps/web/src/state/serviceUpdate.ts:14-16`), and lists the primary's work with `name: null` (`SidebarRestartToUpdate.tsx:152,276`). Its label never names a machine (`SidebarRestartToUpdate.logic.ts:396`). The "a → b" rows are per machine, do name it, and their Update acts on that machine (`apps/web/src/components/sidebar/SidebarServerUpdate.tsx:51-60,168-179`).

**Places the two are confused (verified in code), most harmful first**

1. **Footer.** The user sees "linux-mini 1.0.20 → 1.0.25 Update" (`apps/web/src/components/sidebar/SidebarChrome.tsx:179`) directly above an unnamed "Restart to update" (`:182`). That button seems to belong to the row above or to the coordinator shown. Its tooltip "Stops running work…" names no machine (`SidebarRestartToUpdate.logic.ts:306-307`). Fix: "Restart <window machine>", and add "on <machine>" to that tooltip.
2. **Header tag.** A bare "linux-mini" next to the title reads as "you are on linux-mini", the opposite of what it means. Fix: make the visible text "Showing linux-mini · window on M5".
3. **"This machine" means different machines.** Coordinator problems say "This machine needs an update…" about the viewed machine (`apps/web/src/studio/projectCoordinatorMachine.ts:29-32`, passed through unchanged at `apps/web/src/components/studio/ProjectWorkspace.tsx:353-359`). In the threads filter, "· this machine" (`apps/web/src/components/studio/shell/ThreadsPane.tsx:752,758`) and "on this machine" in the service text (`SidebarRestartToUpdate.logic.ts:363,425`) mean the window's machine. Fix: name the machine in each.
4. **"On {machine}" has three meanings.** It is the coordinator shown (`OrchestratorSwitcher.tsx:201`), the chat filter (`apps/web/src/components/studio/shell/StudioSidebar.tsx:1219`), and where a project lives (`apps/web/src/components/studio/shell/SidebarProjectList.tsx:671`). Fix: "Coordinator: X" and "Chats on X".
5. **No machine name means the window's machine.** A sidebar chat omits its machine only when it is on the window's machine (`StudioSidebar.tsx:1306-1309`). "On other machines" splits projects by the window's machine (`SidebarProjectList.tsx:436-446`, `apps/web/src/sidebarProjectGrouping.ts:130-136`). So while the page shows linux-mini's coordinator, an unlabelled chat is still M5's. The filter's "this machine" exists only in a tooltip and aria-label, and `data-current` has no CSS (I searched). Fix: show the window's machine name once in the sidebar header.
6. **"This computer" and "this device" mean the serving machine.** In a browser on a phone or another Mac, the primary is the remote server (`desktopLocal.ts:51-53`). There, "not this computer" (`ProjectWorkspaceSurface.tsx:1818`) and "Not on this device" (`SidebarProjectList.tsx:671`) are false about the device in hand. Only Leave uses a real same-device test (`OrchestratorSwitcher.tsx:677-678`).
7. **The last viewed machine comes back silently.** Opening a project on M5 can land on linux-mini's coordinator, marked only by the bare tag (`projectCoordinatorMachine.ts:79-84`, `ProjectWorkspace.tsx:150-156`, saved per device at `packages/contracts/src/settings.ts:583-586`).
8. **No primary, no remote marker.** With a null primary nothing is marked remote (`ProjectWorkspaceSurface.tsx:1813`, `sidebarProjectGrouping.ts:130-136`).

**One shared fix:** add a visible "Window: M5" in the sidebar header, change the tag to "Showing linux-mini's coordinator", add a "this window" note on the switcher row for the window's machine, and put machine names in place of every "this machine", "this computer" and "this device".

**Related, outside this dimension:** the "re: PS5 OBS ↗" chip has the source machine's `environmentId` but never shows it (`apps/web/src/components/studio/CoordinatorReplySources.tsx:20-43`). That is why "press Continue in 'PS5 OBS'" does not say M5. The message label "linux-mini · model" is the viewed project's machine (`apps/web/src/components/studio/CoordinatorConversation.tsx:323,364`, `apps/web/src/studio/projectDomain.ts:340`), which is correct for that coordinator's own runs.

**Guesses, not verified**
- If the badge the owner saw was the header tag, his window was not served by linux-mini, since the tag only appears for a remote view. He was then on another machine looking at linux-mini's coordinator, and the bare name told him the reverse. If it was the composer chip, it shows in both cases.
- He probably read "M5" in the Blockers, and the "re:" chip and unnamed chats offered nothing to correct him.
- I did not check whether his nicknames differ from the host labels. The account menu uses the raw label, so the names could differ between places.

## message-attribution

**Facts verified in code (origin/main `0ec9cd9`)**

1. **The reply label names the viewed coordinator's machine, but it doesn't say so.** `apps/web/src/studio/projectDomain.ts:326-341` builds `${machine} · ${model}`. It reads only `id` and `modelSelection` from runs (`:328`), and runs carry no machine (`packages/client-runtime/src/handoff.ts:12-15`). The caller passes `useMachineNickname(project.environmentId)` (`apps/web/src/components/studio/CoordinatorConversation.tsx:323`, `:362-365`). `project` is the checkout picked in the switcher (`apps/web/src/components/studio/ProjectWorkspace.tsx:205-207`), and the header badge uses the same id (`ProjectWorkspaceSurface.tsx:316`).
   - What he sees: an `<h3>Coordinator</h3>` (`CoordinatorConversation.tsx:1181`), then a muted "linux-mini · Claude Code · Opus 5.5" (`:1201-1205`).
   - Why it misleads: the label is accurate, but nothing says "the linux-mini coordinator wrote this". Nothing names the machine serving the window either (`usePrimaryEnvironmentId`, `ProjectWorkspaceSurface.tsx:318`, is never used for the label).
   - Fix: have the heading or label read "Coordinator on linux-mini · Claude Code · Opus 5.5". When `project.environmentId !== primaryEnvironmentId`, add "viewed from <window machine>".

2. **User messages get the same machine label.** `CoordinatorConversation.tsx:362-364` labels `createdBy === "user"` messages too, so his own message reads "linux-mini · Claude Code · Opus 5.5". That looks like he typed on linux-mini, when it really names the coordinator that ran the request. Worker threads behave the same (`apps/web/src/components/chat/UserMessageProvenance.tsx:40-47`), and the tooltip shows a raw environment id, not a name (`:87-89`).
   - Fix: change user-message wording to "Ran by linux-mini coordinator · …" and put the machine name in the tooltip.

3. **The `re: <title> ↗` chip never names the thread's machine.** `apps/web/src/components/studio/CoordinatorReplySources.tsx:20-44` renders only the prefix, the title and "· unavailable". `source.environmentId` is known (`packages/shared/src/coordinatorReplySources.ts:85-89`) but never shown. The live title is resolved only for the coordinator's own environment (`CoordinatorConversation.tsx:429-434`), so remote sources fall back to the stored title.
   - The chip (`:1182-1189`) sits directly above the label (`:1201-1205`). He sees "re: Codex token_expired on M5 ↗" and then "linux-mini · …" with nothing saying the thread itself lives on linux-mini.
   - Fix: in projects on 2 or more machines (`copyRolesSummary` non-null, `projectDomain.ts:354`), append the thread's short machine name: "re: Codex token_expired on M5 · linux-mini ↗".

4. **Thread chips show no machine, even when they cross machines.**
   - `ChipFace` shows only an icon, a status dot and the title (`apps/web/src/components/ThreadLinkChip.tsx:22-32`). Its tooltip is "title · status" (`:60`, `:101`).
   - `ProjectThreadChip` (`ProjectThreadCards.tsx:39-62`) and `ProjectThreadCard` (`:112-147`) add nothing.
   - A link to another machine's thread resolves across all connected machines (`apps/web/src/components/StudioThreadLink.tsx:39-42`) and renders the same chip (`:84-97`). Only the copied Markdown keeps the machine (`:93-95`).
   - So "Thread: PS5 OBS" (on M5) looks identical to a linux-mini thread. The unreachable chip says "Thread on another machine" without naming it (`ThreadLinkChip.tsx:129-131`).
   - The data exists: `executionMachineLabel` on the shell (`packages/client-runtime/src/state/models.ts:219`), and `threadLocation` (`apps/web/src/studio/threadLocation.ts:44-79`) already builds "M4" or "M4 → Minis" for thread lists (`ThreadsPane.tsx:263`, `BoardThreads.tsx:276`, `StudioSidebar.tsx:332`). In this conversation it is used only for access-waiting (`CoordinatorConversation.tsx:337-342`).
   - Fix: give `ChipFace` an optional machine suffix and pass `threadLocation(...).label` when the thread's owner or execution machine differs from the conversation's machine.

5. **Relayed worker notes have no machine at all.** Worker messages are `role "user"`, `createdBy "agent"` (`projectCoordinatorMessageDisplay.ts:96-99`), so `executionLabel` is null (`CoordinatorConversation.tsx:362-365`). They read "Message from <title>" (`:1295-1297`).
   - Fix: "Message from <title> · <thread machine>".

6. **Title rules ignore machines.** None of these mention machine names: the agent rules (`apps/server/src/provider/StudioOrchestrationInstructions.ts:22`; `apps/server/src/project/ProjectWorkspaceService.ts:206`, "a title of a few words") or the auto-title prompts (`apps/server/src/textGeneration/TextGenerationPrompts.ts:245-271`, `:274-290`). A linux-mini thread titled "Codex token_expired on M5" is valid, and in chat nothing next to it says linux-mini. Only the open thread's composer chip names its machine (`apps/web/src/components/chat/ThreadMachineComposerChip.tsx:17-28`).
   - Fix: findings 3 and 4 cover it in the UI. Optionally add one rule: "a title names the subject; the app shows where the thread runs."

**Guesses (not verified)**

- No code emits "Thread:". A case-sensitive search of `apps/web/src`, `packages/shared/src` and `packages/client-runtime/src` found only the unrelated `deviceHandoff.ts:163`. So "Thread: <chip>" is most likely coordinator-written Markdown, rendered through `renderThreadLink` (`CoordinatorConversation.tsx:1110-1130`).
- The coordinator's prompt names other machines by label but calls its own "this machine" (`ProjectWorkspaceService.ts:172-175`). That is likely why its Blockers can say "fix M5 now" without saying which machine the user must act on, or that the reply came from linux-mini.
- For a coordinator whose execution was handed off, the label would still name the owner machine, since runs record no machine. I did not trace whether coordinators can be migrated.

## agent-instructions

Commit `0ec9cd9` (origin/main, November 19, 2026). Paths are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

**Answers:** No prompt tells an agent to name the machine in each user step. None tells it which machine it runs on. None says what to do when asked about another machine's problem.

**1. The coordinator never learns its own name.**
- `apps/server/src/provider/RuntimeInstructions.ts:283` runtime_info names only the harness, model and effort.
- `apps/server/src/project/ProjectWorkspaceService.ts:174` renders the local machine as "this machine". `:195` says `fleet` holds only the owner's other machines.
- `apps/server/src/project/currentTimeLine.ts:8` reads "Current local time on this machine:".
- The real label is only in `studio_machine_list` `local.label` (`apps/server/src/fleet/RemoteWorkers.ts:768`), and that tool's description starts "List the other machines" (`apps/server/src/mcp/toolkits/machines/tools.ts:16`).
- `studio_thread_list` labels the coordinator's own threads "This machine" (`apps/server/src/mcp/toolkits/orchestrator/federatedProjectThreads.ts:168`).

What the user sees: replies that say "this machine" or "here", with no name, in a window that may be served by another machine. Smallest fix: change the clock line, which is re-sent every turn (`ProjectWorkspaceService.ts:683-687`), to `Current local time on ${selfLabel}, the machine this coordinator runs on:`. Source `selfLabel` as at `RemoteWorkers.ts:768`. Do not put it in runtime_info. It is fixed when the session starts, and threads migrate.

**2. Blockers do not name a machine.**
- `RuntimeInstructions.ts:205`: "When you are blocked, end with a paragraph opening **Blockers:** that asks the one question, with the options and your recommendation."
- `ProjectWorkspaceService.ts:226`: "If the user must act, link the worker and say what is needed in one line, quoting errors exactly".
- The only machine-naming rule is about tool arguments, not user steps: "Name machines by their label, never by an id" (`:219`).

What the user sees: "fix M5 now ... press Continue in 'PS5 OBS'", with no "On M5:" in front of each step. Replace the end of `:226` with: "If the user must act, link the worker and give each step with the machine it is done on ("On M5: sign in to Codex in Settings > Providers"), quoting errors exactly." The concise block has about 38 characters to spare under its cap (`RuntimeInstructions.test.ts:388`, 1,300; the test comment says 1,262 is used). So a matching clause at `:205`, " Name the machine for each step (On M5: ...).", also needs that cap raised to about 1,350, and `:389` likewise.

**3. No rule covers another machine's problem.**
- Nothing in the role (`ProjectWorkspaceService.ts:202-252`) or in `StudioOrchestrationInstructions.ts:25` says that each machine runs its own coordinator.
- The only hint is in a tool error: "read that machine's coordinator" (`apps/server/src/mcp/threadNotFoundHint.ts:35`).
- The coordinator can act on M5 itself: `studio_thread_read/wait/send/interrupt {machine}` (`machines/tools.ts:16`). The retry is also its job by its own rules: "settle anything an agent can (... a retry ...)" (`RuntimeInstructions.ts:205`).

Add a line, gated on fleet like `:217`:
> "You are the coordinator on ${selfLabel}. Each of the owner's machines runs its own coordinator for this project, and the user may be reading you from a window served by another machine. Asked about a thread or failure on another machine, read it there with studio_thread_read {machine} and answer here, opening with that machine's label. Continue or retry it yourself with studio_thread_send {machine}. Leave the user only the step no agent can take, such as a sign-in, written "On <machine>: ...". A tool result or error that says "this machine" means the machine that wrote it; write that machine's label instead."

**4. Error text says "this machine", and coordinators must quote errors exactly.**
- `apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts:1214`: "...so press Continue once. If it fails again, sign in to Codex again in Settings > Providers on this machine."
- `RemoteWorkers.ts:394-397`: "On this machine (not on ${label}), the user opens Settings > Machines..."

These meet "quote errors exactly" (`RuntimeInstructions.ts:206`). An M5 error relayed by linux-mini then says "this machine", which now points at the wrong machine. Smallest fix: put the label in the text, `on ${machineLabel}` at `:1214` and `On ${selfLabel} (not on ${label})` at `:397`. Until then, the last sentence of item 3 covers it.

**5. Workers have the same gap.** They get no `fleet` (`ProjectWorkspaceService.ts:649`). Their role (`:253-263`) has no machine line, and a chat gets only `CHAT_CONTEXT_ROLE` (`:606`). Add a fleet-gated worker line: "The user may read your reply from another machine's window: write ${selfLabel}, never "this machine", in any step they must take."

**Verified in code:** all quotes and line numbers above. Also verified: the remote-worker wake text names the worker's machine ("Remote worker ... on ${machineLabel} finished", `apps/server/src/fleet/remoteWorkerMatching.ts:382`; "waiting on the user", `RemoteWorkerFollower.ts:140`). The coordinator had "M5" in front of it but no rule to carry it into Blockers.

**Guesses:**
- The reply paraphrased `CodexAdapterV2.ts:1214`. Its "press Continue once" matches.
- I did not confirm whether `studio-fleet.json` can list the local machine itself. `RemoteWorkers.ts:515` filters out the machine's own row, which suggests it can.
- I don't know whether "PS5 OBS" was this coordinator's worker or a chat owned by M5's coordinator.
- I don't know whether the coordinator's modes and grant on M5 would allow `studio_thread_send` there.

## cross-machine-routing

**Answer:** No. In the owner's case (one project linked on linux-mini and M5), coordinator A cannot hand a problem to M5's own coordinator. The only route is to start a new worker on M5, which M5's coordinator is never told about. Code read at origin/main `0ec9cd9`; paths are repo-relative.

**Verified in code**

1. **M5 refuses a send to its coordinator.** A can call `studio_thread_send {machine}` (`apps/server/src/mcp/toolkits/orchestrator/handlers.ts:284`, `remote.ts:378`). M5 then refuses any thread that is its own coordinator's (`apps/server/src/mcp/workGrantAccess.ts:297-310`), and a test asserts this (`workGrantAccess.test.ts:133-136`). Grants are on in production (`server.ts:1041`). The refusal says "Ask this machine's coordinator", which is the thing A just tried, so A falls back to Blockers that send the user to M5. Smallest fix: let a coordinator that is a member of the same linked project queue a message to the other copy's coordinator thread. Until then, reword the refusal to "Tell the user to open M5's coordinator."

2. **Where a send does go through, M5 labels it wrongly.** That is an unlinked project with a legacy grant (`workGrantAccess.ts:293`). A remote call has no calling thread, so no `senderThreadId` is stored and `createdBy` is "agent" (`apps/server/src/mcp/OrchestratorMcpService.ts:4595,4601`). M5 renders that as "Message from a worker" (`apps/web/src/studio/projectCoordinatorMessageDisplay.ts:96-98`). Fix: store the sending machine on the message and render "From linux-mini's coordinator".

3. **No other path exists.** `studio_project_route` is for personal assistants only, on the same machine (`apps/server/src/mcp/toolkits/project/tools.ts:559`, `ProjectWorkspaceService.ts:238`). `LinkedPeerRoute` only syncs content, plans, memory and members (`LinkedPeerRoute.ts:1-12`).

4. **A worker A starts on M5 is labelled only on M5.**
   - On M5 the thread shows the "From <app> · linux-mini" badge (`ThreadOriginBadge.tsx:14-18`, `ChatHeader.tsx:399`, `ProjectThreadHeader.tsx:274`). M5's coordinator is not woken: threads another machine started have no launcher there (`LaunchedWorkerWake.ts:9-11`).
   - On A, the agent's wake text names the machine (`RemoteWorkerFollower.ts:442,454`). The "re: <title> ↗" chip shows the title only (`CoordinatorReplySources.tsx:40-41`), so a worker on M5 looks the same as a local one.
   - Fix: append " · {machine}" to the chip when `source.environmentId` is not the project's own.

5. **A local worker that investigates M5 is not labelled.**
   - `delegate_task` always runs on A (`remote.ts:451-458`), and the coordinator prompt sends work there by default (`ProjectWorkspaceService.ts:206`).
   - Nothing records which machine the work is about. Only a title the model happens to write would say M5.
   - Fix: add one prompt line: "Work about another machine: launch it there with `studio_thread_launch {machine}`, or name that machine in the title."
   - A launch without `machine` goes to the project's configured worker machines, not to the machine that has the problem (`remoteLaunch.ts:151-190`).

6. **Blockers never have to name a machine.** Neither the Blockers rule (`apps/server/src/provider/RuntimeInstructions.ts:205`), the coordinator lines (`ProjectWorkspaceService.ts:219-226`) nor `StudioOrchestrationInstructions.ts:25` ask for it. That is how "fix M5 now ... press Continue in 'PS5 OBS'" reached the owner without saying where to act. Fix: "When the step is on another machine, start it with that machine's label ('On M5: ...') and link its thread."

**Leftover single-coordinator text (verified)**

- **Link dialog copy, still shown.** `apps/web/src/components/studio/ProjectLinkDialog.tsx` lines 431, 434, 446, 621, 787 and 792-793 say the joining coordinator "stops" or "becomes read-only history" and that the kept one "can start work on both machines". This contradicts `ProjectLink.ts:689`, where the joining copy keeps its own coordinator. It teaches the owner there is one main coordinator. Fix: rewrite it to "each machine keeps its coordinator".
- **Agent hint.** `apps/server/src/mcp/threadNotFoundHint.ts:35` tells agents that "a linked copy usually leaves coordinating to another machine". Fix: drop that sentence.

**Guesses (not verified)**

- `projectRouting.ts:66,106` ("coordinator moved to another machine") looks dead. `projectCoordinatorIsFenced` (`packages/contracts/src/logicalProject.ts:205-214`) needs a non-active binding, and the migration makes every binding active (`EqualCoordinatorMigration.ts:8-14`).
- The epoch fence is still live code: `workGrantAccess.ts:246-266` ("Another machine now coordinates…"), the `studio_coordinator_claim_epoch` relay (`RemoteStudioMcpClient.ts:71-72`) and the takeover adoption in `AwayIntents.ts`. `EqualCoordinatorMigration` never mentions `WorkerEpochStore`, so a claim left over from before 1390 may still block a coordinator from steering. I did not trace whether that can happen.
- Not traced: how linux-mini learned about M5's `token_expired`, and whether `studio_thread_migrate` would have let A continue "PS5 OBS" itself.

## action-surfaces

Root `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`, origin/main `0ec9cd96`.

**Verified in code**

1. **Desktop notifications and toasts never name a machine.** `apps/web/src/components/ThreadNotificationCoordinator.tsx:716-739`: the title is the thread name and the body is something like "Sign in to continue" or "Stopped with an error". The toast at 565-585 and 673-674 shows "Sign-in needed" plus the thread title. The comment at 610-613 says a remote worker's notification goes to the coordinator machine that launched it, so a "PS5 OBS" alert pops on linux-mini while the fix is on M5. Fix: append the thread machine's nickname (`executionMachineId ?? environmentId`, already resolved at `apps/web/src/components/studio/CoordinatorConversation.tsx:339`), for example "Sign in to continue on M5".

2. **Phone push has no machine field.** `packages/contracts/src/relay.ts:182-213` carries project, thread and model only. `infra/relay/src/agentActivity/agentActivityAlerts.ts:120` builds "<thread>" / "<status>: <project>". The phone is never the machine to act on, so this is always ambiguous. Fix: add an optional `machineLabel` to both schemas and render "<status> on M5".

3. **Access cards say "this machine" without naming it.** `apps/web/src/components/chat/AccessRequestCard.tsx:316` says "Always allow on this machine" and 375 says "on that Mac". App subjects get no `hostLabel` (`apps/server/src/access/accessGate.ts:83-89`); only remote devices do (112). iOS `apps/ios/SWCKit/Sources/Weave/Components/AccessRequestCard.swift:27,51,71` shows "Always on this machine" on a phone, where it cannot mean the device in hand. Fix: pass the thread machine's nickname and show "Always allow on M5" (always on iOS).

4. **Reply provenance names threads, not machines.** `apps/web/src/components/studio/CoordinatorReplySources.tsx:21-43` renders "re: <title> ↗" even though `source.environmentId` is available. `apps/web/src/components/ThreadLinkChip.tsx:124-131` names a machine only when the thread is unreachable. Every coordinator message carries the coordinator's own machine (`CoordinatorConversation.tsx:323,364`, `apps/web/src/studio/projectDomain.ts:326-341`), so "linux-mini · Claude Code · Opus 5.5" sits beside an M5 problem and reads as the source of it. Fix: when the source machine differs from the one being viewed, add its `MachineMark` (`apps/web/src/components/studio/OverviewRows.tsx:124`), giving "re: PS5 OBS · M5 ↗".

5. **The switcher never marks the window's own machine.** `apps/web/src/components/studio/OrchestratorSwitcher.tsx:124-127` ("No row names a role") and the rows at 386 show names only. Fix: put a "this window" pill on the serving machine's row, and show "viewing from M5" beside the header chip when the two differ.

6. **Question and approval cards name who asks, not where.** `apps/web/src/studio/coordinatorQuestionAnswers.ts:15,24-26` with `apps/web/src/components/chat/ComposerPendingUserInputPanel.tsx:458` give "Coordinator asks" or "<thread> asks". `apps/web/src/components/chat/ComposerPendingApprovalPanel.tsx:21-30,61` gives "Command approval", and iOS `ApprovalCard.swift:65` gives "Approval needed". Inside a thread view the header row does show the thread's machine (`apps/web/src/components/ChatView.tsx:15811-15813`; `apps/web/src/components/chat/threadMachine.ts:137` returns null only when there is no environment), but the card itself does not. Fix: when `threadMachine.isThisMachine === false`, add "on M5" in the machine's colour to the card header.

7. **Thread recovery buttons are bare.** In `apps/web/src/components/chat/ThreadErrorBanner.tsx:143-145` the title names the machine ("Codex sign-in expired on M5", via `FailureRecovery.tsx:29-34` and `ChatView.tsx:10512-10514`). The buttons at 189-200 just say "Sign in again" and "Continue", and `FailureRecovery.tsx:102` names the machine only in a tooltip. `ProviderStatusBanner.tsx:109-113` says "Codex is unauthenticated" and line 75 says "on this environment". The server text at `apps/server/src/provider/Drivers/CodexManagedProvider.ts:40` has no machine. Fix: "Sign in again on M5", and use the nickname in place of "this environment".

8. **Blockers rule.** `apps/server/src/provider/RuntimeInstructions.ts:205` says nothing about machines. In this case the model happened to name M5, but not that "PS5 OBS" lives on M5. Fix: require the machine for each step. I did not read the coordinator role prompt.

9. **Worker questions.** `packages/client-runtime/src/state/projectAttention.ts:146-155`: a coordinator's workers ask the person on their own thread, so their card sits on M5 and is reached through the machine-less alerts in item 1.

The following already name the machine:
- the coordinator fix button (`apps/web/src/studio/coordinatorFailure.ts:164-172`)
- handoff (`apps/web/src/components/handoff/HandOffMachineDialog.tsx:205,232`)
- sync (`apps/web/src/components/studio/ProjectSyncDialog.tsx:916-928`)
- server update (`apps/web/src/components/ServerUpdateAction.tsx:268-269`)
- the coordinator's access-waiting line (`apps/web/src/studio/accessWaiting.ts:38-46`), which falls back to "this computer" at 45

None of the cards in items 3, 6 and 7 use `machineColorProps`, so the machine never stands out from the window's own.

**Guesses**

- A `token_expired` run failure probably alerts as "Thread failed", not "Sign-in needed". "signin" comes only from a pending sign-in request (`projectAttention.ts:192`).
- `accessGate.ts:112` uses `device.hostId`, which may be a raw ID rather than a nickname. Not checked.
- The sidebar's "Update now" / "Restart to update" (`apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts:363,396`) says "this machine". I did not trace which machine it updates while another coordinator is shown.
- The sign-in banner takes its machine from `environmentId`, not `executionMachineId`, so on a copy left behind by a handoff it may name the old host.

**Not checked:** `UsageLimitRecoveryBanner`, `LimitHandoffCandidates`, `AwayAccessRequests`, `ComputerUsePermissions`, the `ProviderUpdate*` notifications, `MessagesTimeline.tsx:4637`, any `auth_refresh` request card, and Android.
