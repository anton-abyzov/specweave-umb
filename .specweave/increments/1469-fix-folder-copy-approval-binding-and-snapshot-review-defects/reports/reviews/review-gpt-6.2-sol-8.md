<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=7f12e5dfd883b6cae04f24e68a30d21f8d2e04ae at=2026-11-24T19:34:32.153Z -->
# Review: 1469 Folder-copy approval binding and snapshot capture, round 8
Verdict: fix first

GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884 at `7f12e5dfd883b6cae04f24e68a30d21f8d2e04ae`. Delta `68c1f70ea..7f12e5dfd`. Read-only review. Diff whitespace check passed. Tests inspected without execution.

## [high] apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts:57 A vanished macOS root can still downgrade a move to live reads

If the scanned directory is removed after `lstat`, its inode lookup can return ENOENT even when `/.vol` works. The new anchor code treats that as an unsupported filesystem without checking the named root again. A replacement directory present by the time `hashSelected` runs is read under the old inventory (`sourceService.ts:971`, `manifest.ts:1060`). An ordinary .envrc that now holds a secret skips capture's content recheck, and approval into an empty destination can proceed on a stale scan (`sourceSnapshot.ts:539`, `sourceService.ts:1217`, `destinationService.ts:671`). The PR base propagated a missing root observed by its ancestor check (`bf2021f9e`, `sourceSnapshot.ts:93`). Re-verified by tracing both commits and confirming an absent inode returns ENOENT on this Mac with a working `/.vol`. The end-to-end race was not executed. Recheck the named root on an alias miss before allowing the unsupported-filesystem fallback.

## Round-7 finding

Closed for a symlink already present at pinning and for Linux open failure or descriptor mismatch (`sourceCaptureAnchor.ts:48`, `:61–74`). Those paths now propagate ordinary errors. The fixture at `sourceSnapshot.review.test.ts:216` covers the original symlink case. The other original findings retain their round-7 disposition. AC-02 and AC-03 still have the macOS gap above.

## Follow-ups

- D-05 / 1471. Bind scan-time inventory and Git classification to the pinned root (`manifest.ts:632`, `:664`, `:753`).
- Linux open errors such as EACCES and EMFILE now report a changed root (`sourceCaptureAnchor.ts:64`). This fails closed. Preserve the underlying error for diagnosis.
