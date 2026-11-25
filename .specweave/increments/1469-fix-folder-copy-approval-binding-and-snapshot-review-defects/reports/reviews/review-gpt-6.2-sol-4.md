<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=8cf0b9da4004b8deba0529976fc62658967ab723 at=2026-11-24T18:15:45.261Z -->
# Review: 1469 Folder-copy approval binding and snapshot capture, round 4
Verdict: fix first
Reviewer context: GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884. Head 8cf0b9da4004b8deba0529976fc62658967ab723, delta eca816129..8cf0b9da4.

## [high] apps/web/src/components/studio/handoffCopyAuto.ts:149 Replace everything accepts a different conflict at the same count
Window A clicks Replace everything on two open conflicts, a.txt and b.txt. While it stages secrets, a.txt becomes identical and c.txt becomes a conflict. Window B finishes a comparison of that state. A's row-wide answer expands against the current plan (apps/server/src/fleet/folderTransfer/destinationService.ts:618). Row IDs and counts still match. The readiness check skips the vanished a.txt ID and never checks the new c.txt ID. Both dialog and watcher can submit the new revision and replace c.txt without a fresh approval. Re-verified by reading. The delta catches net count changes and new rows.

## [high] apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:500 Streamed capture can reopen a file after it shrinks
An eligible config exceeds the buffered limit at scan and at the first capture stat. The buffered attempt closes it and queues streaming. If the file shrinks below the probe limit before the streamed reopen, the guard has already evaluated an artificial large size at line 499 and skipped the unprobed file. The streamed read uses the new size at line 404 and writes unclassified bytes at line 423. A small config containing a recognized secret can enter the pack as ordinary data. Re-verified by reading. The delta covers a shrink before the first capture stat.

Both round-three findings remain open through these paths. The late shortage race remains closed (apps/server/src/fleet/folderTransfer/destinationService.ts:721). No other prior finding surfaced in this delta.

Static review. Diff whitespace check passed. No tests or builds run. PR gate jobs were still in progress at the last read.
