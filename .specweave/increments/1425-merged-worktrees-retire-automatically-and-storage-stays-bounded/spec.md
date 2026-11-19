# Merged worktrees retire automatically and storage stays bounded

## Problem

The app's storage sweep (increment 1370, app 1.0.384) is the only remover of chat worktrees, and it removes almost nothing. Its traces on the M4 show 10 runs and zero removals, while a manual pass on November 19, 2026 found 15 of 77 folders whose work was merged, pushed and clean.

Evidence, read on `origin/main` at `9a30e314e` and on the M4:

- **Open chats keep merged work.** `decideFinishedWorktree` (`apps/server/src/finishedWorktrees.ts:269-287`) keeps a folder as "open" unless its head chat is resolved or archived, or its pull request merged and the chat has been quiet for 6 hours. Chats are rarely marked resolved. The database holds 15 head chats that are neither archived nor resolved and whose last run ended (12 completed, 2 cancelled, 1 failed).
- **A record of a session keeps a folder.** 254 agent sessions read "ready"; the sweep keeps a folder as "in use" for such a record even when no process works in it (6 folders in the plan of November 17).
- **Ignored bookkeeping keeps a folder.** `.specweave/state/.gc-last` (SpecWeave's maintenance marker, in 60 of 61 umbrella worktrees) counts as "an ignored file that may hold data". So do `__pycache__`, `.specweave/logs/`, lock files and gitignored review reports.
- **The sweep never stops running.** Between 12:04 and 12:56 on November 19 the trace shows 10 full sweeps of 73 to 493 seconds, each starting about 2 minutes after the previous one ended. Every resolved, archived or merged event asks for a pass over every folder. The disk had 58 GiB free, so this is the event path, not low space; nothing backs off when a pass removes nothing.
- **One slow size walk spoils the plan.** A folder whose size walk passes 5 seconds (`SIZE_WALK_TIMEOUT`) marks the whole plan incomplete; 14 of 79 folders had no size on November 17.
- **A failed removal loses its reason.** When `git worktree remove` fails ("Directory not empty", commonly Finder writing `.DS_Store`), the sweep reports "Git refused" once, then the half-removed folder reads "broken registration" forever (15 folders on November 17). A hand cleanup on November 18 answered such failures with `rm -rf`.
- **A retired repository does not come back.** This thread's own app worktree had been removed and its branch deleted; `studio_worktree_add_repository` answered "already a member" and added nothing.
- **Other stores grow.** Checks copies under `<home>/verify` are never retired (8 on the M4, one untouched since November 13). Logs of ended terminals and agent sessions are never removed, since only rotated files are.

## Scope

In: the chat worktree pass and its decision, its triggers, the plan in Settings > Storage, restore of a retired repository, retirement of unused checks copies, old session logs, and the operations docs. All in `repositories/anton-abyzov/specwithcode`.

Out:

- Stopping idle agent processes. 18 folders on the M4 hold a live agent or tool process; they stay "in use" until that process ends.
- A second pruner of pre-update database backups. The update agent already keeps one (`scripts/studio-fleet/state_backup_prune.py`, `KEPT_BEFORE_COPY = 1`); the M4 holds one real copy. Symbolic links to the external archive are left alone.
- pnpm store link mode: proposed below, not built.
- Running any sweep or removal by hand on this machine. The build ships through a release.

## Acceptance Criteria

- [ ] AC-01: A head chat counts as finished when it is archived, resolved, or its last run completed and nothing is running, queued (a held queue included), waiting, pending an answer or working in the background. A head chat whose last run failed, was cancelled or interrupted is finished only once resolved or archived; the 6 quiet hours rule still covers it.
- [ ] AC-02: A sub-chat that shares its parent's folder never decides. It keeps the folder only while it runs, is queued, waits or has a pending request; otherwise its parent's state stands, whatever its own last run was.
- [ ] AC-03: With "Delete merged worktrees" on, a folder goes at the next pass, with no quiet period, when every head chat is finished, a member's pull request merged, and every member is on the default branch or merged with its content there. A closed pull request keeps today's rule.
- [ ] AC-04: A folder whose members are all on the default branch, with no merged pull request, goes once every head chat is finished and the folder has been quiet for 6 hours.
- [ ] AC-05: Every check of 1370 still keeps a folder: uncommitted or untracked files, commits on no remote unless their content is on the default branch, a stash on the branch, commits only the reflog reaches, hidden tracked changes, a nested repository, a locked worktree, a broken registration, a terminal, a process whose working directory is inside, an unreadable process list, an open chat nearby.
- [ ] AC-06: A "ready" session record of a finished chat of the folder no longer keeps it. A session of any other chat, and any process working in the folder, still does.
- [ ] AC-07: `.specweave/state/.gc-last`, `__pycache__` folders and `.pyc` files count as rebuildable when Git ignores them (an untracked one still keeps the folder: plain `git worktree remove` refuses it). Other ignored files still keep the folder, except those copied under AC-08.
- [ ] AC-08: Before removal, ignored media, ignored files in a `reports` folder and ignored files under `.specweave/` are copied to `<baseDir>/evidence/removed-worktrees/` and checked by size, within the existing limits (2,000 files, 1 GiB). A failed copy keeps the folder.
- [ ] AC-09: Removal is plain `git worktree remove` per member, deepest first. Nothing in the sweep passes `--force` or deletes recursively: folders left empty go with a non-recursive remove, a lone `.DS_Store` in them is unlinked by name, and evidence a cancelled removal copied is deleted file by file.
- [ ] AC-10: After a folder's members are removed, each repository runs `git worktree prune`, but only when every worktree Git calls prunable lies under a folder that exists. Otherwise the prune is skipped and logged, so a worktree on an unmounted drive keeps its registration.
- [ ] AC-11: When Git fails to remove a member, the sweep deletes nothing more and leaves the folder as it is. It records Git's message and the processes holding files open in it (`lsof +D`, at most 10 seconds; "not known" on Windows or a timeout), keeps the record in `<stateDir>/worktree-removal-failures.json`, and Settings > Storage lists the folder under Kept with "Git could not remove it" and that detail until the folder is gone or removed cleanly. A folder Git half removed is never retried by the sweep (Git no longer knows it); a refusal that changed nothing is retried after 6 hours.
- [ ] AC-12: A member folder that holds no `.git` and no entry other than `.DS_Store` counts as already gone, not as a broken registration.
- [ ] AC-13: A folder's size walk has 20 seconds, and the plan's walks 3 minutes in total. A folder without a size reads "size unknown" in its row, and the plan stays complete. The plan is incomplete only when ownership or a folder could not be checked.
- [ ] AC-14: A chat's run completing, its pull request newly merging, and a chat being resolved or archived each ask for a pass over that chat's folders only. The hourly pass checks every folder. Settings changes and low disk still ask for a full pass.
- [ ] AC-15: A full pass asked for by low disk backs off while passes remove nothing: 2 minutes, then doubling to at most 1 hour, reset when a pass removes something or the disk level returns to ok. Passes for one chat are never delayed by that backoff. (The disk monitor asks only when the level turns from ok to low; the back-to-back passes measured in the Problem came from chat events, which AC-14 narrows.)
- [ ] AC-16: Adding a repository the thread already lists, whose folder is missing or holds no `.git`, creates it again: from the thread's branch when the repository still has it, else as a new member would be cut. A resumed chat's missing members come back from the thread's branch as before; the sweep never retires a member whose repository no longer has that branch (AC-05), so a branch a person deleted afterwards is the only case left answering "branch missing".
- [ ] AC-17: A checks copy (`<baseDir>/verify/<name>`) untouched for 7 days is retired by the hourly pass when its tree is clean, no commit was made in it (read from its reflogs: a copy fetches by commit, so every checked-out commit counts as unpushed and cannot be the test), it has no stash, no process works in it and the heavy-check gate is not held from inside it. `checks copy` and `checks run` record each use. One copy per repository stays the layout.
- [ ] AC-18: Logs of ended terminals and agent sessions (`logs/terminals/*.log`, `logs/provider/*.log` except `events.log`) not written for "Delete rotated logs after" days (14 by default) are removed with the rotated logs. Live trace and server logs are never removed.
- [ ] AC-19: `docs/operations/worktree-cleanup.md` and `docs/operations/heavy-checks.md` describe the new rules, and no changed file passes 1,500 lines.

## Approach

Order of work, all under `repositories/anton-abyzov/specwithcode`:

1. **Split first.** `worktreeCleanupSweep.ts` is 1,451 lines. Move the member facts (`readMemberGit`, `readHeadInDefault`, `readPullRequest`, `readNested`) to `worktreeCleanupMemberFacts.ts` and the removal (`copyEvidence`, `removeMembers`, the failure record) to `worktreeCleanupRemoval.ts`, with no behaviour change.
2. **Decision** (`finishedWorktrees.ts`, `worktreeCleanupRules.ts`): a head state "finished" beside open, resolved and archived; `storageCleanupThreadFinished`; held queues count as busy. The merged rule accepts finished heads without the quiet wait; the default-branch case of AC-04 asks for the wait.
3. **Facts** (`worktreeCleanupSweep.ts`, `worktreeCleanupWalks.ts`, `orphanWorktrees.ts`): sessions of finished chats, rebuildable markers, evidence classes, empty member folders.
4. **Removal** (`worktreeCleanupRemoval.ts`): no recursive delete, the guarded prune, the failure record with open files.
5. **Triggers** (`storageCleanup.ts`, new `storageCleanupTriggers.ts`): a set of chat ids per event pass, `thread.run-completed`-style events as a trigger, the low-disk backoff. The sweep takes an optional set of chat ids and assesses only their folders.
6. **Plan and UI** (`packages/contracts/src/storageCleanupPlan.ts`, `apps/web/src/lib/storageCleanupPlan.ts`, `StorageCleanupPlanSection.tsx`, the eight locale catalogs): "size unknown", the removal-failed sentence.
7. **Restore** (`git/worktreeSetGit.ts`): a listed member without `.git` is created again.
8. **Checks copies** (new `checksCopyRetention.ts`, `cli/verificationCopy.ts`, `cli/checks.ts`, `storageCleanup.ts`) and **session logs** (`storageCleanup.ts`).
9. **Docs.**

Risks and how they are held:

- **Removing a folder someone returns to.** The branch stays and every member is restorable (AC-16), so a resumed chat gets its folder back; only the dependency install is lost. Everything that exists only in the folder still keeps it (AC-05).
- **Host rate limit.** More folders reach the pull request lookup. The 50-minute reuse per branch head stays, merged stays final, and event passes look at one chat's folders, so lookups per hour are bounded by the number of finished, unmerged folders.
- **Prune.** The owner asked for a prune; 1370 left it out because a prune drops worktrees on an unmounted drive. AC-10 prunes only when that cannot happen.
- **Older clients.** The plan's reason is a closed list, so a new literal would fail to decode on an older window. The failure is sent as reason `unknown` with the sentence in `detail`; no literal is added.

### Proposal: pnpm store link mode (not built)

Each worktree install is mostly clones or hard links of the pnpm store already (`du` 13 GiB freed 1.8 GiB on November 18), so the gain is the virtual store, not the files. The proposal is to pin `packageImportMethod: clone-or-copy` and a machine-wide `storeDir` in `pnpm-workspace.yaml`, so every checkout on a volume shares file blocks with the store and a fresh worktree costs metadata only (APFS on the Macs, XFS reflink on linux-mini). `node_modules` stays a real folder per checkout: never shared, never a symbolic link, since workspace packages would resolve to another checkout's source. It needs a measured before and after on both machines and a check that `vp i` honours the keys, so it is left for its own increment.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: "last run completed" is read literally. A head chat whose last run failed, was cancelled or interrupted is not finished; a person may retry it. It still goes after 6 quiet hours once merged, as today.
- D-02: A folder with no work of its own (every member on the default branch, no merged pull request) waits 6 quiet hours. Removing it at once would cost a reinstall each time a person answers a chat that only asked a question.
- D-03: Ignored files under `.specweave/` and in `reports` folders are copied to evidence, not exempted: nothing is lost, and they hold no credentials. `.env` files and any other ignored file still keep the folder.
- D-04: A lone `.DS_Store` in an emptied container folder is unlinked by name so the folder can go. This happens only after Git removed every member; after a Git failure nothing is touched.
- D-05: Prune runs only when no prunable worktree sits under a missing folder (AC-10).
- D-06: A removal failure is carried as reason `unknown` plus detail, so windows older than this build still read the plan.
- D-07: Pre-update backups get no second pruner; the update agent's rule already keeps one.
- D-08: A checks copy is a clone, so retiring it deletes its folder. It reuses the merged-clone removal, which checks the same facts again right before it removes.

### Open
- Idle agent processes that keep a finished chat's folder "in use" need their own increment.

## Tasks

### T-01 Split the sweep file without changing behaviour
- AC: AC-19 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupMemberFacts.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupRemoval.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/worktreeCleanupSweep.test.ts apps/server/src/worktreeCleanupSweep.safety.test.ts

### T-02 Finished chats and the merged rule
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/finishedWorktrees.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupRules.ts, repositories/anton-abyzov/specwithcode/apps/server/src/finishedWorktrees.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupRules.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/finishedWorktrees.test.ts apps/server/src/worktreeCleanupRules.test.ts

### T-03 Sessions, rebuildable markers, evidence classes and empty member folders
- AC: AC-06, AC-07, AC-08, AC-12 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupWalks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orphanWorktrees.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupWalks.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/worktreeCleanupWalks.test.ts apps/server/src/worktreeCleanupSweep.test.ts

### T-04 Removal without force, guarded prune and the failure record
- AC: AC-09, AC-10, AC-11 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupRemoval.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeRemovalFailures.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeRemovalFailures.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.safety.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/worktreeRemovalFailures.test.ts apps/server/src/worktreeCleanupSweep.safety.test.ts

### T-05 Sizes with a budget and "size unknown"
- AC: AC-13 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupWalks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StorageCleanupPlanSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/lib/storageCleanupPlan.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases] | Test: specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/settings/StorageCleanupPlanSection.test.tsx src/lib/storageCleanupPlan.test.ts src/i18n/i18n.test.ts (from apps/web)

