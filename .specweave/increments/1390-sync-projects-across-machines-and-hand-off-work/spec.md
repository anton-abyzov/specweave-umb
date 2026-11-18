# 1390 Sync projects across machines and hand off work, without Main and Copy

Status: design only. Nothing is built until Anton accepts (this changes data flow between machines). Mockup: `reports/mockup.html`.

## Problem

Anton, November 18, 2026, on the M5 at 1.0.345 (screenshots in `~/.specwithcode/m4/userdata/attachments/`, ids `a03d1d32`, `dd5964b4`, `d6b192bf`):

> "Rethink this concept of main and non-main copy [...] the main motivation was that we could identify all unfinished work and effectively hand it off to another machine. When you are going to close your laptop [...] or when your tokens are about to run out [...] maybe it's just for one or two threads, and it wants to automatically proceed and do this on another machine."
>
> "If you copy the project, you should be able to proceed there on that server. I don't think we need to call it 'make M5 main.' I think this is wrong. The whole idea is about having maybe synchronization in files [...] the preferred way is just to pull all the latest changes. It could be that a new repository was introduced, and that's why copy is good."
>
> "On M5, when I try to click on M5, it's either not working, or it's selecting M4 intentionally, which is weird. If we cannot switch to M5, we should gray it out."

What is wrong, with evidence:

1. **The interface answers a question nobody asked.** Every row carries a role ("Main", "Copy · main on m4") and the only way to work from another machine is "Make M5 main". His goals are different: bring the files up to date, continue work there, and take unfinished work along. The role exists to keep one writer for the coordinator, the plan and memory. That is an internal need, and it leaked into every label.
2. **The chip and the rows mislead.** On the M5 the chip says "Runs on m4" after he picked M5, the notice says "Main for specweave is m4. This copy takes work from there", and the button says "Send to m4". The click did switch the page to the M5's copy. The chip then names the coordinator's machine on purpose (`composerMachines`, `apps/web/src/studio/routeToMain.ts:26`), while the menu it opens is titled "View this project on". No row is ever disabled (`MenuRadioItem` has no `disabled`, `OrchestratorSwitcher.tsx:321`): a machine this window never opened is pressable and leads to a page titled "{machine}'s orchestrator: Unknown".
3. **One entry hides two jobs.** "Send to another machine…" is used both to put a project on a machine that lacks it and to update one that has it. His preferred path for the second is `git pull`, with a clone for a repository that is new. A "Sync {project} to {machine}" mode exists in the dialog (`MachineHandoffDialog.tsx:286`), but nothing opens it. The only path that pulls on the destination is "Git only", and that one always moves Main.
4. **Five entries move work and none moves all of it.** From the M5 thread's report (`.specweave/reports/threads/2026-11-18-how-one-project-runs-across-machines-d53e8d-35b8ae.md`): Make main moves the coordinator and refuses while a thread runs; Leave this machine moves running and queued threads but not threads in a worktree set, not idle threads with unsaved work, and only the coordinator's role; Move running threads lists only threads with "Keep ready to move" on, which is off by default; Move thread moves one. In specweave all 35 unarchived worktree threads on the M4 are worktree sets, so Leave this machine moves none of them.
5. **The automatic paths exist but are off and scattered.** A usage-limit hand off (0968) and a lid-close hand off (1267) are built. Their settings sit under three names (Handoff mode, Away target, provider limit action), and neither warns when the target uses the same provider account, where moving adds no usage.
6. **Real machines are not clean.** On November 18 the M4 had 179 uncommitted umbrella files, 11 umbrella branches with commits on no remote, an untracked `.specweave/project/credentials.json`, three worktrees whose Git data is gone, and repositories 2 to 99 commits behind (`~/.specwithcode/m4/evidence/m4-git-state/2026-11-18-m4-git-state.md`). Any flow that assumes a clean, pushed checkout either refuses or strands that work.
7. **A second coordinator reads as a healthy copy.** m1 holds an old coordinator record (epoch 2, active, no predecessor, left by "Start a coordinator here"). A copy with a live coordinator of its own has the role `also-main` and wears the same badge as a plain copy, "Copy · main on m4" (`apps/web/src/studio/workersOnlyCopy.ts:59`), so nothing tells him it needs a fix. The only Unlink control is in project settings (`ProjectMachinesSettings.tsx:525`).

Facts checked on `origin/main` of `repositories/anton-abyzov/specwithcode` at `af7b77f05` (1.0.346):

- Roles come from `orchestratorCopies` (`apps/web/src/studio/projectCoordinatorMachine.ts`) and `copyRoles` (`apps/web/src/studio/projectDomain.ts:255`): main, also-main, moving, copy, independent. The menu is `apps/web/src/components/studio/OrchestratorSwitcher.tsx` (chip text at line 154, groups at 263 to 443). A row click navigates this window to `/projects/$projectKey?checkout=env:id` and reads that machine's server; it never opens the other machine's app.
- A message typed on a copy already goes to the coordinator's machine: `apps/web/src/components/studio/useRouteToMain.ts` calls `projects.coordinatorSend` there and then opens that machine's page.
- "Make X main" is web policy over existing server calls: an online move through the machine handoff with `transport: "git-sync"` (`packages/contracts/src/machineHandoff.ts:63`, `apps/server/src/fleet/MachineHandoff.ts:1343` to 1410, which checks and fast-forwards the existing copy and refuses with `staleCopy: "refuse"`), or `projectLink.takeover` after `TAKEOVER_UNREACHABLE_MS` = 10 minutes (`apps/web/src/studio/projectLink.ts:113`). Takeover claims the new epoch on member machines (`apps/server/src/project/takeoverEpochClaims.ts`).
- The folder copy already classifies each repository as `same`, `fast-forward`, `ahead`, `diverged`, `dirty`, `conflict`, `new`, `only-here` or `skipped` (`packages/contracts/src/folderCopy.ts:397`), plans each one without losing a commit (`apps/server/src/fleet/folderTransfer/reconcile.ts:450` to 480: same, fast-forward, keep, import the other side's branches as `swc/from-{machine}/…`), and applies a fast-forward with `git merge --ff-only` (`apps/server/src/fleet/folderTransfer/apply.ts:823`).
- A thread hand off carries a hidden checkpoint commit under `refs/specwithcode/handoff/`, never a branch, with limits of 10 MB per file, 20,000 files and a 64 MB bundle (`packages/contracts/src/handoffMode.ts:35` to 44). A worktree set is refused (`WORKTREE_SET_HANDOFF_MESSAGE`, `apps/server/src/handoff/HandoffMoves.ts:26`).
- Defaults: `defaultMode: "off"`, `sleepTarget: null`, `autoTakeoverMinutes: 0` (`handoffMode.ts:90`). Away's coordinator scope defaults to `live` (`apps/server/src/away/AwayPlanner.ts:758`).
- The limit hand off moves a thread only at a real boundary (stopped on the limit, or idle at the threshold within 10 minutes of its last turn), only when the project rule is `switch` with machine targets, and never a review delegation (`apps/server/src/orchestration-v2/MachineLimitHandoff.ts:188` to 232 and 417).

## Scope

In:

- New words everywhere a person or an agent reads them: machine menu, chip, message box, dialogs, Settings, thread menu, limit banner, command palette, tray and File menu, slash commands, iOS, translations and MCP tool descriptions. The table is in Wording.
- A machine menu whose rows say what is true (coordinator here, sync state, offline, cannot open, old record, separate project) and are greyed when they cannot be opened.
- A message box that works on a machine without the coordinator.
- **Sync**: Git first for a project that exists on both machines. **Add**: clone first for a machine that lacks it. The existing full compare stays as the slow path.
- **Hand off**: one dialog and one engine for threads, unsaved work and the coordinator conversation. It absorbs increment 1389's plan.
- Automatic hand off for chosen threads on sleep and at a usage limit, under one settings group.
- Headless fixtures for every changed surface, and a two-machine acceptance run.

Out:

- The leadership model. One active coordinator per project, epochs, `takeover`, `supersede`, the epoch claims and the worker fence stay as they are. Contract values (`transferred`, `runs-workers`, `independent`, `copy-and-move`, `git-sync`) keep their names.
- Several coordinators at once, or merging two coordinator conversations.
- Moving sign-ins, running processes, terminals or dev servers. They never travel.
- Continuous background file sync. Sync runs when asked, and before a hand off.
- Team rules, grants and device approval (1326, 1327). Every new call runs under the existing scopes.
- The in-flight chip and Send button fix owned by the thread "M5 specweave send and Make main". This increment states the rule (AC-02); that thread ships the bug fix first.

## The concept

A project lives on several machines as equals. Three verbs cover what happens between them:

| Verb | Moves | Used when |
|---|---|---|
| **Sync** | Files. Pull on both machines, fast-forward only, clone what is missing. Work Git does not carry is offered as ticked-by-hand extras. | The project is on both machines |
| **Add** | Files, first time. Download from GitHub, plus the same extras. | A machine does not have the project |
| **Hand off** | Work. Threads, unsaved work and the coordinator conversation continue on another machine. | Closing the laptop, a usage limit, or simply working elsewhere |

One fact replaces the roles: **"Coordinator on {machine}"**. The coordinator is the project's one planning conversation. It is work, so it is handed off like a thread. A person never assigns a role to a machine.

## Acceptance Criteria

### A. Words and the machine menu

- [ ] AC-01: The strings "Main", "Copy · main on {machine}", "Make {machine} main", "This copy takes work from there", "Send to another machine…", "Move running threads…", "Leave this machine…" (in the project menu) and "Keep ready to move" appear nowhere in the web, desktop and iOS interfaces, in any language. Each is replaced as the Wording table says. A test fails when an English phrase key from the "Today" column is still present.
- [ ] AC-02: The project page's chip names the machine whose copy the page shows ("On M5"). After a click on a machine row the chip names that machine. The chip never names the coordinator's machine unless that is the machine shown.
- [ ] AC-03: The menu's first group is "{project} on your machines". Each row shows at most two facts: "Coordinator" when the coordinator conversation is there, and one sync state out of "Up to date", "{n} commits behind", "{n} uncommitted files", "{n} commits not pushed", "Not checked yet". A row never shows a role.
- [ ] AC-04: A row is pressable only when this window has something to show for that machine. A machine this window never opened, one that refuses this window, or one whose project is not registered is greyed, is not an action, and has its reason and the one step that fixes it written on the row, not in a tooltip ("This window cannot open {machine} · Connect…"). An offline machine whose copy this window has saved stays pressable, reads "Offline · last seen {time} · read-only" and opens that saved state with every action greyed. A machine without the project is not a row; it is listed in "Add to another machine…". A machine too old for sync or hand off opens, and those actions are greyed with "Needs update · {version}". After any click the chip names the clicked machine (AC-02).
- [ ] AC-05: A machine that runs a live coordinator of its own while the project's coordinator is elsewhere (role `also-main`, m1 on November 18) shows "Second coordinator" and a "Fix…" action. Fix says when that coordinator last ran and offers two choices: "Retire it" (it gives way to the project's coordinator through the existing give-way path and its conversation stays as history) or "Unlink {project} on {machine}" (the existing Unlink). Neither touches threads or files. A copy of the same repository registered on its own shows "Separate project" and keeps "Link {machine} to this project…".
- [ ] AC-06: Below the rows the menu has "Sync all machines…" and "Add to another machine…" (only when a machine lacks the project). The group for the viewed machine, "Work on {machine}", has "Hand off work…", and "Continue the coordinator here" when the coordinator is elsewhere. There is no other coordinator item in the menu.

