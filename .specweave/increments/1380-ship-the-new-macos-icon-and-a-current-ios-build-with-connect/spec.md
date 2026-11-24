# Ship the new macOS icon and a current iOS build with Connect

## Problem

Anton's Mac Dock shows the old SpecWithCode icon (a document with `>_`) on 1.0.337, while Windows and Linux show the new `>=` mark (PR #464, November 15, 2026). Evidence from the installed `/Applications/SpecWithCode.app` on the M4 (macOS 27.2):

- `Contents/Resources/icon.icns` already holds the new mark, so the artwork reaches the bundle.
- The bundle has no `Assets.car` and no `CFBundleIconName`; only `CFBundleIconFile = icon.icns`. macOS 26 and later treat such an app as legacy: `NSWorkspace.icon(forFile:)` returns the new mark shrunk inside a grey squircle, and the Dock keeps serving its cached copy of the old icon across the in-place update.
- `scripts/build-desktop-artifact.ts` passes `mac.icon: "icon.icns"` built from `black-macos-1024.png`, although `assets/prod/app-icon.icon` (Icon Composer) exists and electron-builder 26.15.6 compiles `.icon` into `Assets.car` with `CFBundleIconName`.

The iPhone app is stuck at 0.1.7 (build 45, uploaded November 11, 2026, live on the App Store). Since then 247 commits touched `apps/ios` or shared contracts, including the new icon, advisor-field decoding (1371), Percy, dictation and the add-device dialog. Desktop is at 1.0.338.

## Scope

In: macOS bundle ships the Icon Composer icon (`Assets.car` + `CFBundleIconName`) for latest and nightly channels; a desktop release requested through `request-release.sh`; an iOS build from current `main` to TestFlight and App Store review. Out: device approval (1327, PRs #361/#362 unmerged, not shipped anywhere); Windows and Linux icons (already correct).

## Acceptance Criteria

- [x] AC-01: A packaged macOS build has `Contents/Resources/Assets.car`, `CFBundleIconName = Icon`, and an `icon.icns` rendered from the channel's `app-icon.icon`.
- [x] AC-02: The released desktop version installed on the M4 shows the new full-bleed icon in Finder/LaunchServices and the Dock (screenshot), or the report names the exact one-time Dock refresh step.
- [x] AC-04: After an update that changes the icon, the macOS app re-registers its bundle and offers once to reload the Dock (clearing the user Dock icon cache); M5's Dock shows the new icon (screenshot).
- [x] AC-03: An iOS build from current `main` (version above 0.1.7, build above 45) is processed in TestFlight, in the Internal group, and submitted for App Store review; report names version, build and state.

## Approach

1. `scripts/build-desktop-artifact.ts`: add the channel's `app-icon.icon` folder to `DesktopBuildIconAssets`, copy it into the staged resources as `icon.icon`, set `mac.icon: "icon.icon"`. electron-builder then writes `Assets.car`, `CFBundleIconName` and an actool-rendered `icon.icns` for older macOS. Keep the PNG for `icon.png`. Release runners already select Xcode 26+ (actool 26 is required).
2. Unit test in `scripts/build-desktop-artifact.test.ts`; local unsigned `--target dir` build to inspect the bundle.
3. PR, CI, merge, `request-release.sh`; verify the installed app.
4. iOS: bump to 0.1.8 build 46 in `apps/ios/project.yml`, `make testflight`, stage and submit with asc (release guard needs `ASC_LAUNCH_VERIFIED`).

Rejected: clearing only the Dock cache (the legacy icns still renders in the grey squircle on macOS 26+).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: iOS version 0.1.8 build 46, submitted for review with manual release off (auto-release after approval), matching previous versions.
### Open
- none

## Tasks

### T-01 macOS bundle ships the Icon Composer icon
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/scripts/build-desktop-artifact.ts, repositories/anton-abyzov/specwithcode/scripts/build-desktop-artifact.test.ts | Test: pnpm vitest run scripts/build-desktop-artifact.test.ts, plus PlistBuddy on a local packaged build

### T-02 Release desktop and verify the Dock icon on the M4
- AC: AC-02 | Files: none | Test: PlistBuddy CFBundleIconName on /Applications/SpecWithCode.app, Dock screenshot

### T-03 Ship iOS 0.1.8 to TestFlight and App Store review
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/ios/project.yml | Test: asc builds list --app 6824245458; asc versions list --app 6824245458

### T-04 Refresh the Dock icon cache after an update (M5 report)
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/updates/macIconRefresh.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/updates/macIconRefresh.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopApp.ts | Test: vp test run apps/desktop/src/updates/macIconRefresh.test.ts; M5 Dock screenshot
