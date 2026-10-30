# 1092 Refresh and revalidate folder-copy scans

## Problem
The handoff dialog can resume a persisted scan and present historical external worktree registrations as current folders. Reopening does not guarantee a new scan. Missing registered folders can also appear in new scans.

## Scope
In: scan timestamps, explicit safe freshness check, missing-registration reporting, source and destination validation before approval, regression and headless evidence. Out: cleanup, Git pruning and casual app/service restart. October 27 explicit user authorization adds actual supported project migration and installed acceptance after recovery fixes, fresh review, applicable CI and shipped-code admission; release dispatch remains with its existing owner.

## Acceptance Criteria
- [ ] AC-01: Fresh scans count only existing registered external worktree folders; missing registrations are separately labelled and no registration is removed.
- [ ] AC-02: Resumed scans expose their timestamp or unknown historical age. Refresh checks current source state without cancelling jobs, changing selections, approvals or secret exclusions.
- [ ] AC-03: Copy approval validates the exact reviewed source artifact and destination preview before transfer. Legacy live-file jobs require fresh source inventory; durable captured-file jobs may copy reviewed bytes while newer source work continues. Missing or corrupt captured data never falls back to live files. Destination changes still require review.
- [ ] AC-04: Removed and added worktrees, resume versus new scan, unchanged refresh and changed source/destination are covered by isolated tests. Current source, implementation and installed acceptance are reported separately.

- [ ] AC-05: Copy comparison distinguishes planned counts from repository size and pending decisions, avoids asserting unproven destination repository identity, and offers compact group choices with explicit per-file review without applying a transfer.

- [ ] AC-06: The explicitly authorized M4 umbrella to Ministorm migration is completed through supported controls with prior destination outcomes reconciled, unique destination work preserved, secrets opt-in only, verified destination project/coordinator path and continuation, and real screenshots for every meaningful step. Source drafts, active workers and Stop holds survive.

- [ ] AC-07: A durable immutable snapshot of selected non-secret files makes reviewed copies independent of later source churn, including existing destinations. Restart, corruption, disk failure, cancellation and cleanup preserve source files; live freshness and deferred move ownership checks remain honest and strict.

## Approach
Read-only scan validation retains the original operation and manifest. Store a source inventory signature at measurement and manifest creation; expose refresh diagnostics with current summary separately from the saved summary. Validate it at destination approval over the operation-scoped source route. Refresh does not apply, cancel or prune anything. A changed scan requires an explicit new comparison. Existing selections survive; conflict choices remain on the old job and are not silently replayed onto changed data.

## Decisions
### Asked
- none
### Defaulted
- Preview clarity groups conflict controls visually without excluding, merging or preselecting any file. Counts describe currently planned actions, not source repository size. Destination identity statements are limited to scan evidence.
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

### T-05 Clarify copy preview counts and reduce conflict overload
- AC: AC-05 | Files: apps/web/src/components/studio/HandoffCopyPreview.tsx, apps/web/src/components/studio/HandoffCopyPreview.test.tsx, apps/server/src/fleet/folderTransfer/reconcile.ts, apps/server/src/fleet/folderTransfer/reconcile.test.ts, apps/web/tests/folder-copy/main.tsx, apps/web/tests/folder-copy/previewClarity.tsx, reports and evidence | Test: focused preview and reconcile tests, headless narrow/wide light/dark synthetic preview, relevant web build and scoped typecheck

### T-06 Complete the authorized SpecWithCode project migration
- AC: AC-04, AC-06 | Files: reports and evidence | Test: supported source/destination identity and job-state reconciliation, exact destination integrity and backup/Undo checks, coordinator handoff/continuation verification and file-backed real screenshots after shipped-code/exclusive-native admission

### T-03 Verify and close 1092
- AC: AC-04 | Files: reports and evidence | Test: focused tests, relevant builds, headless fixture and fresh-context review; installed acceptance remains a named closure gate under the no-live-copy instruction.

### T-07 Wait for the published ready scan to finish persisting before revalidation
- AC: AC-02, AC-03 | Files: apps/server/src/fleet/folderTransfer/sourceService.ts, apps/server/src/fleet/folderTransfer/sourceService.measure.test.ts | Test: real ready-record persistence pause must wait then validate; in-progress measuring stays busy; portableGit internal split-index concurrent commit regression