### T-06 Passes for one chat, the run-completed trigger and the low-disk backoff
- AC: AC-14, AC-15 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanupTriggers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanupTriggers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/storageCleanupTriggers.test.ts apps/server/src/storageCleanup.test.ts

### T-07 A retired repository comes back
- AC: AC-16 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/git/worktreeSetGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/git/worktreeSetGit.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/git/worktreeSetGit.test.ts

### T-08 Unused checks copies and ended session logs
- AC: AC-17, AC-18 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/checksCopyRetention.ts, repositories/anton-abyzov/specwithcode/apps/server/src/checksCopyRetention.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/verificationCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/checks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageLogRetention.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageLogRetention.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/checksCopyRetention.test.ts apps/server/src/storageLogRetention.test.ts

### T-09 Docs, typecheck, builds and the pull request
- AC: AC-19 | Files: [repositories/anton-abyzov/specwithcode/docs/operations/worktree-cleanup.md, repositories/anton-abyzov/specwithcode/docs/operations/heavy-checks.md] | Test: specweave-studio checks run -- node node_modules/typescript/bin/tsc --noEmit --project apps/server/tsconfig.json

### T-10 Independent review, merge, release, verify and close
- AC: AC-01 | Files: [.specweave/increments/1425-merged-worktrees-retire-automatically-and-storage-stays-bounded/reports/review.md] | Test: gh pr view --json state,mergeCommit
