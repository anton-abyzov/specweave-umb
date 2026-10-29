# 1108 Consolidate workspace lifecycle and handoff settings

## Problem
Project folder, repository selection, per-chat isolation, worktree storage and application data are confused in settings and handoff. Worktree opt-out exists as Current checkout but is hard to find. Long-inactive completed chats have no protected 30-day archive lifecycle. Anton requested the best applicable Claude Desktop and Codex practices, optional worktrees, consolidated handoff, then reviewed merges and a newest macOS release.

## Scope
In: shared settings contracts; managed/project-local/custom future-worktree placement; explicit worktree/current-checkout choices; resolved path explanations; protected inactive-chat archiving; truthful handoff source/destination/project/checkout/storage disclosure using existing safe transfer mechanisms; focused headless verification, review and existing release-owner handoff.
Out: implicit project rebind or existing-worktree relocation, copying live databases/runtime/auth state, granting fleet access, deleting dirty/unpushed/owned work, duplicate cleanup/release owners, changing stopped threads, unrelated provider behavior. Release is authorized after reviewed feature readiness; installed acceptance remains distinct.

## Acceptance Criteria
- [ ] AC-01: Legacy worktree-location settings decode unchanged; default remains app-managed storage, with project-local and custom options, per-project inheritance where safe, and null/disabled 30-day archiving contracts validated.
- [ ] AC-02: A person can leave Use worktree checked for isolated Git work or uncheck it for Current checkout before starting a chat. Existing explicit local selections survive. Managed/project-local/custom placement reaches actual manual and agent-launched creation paths, rejects unsafe paths, keeps project-local worktrees ignored and preserves old locations/owners.
- [ ] AC-03: Inactive completed/settled local chats auto-archive after 30 days by default, configurable or Never; running, queued/background, pinned, unresolved-request, held/stopped, draft-bearing, scheduled, coordinator and personal-assistant chats remain protected. Archive preserves history and dirty/unpushed worktrees and never runs delete/stop/move actions. Unknown protection state fails closed.
- [ ] AC-04: Handoff clearly distinguishes source project root, current checkout, copy scope and destination project/worktree locations. Destination paths follow the target machine's settings, do not infer sibling access, and do not silently copy external worktrees or private app data. Existing safe copy/clone and coordinator ownership rules remain intact. Cover selected repository and Local versus Worktree continuation wherever supported by current contracts.
- [ ] AC-05: Focused tests, responsive light/dark headless settings/handoff checks and production builds pass, with a fresh-context review. Existing merge/release owner receives exact heads and inclusion gate; latest reviewed eligible features are merged and a signed/notarized macOS release is verified through that owner.

## Approach
Integration branch feat/workspace-lifecycle at /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/workspace-lifecycle, based on origin/main fa678d49dc. One settings lane owns contracts and new placement/default UI; a lifecycle lane owns protected archive service; a handoff lane owns disclosure and continuation integration without rewriting the copy engine. Foundation contracts land first; lanes merge normally, never cherry-pick. Reuse semantic settings controls and existing typed command boundaries. Put new logic in small modules; only minimal wiring in oversized legacy modules. Preserve owners of 1100, 1006, 1092/1103 and the existing release owner.

## Decisions
### Asked
- D-01 Anton explicitly requested optional worktrees, protected 30-day inactivity archiving, handoff improvements, reviewed feature merges and a newest macOS release.
### Defaulted
- D-02 Keep Automatic using a worktree for Git and current folder for non-Git; expose an obvious per-chat opt-out and existing global/project defaults. Never ask a model to override an explicit mode.
- D-03 Managed storage remains default for compatibility; offer Inside project at <selected repository>/.specwithcode/worktrees and Custom. Location changes affect new worktrees; keep existing paths pinned.
- D-04 Archive after 30 days is separate from worktree deletion and history retention. Protect unfinished/held work and unknown protection state, even if older than 30 days.
- D-05 No automatic migration of the live project root or worktree folders. No service restart outside the existing release owner's authorized process.
### Open
- none

