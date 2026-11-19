<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=e73ffa906d339741ee066300049351df09889b4b at=2026-11-19T19:38:29.935Z -->
# Review: 1390 T-17 Sync and Add confinement, round 4
Verdict: fix first
Reviewer context: fresh session, static Git-object review of `0893ee9b..e73ffa906d339741ee066300049351df09889b4b`. Citations below are under `apps/server/src/fleet/folderTransfer/` in the reviewed repository.

## [high] Item 1 remains open: the path authorized need not be the path Git writes

`git.ts:34-40,123-129` decodes stdout with a fatal UTF-8 decoder, but its default BOM handling drops a leading U+FEFF. This is a valid filename character and produces no replacement character. `gitConfinement.ts:22-23,88-95` therefore accepts the changed first name. `apply.ts:509-518,1203-1209` checks the resulting parent chain, then tells Git to update the original tree. The actual parent can be writable by another user without ever passing the privacy check. Preserve initial BOM bytes as pathname data and verify byte-for-byte round trip, or refuse before the Git write. This establishes a wrong-folder authorization, not an observed out-of-root write.

## [high] Item 6 remains open: the first backup can move bytes the preview did not approve

`apply.ts:547-562,574-588` correctly refuses an existing mismatch, including on retry before a backup exists. But the successful hash comparison and the move are separate, with a durable journal append between them on the first attempt. The guard checks parent directories (`confinement.ts:666-677`), not whether another ordinary user can modify the regular file in place. If that user changes its bytes after comparison, the move takes the changed file and Apply can replace it. A private parent does not establish exclusive write access to existing file contents. Refuse when exclusive control of the file cannot be established.

## Remaining determinations

- Item 2: the old admin-record overwrite is closed. `worktreeRepair.ts:65-74,84-98` compares a normalized backlink and replaces only the local worktree pointer. It does not enforce literally exact stored paths: `resolve(recorded.trim())` also accepts some relative or whitespace-altered records. No separate out-of-folder write established from this delta.
- Item 3: closed. Unknown SDDL mnemonic rights and odd-length rights strings count as full control (`confinement.ts:169-182,216-245`).
- Administrator identity: closed. `LA` must resolve to the current SID; elevated Administrators ownership does not waive the DACL (`confinement.ts:216-245,335-345,433-440`).
- Windows: `dd2978255` skips only the quote-in-name alternates test, not the suite (`safeGitConfig.test.ts:458-486`).
