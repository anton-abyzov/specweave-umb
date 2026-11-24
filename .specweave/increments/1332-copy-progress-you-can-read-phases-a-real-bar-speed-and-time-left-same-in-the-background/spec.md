# Copy progress you can read: phases, a real bar, speed and time left, same in the background

## Problem

Anton copied specweave (121,868 files, 7.5 GB) from m4 to m5 on November 14, 2026. Each working step of the copy dialog showed only one line of text: "Measuring… 94,543 files, 5.9 GB", then "Comparing with m5… Reading the selected files on m4… 469 of 121,868 files, 21.1 MB of 7.5 GB". It had no bar, no percent, no speed and no time left. Until Apply nothing said how far the copy was or whether it was stuck. While measuring, the dialog kept the editable setup on screen: the machine list, the "Not connected to this app yet" row and the "Not listed: PRCTY-AABYZOV" notice. The project banner and sidebar row showed only a thin bar and a label. The dialog had no way to send the copy to the background besides the corner X. In m5's window, the thread panel said "m4 is offline" for up to 10 minutes after m4 restarted for an update, because nothing cut the reconnect delay short.

## Scope

In:
- One progress model for every place that shows a copy: dialog, banner, sidebar and toast.
- Three phases named by the machine doing the work: Measure on the source, Send to the destination, Apply on the destination.
- A determinate bar with percent, bytes and files; speed and time left measured in the window; finished and failed states.
- The setup is hidden once a copy runs.
- A "Run in background" action with a progress toast that reuses the update toast's bar.
- "Try again" and an automatic retry on the "X is offline" notice.

- A faster Comparing step (added November 14, 2026): the source captures 12 files at once and checks folders above the copy root by identity only.
- Fewer pull requests: batches of up to 1,024 chunks, 8 at a time, offered by the source's hello. zstd when both sides support it.

Out:
- A direct LAN path between the machines. It is planned separately, with a security review.
- A hash cache for unchanged files on repeat copies.
- Per-file names on the wire.

## Acceptance Criteria

- [ ] AC-01: While a copy measures, reads, compares, sends, checks or applies, the dialog shows its step, a three-phase track (Measure on {source}, Send to {target}, Apply on {target}), percent when a total is known, bytes and files, and speed and time left once a pace is known.
- [ ] AC-02: Once a copy runs, the editable setup (machine list, account rows, folder, options) is replaced by the choices summary.
- [ ] AC-03: With the dialog closed, the banner, the sidebar row and a progress toast show the same phase, counts and speed. The sidebar line covers the whole copy and never runs back to empty.
- [ ] AC-04: "Run in background" appears while a copy measures, compares or copies, and closes the dialog. The copy keeps running and its toast opens Details.
- [ ] AC-05: Done shows the finished track with "Sent X in N files" and the duration. A stopped copy shows the phase it stopped in.
- [ ] AC-06: A thread list that says "{machine} is offline" retries the connection at once, on "Try again", and every 30 s while it shows.
- [ ] AC-07: Comparing never waits on folders above the copy root changing. Up to 12 files are read and hashed at once, and every captured file's bytes and hashes match the source.
- [ ] AC-08: A newer source and destination pull in batches of up to 1,024 chunks, 8 at a time, with zstd when both support it. An older machine on either side still gets 32-chunk gzip batches.
- [ ] AC-09: Closing the dialog while a copy waits at its review keeps the copy followed: the sidebar row, the project banner, Needs you and a toast each offer Review, which reopens the dialog on the same copy. A cancelled copy is not followed.

## Approach

- `apps/web/src/studio/copyProgress.ts` builds the model from the source and destination statuses. The rate is measured inside one step from 1 s readings over a 12 s window. It is null before 3 s or while nothing moves, and bytes already on the destination are left out.
- `CopyProgressPanel.tsx` holds `CopyPhaseTrack` and `useCopyRate`, shared by the dialog, the banner and Done/Failed.
- `CopyActivity` carries the view (`progress`, `source`). `folderCopyToasts.ts` syncs one toast per background copy through the existing `toastManager` `data.progress` bar.
- The offline notice goes through `connection/retryRequests.ts`, a bus the platform wakeups stream turns into a throttled `retry-hint`.
- Capture: a buffered read (files up to 8 MiB) appends to the pack through one serialized lane; a larger file streams into the pack while holding the lane. Folders inside the copy root keep the change and modification time check; folders above it are checked by device and inode only.
- Wire: the source's hello carries `maxBatchChunks`; the destination stores it as `sourceBatchChunks` when the copy starts. The client asks for zstd with `encodings`; the decoder tells zstd from gzip by magic bytes, so no header has to survive the relay.
- Rejected:
  - A weighted overall percent in the dialog: the phases take very different times. The dialog shows the percent of the current step; the sidebar and toast use equal thirds.
  - Making the copy fully server-driven: the plan and approval steps are client-driven today.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The toast appears for every copy watched in the background, not only after "Run in background". Closing it hides it for that copy.
