# Umbrella project: default worktree repository and picker

## Problem

Anton, November 10, 2026, on Project settings > General for the specweave project: "if we are using worktrees, we should specify at least one repository which we're going to use for cloning, or what's available, because it might be an umbrella repository. By default, you could suggest an umbrella repository, right, but it's not mandatory to use it."

Pointing a project at an umbrella (`~/Projects/github/specweave-umb`, child clones under `repositories/<owner>/<repo>`, ignored by the umbrella's `.gitignore`) is allowed, and increment threads already get a per-repo worktree set (`apps/server/src/mcp/toolkits/project/handlers.ts:228-288`, `launchWorkspace.ts:73-98`). Everything else loses isolation (research: thread "Umbrella folder as project root", November 10, 2026):

1. A launch with no increment and no `repository` runs in the umbrella folder itself (`handlers.ts:280-281`, `UMBRELLA_WORKTREE_NOTICE` in `launchWorkspace.ts:55`).
2. The composer's worktree switch is on/off only (`apps/web/src/components/chat/WorkspaceModeControl.tsx`, used in `BranchToolbar.tsx:685`). Its launch sends `prepareWorktree.projectCwd = workspaceRoot` (`ChatView.tsx:10518`), mapped to a worktree strategy without `repository` (`packages/client-runtime/src/operations/commands.ts:739-765`), so it cuts a worktree of the umbrella that holds no child code.
3. There is no project setting naming the repository worktrees come from.
4. The folder Check describes the problem (`ProjectFolderChange.tsx:157-165`) but offers no way to register the child repos as Environment repositories, so `repository` launches fail after the move (`ThreadLaunchService.ts:128-152`). The only hint is "use Import SpecWeave workspace under Environment" when a SpecWeave workspace is present (`ProjectFolderChange.tsx:514-518`).
5. The recommendation says "Use worktrees: off" for every umbrella (`apps/web/src/lib/folderLayoutGuidance.ts:31-35, 74-78`), which is wrong once a default repository exists.

## Scope

In: a per-project optional default worktree repository chosen from Environment repositories; the server launch rule for threads without an increment; a repository choice in the composer's worktree control and its branch list; one-click registration of the umbrella's child repos from the folder Check; recommendation and notice copy.

Out: increment worktree sets (unchanged), the mobile and iOS new-task flows (they get the server default with no picker), routine editor UI (routines get the server default), cloning repositories that are not already checked out, moving the specweave project's folder (Anton does that himself after release).

## Acceptance Criteria

- [ ] AC-01: Project settings > Environment has "Default worktree repository": a select of the project's Environment repositories plus "None", default "None". It is never required, and saving "None" removes it.
- [ ] AC-02: When the project folder holds separate clones and no default is set, the select suggests one repository with a "Suggested" mark and a one-click "Use it": the repository whose checkout was the project's previous folder, else the repository holding the folder's `.specweave` increments' most recent changes, else the first one. A suggestion is never saved without that click.
- [ ] AC-03: Removing a repository that is the default, or its checkout going missing, clears or flags the default in settings ("Default repository `x` is missing"); a launch never fails silently because of a stale default, it falls back to AC-05's root behaviour with a notice naming the cause.
- [ ] AC-04: With Use worktrees on, a launch that names no increment and no `repository` (MCP launch, routine, composer from an older client, mobile) in a project with a default repository gets a worktree of that repository, cut from its checked-out branch, with `newWorktreesStartFromOrigin` honoured, and a notice naming the repository.
- [ ] AC-05: With no default repository, today's behaviour holds exactly: umbrella launches run in the folder with `UMBRELLA_WORKTREE_NOTICE`, single-repo projects get a worktree of the root.
- [ ] AC-06: An explicit `repository` on a launch, and an increment's worktree set, always win over the default; existing `handlers.ts` and `ThreadLaunchService` tests pass unchanged.
- [ ] AC-07: In a project with Environment repositories, the composer's "Use worktree" control gets a repository dropdown: "Project folder" (when the root is a Git repository), each Environment repository, preselected to the default repository, else the project folder. The pick holds for that draft only.
- [ ] AC-08: The branch picker next to it lists the chosen repository's branches, and the launch sends `repository` with a base branch of that repository; switching repository resets the base branch to that repository's current branch.
- [ ] AC-09: When the folder Check finds an umbrella or nested layout, it lists the child repositories it found that are not yet Environment repositories and offers "Register N repositories" after the change, reusing the existing workspace import preview and apply (`ProjectEnvironmentAdoption.ts`). Each row shows path and origin; blocked rows say why. Nothing is registered without the click.
- [ ] AC-10: Recommendation copy: for an umbrella with a default repository, "Recommended for this folder: on. New threads get a worktree of `<repo>`; increments get one worktree per repository they change." Without one, the current "off" advice plus "or set a default worktree repository". The Check's worktree summary names the default when set.
- [ ] AC-11: Mixed versions: an older server never shows or receives the setting (the read result advertises support; the select is hidden otherwise), and an older client launching against a new server gets AC-04's default.
- [ ] AC-12: Headless end-to-end with an umbrella fixture (root repo ignoring `repositories/`, two child clones): set default, launch from the composer with and without a pick, launch via MCP with no repository, launch for an increment touching both repos; each lands in the expected worktree. Screenshots saved to files.

## Approach

1. Contracts (`packages/contracts/src/projectEnvironment.ts`): `defaultWorktreeRepositoryId: Schema.optionalKey(ProjectRepositoryId)` on `ProjectEnvironmentSettings`, with the existing filter extended so it must name a listed repository; the same key plus `supportsDefaultWorktreeRepository` on `ProjectEnvironmentReadResult`. Composer: optional `repository` on `prepareWorktree` in `packages/client-runtime/src/operations/commands.ts`, passed through to the existing `OrchestrationV2ThreadLaunchWorkspaceStrategy.repository` (`orchestrationV2.ts:677-684`); no new RPC.
2. Server launch rule (`launchWorkspace.ts`, `handlers.ts`): after the increment branch and before the umbrella fallback, resolve the default repository through `resolveLaunchRepository`; when its checkout is a Git repository, return `{type: "worktree", repository, baseRef: <its branch>}` with a new `defaultRepositoryWorktreeNotice`. The same rule applies in `ThreadLaunchService` when a worktree strategy arrives without `repository` for a project whose root holds separate clones, so composer, routines and mobile share one rule. Stale default: fall through with a notice (AC-03).
3. Settings (`apps/web/src/components/studio/ProjectEnvironment.tsx`): the select, suggestion and stale state; suggestion logic in a pure `defaultWorktreeRepository.logic.ts`. Removing a repository clears the key server-side in the same write.
4. Composer (`WorkspaceModeControl.tsx`, `BranchToolbar.tsx`, `BranchToolbar.logic.ts`, `ChatView.tsx` launch site): repository dropdown, branch list queried with the repository checkout as cwd, `repository` sent in `prepareWorktree`. `ChatView.tsx` gets only the prop and the launch field; logic stays in `BranchToolbar.logic.ts`.
5. Folder Check (`ProjectFolderChange.tsx`, server `ProjectFolderChange.ts`): after a successful change to an umbrella or nested layout, call the existing import preview for the new root and show "Register N repositories"; apply with its fingerprint. The check result already carries `layout.repositories`.
6. Copy in `folderLayoutGuidance.ts` takes an optional default repository name.

Rejected: a Settings > General field (the list of repositories lives in Environment, and a default must reference it); auto-registering child repos on folder change (silent permission and access change); making the default mandatory for umbrellas (Anton: "not mandatory").

Risks: `ChatView.tsx` size and churn from other increments (touch only the launch site); `ws.ts` import limit (no new RPC planned, TS2589); the shared checkout is used by other workers (branch only on the coordinator's go).

## Decisions

### Asked
- none (Anton's message settles optional, suggested-by-default)
### Defaulted (change any before sw-do)
- D-01 The setting lives under Environment, next to the repositories it references.
- D-02 Default is "None"; the suggestion needs one click (AC-02).
- D-03 The default applies to every launch without an increment or explicit repository, including routines and mobile, via one server rule.
- D-04 Composer pick is per draft, never remembered.
### Open
- none

## Tasks

### T-01 Contracts: default repository key, support flag, composer repository
- AC: AC-01, AC-03, AC-11 | Files: packages/contracts/src/projectEnvironment.ts, packages/contracts/src/projectEnvironment.test.ts, packages/client-runtime/src/operations/commands.ts | Test: bun run --cwd packages/contracts test projectEnvironment

### T-02 Server: store and validate the default, clear on removal, advertise support
- AC: AC-01, AC-03, AC-11 | Files: apps/server/src/project/ProjectEnvironmentPaths.ts, apps/server/src/project/ProjectWorkspaceRpc.ts, apps/server/src/project/ProjectEnvironmentAdoption.ts | Test: bun run --cwd apps/server test ProjectEnvironment

### T-03 Server launch rule: default repository worktree for launches without an increment
- AC: AC-04, AC-05, AC-06, AC-11 | Files: apps/server/src/mcp/toolkits/project/launchWorkspace.ts, apps/server/src/mcp/toolkits/project/launchWorkspace.test.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/orchestration-v2/ThreadLaunchService.ts, apps/server/src/orchestration-v2/ThreadLaunchService.test.ts | Test: bun run --cwd apps/server test launchWorkspace ThreadLaunchService

### T-04 Settings: Default worktree repository select, suggestion, stale state
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/ProjectEnvironment.tsx, apps/web/src/components/studio/defaultWorktreeRepository.logic.ts, apps/web/src/components/studio/defaultWorktreeRepository.logic.test.ts | Test: bun run --cwd apps/web test defaultWorktreeRepository

### T-05 Composer: repository dropdown and per-repository branches
- AC: AC-07, AC-08 | Files: apps/web/src/components/chat/WorkspaceModeControl.tsx, apps/web/src/components/BranchToolbar.tsx, apps/web/src/components/BranchToolbar.logic.ts, apps/web/src/components/BranchToolbar.logic.test.ts, apps/web/src/components/ChatView.tsx | Test: bun run --cwd apps/web test BranchToolbar

### T-06 Folder Check: register child repositories, recommendation copy
- AC: AC-09, AC-10 | Files: apps/web/src/components/studio/ProjectFolderChange.tsx, apps/web/src/components/studio/ProjectFolderChange.test.tsx, apps/web/src/lib/folderLayoutGuidance.ts, apps/web/src/lib/folderLayoutGuidance.test.ts, apps/web/src/components/settings/ProjectDefaultsSettings.tsx, apps/server/src/project/ProjectFolderChange.ts | Test: bun run --cwd apps/web test ProjectFolderChange folderLayoutGuidance ProjectDefaultsSettings

### T-07 Headless end-to-end on an umbrella fixture
- AC: AC-12 | Files: apps/web/tests/umbrella-worktrees/verify.mjs, apps/web/tests/umbrella-worktrees/fixture.mjs | Test: node apps/web/tests/umbrella-worktrees/verify.mjs
