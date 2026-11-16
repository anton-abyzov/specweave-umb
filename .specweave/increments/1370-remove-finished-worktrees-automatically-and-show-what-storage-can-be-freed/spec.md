# Remove finished worktrees automatically and show what storage can be freed

## Problem

On the M4, `~/.specwithcode` reached 324 GB in Finder (1,457,414 items) and the disk 99% full (14 GiB free) on November 16, 2026. Release builds need 10 GiB.

Measured the same day (`du`, `df`, thread state through `specweave-studio db query`; tables in `reports/storage-measurement-2026-11-16.md`):

| Where | `du` size | Real disk | What it is |
|---|---|---|---|
| `m4/verify/specwithcode/.git` | 80.2 GiB | 79.2 GiB | 440 `tmp_pack_*` files left by failed Git housekeeping |
| `m4/worktrees` | 121.7 GiB, 41 folders | far less | 103.9 GiB is `node_modules`, and those are APFS clones of the pnpm store |
| `m4/scratch` | 70.9 GiB, 296 folders | less | 32.0 GiB `node_modules` (clones), 13.9 GiB videos of work in progress |
| `m4/userdata/statev2.sqlite` | 11.1 GiB | 11.1 GiB | live database |
| `m4/evidence` | 11.5 GiB | 11.5 GiB | evidence, kept |
| `backups/pre-08a1…` | 10.9 GiB | 10.9 GiB | one database copy from the November 16 update |

Two measurements correct the picture Finder gives:

- Removing every `node_modules` of one app worktree (5.9 GiB by `du`) returned 146 MiB by `df`. Dependency folders share their files with the package store, so pruning them frees almost nothing. The real cost of a worktree is its checkout, about 0.5 GiB.
- The one large real consumer was the checks copy. Its repository has refs with missing objects, so `git gc --auto` fails (`fatal: unable to read 7ac0eb11…`, `fatal: failed to run repack`) after every `checks copy` fetch and leaves a 198 MB `tmp_pack_*` each time. Nothing removes them.

The app's own cleanup (worktree rules, an hourly orphan sweep, an hourly merged-clone sweep) removed no thread worktree. Four gates in `apps/server/src/storageCleanup.ts` each keep every finished folder:

1. `:399` takes only folders recorded by exactly one thread. Sub-chats copy their parent's folder (`SubagentProjection.ts:69-77`), so a worker with reviews is never a candidate: `fix-ports-integration` has 31 threads, `1339-model-tracks` 35.
2. `:161-171` accepts thread status `idle` or `failed`. A finished thread reports `completed` or `cancelled`.
3. `:419` keeps a folder while any thread using it is not archived and not resolved, the candidate included. Sub-chats never resolve on their own, and a merge resolves a thread only with passing checks and an approving review (`ThreadResolutionPolicy.ts:34-41`).
4. `:461` and `:522` keep a folder with ignored files or a nested repository. A multi-repository thread folder always has both, and the sweep never reads the worktree-set manifest.

A second remover made things worse. The launchd job `com.specwithcode.cleanup` (every 30 minutes) checks ownership by the nested repository path, which no thread records, so on November 15 and 16 it ran `git worktree remove` on nested worktrees of 11 folders that open threads use. Git deleted the registration and left the files ("Directory not empty"). Five of those folders then pointed at another thread's registration once Git reused the name, so Git commands there acted on another thread's branch.

Settings > Storage shows no list of what cleanup would remove or why a folder stays.

## Scope

In:

- Finished thread folders are removed by the app: single worktrees and multi-repository folders, with sub-chats following their parent.
- A folder whose Git registration does not point back at it is never read or removed.
- Ignored media is copied to evidence before a folder goes; any other ignored file keeps the folder.
- Leftover download packs in app-owned checks copies are removed, and the checks copy stops creating them.
- A sweep when a chat is resolved or archived, when a pull request merges, and when the disk runs low, besides the hourly one.
- Settings > Storage: a setting for resolved chats, a list of what would be removed and what is kept with the reason, and "Clean up now".
- The one-off cleanup of the M4 with the shipped planner, and retiring the launchd job's worktree step.

Out:

- Pruning only `node_modules` of kept folders (measured: 146 MiB per folder).
- The scratch retention default, database compaction, the per-session files in `userdata/secrets` (262,244 files, 1.0 GiB) and the size the app-folder check reports for cloned files. Each is listed in the report as a follow-up.
- A preview of orphan worktrees and scratch clones (`specweave-studio clones sweep` prints that plan).
- Repairing the missing objects of the existing checks copy.

## Acceptance Criteria

