# Offline thread banner offers a machine chooser and knows when work is bound to one machine

Repo: `anton-abyzov/specwithcode` (checkout `repositories/anton-abyzov/specwithcode`). Code was read on `origin/main` `42dafc536` (November 23, 2026), not on the checked-out branch. Plan only: nothing is built yet.

## Problem

Anton, November 23, 2026, about the banner on a thread whose machine is offline (`reports/screens/banner-today.png`). The thread "Sweep idle threads, finish un..." runs on m1, m1 is offline, and the banner reads "m1 is offline · Last answered 11m ago · Retrying by itself" with [Continue on m4] [Retry] [Disconnect server]. The thread's report ends with two steps for him, both starting "On m4:" (free about 35 GB of disk, or connect an SSD).

His ideas:

> "Maybe it's good to have 'Continue on another device,' but why do we have the predefined option?"
> "Maybe if we have M5 available or others, there is a beautiful way to visualize it."
> "This kind of task: maybe a few threads could be related."
> "I'll stick to just a machine, for example, cleaning up the disk on one machine, and it doesn't make sense to move it to other machines."
> "Maybe you should warn the user that it might not make sense to move it, or maybe when you're 100% sure, just don't show this button at all."
> "Maybe leave in a short message or something like a tooltip on hover."

## Findings

**1. One machine is offered because the picker returns the first that passes its checks.** `pickContinueTarget` (`apps/web/src/components/chat/deviceHandoff.ts:92`) walks the candidates in order and returns the first one (`:100`) that is not the source, is connected, lets this window start threads, has the project (or is a chat without a project), and has a subscription sign-in able to take a turn (`pickDeviceModel`, `:41`). The banner renders that single result as "Continue on {label}" (`apps/web/src/components/ChatView.tsx:3736-3800`, button at `:3905-3932`).

**2. The order is "this window's machine first, then by name", nothing about the work.** For a project thread the candidates are the machines that hold the project, sorted primary first and then by label (`apps/web/src/components/chat/logicalProjectEnvironments.ts:88-89`). For a chat without a project they are the machines with a chat folder, in the same order (`ChatView.tsx:3766-3774`). The picker does not look at what the thread does, what it waits for, how busy the machine is, or what else could take it. Which of the two rules made it m4 in the screenshot is not known, because the capture does not say which machine's window it is.

**3. "Continue" is a new thread from a summary, not a move.** `continueOnDevice` (`ChatView.tsx:10606-10693`) writes a text handoff of the conversation (first message plus the latest eight, 12,000 characters, `deviceHandoff.ts:24`, `:138`). For a project thread it stages that text in the destination's coordinator for the user to send (`apps/web/src/components/chat/coordinatorDeviceHandoff.ts`). For a chat without a project it starts a new chat. The original stays on the offline machine and can resume when that machine returns. The banner says none of this. A tooltip on the button says "Start a new chat on m4 (model) from a summary of this one".

**4. A real move cannot run while the source is offline.** The move a thread's menu and its "Runs on m1" chip offer (`apps/web/src/components/chat/ThreadMachineComposerChip.tsx`, "Move to {machine}") runs on the source machine. The destination refuses to take a thread from a silent source: "has not answered, so it may still be running this thread" (`apps/server/src/handoff/HandoffTransferRunner.ts:1354`), and silence never starts a handoff (`apps/server/src/handoff/HandoffAutoContinue.ts:4`, 1390 AC-36). So the banner's button is the only way forward while the machine is down, and no other control can stand in for it.

**5. The link between the two threads lives on one device.** `recordChatContinuation` keeps it in this browser's local storage (`apps/web/src/lib/chatContinuations.ts:12`, at most 200 links). No server knows. Another window can continue the same thread again, and a thread that waits for the original never learns of the copy.

**6. Signals for "this work belongs to one machine" exist, but only as cached data.** The source is offline, so the verdict can only use what the window already holds: each machine's thread list and every thread this window has opened are stored on the device (`apps/web/src/connection/storage.ts:823`). A new server field could not help, because the offline machine cannot be asked or updated.