### T-08 Explain copy action availability and align disk guards
- AC: AC-04, AC-05 | Files: apps/web/src/components/studio/HandoffCopyFooter.tsx, apps/web/src/components/studio/HandoffCopyFooter.test.tsx, apps/web/tests/folder-copy/previewClarity.tsx, reports and evidence | Test: isolated blocker/callback matrix, existing copy lifecycle tests, headless footer screenshots and production web build. Preserve all live copy holds.

### T-09 Verify and close 1092
- AC: AC-04, AC-06 | Files: reports and evidence | Test: existing installed migration acceptance gates remain; do not close from fixture proof.

### T-10 Recover a refused stale copy through a fresh comparison
- AC: AC-02, AC-03, AC-04 | Files: packages/contracts/src/folderCopy.ts, apps/server/src/fleet/FolderCopyHandoff.ts, apps/server/src/fleet/FolderCopyHandoff.test.ts, apps/server/src/fleet/folderTransfer/destinationService.ts, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, apps/web/src/components/studio/handoffFolderCopyPending.ts, apps/web/src/components/studio/handoffCopyScanRecovery.ts, apps/web/src/components/studio/HandoffCopyScanFreshness.tsx, apps/web/src/components/studio/HandoffCopyFooter.tsx, apps/web/tests/folder-copy/previewClarity.tsx, apps/web/tests/folder-copy/verify.mjs, apps/web/tests/folder-copy/stubs.tsx, docs/user/moving-a-project.md, reports and evidence | Test: typed stale-refusal adapter and complete refusal/reopen/recompare lifecycle tests, existing unchanged/changed source two-server guards, headless recovery controls and relevant product builds

### October 29 recovery decision
Anton explicitly requested investigation, code repair and a release for the repeated copy refusal. The saved live scans predate changed source work. Preserve the refusal for an existing destination; make its recovery explicit and durable across reopening. A stale approval must disable repeated Copy/Replace actions and offer a fresh comparison directly. Do not replay destination conflict choices or secret approval onto changed source data. Existing source/destination safety checks and manual installed migration acceptance remain required.
Native verification also found a read-only freshness request that kept the dialog busy without sustained source scan activity. Bound that UI wait to two minutes; keep the saved job and choices, never infer freshness or approval from timeout, and ignore a late reply after the bounded wait ends. This addresses the observed indefinite UI lock; the underlying transport stall remains unproven.

### T-11 Replace stale worktree notices after a fresh scan
- AC: AC-02, AC-05 | Files: apps/web/src/components/studio/handoffCopyNotices.ts, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyGuide.tsx, apps/web/src/components/studio/handoffCopyAuto.test.ts, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, docs/user/moving-a-project.md, reports and evidence | Test: refresh removes old outside-worktree names while retaining unrelated destination warnings; declared worktree totals survive shortened name previews; actual wizard and headless copy regressions, web typecheck/build and independent review

### T-12 Capture immutable reviewed source files before approving copies
- AC: AC-02, AC-03, AC-04, AC-07 | Files: apps/server/src/fleet/folderTransfer/sourceSnapshot.ts, apps/server/src/fleet/folderTransfer/sourceSnapshot.test.ts, apps/server/src/fleet/folderTransfer/sourceService.ts, apps/server/src/fleet/folderTransfer/sourceService.snapshot.test.ts, apps/server/src/fleet/folderTransfer/sourceRoutes.ts, apps/server/src/fleet/folderTransfer/sourceClient.ts, apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/twoServer.snapshot.test.ts, apps/server/src/fleet/folderTransfer/sourceService.test.ts, apps/server/src/fleet/folderTransfer/sourceService.measure.test.ts, apps/server/src/fleet/folderTransfer/twoServer.verify.test.ts, apps/server/src/fleet/FolderCopyHandoff.ts, packages/contracts/src/folderCopy.ts, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/handoffCopySnapshot.ts, apps/web/src/components/studio/HandoffCopyScanFreshness.tsx, apps/web/src/components/studio/HandoffCopyFooter.tsx, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, apps/web/tests/folder-copy/previewClarity.tsx, apps/web/tests/folder-copy/stubs.tsx, apps/web/tests/folder-copy/verify.mjs, docs/user/moving-a-project.md, reports and evidence | Test: real two-server reviewed copy into existing destination under continuous selected/unselected source churn; legacy refusal, changed destination refusal, missing/corrupt snapshot, restart/cleanup and secret exclusion regressions; scoped coverage, server/web typecheck/build, headless real wizard evidence and fresh independent review

