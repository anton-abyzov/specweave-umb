# 1389 Leave this machine takes everything to another machine

## Problem

Anton, November 18, 2026: he is working on the M4 with commits and uncommitted work in progress, the project already has a copy on the M5, and he wants to close the laptop and carry on from the M5 (for example because the M4's provider is out of tokens). He asked which menu does that, and whether every thread moves, only the coordinator, or only running threads.

In 1.0.345 the answer is spread over five entries that each move a different slice. None of them moves everything:

- **Make m5 main** (machine chip menu, This project). Moves the coordinator, its conversation and committed Git state. It refuses while any thread of the project is running or waiting ("N threads are still working or waiting for you on m4, so the coordinator stayed there"). Uncommitted files stay on the M4 unless the person presses Commit for me, which commits only the project root's repository, or picks Copy everything under Details.
- **Leave this machine…** (Away mode; same menu, On m4 group, also `/away`, the File menu, the tray and `mod+alt+l`). Moves running and queued threads with their uncommitted files (a hidden checkpoint commit), routines, and the coordinators of projects that have live work. Its coordinator handover (`CoordinatorPlannedHandover`) moves only the role and epoch: the M5's own coordinator thread takes over, the M4's coordinator conversation stays behind, and no Git is pushed or fast-forwarded. The dialog always sends `coordinatorScope: "live"`, so an idle project's coordinator stays on the M4.
- **Move running threads…** lists only running threads that have Keep ready to move on (`handoffMachineCandidates`), so it is usually empty.
- **Move thread…** (a thread's ⋯ menu). Moves one thread, idle or running, with its conversation, commits and uncommitted files into a new worktree on the M5.
- **Send to another machine…** copies files. It moves Main only on Git only.

Two gaps make Away, the decided one-action path (increment 1267), unusable for this project:

1. A thread in a worktree set (several repositories in one thread folder) never moves (`WORKTREE_SET_HANDOFF_MESSAGE` in `HandoffMoves.ts`). The specweave project has Use worktrees on, and the M4 has 40 worktree-set manifests under `~/.specwithcode/m4/worktrees/specweave-umb/`. Away lists those threads as "Stays: Finish it here", so most of Anton's real work stays on the M4.
2. Idle and finished threads are not in the plan, even when their worktrees hold uncommitted or unpushed work. Closing the laptop strands that work.

On tokens: every move checks only that the M5's provider is installed, on and signed in (`handoffPreflight.ts`). If both Macs use the same Claude or Codex account, the limit is shared, and the move gains no tokens. Only the limit banner's "Move to {machine}" (Settings > Models > Other machines) skips a machine on the same account. Away and Move thread say nothing.

## Scope

In:
- Away moves worktree-set threads, one repository at a time, as one move per thread.
- Away lists idle threads that hold unsaved work and offers to bring them.
- Away's coordinator item uses the Make-main path (git-sync with the fast-forward from 1379/PR 560, plus the coordinator conversation) after the threads have left, so the project is idle when it runs.
- An option to move every linked project's coordinator, not only live ones.
- The same-account warning in the Away and Move thread previews.
- Clearer menu wording: Leave this machine is the one "take everything" entry, and Move running threads no longer looks empty for no reason.

Out:
- Moving secrets or provider sign-ins (they never travel; the M5 uses its own).
- Changing Make main's rules or the copy dialog.
- Bring back changes beyond carrying the same items back.
- Live processes (dev servers, terminals): they never move.

## Acceptance Criteria

- [ ] AC-01: A thread whose folder is a worktree set moves with Leave this machine. Every member repository's branch, commits and uncommitted files arrive in a worktree set on the target, and the thread continues there. If any member cannot move, nothing of that thread moves, and the plan row names the member and the reason.
- [ ] AC-02: The Leave this machine plan lists idle and finished threads whose worktree holds uncommitted files or unpushed commits under "Has unsaved work (N)", each with a checkbox, ticked by default. A ticked one moves like a running thread but does not start a turn. An unticked one stays and is named in the result.
- [ ] AC-03: When Leave this machine hands over a coordinator, the target ends up with the source's coordinator conversation and with every repository fast-forwarded to the pushed commits, the same result as Make main. It runs after the threads stage, and the old "planned handover" (role only) is used only when the source is offline or the Make-main path is refused.
- [ ] AC-04: The Leave this machine dialog has "Coordinators: projects with live work / every linked project", and the choice reaches `away.preflight` and `away.start` as `coordinatorScope`.
- [ ] AC-05: When the target's provider account for a moving thread is the same account as the source's, and the source's usage for that provider is at or over the switch threshold, the plan row and the Move thread dialog say "{target} uses the same {provider} account, so this does not add usage". The move is still allowed.
- [ ] AC-06: In the machine chip menu, "Leave this machine…" carries the hint "Threads, unsaved work, routines and Main go to the machine you pick". "Move running threads…" says how many threads it would list, and shows "None set to Keep ready to move" when it lists none.
- [ ] AC-07: A headless fixture shows the plan for the scenario: two running threads (one in a worktree set), one idle thread with uncommitted files, a coordinator, and a same-account target. Captures are taken light and dark at 1280 and 390 px.

## Approach

Server first, then the dialog.

1. `apps/server/src/handoff/checkpointGit.ts`, `bundleGit.ts`, `HandoffMoves.ts`, `HandoffReceiver.ts`: a worktree-set checkpoint is a list of per-member checkpoints under one lease and epoch. The receiver builds a set with `planWorktreeSet` and applies each member. The move is all-or-nothing: the members are preflighted together, then held and taken over together.
2. `apps/server/src/away/AwayPlanner.ts`: add `unsaved` thread facts (idle threads whose worktree is dirty or ahead of upstream, read with the existing VCS status), with the item action `move` when it is selected. Add the same-account fact from the provider usage summary per machine.
3. `apps/server/src/away/AwayRunner.ts`: put the coordinators stage after the threads stage. Call `MachineHandoff` git-sync with `staleCopy: "refuse"`, and fall back to `CoordinatorPlannedHandover` only on unreachable or refusal, recording which path ran.
4. `apps/web/src/components/away/AwayDialog.tsx`, `awayDialog.logic.ts`: the unsaved group with checkboxes, the coordinator scope choice, and the same-account line.
5. `apps/web/src/components/studio/OrchestratorSwitcher.tsx`: hints and the empty-state note. `apps/web/src/components/handoff/HandOffThreadDialog.tsx`: the same-account line.
6. Fixture: repair `apps/web/tests/away-mode` (its mocks miss `useThreadShell`, `useEnvironment` and `useMachineReachStates` at v1.0.345, so it no longer builds) and add the scenario.

Rejected:
- A sixth menu entry, "Take everything to M5". Away already is that entry by decision (1267). Closing its gaps beats adding another path.
- Making Make main move threads. It is a coordinator switch, and it refusing busy work is correct for that job.

Risks:
- A worktree-set move is larger, and the bundle cap (`too_large`) applies per member.
- Reordering the stages changes what an in-doubt session resumes. The stage is saved per item, so a resume must read the old order too.

## Decisions

### Asked
- none yet. Anton asked for the proposal, not the build.

### Defaulted (change any before sw-do)
- D-01 The fix extends Leave this machine (Away) instead of adding a new entry (decision 1267: Away is the one-action way to leave).
- D-02 Idle threads with unsaved work are ticked by default (Anton's case is "I'm leaving, take my work"). Unticking keeps one here.
- D-03 Same account is a warning, not a block (a person may move for reasons other than tokens).
- D-04 The coordinator scope default stays "projects with live work" (the 1267 default). "Every linked project" is one click.
- D-05 The coordinator handover in Away uses git-sync with `staleCopy: "refuse"`: a target copy that cannot fast-forward keeps the coordinator here and says why, as Make main does since PR 560.

### Open
- Should Leave this machine also commit uncommitted files in the project root (outside any thread) the way Commit for me does, or carry them as a snapshot? Proposed: carry them as a snapshot on a `from-<machine>` branch, never committing on the person's branch without asking.

## Tasks

### T-01 Worktree-set threads move as one
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/handoff/checkpointGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/bundleGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffReceiver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/handoff/HandoffMoves.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/handoff/HandoffMoves.test.ts

### T-02 Away plans unsaved idle threads, same-account rows and coordinator scope
- AC: AC-02, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayPlanner.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/away.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/away/AwayPlanner.test.ts

### T-03 Away hands coordinators over by the Make-main path after threads
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/away/AwayRunner.test.ts

### T-04 Dialog and menu wording
- AC: AC-02, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/away/AwayDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/away/awayDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/handoff/HandOffThreadDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/away/awayDialog.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/away/awayDialog.logic.test.ts

### T-05 Headless scenario fixture
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/away-mode/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/away-mode/vite.config.ts && node apps/web/tests/away-mode/verify.mjs

### T-06 Verify and close 1389
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1389-leave-this-machine-takes-everything/reports/closure.md | Test: specweave verify 1389-leave-this-machine-takes-everything
