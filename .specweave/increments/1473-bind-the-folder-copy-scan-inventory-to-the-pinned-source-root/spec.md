# Bind the folder-copy scan inventory to the pinned source root

## Problem

The folder-copy scan (`scanFolder` in `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.ts`) walks the source by path and runs Git by path. Capture (1469) pins the root by inode and proves every file it reads sits below it. But the inventory itself is not bound to that pin. A folder above the root can be swapped for another tree while the scan walks, then put back before capture. The root's dev, inode and change time all survive that (checked on APFS, November 24, 2026). The manifest can then carry facts from the other tree that capture cannot re-derive: a file's tracked Git class (tracked files skip the secret probe), mode bits, empty directories, and which paths exist (Mirror moves a destination file the scan missed to backup). The GPT-6.2 Sol reviews of 1469 raised this as round 2 finding 2, round 5 and round 6 findings 1 and 2 (`.specweave/increments/1469-fix-folder-copy-approval-binding-and-snapshot-review-defects/reports/reviews/`). 1469 closes the byte-level part: files are read through the pin and checked, probed files are re-checked, and links and their parent folders are looked up from the pin.

## Scope

In: walk the source and classify Git state through the pinned root on macOS and Linux; capture reuses the scan's pin instead of pinning again. Out: Windows (no inode lookup, as in 1469 D-03); the legacy live-file `hashSelected` path.

## Acceptance Criteria

- [ ] AC-01: On macOS and Linux the scan pins the root once at its start (`/.vol/<dev>/<ino>`, an `O_DIRECTORY` descriptor under `/proc/self/fd`), and every directory read, lstat and readlink of the walk goes through that pin. A folder above the root swapped during the walk cannot add, remove or change an inventoried entry.
- [ ] AC-02: Git classification (tracked, ignored, untracked) for files below the root is computed from the pinned tree. A regression test swaps a repository above the root between the walk and classification and shows the class comes from the pinned tree.
- [ ] AC-03: Capture uses the scan's pin (the same descriptor or `/.vol` base) and refuses when it is gone. No second pin is taken between the scan and capture.
- [ ] AC-04: Mode bits recorded for captured files come from the capture's opened descriptor, not the scan.

## Approach

Thread a `RootAnchor` from `scanFolder` into `captureSourceFiles` (`sourceCaptureAnchor.ts` already provides pinning). Walk with anchored paths. Run Git with `-C <anchored path>` or compare `git ls-files` results against anchored lstat identities. Main risk: worktree registrations and `.git` files hold absolute paths, so anchored paths must not leak into reported paths. Rejected: comparing the root's change time between scan and capture. A swap above the root leaves it unchanged, and a name added in the root refuses honest copies.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Windows keeps the path walk → reported limit, as 1469 D-03.
### Open
- none

## Tasks

### T-01 Walk the scan through the pinned root
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSnapshot.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.anchored.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/manifest.anchored.test.ts

### T-02 Classify Git state from the pinned tree
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/git.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.anchored.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/manifest.anchored.test.ts

### T-03 Take captured mode bits from the opened file
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSnapshot.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSnapshot.review.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/sourceSnapshot.review.test.ts