| Signal | Where it is | Held while the source is offline |
|---|---|---|
| The report's steps name a machine ("On m4: ...") | Agents are told to write steps this way (`apps/server/src/provider/RuntimeInstructions.ts:205`, `apps/server/src/project/ProjectWorkspaceService.ts:200`, `:213`). The text is in the last assistant message and, clipped to 400 characters with list numbers stripped, in `reportedBlocker` (`packages/contracts/src/orchestrationV2.ts:2456`, `packages/shared/src/reportDocument.ts:304`, `:310`) | Yes |
| The thread waits for the user, not for the machine | `reportedBlocker`, `reportedWait` (`orchestrationV2.ts:2456`, `:2458`) | Yes |
| The thread drove the machine's screen or a device | `toolSurface: "computer"` on turn items (`orchestrationV2.ts:1773`), `access_request` items | Yes, for an opened thread |
| The thread ran commands on the machine itself (disks, services, system folders) | `command_execution.input` turn items | Yes, for an opened thread |
| A personal assistant's chat | `isPersonalAssistantProject` (already makes Move "private", `ChatView.tsx:5096-5102`) | Yes |
| The machine's own project coordinator | `workspaceSettings.coordinatorThreadId` (`ChatView.tsx:3098`) | Yes |
| A subagent the provider spawned inside another thread's run | `isProviderNativeSubagentThread` (`orchestrationV2.ts:574-577`): the subagent relation with `creationSource: "provider"`. A `delegate_task` thread has the same relation with `creationSource: "mcp"`, takes messages, and is an ordinary worker | Yes |
| Which machines hold the project | `buildLogicalProjectEnvironments` | Yes |
| Files the source had not committed or pushed | `projectSync.status` is asked of each machine and kept in memory for 60 s (`apps/web/src/studio/projectSync.ts:146`, `:166`) | No |
| A launch that required a kind of machine (`needs`) | Used at launch only, not kept on the thread | No |

Nothing parses "On {machine}:" today: no function maps a step to a machine.

**7. The banner's own code does not exclude a coordinator, an assistant chat or a provider's subagent.** `continueElsewhereTarget` checks only that the thread was sent and its machine is down (`ChatView.tsx:3736-3749`). Whether such a thread ever has a candidate machine was not traced (an assistant project may have none). For m1's coordinator it would stage m1's conversation in another machine's coordinator, which the November 19 decision rules out ("Continue the coordinator here" is not to come back, `decision_sync_and_hand_off`). T-01 pins this with a test before changing it.

**8. Related threads are on record, with no list of them.** The cached thread lists carry `lineage` (parent, root), `origin.parentThreadRef` (`orchestrationV2.ts:437`), `pendingBackgroundTasks[].childThreadId` (`:2464`), `activeWork.waitThreadId` (`:2426`), `movedTo`/`movedFrom` (`:2521`), and messages carry `studio://thread/` links (`packages/shared/src/studioThreadLinks.ts`). The screenshot shows both kinds: "Message from coordinator" and a link to "Finish MatchCam GPU pricing and upload decision".

**9. The screenshot, read with these facts.** The thread is on m1. It is blocked on Anton, and both steps are on m4. Continuing on m4 would start a new thread that still cannot free the disk for him, though a thread on m4 is the only one that could look at m4's disk. Continuing on M5 makes no sense at all. Today's button named m4 by sort order, not because the step is there.

## Scope

In: the banner's "Continue on…" button and its chooser; the per-machine state in the chooser; a verdict on where the thread's work belongs, computed in the window from cached data; the warning mark and hover note; no button for threads that are structurally bound; a related-threads list in the chooser with the notes that follow from relations; phrases in the eight catalogs; a headless fixture with captures.

Out: a real move while the source is offline (finding 4, and the new handoff is held under 1390); moving several threads at once; telling a waiting parent thread about the copy, or keeping the link on a server (finding 5); any server or contract change; the usage-limit banner's own device button (`UsageLimitRecoveryBanner.tsx`), which keeps `pickContinueTarget`; adding the project to a machine from the chooser; the "Runs on" chip and Move thread; phone apps; a user-set "keep on this machine" pin and keeping a launch's `needs` on the thread (follow-up, D-10).

## Acceptance Criteria

