# Finished worktrees stop holding gigabytes

## Problem

`~/.specwithcode` reached 123 GB. Agents add a worktree per task with `git worktree add`, about 6 GB each, nearly all of it `node_modules`. The orphan sweep waits a full day after a merge, and then keeps a finished folder forever if it holds any ignored file other than dependencies (`.artifacts/`, `dist/`, `.generated/`) or a commit only its reflog reaches, which any rebase leaves.

## Scope

In: the orphan sweep in `apps/server/src/storageCleanup.ts` and `apps/server/src/orphanWorktrees.ts`. Out: threads' own worktrees, the removal safety checks, the size of a dependency install, `statev2.sqlite`.

## Acceptance Criteria

- [x] AC-01: A clean worktree with no owner whose PR merged and with nothing unpushed is removed after 6 idle hours; every other removable state still waits a day.
- [x] AC-02: When ignored files or reflog-only commits keep such a folder, only its `node_modules` folders are removed, after a full idle day; those files, its source and the reflog stay.
- [x] AC-03: Open PR, no PR, working tree changes, unpushed commits or any owner remove nothing, not even dependencies.
- [x] AC-04: A locked worktree loses nothing, and a kept folder with nothing left to prune costs no PR lookup.

## Approach

`orphanDependenciesPrunable` is the removal test without the ignored-files condition. The sweep checks finished work first, then either removes the worktree or prunes its dependency installs. Rejected: sweeping a project's own `.worktrees` folders, because another SpecWithCode instance on the machine can own them and the other-instance guard only covers the base dir. Rejected: adding `dist/` and `.artifacts/` to the rebuildable list, because existing tests keep them on purpose and a whole ignored directory can hold secrets or evidence.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Six hours after a merge, long enough for a post-merge check → reversible.
### Open
- none

## Tasks

### T-01 Prune dependencies, shorter merged wait

**Satisfies**: AC-01, AC-02, AC-03, AC-04
**Files**: `apps/server/src/storageCleanup.ts`, `apps/server/src/orphanWorktrees.ts`, tests

### T-02 Verify and close 1173