### B. The message box on a machine without the coordinator

- [ ] AC-07: The coordinator's machine answers: the box is enabled. Send delivers the message to the coordinator where it is, and the reply appears on this page without navigating away. The line above reads "The coordinator for {project} is on {machine}. Your message goes there and the answer shows here." A secondary button "Continue here" is next to it.
- [ ] AC-08: The coordinator's machine has been silent for less than 10 minutes: the box keeps the typed message and the button reads "Send when {machine} is back". "Continue here" is greyed with the time left. Nothing is lost if the window closes: the message is kept as a held draft on this machine and sent once when {machine} answers.
- [ ] AC-09: Silent for 10 minutes or more: the primary button is "Continue here and send". It runs the existing takeover, then sends. The line says the coordinator starts from the shared plan and memory, that its conversation on {machine} stays readable there, and that {machine} gives way when it is back. When the old machine returns, the page lists what it ran while disconnected (existing `ranWhileDisconnected`).

### C. Sync and Add

- [ ] AC-10: "Sync" (row button) and "Sync all machines…" open "Sync {project}: {a} and {b}". It lists every repository of the project with its branch and state on each machine, and what Sync will do there. It runs `git fetch` on both machines first.
- [ ] AC-11: Per repository and per machine, Sync does exactly one of the following and says which:

  | State on a machine | Sync does there |
  |---|---|
  | Clean, behind its upstream | `git merge --ff-only` to the fetched commit |
  | Up to date | Nothing |
  | Has uncommitted changes | Fetch only. "Not moved forward: {n} uncommitted files" |
  | Diverged from its upstream | Fetch only. "Has commits {other} does not have" |
  | In use by a running thread | Fetch only. "In use by {thread}" |
  | A different branch than the other machine | Fetch only; the other machine's branch becomes available locally, and nothing is checked out |
  | Repository missing, has a remote | Clone from the remote |
  | Repository missing, no remote | Nothing. Listed under "Compare all files…" |
  | Branch has no upstream | Nothing. Its commits are listed as an extra |

  Sync never resets, rebases, merges with a merge commit, stashes, switches a branch, deletes, pushes or commits on a branch a person works on.
- [ ] AC-12: Work that Git does not carry is listed per machine under "Only on {machine}", each line unticked: commits not pushed (per branch), branches that exist only there, uncommitted and untracked files (count per repository), stashes, and secrets. Nothing in this list travels unless its line is ticked.
- [ ] AC-13: A ticked "commits not pushed" or "branches only on {machine}" line sends those commits straight to the other machine and pushes nothing to the remote. They land as the same branch when that is a fast-forward there, otherwise as `swc/from-{machine}/{branch}` (the name the folder copy already uses). A ticked "uncommitted files" line arrives as the branch `swc/from-{machine}/uncommitted-{date}` holding one snapshot commit made with a private index, so the source's branch, index and working tree are unchanged.
- [ ] AC-14: Secrets are a separate line, found by the existing three-layer detector, and never part of a snapshot commit. A ticked secret travels sealed to the destination (the 1365 route). A secret missing on the destination is ticked by default; one that exists there with different content is unticked and shows which side is newer. When the sealed route is unavailable the line says why and stays behind.
- [ ] AC-15: "Add to another machine…" opens "Add {project} to {machine}" with "Download from GitHub (recommended)" selected, the folder, and the same "Only on {source}" extras, ticked as they are today (the November 15 default: download from GitHub, local changes from the source). "Copy the whole folder from {source}" is the second choice and the only one for a project with no remote. After Add the machine is a row like any other; the coordinator does not move.
- [ ] AC-16: "Compare all files…" in the Sync dialog opens the existing measured copy (per-file compare, with its Undo). The Sync result screen lists each repository as done or skipped with its reason, the extras that travelled, and "Check again".

### D. Hand off

- [ ] AC-17: "Hand off work…" opens "Hand off work from {machine}" with a target picker, a scope ("{project}" or "Every project on {machine}") and one ticked list: Running, Waiting for you, Not running with unsaved work, Project folder work, Coordinator conversation, and (scope every project) Routines. A "Stays" group names each item that cannot go and why. It replaces the Move running threads and Leave this machine dialogs.
- [ ] AC-18: A thread in a worktree set moves whole: every member repository's branch, commits and uncommitted files arrive in a worktree set on the target. If one member cannot move, none of that thread moves and the row names the member and the reason.
- [ ] AC-19: An idle or finished thread whose folder holds uncommitted files or commits on no remote is listed under "Not running, with unsaved work", ticked. It moves like a running thread and starts no turn on the target.
- [ ] AC-20: "Project folder work" covers the project folder's own uncommitted files and branches that exist only on the source (the 179 files and 11 branches of November 18). Ticked in a hand off of everything. It travels as AC-13 says. Secrets follow AC-14.
- [ ] AC-21: Order: check, sync the target (AC-11), threads, project folder work, coordinator, routines. A repository that cannot fast-forward on the target holds only the items that need it and is named. The coordinator moves last by the existing git-sync move with its conversation, and with `staleCopy: "refuse"`. While an unticked thread keeps running on the source, the coordinator row is greyed with "Stays while {n} threads keep running here".
- [ ] AC-22: The target picker shows, per machine and per provider the moving threads use, "Different {provider} account · {n}% left" or "Same {provider} account as {source}: adds no usage". A same-account target is allowed by hand and warned.
- [ ] AC-23: The source keeps every file. Each moved thread stays readable on the source, marked "Handed off to {machine}", with "Bring back". A hand off that gets no answer is in doubt and is replayed under the same operation id, never reverted blindly (the 1267 rule).
- [ ] AC-24: A folder whose Git data is broken is listed under Stays with its path and "Copy as plain files", which archives it to the target's `recovered/{source}-{name}/` folder and changes nothing on the source. Limits are checked before the button is enabled: a file over 10 MB, more than 20,000 files, or a bundle over 64 MB is named with the item it holds back.

