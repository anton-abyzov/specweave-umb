<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=a91a90111af67d29bec2cbb1acc9532c533a11b4 at=2026-11-24T18:34:06.536Z -->
# Review: 1469 Folder-copy approval binding and snapshot capture, round 5
Verdict: fix first
Reviewer context: GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884. Head a91a90111af67d29bec2cbb1acc9532c533a11b4, delta 8cf0b9da4..a91a90111.

## [high] apps/server/src/fleet/folderTransfer/manifest.ts:802 The scan can still inventory the wrong tree
Round 2's inventory identity finding remains open. If the selected root is temporarily replaced between the identity stat at line 570 and the walk at line 802, restoring the selected root before capture satisfies sourceCaptureAnchor.ts:37. The manifest can still carry a symlink target read from the replacement tree at manifest.ts:765. Capture checks regular files (sourceSnapshot.ts:307), and the final consistency pass receives that same manifest target from sourceService.ts:1317. A copy to an empty destination can create a link that did not exist in the selected tree (apply.ts:863). Bind the inventory and the capture to the same root identity. Re-verified by reading.

## Delta
- Replace all now refuses unseen listed rows and conflict IDs, including same-count swaps, and refuses count growth. Resolved rows may vanish, including in the existing dialog fixture (handoffCopyAuto.ts:150, HandoffFolderCopy.test.tsx:1619). The 200-entry cap is acceptable for the explicit row-wide All choice (FolderCopyHandoff.ts:253, handoffCopyAuto.ts:287). The client cannot distinguish an unlisted swap if the listed IDs and choices stay the same and the count does not grow.
- Streamed reopen and short kept-last reads now route through buffered classification before the entry can be recorded (sourceSnapshot.ts:406, :456, :522). The shrink-between-opens repro is covered at sourceSnapshot.review.test.ts:90. The late disk shortage write remains guarded by destinationService.ts:721.

Both round-four findings close on static inspection. No new delta finding or other open prior finding surfaced. Diff whitespace check passed. Tests and builds were outside this read-only review. PR gates were in progress at readback.
