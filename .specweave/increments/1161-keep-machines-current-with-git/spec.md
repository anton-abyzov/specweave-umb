# 1161 Keep machines current with Git

## Problem

The header says "Copy to ministorm is waiting for your review" days after two copies finished. The dialog shows an unfinished comparison from October 29, 2026 at 6:30 PM EDT (`d97c138e`): 72 files and 7 repositories "would be replaced", of which 67 files are identical today and M4 is newer on the rest. A preview never closes when a later copy finishes.

Keeping a second machine current means running that heavy file comparison again, while a new thread on Ministorm starts from a stale checkout. The user wants Git to carry committed work: fetch and fast-forward when a thread starts or the coordinator moves there, with the copy kept for first setup and what Git cannot carry.

## Scope

In: closing superseded previews, including the stale record already on Ministorm; a best-effort repository sync at a thread's first turn and at a coordinator's first turn after a move; a coordinator move with no file copy and no refusal for a dirty checkout; unpushed work shown before a move; the "Copy local files" wording and default.

Out: creating, copying or changing credentials or remotes; pushing from the source; syncing repositories in the background; changing how the file copy itself works.

## Acceptance Criteria

- [ ] AC-01: When a copy finishes, every other unfinished comparison for the same target folder and source project is closed, and the record on disk says `cancelled`.
- [ ] AC-02: On service start, a comparison older than a finished copy of the same target and source project is closed, so the October 29 record clears after the update without anyone pressing a button.
- [ ] AC-03: A saved pointer to a closed comparison is removed, and the banner no longer shows after an app restart.
- [ ] AC-04: A thread's first turn fetches every repository of the project (the project, its containing workspace, nested and environment repositories) from origin, and fast-forwards a clean checkout on origin's default branch that is strictly behind.
- [ ] AC-05: A checkout with uncommitted changes, on another branch, diverged, or in use by another running thread is fetched but its files, HEAD and index are untouched. Each is named in a short plain notice with the reason.
- [ ] AC-06: An unreachable origin never stops a thread: the first turn still runs and the notice names the repository. A new worktree whose origin fetch fails starts from the local base instead of failing the launch. Sync time is capped at 30 seconds.
- [ ] AC-07: An SSH origin this machine cannot reach is fetched over its HTTPS form with the machine's existing Git login, without changing the remote, config or any credential.
- [ ] AC-08: Nothing is shown when every repository was already current. The same skip text is not repeated for a project within one hour.
- [ ] AC-09: A coordinator move using Git needs no file copy, is not refused for uncommitted work on either machine, and the destination runs the same sync at the coordinator's first turn, including a thread that already has runs.
- [ ] AC-10: Before a move, the dialog lists what stays on the source, per repository: unpushed commits on the current branch, uncommitted changes, and local branches that are ahead or have no upstream.
- [ ] AC-11: The dialog's files action reads "Copy local files" and says what it is for. A move to a machine that already has the project defaults to Git, and a machine without it defaults to the copy.
- [ ] AC-12: Live: on released Ministorm, a new thread fast-forwards a clean repository and skips a dirty one with the files byte-identical, and the October 29 comparison is closed.

## Approach

Banner: `destinationService.ts` closes superseded previews in `finish` and `resume`; `HandoffFolderCopyWatcher.tsx` drops the pointer of a cancelled copy.

Sync: `apps/server/src/fleet/repositorySync.ts` holds target discovery, fetch, safety checks, fast-forward and notice text as plain async functions over real Git, like `folderTransfer/git.ts`. `apps/server/src/project/ProjectRepositorySync.ts` wraps the provider session's `startTurn`, like `ProjectEnvironmentRuntime`, and records a `system_notice`. Fast-forward uses `merge --ff-only --no-overwrite-ignore` with hooks off.

Move: a new `git-sync` handoff transport skips publish and materialize, and checks only that the root repository's identity matches. `MachineHandoff.ts` marks the project so its next first turn syncs. A new read-only RPC reports unpushed work on the source.

