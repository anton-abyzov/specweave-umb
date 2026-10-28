# Delete threads but keep project memory

## Problem

Threads made by older SpecWithCode versions run the old way. To start them anew, the owner has to delete them one at a time from each thread's menu, or delete the whole project, which also wipes project memory, plan, routines and connections (`ProjectStore.ts` on `project.deleted`). The project-delete worktree cleanup from specwithcode-dev #933 only works after the project itself is deleted, so a live project's old worktrees stay on disk.

## Scope

In:
- "Delete all threads" in Project settings > General > Danger zone. It deletes every thread except the coordinator, archived threads included.
- An optional removal of those threads' worktrees, reusing the #933 preview and guard.

Out:
- Hard purge of conversation records. The `thread.created` and `thread.deleted` events stay as a tombstone, so a deleted v1 thread is never re-imported (`LegacyV1ThreadImporter` re-imports any v1 row with no `thread.created`).
- Deleting a single thread. That already exists in the thread "..." menu, with its own worktree prompt.

## Acceptance Criteria

- [ ] AC-01: `projects.threadsDelete` deletes every thread of a live project except its coordinator after the person types the project title. The project, its coordinator and `project_memory` rows stay. It refuses a wrong title and refuses while a thread has active work.
- [ ] AC-02: `projects.worktreesRemove` works for a live project. It removes only folders whose recording threads are all deleted, never a folder the coordinator or another live thread records, and keeps branches.
- [ ] AC-03: The Danger zone shows "Delete all threads" with the thread count, what stays, a typed-title confirmation and the worktree choice (clean folders ticked, folders with uncommitted files unticked). Confirming deletes the threads first, then only the ticked worktrees. A refusal is shown inline.

## Approach

- Server: `ProjectService.deleteThreads` reuses the project-delete child loop (`deleteChildThread`: one thread at a time, under each thread's lock, with stable command ids and the old-transcript load). It runs under the project admission lock and the client delete burst limit. The coordinator is excluded with `isProjectCoordinatorThreadId`. The RPC sits in the planning group next to the worktree RPCs and needs the orchestration operate scope.
- `ProjectWorktreeCleanup`: for a live project, the coordinator's threads are not candidate owners, so a folder they share shows as in use. `remove` checks each folder's recording threads instead of requiring a deleted project. The guard flag `projectDeletion` is renamed `confirmedDeletion`.
- Web: a `ProjectThreadsDeletion` component inside the existing danger zone, with its own `useProjectDeletionWorktrees` instance. Failure toasts are parameterized.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Delete-all refuses while any thread is working, matching project delete. Reversible: the person stops them first.
- D-02: Typed project title as confirmation, the same as project delete.
- D-03: Soft delete only, no purge of records. Purging would re-import v1 threads, and the disk space is in worktrees.
### Open
- none

## Tasks

### T-01 Server: delete all threads and live-project worktree removal
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectWorktreeCleanup.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/git/worktreeRemovalSafety.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectWorkspaceRpc.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/project.ts | Test: cd apps/server && ./node_modules/.bin/vp test run src/project/ProjectService.threadsDeletion.test.ts src/project/ProjectWorktreeCleanup.test.ts

### T-02 Web: Danger zone "Delete all threads"
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectThreadsDeletion.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/tests/project-workspace/deletion-worktrees-check.mjs | Test: cd apps/web && ./node_modules/.bin/vp test run src/components/studio/ProjectWorkspaceSettings.test.tsx && node tests/project-workspace/deletion-worktrees-check.mjs

### T-03 Verify and close 1120
- AC: AC-01, AC-02, AC-03 | Files: none | Test: specweave verify 1120-delete-threads-keep-memory
