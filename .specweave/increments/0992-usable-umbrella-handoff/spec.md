# Usable umbrella handoff and unfinished work portability

## Problem
The released dialog puts Measure the folder beneath scrolling content. A project registered at a child repository exposes only that subtree and sends users to settings to choose the umbrella. Existing copy support preserves dirty repositories and internal worktrees, but an external linked worktree loses its Git relationship. These gaps make continuing unfinished multi-repository work on another machine confusing and incomplete.

## Scope
Keep primary copy actions in the dialog footer throughout the flow. Offer a verified umbrella/project scope directly in the dialog, preserving arbitrary layouts and clearly showing exactly what is copied. Preserve unfinished Git state and portable worktree continuation. Verify real Mac-to-Ministorm scenarios in isolated disposable folders through production code, including consolidation, conflicts and rollback. Release and verify the installed desktop/service; provide screenshots and a full evidence report.

## Acceptance Criteria
- [ ] AC-01: Measure, preview, apply and applicable recovery actions remain visible in the non-scrolling footer at desktop and mobile sizes, including busy/error states; keyboard and duplicate-click behavior remain correct.
- [ ] AC-02: A nested project offers its verified containing umbrella directly in the dialog, distinguishes project scope from the selected child repository, preserves relative paths and destination suggestions, and never silently copies arbitrary ancestors or siblings.
- [ ] AC-03: Dirty, staged, untracked and ahead-branch work, stashes and linked worktrees can be copied and continued on Linux without requiring commits first; external Git dependencies are materialized or explicitly included and no broken Mac paths remain.
- [ ] AC-04: Repeated copies consolidate into the intended destination, preserve destination-only work, require explicit conflict decisions, and support verified rollback/recovery without damaging either source or unrelated destination folders.
- [ ] AC-05: Headless screenshots and production-code Mac-to-Ministorm receipts cover the scenario matrix; focused tests, relevant builds, coverage, fresh review, release and installed-artifact readback pass.

## Approach
Separate UI, source-scope, and Git/remote-verification worktrees based on merged1.0.69. The parent dialog owns a footer outlet for the copy state machine. Detect an umbrella from explicit project configuration and containment evidence; expose selected copy root without mutating live source registration. Validate scope again server-side and bind it to the copy operation. Keep copying and coordinator-context ownership distinct; active work can defer context transfer while preserving copied files. Materialize a selected external linked worktree as a portable independent repository when its common repository lies outside scope, preserving index and branch state without copying unrelated working directories. Tests use new private homes and exact scratch roots; no live provider turns or permanent coordinator takeover. Reconcile existing destinations through preview decisions and undo journals.

## Decisions
### Asked
- User requests footer fix, root-scope correction, testing, screenshots, release, consolidation scenarios and cleanup of test folders on Ministorm.
### Defaulted
- D-01: Preserve live projects and sessions; delete disposable test copies only after exact ownership/source-preservation checks.
- D-02: Never silently widen to arbitrary parents. Recommend only a verified umbrella, show its actual path and included repositories, retain explicit child-only scope.
- D-03: Each machine retains its own coordinator/service; running processes and credentials remain local.
- D-04: Distinguish real production transfers, isolated coordinator tests, UI fixtures and installed-runtime evidence.
### Open
- None.

## Tasks
### T-01 Keep copy actions in the dialog footer
- AC: AC-01, AC-05 | Files: apps/web/src/components/studio/MachineHandoffDialog.tsx, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/ProjectMachineHandoff.tsx, adjacent footer helpers and tests, apps/web/tests/folder-copy | Test: focused handoff UI tests and headless folder-copy verification at desktop/mobile sizes

### T-02 Resolve and validate umbrella copy scope
- AC: AC-02, AC-05 | Files: packages/contracts/src/folderCopy.ts, packages/contracts/src index/RPC exports, apps/server/src/fleet/MachineHandoff.ts, extracted folder-copy handlers, apps/server/src/fleet/folderCopyScope.ts and tests, apps/server/src/fleet/folderCopyPreparation.ts, source scope commands/client plumbing and tests | Test: focused source-scope contract/service tests and production server build

### T-03 Preserve portable Git worktrees and verify remote consolidation
- AC: AC-03, AC-04, AC-05 | Files: apps/server/src/fleet/folderTransfer Git snapshot/scan/reconcile/apply helpers and tests, apps/server/scripts/folder-transfer-acceptance.ts, scripts/studio-folder-transfer | Test: focused folderTransfer tests and real Mac-to-Ministorm scenario harness with Git/content/Undo/source-preservation receipts

### T-04 Integrate source scope and verify complete UI
- AC: AC-01, AC-02, AC-05 | Files: apps/web/src/components/studio/HandoffFolderCopy.tsx, extracted source-scope UI, apps/web/src/studio/folderCopy.ts, apps/web/src/components/studio/ProjectMachineHandoff.tsx, adjacent tests, apps/web/tests/folder-copy | Test: focused combined UI tests, web production build and headless light/dark desktop/mobile screenshots

### T-05 Review, release and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: docs/user/moving-a-project.md, increment reports/evidence, increment spec and ledger | Test: scoped coverage above configured target, fresh review, release pipeline, installed app/service verification, specweave verify and complete0992
