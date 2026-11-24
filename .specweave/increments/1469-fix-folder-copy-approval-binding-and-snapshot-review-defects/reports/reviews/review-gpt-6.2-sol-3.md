<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=eca816129ab20b2c25e3dde7ac050ab6dc973150 at=2026-11-24T17:51:10.121Z -->
# Review: 1469 Folder-copy approval binding and snapshot capture, round 3
Verdict: fix first

Reviewer context: GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884. Reviewed head eca816129ab20b2c25e3dde7ac050ab6dc973150, delta 3b5ba2922..eca816129, and the prior records and 1469 contract.

## [high] apps/web/src/components/studio/handoffCopyAuto.ts:146 Replace everything can still approve a conflict the click never saw
Window A clicks Replace everything on a row with one open conflict and another file that was new to the destination. While A stages secrets, the destination gains a different version of that second file. Window B answers the first conflict Take theirs and finishes comparing, so the second file is now an open conflict. A's row-wide answer expands against the current plan (apps/web/src/components/studio/handoffCopyAuto.ts:278, apps/server/src/fleet/folderTransfer/destinationService.ts:618) and takes both source versions. The shared decision is as expected and the new conflict ID is absent from A's basis, so readiness passes. The dialog and watcher then send the new revision (apps/web/src/components/studio/HandoffFolderCopy.tsx:545, apps/web/src/components/studio/HandoffFolderCopyWatcher.tsx:542 and :587). The plan replaces the second file without A reviewing that replacement. Re-verified by reading. The round-two test covers a changed decision on a shared ID.

## [high] apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:506 Streamed capture misses a config that shrank below the probe limit
If the inventory sees an untracked settings.json larger than 8 MiB and capture opens a small version containing a recognized token, the old inventory size selects the streamed path. It runs the guard with Number.MAX_SAFE_INTEGER (:499), which fails the new size-at-most-64-KiB condition (:341). The read then writes bytes straight into the pack (:423) and records the actual size and hash under the old non-secret class (:487). The captured approval validates the pack without rescanning the source (apps/server/src/fleet/folderTransfer/sourceService.ts:1081). The inventory can still come from a different tree (apps/server/src/fleet/folderTransfer/manifest.ts:570 and :802), and the same bypass occurs on an ordinary shrink. Re-verified by reading. The new 70,000-byte fixture takes the buffered path.

## Prior findings
The two high round-two findings remain open through the paths above. The specific shared-ID choice change and buffered shrink are covered. The late shortage write is closed by the locked assertSamePreview at apps/server/src/fleet/folderTransfer/destinationService.ts:721. No other round-one finding remains open in this delta.

Read-only review. Diff whitespace check passed. No tests or builds run. The PR head matched the reviewed SHA and its gate jobs were still in progress at the last read.