- [ ] AC-01: The banner's button reads "Continue on…" and never names a machine. Pressing it opens the chooser. It shows under the same conditions as today's button (the thread was sent, its machine is down past the reconnect grace, it has not already continued) and only when at least one machine can take the thread.
- [ ] AC-02: The chooser lists every machine that holds the project, or every machine with a chat folder for a chat without a project. The source is the first row, not pressable: "{source} · Offline · last answered {age}" and "This thread stays here and may resume when {source} is back." Each other row shows the machine's colour and name, "This window" on the window's own machine, and one state from this list: "Ready · {n} running" with the model it would use, "Offline · last answered {age}", "Reconnecting", "No model ready", "Can't start threads there". Only Ready rows can be pressed, and the others are greyed with their state as the reason. A Ready machine on another version stays pressable, as today, and adds "other version" to its line.
- [ ] AC-03: When the verdict carries no warning, one Ready row is marked "Suggested", listed first and focused when the chooser opens. It is the work's home machine when the verdict names one that is Ready (AC-06), else the window's own machine, else the first Ready machine by name. The other Ready rows follow by name, then the rows that are not Ready. When the verdict warns (AC-08, AC-13) no row is suggested: the rows keep the same order (window's machine first) and the first line of the chooser has the focus.
- [ ] AC-04: Pressing a Ready row continues exactly as today's button does for that machine and its model (staged in the destination's coordinator for a project thread, a new chat for a chat without a project), including the "Continued on {machine}" state and "Open on {machine}" afterwards. The chooser's last line says what will happen: "Starts a new thread on the machine you pick, from a summary of this one. Changes {source} had not pushed are not carried." Machines of the fleet that lack the project are named in the same line ("Not on: {names}") and cannot be picked.
- [ ] AC-05: A pure function returns the verdict `{home, level, reasons}` with `level` none, likely or certain, from the cached thread list entry and the cached thread alone. It makes no request. A missing field, a thread never opened in this window, or a source on any older version gives fewer signals and never a warning that today's data does not support.
- [ ] AC-06: Steps that name a machine set the home, only while the thread reports a blocker (`reportedBlocker` is set) and only inside the report's Blockers part. A step counts when a sentence or list item of that part starts with "On {name}:" or "Or on {name}:" (also "On the {name}:"), where {name} is a fleet machine's name, nickname or short label, matched as a whole word without regard to case. The Blockers part of the last assistant message is read when the thread is cached, to get past the 400-character clip, and `reportedBlocker` otherwise. A machine named anywhere else in a report ("On m4: I installed both slots") sets nothing. When every counted step names the same machine, that machine is the home at level likely. Steps naming different machines, or none, set no home.
- [ ] AC-07: The screenshot is a fixture: a thread on m1 (offline) whose report ends "1. On m4: free about 35 GB ... 2. Or on m4: connect an SSD ...", in a project on m1, m4 and M5. Outcome: the button shows without a warning mark; the chooser opens with the line "Waiting for your step on m4: {first step, clipped}. A new thread does not do that step for you."; m4 is Suggested with "The next step is here"; M5 stays pressable and carries "The next step is on m4, not here" in the warning tone. The same holds when only the clipped `reportedBlocker` text is available.
- [ ] AC-08: When the home is the offline source at level likely, the button keeps its place and gains a warning mark, the list heading reads "Continue anyway on", and the chooser's first line names the reason in the warning tone. The reasons, each with its own sentence: every step names the source ("its next step is on {source} itself"); the thread drove the source's screen or a device ("it used {source}'s screen"); two or more of its last 50 commands act on the machine itself ("it worked on {source}'s own disk and services"). The list starts with these and is tested by example: `diskutil`, `df`, `du` on a path outside the project folder, `tmutil`, `launchctl`, `systemctl`, `brew`, `apt`, `dnf`, `softwareupdate`, `docker system prune`, `xcrun simctl`, and any command whose target is under `/Volumes`, `/Library`, `~/Library`, `/srv`, `/etc` or `/var`.
- [ ] AC-09: A thread that waits for the user with no machine named (`reportedBlocker` or `reportedWait` set, no counted step) gets no warning mark. Its chooser opens with "This thread waits for your answer, not for {source}. What you type is kept and sent when {source} is back."
- [ ] AC-10: The button is not shown at level certain, which only facts about the thread itself can give: a personal assistant's chat, the source machine's own project coordinator, or a subagent the provider spawned inside another thread's run (`isProviderNativeSubagentThread`, which cannot take messages). A thread started with `delegate_task` is an ordinary worker and keeps the button. In its place the banner shows "Stays on {source}" as plain text with a note saying which of the three applies. Text signals (AC-06, AC-08) never reach level certain.
- [ ] AC-11: The warning mark and "Stays on {source}" carry a one-sentence note on hover and on keyboard focus, and the same sentence is the chooser's first line, so touch needs no hover. The note names the machine and the reason and is at most 140 characters in English.
- [ ] AC-12: The chooser lists related threads under "Related threads", at most five and then "{n} more": the thread that started this one, threads it started, a thread it waits for or that waits for it, threads its last report links to, and a thread it continued from or as. Each line has the relation in a word or two, the title, and the machine with its colour and state (Running, Waiting for you, Offline, Done). Pressing a line opens that thread. Nothing in the list is moved or continued with this thread.
- [ ] AC-13: Relations change the first line of the chooser when they make continuing pointless or lossy: the thread that started this one is on another machine, named by `origin.parentThreadRef`, and has not finished ("'{title}' on {machine} started this thread. A new thread does not report back to it."), or this thread waits for one that is running on a reachable machine ("Waits for '{title}' on {machine}, which is still running."). `childThreadId` and `waitThreadId` are ids without a machine, so they are resolved on the thread's own machine first and give a note only when exactly one cached thread matches. These are notes at level likely with no home, and the button gains the warning mark.
- [ ] AC-14: When several first lines apply, one shows, in this order: started by a thread on another machine, waits for another thread, home is the source, home is another machine, waits for the user. The other reasons stay in the hover note's accessible description.
- [ ] AC-15: Nothing changes for the usage-limit banner, the "Runs on" chip, Move thread, the composer's "Waiting for {source}" text, Retry or Disconnect server. No server, contract or stored-data change ships. `ChatView.tsx` ends shorter than it starts: the banner's actions and the continue target move to their own modules.
- [ ] AC-16: Every new phrase exists in the eight catalogs, and headless captures of the five states in the mockup (today for reference, free, home elsewhere, likely bound, certainly bound), light and dark, at 390 px and desktop width, are in `reports/screens/`.

