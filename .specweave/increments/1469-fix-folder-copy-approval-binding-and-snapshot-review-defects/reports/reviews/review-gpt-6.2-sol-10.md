<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=6a5ec17874174c8c34b3b518955698e495e78da0 at=2026-11-24T20:04:19.635Z -->
# Review: 1469 Folder-copy approval binding and snapshot capture, round 10
Verdict: ship

GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884. Head `6a5ec17874174c8c34b3b518955698e495e78da0`, delta `b3a19fa1d..6a5ec1787`. Diff whitespace check passed. Fixtures inspected without execution.

## Findings

No blockers. The round-9 high finding is closed, re-verified by reading. At `apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts:76`, EIO on either platform returns an ordinary pinning error. The Linux branch checks the descriptor first and closes it on refusal (`:96`). A successful alias lookup of a different object refuses as a changed root (`:83`). The four allowed absence or unsupported-operation codes still require a fresh identity match (`:85`). Only the resulting `CaptureFilesystemRefused` reaches live hashing on a move (`apps/server/src/fleet/folderTransfer/sourceService.ts:971`).

The 11 original findings remain closed within the increment contract. The delta leaves the prior fixes intact and closes the remaining capture downgrade from round 9.

## Follow-ups

- [low] `apps/server/src/fleet/folderTransfer/sourceSnapshot.review.test.ts:252`. An early Linux open or descriptor failure would also satisfy the generic error assertions, so the fixture can pass without hitting its Linux lookup seam. Assert that the seam ran and that the refusal reports EIO. Re-verified by reading.
- D-05 stays in 1471. Scan inventory and Git classification still use the mutable path (`apps/server/src/fleet/folderTransfer/manifest.ts:632`, `:664`, `:753`).
