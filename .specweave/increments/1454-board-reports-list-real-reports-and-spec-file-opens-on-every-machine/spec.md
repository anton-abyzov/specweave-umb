# Board increment panel: Reports lists the real reports and Spec file opens on every machine

## Problem

The Board's increment panel has two buttons that fail the owner (November 23, 2026, increment 1451 on M5).

**Reports opens a task log.** Clicking Reports on 1451 opened `task-T-01.txt`, "1 of 2": a two-line command log (`test -s .../reports/parity.md`, `# exit 0`). The 20 KB `parity.md` research report was the second file, one arrow away, with nothing saying so. Two causes in the code:

- The server lists only the top level of `reports/`, newest file first (`apps/server/src/project/ProjectBoardIncrement.ts`, `newestFiles`). `specweave task done --run` writes `task-T-NN.txt` after the report it checks, so the evidence log is always newest and opens first. Across increments 1400 to 1453 there are 11 such logs beside the real reports.
- Subfolders are never listed: `reports/reviews/` (13 GPT-6.2 Sol and Gemini reviews in recent increments) and `reports/screens/` (screenshots) never reach the panel.
- The viewer the Board uses (`LibraryFileViewer.tsx`) shows images and HTML mockups as a "has no preview here" card or as raw source, so `mockup.png` and `mockup.html` reports are unreadable even when they are listed.

**Spec file fails on some machines.** Since 1.0.382 (increment 1421) the Board shows each increment's newest copy: the project folder, a thread worktree, or the remote default branch. A remote copy is written to `<state>/board-copies/<hash>/<commit>/` (`IncrementCopies.ts`, `ThreadIncrementProgressService.ts:307`, state folder `~/.specwithcode/userdata`), and the card's `specPath` points there. The file reader refuses everything under the state folder except a short list of readable subfolders (`WorkspaceSensitivePaths.ts`, `READABLE_STATE_SUBDIRECTORIES`), so `projects.readFile` refuses it. M5's own server trace (1.0.409) holds 10 such refusals, all for `board-copies/.../1342-office-artifacts-.../spec.md`: "Workspace file '...' is a protected credential or app state file and cannot be read here." The same refusal hits the reports and images of that copy, through both the file reader and the asset reader.

It depends on the machine because it depends on that machine's project folder: where the folder holds the newest copy (M5 for 1451, whose commits are local and unpushed), Spec file opens; where the folder lags `origin/main` (another Mac, or M5 after someone else's merge), the Board shows the remote copy and Spec file fails.

## Scope

In:
- Remote board copies readable (read only) by the file and asset readers.
- Reports listed from `reports/` and its subfolders, sorted into groups, real reports first.
- A Reports list in the increment panel; the button opens the best real report, never a task log while a real report exists.
- The Board and Library viewer show images as images and HTML reports rendered in a sandbox.
- When Spec file or a report still cannot be read, the viewer says why and where the file lives, never "protected".

Out:
- Writing to board copies, or changing which copy the Board picks (1421's rules stand).
- Relative image links inside a Markdown report (they resolve against the project folder today; separate fix).
- 1451's own files and threads.

## Acceptance Criteria

- [ ] AC-01: A file under `<state>/board-copies/` reads through `projects.readFile` and serves through the asset reader; writes there are still refused, and every other state folder stays refused as before.
- [ ] AC-02: For an increment whose Board copy is the remote branch copy, Spec file opens the spec text in the viewer (headless check on a scratch project whose folder lags its remote).
- [ ] AC-03: The panel's reports come from `reports/` and its subfolders (one level, for example `reviews/`, `screens/`), up to the existing limit of 30, real reports before evidence so evidence never crowds them out. Each file falls in one group by its path alone (shared code, so a new client groups an older server's list the same way): `report` (Markdown, HTML, PDF, Office files), `review` (anything in `reviews/` or named `review*`), `image`, `evidence` (`task-*.txt`, `*.log`, `verify.json`, `verify.md`, scripts and data files). Order: report, review, image, then evidence; newest first inside a group. The wire shape (`path`, `name`) does not change.
- [ ] AC-04: The panel shows a Reports section listing the files by group with their names; evidence is folded under "Task evidence (N)". Clicking a name opens it in the viewer, stepping through that file's group and the other non-evidence groups. The Reports button opens the newest real report (report, else review, else image) and, when only evidence exists, the newest evidence file.
- [ ] AC-05: In the Board and Library viewer an image shows as an image and an `.html` file renders in a sandboxed frame with scripts off, with a "Source" switch to see its text.
- [ ] AC-06: When the spec or a report cannot be read, the viewer says so in a sentence and names where the Board found it (project folder, worktree name, or the remote branch with its fetch age), never the raw error: a missing file says "This file is no longer at <path>."; a refusal (an older server on another machine) says the copy could not be opened on that machine and where the spec lives.

