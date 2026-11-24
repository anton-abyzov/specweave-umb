# Linux chats fail with native subscription authorization unverified

## Problem

On Ministorm (Linux), every chat in the desktop app fails, including a new one, with: "Native subscription authorization is unverified. Sign in with the official native CLI on this machine and refresh provider status." The Claude CLI is signed in: `claude auth status` reports `loggedIn: true` and `authMethod: claude.ai`.

The running app is the `.deb` at `/opt/SpecWithCode`, version 1.0.76 from October 24, 2026. It only accepts plan names on an old allow-list, and Claude now reports "Claude Ultra". PR #1104 fixed that on October 31, so 1.0.142 and later accept it.

The `.deb` cannot reach that fix. With a `gh` sign-in on the machine, the updater uses electron-updater's private GitHub provider, whose file URLs are `/releases/assets/<id>` with no extension. `DebUpdater` then finds no `.deb` and falls through to the AppImage, and `dpkg -i` refuses it: "is not a Debian format archive". The journal for November 2, 2026 at 01:41 shows this, and the app shows "Retry update" forever. `origin/main` has the same defect.

## Scope

In: `.deb` installs download the `.deb` whether or not a GitHub sign-in exists; release; bring Ministorm's `.deb` to a fixed version once by hand, since 1.0.76 cannot update itself; live check of a new chat on Ministorm.

Out: the Claude plan check (fixed by #1104); AppImage and other platforms' feeds; the polkit prompt a `.deb` update shows; fleet rollout of the `.deb`.

## Acceptance Criteria

- [x] AC-01: With a GitHub token present, a `.deb` install's update feed carries no token and uses public release URLs, so `DebUpdater` selects the `.deb`.
- [x] AC-02: Feeds for AppImage and other installs are unchanged, including the sign-in for a private repository.
- [x] AC-03: A release containing the fix is published, with its Linux `.deb` attached.
- [x] AC-04: On Ministorm the installed `.deb` is the fixed version or newer, and a new chat on that machine opens and replies.

## Approach

`apps/desktop/src/updates/platformFeed.ts`: `resolveUpdateFeed` takes `isDebPackage` and ignores the token when it is true. `apps/desktop/src/updates/DesktopUpdates.ts` passes the value it already computes.

A private repository with a `.deb` could not update before this change either; it now fails at the check rather than by installing the wrong file. Rejected: patching electron-updater, because the provider's URL shape is correct for its own use and a patch would need carrying through every upgrade.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 "Provide a session for it to open" → create a fresh test chat on Ministorm once fixed and give its link (reversible).
- D-02 Ministorm's one-time `.deb` upgrade → `sudo dpkg -i` of the published, checksum-verified file; the running app is not stopped, because only processes this work started may be stopped (reversible).
### Open
- none

## Tasks

### T-01 Keep the GitHub sign-in out of the .deb update feed
- AC: AC-01, AC-02 | Files: apps/desktop/src/updates/platformFeed.ts, apps/desktop/src/updates/platformFeed.test.ts, apps/desktop/src/updates/DesktopUpdates.ts | Test: cd apps/desktop && pnpm exec vp test run src/updates/platformFeed.test.ts

### T-02 Review, merge and release
- AC: AC-03 | Files: none | Test: gh release view vX.Y.Z -R anton-abyzov/specwithcode --json assets

### T-03 Upgrade Ministorm and check a new chat live
- AC: AC-04 | Files: none | Test: on Ministorm, dpkg-query -W studio, then a new thread replies

### T-04 Verify and close 1166
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1166
