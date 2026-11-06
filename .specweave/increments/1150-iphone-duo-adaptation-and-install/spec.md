# iPhone Duo adaptation and install

## Problem

Anton's iPhone Duo is now connected by cable. Increment 1079 made the drawer a persistent column on regular-width windows and proved it only in the M1 Duo simulator; hardware acceptance stayed open. Unfolded, the app still reads as a stretched phone: a custom drawer beside chat, not the sidebar plus detail layout people expect on iPad. The phone has never had the Duo build installed, and the M1 and M4 desktop apps may lag the latest release (the M4 shows a pending 1.0.136 to 1.0.140 update).

## Scope

In: the unfolded (regular width) layout as a native sidebar plus detail split view, folded (compact) layout unchanged, polish of the sidebar and detail chrome on the inner display, tests, M1 Duo simulator screenshots folded and unfolded, a Release development install on the physical iPhone Duo with screenshots and a version readback, one merged PR, and the latest SpecWithCode desktop app on the M1 and M4. Out: App Store or TestFlight submission, hinge pose automation, Instruments performance work, server or web changes.

## Acceptance Criteria

- [ ] AC-01: With regular horizontal size class and enough width, the app shows a native sidebar (projects, threads, Aide) beside the selected chat in a split view; selecting a sidebar row changes the detail without a modal drawer.
- [ ] AC-02: With compact width (folded outer display, narrow split), the existing phone layout and modal drawer are unchanged.
- [ ] AC-03: Folding and unfolding preserves the selected thread, the unsent draft and scroll position; no content is hidden from accessibility after a size change.
- [ ] AC-04: Unit and UI tests cover both layouts and the size-change transition; `swift test` in apps/ios/SWCKit and the adaptive UI tests pass on the M1 Duo simulator.
- [ ] AC-05: Folded and unfolded screenshots exist from the M1 Duo simulator and from the physical iPhone Duo.
- [ ] AC-06: The merged build is installed and launched on the physical iPhone Duo, with a readback of app version and build, iOS version and time.
- [ ] AC-07: The M1 and M4 run the latest released SpecWithCode desktop app.

## Approach

Work on the M1 (Xcode 27.1, iOS 27.1 Duo runtime) in a fresh worktree of anton-abyzov/specwithcode-dev off origin/main. Replace the regular-width branch of `DrawerContainer` with a `NavigationSplitView` (sidebar plus detail, balanced style) that reuses the drawer's content as the sidebar, keeping one detail subtree mounted so draft and scroll survive size changes. The compact branch keeps today's drawer. Decide the mode from size class plus available width, never device identity. Tests extend `AdaptiveDrawerTests` and `AdaptiveLayoutUITests`. Simulator evidence through `Tools/duo-readiness.sh` and `make sim-*`; device install through `Tools/device.sh`, readback with `ideviceinstaller` and `devicectl`. Merge with `gh pr merge --squash --admin`. Desktop app updates through the in-app updater or the release DMG on each Mac, outside the Duo work.

Risk: a split view changes navigation ownership (Router). Keep the Router the single source of selection so both layouts share it.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Unfolded layout → NavigationSplitView sidebar plus detail (user asked for an iPad-like experience).
- D-02 Physical install → Release development build via `Tools/device.sh`, no TestFlight (user approved the cable install).
### Open
- none

## Tasks

### T-01 Native split view on the unfolded display
- AC: AC-01, AC-02, AC-03 | Files: apps/ios/SWCKit/Sources/Weave/Components/DrawerContainer.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift | Test: cd apps/ios/SWCKit && swift test

### T-02 Tests for both layouts and the transition
- AC: AC-03, AC-04 | Files: apps/ios/App/Tests/AdaptiveDrawerTests.swift, apps/ios/UITests/AdaptiveLayoutUITests.swift | Test: cd apps/ios && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer bash Tools/duo-readiness.sh test

### T-03 Simulator and device screenshots, device install and readback
- AC: AC-05, AC-06 | Files: .specweave/increments/1150-iphone-duo-adaptation-and-install/evidence | Test: ideviceinstaller -l | grep com.specwithcode.ios

### T-04 Latest desktop app on the M1 and M4
- AC: AC-07 | Files: .specweave/increments/1150-iphone-duo-adaptation-and-install/evidence | Test: defaults read /Applications/SpecWithCode.app/Contents/Info.plist CFBundleShortVersionString

### T-05 Verify and close 1150
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1150-iphone-duo-adaptation-and-install | Test: specweave verify 1150