## Approach

Mockup: `reports/mockup-continue-chooser.html` (today, then states A to D and the level table).

**Rows (web, pure).** A new `continueChoices.ts` beside `deviceHandoff.ts` turns the same candidates the banner builds today into rows: reach from the existing reach state (`packages/client-runtime/src/connection/reach.ts:35`), the model from `pickDeviceModel`, the operate scope, and a running count from the cached thread lists. It reuses the words of `machineStatus.ts` and `machineRowState.ts`, so a machine reads the same here as in the machine menu. `pickContinueTarget` stays for the usage-limit banner.

**Verdict (shared and web, pure).** `packages/shared/src/machineSteps.ts` finds the steps and their machine names in a report or a clipped blocker. `threadMachineHome.ts` combines steps, turn-item signals and the structural facts into `{home, level, reasons}`. The command list is a small fixed table in that module, tested by example, and it can only raise the level to likely.

**Relations (web, pure).** `relatedThreads.ts` collects the links of finding 8 from the cached thread lists of all connected and cached machines, dedupes by machine and thread, and orders them by relation. It also yields the two notes of AC-13.

**Chooser (web).** `ContinueOnChooser.tsx` renders rows, the first line, the related list and the last line in the existing menu and tooltip components. `EnvironmentUnavailableActions.tsx` takes the banner's buttons out of `ChatView.tsx` (16,703 lines against the 1,500-line rule, so new code goes in new modules and the file shrinks). `ChatView` passes the thread, the candidates and `continueElsewhereRef`.

**Mixed versions.** Everything reads optional fields that exist today. The offline machine's version does not matter.

Rejected:
- Keep the named button and add a second "Other machines" menu. The first click would still act on a machine chosen by sort order, which is the complaint.
- A server field for "bound to this machine". The machine that would have to supply it is the one that is offline. It is worth adding later for launches with `needs` and for a user pin (D-10), as one more input to the same verdict.
- Ask a model whether the work is machine-bound. It costs a turn on another machine for a hint the report's own steps already give, and its answer could not be tested.
- Hide the button on text signals. A step that says "On m1:" is strong evidence and still text; a wrong reading would remove the only way forward (finding 4).
- Continue related threads together. One staged coordinator message per continuation, a device-local link and an original that may resume (findings 3 and 5) make a group copy easy to duplicate and hard to follow.
- Show how the destination's files differ from the source's. That fact is in memory for 60 s and unknown once the source is down, so the last line states the limit in words instead.

