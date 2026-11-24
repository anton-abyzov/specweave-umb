<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=openai depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=bdc54e3ab280b900bcd10e66d7433508efdaadca at=2026-11-24T15:54:21.928Z -->
# 1092 T-12 captured-copy snapshot review (GPT-6.2 Sol, Codex, effort high)
Verdict: fix first

Head: bdc54e3ab280b900bcd10e66d7433508efdaadca (v1.0.420). Read-only, no tests run.
Scope: sourceSnapshot.ts, sourceCaptureFilesystem.ts, sourceService.ts snapshot paths, destinationService.ts approval validation, related tests.


- Blocker · apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:270 — An untracked `.envrc` can gain a literal secret after scanning and before capture. Capture packs the new bytes under the earlier non-secret classification, and `ready()` exempts `.envrc` from its secret-path check. The secret can travel without per-file approval. Re-verified by reading.
- Blocker · apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:114 — A temporary replacement of an ancestor above the copy root can redirect the open to a different same-volume tree. The descriptor and named-file checks can agree on the replacement, while the final identity check sees the restored directories. Capture can pack bytes from outside the selected tree. Re-verified by reading.
- Important · apps/server/src/fleet/folderTransfer/sourceService.ts:1073 — If a readable operation record loses `capturedSource`, approval treats it as legacy even when the manifest still has `capturedAt`. An unchanged inventory passes approval and chunk reads fall back to live files. The legacy fixture removes only `capturedSource`, so it exercises this downgrade. Re-verified by reading.
- Important · apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:409 — The drift shortcut measures timestamp age after a buffered read waits for the pack writer. A long wait can make a same-tick, same-size rewrite appear safe to skip hashing, so deferred move validation can miss changed bytes. Re-verified by reading.
- Important · apps/server/src/fleet/folderTransfer/sourceService.ts:1702 — A crash after the terminal record is saved but before cleanup leaves the pack on disk. Restart skips it because `snapshotCleanupPending` is written only when cleanup runs and throws. Re-verified by reading.
- Important · apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:150 — On Unix, a scanned file replaced by a FIFO with no writer blocks the read-only open before the regular-file check. Cancellation waits for that build, so it cannot finish or clean up the partial pack. Re-verified by reading.

Author check (closing worker, by reading at the same head): blocker 1 mechanism confirmed (capture overwrites entry.sha256 from the bytes it reads at sourceSnapshot.ts:404 with no content re-classification; ready() skips `.envrc` at sourceService.ts:1209). Finding 3 confirmed (validateReviewed branches only on record.capturedSource at sourceService.ts:1073, else the legacy live-file path). Not patched here, per the closing brief.
