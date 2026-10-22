# Portable project copy with active work

## Problem
Copy and move rejects an active project before measuring files, and suggests the source macOS path on Linux. The dialog obscures the source root and confuses per-machine coordinators with transfer of coordinator context and responsibility.

## Scope
Permit copies during unfinished work with snapshot warnings; retain safe ownership transitions. Resolve destination paths on that machine, expose source scope, preserve arbitrary nested repositories, and verify production transfer code against ministorm in isolated folders. No live coordinator takeover or changes to existing remote projects.

## Acceptance Criteria
- [ ] AC-01: Active work does not prevent measurement or copying; warnings explain snapshot limits and deferred context transfer. Context transfer never silently fences active work.
- [ ] AC-02: Linux destinations use their own home; saved/custom paths and edits survive async resolution. The source root is explicit and nested repositories retain relative paths for umbrella and custom layouts.
- [ ] AC-03: An isolated Mac-to-ministorm transfer through production transfer code preserves real SpecWeave source and dirty/untracked fixture files, excludes default secret/rebuildable classes, verifies Git/content, and leaves live projects/services untouched.
- [ ] AC-04: UI and docs distinguish copy, coordinator-context transfer, per-machine coordinators and thread migration; focused tests, builds, headless evidence and fresh review pass.
- [ ] AC-05: The coordinator failure is traced to the selected model's own context and distinguished from account quota; the applicable recovery is verified and its installed-runtime result is recorded.

## Approach
The source is registered workspaceRoot; never silently widen to arbitrary parents. Recursive manifest discovery supports arbitrary nested .git paths. Remove the early move-mode busy veto while preserving ownership guards. Copy before attempting context transfer; if busy, retain the successful copy and present an explicit later retry. Resolve home-based suggestions through destination filesystem API. Changes belong to specweave-studio, based on origin/main, in separate lane worktrees.

## Decisions
### Asked
- User: allow copying unfinished work with warning; test on ministorm and explain coordinator semantics.
- User accepted the concrete UI for release in this chat: "Accept this UI" (2026-10-22).
- User additionally requested investigation of the coordinator's context-allowance error despite 91% account quota remaining.
### Defaulted
- D-01: No live coordinator migration during testing; isolated services and copies.
- D-02: Preserve registered roots; explain scope rather than silently include siblings or unrelated parents.
- D-03: Active coordinator responsibility transfer remains guarded; copying is independent.
### Open
- None.

## Tasks
### T-01 Active copy backend
- AC: AC-01 | Files: apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/MachineHandoffFolderCopy.test.ts, apps/server/src/fleet/folderCopyPreparation.ts, apps/server/src/fleet/folderTransfer/sourceService.ts, packages/contracts/src/folderCopy.ts, focused backend tests | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0990-copy && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/MachineHandoff*.test.ts apps/server/src/fleet/FolderCopyHandoff.test.ts apps/server/src/fleet/folderTransfer --maxWorkers=2 --coverage

### T-02 Destination paths and clear copy flow
- AC: AC-01, AC-02, AC-04 | Files: apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/ProjectMachineHandoff.tsx, apps/web/src/studio/folderCopy.ts, adjacent tests, apps/web/tests/folder-copy | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0990-copy && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffFolderCopy.test.tsx apps/web/src/studio/folderCopy.test.ts && node apps/web/tests/folder-copy/verify.mjs

### T-03 Real Linux transfer proof
- AC: AC-02, AC-03 | Files: scripts/studio-folder-transfer/ministorm-verify.mjs, scripts/studio-folder-transfer remote helpers, evidence receipt | Test: node scripts/studio-folder-transfer/ministorm-verify.mjs <new-absolute-report-directory> /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave

### T-04 Documentation, integrated review and completion
- AC: AC-04 | Files: docs/user/moving-a-project.md, increment reports | Test: focused coverage, web/server production builds, independent review, specweave verify 0990, manual UI acceptance, specweave complete 0990

### T-05 Recover a copied snapshot without losing an ownership fence
- AC: AC-01, AC-04 | Files: apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/folderCopyPreparation.ts, apps/server/src/fleet/folderTransfer/sourceService.ts, apps/server/src/fleet/MachineHandoffFolderCopy.test.ts, apps/server/src/fleet/folderTransfer/sourceService.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0990-copy && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/MachineHandoffFolderCopy.test.ts apps/server/src/fleet/folderTransfer/sourceService.test.ts

### T-06 Keep the remote verification harness inside its typecheck boundary
- AC: AC-03, AC-04 | Files: scripts/studio-folder-transfer/ministorm-verify.mjs, scripts/studio-folder-transfer/remote-worker.ts, apps/server/scripts/folder-transfer-acceptance.ts, focused harness verification | Test: scripts and server typecheck gates at the final commit, production harness bundle, and scoped remote smoke verification

### T-07 Diagnose and verify coordinator context recovery
- AC: AC-05 | Files: increment reports/coordinator-context-diagnosis.md, reports of installed recovery | Test: supported live readback scoped to the selected coordinator; existing handoff budget/delivery and overflow recovery tests; exact installed source and targeted recovery readback after release