Rejected: `git pull` (merges, stops on a dirty tree); relaxing the push-and-fetch handoff in place (its refusals protect exact heads that older clients still rely on); a background timer (the user asked for thread start and move).

Risks: an older destination refuses the new transport for that one move, per the version skew policy. Fast-forwarding while a person edits by hand with no thread running is limited by the clean check and by Git refusing to overwrite.

## Decisions

### Asked

- D-01 Build the banner fix and Git sync, fast-forward only when safe (user, November 1, 2026).
- D-02 No key creation or credential change on Ministorm (user).

### Defaulted (change any before sw-do)

- D-03 Untracked files count as uncommitted, so that checkout is not fast-forwarded. Strict, because the rule is "never touch files".
- D-04 Only origin's default branch is fast-forwarded; any other branch is reported as skipped.
- D-05 No settings toggle. The rule is safe by construction, and a toggle can follow if the notices prove unwanted.
- D-06 The move does not push. Unpushed work stays visible on the source, as the user asked.
- D-07 The HTTPS fallback runs at fetch time, so `specweave-umb` and `greet-anton` work with no remote change. Switching their `origin` remains optional and is left to the user.

### Open

- none

## Tasks

### T-01 A finished copy closes its comparison
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationService.superseded.test.ts, apps/web/src/components/studio/HandoffFolderCopyWatcher.tsx, apps/web/src/components/studio/HandoffFolderCopyWatcher.test.tsx | Test: cd apps/server && pnpm exec vp test run src/fleet/folderTransfer/destinationService.superseded.test.ts && cd ../web && pnpm exec vp test run src/components/studio/HandoffFolderCopyWatcher.test.tsx

### T-02 Repository sync
- AC: AC-04, AC-05, AC-06, AC-07, AC-08 | Files: apps/server/src/fleet/repositorySync.ts, apps/server/src/fleet/repositorySync.test.ts, apps/server/src/project/ProjectRepositorySync.ts, apps/server/src/project/ProjectRepositorySync.test.ts, apps/server/src/orchestration-v2/ProviderTurnStartService.ts, apps/server/src/orchestration-v2/ThreadLaunchService.ts | Test: cd apps/server && pnpm exec vp test run src/fleet/repositorySync.test.ts src/project/ProjectRepositorySync.test.ts src/orchestration-v2/ThreadLaunchService.test.ts

### T-03 Coordinator move over Git and unpushed work
- AC: AC-09, AC-10 | Files: packages/contracts/src/machineHandoff.ts, packages/contracts/src/folderCopy.ts, packages/contracts/src/machineHandoffRpc.ts, packages/contracts/src/clientRpcPermissions.ts, apps/server/src/fleet/handoffGit.ts, apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/MachineHandoff.gitSync.test.ts | Test: cd apps/server && pnpm exec vp test run src/fleet/MachineHandoff.gitSync.test.ts src/fleet/MachineHandoff.test.ts

### T-04 Copy local files
- AC: AC-10, AC-11 | Files: apps/web/src/components/studio/MachineHandoffDialog.tsx, apps/web/src/components/studio/ProjectMoveOptions.tsx, apps/web/src/components/studio/ProjectMachineHandoff.tsx, apps/web/src/components/studio/HandoffLeftBehind.tsx, apps/web/src/studio/machineHandoff.ts, docs/user/moving-a-project.md | Test: cd apps/web && pnpm exec vp test run src/components/studio/ProjectMachineHandoff.test.tsx src/components/studio/MachineHandoffDialog.test.tsx

### T-05 PR, release and live check on Ministorm
- AC: AC-12 | Files: none | Test: live receipt under .specweave/increments/1161-keep-machines-current-with-git/reports/

### T-06 Verify and close 1161
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12 | Files: none | Test: specweave verify 1161-keep-machines-current-with-git
