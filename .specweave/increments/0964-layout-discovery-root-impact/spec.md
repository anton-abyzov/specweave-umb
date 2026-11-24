# Folder layout discovery and guarded root change

## Problem

Nested repository discovery follows only the umbrella convention. The CLI's `findNestedCheckouts` finds registered repos plus `repositories/<x>` and `repositories/<org>/<repo>`; a repository nested under any other name is invisible to handoff and pickup. In the app, changing a project's folder checks missing folders, conflicts, active work and a different repository, but says nothing about the plan: which planning root the threads will read, how many increments they lose or gain, which manual increment links stop resolving, and what layout the new folder has.

## Scope

In: CLI bounded nested discovery (`src/core/session/nested-repos.ts`), the app folder check and change (`apps/server/src/project/ProjectFolderChange.ts`), its contract and dialog. Out: performing any real root change, merging projects by remote, remote-only roots (machine-flow owner).

## Acceptance Criteria

- [ ] AC-01: The CLI finds Git checkouts nested under any folder name, up to three levels below the root, alongside the registered and `repositories/` ones
- [ ] AC-02: Discovery stays inside the root: it skips dot folders and dependency folders, does not follow a symlink that leaves the root, stops at the first checkout, counts a `.git` file (worktree) as a checkout, and lists each real path once
- [ ] AC-03: The folder check reports the target layout (single repository, `repositories/` umbrella, nested repositories, or plain folder) with the repositories it found, bounded the same way
- [ ] AC-04: The folder check reports the planning impact: planning root and increment count before and after, and manual increment links that will no longer resolve
- [ ] AC-05: A change that loses increments or breaks links is refused until the user confirms the planning impact, the dialog says what changes and how to go back, and nothing is merged because two remotes match
- [ ] AC-06: Projects without increments or without `.specweave` change folders exactly as before

## Approach

The CLI adds a bounded walk to `findNestedCheckouts`. The app mirrors the same rules in its folder check (the app does not depend on the CLI package). Going back is the same guarded change to the previous folder, which the result returns.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Depth three, the same as `scanForChildRepos` in `save`
- D-02 Approving a change through an agent's request card also confirms the planning impact, because the card shows it
### Open
- none

## Tasks

### T-01 CLI bounded nested discovery
- AC: AC-01, AC-02 | Files: src/core/session/nested-repos.ts, tests/unit/core/session/nested-discovery.test.ts | Test: npx vitest run tests/unit/core/session/nested-discovery.test.ts tests/unit/core/session/nested-repos.test.ts
### T-02 App folder check reports layout and planning impact
- AC: AC-03, AC-04, AC-05, AC-06 | Files: packages/contracts/src/project.ts, apps/server/src/project/ProjectFolderChange.ts, apps/server/src/project/FolderLayout.ts, apps/server/src/project/ProjectFolderChange.test.ts | Test: vp test run apps/server/src/project/ProjectFolderChange.test.ts
### T-03 Folder change dialog shows impact and asks to confirm
- AC: AC-05 | Files: apps/web/src/components/studio/ProjectFolderChange.tsx | Test: headless folder dialog screenshot
### T-04 Verify and close 0964
