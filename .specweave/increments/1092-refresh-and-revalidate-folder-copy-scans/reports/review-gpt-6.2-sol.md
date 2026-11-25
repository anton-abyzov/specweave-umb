<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=openai depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=cf41f4dc9060adc4fc7ea32192b67c1baa9de2cf at=2026-11-25T00:28:32.807Z -->
# 1092 T-12 captured-copy snapshot review round 2 (GPT-6.2 Sol, Codex, effort high)
Verdict: fix first

Head: cf41f4dc9060adc4fc7ea32192b67c1baa9de2cf (main, 1.0.429 merge; contains v1.0.428 with PR #884). Round 1 at bdc54e3ab. Read-only, test assertions inspected, not run.

## Round 1 findings
1. `.envrc` gained a secret: fixed (sourceSnapshot.ts:535; sourceSnapshot.review.test.ts:45).
2. Ancestor swap: not fixed in full; pinned descendant lookup gap below (sourceCaptureAnchor.ts:122; sourceSnapshot.review.test.ts:135).
3. Missing capturedSource: fixed (sourceService.ts:1214; sourceService.review.test.ts:55).
4. Drift stamp: fixed for the buffered writer queue (sourceSnapshot.ts:448; sourceSnapshot.review.test.ts:271); streamed reads gap below.
5. Crash before cleanup: fixed (sourceService.ts:507; sourceService.review.test.ts:71).
6. FIFO open: fixed (sourceSnapshot.ts:173; sourceSnapshot.review.test.ts:285).

## Findings
- High · apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts:122, sourceSnapshot.ts:194 — the pinned lookup follows intermediate symlinks. On Linux, if the root is replaced after pinning and a nested directory in the parked original becomes a link to the replacement tree, both lookups can resolve to the same outside inode; absolute-path checks see a stable replacement tree, so capture packs its bytes. After scanning. Re-verified by source trace.
- Medium · apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:437, sourceDrift.ts:603 — streamed writes can age a racy stamp: a same-size rewrite within one filesystem tick leaves timestamps unchanged; a slow pack write pushes the sampled time past the two-second guard, so deferred move validation can skip hashing changed bytes. Re-verified by source trace.
- Medium · apps/server/src/fleet/folderTransfer/agentCopy.ts:329, destinationService.ts:655 — same-version agent approval drops the revision: the agent checks the preview is clean, then calls copyApprove({ operationId }) without previewRevision; a concurrent replan publishing a ready mirror plan in between can move a destination-only file to backup. Re-verified by source trace.

Author check (closing worker, by reading at cf41f4dc9): agentCopy.ts:329 confirmed, copyApprove({ operationId }) with no previewRevision. Not patched here.
