<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=f7a16281c53d503295d7680f8ea50a35c80746a4 head=8489381e500d1f3193ab47e2b1de6af0a97bf6c9 at=2026-11-25T01:35:23.703Z -->
# Review of increment 1469, PR #903
Verdict: fix first

Reviewed `f7a16281c53d503295d7680f8ea50a35c80746a4..8489381e500d1f3193ab47e2b1de6af0a97bf6c9` as the OpenAI fallback for Claude-authored changes. Static re-verification only.

## [high] Reopened Replace everything can still copy an excluded secret (AC-13)

Capture a source with no secrets. Window A creates `.env`, finds it with Refresh, explicitly ticks it, and clicks Replace everything. The source accepts the live path and stores it in the offer while the saved summary stays empty. Close A during re-compare and reopen the dialog while the Replace everything pointer is present. Before the reopened dialog approves, window B refreshes from its still-open preview and records the `.env` exclusion in shared storage. The reopened dialog already holds the pointer and reads the old summary. `sendableSecrets` returns `null` even with the exclusion present. `sendOnce` leaves the old offer untouched, `sendTicked` accepts `null === null`, and `approveInput` omits `expectedSecrets` because Secrets is still on. The destination then pulls `.env` from the old offer. Captured validation checks the saved artifact, so the later `.env` does not force a new comparison.

Re-verified by source trace. `apps/web/src/components/studio/handoffCopyScanRecovery.ts:56`, `apps/server/src/fleet/folderTransfer/sourceService.ts:761` and `:1512`, `apps/server/src/fleet/folderTransfer/sourceSecrets.ts:70`, `apps/web/src/components/studio/HandoffFolderCopy.tsx:506`, `:678` and `:913`, `apps/web/src/components/studio/handoffCopySecrets.ts:97`, `apps/web/src/components/studio/useCopySecrets.ts:159` and `:192`, `apps/web/src/studio/copySecretsPolicy.ts:95`, `apps/server/src/fleet/folderTransfer/sourceService.ts:1086`, `apps/server/src/fleet/folderTransfer/destinationService.ts:1463`. Send an explicit empty expectation when the summary yields no paths, or refuse approval until the staged offer can be reconciled.

## Prior findings

- AC-12 repository replacements now enter the destination digest. The occupied-folder and different-identity branches match reconciliation, and file-over-folder still uses the unreadable-subtree guard. Re-verified in `apps/server/src/fleet/folderTransfer/destinationScan.ts:131` and `:244` and `apps/server/src/fleet/folderTransfer/reconcile.ts:365` and `:432`.
- AC-13 stale saves only record changes from the displayed choice. Refresh adds exclusions against its own base. The dialog re-stages a changed concrete list, and the watcher checks the settled choice before approval and during repair. Re-verified in `apps/web/src/components/studio/useCopySecrets.ts:107`, `:129` and `:156` and `apps/web/src/components/studio/HandoffFolderCopyWatcher.tsx:493` and `:520`. The dialog's empty-summary case remains open above.
- AC-14 through AC-16 remain intact at `apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts:125`, `apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:419` and `apps/server/src/fleet/folderTransfer/agentCopy.ts:330`.

## Follow-ups

The prior report's follow-ups stay open, including destination edits after approval, exclusions keyed by scan-relative path, and D-05 in increment 1473. No tests run in this read-only pass. PR checks were still running at the pinned head.

Verdict: fix first
