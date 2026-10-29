# 1103 Recover pre-clipping folder-copy partials

## Problem
PR #909 clips cross-volume temporary filenames but cleanup misses the preceding deterministic spelling. A valid Unicode partial created before an upgrade can survive Apply replay and Undo.

## Scope
In: exact pre-clipping deterministic partial cleanup and the complete interrupted-Undo lifecycle across journal, service/startup, wire status and UI, with regression coverage and source validation on PR #909. Out: live copy Retry, moves, Trash operations, deployment, restart, credentials and live databases. Installed copy acceptance remains owned separately under 1092.

## Acceptance Criteria
- [ ] AC-01: Apply replay and Undo remove the exact pre-clipping partial for their journal and destination, alongside current and UUID-style cleanup.
- [ ] AC-02: Other operations' and destinations' partials survive. Cleanup does not attempt an absent over-limit legacy pathname on byte-limited filesystems.
- [ ] AC-03: Focused regression tests and server bundle pass; the pushed exact head is sent to the existing review owner for fresh Sol review before closure.
- [ ] AC-04: An incomplete Undo stays visibly failed and retryable across reload, retains the source operation, and protects unrestored original backups from retention. Successful retry restores the original and reports Undo complete.

- [ ] AC-05: Failed and interrupted Undo exposes an explicit Undo recovery action after UI reload for committed and uncommitted copies. Ending the source hold is a separate explicit action that preserves destination recovery and original backups.
- [ ] AC-06: Startup never applies, commits or registers an incomplete Undo, including during a foreground claim or after a crash before source release.
- [ ] AC-07: Multi-file Undo retry skips its own completed restoration, reconciles a completed move whose completion record was lost, and preserves later user edits; legacy journals remain usable.

## Approach

### Round-4 re-plan before further implementation
Four reviews exposed that helper-level cleanup success does not establish end-to-end rollback recovery. Treat Undo as a durable lifecycle, not another failed Apply. Invariants: incomplete Undo never dispatches Apply/finish/commit/register; only one foreground or startup owner dispatches an operation; the UI offers Undo recovery after reload; each restored filesystem path has synced Undo intent and completion records, with reconciliation when the move completed before its completion record; genuine later edits remain untouched. Preserve original backups until all required restoration completes.

Implement in three sequential boundaries: public status/UI recovery and an explicit source-only end path that preserves destination recovery; startup fencing and foreground claim serialization; durable per-path Undo replay, including repair of a torn final journal line before appending new records. Reproduce each round-4 finding first through the real components/services/filesystem, then test crash windows, multiple files, edited originals and old journals without Undo entries. Run focused server/web tests, relevant bundles and scoped typecheck; push one final head for the original Sol review coordinator. No merge, deployment, closure or live copy Retry in this round.

Round-5 retention correction: expiry must reserve the same per-operation claim as Undo before rereading eligibility, and keep it through backup deletion and the expiry marker update. Verify expiry-first, Undo-first, stale-list eligibility and claim release on deletion failure with real filesystem fixtures and controlled pauses.

Share the existing journal/destination hash suffix between clipped generation and legacy recognition. Match the old deterministic basename against the directory listing before removing it. Exercise real Unicode leftovers through Apply replay and Undo where the host permits their names, plus filesystem-independent listing coverage.

Stash recovery follow-up: persist a pre-apply fingerprint of affected paths and index, then a restored marker before dropping the stash and a completion marker afterward. Reconcile interrupted apply against the actual saved Git trees/index, including untracked content via a private temporary index. Retry only from the recorded pre-state or a proven restored outcome; unknown intermediate state is kept and reported, never overwritten. Completed stashes skip reapplication and preserve later edits.

## Decisions
### Asked
- Sole implementation ownership and exact-head review routing were assigned by the user.
### Defaulted
- Preserve 1092's scan-only scope and installed acceptance hold; track this recovery correction separately.
### Open
- none

## Tasks
### T-01 Recover old deterministic partials
- AC: AC-01, AC-02 | Files: apps/server/src/fleet/folderTransfer/apply.ts, apps/server/src/fleet/folderTransfer/apply.partialName.test.ts, apps/server/src/fleet/folderTransfer/apply.recovery.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/apply.partialName.test.ts apps/server/src/fleet/folderTransfer/apply.recovery.test.ts

### T-03 Surface incomplete cleanup when directory listing fails
- AC: AC-01, AC-02 | Files: apps/server/src/fleet/folderTransfer/apply.ts, apps/server/src/fleet/folderTransfer/apply.partialName.test.ts, apps/server/src/fleet/folderTransfer/apply.recovery.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/apply.partialName.test.ts apps/server/src/fleet/folderTransfer/apply.recovery.test.ts

### T-04 Repair the parameterized regression test context
- AC: AC-01, AC-03 | Files: apps/server/src/fleet/folderTransfer/apply.recovery.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/apply.recovery.test.ts; bash scripts/studio-verify/typecheck-gate.sh --package apps/server --jobs 1

