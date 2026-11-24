# Per-increment multi-repo worktrees

## Problem

A feature that changes several repositories has no isolated workspace in SpecWithCode. A worktree covers one git repository: the project root, or one listed repository through `repository`. A project folder that holds other repositories (an umbrella) keeps its threads in the shared folder even with Use worktrees on, so parallel workers collide in the same checkouts.

The Use worktrees switch is only on Settings > Projects > <project> > New threads (`ProjectSettingsPanel.tsx:625`). The project's own General tab, which shows Name, Project folder, Goal and Coordinator model, does not show it, so the user concluded the setting did not exist (November 6, 2026).

SpecWeave maps a task's files to their repository only through the `repositories/<org>/<repo>/` path prefix (`src/core/tasks/strict-close.ts:27`), so a project whose repositories live elsewhere (this project: `specweave` plus `specwithcode-dev` as a listed repository) cannot declare them.

## Scope

In: the increment declares its repositories; a thread working that increment gets one worktree per declared repository under one thread folder, on one branch; an agent can add a repository mid-task through a tool; one PR per repository, linked to each other; the Use worktrees switch on the project's General tab; SpecWeave resolves owning repositories by registered path.

Out: a machine-wide worktree default (stays removed; storage location and cleanup stay machine settings with project overrides); threads without an increment (unchanged: project root, or one `repository`); copying `.specweave/` into worktrees (planning stays in the project root).

## Acceptance Criteria

- [x] AC-01: An increment records the repositories it changes in `metadata.json` `repositories` (paths relative to the project root, or a registered repository id); SpecWeave fills it from task `Files` owners and `specweave` accepts repositories at any path, not only `repositories/<org>/<repo>`.
- [x] AC-02: Strict close resolves each task file to its owning repository by the registered repository paths, and still accepts `repositories/<org>/<repo>/` files.
- [x] AC-03: With Use worktrees on, a thread launched for an increment that lists N repositories gets one thread folder holding N worktrees, each at the repository's path relative to the project root, all on the same branch name.
- [x] AC-04: With Use worktrees off, the same launch starts in the project folder as today; a thread without an increment behaves exactly as today.
- [x] AC-05: An agent adds one more repository to its thread's worktree set through an MCP tool; the shell `git worktree add` stays refused.
- [x] AC-06: Each repository with commits gets its own PR; every PR body links the others and the increment.
- [x] AC-07: The project's own General tab shows the Use worktrees switch, bound to the same setting as Settings > Projects.

## Approach

SpecWeave (this repository) first: `metadata.json` gets an optional `repositories` array; `create-increment` and `task` writes derive it from `Files` owners; `strict-close.ts` resolves owners through the config's registered repositories (`workspace.repos`, `umbrella.childRepos`, adopted checkouts) before the prefix rule.

SpecWithCode (public `anton-abyzov/specwithcode`): thread launch reads the increment's `repositories`, maps each to a project environment repository, and creates the worktree set in the thread folder (`worktreePlacement.ts`, `WorktreeMcpService.ts`, thread workspace binding and restore). Cleanup and handoff treat the set as one unit. The settings switch reuses `ProjectDefaultsSettings` on the project General tab.

Rejected: a per-thread repository picker (the increment already knows its repositories); worktrees of every repository in the umbrella (slow and wasteful for microservice umbrellas).

Risk: thread restore and handoff assume one checkout per thread; the set needs one record with N paths.

## Decisions

### Asked
- D-01 Which repositories a multi-repo thread checks out → the increment's declared repositories (user, November 6, 2026). Simple work without an increment keeps one checkout.
- D-02 Is Use worktrees per project → yes, per project only, no machine-wide default (user, November 6, 2026; already the case).
### Defaulted (change any before sw-do)
- D-03 Branch name → the same branch name in every repository of the set (reversible).
- D-04 Worktree folder layout → mirrors each repository's path relative to the project root (reversible).
### Open
- none

## Tasks

### T-01 Declare an increment's repositories and resolve owners by path
- AC: AC-01, AC-02 | Files: src/core/tasks/strict-close.ts, src/core/types/increment-metadata.ts, tests/unit/core/tasks/strict-close-repositories.test.ts | Test: npx vitest run tests/unit/core/tasks/strict-close-repositories.test.ts

### T-02 Show Use worktrees on the project General tab
- AC: AC-07 | Files: apps/web/src/components/settings/ProjectSettingsPanel.tsx | Test: pnpm exec vp test run apps/web/src/components/settings/ProjectSettingsPanel.test.tsx

### T-03 Worktree set for an increment thread
- AC: AC-03, AC-04 | Files: apps/server/src/worktreePlacement.ts, apps/server/src/orchestration-v2/ThreadWorkspaceRestore.ts | Test: pnpm exec vp test run apps/server/src (worktree set tests)

### T-04 Add a repository mid-task and link PRs
- AC: AC-05, AC-06 | Files: apps/server/src/mcp/WorktreeMcpService.ts | Test: pnpm exec vp test run apps/server/src/mcp

### T-05 Verify and close 1251
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 1251-per-increment-multi-repo-worktrees