- D-02: Measure-phase speed is the reading speed on the source. It restarts when the step changes.
### Open
- none

## Tasks

### T-01 Progress model, panel and dialog wiring
- AC: AC-01, AC-02, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/copyProgress.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyProgressPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyStepPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/handoffCopySteps.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyDone.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/copyProgress src/components/studio/HandoffFolderCopy

### T-02 Background view: banner, sidebar, toast and Run in background
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/folderCopyActivity.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/FolderCopyBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/folderCopyToasts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/FolderCopyWatchers.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyFooter.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/FolderCopyBanner src/components/studio/folderCopyToasts src/components/studio/HandoffCopyFooter src/components/studio/HandoffFolderCopyWatcher

### T-03 Offline notice retries
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/connection/retryRequests.ts, repositories/anton-abyzov/specwithcode/apps/web/src/connection/platform.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectExecutionHistory.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/ProjectExecutionHistory

### T-05 Parallel capture, identity-only checks above the copy root
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSnapshot.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSnapshot.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/sourceSnapshot

### T-06 Larger pull batches and zstd, negotiated
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/wire.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceRoutes.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceClient.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/pullWorker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/destinationService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/wire.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/twoServer.verify.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer

### T-07 Review stays reachable after closing the dialog
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/ProjectMachineHandoff

### T-08 Review fixes on the current flow (after 1390)
- AC: AC-01, AC-03, AC-04, AC-05, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/copyProgress.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyFooter.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/folderCopyToasts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/SidebarProjectList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopyWatcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useCopyDraft.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/destinationService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/pullWorker.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/studio/copyProgress src/components/studio
- Owner chose a fix over a superseded close (November 24, 2026). Sol findings at `f3ce25682`, listed in Closure triage below: recompare after Clone/Skip shows no track or Run in background, Verify and Apply carry no progress; background view drops counts and speed; Add reopens fresh instead of the running copy (#653); Measure failure loses the stopped phase; 4 not 8 full batches at once; closing a foreground Review shows no toast. Where 1390's Sync dialog replaced a path for good, say so in the AC instead of rebuilding it.

### T-04 Verify and close 1332
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/1332-copy-progress-you-can-read-phases-a-real-bar-speed-and-time-left-same-in-the-background/reports/ | Test: specweave verify 1332

## Closure triage (November 24, 2026)

Shipped in PRs #382 (`9e5140399`, v1.0.301), #385 (`4e972a644`, v1.0.300), #427 (`76ff89e53`, v1.0.314). Closing review by GPT-6.2 Sol (Codex) at main `f3ce25682`: **fix**, so not verified or closed. AC-02, AC-06, AC-07 hold; AC-01, AC-03, AC-04, AC-05, AC-08 (partly) and AC-09 do not.
- AC-01/AC-04: a Clone or Skip change on Review recompares with no track and no Run in background; Verify gets no progress and Apply clears it. `HandoffFolderCopy.tsx:854`; `destinationService.ts:1321`, `:1353`
- AC-03: the background view drops counts and speed during Compare; sidebar and toast never show the speed. `copyProgress.ts:159`, `:269`; `folderCopyToasts.ts:61`
- AC-04/AC-09: machine-menu Add passes `fresh`, so reopening skips the running copy; from `0262c7bb2cc` (#653, increment 1390), which also moved Sync to `ProjectSyncDialog` with spinner-only progress.
- AC-05: a Measure failure on the source returns to setup without the stopped phase. `HandoffFolderCopy.tsx:432`, `:453`
- AC-08: the 256 MiB budget allows 4 full batches at once, not 8. `pullWorker.ts:49`, `:64`
- AC-09: closing a foreground Review shows no toast; `HandoffFolderCopyWatcher.test.tsx:1190` expects none.
Part of the gap comes from 1390 replacing the flow; needs a fix increment or a superseded close; owner's call.