### T-05 Preserve recovery when Undo reports problems
- AC: AC-01, AC-03, AC-04 | Files: apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts, apps/server/src/fleet/FolderCopyHandoff.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts apps/server/src/fleet/FolderCopyHandoff.test.ts

### T-06 Expose incomplete Undo recovery in the UI
- AC: AC-04, AC-05 | Files: packages/contracts/src/folderCopy.ts, packages/contracts/src/folderCopy.test.ts, apps/server/src/fleet/FolderCopyHandoff.ts, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyDone.tsx, apps/web/src/components/studio/HandoffCopyFooter.tsx, apps/web/src/components/studio/HandoffFolderCopy.held.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffFolderCopy.held.test.tsx packages/contracts/src/folderCopy.test.ts

### T-07 Fence incomplete Undo during startup and foreground work
- AC: AC-04, AC-06 | Files: apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts

### T-08 Journal idempotent per-path Undo restoration
- AC: AC-04, AC-07 | Files: apps/server/src/fleet/folderTransfer/apply.ts, apps/server/src/fleet/folderTransfer/undo.ts, apps/server/src/fleet/folderTransfer/undo.recovery.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/undo.recovery.test.ts apps/server/src/fleet/folderTransfer/apply.recovery.test.ts

### T-09 Capture headless incomplete-Undo recovery states
- AC: AC-05 | Files: apps/web/tests/folder-copy/stubs.tsx, reports and evidence | Test: build the existing folder-copy fixture and run headless Chromium recovery at narrow/wide viewports

### T-10 Keep resumed journal appends readable after a torn final line
- AC: AC-07 | Files: apps/server/src/fleet/folderTransfer/durable.ts, apps/server/src/fleet/folderTransfer/durable.recovery.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/durable.recovery.test.ts

### T-11 Serialize backup retention with Undo
- AC: AC-04, AC-06 | Files: apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts | Test: real filesystem interleaving regressions for expiry-first, Undo-first, stale eligibility and deletion failure; focused folderTransfer suites and server bundle

### T-12 Finish interrupted Undo after a lost source commit reply
- AC: AC-04, AC-06 | Files: apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts | Test: real-service two-file partial Undo with unreachable source, then committed-source reconnect; zero registration and full original restoration

### T-13 Isolate crash-replay fixtures from Windows timing and sync-spy leakage
- AC: AC-03, AC-07 | Files: apps/server/src/fleet/folderTransfer/apply.test.ts | Test: batch-boundary replay at synced intents, lost done marks and original-backup boundaries, plus unchanged 2000-file batching stress; real journal durability and restored originals checked

### T-14 Claim Retry before reading recovery eligibility
- AC: AC-04, AC-06 | Files: apps/server/src/fleet/folderTransfer/destinationService.ts, apps/server/src/fleet/folderTransfer/destinationService.undoRecovery.test.ts | Test: delayed actual record read while Undo competes, then Undo-first partial marker refuses Retry; source commit and registration cannot consume stale pre-Undo state

### T-15 Verify concurrent Retry reports operation ownership
- AC: AC-03, AC-06 | Files: apps/server/src/fleet/folderTransfer/destinationService.grant.test.ts | Test: held-commit service test rejects overlapping Undo and Retry as busy before registration, then completes once released

### T-16 Journal and reconcile stash restoration during Undo
- AC: AC-04, AC-07 | Files: apps/server/src/fleet/folderTransfer/apply.ts, apps/server/src/fleet/folderTransfer/undo.ts, apps/server/src/fleet/folderTransfer/undo.stashRecovery.test.ts | Test: real Git/service partial Undo followed by retry, staged/unstaged/untracked state, intent/apply/drop crash windows, legacy journals and later user edits preserved

### T-17 Repair Windows journal tail recovery and manifest path assertion
- AC: AC-03, AC-07 | Files: apps/server/src/fleet/folderTransfer/durable.ts, apps/server/src/fleet/folderTransfer/durable.recovery.test.ts, apps/server/src/fleet/folderTransfer/manifest.test.ts | Test: existing torn/concurrent journal and Undo recovery regressions plus manifest registration preservation; applicable Windows hosted CI must pass

### T-18 Reconcile unstaged deletions before completing stash Undo
- AC: AC-04, AC-07 | Files: apps/server/src/fleet/folderTransfer/undo.ts, apps/server/src/fleet/folderTransfer/undo.stashRecovery.test.ts | Test: real stash unstaged deletion and interrupted apply with completion record lost, replay preserves deletion and later recreated files

### T-19 Restore valid local stash filenames without weakening transfer path validation
- AC: AC-04, AC-07 | Files: apps/server/src/fleet/folderTransfer/undo.ts, apps/server/src/fleet/folderTransfer/undo.stashRecovery.test.ts | Test: real POSIX newline, tab and backslash untracked stash names restore with tracked edits; retain lexical containment and wire-path guard

### T-02 Verify and close 1103
- AC: AC-03 | Files: reports and evidence | Test: focused folderTransfer tests, server bundle, specweave verify and fresh exact-head Sol review from the existing review owner
