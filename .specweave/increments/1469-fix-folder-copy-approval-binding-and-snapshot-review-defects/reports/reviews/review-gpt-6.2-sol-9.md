<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=b3a19fa1d9518c3d055154eb4d68b50feb08aadb at=2026-11-24T19:47:41.324Z -->
# Review: 1469 Folder-copy approval binding and snapshot capture, round 9
Verdict: fix first

GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884. Reviewed head `b3a19fa1d9518c3d055154eb4d68b50feb08aadb`, delta `7f12e5dfd..b3a19fa1d`. Read-only review. Diff whitespace check passed. Tests inspected without execution.

## [high] apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts:63 An anchor I/O error can downgrade a move to live reads

On a supported filesystem, if the anchor lookup returns a transient I/O error such as EIO while the ordinary root lstat succeeds, the code throws CaptureFilesystemRefused. The Linux alias lookup has the same branch at lines 77–81. The source then uses live hashing under the saved classification (sourceService.ts:971, :979, manifest.ts:1063). A file that gained secret content since scanning can bypass the capture recheck, and the destination can accept a stale scan into an empty folder (sourceSnapshot.ts:539, sourceService.ts:1211, destinationService.ts:671). The PR base uses ordinary ancestor checks and has no downgrade on this alias error (bf2021f9e, sourceSnapshot.ts:93–97, :148). Re-verified by tracing both revisions. No fault injection run. Reserve the fallback for demonstrated lack of anchor support and propagate other lookup errors.

The round-8 removed-root case now refuses at sourceCaptureAnchor.ts:59–64. Linux also preserves other errors from opening the root at line 72. The earlier findings retain their dispositions within the 1469 contract, but the new anchor error path still bypasses AC-02 and AC-03.

## Follow-ups

- [low] apps/server/src/fleet/folderTransfer/sourceSnapshot.review.test.ts:240 exercises Linux removal before open. It leaves the post-open proc lookup failure and root recheck at sourceCaptureAnchor.ts:75–81 untested. Re-verified by reading the fixture.
- D-05 stays in 1471. Scan inventory and Git classification still use the mutable pathname (apps/server/src/fleet/folderTransfer/manifest.ts:632, :664, :753).