Risks: a machine name that is also a common word in a report ("mini") could count as a step; the match needs the "On {name}:" form at the start of a sentence or item, and it can only warn. The running count comes from cached lists and can lag. A second device can still continue the same thread (finding 5, out of scope, said in the chooser's source row).

## Decisions

### Asked
- D-03 When to hide the button → only on facts about the thread itself (assistant chat, coordinator, a provider's own subagent); steps and tool use warn and never hide, because this button is the only way forward while the machine is down (Anton, November 23, 2026: "The best approach you recommend").
- D-04 The screenshot's case → the button stays, with m4 suggested and a note on M5; the fixture is a `delegate_task` worker thread (Anton, November 23, 2026: "Yes, also go with recommended").

### Defaulted (change any before sw-do)
- D-01 Button label → "Continue on…", never a machine name, even when one machine can take it; the chooser then has one Ready row (reversible).
- D-02 Suggested row → the work's home, else the window's machine, else first by name. The window's machine is where the person sits; no "least busy" ranking (reversible).
- D-05 Verdict → computed in the window from cached data, no model call, no server field (reversible).
- D-06 Related threads → listed with machine and state, opened by a press, never continued together (reversible).
- D-07 No files comparison in the rows; one sentence says unpushed changes are not carried (reversible).
- D-08 Machines without the project → named in the last line, no Add action in the chooser (reversible).
- D-09 The usage-limit banner keeps its own device button; it can adopt the chooser later (reversible).
- D-10 A "keep on this machine" pin and a launch's `needs` kept on the thread → a follow-up increment, since both need a server field and both machines updated (reversible).
- D-11 A coordinator's thread stops offering Continue (finding 7), following the November 19 rule that coordinators are not continued elsewhere (reversible).

### Open
- none

## Tasks

### T-01 Pin today's behaviour, then move the banner actions out of ChatView
- AC: AC-15 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/EnvironmentUnavailableActions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/EnvironmentUnavailableActions.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/deviceHandoff.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/chat/EnvironmentUnavailableActions.test.tsx src/components/chat/deviceHandoff.test.ts

The tests first record what the banner offers today for a `delegate_task` worker thread, a coordinator, an assistant chat and a provider's subagent (finding 7), then the move keeps them green.

### T-02 Find machine-named steps in a report
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/machineSteps.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/machineSteps.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && npx vp test run src/machineSteps.test.ts

Fixtures: the screenshot's report in full and as `reportBlocker` returns it; "Or on m4:"; "On the M4:"; a nickname; mixed machines; a machine name inside a sentence (no step); a report with no steps.

### T-03 Verdict on where the work belongs
- AC: AC-05, AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/threadMachineHome.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/threadMachineHome.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/chat/threadMachineHome.test.ts

### T-04 Chooser rows and the suggested machine
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/continueChoices.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/continueChoices.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/chat/continueChoices.test.ts

### T-05 Related threads and their notes
- AC: AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/relatedThreads.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/relatedThreads.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/chat/relatedThreads.test.ts

### T-06 The chooser, the warning mark and "Stays on {source}" in the banner
- AC: AC-01, AC-04, AC-07, AC-10, AC-11, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ContinueOnChooser.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ContinueOnChooser.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/EnvironmentUnavailableActions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/EnvironmentUnavailableActions.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/chat/ContinueOnChooser.test.tsx src/components/chat/EnvironmentUnavailableActions.test.tsx

### T-07 Phrases in eight catalogs, fixture and captures
- AC: AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/continue-chooser/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/continue-chooser/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/continue-chooser/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && (cd apps/web && npx vp test run src/i18n/i18n.test.ts) && npx vp build --config apps/web/tests/continue-chooser/vite.config.ts && node apps/web/tests/continue-chooser/verify.mjs /Users/anton/Projects/github/specweave-umb/.specweave/increments/1442-offline-thread-banner-offers-a-machine-chooser-and-knows-when-work-is-bound-to-one-machine/reports/screens

### T-08 Check on the released build, verify and close
- AC: AC-01, AC-07, AC-10 | Files: .specweave/increments/1442-offline-thread-banner-offers-a-machine-chooser-and-knows-when-work-is-bound-to-one-machine/reports/live-check.md | Test: test -s .specweave/increments/1442-offline-thread-banner-offers-a-machine-chooser-and-knows-when-work-is-bound-to-one-machine/reports/live-check.md && specweave verify 1442-offline-thread-banner-offers-a-machine-chooser-and-knows-when-work-is-bound-to-one-machine

`live-check.md` is written on M5 with the released build and one machine switched off: a worker thread with no signal, a thread whose report names another machine, a thread that drove the offline machine's screen, and that machine's coordinator, with a capture of the banner and the chooser for each.
