# 1390 Sync projects across machines and hand off work, without Main and Copy

Status: design only, revised after review round 1 (verdict: fix first; every finding is answered in "Round 1 responses"). Nothing is built until Anton accepts, because this changes data flow between machines. Mockup: `reports/mockup.html`.

## Problem

Anton, November 18, 2026, on the M5 at 1.0.345 (screenshots in `~/.specwithcode/m4/userdata/attachments/`, ids `a03d1d32`, `dd5964b4`, `d6b192bf`):

> "Rethink this concept of main and non-main copy [...] the main motivation was that we could identify all unfinished work and effectively hand it off to another machine. When you are going to close your laptop [...] or when your tokens are about to run out [...] maybe it's just for one or two threads, and it wants to automatically proceed and do this on another machine."
>
> "If you copy the project, you should be able to proceed there on that server. I don't think we need to call it 'make M5 main.' I think this is wrong. The whole idea is about having maybe synchronization in files [...] the preferred way is just to pull all the latest changes. It could be that a new repository was introduced, and that's why copy is good."
>
> "On M5, when I try to click on M5, it's either not working, or it's selecting M4 intentionally, which is weird. If we cannot switch to M5, we should gray it out."

What is wrong, with evidence:

1. **The interface answers a question nobody asked.** Every row carries a role ("Main", "Copy · main on m4") and the only way to work from another machine is "Make M5 main". His goals are different: bring the files up to date, continue work there, and take unfinished work along. The role exists to keep one writer for the coordinator, the plan and memory. That is an internal need, and it leaked into every label.
2. **The chip and the rows mislead.** On the M5 the chip says "Runs on m4" after he picked M5, the notice says "Main for specweave is m4. This copy takes work from there", and the button says "Send to m4". The click did switch the page to the M5's copy. The chip names the coordinator's machine on purpose since 1.0.343 (`composerMachines`, `apps/web/src/studio/routeToMain.ts:26`, PR #551, so that the chip and "Send to m4" agree), while the menu it opens is titled "View this project on". That is his "it's selecting M4". No row is ever disabled (`MenuRadioItem` has no `disabled`, `OrchestratorSwitcher.tsx:321`): a machine this window never opened is pressable and leads to a page titled "{machine}'s orchestrator: Unknown".
3. **One entry hides two jobs.** "Send to another machine…" is used both to put a project on a machine that lacks it and to update one that has it. His preferred path for the second is `git pull`, with a clone for a repository that is new. A "Sync {project} to {machine}" mode exists in the dialog (`MachineHandoffDialog.tsx:286`), but nothing opens it. The only path that pulls on the destination is "Git only", and that one always moves Main.
4. **Five entries move work and none moves all of it.** From the M5 thread's report (`.specweave/reports/threads/2026-11-18-how-one-project-runs-across-machines-d53e8d-35b8ae.md`): Make main moves the coordinator and refuses while a thread runs or waits (`makeProjectIdleCheck`, `apps/server/src/fleet/folderCopyPreparation.ts:73`); Leave this machine moves running and queued threads but not threads in a worktree set, not idle threads with unsaved work, and only the coordinator's role; Move running threads lists only threads with "Keep ready to move" on, which is off by default; Move thread moves one. In specweave all 35 unarchived worktree threads on the M4 are worktree sets, so Leave this machine moves none of them.
5. **The automatic paths exist but are off and scattered.** A usage-limit hand off (0968) and a lid-close hand off (1267) are built. Their settings sit under three names (Handoff mode, Away target, provider limit action). The limit path already skips a machine on the same provider account; Away and a move by hand say nothing about it, although moving to the same account adds no usage.
6. **Real machines are not clean.** On November 18 the M4 had 179 uncommitted umbrella files, 11 umbrella branches with commits on no remote, an untracked `.specweave/project/credentials.json`, three worktrees whose Git data is gone, and repositories 2 to 99 commits behind (`~/.specwithcode/m4/evidence/m4-git-state/2026-11-18-m4-git-state.md`). Any flow that assumes a clean, pushed checkout either refuses or strands that work.
7. **A second coordinator reads as a healthy copy.** m1 holds an old coordinator record (epoch 2, active, no predecessor, left by "Start a coordinator here"). A copy with a live coordinator of its own has the role `also-main` and wears the same badge as a plain copy, "Copy · main on m4" (`apps/web/src/studio/workersOnlyCopy.ts:59`), so nothing tells him it needs a fix. The only Unlink control is in project settings (`ProjectMachinesSettings.tsx:525`).

Facts checked on `origin/main` of `repositories/anton-abyzov/specwithcode` at `af7b77f05` (1.0.346):

- Roles come from `copyRoles` (`apps/web/src/studio/projectDomain.ts:255`): main, also-main, moving, copy. `orchestratorCopies` (`apps/web/src/studio/projectCoordinatorMachine.ts`) adds independent. The menu is `apps/web/src/components/studio/OrchestratorSwitcher.tsx` (chip text at line 154, groups at 263 to 443). A row click navigates this window to `/projects/$projectKey?checkout=env:id` and reads that machine's server; it never opens the other machine's app.
- A message typed on a copy already goes to the coordinator's machine: `apps/web/src/components/studio/useRouteToMain.ts` calls `projects.coordinatorSend` there and then opens that machine's page (`onOpen`, line 80). It refuses without an operate grant or a live coordinator (`canRouteToMain`, `routeToMain.ts:45`) and with attached files (`routeToMain.ts:83`).
- "Make X main" is web policy over existing server calls: an online move through the machine handoff with `transport: "git-sync"` (`packages/contracts/src/machineHandoff.ts:63`, `apps/server/src/fleet/MachineHandoff.ts:1343` to 1410, `staleCopy: "refuse"`), or `projectLink.takeover` after `TAKEOVER_UNREACHABLE_MS` = 10 minutes (`apps/web/src/studio/projectLink.ts:113`). Takeover claims the new epoch on member machines (`apps/server/src/project/takeoverEpochClaims.ts`).
- **The git-sync move goes through origin.** The source pushes each repository's head to origin under a hidden ref (`git push origin {head}:{ref}`, `apps/server/src/fleet/handoffGit.ts:1155`, ref from `handoffRef(operationId, head)`, `handoffGitTypes.ts:68`), and the destination fetches that ref from origin (`handoffGit.ts:1250`). The dialog asks for it: "Push these commits and continue the project on {target}." (`MachineHandoffDialog.tsx:784`).
- **The idle check runs on both machines.** On the source before the push, and on the destination before the coordinator starts there ("…on {target}, so the coordinator hasn't started there yet", `apps/web/src/components/studio/handoffCopySteps.ts:337`). It counts every thread of the project that runs, waits for an answer, a sign-in or an approval, or has a tool call, effect or provider session open (`folderCopyPreparation.ts:73` to 130).
- **Routines travel only with the role-only handover.** `apps/server/src/project/CoordinatorPlannedHandover.ts:120` carries coordinator-owned routines and their run state. The git-sync move carries none.
- The folder copy already classifies each repository as `same`, `fast-forward`, `ahead`, `diverged`, `dirty`, `conflict`, `new`, `only-here` or `skipped` (`packages/contracts/src/folderCopy.ts:397`). Its planner can also stash (`apps/server/src/fleet/folderTransfer/reconcile.ts:460`) and `reset --keep` (`apply.ts:825`), which Sync must never do.
- A thread hand off carries a hidden checkpoint commit under `refs/specwithcode/handoff/`, parent HEAD, built with a private index (`apps/server/src/handoff/checkpointGit.ts:89`), sent as a Git bundle that leaves out the commits the receiver names (`exclude`, `apps/server/src/handoff/bundleGit.ts:108` to 128) and fails with `missing_prerequisites` when the receiver lacks the base (`:159`). Limits: 10 MB per file, 20,000 files, a 64 MB bundle (`packages/contracts/src/handoffMode.ts:35` to 44). A worktree set is refused (`WORKTREE_SET_HANDOFF_MESSAGE`, `apps/server/src/handoff/HandoffMoves.ts:26`).
- **The checkpoint leaves secrets out by file name only** (`isSecretLikeProjectPath`, `isUntrackedSecretConfigPath`, `checkpointGit.ts:133`). The content check (`apps/server/src/fleet/folderTransfer/secretContent.ts`) is used only by the folder copy and stops after 300 files and 64 KB per file (lines 16 and 18).
- Defaults: `defaultMode: "off"`, `sleepTarget: null`, `autoTakeoverMinutes: 0` (`handoffMode.ts:90`). Away's coordinator scope defaults to `live` (`apps/server/src/away/AwayPlanner.ts:758`). After a lid close the source's coordinator and the named threads are held on wake until the target says what it took (`apps/server/src/away/AwayWakeHold.ts`).
- The limit hand off moves a thread only at a real boundary (stopped on the limit, or idle at the threshold within 10 minutes of its last turn), only when the project rule is `switch` with machine targets, and never a review delegation (`apps/server/src/orchestration-v2/MachineLimitHandoff.ts:188` to 232 and 417).
- The app has no build-flag mechanism in `apps/web/src` or `packages/contracts/src`.

## Scope

In:

- New words everywhere a person or an agent reads them: machine menu, chip, message box, dialogs, Settings, thread menu, limit banner, command palette, tray and File menu, slash commands, iOS, translations, server messages and MCP tool descriptions. The table is in Wording.
- A machine menu whose rows say what is true (coordinator here, sync fact, offline, cannot open, second coordinator, separate project) and are greyed when they cannot be opened.
- A message box that tells the truth on a machine without the coordinator and offers "Continue here".
- **Sync**: Git first for a project that exists on both machines. **Add**: clone first for a machine that lacks it. The existing full compare stays as the slow path.
- **Hand off**: one dialog and one engine for threads, unsaved work, the coordinator conversation and its routines. It takes over the server work planned in increment 1389, which was abandoned on November 18 in favour of this one (umbrella PRs #179 and #180).
- Automatic hand off for chosen threads on sleep and at a usage limit, under one settings group.
- Headless fixtures for every changed surface, server tests on real Git repositories, and two-machine runs.

Out:

- The leadership model. One active coordinator per project, epochs, `takeover`, `supersede`, the epoch claims and the worker fence stay as they are. Contract values (`transferred`, `runs-workers`, `independent`, `copy-and-move`, `git-sync`) keep their names.
- Several coordinators at once, or merging two coordinator conversations.
- Showing another machine's coordinator conversation inside this machine's page, and holding a message to send later (both are alternatives of D-01, not designed here).
- A coordinator move that does not push to origin (the alternative of D-03).
- Moving sign-ins, running processes, terminals or dev servers. They never travel.
- Moving stashes, or a folder whose Git data is broken. Both are listed with the reason and stay.
- Continuous background file sync. Sync runs when asked, and before a hand off.
- Team rules, grants and device approval (1326, 1327). New calls get scopes from the existing set (AC-33).
- Personal projects (the personal assistant; `refusePersonal` in `ProjectLink.ts`). They show none of the new entries.
- The fleet's "Main machine" in Settings > Machines (the machine others pair to). It is another concept and keeps its name (D-20).

## The concept

A project lives on several machines as equals. Three verbs cover what happens between them:

| Verb | Moves | Used when |
|---|---|---|
| **Sync** | Files. Each machine fetches from the remote and fast-forwards; what is missing is cloned. Nothing is pushed. Work Git does not carry is offered as extras, ticked by hand. | The project is on both machines |
| **Add** | Files, first time. Download from GitHub, plus the same extras. | A machine does not have the project |
| **Hand off** | Work. Threads, unsaved work, the coordinator conversation and its routines continue on another machine. | Closing the laptop, a usage limit, or simply working elsewhere |

One fact replaces the roles: **"Coordinator on {machine}"**. The coordinator is the project's one planning conversation. It is work, so it is handed off like a thread. A person never assigns a role to a machine.

## Acceptance Criteria

Where an AC depends on a decision Anton has not made, it says "(D-xx)" and is written for the recommended choice.

### A. Words and the machine menu

- [ ] AC-01: No string a person or an agent reads matches a pattern in "Banned phrases" (below the Wording tables). The test `retiredPhrases.test.ts` greps the source of `apps/web/src`, `apps/desktop/src`, `apps/ios/SWCKit/Sources`, `apps/server/src/mcp`, `apps/server/src/away`, `apps/server/src/handoff`, `apps/server/src/fleet` and `apps/server/src/provider` (string literals and template text, not identifiers or comments) and the eight phrase files, minus the allowlist printed there. It is added in the Phase 1 pull request and passes there: Phase 1 renames every string, including those in dialogs that later phases replace.
- [ ] AC-02: The project page's chip names the machine whose page is shown ("On M5"), and reads "On", not "Runs on". After a click on a machine row the chip names that machine. This reverses what ships since 1.0.343 (PR #551), where the chip of a copy names the coordinator's machine. The invariant of PR #551 stays in a stronger form: the Send button carries no machine name at all, so it can never name a machine the chip does not. A test fails if the Send button's text contains a machine label.
- [ ] AC-03: The menu's first group is "{project} on your machines". A row has exactly one state, the first that matches:

  | # | Condition (from `copyRoles`, `orchestratorCopies` and the window's reach state) | Row shows | Pressable |
  |---|---|---|---|
  | 1 | This window never opened the machine, or the machine refuses this window | This window cannot open {machine} · Connect… | No, greyed |
  | 2 | `independent` | Separate project (in its own group, with "Link {machine} to this project…") | Yes |
  | 3 | Offline, and this window has saved state for it | Offline · last seen {time} · read-only | Yes; every action on the page is greyed |
  | 4 | `also-main` | Second coordinator · Fix… | Yes |
  | 5 | `moving` | Handing off the coordinator… | Yes |
  | 6 | `main` | Coordinator | Yes |
  | 7 | `copy` | (no role word) | Yes |

  Two notes can follow a pressable state: "Needs update · {version}" (the page opens; Sync and Hand off are greyed there) and "Old conversation kept" (today's "coordinator paused"). A row never shows a role. A machine without the project is not a row; it is offered in "Add to another machine…".
- [ ] AC-04: From Phase 2, a row for another machine than the one shown also carries one sync fact. It compares, repository by repository, that machine's checked-out commit and working tree with the same repository on the machine shown, from each machine's last `projectSync.status` (a local Git read, no network):

  | Fact | When |
  |---|---|
  | Same as {shown} | Every repository is at the same commit on both, and both working trees are clean |
  | {k} of {n} repositories differ | Anything else. The Sync dialog has the counts |
  | Not checked yet | A status is missing, or older than 10 minutes with the machine offline (then "as of {time}" follows the last known fact) |

  The row of the machine shown has no sync fact. Before Phase 2 no row has one.
- [ ] AC-05: The "Second coordinator" row (m1 on November 18) has "Fix…". It opens a dialog that says when that coordinator last ran and how many threads it started, and offers one action, "Unlink {project} on {machine}" (the existing Unlink with its confirmation), with the sentence "To make {machine} part of this project again, link it afterwards. Linking makes it give way to the coordinator on {main}." (true today: `accept` relinquishes the joining copy, `ProjectLink.ts:671`). Nothing touches threads or files. New server work: after an unlink, no reachable member's record names the leaving machine as coordinator or successor; a member that could not be reached is listed in the result and repaired when it next connects. "Start a coordinator here" is removed (D-06).
- [ ] AC-06: Below the rows the menu has "Sync…" (when another machine has the project; with several, the dialog starts with a machine picker) and "Add to another machine…" (only when a paired machine lacks the project). The group for the machine shown, "Work on {machine}", has "Hand off work…", and "Continue the coordinator here" when the coordinator is elsewhere. There is no other coordinator item in the menu. When the page shows another machine than the one this app runs on, "Hand off work…" opens with that machine as the source and this one preset as the target, so work can be brought here from here. A personal project shows none of these entries.

### B. The message box on a machine without the coordinator

- [ ] AC-07 (D-01): The coordinator's machine answers, this window may operate it, and the coordinator is running there. The line above the box reads "The coordinator for {project} is on {machine}. Send opens it there." The button reads "Send". It delivers the message through `projects.coordinatorSend` and opens the coordinator's page, as today; the chip then reads "On {machine}", because that is the page shown. "Continue here" sits next to it.
- [ ] AC-08: Every other state keeps the typed text in the box and sends nothing later on its own. The first matching row applies:

  | State | Line above the box | Send | Continue here |
  |---|---|---|---|
  | The draft has files | Files stay on this machine. Remove them to send the text, or open {project} on {machine} to attach them there. | Greyed | Enabled |
  | This window can only read the coordinator's machine | This window can only read {machine}, so it cannot send there. Open SpecWithCode on {machine}, or connect to it with full access. | Greyed | Greyed, same reason |
  | The coordinator is not running on its machine | The coordinator on {machine} is not running. | Greyed | Enabled |
  | The coordinator moved while the message was typed | The coordinator moved to {new}. Nothing was sent. | Enabled; it goes to {new} | Enabled |
  | {machine} silent for less than 10 minutes (D-05) | {machine} is not answering. Continue here unlocks in {m} min. | Greyed | Greyed, "in {m} min" |
  | {machine} silent for 10 minutes or more | (AC-09) | "Continue here and send" | Is the Send button |

- [ ] AC-09: Silent for 10 minutes or more: the primary button is "Continue here and send". It runs the existing takeover, then sends. The line says the coordinator starts from the shared goal, memory and plan, that its conversation on {machine} stays readable there, and that {machine} gives way when it is back. When the old machine returns, the page lists what it ran while disconnected (existing `ranWhileDisconnected`).

### C. Sync and Add

- [ ] AC-10: "Sync…" opens "Sync {project}: {a} and {b}". It lists the project's root repository and every nested repository the existing manifest scan finds (`handoffGit.ts:762` to 803; a tree past the scan limits is listed as skipped), each with its branch and state on both machines and what Sync will do there. Thread folders and worktree sets are not part of Sync; they are work, and Hand off moves them. Each machine runs `git fetch origin` for its own repositories. Nothing is fetched from the other machine, and nothing is pushed.
- [ ] AC-11: Per repository and per machine, Sync does exactly one of the following and says which:

  | State on a machine | Action | Sync says |
  |---|---|---|
  | Clean, behind its upstream, no commits of its own | `fast-forward` (`git merge --ff-only`) | Moved forward {n} commits |
  | Up to date | `none` | Up to date |
  | Clean, has commits its upstream lacks, not behind | `none` | {n} commits not pushed (listed as an extra) |
  | Has commits of its own and is behind | `fetch` | Has {a} commits of its own and is {b} behind. Not moved |
  | Has uncommitted changes | `fetch` | Not moved forward: {n} uncommitted files |
  | A running thread works in this very checkout | `fetch` | In use by {thread} |
  | On a different branch than the other machine | `fetch` | On {branch}. The other machine's branch is fetched; nothing is checked out |
  | Not on a branch | `fetch` | Not on a branch. Not moved |
  | Branch has no upstream | `none` | No upstream. Its commits are listed as an extra |
  | The fetch failed (offline, no access, remote gone) | `none` | Could not fetch: {Git's reason}. The other repositories continue |
  | Repository missing, has a remote | `clone` | Cloned from {remote} |
  | Repository missing, no remote | `none` | Not in Git on a remote. Use "Compare all files…" |

  A thread running in its own worktree does not block the project's main checkout (today's `notInUse`, `handoffGit.ts:713`, blocks on any linked worktree; Sync gets its own check). The plan type has exactly four actions: `none`, `fetch`, `fast-forward`, `clone`. Sync never resets, rebases, merges with a merge commit, stashes, switches a branch, deletes, pushes or commits, and never calls the reconcile paths that stash or reset. A server test on real repositories covers each row and asserts that the working tree, index, stash list and branch list of every repository that was not fast-forwarded are identical before and after.
- [ ] AC-12: Work that Git does not carry is listed per machine under "Only on {machine}", each line unticked: commits not pushed (per branch), branches that exist only there, and uncommitted and untracked files (count per repository). Stashes are listed and cannot be ticked ("Stashes stay. Compare all files… can bring them"). Secrets are a separate group (AC-14). Nothing in this list travels unless its line is ticked.
- [ ] AC-13: A ticked "commits not pushed" or "branches only on {machine}" line sends those commits to the other machine as a Git bundle over the link between the machines (the route a thread hand off uses, `apps/server/src/handoff/bundleGit.ts`). The destination first names the commits it has (its branch heads and remote-tracking heads); the bundle leaves those out. Nothing goes to the remote. The commits land as the same branch when that is a fast-forward there and the branch is not checked out with changes or in use, otherwise as `swc/from-{machine}/{branch}`. A ticked "uncommitted files" line arrives as one snapshot commit, built with a private index so the source's branch, index and working tree are unchanged, with the source's HEAD as its parent, on the branch `swc/from-{machine}/uncommitted-{yyyymmdd-hhmmss}-{id}` ({id} is six characters of the operation id, so two runs never collide). When HEAD has commits the destination lacks, they travel in the same bundle: the line reads "Includes {n} commits not pushed on {branch}" and ticking it ticks that branch's commits line, which then cannot be unticked alone.
- [ ] AC-14 (D-11): Every file that would enter a snapshot or a checkpoint (untracked, and tracked with changes) is checked by name (today's check) and by content (`tokenKind` of `secretContent.ts` on the first 64 KB of each file; the 300-file cap stays for folder scans and does not apply here). A file that is flagged, or that could not be read, is left out and listed under "Secrets and files left out". The dialog says what the check is: "Checked by file name and by the first 64 KB of each file. Look through the list before you send." It does not say "never". The same check runs for hand off checkpoints and for standby checkpoints, where it is cached per blob id so a turn re-checks only files that changed. A ticked secret travels sealed to the destination (the 1365 route): one missing there is ticked by default, one that exists there with different content is unticked and shows which side is newer. When the sealed route is unavailable the line says why and the secret stays.
- [ ] AC-15: "Add to another machine…" opens "Add {project} to {machine}" with "Download from GitHub (recommended)" selected, the folder, and the same "Only on {source}" extras, ticked as they are today (the November 15 default). "Copy the whole folder from {source}" is the second choice and the only one for a project with no remote. After Add the machine is linked into the project as today (`HandoffCopyDone.tsx:230` to 233) and is a row like any other. If linking fails, the row is "Separate project" with the reason and "Link {machine} to this project…". The coordinator does not move.
- [ ] AC-16: "Compare all files…" in the Sync dialog opens the existing measured copy (per-file compare, with its Undo). The Sync result screen lists each repository as done or not, with the sentence from AC-11, the extras that travelled, and "Check again".
- [ ] AC-33: Each new call has one scope from the existing set, written in `packages/contracts/src/clientRpcPermissions.ts` and covered by a new test, `clientRpcPermissions.test.ts`:

  | Call | Does | Scope |
  |---|---|---|
  | `projectSync.status` | Reads local Git state | `filesystem:read` |
  | `projectSync.fetch` | `git fetch origin` on that machine | `source-control:write` |
  | `projectSync.run` | Fast-forward and clone on that machine | `source-control:write` |
  | `projectSync.offerExtras` | The source builds a bundle or a snapshot on a hidden ref | `orchestration:operate` |
  | `projectSync.receiveExtras` | The destination takes a bundle | `source-control:write` |
  | Secrets | The existing `machineHandoffCopySecrets*` calls | Unchanged |

  A window that holds only read scopes on a machine sees its sync fact and gets "Sync…" greyed with "This window can only read {machine}". Calls between machines use the existing peer grant.

### D. Hand off

- [ ] AC-17: "Hand off work…" opens "Hand off work from {machine}" with a target picker, a scope ("{project}" or "Every project on {machine}") and one list with a tick per item, in the groups Running, Queued, Waiting for your next message, Not running with unsaved work, Project folder work, Coordinator conversation and Routines. A "Stays" group cannot be ticked and names why each item cannot go: a thread with a question, sign-in or approval pending ("Answer it first"), a review thread (D-10), an item over a limit (AC-34), a folder whose Git data is broken (its path). It replaces the Move running threads and Leave this machine dialogs.
- [ ] AC-18: A thread in a worktree set moves whole: every member repository's branch, commits and uncommitted files arrive in a worktree set on the target. If one member cannot move, none of that thread moves and the row names the member and the reason.
- [ ] AC-19: An idle or finished thread whose folder holds uncommitted files or commits on no remote is listed under "Not running, with unsaved work", ticked. It moves like a running thread and starts no turn on the target.
- [ ] AC-20 (D-04): "Project folder work" covers the project folder's own uncommitted files and branches that exist only on the source (the 179 files and 11 branches of November 18). It is ticked in a hand off and travels as AC-13 says, with the check of AC-14.
- [ ] AC-21: A hand off runs in this order.

  1. **Check.** Nothing moves. The source builds each ticked item's checkpoint on a hidden ref (private index; the working tree does not change) and measures it (AC-34). The coordinator's checks run now, not later: the target's version and scopes, the fast-forward check of every repository on the target (`checkExistingCopy`), the idle check on the target, and the idle check on the source counting only threads that are not ticked to go. The button is enabled when the check is done, and each row shows its result.
  2. **Sync the target** (AC-11).
  3. **Coordinator**, when ticked: the existing git-sync move with its conversation and `staleCopy: "refuse"`. New server work: the source's idle check leaves out exactly the threads of this operation, read from the source's own saved session record, never from the caller. This move pushes each repository's head to origin under a hidden ref (D-03), so when the source has commits that are not on origin the coordinator row carries today's consent line and cannot be ticked without it.
  4. **Coordinator-owned routines** and their run state, by the routine part of the planned handover, under the same operation id.
  5. **Threads**, one at a time.
  6. **Project folder work.**

  The coordinator goes before the threads because the destination refuses to start a coordinator while threads work there (`handoffCopySteps.ts:337`); Away hands the coordinator over first today for the same reason. Every partial result is a state the product already runs in, and the result screen names it with one next step:

  | What happened | State | Next step offered |
  |---|---|---|
  | The coordinator was refused in step 3 (the target cannot fast-forward, the target is busy, the coordinator is in the middle of a turn) | Nothing has moved | "Hand off the threads without the coordinator" or Cancel |
  | The coordinator moved; the routines step failed or got no answer | Routines stay on the source, paused; they never run on both | "Try the routines again" (replays the same operation id) |
  | The coordinator moved; a thread did not | That thread keeps working on the source for the coordinator on the target, as any thread on a second machine does | "Try again" |
  | A thread that is not ticked keeps working or waiting on the source | The coordinator row is greyed: "Stays while {n} threads keep working or waiting on {source}" | Tick them, or hand off without the coordinator |

  A server test proves that a thread the coordinator started before the move still reports to it afterwards in both cases: the thread moved too, and the thread stayed.
- [ ] AC-22: The target picker shows, per machine and per provider the moving threads use, "Different {provider} account · {n}% left", "Same {provider} account as {source}: adds no usage" or "Usage unknown". A same-account or unknown target is allowed by hand with that line, and is never chosen automatically.
- [ ] AC-23: The source keeps every file. Each moved thread stays readable on the source, marked "Handed off to {machine}", with "Bring back". A hand off that gets no answer is in doubt and is replayed under the same operation id, never reverted blindly (the 1267 rule).
- [ ] AC-24 (D-18, D-19): By hand, a coordinator that cannot move with its conversation stays, with its reason; the role-only handover is not used as a quiet fallback. In the scope "Every project on {machine}", a project with unfinished work has its coordinator ticked, and every other linked project's coordinator is listed unticked.
- [ ] AC-34: Limits are measured in the check, on the checkpoint or bundle that will travel: 10 MB per file, 20,000 files and a 64 MB bundle, each per repository (so per member of a worktree set, and per Sync extra). A row shows its measured size. An item over a limit is listed under Stays with the file or the count that exceeded it. If the item grew past a limit between the check and the run, it stays and the result says so.

### E. Automatic hand off

- [ ] AC-25: A thread's menu has "Hand off automatically" (Project default / On / Off), replacing "Keep ready to move". On keeps a standby copy of the thread on the hand off machine after each turn, and the thread shows "Standby on {machine} · saved {time} ago".
- [ ] AC-26 (D-02): Settings > Machines > Hand off has one row "When this machine goes to sleep": "Do nothing" (default) or "Hand off to {machine} after {n} minutes", with 2 minutes as the least (above the 90 seconds after which a lease counts as stale). The target continues the threads set to hand off automatically, each from its last standby copy, and takes the coordinator's role when one of them belongs to that project (the role-only handover, as today: the source is asleep and its conversation stays readable there). A turn that was running when the machine slept is not a safe point, and the spec does not claim it is: the standby copy is from the end of the turn before. The first prompt of a continued thread on the target therefore carries "The last turn on {source} was cut off at {time}. Check what it already did (commits, pushes, pull requests, messages) before repeating anything." On wake the source starts no turn in those threads or that coordinator until the target has said what it took (today's wake hold); a thread the target continued reads "Handed off to {target}" with "Bring back". The Hand off dialog's "Also do this when {machine} goes to sleep" sets the machine and turns the setting on for the ticked threads.
- [ ] AC-27: The same group has "When a usage limit stops a thread": "Ask me" (default; the banner offers "Hand off to {machine}") or "Hand off to a machine with usage left". Both existing orders stay ("Other machines first" and "This machine's models first"). A machine on the same account or with unknown usage never counts, a review thread never moves (D-10), and a thread set to Off never moves.
- [ ] AC-28: Every automatic hand off writes one line in the thread on both machines ("Handed off to M5 at 14:02: Claude usage limit on m4") and a notification, and can be undone with "Bring back".

### F. Everywhere else, and proof

- [ ] AC-29: The command palette, the desktop File menu, the tray, `/away` and `/back`, Settings > Machines, the thread menu and the limit banner use the Wording table's words. `/away` and `mod+alt+l` keep working and open the Hand off dialog with the scope "Every project on {machine}"; `/handoff` is added.
- [ ] AC-30: Translations in all eight languages, the iOS strings, the server messages and the MCP tool descriptions and errors that agents read use the new words. Tool names and parameters do not change.
- [ ] AC-31: Headless fixtures render the menu (every row of AC-03 and each fact of AC-04), the box states of AC-07 to AC-09, the Sync dialog with the November 18 state of the M4, the Add dialog, the Fix dialog and the Hand off dialog with each partial result of AC-21, light and dark, at 1280 and 390 px, with assertions on the greyed rows and on each "Stays" reason. The `away-mode` and `handoff-mode` fixtures, which no longer build at 1.0.345, are repaired or replaced. Server tests run on real Git repositories for AC-11, AC-13 and AC-14; the AC-14 case uses the M4's untracked `credentials.json`, a `notes.txt` holding a token, and a file whose token sits past the first 64 KB (which travels, and the test says so).
- [ ] AC-32: There is no build flag. Each phase is one pull request and one release, and ships only after its fixtures pass and a run between the M4 and the M5 is recorded in `reports/`. At the end Anton runs it himself: sync both ways, add a project to a machine without it, hand off two running threads (one in a worktree set) with the coordinator, close the lid with one thread set to hand off automatically, and bring the work back. His "accepted" closes the increment.

## Wording

Every string below was read at `origin/main` `af7b77f05` (1.0.346) of `repositories/anton-abyzov/specwithcode`. Prefixes: `web/` = `apps/web/src/`, `srv/` = `apps/server/src/`, `desk/` = `apps/desktop/src/`, `ios/` = `apps/ios/SWCKit/Sources/`. "(unchanged)" rows are listed so nobody has to wonder whether they were missed. Phase 1 changes every row; rows that need a later phase say so.

### 1. Machine menu, chip and rows

| Surface | Today | New |
|---|---|---|
| Chip (`web/components/studio/OrchestratorSwitcher.tsx:154`; it names the coordinator's machine through `composerMachines`, `web/studio/routeToMain.ts:26`) | Runs on {machine} | On {machine}, always the machine shown |
| Chip, screen readers (`OrchestratorSwitcher.tsx:249`) | Viewing {machine}. Choose a machine to view | (unchanged) |
| Group label (`:263`) | View this project on | {project} on your machines |
| Group note (`:266`) | Viewing moves nothing: work stays on each machine. Adding or moving the project asks first. | Pick a machine to see its threads and files. Nothing moves until you sync or hand off. |
| Row badge (`web/studio/workersOnlyCopy.ts:56`) | Main | Coordinator |
| Row badge (`workersOnlyCopy.ts:59`, also worn by a copy that runs a coordinator of its own) | Copy · main on {machine} / Copy | (no role word). From Phase 2 one sync fact: Same as {shown} / {k} of {n} repositories differ / Not checked yet |
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
| Item (`:353`) | Send to another machine… | Sync… (another machine has the project) and Add to another machine… (a paired machine lacks it) |
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
| Sidebar tooltip (built in `web/studio/projectDomain.ts:362` as "{name}: {role label}" joined by " · ") | {M4}: Main · {M3}: Copy · main on {M4} | On {M4} (coordinator) and {M3} |
| Sidebar badge (`web/studio/linkedMachines.ts:78`) | Handed off: coordinator on {machine}, {here} runs workers | Coordinator on {machine} |
| Sidebar badge (`linkedMachines.ts:82`) | Shared from {here} with {machines} | On {here} and {machines} |
| Sidebar row (`web/components/studio/shell/SidebarProjectList.tsx:667`) | Runs on {machine}. No copy on this device. | On {machine}. Not on this device. |
| Sidebar menu (`SidebarProjectList.tsx:960`) | Add to this machine… | (unchanged) |
| Settings button (`web/components/studio/ProjectMachinesSettings.tsx:494`; hook `useStartCoordinator`, `OrchestratorSwitcher.tsx:610`) | Start a coordinator here | (removed, D-06) |
| Fix dialog (new, opened by "Fix…" on a Second coordinator row) | (none) | {machine} runs a second coordinator for {project}. It last ran {time} and started {n} threads. · Unlink {project} on {machine} · To make {machine} part of this project again, link it afterwards. Linking makes it give way to the coordinator on {main}. |

### 2. Message box on a machine without the coordinator

| Surface | Today | New |
|---|---|---|
| Line (`web/components/studio/CoordinatorBlockedNotice.tsx:59`) | Main for {project} is {machine}. This copy takes work from there. | The coordinator for {project} is on {machine}. Send opens it there. |
| Line (`:63`) | Main for {project} is on another machine. This copy takes work from there. | The coordinator for {project} is on another machine that this window cannot reach. |
| Line (`:66`) | The conversation here is kept as history. | (unchanged) |
| Button (`:77`, `:78`) | Write to {machine}'s coordinator / Write to main's coordinator | (removed; Send does it) |
| Button (`:89`) | Make {machine} main | Continue here |
| Note (`:97`, `:101`) | Send delivers your message to {machine}'s coordinator and opens its page, where the answer comes. | (removed; the line above says it) |
| Note (`:108`, `:112`) | Write opens {machine}'s page for this project, where its coordinator answers. Nothing is sent from here. | (removed) |
| Note (`:122`) | {main} has been unreachable for 10 minutes or more. Making {machine} main starts from the shared goal, memory and plan; the conversation on {main} stays there as history. | {main} has been offline for {n} minutes. Continue here: the coordinator starts on {machine} from the shared goal, memory and plan. Its conversation on {main} stays readable there, and {main} gives way when it is back. |
| Note (`:126`) | Making {machine} main moves the coordinator and its conversation here from {main}, which becomes a copy. | Continue here syncs {machine}, then moves the coordinator conversation here from {main}. |
| Banner (`:171`, `:175`) | {machine} became main while {main} was unreachable. It started from the shared goal, memory and plan; the earlier conversation stays on {main} as history. | The coordinator continued on {machine} while {main} was offline. It started from the shared goal, memory and plan; the earlier conversation stays on {main} as history. |
| Placeholder (`ProjectWorkspaceSurface.tsx:2083`) | Message {machine}'s coordinator for {project}. | Ask the coordinator for {project} (on {machine}). |
| Placeholder (`:2089`, `:2093`) | Work for {project} starts on {machine}. / Work for {project} starts on another machine. | The coordinator for {project} is on {machine}, which is not answering. / …is on another machine. |
| Send (`web/components/studio/CoordinatorComposer.tsx:335`) | Send to {machine} | Send (never a machine name) / Continue here and send |
| Send tip (`CoordinatorComposer.tsx:327`) | Send to {machine}… | Goes to the coordinator on {machine} and opens it there |
| Send, screen readers (`:340`) | Send to the coordinator on {machine} | (unchanged) |
| Files refused (`web/studio/routeToMain.ts:83`) | Files stay on this machine. Remove them to send the text to main, or open main's page to attach them there. | Files stay on this machine. Remove them to send the text, or open {project} on {machine} to attach them there. |
| Error (`web/components/studio/useRouteToMain.ts:61`) | Main is not reachable from here. | The coordinator's machine is not reachable from here. |
| Error (`useRouteToMain.ts:77`) | Main did not confirm the message. | The coordinator's machine did not confirm the message. It may not have arrived. |
| New lines of AC-08 | (none) | This window can only read {machine}, so it cannot send there. Open SpecWithCode on {machine}, or connect to it with full access. · The coordinator on {machine} is not running. · The coordinator moved to {new}. Nothing was sent. · {machine} is not answering. Continue here unlocks in {m} min. |
| Problem (`projectCoordinatorMachine.ts:35`) | Work starts on another machine. This copy takes work from there. Switch to that machine above to send messages. | The coordinator is on another machine. Send opens it there. |
| Problem (`projectCoordinatorMachine.ts:33`) | Another machine took over this coordinator. It gives way once its machine is reachable; view the newer coordinator to send messages. | The coordinator continued on another machine. This one gives way once it is reachable; Send opens the newer one. |
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
| Refusal (`web/components/studio/handoffCopySteps.ts:302`, `:320`, `:337`) | {n threads} still working or waiting for you on {target}, so the coordinator stayed on {source}. {next step} / …on {source}, so the coordinator stayed there. {next step} / …on {target}, so the coordinator hasn't started there yet. {next step} | (unchanged; no role word) |
| Second-coordinator toast (`OrchestratorSwitcher.tsx:633`, `:640`) | {machine}'s coordinator runs again · Each coordinator keeps the threads it started. Nothing moved. | (removed with "Start a coordinator here", D-06) |

### 3. Sync and Add (today's Send dialog)

| Surface | Today | New |
|---|---|---|
| Trigger (`web/components/studio/MachineHandoffDialog.tsx:83`, `:86`) | Send this project to another machine / Send to another machine | Sync or add this project on another machine / Sync… |
| Title (`:297` to `304`) | Move {project} to {machine} / Copy {project} to {machine} / Move {project} to another machine / Copy {project} to another machine | Continue the coordinator on {machine} / Add {project} to {machine} / Add {project} to another machine |
| Title (`:295`) | Make {machine} main for {project} | Continue the coordinator on {machine} |
| Title, sync mode (`:286` to `291`; no caller opens it today) | Sync {project} to {machine} / {project} is synced to {machine} / {project} is on {machine} (copied {when}) | Sync {project}: {source} and {machine} / {project} is in sync on {source} and {machine} / {project} is on {machine} (added {when}) |
| Description, sync mode (`:314`) | {machine} already has this project at {folder}. Sync compares the two copies and adds what {machine} is missing: […] The coordinator stays on {source}. | Phase 1: {machine} already has this project at {folder}. Sync compares the two folders and adds what {machine} is missing: […] The coordinator stays on {source}. Phase 2: Git first. Each machine fetches from the remote and moves forward, fast-forward only. Nothing is overwritten and nothing is pushed. The coordinator stays where it is. |
| Description (`:316`) | Nothing on {machine} is replaced without asking. | (unchanged) |
| Description (`:312`) | The coordinator now runs on {target}. | The coordinator continues on {target}. |
| Header (`web/studio/sendToMachine.ts:175` to `179`) | From {source}. Main moves to {machine}. / From {source}. Main moves to the machine you choose. / From {source}. Main stays on {main}. / From {source}. Main stays where it is. | From {source}. The coordinator continues on {machine}. / …continues on the machine you choose. / From {source}. The coordinator stays on {main}. / From {source}. |
| Buttons (`MachineHandoffDialog.tsx:434`, `:461`) | Make {machine} main | Continue here |
| Buttons (`:435`, `:462`) | Move project to {machine} / Move project | Continue the coordinator on {machine} |
| Button (`:432`) | Moving… | Handing off the coordinator… |
| Button (`:730`) | Keep Main on {source} | Keep the coordinator on {source} |
| Note (`:546`) | Add this project on {machine} first, then hand it off there. | (unchanged) |
| Note (`:563`) | {machine} already has this project in this folder. Nothing is copied: only the coordinator conversation moves, and the code there comes from Git. | (unchanged) |
| List (`:571` to `576`) | What comes along · Committed work in every repository, through Git · Project goal, instructions, memory and the coordinator's threads · Stays on {source}: secrets, sign-ins […] | (unchanged) |
| Line (`:810`, `:817`) | {n} uncommitted files stay on {source}: Git carries commits only. Commit them, or choose Copy everything under Details. | {n} uncommitted files stay on {source}: Git carries commits only. Commit them, or take them along with Hand off work…. |
| Button (`:829`) | Commit for me | Commit on {source}… (lists the repositories it will commit in; never the default) |
| Review (`:706` to `708`) | {source} pushes its commits. {target}'s copy fast-forwards only where nothing there would be overwritten. […] / {source} pushes its commits, and {target}'s copy fast-forwards to them in every repository. […] | {source} pushes its commits. {project} on {target} fast-forwards only where nothing there would be overwritten. […] / {source} pushes its commits, and {project} on {target} fast-forwards to them in every repository. […] (the push stays, D-03) |
| Consent (`:784`) | Push these commits and continue the project on {target}. | Push these commits and continue the coordinator on {target}. |
| Methods (`web/components/studio/ProjectMoveOptions.tsx:297`) | Download from GitHub (recommended) | (unchanged, and the default) |
| Methods (`ProjectMoveOptions.tsx:303`) | Copy everything | Copy the whole folder from {source} (Add) / Compare all files… (Sync) |
| Methods (label `ProjectMoveOptions.tsx:309`, detail `:311`) | Git only, no file copy · Continues in a folder already saved there, which updates from origin. Always moves Main there. | (removed as a choice; "Continue the coordinator here" does it) |
| Picker (`ProjectMoveOptions.tsx:194`, `:213`) | Copy to send to · Main | Folder on {machine} · Coordinator |
| Refused (`ProjectMoveOptions.tsx:351`, `:353`) | Not available: that machine already has Main. / Not available: it would move Main into a project this copy is not linked to. | (removed with the choice) |
| Refused (`ProjectMoveOptions.tsx:126`) | Main cannot move to {machine} from here: {source} is not linked to the project {machine} belongs to. […] | The coordinator cannot continue on {machine}: it has this repository as a separate project. Link it first. |
| Destination (`sendToMachine.ts:139`) | {there} has {n} copies of this project. Pick the one to send to. | {there} has this project in {n} folders. Pick one. |
| Destination (`sendToMachine.ts:142`) | {there} already has Main, at {folder}, so there is nothing to move. | {there} already has the coordinator, at {folder}. |
| Destination (`sendToMachine.ts:143`) | {there} already has a copy, at {folder}. Only what it is missing is copied. | {there} already has this project, at {folder}. Sync brings it up to date. |
| Plan (`sendToMachine.ts:227` to `246`) | Work continues on {there}, and this copy stops starting work. / Push this machine's commits, then move Main to {into}. | The coordinator continues on {there}. / Push this machine's commits, then continue the coordinator in {into}. |
| Plan (same lines) | Copy the folder to {there} / Copy {n} changed local files into {into} / Compare with {into} and copy what it is missing | (unchanged) |
| Not linked (`sendToMachine.ts:166`, `:170`) | From {source}. {source}'s copy is not linked to the project {machine} belongs to (Main: {main}). | From {source}. {machine} has this repository as a separate project (coordinator on {main}). |
| Not linked (`sendToMachine.ts:194`, `:198`) | Only files are copied into {machine}'s copy. Main stays on {main}, and {source} is not linked to that project. To make them one project, link {source} to it from the machine menu. | Only files go into {machine}'s folder. Its coordinator stays on {main}. To make them one project, link {source} to it from the machine menu. |
| Done (`web/components/studio/HandoffCopyDone.tsx:145`, `:146`) | {machine} has a copy. Main stays on {main}. / {target} has a copy. The coordinator stays here. | {project} is on {machine}. The coordinator stays on {main}. / …stays here. |
| Done (`HandoffCopyDone.tsx:128`) | The files are on {target}, but {problem}. Copy again: it compares first and moves only what changed. | The files are on {target}, but {problem}. Sync again: it compares first and moves only what changed. |
| Done (`:143`) | Files are copied. Hand off the coordinator once work here is idle. | (unchanged) |
| Done buttons (`:648`, `:676`, `:692`) | Copy again / Copy changes again | Sync again |
| Done button (`:653`) | Hand off coordinator now | Continue the coordinator on {target} |
| Done button (`:671`) | Make {machine} main | Continue the coordinator on {machine} |
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
| Link picker (`web/components/studio/ProjectLinkCandidates.tsx:36`) | Pick the copy of {project} on another machine. Each copy keeps its own coordinator, and you can switch Main any time. | Pick {project} on another machine. Linking makes them one project with one coordinator. |
| Link picker (`ProjectLinkCandidates.tsx:40`) | Pick the copy of {project} on another machine. Each copy keeps its own coordinator; Main stays on {main} and you can switch it any time. | Pick {project} on another machine. The coordinator stays on {main}; you can continue it on another machine any time. |
| Release reason (`web/components/studio/ProjectMachineHandoff.tsx:730`) | Main stays here: the copy there could not fast-forward. | The coordinator stays here: {project} there could not fast-forward. |
| Error (`ProjectMachineHandoff.tsx:743`) | That move is no longer waiting on this machine. Check where Main is now before moving again. | That hand off is no longer waiting on this machine. Check where the coordinator is now before trying again. |
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
| Groups (`web/components/away/awayDialog.logic.ts:67` to `69`) | Threads / Routines / Coordinators | Phase 1: Threads / Routines / Coordinator conversations. Phase 3: Running / Queued / Waiting for your next message / Not running, with unsaved work / Project folder work / Coordinator conversation / Routines / Stays |
| Row states (`awayDialog.logic.ts:81` to `84`) | Moves / Ready to move / Stays / Pauses | Goes / Stays, with a standby copy on {target} / Stays / Pauses |
| Empty (`awayDialog.logic.ts:111`) | Nothing here needs to move. | Nothing unfinished here. |
| Confirm (`AwayDialog.tsx:571`) | Running and queued threads, routines and coordinators listed as Moves go to {target} now. The rest stay here and are listed in the summary. {target} becomes your Away target: the next Leave and closing the lid use it. Change it in Settings, Machines. | Phase 1: Running and queued threads, routines and coordinators listed as Goes continue on {target} now. The rest stays here and is listed in the summary. {target} becomes your hand off machine: the next hand off and closing the lid use it. Change it in Settings, Machines. Phase 3: Everything ticked goes to {target} now. The rest stays here and is listed in the summary. (The sleep machine is set only by its own tick, D-16.) |
| Buttons (`:603`, `:612`) | Leave for {target} / Leaving… / Leave | Hand off to {target} / Handing off… / Hand off |
| Session (`:413` to `421`) | Bring work back / Bring work back from {target} / Away on {target} | (unchanged) / (unchanged) / Handed off to {target} |
| Button (`:455`) | Bring back / Bringing back… | Bring work back / Bringing work back… |
| Button (`:387`) | Run here anyway… | (unchanged) |
| Access (`:523`, `:548` to `551`) | Needed first ({n}) / Request access / Request sent | (unchanged) |
| Access request (`web/components/away/awayAccessRequests.logic.ts:90`) | Let this machine take over a coordinator | Let this machine continue a coordinator |
| New lines of AC-21 and AC-22 (Phase 3) | (none) | Stays while {n} threads keep working or waiting on {source} · Hand off the threads without the coordinator · Try the routines again · Different {provider} account · {n}% left · Same {provider} account as {source}: adds no usage · Usage unknown · Answer it first · Checked by file name and by the first 64 KB of each file. Look through the list before you send. |
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
| Refusal (`srv/handoff/HandoffMoves.ts:27`) | This thread works in a worktree set across several repositories, and a handoff carries one repository. Finish it on this machine, or push each repository's branch and continue on the other machine from there. | (unchanged until Phase 3; then gone, because it moves. If a member cannot: "{repository} cannot be handed off: {reason}. Nothing of this thread moved.") |
| Preflight (`srv/handoff/handoffPreflight.ts:64`) | no {path}. Send it with studio_file_transfer, or with Copy to another machine | Phase 1: no {path}. Send it with studio_file_transfer, or with Add to another machine. Phase 2: …or tick it in Sync |
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
| Project machines (`ProjectMachinesSettings.tsx:641`, `:228`) | Take over the coordinator on {machine}? / Take over did not finish. Retry it. | Continue the coordinator on {machine}? / The coordinator did not continue on {machine}. Try again. |
| Standby (`web/components/studio/CoordinatorStandbySettings.tsx:168`, `:207`) | Take over automatically on / Take over after | Continue the coordinator automatically on / After |
| Standby (`CoordinatorStandbySettings.tsx:198`) | How long this machine must stay quiet before the other copy takes over. | How long this machine must stay quiet before the other machine continues the coordinator. |
| Hand off settings (`web/components/settings/HandoffModeSettings.tsx:199`) | How long the target waits after the lid closes before it takes over. | How long the target waits after the lid closes before it continues the work. At least 2 minutes. |
| Fleet pairing (`web/components/settings/FleetInvite.tsx:235`, `:274`, `web/components/settings/machineNextStep.logic.ts:171`) | Main machine ID / Main machine | (unchanged; the machine others pair to, D-20) |
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
| `ios/SWCFeatures/Linked/LinkedProjectViews.swift:73`, `:77` | Take over the coordinator on {machine}? / Take over | Continue the coordinator on {machine}? / Continue here |
| `ios/SWCFeatures/Linked/LinkedProjectViews.swift:133`, `:134` | Another copy can take over this coordinator when its machine stops answering. […] / Take over automatically on | Another machine can continue this coordinator when its machine stops answering. […] / Continue automatically on |
| `ios/SWCFeatures/Linked/LinkedProjectState.swift:88`, `:116` | […] Check the machines and take over again […] / Take over did not finish. Retry it. | […] Check the machines and continue here again […] / The coordinator did not continue here. Try again. |
| `ios/SWCFeatures/Chat/OrchestratorSwitcher.swift:70` (screen reader label of the machine shown) | Coordinator on {machine} | Viewing {machine} |
| `ios/SWCSync/LinkedProjects.swift:288`, `:295`, `:296` | Update SpecWithCode on {machine} to take over. / {machine} has been unreachable for 10 minutes or more. This copy can take over the coordinator. / …can take over the coordinator in {n} min. | Update SpecWithCode on {machine} to continue the coordinator there. / {machine} has been offline for 10 minutes or more. The coordinator can continue here. / …can continue here in {n} min. |
| `ios/SWCSync/LinkedProjects.swift:300` to `308`, `:358` | Took over from {machine} {time}. […] / {machine} took over {time}. Review the coordinator turns this copy ran after that. | (unchanged, D-25), except "this copy" becomes "this machine" |
| `ios/SWCSync/LinkedProjects.swift:426`, `:428` | {machine} has a copy of {project} and is switched off on this phone. […] / {n} machines with a copy of {project} are switched off on this phone. […] | {machine} has {project} and is switched off on this phone. […] / {n} machines with {project} are switched off on this phone. […] |
| `ios/SWCFeatures/Chat/HandoffSheet.swift:24` | Move this conversation and its checkpoint to another machine. The source becomes read-only. Opening these options does not move anything. | Hand off this conversation and its files to another machine. It becomes read-only here. Opening these options moves nothing. |
| `HandoffSheet.swift:56`, `:83` | Hand off to {name} / Hand off thread | (unchanged) |
| `HandoffSheet.swift:92` to `98` | Handoff ready / Checkpoint catching up / Handoff paused | Standby copy ready / Standby copy catching up / Hand off paused |
| MCP `studio_thread_migrate` (`srv/mcp/toolkits/orchestrator/tools.ts:383`) | Move threads this coordinator owns to another machine through handoff. […] omit them to move every running handoff-mode thread of this project. | Hand off threads this coordinator owns to another machine. […] omit them to hand off every running thread of this project that is set to hand off automatically. |
| MCP `studio_handoff_ready_list` (`tools.ts:396`) | List this project's threads that another machine replicated here through handoff mode […] | List this project's threads that have a standby copy here from another machine […] |
| MCP `studio_thread_continue_here` (`tools.ts:410`), `studio_project_add_to_machine` (`srv/mcp/toolkits/project/tools.ts:182`), `studio_machine_list` (`srv/mcp/toolkits/machines/tools.ts:14`) | (no Main or Copy wording) | (unchanged) |
| MCP error (`srv/mcp/toolkits/orchestrator/migrate.ts:284`) | studio_thread_migrate moves threads to another machine; name one from studio_machine_list. | studio_thread_migrate hands threads off to another machine; name one from studio_machine_list. |
| MCP error (`srv/mcp/toolkits/project/addToMachine.ts:507`) | {machine} has this project as {id} at {folder}, but it is not linked to the project here […] studio_machine_list shows it as this project's copy on {machine}. | {machine} has this repository as a separate project, {id} at {folder} […] studio_machine_list shows this project on {machine}. |
| MCP errors (`srv/mcp/toolkits/project/remoteLaunch.ts:412`, `:461`) | This project already names a copy on {machine}, and it cannot be used now […] Do not add another copy. / {named} on {machine} is not a copy of this project's repository that can be linked. […] | This project is already on {machine}, and it cannot be used now […] Do not add it again. / {named} on {machine} is not this project's repository, so it cannot be linked. […] |
| Agent instructions (`srv/provider/StudioOrchestrationInstructions.ts:25`) | `studio_thread_migrate` moves an existing thread's execution […] Switching the viewed orchestrator never moves a thread. | `studio_thread_migrate` hands an existing thread off to another machine […] Switching the viewed machine never moves a thread. |

Tool names, parameters and contract values do not change.

### Banned phrases (AC-01)

The test matches these patterns against string literals and template text, case-sensitive:

| Pattern | Catches |
|---|---|
| `\bMain\b(?! machine)` | Main, Main for, Main stays, Main moves, has Main, switch Main, Keep Main |
| `\b[Mm]ake \{?\w+\}? main\b`, `\bmain on \{`, `\b(is|became|become|becomes) main\b`, `\b[Mm]oving main\b`, `\bmove[sd]? main\b`, `\bmain's\b`, `\bto main\b` | Make {machine} main, Copy · main on {machine}, {machine} is main now, Moving main, main's coordinator |
| `takes work from` | This copy takes work from there |
| `Send to another machine`, `Send this project to another machine` | The old entry |
| `[Mm]ove [Rr]unning [Tt]hreads`, `Leave [Tt]his [Mm]achine`, `Leave for \{` | The two old dialogs and their menu, palette, tray and File menu entries |
| `[Rr]eady to move`, `Away target`, `Away on \{` | Keep ready to move, Away target, Away on {target} |
| `Start a coordinator here`, `Take over coordinator here`, `Take over the coordinator`, `Take over automatically` | The old coordinator actions |
| `Git only, no file copy`, `Not linked:` | The old method and the old label for a separate project |

Allowlist, exact strings: "Main machine", "Main machine ID" (D-20).

Not banned, because a pattern cannot tell the role from the ordinary word: "copy" ("standby copy", "Copy the whole folder") and "took over" (D-25). Their role uses are replaced row by row above, and the fixtures assert the new text.

## Approach

Four phases, each its own pull request and release (AC-32). No flag: the app has none, and two sets of 200 strings would have to live side by side.

**Phase 1, words and an honest menu. Web, desktop, iOS and server strings only. No new call between machines, no server logic.**
- A new `apps/web/src/studio/machineRowState.ts` maps a member's `copyRoles` role (or `independent` from `orchestratorCopies`) plus the window's reach state to one row of AC-03. `OrchestratorSwitcher.tsx` renders rows from it, disables row 1 and drops the per-machine coordinator items.
- `composerMachines` (`routeToMain.ts`) stops substituting the coordinator's machine into the chip. Send loses its machine name. A new `coordinatorBoxState.ts` maps today's inputs (`canRouteToMain`, files, the silence clock of `makeMain.ts`) to the rows of AC-07 to AC-09, and `CoordinatorBlockedNotice.tsx` renders them. `useRouteToMain.ts` keeps its behaviour: send there, then open that page.
- "Send to another machine…" becomes "Sync…" and "Add to another machine…", both opening today's dialog under the new titles. "Move running threads…" and "Leave this machine…" become "Hand off work…" with the two scopes, opening today's two dialogs with the new words.
- "Start a coordinator here" is removed (D-06), and the Fix dialog of AC-05 is added over the existing Unlink.
- Every string of the Wording tables, the eight phrase files, the palette, the desktop menu and tray, iOS strings, server messages and MCP descriptions.

**Phase 2, Sync and Add.**
- New contract `packages/contracts/src/projectSync.ts`: `status`, `fetch`, `run`, `offerExtras`, `receiveExtras`, with the scopes of AC-33. The plan type is the closed set of AC-11.
- New server module `apps/server/src/fleet/ProjectSync.ts`. It enumerates repositories with the manifest scan of `handoffGit.ts`, runs `git fetch origin` and `git merge --ff-only` on its own machine under the project's admission lock, and clones a missing repository through the Add-to-machine clone path. It does not use `git.materialize`, which needs a ref published to origin, and it does not use the reconcile planner, which can stash and reset.
- Extras in `apps/server/src/fleet/ProjectSyncExtras.ts`: a bundle built with `bundleGit.ts` and its `exclude` list, sent over the folder-transfer route; the snapshot commit built as `checkpointGit.ts` builds a checkpoint. The content check of AC-14 goes into a new `apps/server/src/handoff/snapshotSecrets.ts` that `checkpointGit.ts` calls, so every checkpoint gets it.
- The sync fact of AC-04 comes from `projectSync.status`, read when the menu opens and cached for 60 seconds.
- Web: a new `ProjectSyncDialog.tsx`; the Add entry keeps `MachineHandoffDialog.tsx`; the measured copy stays behind "Compare all files…".

**Phase 3, Hand off (the server work 1389 planned, in a different order).**
- Worktree-set checkpoints in a new `apps/server/src/handoff/HandoffSetMoves.ts` (one checkpoint per member under one lease, all or nothing).
- `apps/server/src/away/AwayPlanner.ts` plans queued threads, idle threads with unsaved work, project folder work, same-account and unknown-usage facts, a project scope and the measured sizes.
- A new `apps/server/src/away/HandOffCoordinatorStage.ts` runs steps 3 and 4 of AC-21: the git-sync move with the source idle check's leave-out list, then the routines. `makeProjectIdleCheck` gets an optional set of thread ids to leave out, filled only from the saved session. `AwayRunner.ts` calls the stages in the new order.
- Web: one `HandOffDialog.tsx` replaces `HandOffMachineDialog.tsx` and `AwayDialog.tsx`. The Away session, wake card and Bring back keep their engine.

**Phase 4, automatic.**
- `HandoffThreadModeSetting` (inherit, off, on) stays and is shown as "Hand off automatically". `sleepTarget`, `sleepTrigger` and `graceMinutes` stay and are shown as one row, with the 2 minute floor. The limit rule keeps `providerLimitAction`, `providerLimitMachineTargets` and `providerLimitTargetOrder`; a thread set to Off is excluded in `limitHandoffTrigger`. The cut-off line of AC-26 goes into the seed a continuation carries (`HandoffTurnGate.pendingSeed`).

**File sizes.** Three files are already over the 1,500 line rule: `HandoffMoves.ts` (1,563), `CommandPalette.tsx` (4,467) and `Sidebar.tsx` (5,797). They get string edits only; no task adds lines to them. `ProjectMachineHandoff.tsx` (1,344) and `AwayRunner.ts` (1,266) get new logic in the new files named above.

**Single writer, unchanged.** One active coordinator per logical project at the highest epoch. "Continue here" is today's Make main. A takeover still waits 10 minutes and still claims the epoch on member machines. Plan claims and memory writes keep their current owner. What changes is that a person sees where the coordinator is and continues it, instead of assigning a role.

**Rejected:**
- *Every machine runs its own coordinator, with a lock only on the plan.* Two conversations plan the same goal and split the context. Anton rejected it on November 16 (1372), and nothing he said on November 18 asks for it back.
- *Threads first, then the coordinator* (1389's order). The destination refuses to start a coordinator while the threads that just arrived work there.
- *"Retire" a second coordinator in place.* `supersede` (`ProjectLink.ts:1177`) needs the predecessor to be the caller and an epoch at or above the binding's, which m1's record cannot meet. Unlink, then link again, reaches the same end over existing calls.
- *Push before every sync.* A push publishes work. Sync sends unpushed commits directly, and only when ticked.
- *Commit uncommitted work on the person's branch.* A snapshot branch on the target is reversible; a commit on his branch is not his choice.
- *Keep "Leave this machine" as a second entry.* It is the same dialog with a wider scope.
- *Copy a folder with broken Git data as plain files.* It needs its own discovery, route, size cap and secret rules. The folder is listed with its path and stays.
- *Continuous file sync.* It fights running threads for the working tree.

**Risks:**
- Phase 1 changes about 230 strings at once. The banned-phrase test of AC-01 and the fixtures are the guard.
- The sync fact can be stale. It reads "Not checked yet" instead of guessing, and the dialog always fetches.
- The leave-out list of the idle check is new behaviour in a safety check. It is filled only from the source's own session record, and AC-21's reporting test must pass before Phase 3 ships. If it cannot be made safe, the coordinator moves only when every thread is idle, as today, and the dialog says so.
- The content check reads 64 KB per file. A token further into a file travels. The dialog says what was checked.
- A sent bundle is capped at 64 MB per repository. A larger item stays and points to "Compare all files…".
- Reordering the Away stages changes what an in-doubt session resumes. The saved stage is per item, so a resume reads both orders.
- Mixed versions: a machine without `projectSync` shows "Needs update" and offers the measured copy.

## Round 1 responses

Review round 1: `reports/reviews/review-muse-wonder-full-1.0-1.md`, verdict "fix first". Every claim was checked against `af7b77f05` before it was accepted.

| Id | Finding | Response |
|---|---|---|
| C1 | "Continue here" pushes to origin while the words say nothing is pushed; Sync on `materialize` needs a published ref | Accepted. Sync gets its own fetch and fast-forward path and never pushes (AC-10, Approach Phase 2). The coordinator move keeps its push and its consent line (AC-21 step 3, D-03) |
| C2 | "Retire it" cannot work through `supersede` | Accepted. Retire is gone; Fix offers Unlink, and linking again makes the machine give way (AC-05, Rejected) |
| C3 | Snapshot secret exclusion is by name only | Accepted. Name and content check on every file of a snapshot or checkpoint, unreadable files left out, wording without "never", stated 64 KB limit (AC-14, AC-31) |
| C4 | Routines do not travel on the git-sync path | Accepted. Step 4 of AC-21 and its partial result |
| C5 | Threads move before a coordinator move that can still refuse | Accepted, and the order is reversed: the coordinator's checks run in the check step and the coordinator moves before the threads (AC-21) |
| C6 | Snapshot parent, bundle basis and branch name undefined | Accepted. AC-13 |
| C7 | New cross-machine write calls have no scopes | Accepted. AC-33 |
| H1 | Phase 1 is not free of new data flow | Accepted. The sync fact moved to Phase 2 (AC-04); the in-place conversation and the held message are gone |
| H2 | Row states contradict each other and cannot be decided | Accepted. One state per row by precedence (AC-03), one sync fact with its reference and age (AC-04); a machine without the project is not a row |
| H3 | "Start a coordinator here" still creates second coordinators | Accepted as a question for Anton, recommended to remove (D-06) |
| H4 | Wording table misses strings; the test must grep source | Accepted. Rows added in every table; "Banned phrases" and its allowlist; AC-01 greps source |
| H5 | Task files incomplete | Accepted. T-04 lists all eight phrase files; T-05 lists every dialog and string file |
| H6 | Sync table misses states | Accepted. AC-11 has ahead, fetch failure, not on a branch and the in-use rule; AC-10 names how repositories are found |
| H7 | Queued threads missing; broken folders have no route | Accepted. Queued is a group (AC-17). Broken folders are listed and stay (Scope, Rejected) |
| H8 | Automatic hand off races a running turn | Accepted. AC-26 drops "safe point", sets the 2 minute floor, adds the cut-off line and names the wake hold |
| H9 | Box states drop today's refusals | Accepted. AC-08 lists them; nothing is held for later |
| H10 | The chip rule and the in-place conversation contradict | Accepted. The page always shows one machine; Send opens the coordinator's page (AC-07). In place is an alternative of D-01 |
| H11 | Three behaviours of 1389 were dropped silently | Accepted. They are D-02, D-18 and D-19, with AC-24 |
| H12 | Limits cannot be known before the button | Accepted. The check step builds and measures (AC-21 step 1, AC-34) |
| M1 | Base the row state on `copyRoles` | Accepted (AC-03, Approach) |
| M2 | The same-account claim is wrong for the limit path | Accepted (Problem 5) |
| M3 | Fence Sync to fast-forward in the planner contract | Accepted (AC-11 closed action set and its test) |
| M4 | Asked decisions are prejudged in the ACs; D-10 and D-11 belong to Anton | Accepted. They are Asked, and each AC that depends on a decision is marked |
| M5 | Mockup contradictions | Accepted. The mockup is redone to match |
| M6 | Unknown usage, both limit orders, the standby rule | Accepted (AC-22, AC-27; standby rows in Wording 5) |
| M7 | The flag has no mechanism; file line limits | Accepted. No flag (AC-32); file sizes in Approach |
| M8 | Linking on Add and its failure; personal projects | Accepted (AC-15, AC-06, Scope) |
| L1 | Three paraphrased rows | Accepted. Fixed to the exact strings |
| L2 | No entry on the target side | Accepted (AC-06) |
| L3 | Server Git tests and build steps | Accepted (AC-31, T-07, T-08, T-15) |

## Reviews

Reviewer: muse, model `muse-wonder-full-1.0`, effort xhigh, adversarial, named by Anton.

- Round 1: fix first. `reports/reviews/review-muse-wonder-full-1.0-1.md`.
- Round 2: on this revision.

## Decisions

### Asked (waiting for Anton; each has a recommended choice, and the ACs are written for it)

- D-01 Typing on a machine without the coordinator. Recommended: Send opens the coordinator where it is, and "Continue here" is one click away (today's mechanism, new words). Alternative A, closest to "you should be able to proceed there": Send brings the coordinator to the machine you type on whenever the project is idle on the other one; each switch pushes commits and moves a conversation, and it refuses while threads work there. Alternative B: the answer shows on this page without leaving it; one page would read two machines, which is a new data flow not designed here.
- D-02 Automatic hand off defaults. Recommended: off (the November 12 decision), offered at the moment it helps: the limit banner and the "Also do this when {machine} goes to sleep" tick. Alternative, which is 1389's AC-08: once a sleep machine is chosen, every running thread keeps a standby copy and continues there on sleep, at the cost of a checkpoint after every turn.
- D-03 The coordinator move pushes commits to origin under a hidden ref, as shipped in PR #560. Recommended: keep it, with the consent line. Alternative: build a transport that sends them directly, like a thread hand off; that is a fifth phase.
- D-04 Uncommitted project folder files in a hand off. Recommended: ticked, arriving as a `swc/from-{machine}/uncommitted-…` branch. Alternative: unticked, so they stay unless chosen. In Sync they are always unticked.
- D-05 The 10 minute wait before "Continue here" when the coordinator's machine is silent. Recommended: keep it (1372). Alternative: allow at once behind a confirm that both machines may run the coordinator until the old one is back.
- D-06 "Start a coordinator here" in a project's machine settings, kept by 1372 as the way to revive a coordinator. It is what left m1 with a second coordinator. Recommended: remove it; "Continue the coordinator here" does the reviving. Alternative: keep it in Settings.
- D-10 Review threads in a hand off. Recommended: they stay on their machine, by hand and automatically, because the reviewer lock does not travel. Alternative: allow by hand with a warning.
- D-11 Secrets. Recommended: one missing on the destination is ticked, one that differs there is unticked (the November 13 default). Alternative: every secret unticked.
- D-18 A coordinator that cannot move with its conversation. Recommended: by hand it stays and says why; on sleep, with the source gone, the target takes the role only, as today. Alternative, which is 1389's AC-03: fall back to the role-only handover by hand too.
- D-19 Coordinators in the scope "Every project on {machine}". Recommended: ticked for projects with unfinished work, listed unticked for the rest. Alternative, which is 1389's AC-04: one switch between "projects with live work" and "every linked project".

### Defaulted (change any before sw-do)

- D-07 The verb is "Hand off" (two words; "hand off" in sentences; the settings group is "Hand off").
- D-08 The coordinator's location reads "Coordinator" on a row and "Coordinator on {machine}" in sentences. The words Main and Copy are not used as roles anywhere. "Copy" stays as an ordinary word ("standby copy", "Copy the whole folder").
- D-09 `/away` and `mod+alt+l` stay as shortcuts to the wide scope. The project menu has one entry, "Hand off work…".
- D-12 "Fix…" on a second coordinator is a person's click, never automatic.
- D-13 A same-account or unknown-usage target is allowed by hand with its line, and never chosen automatically.
- D-14 The sync fact reads local Git only. Only the Sync dialog fetches from the remote.
- D-15 Extras are unticked in Sync and ticked in Add, where today's default already brings local changes from the source.
- D-16 A hand off no longer sets the sleep machine as a side effect (today the first Leave makes its target the Away target). Only the "Also do this when {machine} goes to sleep" tick or Settings sets it.
- D-17 An offline machine with saved state stays openable, read-only. Only a machine this window cannot open is greyed.
- D-20 The fleet's "Main machine" and "Main machine ID" (`web/components/settings/FleetInvite.tsx:235`, `:274`, `web/components/settings/machineNextStep.logic.ts:171`) keep their words. They name the machine others pair to, not a project role, and are the allowlist of AC-01.
- D-21 No build flag. Phases ship one by one (AC-32).
- D-22 In a hand off the coordinator moves before the threads (AC-21).
- D-23 Stashes and folders with broken Git data are listed and stay.
- D-24 No message is held to be sent later. Text stays in the box until a button is pressed while the other machine answers.
- D-25 "Took over" stays as the past-tense report of an offline takeover ("m5 took over from m4 at 14:02"). The buttons and titles that start one read "Continue here".

### Reverses

- "One Copy to another machine flow" (1325, November 13): one entry becomes Sync and Add. The rule against a separate Move entry stays.
- "One main, switch any time" (1372, November 16): the mechanism stays; the words Main, Copy and Make X main go, and "Start a coordinator here" goes with D-06.
- Away mode as the one way to leave (1267, November 10): its engine stays as the wide scope of Hand off; the menu entry and the name go.
- 1389 "Leave this machine takes everything": abandoned on November 18 (umbrella PRs #179 and #180); its server work is Phase 3 here, with the coordinator before the threads.
- The chip rule of specwithcode PR #551 (1.0.343), which made the chip name the coordinator's machine: the chip now names the machine shown, and Send carries no machine name.
- PR #560 (1.0.346) stays as the engine of "Continue here": push, fast-forward every repository, name the one that cannot, and keep the coordinator where it is on a refusal. Only its words change.

### Open

- Whether Sync should offer "Keep in sync" (pull when a machine is idle and clean). Left out until the manual flow has run on real machines.

## Tasks

### T-01 Row states, greyed rows and the chip
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCoordinatorMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectDomain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/workersOnlyCopy.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/routeToMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/routeToMain.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspace.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/machineRowState.test.ts src/studio/routeToMain.test.ts

### T-02 The message box on a machine without the coordinator
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorBoxState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/coordinatorBoxState.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useRouteToMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorComposer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useMakeMain.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/coordinatorBoxState.test.ts src/studio/makeMain.test.ts

### T-03 Menu entries, the Fix dialog, palette, tray, File menu and slash commands
- AC: AC-05, AC-06, AC-29 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/SecondCoordinatorFix.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachinesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorStandbySettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/composerAppCommands.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/threadActionMenu.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/DesktopApplicationMenu.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopLifecycle.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/coordinator-menu/vite.config.ts && node apps/web/tests/coordinator-menu/verify.mjs

### T-04 Phrases in all eight languages, iOS strings, agent-facing strings, and the banned-phrase test
- AC: AC-01, AC-30 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/retiredPhrases.test.ts, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/Handoff.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/LinkedProjects.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/HandoffSheet.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/OrchestratorSwitcher.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Linked/LinkedProjectViews.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Linked/LinkedProjectState.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/LinkedProjectResolverTests.swift, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/migrate.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/addToMachine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/i18n/retiredPhrases.test.ts src/i18n/i18n.test.ts

### T-05 New words in every existing dialog, setting and server message (strings only)
- AC: AC-01, AC-29 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/sendToMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMoveOptions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyDone.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyScanFreshness.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyFooter.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/handoffCopySteps.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkCandidates.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/SidebarProjectList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/useProjectLinkSuggestions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/linkedMachines.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AddToMachineDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/threadMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/LimitHandoffCandidates.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffMachineDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffThreadDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/away/AwayDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/away/awayDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/HandoffModeSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectHandoffModeSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineFallbackSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/Sidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/hooks/useThreadActionMenu.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPreflight.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/i18n/retiredPhrases.test.ts

### T-06 Unlink leaves no record that names the leaving machine
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectLink.test.ts

### T-07 Project sync contract, scopes and server, tested on real repositories
- AC: AC-04, AC-10, AC-11, AC-33 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSync.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/ProjectSync.test.ts packages/contracts/src/clientRpcPermissions.test.ts

### T-08 Extras: commits by bundle, the snapshot branch, the secret check, sealed secrets
- AC: AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSyncExtras.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSyncExtras.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/snapshotSecrets.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/snapshotSecrets.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/checkpointGit.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/ProjectSyncExtras.test.ts apps/server/src/handoff/snapshotSecrets.test.ts

### T-09 Sync dialog, Add dialog and the sync fact on rows
- AC: AC-04, AC-10, AC-12, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectSyncDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSyncDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSyncDialog.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/projectSyncDialog.logic.test.ts

### T-10 Worktree-set threads move whole
- AC: AC-18 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffSetMoves.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffSetMoves.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/checkpointGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/bundleGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffReceiver.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/handoff/HandoffSetMoves.test.ts

### T-11 Hand off plan: queued and idle threads, project folder work, usage facts, scope, measured sizes
- AC: AC-17, AC-19, AC-20, AC-22, AC-24, AC-34 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/away.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/away/AwayPlanner.test.ts

### T-12 Hand off runner: check, sync, coordinator, routines, threads, folder work, and each partial result
- AC: AC-21, AC-23 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/away/HandOffCoordinatorStage.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/HandOffCoordinatorStage.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderCopyPreparation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/MachineHandoff.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/away/HandOffCoordinatorStage.test.ts apps/server/src/away/AwayRunner.test.ts

### T-13 One Hand off dialog
- AC: AC-17, AC-21, AC-22, AC-23, AC-24, AC-34 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/handOffDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/handOffDialog.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/away/AwayDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffMachineDialog.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/handoff/handOffDialog.logic.test.ts

### T-14 Automatic hand off: per thread, on sleep, at a limit
- AC: AC-25, AC-26, AC-27, AC-28 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/HandoffModeSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/LimitHandoffCandidates.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/MachineLimitHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitHandoffPreflight.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffTurnGate.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffNote.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/limitHandoffPreflight.test.ts

### T-15 Headless fixtures for every changed surface, built and run
- AC: AC-31 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/project-sync/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-sync/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/project-sync/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && for f in coordinator-menu project-sync away-mode; do node node_modules/vite-plus/bin/vp build --config apps/web/tests/$f/vite.config.ts && node apps/web/tests/$f/verify.mjs || exit 1; done

### T-16 Two-machine runs per phase, and Anton's acceptance
- AC: AC-32 | Files: .specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/acceptance.md | Test: test -s .specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/acceptance.md

### T-17 Verify and close 1390
- AC: AC-01, AC-32 | Files: .specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/closure.md | Test: specweave verify 1390-sync-projects-across-machines-and-hand-off-work
