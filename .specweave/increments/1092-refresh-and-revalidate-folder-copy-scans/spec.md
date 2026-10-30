# 1092 Refresh and revalidate folder-copy scans

## Problem
The handoff dialog can resume a persisted scan and present historical external worktree registrations as current folders. Reopening does not guarantee a new scan. Missing registered folders can also appear in new scans.

## Scope
In: scan timestamps, explicit safe freshness check, missing-registration reporting, source and destination validation before approval, regression and headless evidence. Out: cleanup, Git pruning, live copy, restart, deployment, ownership migration.

## Acceptance Criteria
- [ ] AC-01: Fresh scans count only existing registered external worktree folders; missing registrations are separately labelled and no registration is removed.
- [ ] AC-02: Resumed scans expose their timestamp or unknown historical age. Refresh checks current source state without cancelling jobs, changing selections, approvals or secret exclusions.
- [ ] AC-03: Copy approval revalidates the source inventory and destination preview, refuses changed snapshots before any transfer, and requires a fresh comparison when changed. Legacy snapshots cannot silently pass a freshness check.
- [ ] AC-04: Removed and added worktrees, resume versus new scan, unchanged refresh and changed source/destination are covered by isolated tests. Current source, implementation and installed acceptance are reported separately.

## Approach
Read-only scan validation retains the original operation and manifest. Store a source inventory signature at measurement and manifest creation; expose refresh diagnostics with current summary separately from the saved summary. Validate it at destination approval over the operation-scoped source route. Refresh does not apply, cancel or prune anything. A changed scan requires an explicit new comparison. Existing selections survive; conflict choices remain on the old job and are not silently replayed onto changed data.

## Decisions
### Asked
- none
### Defaulted
- Missing registration is historical metadata, not a current folder.
- A changed inventory requires reviewing a new comparison; unchanged refresh preserves the existing preview and approvals.
### Open
- none

## Tasks

### T-01 Validate scan inventory and approval
- AC: AC-01, AC-03, AC-04 | Files: apps/server/src/fleet/folderTransfer/manifest.ts, apps/server/src/fleet/folderTransfer/manifest.test.ts, apps/server/src/fleet/folderTransfer/sourceService.ts, apps/server/src/fleet/folderTransfer/sourceService.test.ts, apps/server/src/fleet/folderTransfer/sourceRoutes.ts, apps/server/src/fleet/folderTransfer/sourceClient.ts, apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationScan.ts, apps/server/src/fleet/folderTransfer/reconcile.ts, apps/server/src/fleet/folderTransfer/destinationService.grant.test.ts, apps/server/src/fleet/folderTransfer/destinationService.held.test.ts, apps/server/src/fleet/folderTransfer/portableGit.test.ts, apps/server/src/fleet/folderTransfer/twoServer.verify.test.ts, apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/FolderCopyHandoff.ts, packages/contracts/src/folderCopy.ts, packages/contracts/src/machineHandoffRpc.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/manifest.test.ts apps/server/src/fleet/folderTransfer/sourceService.test.ts apps/server/src/fleet/folderTransfer/twoServer.verify.test.ts

### T-02 Expose scan age and safe refresh
- AC: AC-02, AC-04 | Files: apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyFooter.tsx, apps/web/src/components/studio/HandoffCopyScanFreshness.tsx, apps/web/src/components/studio/HandoffCopyScanFreshness.test.tsx, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, apps/web/tests/folder-copy/verify.mjs, apps/web/tests/folder-copy/stubs.tsx, docs/user/moving-a-project.md | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffCopyScanFreshness.test.tsx apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx

### T-04 Repair strict optional-property CI diagnostics
- AC: AC-03, AC-04 | Files: apps/server/src/fleet/folderTransfer/sourceService.ts, apps/server/src/fleet/folderTransfer/manifest.ts, apps/server/src/fleet/folderTransfer/destinationService.ts | Test: bash scripts/studio-verify/typecheck-gate.sh --package apps/server --jobs 1

### T-03 Verify and close 1092
- AC: AC-04 | Files: reports and evidence | Test: focused tests, relevant builds, headless fixture and fresh-context review; installed acceptance remains a named closure gate under the no-live-copy instruction.
