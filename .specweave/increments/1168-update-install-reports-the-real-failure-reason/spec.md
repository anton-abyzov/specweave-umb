# Update install reports the real failure reason

## Problem

A failed desktop install says nothing useful. On Ministorm the .deb app has stayed on 1.0.76 since October 24, 2026: every Restart runs `dpkg -i` on an AppImage, dpkg refuses it, electron-updater runs `apt-get install -f`, which succeeds, and the app relaunches on the old version with no error. The one logged error, "Desktop updater install operation reported an error.", drops the cause.

The AppImage comes from the token path. With `gh` signed in, the feed is `private: true`, whose asset URLs end in an ID, so DebUpdater's `findFile` cannot see `.deb` and takes the first file not excluded by name.

## Scope

In: the failure reason in the sidebar and logs, a review at the next launch of whether the attempted version runs, and looking in the Linux journal for the installer's error. A release, and M4 and Ministorm on it.

Out: the .deb feed fix, which the Linux chat session worker owns in #1188. Showing a desktop app failure from another machine in this machine's fleet row. Service failures already reach that row through `ServerUpdateProgress`. Raw check and download errors stay generic, because HTTP errors may carry request details.

## Acceptance Criteria

- [ ] AC-01: The release carries #1188, so a .deb install downloads the .deb.
- [ ] AC-02: A failed install's state and log carry the updater's first line, with tokens removed.
- [ ] AC-03: A relaunch that still runs the old version records why, from the Linux journal when it has the installer's error, and says plainly when the machine left none.
- [ ] AC-04: The sidebar keeps saying why across later checks, until that version is reached.
- [ ] AC-05: M4 and Ministorm run the released version, with the Ministorm app on the .deb of that release.

## Approach

`apps/desktop/src/updates/installAttempt.ts` holds the records and the diagnosis. `DesktopUpdates.ts` writes the attempt before the quit and reviews it when the pollers start. The 1.0.76 app cannot fix itself because its updater has the bug, so Ministorm needs one `dpkg -i` of the new .deb.

## Tasks

### T-01 Reason in the install failure and the relaunch review

- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/installAttempt.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/DesktopUpdates.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/desktopUpdateState.ts | Test: `installAttempt.test.ts`, `DesktopUpdates.test.ts`

### T-02 Carry the .deb feed fix from #1188

- AC: AC-01 | Files: none | Test: `git log` of the release contains #1188

### T-03 Release and verify on M4 and Ministorm

- AC: AC-05 | Files: none | Test: installed versions read on each machine

### T-04 Verify and close 1168

- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: `specweave verify`