## Approach

1. **Server, sensitive paths** (`apps/server/src/workspace/WorkspaceSensitivePaths.ts`): add `board-copies` to the readable state subfolders. It holds only files copied from the project's own remote branch, by the server, under a hash folder; the same bytes are readable in any checkout. Writes stay refused (the readable list applies to reads only). Tests in `WorkspaceSensitivePaths.test.ts` and a `WorkspaceFileSystem.test.ts` read case.
2. **Shared classifier** (`packages/shared/src/boardReports.ts`): `boardReportGroup(path)` and `orderBoardReports(list)` by path alone. **Server, reports** (`apps/server/src/project/ProjectBoardIncrement.ts`): list one level of subfolders, order with the shared code before the limit; keep the project folder's extra reports after the copy's own; signature covers each listed subfolder. No contract change. Tests in `boardReports.test.ts` and `ProjectBoardIncrement.test.ts`.
3. **Web, panel** (`apps/web/src/components/studio/shell/BoardIncrementView.tsx` and a new `BoardIncrementReports.tsx`): a Reports section with grouped names, evidence folded; the button opens the best real report with the non-evidence file set.
4. **Web, viewer** (`apps/web/src/components/studio/shell/LibraryFileViewer.tsx`): reuse what the thread file viewer already has. Images through `ViewerImageStage`, HTML through `BrowserDocumentFrame` (the server's locked frame, scripts confined) with `HtmlSourceSwitch`, both from an asset URL for a `draft-workspace-file` resource on the absolute path (no thread needed). A read failure of kind missing or protected shows AC-06's sentence with the source line passed in from the Board.
5. Headless check with the project-board verifier (`apps/web/tests/project-board/verify.mjs`) or a scratch fixture: before and after screenshots of Reports and Spec file on a remote copy.

Rejected: a new `projects.boardFile` RPC that reads through the board's guarded resolver. It would fix Spec file but leave images (asset reader) and the viewer's Open in editor and Reveal actions refused, and add an RPC every client must learn. Rejected: copying remote increments into the project folder; the Board must never write a checkout (1421).

Risk: the readable list is a security boundary. `board-copies` content comes from Git objects of the project's own remote, never from a provider or user secret; the folder name is fixed by the server. Review checks that no other state folder becomes readable and that a symlink planted there cannot reach a protected file (the realpath identity check still runs after the folder test).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Fix Spec file by making `board-copies` readable rather than adding a new RPC → readable subfolder (smaller, fixes images and file actions too).
- D-02: Evidence logs stay listed but folded, not hidden → folded under "Task evidence (N)" (they are proof a task's check ran).
- D-03: HTML reports render in the existing locked file frame (`BrowserDocumentFrame lockedFile`), the same as a thread's linked HTML file; View source switches to the text.
- D-04: Groups are computed from the path on both sides, no `group` field on the wire → a new client works with an older server and an older client sees nothing new.
### Open
- none

## Tasks

### T-01 Remote board copies readable
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceSensitivePaths.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceSensitivePaths.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceFileSystem.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/workspace/WorkspaceSensitivePaths.test.ts apps/server/src/workspace/WorkspaceFileSystem.test.ts

### T-02 Reports from subfolders, grouped and ordered
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoardIncrement.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoardIncrement.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/boardReports.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/boardReports.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/boardReports.test.ts apps/server/src/project/ProjectBoardIncrement.test.ts

### T-03 Reports section and button in the panel
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardIncrementView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardIncrementReports.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardIncrementView.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/BoardIncrementView.test.tsx

### T-04 Viewer shows images, HTML and a clear unreadable message
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/LibraryFileViewer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/LibraryFileViewer.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/LibraryFileViewer.test.tsx

### T-05 Headless proof on a remote copy, review, merge, release
- AC: AC-02 | Files: .specweave/increments/1454-board-reports-list-real-reports-and-spec-file-opens-on-every-machine/reports/ | Test: headless screenshots of Reports and Spec file before and after, saved under reports/screens/