## Tasks
### T-01 Define backward-compatible workspace lifecycle settings
- AC: AC-01 | Files: packages/contracts/src/settings.ts, packages/contracts/src/settings.test.ts, packages/contracts/src/workspaceLifecycleSettings.ts, packages/shared/src/projectSettings.ts, packages/shared/src/projectSettings.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/contracts/src/settings.test.ts packages/shared/src/projectSettings.test.ts --maxWorkers=1

### T-02 Consolidate creation modes and worktree storage controls
- AC: AC-02 | Files: packages/contracts/src/environment.ts, packages/contracts/src/environment.test.ts, apps/server/src/environment/ServerEnvironment.ts, apps/server/src/environment/ServerEnvironment.test.ts, apps/server/src/git/GitManager.ts, apps/server/src/worktreePlacement.ts, packages/shared/src/serverSettings.ts, packages/shared/src/serverSettings.test.ts, apps/web/src/components/BranchToolbar.tsx, apps/server/src/worktreesDirectory.ts, apps/server/src/worktreesDirectory.test.ts, apps/server/src/vcs/GitVcsDriver.ts, apps/server/src/vcs/GitVcsDriverCore.ts, apps/server/src/vcs/GitVcsDriverCore.test.ts, apps/server/src/serverSettings.ts, apps/server/src/serverSettings.test.ts, apps/server/src/orchestration-v2/ThreadLaunchService.ts, apps/server/src/orchestration-v2/ThreadLaunchService.test.ts, apps/server/src/storageCleanup.ts, apps/server/src/storageCleanup.test.ts, apps/web/src/components/settings/StorageSettings.tsx, apps/web/src/components/settings/StorageSettings.test.tsx, apps/web/src/components/settings/ProjectDefaultsSettings.tsx, apps/web/src/components/settings/ProjectDefaultsSettings.test.tsx, apps/web/src/components/settings/settingsSearch.ts, apps/web/src/components/settings/SettingInheritance.tsx, apps/web/src/components/settings/projectOverrideRows.ts, apps/web/src/components/chat/WorkspaceModeControl.tsx, apps/web/tests/workspace-lifecycle | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/worktreesDirectory.test.ts apps/web/src/components/settings/ProjectDefaultsSettings.test.tsx apps/web/src/components/settings/StorageSettings.test.tsx --maxWorkers=1
- Dependencies: T-01

### T-03 Archive inactive chats without touching retained work
- AC: AC-03 | Files: packages/contracts/src/orchestrationV2.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/Orchestrator.inactiveArchive.test.ts, apps/server/src/orchestration-v2/InactiveThreadArchiveGuard.ts, apps/server/src/terminal/Manager.ts, apps/server/src/terminal/Manager.test.ts, apps/server/src/composerDrafts/ComposerDrafts.ts, apps/server/src/composerDrafts/draftFiles.ts, apps/server/src/composerDrafts/draftFiles.test.ts, apps/server/src/orchestration-v2/InactiveThreadArchive.ts, apps/server/src/orchestration-v2/InactiveThreadArchive.test.ts, apps/server/src/server.ts, apps/web/src/components/settings/InactiveThreadArchiveSetting.tsx, apps/web/src/components/settings/InactiveThreadArchiveSetting.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/InactiveThreadArchive.test.ts apps/web/src/components/settings/InactiveThreadArchiveSetting.test.tsx --maxWorkers=1
- Dependencies: T-01

