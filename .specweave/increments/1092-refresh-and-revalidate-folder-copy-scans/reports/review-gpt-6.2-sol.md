<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=openai depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=bdc54e3ab280b900bcd10e66d7433508efdaadca at=2026-11-24T15:57:14.082Z -->
# 1092 closure review of task Files (GPT-6.2 Sol, Codex, effort high)
Verdict: fix first

Head: bdc54e3ab280b900bcd10e66d7433508efdaadca (v1.0.420). Read-only, no tests run. All 43 task-listed files present at the head.

## Per AC
- AC-01 gap: apps/server/src/fleet/folderTransfer/manifest.test.ts:332 covers ordinary removal, addition and registration retention; a missing worktree with a non-directory ancestor aborts the scan (manifest.ts:309).
- AC-02 gap: apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx:797 covers scan age, unchanged Refresh and timeout; Refresh can expand the secret list and retain obsolete missing-worktree notices.
- AC-03 gap: twoServer.snapshot.test.ts:133 proves captured bytes survive churn and changed destinations or damaged backing are refused; approval can still accept a different preview from the one the caller saw.
- AC-04 met: manifest.test.ts:332, apps/web/tests/folder-copy/verify.mjs:353, twoServer.verify.test.ts:636; evidence separates source, fixture and installed checks.
- AC-05 met: reconcile.test.ts:588, HandoffCopyPreview.test.tsx:412.
- AC-07 met: twoServer.snapshot.test.ts:133, sourceSnapshot.test.ts:61, sourceService.snapshot.test.ts:57; folderCopyPreparation.ts:206 keeps idle and drift checks.

## Findings
- Blocker · packages/contracts/src/folderCopy.ts:335, apps/server/src/fleet/folderTransfer/destinationService.ts:646 — approval can use an unseen preview. Window A reviews a job; window B changes a conflict choice and finishes comparing; A clicks Copy; approval carries only operationId and secret options, so the server validates and transfers B's plan. The concurrent-approval test covers two approvals of the same plan. Re-verified statically.
- Important · apps/web/src/components/studio/handoffCopyScanRecovery.ts:50, handoffCopySecrets.ts:73, useCopySecrets.ts:115 — Refresh can expand the secret list: a newly added `.env.local` enters the live summary and, with secrets included, the next Copy stages it unless unticked; the saved pointer stays identical so the assertion misses it. Re-verified statically.
- Important · apps/server/src/fleet/folderTransfer/manifest.ts:309 — a registered worktree whose parent is replaced by a file gives `ENOTDIR` from lstat; the scan throws before labelling the registration missing. Re-verified statically.
- Important · apps/web/src/components/studio/handoffCopyNotices.ts:32 — restore a previously missing folder and Refresh: the live summary counts it present while the saved warning still says missing. Re-verified statically.
- Important · apps/server/src/fleet/folderTransfer/destinationService.ts:703, :1209, apps/web/src/components/studio/HandoffCopyFooter.tsx:192 — approval persists a disk shortage; freeing space and recomputing leaves the old disk flag set and both approval actions disabled. Re-verified statically.

## Evidence
The release receipt records 100 passing tests across seven files; older ledger runs apply to their recorded heads; the installed README honestly limits its claim to an isolated one-machine check (live scan and Refresh UI need a second paired machine).

Author check (closing worker, by reading at the same head): blocker confirmed, FolderCopyApproveInput (folderCopy.ts:335) has no plan or preview identity and approve() reads the current plan (destinationService.ts:646-650). Not patched here, per the closing brief.
