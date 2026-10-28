# Delete project with its worktrees

## Problem

Deleting a SpecWithCode project removes its threads, memory, plans and routines but leaves every thread worktree on disk. Worktrees were the largest disk hog on the M4 (171 GB, 2026-10-26), and nothing in the delete flow says they stay or offers to remove them.

## Scope

In: the three delete dialogs (Project settings General tab, settings panel, sidebar) list the project's worktrees with sizes and offer to delete them after the project is deleted; server RPCs that read and remove a deleted project's worktrees under the existing worktree-removal guard. Out: CLI and MCP options, branch deletion, worktrees outside the managed worktree roots.

## Acceptance Criteria

- [x] AC-01: The delete dialog lists the project's worktrees with sizes, ticks "Also delete N worktrees (X GB)" for clean ones, leaves worktrees with uncommitted files unticked behind a "Those files are lost" warning, and lists worktrees another project uses as kept.
- [x] AC-02: Worktrees are removed only after the project is deleted, only when confirmed; branches stay, and worktrees in use elsewhere, outside the managed roots, or with unconfirmed local changes are kept with a reason.
- [x] AC-03: After removal a toast reports how many were removed, the space freed, and any kept with reasons.

## Approach

Contracts add `projects.worktreesRead` (filesystem read scope) and `projects.worktreesRemove` (source-control write scope). `ProjectWorktreeCleanup` groups the project's threads by worktree path, classifies each one (removable, local_changes, in_use, not_removable), measures size with `du -sk` and counts commits no remote has. Removal refuses until the project is deleted and goes through `GitWorkflowService.removeWorktree` with an internal-only `projectDeletion` context that allows `--force` only for confirmed paths. The web hook `useProjectDeletionWorktrees` loads the preview when deletion starts and removes the confirmed ones after the delete succeeds.

## Decisions

### Asked
- D-01 Delete worktrees in the dialog (A) or only instruct the user (B) → A, recommended; user can still pick B.
### Defaulted (change any before sw-do)
- D-02 Clean worktrees ticked by default; uncommitted ones need a second explicit tick.
- D-03 Git branches are never deleted, so local-only commits survive.
### Open
- none

## Tasks

### T-01 Server read and remove of a deleted project's worktrees
- AC: AC-02 | Files: packages/contracts/src/project.ts, packages/contracts/src/projectWorkspaceRpc.ts, apps/server/src/project/ProjectWorktreeCleanup.ts, apps/server/src/git/worktreeRemovalSafety.ts | Test: npx vp test run src/project/ProjectWorktreeCleanup.test.ts src/git

### T-02 Delete dialogs offer worktree removal
- AC: AC-01, AC-03 | Files: apps/web/src/components/studio/ProjectDeletionWorktrees.tsx, apps/web/src/components/studio/useProjectDeletionConfirmation.tsx, apps/web/src/components/studio/ProjectWorkspaceSettings.tsx | Test: node apps/web/tests/project-workspace/deletion-worktrees-check.mjs

### T-03 Verify and close 1115
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1115-delete-project-with-its-worktrees/reports | Test: specweave verify
