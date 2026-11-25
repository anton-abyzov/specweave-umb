<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=openai depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=cf41f4dc9060adc4fc7ea32192b67c1baa9de2cf at=2026-11-25T00:28:00.498Z -->
# 1092 closure review round 2 (GPT-6.2 Sol, Codex, effort high)
Verdict: fix first

Head: cf41f4dc9060adc4fc7ea32192b67c1baa9de2cf (main, 1.0.429 merge; contains v1.0.428 with PR #884). Round 1 at bdc54e3ab. Read-only, no tests run. All 43 task-listed files reviewed.

## Per AC
- AC-01 met: apps/server/src/fleet/folderTransfer/manifest.ts:313.
- AC-02 gap: Refresh can overwrite a secret exclusion saved by another window (apps/web/src/components/studio/useCopySecrets.ts:98).
- AC-03 gap: direct Copy binds the reviewed revision; Replace everything can approve a later destination version never seen (apps/web/src/components/studio/HandoffFolderCopy.tsx:541).
- AC-04 met: manifest.test.ts:332, HandoffFolderCopy.wizard.test.tsx:797, twoServer.verify.test.ts:645.
- AC-05 met: HandoffCopyPreview.test.tsx:381.
- AC-07 met: twoServer.snapshot.test.ts:138, sourceService.snapshot.test.ts:107, portableGit.test.ts:145.

## Round 1 findings
1. Unseen preview: not fixed end to end (direct approval fixed, destinationService.previewRevision.test.ts:79; bulk path below).
2. New secrets selected by Refresh: fixed for the single-window case (handoffCopyRefresh.test.ts:20).
3. ENOTDIR abort: fixed (manifest.missingWorktree.test.ts:18).
4. Stale missing-worktree notice: fixed (handoffCopyRefresh.test.ts:45).
5. Stale disk shortage: fixed (destinationService.previewRevision.test.ts:104, HandoffCopyFooter.test.tsx:107).

## Findings
- High, remaining · apps/web/src/components/studio/handoffCopyAuto.ts:112, HandoffFolderCopy.tsx:545 — Replace everything can approve unseen destination edits. Edit an already conflicting destination file before the bulk recompare scans it; conflict ID, count and decision stay the same; the bulk check passes and sends the new revision, so approval replaces the edited file and moves its latest version to backup without another review. Re-verified statically.
- High, new · apps/web/src/components/studio/useCopySecrets.ts:98, HandoffFolderCopy.tsx:272 — Refresh can restore an excluded secret. Two windows open the same saved copy; B unticks `.env`; A refreshes, finds `.env.local`, adds that exclusion to its stale in-memory choices and overwrites the shared saved copy; on reopen `.env` is selected again and can be sent on approval. Re-verified statically.

Evidence: November 25 UTC verify covers umbrella checks; the 100 focused passes and isolated installed check are from 1.0.420; live two-machine UI acceptance unverified.

Author check (closing worker, by reading at cf41f4dc9): first finding confirmed. replaceAllBasis/listedDecisions (handoffCopyAuto.ts:91-130) key on choices, decisions, conflict ids and counts, not destination content; settlePreview approves with next.previewRevision (HandoffFolderCopy.tsx:545). Not patched here.