- [ ] AC-01: A folder recorded by a worker chat and its sub-chats is a candidate. A sub-chat whose parent records the same folder and that has no run in progress or queued takes its parent's state in `worktreeOwnership.ts`, so the sweep, the manual removal guard and `specweave-studio worktree owners` agree. A sub-chat with a run in progress keeps the folder.
- [ ] AC-02: A chat whose last run is `completed`, `cancelled`, `interrupted` or `rolled_back` counts as quiet; `waiting`, `queued`, `preparing`, `starting`, `running`, a pending request, a background task or a queued turn do not.
- [ ] AC-03: With "Delete merged worktrees" on, a folder whose pull request is merged (content on the default branch) or closed (no unpushed commit) is removed when every chat using it is quiet and, if a chat is still open, nothing happened in it for 6 hours. Resolved and archived chats need no wait.
- [ ] AC-04: With the new setting "Delete worktrees of resolved chats" on (default), a folder whose chats are all resolved or archived is removed once every repository in it is clean and has no unpushed commit. A project whose worktree cleanup is Off keeps its folders.
- [ ] AC-05: Nothing that exists only in the folder is lost. Each of these keeps it, with its reason in the plan: uncommitted changes, untracked files, unpushed commits (unless the content is on the default branch), a stash entry made on its branch, commits only its reflog reaches, hidden tracked changes, a nested repository that is not a member, an ignored file that is neither rebuildable nor media.
- [ ] AC-06: A multi-repository folder is checked repository by repository and removed member by member, deepest first, without `--force`. Branches and the manifest stay, and a chat that resumes gets every member back (test: remove, then restore).
- [ ] AC-07: Before any Git command in a worktree, its `.git` file must name a registration whose `gitdir` points back at the same folder. A folder that fails is kept as "broken registration" and `removeWorktree` is never called on it.
- [ ] AC-08: Ignored media files (by extension, at most 1 GiB per folder) are copied to `<app folder>/evidence/removed-worktrees/<folder>-<time>/` and verified by size before removal. A failed copy or more media than the limit keeps the folder.
- [ ] AC-09: A folder is never removed while a chat using it is running, a live agent session or terminal is in it, or a process has its working directory in it. All checks are read again right before removal, under the workspace lease.
- [ ] AC-10: `specweave-studio checks copy` fetches with `--no-auto-gc` and, before fetching, removes `tmp_pack_*` and `tmp_obj_*` files older than one hour from the copy. The storage sweep removes the same files, older than six hours, from every `<app folder>/verify/*/.git`.
- [ ] AC-11: A sweep is queued when a chat is resolved or archived, when a pull request sync reports a merge, and when the disk status turns low. Queued requests collapse into one sweep, and event-driven sweeps run at most once every 2 minutes. The hourly sweep stays.
- [ ] AC-12: `server.getStorageCleanupPlan` returns, without removing anything, every chat worktree and every leftover-download item with action, reason, size outside dependency installs and the owning chat. The sweep and the plan share one decision function.
- [ ] AC-13: Settings > Storage shows "What cleanup would remove": a Check button, the list grouped into "Would be removed" and "Kept" with a plain reason per row, a total ("at least N GB"), and "Clean up now", which runs one sweep and shows the result. The new setting has a switch. Both RPCs are refused without the settings scope.
- [ ] AC-14: `docs/operations/worktree-cleanup.md` and `docs/operations/heavy-checks.md` describe the new rules, and the Settings copy no longer promises that open chats always keep their folder.
- [ ] AC-15: On the M4, the one-off cleanup ran with the shipped planner, the report lists before and after `df` and `du` figures, and everything kept has its reason.

## Approach

Decision logic moves out of the 1,281-line `storageCleanup.ts` into pure, tested modules; the service keeps I/O and scheduling.

1. `packages/contracts/src/storageCleanupPlan.ts` (done): plan item, plan, run result. `storageCleanupSettings.ts`: `removeResolvedWorktrees` (default true). The name avoids the `worktree*` prefix, which the web client routes into per-project rules.
2. `apps/server/src/git/worktreeOwnership.ts`: the thread query also returns `parentThreadId` and `busy` (a run in a non-final status). `decodeWorktreeBindings` resolves each thread's effective state: a sub-chat whose parent is in the list with the same folder and that is not busy takes the parent's state (cycle-safe). `isOpenThreadOwner` reads the effective state.
3. `apps/server/src/git/worktreeRegistration.ts` (new): the round-trip identity check.
4. `apps/server/src/finishedWorktrees.ts` (new, pure): facts per member and per folder in, `{ action, reason, detail }` out. Rules in order: deleted, inactive, unchanged, merged or closed, resolved.
5. `apps/server/src/worktreeCleanupSweep.ts` (new): gathers facts (threads by folder, manifest members, status, untracked, ignored, stash, reflog, default-branch ancestry, host pull request, process working directories), calls the pure decision, and in apply mode rechecks, copies media and removes. Members are removed through the Git driver, deepest first, then `git worktree prune` in each repository; the manifest and branches stay so `restoreWorktreeSet` works.
6. `apps/server/src/staleGitPacks.ts` (new): finds and removes leftover packs; used by `cli/verificationCopy.ts` and the sweep.
7. `storageCleanup.ts`: becomes a service (`StorageCleanupService`, `layer`) exposing `plan` and `cleanNow`; adds the event and low-disk triggers with one coalesced, rate-limited queue.
8. RPCs `server.getStorageCleanupPlan` and `server.runStorageCleanup` in their own group (as `cleanOldAppVersions`), handler `apps/server/src/storageCleanupRpc.ts`, client command, web section `StorageCleanupPlanSection.tsx`.