### E. Automatic hand off

- [ ] AC-25: A thread's menu has "Hand off automatically" (Project default / On / Off), replacing "Keep ready to move". On keeps a standby checkpoint of the thread on the hand off machine, and the thread shows "Standby on {machine} · saved {time} ago".
- [ ] AC-26: Settings > Machines > Hand off has one row "When this machine goes to sleep": "Do nothing" (default) or "Hand off to {machine} after {n} minutes". With a machine chosen, the target continues the threads set to hand off automatically, and takes the coordinator when one of them belongs to that project. The Hand off dialog's "Also do this when {machine} goes to sleep" sets the machine and turns the setting on for the ticked threads.
- [ ] AC-27: The same group has "When a usage limit stops a thread": "Ask me" (default; the banner offers "Hand off to {machine}") or "Hand off to a machine with usage left". The order stays: a model switch on the same machine where the project rule says so, then a machine. A machine on the same account never counts, a review thread never moves, and a thread set to Off never moves.
- [ ] AC-28: Every automatic hand off writes one line in the thread on both machines ("Handed off to M5 at 14:02: Claude usage limit on m4") and a notification, and can be undone with "Bring back".

### F. Everywhere else, and proof

- [ ] AC-29: The command palette, the desktop File menu, the tray, `/away` and `/back`, Settings > Machines, the thread menu and the limit banner use the Wording table's words. `/away` and `mod+alt+l` keep working and open the Hand off dialog with the scope "Every project on {machine}"; `/handoff` is added.
- [ ] AC-30: Translations, the iOS strings and the MCP tool descriptions that agents read (`studio_thread_migrate`, `studio_project_add_to_machine`, `studio_handoff_ready_list`, `studio_thread_continue_here`, `studio_machine_list`) use the new words. Tool names and parameters do not change.
- [ ] AC-31: Headless fixtures render the menu (every row state of AC-03 to AC-05), the three box states, the Sync dialog with the November 18 state of the M4, the Add dialog and the Hand off dialog, light and dark, at 1280 and 390 px, with assertions on the greyed rows and on each "Stays" reason.
- [ ] AC-32: Anton runs it between the M4 and the M5: sync both ways, add a project to a machine without it, hand off two running threads (one in a worktree set) and the coordinator, close the lid with one thread set to hand off automatically, and bring the work back. His "accepted" closes the increment. Until then every phase stays behind a build flag that is off in releases.

## Wording

Every string below was read at `origin/main` `af7b77f05` (1.0.346) of `repositories/anton-abyzov/specwithcode`. Prefixes: `web/` = `apps/web/src/`, `srv/` = `apps/server/src/`, `desk/` = `apps/desktop/src/`, `ios/` = `apps/ios/SWCKit/Sources/`. "(unchanged)" rows are listed so nobody has to wonder whether they were missed.

### 1. Machine menu, chip and rows