### T-04 Consolidate handoff paths and execution context
- AC: AC-04 | Files: apps/web/src/components/studio/ProjectMachineHandoff.tsx, apps/web/src/components/studio/ProjectMachineHandoff.test.tsx, apps/web/src/components/studio/HandoffCopySetup.tsx, apps/web/src/components/studio/HandoffCopySetup.test.tsx, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffFolderCopy.test.tsx, apps/web/src/components/studio/MachineHandoffDialog.tsx, apps/web/src/components/studio/MachineHandoffDialog.test.tsx, apps/web/src/components/studio/HandoffWorkspaceSummary.tsx, apps/web/src/components/studio/HandoffWorkspaceSummary.test.tsx, apps/web/src/studio/machineHandoff.ts, apps/web/src/hooks/useProjectCoordinatorHandoff.ts, apps/web/src/hooks/useProjectCoordinatorHandoff.test.tsx, apps/web/tests/workspace-handoff | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffWorkspaceSummary.test.tsx apps/web/src/components/studio/MachineHandoffDialog.test.tsx apps/web/src/hooks/useProjectCoordinatorHandoff.test.tsx --maxWorkers=1

### T-05 Verify integration, review, and deliver through the release owner
- AC: AC-05 | Files: reports/workspace-lifecycle.md, reports/workspace-lifecycle.html | Test: node apps/server/scripts/cli.ts build
- Dependencies: T-02, T-03, T-04, T-06, T-07, T-08, T-09, T-10, T-11

### T-06 Respect destination worktree placement during thread handoff
- AC: AC-04 | Files: apps/server/src/handoff/HandoffReceiver.ts, apps/server/src/handoff/handoffMove.test.ts, apps/server/src/handoff/handoffPlacement.ts, apps/server/src/handoff/handoffPlacement.test.ts, apps/server/src/orchestration-v2/limitHandoffPreflight.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/handoff/handoffMove.test.ts apps/server/src/handoff/handoffPlacement.test.ts --maxWorkers=1
- Dependencies: T-02

### T-07 Serialize terminal admission with inactive archive commit
- AC: AC-03 | Files: apps/server/src/server.ts, apps/server/src/orchestration-v2/InactiveThreadArchiveGuard.ts, apps/server/src/orchestration-v2/Orchestrator.inactiveArchive.test.ts, apps/server/src/terminal/Manager.ts, apps/server/src/terminal/Manager.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Orchestrator.inactiveArchive.test.ts apps/server/src/terminal/Manager.test.ts --maxWorkers=1
- Dependencies: T-03

### T-08 Repair settings and handoff type integration
- AC: AC-02, AC-04, AC-05 | Files: apps/server/src/handoff/handoffPlacement.ts, apps/web/src/components/settings/StorageSettings.tsx, apps/web/src/components/settings/StorageSettings.test.tsx, apps/web/tests/workspace-lifecycle/mocks.tsx, apps/web/src/components/studio/ProjectMachineHandoff.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/StorageSettings.test.tsx apps/web/src/components/studio/ProjectMachineHandoff.test.tsx --maxWorkers=1
- Dependencies: T-02, T-04

### T-09 Repair hosted typecheck and settings continuity gates
- AC: AC-01, AC-05 | Files: apps/server/src/orchestration-v2/InactiveThreadArchive.test.ts, scripts/studio-fleet/settings_continuity.py, scripts/studio-fleet/test-settings-continuity.py, reports/workspace-lifecycle.md, reports/workspace-lifecycle.html | Test: python3 -B scripts/studio-fleet/test-settings-continuity.py
- Dependencies: T-03, T-08

### T-10 Repair workspace integration fixture server-config mocks
- AC: AC-04, AC-05 | Files: apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx, apps/web/src/components/studio/ProjectWorkspace.lifecycle.test.tsx, reports/workspace-lifecycle.md | Test: cd apps/web && node --run test -- --shard 1/2
- Dependencies: T-04, T-09

### T-11 Verify raw ignored paths in portable handoff fixtures
- AC: AC-04, AC-05 | Files: apps/server/src/handoff/handoffMove.test.ts, reports/workspace-lifecycle.md | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/handoff/handoffMove.test.ts apps/server/src/handoff/handoffPlacement.test.ts --maxWorkers=1
- Dependencies: T-06

Verify and close 1108.
