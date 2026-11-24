# Duo coordinator beside thread

## Problem

On an unfolded iPhone Duo the left column of the iOS app only ever holds the project list (`NavigationColumn` in `apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift`). To read or answer the coordinator while a thread is open, the person has to leave the thread. Anthropic's Claude mobile update video (October 29, 2026, `SkpwzfR4A1E`) shows the Duo running two chats side by side, split at the hinge. Anton wants that for coordinator and thread.

## Scope

In: the iOS app at 760 points or wider. The column shows the open thread's coordinator with an adjustable width, the thread stays on the right, the project list is one tap away, and a setting turns it off.

Out: the upright unfolded Duo at 669 points and the folded phone, which keep the modal drawer. Arbitrary pairs of chats. The Expo app.

## Acceptance Criteria

- [ ] AC-01: With a project thread open in the wide layout, the column shows that thread's project coordinator and the thread stays on the right.
- [ ] AC-02: Dragging the divider resizes the coordinator column, the width is remembered apart from the project list's width, and the default is half the scene, on the Duo's hinge.
- [ ] AC-03: With no thread open (Aide, a coordinator, machines), the column shows the project list as before.
- [ ] AC-04: "Show projects" in the coordinator column shows the list, picking a row returns to the coordinator, and "Show coordinator" returns without picking.
- [ ] AC-05: A Settings switch "Coordinator beside threads" turns the behavior off and is remembered.
- [ ] AC-06: A thread opened from a coordinator link in the column opens on the right, and each pane keeps its own draft.
- [ ] AC-07: Below 760 points nothing changes.

## Approach

`AppRouter` derives the column's coordinator from `sidebarSelection`, so the router stays the single source of selection. `NavigationColumn` hosts `ChatView` in its own stack, and the shared `StackNavigator` in the environment sends pushes from that chat to the main stack on the right. `DrawerContainer` takes `isChatColumn` for wider bounds and a second remembered width. Viewer counting in `AppModel.openSession` already allows one chat on screen twice.

Rejected: `NavigationSplitView`, for the overlay behavior recorded in `apps/ios/docs/IPHONE-DUO.md`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 On by default, because Anton asked for it and the Settings switch reverts it.
- D-02 Keep the 760-point breakpoint, so the upright Duo at 669 points keeps the drawer.
- D-03 Aide threads show Aide in the column.
### Open
- none

## Tasks

### T-01 Router state and setting
- AC: AC-01, AC-03, AC-04, AC-05 | Files: [apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, apps/ios/SWCKit/Sources/SWCFeatures/Settings/GlobalSettingsSheet.swift, apps/ios/SWCKit/Tests/SWCFeaturesTests/SidebarSelectionTests.swift] | Test: cd apps/ios/SWCKit && swift test --filter SidebarSelectionTests

### T-02 Column layout
- AC: AC-01, AC-02, AC-04, AC-06, AC-07 | Files: [apps/ios/SWCKit/Sources/Weave/Components/DrawerContainer.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift, apps/ios/App/Tests/AdaptiveSplitTests.swift] | Test: bash apps/ios/Tools/duo-readiness.sh test

### T-03 Install on the Duo
- AC: AC-01, AC-02 | Files: [apps/ios/docs/IPHONE-DUO.md] | Test: DEVICE=<duo> STUDIO_APPLE_TEAM_ID=<team> apps/ios/Tools/device.sh