2026-10-29 decision and ownership: the user requires a working copy while active owners remain untouched. Root transferred exclusive implementation ownership of copy-button-reasons at36290fa3fc22f3e0b97340ce756438748317cbe1 to copy-snapshot-fleet. A snapshot stores only selected non-secret bytes and link metadata before the manifest becomes ready; no hardlinks or unsafe source-path traversal. Publish readiness only after durable backing/manifest, validate exact artifacts on approval, and serve those artifacts after restart. Keep live Measure again diagnostics separate. Captured copies explicitly describe that newer source work stays on source and offer a new comparison. Retain destination preview/Apply guards and strict deferred copy-and-move idle/current snapshot checks. Legacy saved jobs remain strict. Operation cleanup owns generated artifacts only; low disk/partial capture must not publish readiness. Finish with independent exact-head review, required delivery gates and verify/close1092 under existing acceptance ownership.

T-12 additive wire scope: apps/server/src/fleet/folderTransfer/manifest.ts carries capturedAt in the reviewed manifest and destination preview, so unavailable source-status diagnostics cannot accidentally restore auto-approval. Destination rules and old-job defaults remain unchanged.

T-12 final scope decision: captured backing applies only to copy-only, matching the actual authorized saved job. Copy-and-move retains its existing live transfer, held-copy and strict deferred-context checks. Approval validation returns current:true plus captured:true for valid immutable backing, preserving old destination protocol behavior; live checkScan still reports actual current inventory. Extend regression Files to destinationService.held.test.ts solely to exercise the new approval seam for its copy-only case, without changing assertions.

T-12 scope addition from real source capture (2026-10-29): the untracked name scripts/.cf-monitor.env bypassed the existing prefix-only secret predicate. Root authorized the bounded shared WorkspaceSensitivePaths.ts fix and a separate WorkspaceSensitivePaths.env.test.ts (existing test file exceeds 1500 lines), plus real manifest/opt-in assertions. Read-only ownership check found only completed 0949 T09 scope for these paths; no active writer identified. Preserve Git-tracked policy and template exemptions; do not read real credential contents.

T-12 legacy regression seam: apps/server/src/fleet/folderTransfer/apply.test.ts and pullWorker.test.ts continue testing live-file refresh/restoration through copy-and-move, whose semantics remain unchanged. Keep every existing assertion; new snapshot tests verify copy-only frozen bytes separately. Missing/corrupt/protected-secret reviewed artifacts use a hard refusal with compare-again recovery and never the legacy empty-destination stale exception.

T-12 visual review addition: handoffCopyNotices.ts and handoffCopyAuto.test.ts distinguish captured copy-only active-work wording from legacy/move warnings. Later edits stay on source; captured versions remain included. Parent requested this correction from the actual narrow screenshot before acceptance.

T-12 independent security review: asynchronous leaf observations alone can miss a replaced-and-restored ancestor. Before reading any source bytes, retain top-down bigint directory identities/change times from filesystem root through leaf parent and verify bottom-up after opening; retain no-follow and opened/named file identity. Retry only a changed ancestor proof at most three times. This protects local filesystem rename races; coarse/cached network metadata is explicitly outside the captured-copy guarantee. Review uses static analysis and ordinary fictional file-replacement/cancellation cases only, no blocked exploit reproduction.

T-12 mixed-version approval correction: absent source diagnostics plus an older destination without capturedAt must stay at manual review. Extend Files to HandoffFolderCopy.testkit.tsx only for a realistic default source-status reply; preserve all existing behavioral assertions and test unavailable diagnostics both with and without the destination capture marker.

T-12 filesystem admission: root authorized sourceCaptureFilesystem.ts and sourceCaptureFilesystem.test.ts. Fail captured mode closed on unsupported/unknown/coarse/network filesystem capabilities using bounded native type probes; admit local APFS, Linux ext4/xfs/btrfs/tmpfs, and positively identified local NTFS. Cache admission per root/device, reject nested cross-device files, retain copy-and-move semantics.