Rejected:

- A 30-minute timer. Two schedulers already ran, one every 30 minutes, and removed nothing useful: the gates were wrong, not the interval. Each candidate also costs a host lookup, so a tighter timer spends GitHub rate limit on folders that did not change. Events catch the moment work finishes; the hourly sweep catches the rest.
- Resolving sub-chats automatically. It would change what the sidebar shows and the settlement policy; ownership is the narrower place.
- `--force` removal, or deleting leftovers of a folder Git no longer knows. Unknown folders are reported, never removed.
- Copying every ignored file to evidence. Ignored files can be secrets; only media is copied, everything else keeps the folder.

Risks: a chat resumes after its folder went (covered by restore, tested for sets); a launch binds the folder between the last check and removal (launch does not take the lease; the final ownership read narrows the window and removal never forces); the launchd job stays a second remover until it is turned off.

## Decisions

### Asked
- D-01 Turn off the launchd job `com.specwithcode.cleanup`? → asked November 16, 2026, recommendation: turn it off now.
### Defaulted (change any before sw-do)
- D-02 Cadence → on resolve, archive, merge and low disk, plus the existing hourly sweep; no 30-minute timer.
- D-03 An open chat with a merged or closed pull request loses its folder after 6 quiet hours (the task's rule "PR merged or closed"); the branch stays and resume restores it.
- D-04 `removeResolvedWorktrees` defaults to on, including for existing installs.
- D-05 Dependency-only pruning is not built (146 MiB measured per folder).
- D-06 Media limit 1 GiB per folder; over it the folder is kept and shown.
- D-07 Sizes in the plan leave out dependency installs and are labelled "at least".
### Open
- none

## Review

Adversarial review by Muse Wonderful (`muse`, `muse-wonder-1.0`, extra high effort): deletion is hard to undo.

## Tasks

### T-01 Contracts: plan schema and the resolved-chats setting
- AC: AC-04, AC-12 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/storageCleanupPlan.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/storageCleanupSettings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/serverSettings.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/contracts/src/settings.test.ts packages/shared/src/serverSettings.test.ts

### T-02 Ownership: sub-chats follow their parent; registration identity check
- AC: AC-01, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/git/worktreeOwnership.ts, repositories/anton-abyzov/specwithcode/apps/server/src/git/worktreeOwnership.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/git/worktreeRegistration.ts, repositories/anton-abyzov/specwithcode/apps/server/src/git/worktreeRegistration.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/worktree.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/git/worktreeOwnership.test.ts apps/server/src/git/worktreeRegistration.test.ts

### T-03 Finished-folder decision and the sweep for single and multi-repository folders
- AC: AC-02, AC-03, AC-04, AC-05, AC-06, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/finishedWorktrees.ts, repositories/anton-abyzov/specwithcode/apps/server/src/finishedWorktrees.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/finishedWorktrees.test.ts apps/server/src/worktreeCleanupSweep.test.ts apps/server/src/storageCleanup.test.ts

### T-04 Leftover download packs: checks copy and sweep
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/staleGitPacks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/staleGitPacks.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/verificationCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/verificationCopy.test.ts, repositories/anton-abyzov/specwithcode/docs/operations/heavy-checks.md | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/staleGitPacks.test.ts apps/server/src/cli/verificationCopy.test.ts

### T-05 Service, triggers and the plan and run RPCs
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanupRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanupRpc.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/server.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/storageCleanupRpc.test.ts apps/server/src/storageCleanup.test.ts

### T-06 Settings > Storage: the setting, the plan list and Clean up now
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StorageSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StorageCleanupPlanSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StorageCleanupPlanSection.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/lib/storageCleanupPlan.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/docs/operations/worktree-cleanup.md | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/StorageCleanupPlanSection.test.tsx src/components/settings/StorageSettings.test.tsx

### T-07 Review, merge and release
- AC: AC-01 to AC-14 | Files: repositories/anton-abyzov/specwithcode | Test: gh pr checks <number> --repo anton-abyzov/specwithcode

### T-08 One-off cleanup of the M4 and the report
- AC: AC-15 | Files: .specweave/increments/1370-remove-finished-worktrees-automatically-and-show-what-storage-can-be-freed/reports | Test: df -h ~ && specweave-studio db query "select count(*) from orchestration_v2_projection_threads"