| Surface | Today | New |
|---|---|---|
| Chip (`web/components/studio/OrchestratorSwitcher.tsx:154`; it names the coordinator's machine through `composerMachines`, `web/studio/routeToMain.ts:26`) | Runs on {machine} | On {machine}, always the machine shown |
| Chip, screen readers (`OrchestratorSwitcher.tsx:249`) | Viewing {machine}. Choose a machine to view | (unchanged) |
| Group label (`:263`) | View this project on | {project} on your machines |
| Group note (`:266`) | Viewing moves nothing: work stays on each machine. Adding or moving the project asks first. | Pick a machine to see its threads and files. Nothing moves until you sync or hand off. |
| Row badge (`web/studio/workersOnlyCopy.ts:56`) | Main | Coordinator |
| Row badge (`workersOnlyCopy.ts:59`, also worn by a copy that runs a coordinator of its own) | Copy · main on {machine} / Copy | The sync state: Up to date / {n} commits behind / {n} uncommitted files / {n} commits not pushed / Not checked yet |
| Row badge, copy with a live coordinator of its own (role `also-main`) | Copy · main on {machine} | Second coordinator · Fix… |
| Row badge (`workersOnlyCopy.ts:57`) | Moving main | Handing off the coordinator… |
| Row note (`OrchestratorSwitcher.tsx:294`) | coordinator paused | Old conversation kept |
| Row tooltip (`:300`) | {machine} kept its coordinator conversation from before as history. View it to read that conversation. | (unchanged) |
| Row note, machine never opened in this window (`:314`, pressable today) | not connected | This window cannot open {machine} · Connect… (greyed) |
| Row tooltip (`:316`) | This app isn't connected to {machine}, so its copy can't be shown. Connect it in Settings > Machines. | (the same sentence, written on the row) |
| Row note (`web/studio/projectCoordinatorMachine.ts:247`) | not linked | Separate project |
| Row tooltip (`OrchestratorSwitcher.tsx:305`) | Not linked: {machine} runs its own coordinator, threads and memory for this repository. | Separate project: {machine} added this repository on its own, with its own coordinator, threads and memory. |
| Group sentence (`:275`) | Not linked: these are separate projects for this repository, each with its own coordinator, threads and memory. That does not stop you viewing or messaging any of them. | These are separate projects for this repository, each with its own coordinator, threads and memory. You can still open and message each one. |
| Group sentence (`:277`) | Link them below to make one project. | (unchanged) |
| Offline machine with a saved copy (pressable today, no mark) | (its role badge) | Offline · last seen {time} · read-only (pressable, opens what it last had) |
| Group label (`:344`) | This project | (removed; its items sit under the rows) |
| Item (`:353`) | Send to another machine… | Sync all machines… and Add to another machine… |
| Item (`:369`) | Link {machine} to this project… | (unchanged) |
| Item tooltip (`:361`) | Makes the project on {machine} part of this one. Main does not change, and threads and files stay where they are. You confirm what {machine} gives up first. | Makes the project on {machine} part of this one. The coordinator stays where it is, and threads and files stay where they are. You confirm what {machine} gives up first. |
| Item (`:397`) | Make {machine} main (one per machine) | Continue the coordinator here (one, for the machine shown) |
| Item tooltip (`:386`) | Moves the coordinator and its conversation from {main} to {machine}. {main} becomes a copy. You confirm first. | Syncs {machine}, then moves the coordinator conversation here from {main}. You confirm first. |
| Item tooltip (`:382`) | {main} is unreachable: {machine} takes over and starts from the shared goal, memory and plan. You confirm first. | {main} is offline: the coordinator starts on {machine} from the shared goal, memory and plan. You confirm first. |
| Group label (`:410`) | On {machine} | Work on {machine} |
| Item (`:419`) | Move running threads… | Hand off work… |
| Item note (`:422`) | {machine} offline | (unchanged) |
| Item (`:434`) | Leave this machine… | (removed from this menu; "Hand off work…" has the scope) |
| Item (`:443`) | Machine access settings | (unchanged) |
| Page for a row with nothing to show (`web/components/studio/ProjectWorkspace.tsx:256`, `:271`) | {machine}'s orchestrator: Unknown · View {machine}'s orchestrator | {project} on {machine} cannot be opened from this window · Open {project} on {machine} (only reachable from an old link; the row is greyed) |
| Header tag (`web/components/studio/ProjectWorkspaceSurface.tsx:1864`) | Copy on {machine}, not this computer. Its coordinator runs on {main} | {project} on {machine}, not this computer. Coordinator on {main} |
| Header tag (`:1865`) | Runs on {machine}, not this computer | On {machine}, not this computer |
| Sidebar tooltip (`web/studio/projectDomain.ts:362`) | {M4}: Main · {M3}: Copy | On {M4} (coordinator) and {M3} |
| Sidebar badge (`web/studio/linkedMachines.ts:78`) | Handed off: coordinator on {machine}, {here} runs workers | Coordinator on {machine} |
| Sidebar badge (`linkedMachines.ts:82`) | Shared from {here} with {machines} | On {here} and {machines} |
| Sidebar row (`web/components/studio/shell/SidebarProjectList.tsx:667`) | Runs on {machine}. No copy on this device. | On {machine}. Not on this device. |
| Sidebar menu (`SidebarProjectList.tsx:960`) | Add to this machine… | (unchanged) |

### 2. Message box on a machine without the coordinator

| Surface | Today | New |
|---|---|---|
| Line (`web/components/studio/CoordinatorBlockedNotice.tsx:59`) | Main for {project} is {machine}. This copy takes work from there. | The coordinator for {project} is on {machine}. Your message goes there and the answer shows here. |
| Line (`:63`) | Main for {project} is on another machine. This copy takes work from there. | The coordinator for {project} is on another machine that this window cannot reach. |
| Line (`:66`) | The conversation here is kept as history. | (unchanged) |
| Button (`:77`, `:78`) | Write to {machine}'s coordinator / Write to main's coordinator | (removed; Send does it) |
| Button (`:89`) | Make {machine} main | Continue here |
| Note (`:97`, `:101`) | Send delivers your message to {machine}'s coordinator and opens its page, where the answer comes. | (removed; the line above says it, and the page no longer changes) |
| Note (`:108`, `:112`) | Write opens {machine}'s page for this project, where its coordinator answers. Nothing is sent from here. | (removed) |
| Note (`:122`) | {main} has been unreachable for 10 minutes or more. Making {machine} main starts from the shared goal, memory and plan; the conversation on {main} stays there as history. | {main} has been offline for {n} minutes. Continue here: the coordinator starts on {machine} from the shared goal, memory and plan. Its conversation on {main} stays readable there, and {main} gives way when it is back. |
| Note (`:126`) | Making {machine} main moves the coordinator and its conversation here from {main}, which becomes a copy. | Continue here syncs {machine}, then moves the coordinator conversation here from {main}. |
| Banner (`:171`, `:175`) | {machine} became main while {main} was unreachable. It started from the shared goal, memory and plan; the earlier conversation stays on {main} as history. | The coordinator continued on {machine} while {main} was offline. It started from the shared goal, memory and plan; the earlier conversation stays on {main} as history. |
| Placeholder (`ProjectWorkspaceSurface.tsx:2083`) | Message {machine}'s coordinator for {project}. | Ask the coordinator for {project} (on {machine}). |
| Placeholder (`:2089`, `:2093`) | Work for {project} starts on {machine}. / Work for {project} starts on another machine. | The coordinator for {project} is on {machine}, which is not answering. / …is on another machine. |
| Send (`web/components/studio/CoordinatorComposer.tsx:335`) | Send to {machine} | Send / Send when {machine} is back / Continue here and send |
| Send tip (`CoordinatorComposer.tsx:327`) | Send to {machine}… | Goes to the coordinator on {machine} |
| Send, screen readers (`:340`) | Send to the coordinator on {machine} | (unchanged) |
| Files refused (`web/studio/routeToMain.ts:83`) | Files stay on this machine. Remove them to send the text to main, or open main's page to attach them there. | Files stay on this machine. Remove them to send the text, or open {project} on {machine} to attach them there. |
| Problem (`projectCoordinatorMachine.ts:35`) | Work starts on another machine. This copy takes work from there. Switch to that machine above to send messages. | The coordinator is on another machine. Messages typed here go to it. |
| Problem (`projectCoordinatorMachine.ts:33`) | Another machine took over this coordinator. It gives way once its machine is reachable; view the newer coordinator to send messages. | The coordinator continued on another machine. This one gives way once it is reachable; messages typed here go to the newer one. |
| Problem (`projectCoordinatorMachine.ts:37`) | This copy has not confirmed its coordinator yet. Reconnect its machine to send messages. | {machine} has not confirmed where the coordinator is yet. Reconnect it to send messages. |
| Problems (`projectDomain.ts:203` to `208`) | Coordinator handoff is pending. […] / Two coordinators claim the same epoch […] / The active coordinator is unavailable. […] | (unchanged) |
| Confirm title (`web/components/studio/useMakeMain.tsx:294`) | Make {machine} main? | Continue the coordinator on {machine}? |
| Confirm body (`:297`) | {main} has been unreachable for 10 minutes or more. {machine} becomes main […] Until {main} is back it can still start work on its own machine; then it gives way and lists what it ran meanwhile. | {main} has been offline for 10 minutes or more. The coordinator starts on {machine} […] (the rest unchanged) |
| Confirm button (`:308`) | Make {machine} main / Switching… | Continue here / Starting the coordinator… |
| Toast (`:174`) | Main cannot move from this machine yet. | The coordinator cannot be handed off from this machine yet. |
| Toast (`:231`, `:239`) | {machine} cannot become main yet. | The coordinator cannot continue on {machine} yet. |
| Toast (`:246`) | {machine} is main now | The coordinator continues on {machine} |
| Toast (`:255`) | {machine} is main now, with machines not yet following it | The coordinator continues on {machine}. {names} have not confirmed it yet. |
| Toast (`:266`) | {machine} did not become main | The coordinator stayed on {main} |
| Reason (`web/studio/makeMain.ts:167`) | {main} must be unreachable for 10 minutes before {machine} can become main. That unlocks in {minutes} min. | {main} must be silent for 10 minutes before the coordinator can continue on {machine}. That unlocks in {minutes} min. |
| Reason (`makeMain.ts:176`) | This window can only read {main}, so it cannot move main from there. Open SpecWithCode on {main}, or connect to it with full access, to make {machine} main. | This window can only read {main}, so it cannot hand the coordinator off from there. Open SpecWithCode on {main}, or connect to it with full access. |
| Reason (`makeMain.ts:183`) | Connect {machine} first to make it main. | Connect {machine} first to continue the coordinator there. |
| Reason (`makeMain.ts:189`) | {machine} cannot take over yet. Update SpecWithCode there, or connect to it with permission to change settings and run work. | {machine} cannot continue the coordinator yet. Update SpecWithCode there, or connect to it with permission to change settings and run work. |
| Reason (`makeMain.ts:219`) | Connect {main} first. This window has not loaded main's copy on {main}, so it cannot make {machine} main yet. | Connect {main} first. This window has not opened {project} on {main}, so it cannot hand the coordinator off yet. |
| Short reasons (`makeMain.ts:170`, `179`, `184`, `192`, `222`) | in {minutes} min / read-only on {main} / {machine} offline / not ready / connect {main} first | (unchanged) |
| Refusal (`web/components/studio/handoffCopySteps.ts:302`, `320`, `337`) | {n} threads still working or waiting for you on {machine}, so the coordinator stayed there. […] | {n} threads are still working on {machine}, so the coordinator stays there. Hand them off too, or try again when they finish. |
| Second-coordinator toast (`OrchestratorSwitcher.tsx:633`, `:640`) | {machine}'s coordinator runs again · Each coordinator keeps the threads it started. Nothing moved. | (removed with its caller if T-01 confirms none is left; a second coordinator is a state to fix, not one to start) |

### 3. Sync and Add (today's Send dialog)

| Surface | Today | New |
|---|---|---|
| Trigger (`web/components/studio/MachineHandoffDialog.tsx:83`, `:86`) | Send this project to another machine / Send to another machine | Sync or add this project on another machine / Sync… |
| Title (`:297` to `304`) | Move {project} to {machine} / Copy {project} to {machine} / Move {project} to another machine / Copy {project} to another machine | Continue the coordinator on {machine} / Add {project} to {machine} / Add {project} to another machine |
| Title (`:295`) | Make {machine} main for {project} | Continue the coordinator on {machine} |
| Title, sync mode (`:286` to `291`; no caller opens it today) | Sync {project} to {machine} / {project} is synced to {machine} / {project} is on {machine} (copied {when}) | Sync {project}: {source} and {machine} / {project} is in sync on {source} and {machine} / {project} is on {machine} (added {when}) |
| Description, sync mode (`:314`) | {machine} already has this project at {folder}. Sync compares the two copies and adds what {machine} is missing: […] The coordinator stays on {source}. | Git first. Each repository moves forward to the newest commits, fast-forward only. Nothing is overwritten. The coordinator stays where it is. |
| Description (`:316`) | Nothing on {machine} is replaced without asking. | (unchanged) |
| Description (`:312`) | The coordinator now runs on {target}. | The coordinator continues on {target}. |
| Header (`web/studio/sendToMachine.ts:175` to `179`) | From {source}. Main moves to {machine}. / From {source}. Main stays on {main}. / From {source}. Main stays where it is. | From {source}. The coordinator continues on {machine}. / From {source}. The coordinator stays on {main}. / From {source}. |
| Buttons (`MachineHandoffDialog.tsx:434`, `:461`) | Make {machine} main | Continue here |
| Buttons (`:435`, `:462`) | Move project to {machine} / Move project | Continue the coordinator on {machine} |
| Button (`:432`) | Moving… | Handing off the coordinator… |
| Button (`:730`) | Keep Main on {source} | Keep the coordinator on {source} |
| Note (`:546`) | Add this project on {machine} first, then hand it off there. | (unchanged) |
| Note (`:563`) | {machine} already has this project in this folder. Nothing is copied: only the coordinator conversation moves, and the code there comes from Git. | (unchanged) |
| List (`:571` to `576`) | What comes along · Committed work in every repository, through Git · Project goal, instructions, memory and the coordinator's threads · Stays on {source}: secrets, sign-ins […] | (unchanged) |
| Line (`:810`, `:817`) | {n} uncommitted files stay on {source}: Git carries commits only. Commit them, or choose Copy everything under Details. | {n} uncommitted files on {source}. Git does not carry them. Tick them to send a snapshot. |
| Button (`:829`) | Commit for me | Commit on {source}… (lists the repositories it will commit in; never the default) |
| Review (`:706` to `708`) | {source} pushes its commits. {target}'s copy fast-forwards only where nothing there would be overwritten. […] | {target} moves forward only where nothing there would be overwritten. […] (the push sentence depends on D-03) |
| Consent (`:784`) | Push these commits and continue the project on {target}. | Send these commits to {target} and continue the coordinator there. (D-03) |
| Methods (`web/components/studio/ProjectMoveOptions.tsx:297`) | Download from GitHub (recommended) | (unchanged, and the default) |
| Methods (`ProjectMoveOptions.tsx:303`) | Copy everything | Copy the whole folder from {source} (Add) / Compare all files… (Sync) |
| Methods (`ProjectMoveOptions.tsx:308`) | Git only, no file copy | (removed as a choice; it is what Sync does) |
| Picker (`ProjectMoveOptions.tsx:194`, `:213`) | Copy to send to · Main | Folder on {machine} · Coordinator |
| Refused (`ProjectMoveOptions.tsx:351`, `:353`) | Not available: that machine already has Main. / Not available: it would move Main into a project this copy is not linked to. | (removed with the choice) |
| Refused (`ProjectMoveOptions.tsx:126`) | Main cannot move to {machine} from here: {source} is not linked to the project {machine} belongs to. […] | The coordinator cannot continue on {machine}: it has this repository as a separate project. Link it first. |
| Destination (`sendToMachine.ts:139`) | {there} has {n} copies of this project. Pick the one to send to. | {there} has this project in {n} folders. Pick one. |
| Destination (`sendToMachine.ts:142`) | {there} already has Main, at {folder}, so there is nothing to move. | {there} already has the coordinator, at {folder}. |
| Destination (`sendToMachine.ts:143`) | {there} already has a copy, at {folder}. Only what it is missing is copied. | {there} already has this project, at {folder}. Sync brings it up to date. |
| Plan (`sendToMachine.ts:227` to `246`) | Work continues on {there}, and this copy stops starting work. / Push this machine's commits, then move Main to {into}. | The coordinator continues on {there}. / Send this machine's commits, then continue the coordinator in {into}. |
| Plan (same lines) | Copy the folder to {there} / Copy {n} changed local files into {into} / Compare with {into} and copy what it is missing | (unchanged) |
| Not linked (`sendToMachine.ts:166`, `:170`) | From {source}. {source}'s copy is not linked to the project {machine} belongs to (Main: {main}). | From {source}. {machine} has this repository as a separate project (coordinator on {main}). |
| Not linked (`sendToMachine.ts:194`, `:198`) | Only files are copied into {machine}'s copy. Main stays on {main}, and {source} is not linked to that project. To make them one project, link {source} to it from the machine menu. | Only files go into {machine}'s folder. Its coordinator stays on {main}. To make them one project, link {source} to it from the machine menu. |
| Done (`web/components/studio/HandoffCopyDone.tsx:145`, `:146`) | {machine} has a copy. Main stays on {main}. / {target} has a copy. The coordinator stays here. | {project} is on {machine}. The coordinator stays on {main}. / …stays here. |
| Done (`HandoffCopyDone.tsx:128`) | The files are on {target}, but {problem}. Copy again: it compares first and moves only what changed. | The files are on {target}, but {problem}. Sync again: it compares first and moves only what changed. |
| Done (`:143`) | Files are copied. Hand off the coordinator once work here is idle. | (unchanged) |
| Done buttons (`:648`, `:676`, `:692`) | Copy again / Copy changes again | Sync again |
| Done button (`:653`) | Hand off coordinator now | Continue the coordinator on {target} |
| Done button (`:671`) | Make {machine} main | Hand off work to {machine}… |
| Done button (`:465`) | Hand off anyway | Continue on {target} anyway, on its older commits |
| Done buttons (`:698`, `:205`) | Start a new copy / Copy again with secrets | Add to another machine / Sync again with secrets |
| Done (`:214`, `:218`) | Not linked: the copy on {machine} belongs to a project whose Main is {main}, and {source} is not part of it. Nothing was linked. | {machine} has this repository as a separate project whose coordinator is on {main}. Nothing was linked. |
| Done (`:230` to `233`) | Linking the copy on {target} to {source}… / Linked: {source} can send work to the copy on {target}. / Not linked yet. {reason} | Linking {target}… / Linked: {source} can start work on {target}. / (unchanged) |
| Freshness (`web/components/studio/HandoffCopyScanFreshness.tsx:43`) | Check for changes | (unchanged) |
| Freshness (`HandoffCopyScanFreshness.tsx:68`, `web/components/studio/HandoffCopyFooter.tsx:264`) | Measure and compare again | Compare again |
| Per-repository rows (`srv/fleet/folderTransfer/reconcile.ts:453` to `477`) | Same commit on both machines. / Behind the source; moves forward to its commit. / Behind the source, with uncommitted changes here. / Ahead of the source; kept. Source branches arrive as swc/from-{machine}/…. / Both machines have commits the other lacks. Nothing is lost either way. | (unchanged; "the source" becomes the other machine's name) |
| New chat picker (`web/components/chat/DraftMachinePicker.tsx:544`) | Add to another machine… | (unchanged) |
| Add dialog (`web/components/chat/AddToMachineDialog.tsx:319`) | […] Copy its folder there instead: the project's menu > Add to another machine… > Review files to transfer. | […] Copy its folder there instead: the machine menu > Add to another machine… > Copy the whole folder. |
| Link dialog (`web/components/studio/ProjectLinkDialog.tsx:426`) | {machine} joins {project} as a copy. Main stays on {main}: linking does not change it. | {machine} joins {project}. The coordinator stays on {main}: linking does not move it. |
| Link dialog (`ProjectLinkDialog.tsx:423`) | […] The coordinator on {kept} can send work to both copies. | […] The coordinator on {kept} can start work on both machines. |
| Link dialog (`ProjectLinkDialog.tsx:609`) | Main stays on {main}. To have main on {machine}, make {machine} main after linking. | The coordinator stays on {main}. To continue it on {machine}, use Continue here after linking. |
| Link dialog (`ProjectLinkDialog.tsx:775`) | […] Main stays on {main}. Files are not copied. | […] The coordinator stays on {main}. Files are not copied. |
| Sidebar suggestion (`web/components/studio/shell/useProjectLinkSuggestions.tsx:63`) | Same repository ({repo}) also added on {machines}, not linked | Same repository ({repo}) is a separate project on {machines} |
| Sidebar pill (`SidebarProjectList.tsx:763`) | Link | (unchanged) |

### 4. Hand off (today's Move and Away dialogs)

| Surface | Today | New |
|---|---|---|
| Title (`web/components/handoff/HandOffMachineDialog.tsx:122`) | Move running threads / Move {project}'s running threads | Hand off work from {machine} |
| Lead (`:173`, `:176`) | Review readiness before moving the selected threads. They continue on the machine you pick. Anything that can't move stays here, untouched. · {project}'s coordinator stays on {machine}. | Tick what goes. It continues on the machine you pick. Anything that cannot go stays here, untouched, with its reason. |
| Empty (`:214`, `:215`) | Nothing of {project} is running on {machine} that's set to keep ready to move. / Nothing is running here that's set to keep ready to move. | Nothing unfinished in {project} on {machine}. / Nothing unfinished here. |
| Empty (`:203`) | No other machine is online. Pair one in Settings › Machines. | (unchanged) |
| Rows (`:252`, `:253`, `:263`) | The current turn keeps running there. / It will wait there for your next message. / Ready | (unchanged) / (unchanged) / Goes |
| Buttons (`:131` to `134`) | Moving… / Nothing ready to move / Move 1 thread / Move {n} threads | Handing off… / Nothing can go / Hand off to {machine} |
| Title (`web/components/away/AwayDialog.tsx:468`) | Leave this machine | Hand off work from {machine} (scope "Every project on {machine}") |
| Lead (`:470`) | Pick the machine that keeps working while you are away. Nothing changes until you leave. | Pick the machine that continues the work. Nothing changes until you press Hand off. |
| Legend (`:476`) | Leave work on | Hand off to |
| Groups (`web/components/away/awayDialog.logic.ts:67` to `69`) | Threads / Routines / Coordinators | Running / Waiting for you / Not running, with unsaved work / Project folder work / Coordinator conversation / Routines |
| Row states (`awayDialog.logic.ts:81` to `84`) | Moves / Ready to move / Stays / Pauses | Goes / Stays, with a standby copy on {target} / Stays / Pauses |
| Empty (`awayDialog.logic.ts:111`) | Nothing here needs to move. | Nothing unfinished here. |
| Confirm (`AwayDialog.tsx:571`) | Running and queued threads, routines and coordinators listed as Moves go to {target} now. The rest stay here and are listed in the summary. {target} becomes your Away target: the next Leave and closing the lid use it. Change it in Settings, Machines. | Everything ticked goes to {target} now. The rest stays here and is listed in the summary. (The sleep machine is set only by its own tick.) |
| Buttons (`:603`, `:612`) | Leave for {target} / Leaving… / Leave | Hand off to {target} / Handing off… / Hand off |
| Session (`:413` to `421`) | Bring work back / Bring work back from {target} / Away on {target} | (unchanged) / (unchanged) / Handed off to {target} |
| Button (`:455`) | Bring back / Bringing back… | Bring work back / Bringing work back… |
| Button (`:387`) | Run here anyway… | (unchanged) |
| Access (`:523`, `:548` to `551`) | Needed first ({n}) / Request access / Request sent | (unchanged) |
| Coordinator rows (`srv/away/AwayPlanner.ts:355`, `364`, `370`) | Finishes the handover to {target} […] / Hands over once {target} lets this machine's work into it. / Hands over to {target}. This machine's copy steps back. | Finishes the hand off to {target} […] / Goes once {target} lets this machine's work into it. / Continues on {target}. |
| Coordinator row (`AwayPlanner.ts:347`) | Not linked with a copy on {target}, so it stays here. | {target} does not have this project, so its coordinator stays here. Add it first. |
| Thread menu (`web/components/threadActionMenu.logic.ts:404`) | Move thread… | Hand off to another machine… |
| Thread menu (`threadActionMenu.logic.ts:417`) | Keep ready to move (Default / On / Off) | Hand off automatically (Project default / On / Off) |
| Thread menu (`threadActionMenu.logic.ts:411`) | Switch model and continue… | (unchanged) |
| Toast (`web/components/Sidebar.tsx:4903`, `web/hooks/useThreadActionMenu.ts:409`) | Couldn't change Keep ready to move | Couldn't change Hand off automatically |
| Thread chip tip (`web/components/chat/threadMachine.ts:64`, `:65`) | To move it, use ⋯ › Move thread. / It already moved to another machine, so this copy stays here to read. | To continue it elsewhere, use ⋯ › Hand off to another machine. / It was handed off to another machine, so it stays here to read. |
| Thread chip (`web/components/chat/ThreadMachineComposerChip.tsx:29`) | Runs on {machine} | (unchanged; true for a thread) |
| Thread dialog (`web/components/handoff/HandOffThreadDialog.tsx:177`, `:181`) | Move "{title}" · Its conversation and file changes go with it. This copy stops and stays here to read. | Hand off "{title}" · Its conversation and file changes go with it. It stops here and stays readable. |
| Thread dialog (`HandOffThreadDialog.tsx:133` to `135`, `:171`) | Can't move / Move to {machine} / Move / Moved to {machine} | Can't hand off / Hand off to {machine} / Hand off / Handed off to {machine} |
| Limit banner (`web/components/chat/LimitHandoffCandidates.tsx:93`) | Move to {machine} | Hand off to {machine} |
| Limit banner (`LimitHandoffCandidates.tsx:57`) | This server can't move threads to another machine yet. | This machine can't hand threads off yet. |
| Limit banner (`LimitHandoffCandidates.tsx:66`) | No other machine can take this thread now. | (unchanged) |
| Thread badge (`web/components/handoff/HandoffBadge.tsx:159`, `:191`, `:219`) | Continue here / Open on {machine} / Resume this machine… | (unchanged) |
| Refusal (`srv/handoff/HandoffMoves.ts:27`) | This thread works in a worktree set across several repositories, and a handoff carries one repository. Finish it on this machine, or push each repository's branch and continue on the other machine from there. | (gone; it moves. If a member cannot: "{repository} cannot be handed off: {reason}. Nothing of this thread moved.") |
| Preflight (`srv/handoff/handoffPreflight.ts:64`) | no {path}. Send it with studio_file_transfer, or with Copy to another machine | no {path}. Send it with studio_file_transfer, or tick it in Sync |
| Command palette (`web/components/CommandPalette.tsx:2938`) | Move running threads to another machine… | Hand off work… |
| Command palette (`CommandPalette.tsx:2957`, `:2969`) | Leave this machine… / Bring work back | Hand off everything on this machine… / (unchanged) |
| File menu (`desk/window/DesktopApplicationMenu.ts:227` to `229`) | Move Running Threads... / Leave This Machine... / Bring Work Back | Hand Off Work... / Hand Off Everything on This Machine... / (unchanged) |
| Tray (`desk/app/DesktopLifecycle.ts:265`, `:266`) | Leave This Machine... / Bring Work Back | Hand Off Everything on This Machine... / (unchanged) |
| Slash command (`web/studio/composerAppCommands.ts:42`) | `/away` "Leave this machine: hand its threads, routines and coordinator on" | `/handoff` "Hand off work to another machine" (new) · `/away` "Hand off everything on this machine" |
| Slash command (`composerAppCommands.ts:45`) | `/back` "Bring work back to this machine" | (unchanged) |

### 5. Settings

| Surface | Today | New |
|---|---|---|
| Row (`web/components/settings/HandoffModeSettings.tsx:140`, `:141`) | Away target · Where Away sends your threads, routines and coordinators. Also used when this machine sleeps; locking the screen doesn't count. | Hand off machine · Where Hand off sends work by default, and where it goes when this machine sleeps. Locking the screen doesn't count. |
| Row (`:176`, `:177`) | Leave automatically when the lid closes · Hands work to the Away target when this Mac sleeps. […] | When this machine goes to sleep: Do nothing / Hand off to {machine} · Threads set to hand off automatically continue there. […] |
| Row (`:198`) | Grace time | Wait before handing off |
| Row (`:47`) | Bring back automatically on power | Bring work back when this machine is on power again |
| Row (`:231`, `:262`) | When this machine wakes / Continue automatically when a machine stops answering | (unchanged) |
| Button (`:96`) | Move running threads… | Hand off work… |
| Row (`:101`, `:102`) | Keep threads ready to move · After each turn, copies this machine's threads, existing ones too, to your other machines with the same project, so any of them can pick up. Uses a few more tokens. | Hand off new threads automatically · After each turn, keeps a standby copy of each thread on your hand off machine, so it can continue there when this machine sleeps or reaches a limit. Uses a few more tokens. |
| Row (`:309`, `:310`) | Also back up syncs to the repository's remote · Pushes each sync to origin under refs/specwithcode/handoff, including uncommitted and untracked files. Moves don't need it. Your branches are never pushed. | Also back up standby copies to the repository's remote · Pushes each standby copy to origin under refs/specwithcode/handoff, including uncommitted and untracked files. A hand off doesn't need it. Your branches are never pushed. ("sync" now means only Sync) |
| Project row (`web/components/settings/ProjectHandoffModeSettings.tsx:73`) | Keep this project's threads ready to move | Hand off this project's threads automatically |
| Limit rule (`web/components/settings/MachineFallbackSettings.tsx:174`) | Other machines · Paired machines a limited thread can move to, best first. The thread resumes there from its last checkpoint. […] | When a usage limit stops a thread · Machines a limited thread can be handed off to, best first. It resumes there from its last checkpoint. […] (the conditions keep their words) |
| Limit order (`MachineFallbackSettings.tsx:54`) | Other machines first / This machine's models first | (unchanged) |
| Machines card (`web/components/settings/machinesSettings.logic.ts:504`, `:506`) | Not linked · also on {machine} · This copy is not linked to the copies on {machine}. Link them from the project menu to share one coordinator. | Separate project · also on {machine} · {machine} has this repository as a separate project. Link them from the project menu to share one coordinator, plan and memory. |
| Machines card (`machinesSettings.logic.ts:511`, `:512`) | Not shared · No other machine has a copy of this project. | Only on this machine · No other machine has this project. |
| Machines card (`machinesSettings.logic.ts:554`, `:555`) | Connect to see its role · This app cannot see this machine, so it cannot tell what this copy does. | Connect to see its state · This app cannot see this machine, so it cannot tell whether it is in sync. |
| Badge help (`workersOnlyCopy.ts:72`) | Work for this project starts here. Copies on other machines take work from it. | The coordinator conversation is on this machine. |
| Badge help (`workersOnlyCopy.ts:76`) | Main is on {machine}. This copy can also start work of its own. | The coordinator is on {machine}. {this} also runs a coordinator of its own, which should be fixed. |
| Badge help (`workersOnlyCopy.ts:81`) | Work starts on {machine}. This copy takes work from there. | The coordinator is on {machine}. Messages typed here go to it. |
| Badge help (`workersOnlyCopy.ts:85`) | Main is moving between machines right now. | The coordinator is being handed off right now. |
| Project machines (`web/components/studio/ProjectMachinesSettings.tsx:514`, `:658`) | Take over coordinator here / Take over | Continue the coordinator here / Continue here |
| Project machines (`ProjectMachinesSettings.tsx:525`, `:611`) | Unlink · Unlink the copy on {machine}? | Unlink · Unlink {project} on {machine}? (also reachable from "Fix…" on a row) |
| Standby (`web/components/studio/CoordinatorStandbySettings.tsx:930`) | Make {machine} the coordinator again | Continue the coordinator on {machine} again |
| Standby (`CoordinatorStandbySettings.tsx:261`) | Run here anyway | (unchanged) |

### 6. iOS and agents

| Surface | Today | New |
|---|---|---|
| `ios/SWCSync/Handoff.swift:125` | This project is not linked to another machine. Link it from the desktop app before handing off. | This project is on no other machine yet. Add it to one from the desktop app, then hand off. |
| `ios/SWCSync/Handoff.swift:82`, `:170` | This copy was handed off. […] / Continue from the saved checkpoint. […] | (unchanged) |
| `ios/SWCSync/LinkedProjects.swift:237` | Coordinator. Plans the work and can send it to every copy. | Coordinator. Plans the work and can start it on every machine. |
| `ios/SWCSync/LinkedProjects.swift:238` | Runs workers. Its own coordinator is read-only history until you start a coordinator here. | The coordinator is on another machine. An older conversation here is read-only history. |
| `ios/SWCFeatures/Linked/LinkedProjectViews.swift:51` | Each machine keeps its own copy. One coordinates; the others run workers. | Each machine has the project's files. The coordinator conversation is on one of them. |
| `ios/SWCFeatures/Linked/LinkedProjectViews.swift:97` | Take over coordinator here | Continue the coordinator here |
| `ios/SWCFeatures/Chat/HandoffSheet.swift:24` | Move this conversation and its checkpoint to another machine. The source becomes read-only. Opening these options does not move anything. | Hand off this conversation and its files to another machine. It becomes read-only here. Opening these options moves nothing. |
| `HandoffSheet.swift:56`, `:83` | Hand off to {name} / Hand off thread | (unchanged) |
| `HandoffSheet.swift:92` to `98` | Handoff ready / Checkpoint catching up / Handoff paused | Standby copy ready / Standby copy catching up / Hand off paused |
| MCP `studio_thread_migrate` (`srv/mcp/toolkits/orchestrator/tools.ts:383`) | Move threads this coordinator owns to another machine through handoff. […] omit them to move every running handoff-mode thread of this project. | Hand off threads this coordinator owns to another machine. […] omit them to hand off every running thread of this project that is set to hand off automatically. |
| MCP `studio_handoff_ready_list` (`tools.ts:396`) | List this project's threads that another machine replicated here through handoff mode […] | List this project's threads that have a standby copy here from another machine […] |
| MCP `studio_thread_continue_here` (`tools.ts:410`), `studio_project_add_to_machine` (`srv/mcp/toolkits/project/tools.ts:182`) | (no Main or Copy wording) | (unchanged) |
| Agent instructions (`srv/provider/StudioOrchestrationInstructions.ts:25`) | `studio_thread_migrate` moves an existing thread's execution […] Switching the viewed orchestrator never moves a thread. | `studio_thread_migrate` hands an existing thread off to another machine […] Switching the viewed machine never moves a thread. |

Tool names, parameters and contract values do not change.

## Approach

Four phases, each its own pull request and release, each behind the flag `studio.syncAndHandOff` until AC-32.

**Phase 1, words and an honest menu (web, desktop, iOS strings; no new data flow).**
- `apps/web/src/studio/projectCoordinatorMachine.ts` keeps `orchestratorCopies` and its roles. A new `machineRowState.ts` maps a copy plus its reach state to one row state of AC-03 to AC-05. The second-coordinator state is the existing role `also-main`.
- `OrchestratorSwitcher.tsx` renders rows from that state, disables rows with nothing to show and drops the per-machine coordinator items. `composerMachines` (`routeToMain.ts`) stops substituting the coordinator's machine into the chip. `CoordinatorBlockedNotice.tsx` becomes the three box states. `makeMain.ts` and `useMakeMain.tsx` keep their paths (online move, takeover after the guard) and change only names and the caller.
- Send from a non-coordinator machine already exists: `apps/web/src/components/studio/useRouteToMain.ts` calls `projects.coordinatorSend` on the coordinator's machine and then opens that machine's page. The change is what happens after: the page keeps showing the machine the person picked, with the coordinator's conversation rendered in place and the chip unchanged. A draft with files is still refused with its reason (`ROUTED_FILES_MESSAGE`), because files stay on their machine. While the coordinator's machine is unreachable the message is kept as a held draft on this machine and sent on reconnect, once, under one command id.
- Phrase files under `apps/web/src/i18n/phrases/`, the command palette, `apps/desktop` menu and tray titles, iOS strings and MCP descriptions.

**Phase 2, Sync and Add.**
- The dialog's unused sync mode (`MachineHandoffOpenRequest` `mode: "sync"`, `ProjectMachineHandoff.tsx:124`) becomes the Sync entry point, and the reconcile planner stays the judge of each repository. What is new is the Git-first step in front of it and running it in both directions.
- New contract `packages/contracts/src/projectSync.ts`: `projectSync.status` (per repository: branch, head, upstream, ahead, behind, dirty and untracked counts, in use, missing), `projectSync.plan` and `projectSync.run`. Statuses reuse `FolderCopyRow.status`.
- New server module `apps/server/src/fleet/ProjectSync.ts`. It calls the Git steps the git-sync move already uses (`git.checkExistingCopy`, `git.materialize` with `existingCopy`) without a coordinator move, under the project's admission lock, and adds the clone of a missing repository through the Add-to-machine clone path. Each machine changes only its own checkout; the caller asks each one over the existing fleet link.
- Extras: commits travel as a Git bundle over the existing folder-transfer route; the snapshot commit is built with a temporary index, as the hand off checkpoint is. Secrets use the sealed route of 1365.
- Row sync states come from `projectSync.status`, read when the menu opens and cached for 60 seconds. It reads local Git only and makes no network call; only the dialog fetches.
- Web: `MachineHandoffDialog.tsx` is split by entry point into a Sync dialog and an Add dialog; the measured copy stays behind "Compare all files…".

**Phase 3, Hand off (absorbs 1389).**
- Server, in 1389's order: worktree-set checkpoints in `apps/server/src/handoff/` (one checkpoint per member under one lease, all or nothing); `apps/server/src/away/AwayPlanner.ts` plans idle threads with unsaved work, project folder work, same-account facts and a project scope; `AwayRunner.ts` runs sync, threads, project folder, then the coordinator through the git-sync move, and falls back to the role-only planned handover only when the source is unreachable.
- Web: one `HandOffDialog` replaces `HandOffMachineDialog.tsx` and `AwayDialog.tsx`. The Away session, wake card and Bring back keep their engine.

**Phase 4, automatic.**
- `HandoffThreadModeSetting` (inherit, off, on) stays and is shown as "Hand off automatically". `sleepTarget`, `sleepTrigger` and `graceMinutes` stay and are shown as one row. The limit rule keeps `providerLimitAction` and `providerLimitMachineTargets`; a thread set to Off is excluded in `limitHandoffTrigger`.

**Single writer, unchanged.** One active coordinator per logical project at the highest epoch. "Continue here" is today's Make main. A takeover still waits 10 minutes and still claims the epoch on member machines. Plan claims and memory writes keep their current owner. What changes is that a person sees where the coordinator is and continues it, instead of assigning a role.

**Rejected:**
- *Every machine runs its own coordinator, with a lock only on the plan.* Two conversations plan the same goal and split the context. Anton rejected it on November 16 (1372), and nothing he said on November 18 asks for it back.
- *The coordinator follows the machine you type on.* Each switch moves a conversation and may refuse while threads run. It is an Asked decision (D-01), off by default.
- *Push before every sync, as Make main does today.* A push publishes work. Sync sends unpushed commits directly instead.
- *Commit uncommitted work on the person's branch.* A snapshot branch on the target is reversible; a commit on his branch is not his choice.
- *Keep "Leave this machine" as a second entry.* It is the same dialog with a wider scope.
- *Continuous file sync.* It fights running threads for the working tree.

**Risks:**
- Phase 1 changes many strings at once. The phrase-key test of AC-01 and the fixtures are the guard.
- The row sync state can be stale. It shows "Not checked yet" instead of a guess, and the dialog always fetches.
- A sent bundle is capped at 64 MB. A larger extra says so and points to "Compare all files…".
- Reordering the Away stages changes what an in-doubt session resumes. The saved stage is per item, so a resume reads both orders.
- Mixed versions: a machine without `projectSync` shows "Needs update" and falls back to the measured copy.

## Reviews

Reviewer: muse, model `muse-wonder-full-1.0`, effort xhigh, adversarial, named by Anton. Round reports in `reports/reviews/`. A "fix first" verdict gets a second round.

## Decisions

### Asked (waiting for Anton)

- D-01 Typing on a machine without the coordinator while its machine answers. Recommended: send it there and show the answer here, with "Continue here" one click away. Alternative: bring the coordinator to the machine you type on whenever it is idle.
- D-02 Automatic hand off defaults. Recommended: stay off (the November 12 decision), offered at the moment it helps: the limit banner and the "Also do this when {machine} goes to sleep" tick. Alternative: on for every thread once a sleep machine is chosen.
- D-03 Commits that were never pushed. Recommended: Sync and Hand off send them straight to the other machine and push nothing. Alternative: push to GitHub first, as Make main does today.
- D-04 Uncommitted project folder files in a hand off of everything. Recommended: ticked, arriving as branch `swc/from-{machine}/uncommitted-{date}`. Alternative: unticked, so they stay unless chosen.
- D-05 The 10 minute wait before "Continue here" when the coordinator's machine is silent. Recommended: keep it (1372). Alternative: allow at once behind a confirm that both machines may run the coordinator until the old one is back.
- D-06 Increment 1389 is folded into this one and closed as superseded. Recommended: yes, once this spec is accepted.

### Defaulted (change any before sw-do)

- D-07 The verb is "Hand off" (two words as a verb, "hand off" in sentences; the noun in Settings is "Hand off").
- D-08 The coordinator's location reads "Coordinator" on a row and "Coordinator on {machine}" in sentences. The words Main and Copy are not used for projects anywhere.
- D-09 `/away` and `mod+alt+l` stay as shortcuts to the wide scope. The project menu has one entry, "Hand off work…".
- D-10 Review threads stay on their machine in every hand off, by hand or automatic, because the reviewer lock does not travel.
- D-11 A secret that exists on both machines with different content is unticked. A secret missing on the destination is ticked (the November 13 default).
- D-12 "Fix…" on a second coordinator is a person's click, never automatic.
- D-13 A same-account target is warned, not blocked, by hand, and never chosen automatically.
- D-14 Row sync states read local Git only. Only the Sync dialog fetches from the remote.
- D-15 Extras are unticked in Sync and ticked in Add, where today's default already brings local changes from the source.
- D-16 A hand off no longer sets the sleep machine as a side effect (today the first Leave makes its target the Away target). Only the "Also do this when {machine} goes to sleep" tick or Settings sets it.
- D-17 An offline machine with a saved copy stays openable, read-only. Only a machine with nothing to show is greyed.

### Reverses

- "One Copy to another machine flow" (1325, November 13): one entry becomes Sync and Add. The rule against a separate Move entry stays.
- "One main, switch any time" (1372, November 16): the mechanism stays; the words Main, Copy and Make X main go.
- Away mode as the one way to leave (1267, November 10): its engine stays as the wide scope of Hand off; the menu entry and the name go.
- 1389 "Leave this machine takes everything": its server work is Phase 3 here.

### Open

- Whether Sync should offer "Keep in sync" (pull when a machine is idle and clean). Left out until the manual flow has run on real machines.

## Tasks

### T-01 Row states, greyed rows and the chip
- AC: AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCoordinatorMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/workersOnlyCopy.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/routeToMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/machineRowState.test.ts

### T-02 The message box on a machine without the coordinator
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useRouteToMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorComposer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useMakeMain.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/makeMain.test.ts

### T-03 Menu entries, palette, tray, File menu and slash commands
- AC: AC-06, AC-29 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/composerAppCommands.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/threadActionMenu.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/DesktopApplicationMenu.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopLifecycle.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/coordinator-menu/vite.config.ts && node apps/web/tests/coordinator-menu/verify.mjs

### T-04 Phrases in all eight languages (de, es, fr, ja, ko, pt, ru, zh), iOS strings, MCP descriptions, and the old-phrase test
- AC: AC-01, AC-30 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/retiredPhrases.test.ts, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/Handoff.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/LinkedProjects.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/HandoffSheet.swift, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/i18n/retiredPhrases.test.ts

### T-05 Project sync contract and server: status, plan and run
- AC: AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/ProjectSync.test.ts

### T-06 Extras: commits sent directly, snapshot branch, sealed secrets
- AC: AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSyncExtras.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSyncExtras.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/ProjectSyncExtras.test.ts

### T-07 Sync dialog and Add dialog
- AC: AC-10, AC-12, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectSyncDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSyncDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSyncDialog.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/projectSyncDialog.logic.test.ts

### T-08 Worktree-set threads move whole
- AC: AC-18 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/handoff/checkpointGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/bundleGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffReceiver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/handoff/HandoffMoves.test.ts

### T-09 Hand off plan: unsaved idle threads, project folder work, same account, project scope
- AC: AC-17, AC-19, AC-20, AC-22, AC-24 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/away.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/away/AwayPlanner.test.ts

### T-10 Hand off runner: sync, threads, project folder, coordinator last
- AC: AC-21, AC-23 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/away/AwayRunner.test.ts

### T-11 One Hand off dialog
- AC: AC-17, AC-22, AC-23, AC-24 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/handOffDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/handOffDialog.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/away/AwayDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffMachineDialog.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/handoff/handOffDialog.logic.test.ts

### T-12 Automatic hand off: per thread, on sleep, at a limit
- AC: AC-25, AC-26, AC-27, AC-28 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/HandoffModeSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/Sidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/LimitHandoffCandidates.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/MachineLimitHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitHandoffPreflight.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/limitHandoffPreflight.test.ts

### T-13 Headless fixtures for every changed surface
- AC: AC-31 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/project-sync/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/coordinator-menu/verify.mjs && node apps/web/tests/project-sync/verify.mjs && node apps/web/tests/away-mode/verify.mjs

### T-14 Two-machine run and Anton's acceptance
- AC: AC-32 | Files: .specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/acceptance.md | Test: test -s .specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/acceptance.md

### T-15 Verify and close 1390
- AC: AC-01, AC-32 | Files: .specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/closure.md | Test: specweave verify 1390-sync-projects-across-machines-and-hand-off-work
