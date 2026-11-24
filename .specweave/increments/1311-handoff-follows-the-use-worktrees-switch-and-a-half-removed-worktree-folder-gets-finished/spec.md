# Handoff follows the Use worktrees switch, and a half-removed worktree folder gets finished

## Problem

On November 11, 2026 a thread handed off from the Minisforum to the M4 landed in a new worktree (`fortnite-3js-handoff-...-e1`) although the fortnite-3js project has Use worktrees off. The same happened in the specweave project. The takeover step (`takeoverLocked` in `apps/server/src/handoff/HandoffReceiver.ts`) always runs `git worktree add`; it never reads the project's switch, unlike every other launch path (`projectUsesWorktrees` in `mcp/toolkits/project/launchWorkspace.ts`). The owner noticed on November 12: "Investigate why, for the Fortnite project, we use the worktrees. I believe it should not be there."

The same day a second leftover turned up: `~/.specwithcode/m4/worktrees/specwithcode-dev/1276-umbrella-repos`, 2.8 GB, half deleted and no longer registered with Git. `git worktree remove` unregisters a worktree even when it cannot delete every file (a build was still writing into `node_modules`), and `removeWorktree` in `apps/server/src/vcs/GitVcsDriverCore.ts` reported the failure and left the folder, which no later removal can reach because Git no longer knows it.

## Scope

In: where a takeover puts arriving work when the project's switch is off; a notice saying where the work went and why; a retry that does not apply the work twice; finishing a removal Git gave up on halfway; tests and docs for both.

Out: the "Recommended for this folder" hint in project settings (1276, AC-31); worktrees made by scheduled tasks that saved a worktree strategy; restoring a missing thread worktree; whole-folder machine copies under `fleet/`.

## Acceptance Criteria

- [ ] AC-01: With Use worktrees off, a takeover into a project folder that is clean and at the checkpoint's base commit puts the work there as uncommitted changes, creates no worktree and no branch, leaves HEAD and the checked-out branch as they were, and starts the thread in the project folder.
- [ ] AC-02: With Use worktrees off, a project folder that already holds exactly the checkpoint's changes (the source worked in that folder on the same machine) is used as it is: nothing is applied and no worktree is made.
- [ ] AC-03: With Use worktrees off, a project folder that has other uncommitted changes, is at another commit, is in the middle of a merge or rebase, or has a file (also one Git ignores) where the work adds a path is left untouched; the work gets its own worktree as before. So does work that belongs to a repository below the project folder.
- [ ] AC-04: The takeover's notice says where the work went: the project folder (and the branch, when it differs from the source's), or a worktree together with the reason the folder could not take it.
- [ ] AC-05: A takeover retried after a failed start does not apply the work twice and does not move it: work first put in the project folder stays there, work first put in a worktree stays there.
- [ ] AC-06: With Use worktrees on, a takeover behaves as before, including a clean project folder that is not touched.
- [ ] AC-07: When `git worktree remove` exits non-zero but has unregistered a worktree that was registered before the call, the app deletes the folder that is left and prunes; the removal succeeds and no folder stays behind. When Git cannot say whether the path is still registered, nothing is deleted.
- [ ] AC-08: A failed removal of a path that was never a registered worktree still fails and deletes nothing.
- [ ] AC-09: In the released app, a handoff into a project with Use worktrees off lands in the project folder (checked on a throwaway project between two machines, or on one machine between sign-ins).

## Approach

1. `apps/server/src/handoff/bundleGit.ts`: `applyCheckpointInPlace` (HEAD equals base, no unfinished merge or rebase, index refreshed, clean status or `holdsCheckpoint`, no file on disk where the checkpoint adds a path, two-tree `read-tree -u -m`, `reset -q`).
2. `apps/server/src/handoff/HandoffReceiver.ts`: `takeoverLocked` reads the switch with the existing `projectUsesWorktrees`; a worktree already registered for this takeover wins (retry); work for a repository below the project folder keeps its worktree, because a thread in the project folder would not run Git there; otherwise it tries the project folder and falls back to `materialize`. The launch uses `{ type: "root" }` for the folder. A retry needs no marker: a folder that already holds the work is used as it is, and one that lost it gets it again.
3. `apps/server/src/vcs/worktreeRegistration.ts` (new, the driver file is far over the size limit) and `GitVcsDriverCore.ts`: `removeWorktree` notes whether the path was registered before the call and finishes the folder when Git unregistered it and failed. The registration check has three answers (yes, no, unknown); only a positive no deletes.
4. Docs: `docs/studio/workspaces-and-consolidation.md`, `docs/operations/worktree-cleanup.md`.

Rejected: refusing the handoff when the project folder cannot take the work (the handoff would fail while the source is already paused); switching the project folder's branch to the source's branch (nothing may switch a shared folder's branch); `read-tree --reset` in the project folder (it writes over untracked files).

Review (2026-11-12, first commit): four confirmed findings fixed in the second commit: a failed `worktree list` read as unregistered, a retry marker trusted without looking at the folder (marker removed), nested-repository work applied in place while the thread started at the project root, and a stale index or mid-merge folder.

Review of the merged head (3d64b0d3cd, merged as 915c196aba in PR 243): ship. Left open, all low: no rollback of an in-place apply when a later takeover step fails (a retry is safe; changing the switch before retrying would leave the work in the folder and in a worktree); a `read-tree` that fails after it began writing (disk full) reports "files in the way" with a partial copy left; `REBASE_HEAD` and `sequencer` are not in the unfinished-operation list (the dirty check covers them in practice).

Risk: Git 2.34 and later write over ignored files during a merge-style checkout, so the apply checks the disk itself for every path the checkpoint adds.

## Decisions

### Asked
- D-01 When the project folder is busy (other changes, another commit) and the switch is off: still use a worktree and say why, or stop and ask to free the folder? Put to the owner on November 12, 2026; no answer yet. Built: the worktree with a notice.
### Defaulted (change any before sw-do)
- D-02 The project folder takes the work on whatever branch is checked out there; the notice names both branches when they differ.
- D-03 The switch is read as every launch path reads it: only the project's own "worktree" choice counts as on, so a project that never touched the switch counts as off.
- D-04 Shipped as one pull request to anton-abyzov/specwithcode, built in a scratch copy of main because the shared checkout was in use.
### Open
- none

## Tasks

### T-01 Takeover puts work in the project folder when the switch is off
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/handoff/bundleGit.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/handoff/HandoffReceiver.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/handoff/handoffIncoming.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/handoff/handoffMove.test.ts, repositories/anton-abyzov/specwithcode-dev/docs/studio/workspaces-and-consolidation.md | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/handoff/

### T-02 Worktree removal finishes a folder Git left half deleted
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/vcs/GitVcsDriverCore.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/vcs/worktreeRegistration.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/vcs/GitVcsDriverCore.test.ts, repositories/anton-abyzov/specwithcode-dev/docs/operations/worktree-cleanup.md | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/vcs/GitVcsDriverCore.test.ts

### T-03 Review, pull request, merge and release
- AC: AC-01, AC-07 | Files: .specweave/increments/1311-handoff-follows-the-use-worktrees-switch-and-a-half-removed-worktree-folder-gets-finished/spec.md | Test: gh pr view --repo anton-abyzov/specwithcode --json state --jq .state

### T-04 Check a handoff in the released app
- AC: AC-09 | Files: .specweave/increments/1311-handoff-follows-the-use-worktrees-switch-and-a-half-removed-worktree-folder-gets-finished/spec.md | Test: specweave-studio --version

### T-05 Verify and close 1311
- AC: AC-09 | Files: .specweave/increments/1311-handoff-follows-the-use-worktrees-switch-and-a-half-removed-worktree-folder-gets-finished/spec.md | Test: specweave verify 1311
