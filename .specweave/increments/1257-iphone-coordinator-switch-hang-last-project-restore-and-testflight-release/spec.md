# iPhone coordinator switch hang, last-project restore and TestFlight release

## Problem

Anton reported three problems with the native iPhone app (`apps/ios`, App Store 0.1.4 build 30, TestFlight build 31) on November 7, 2026:

1. On a project's coordinator screen the header switcher shows the machine the coordinator runs on (for example Ministorm). Picking another machine in that switcher leaves the app stuck. This is a regression.
2. Every cold start opens the Aide (personal assistant), not the last project or thread used. `AppRouter.root` is memory only (`SWCFeatures/Navigation/Router.swift:58`), and nothing persists it.
3. Recent server changes reached the desktop and web but not the phone: routed-message headers ("Regarding thread <id> on machine <env> (<title>):", "Routed from personal assistant ...") show raw text (`SWCSync/TranscriptMapper.swift:54`), and `secret_request` turn items decode as unknown and are dropped, so a thread waiting on a secret looks stalled.

A fixture-mode switch did not hang (about 2.6 s per switch), so the hang depends on live data. A live reproduction against the fleet decides the root cause.

## Scope

In: the coordinator-switch fix with a regression test; restoring the last-used project and thread on cold start; routed-message display; a `secret_request` notice row; an in-repo TestFlight release script; publishing 0.1.5 to TestFlight and staging it for the App Store.

Out: entering secrets on the phone, which needs its own design for how the value travels. Generated wire fixtures from `packages/contracts`. The Expo app `apps/mobile`, which is not the shipping iPhone app.

## Acceptance Criteria

- [ ] AC-01: Picking another machine in the orchestrator switcher shows that machine's coordinator chat, and the app stays responsive: the drawer opens within 5 s of the switch, in portrait and landscape. A regression test covers the root cause.
- [ ] AC-02: After a cold start the app opens the last project chat, and the last thread pushed on it, once their machine's data has loaded. It does not flash the Aide while that data loads.
- [ ] AC-03: The app opens the Aide only on first run, or when the saved project or thread no longer exists. A deep link or launch route takes precedence over the saved state.
- [ ] AC-04: User messages that carry the routed-thread header show "Regarding <title> on <machine>:" and then the user's words. Assistant-routed requests show only the user's words, matching `packages/shared/src/routedMessage.ts`.
- [ ] AC-05: A `secret_request` turn item shows a notice row naming the requested secret and its status.
- [ ] AC-06: Version 0.1.5 with a build number above 31 is uploaded, processed (VALID) and in the Internal TestFlight group, and the App Store version 0.1.5 is staged with that build. Review is submitted only after `ASC_LAUNCH_VERIFIED` confirms a real-device launch.

## Approach

All changes are in `repositories/anton-abyzov/specwithcode-dev` (`origin` = public `anton-abyzov/specwithcode`), branch `fix/1257-iphone-coordinator-switch`, made only after the checkout queue hands over ("1257 may branch").

- Hang: fix the root cause found by the live reproduction in `SWCFeatures` and `SWCSync`. The test goes in `SWCKit/Tests` (the `swift test` suite), plus a fixture UITest.
- Restore: a `LastOpenedStore` (UserDefaults key `swc.lastOpened`, a Codable root `ChatTarget` plus an optional thread) that `AppRouter` writes on `open` and `pushThread` and clears on pop. `applyRestore(in:)` runs from `RootView`'s launch task and waits while `model.isLoading`. Fixture runs and launch routes skip it.
- Display: `SWCSync/RoutedMessageDisplay.swift`, a port of the shared TS rules, used by `TranscriptMapper` with the engine's machine labels.
- Secret request: a `TurnItem.SecretRequest` wire type mapped to `.notice`.
- Release: `apps/ios/Tools/release.sh` plus `make testflight`. The script archives with Xcode 27.2, exports, uploads with `asc`, waits, and adds the build to the Internal group. It never submits for review. `project.yml` goes to 0.1.5 / 32.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: "the one in the middle" is read as the header's centre title capsule, which shows "Aide" on launch → restore the last chat. Reversible.
- D-02: App Store submission waits for Anton's real-iPhone launch of the build (the asc guard). TestFlight upload and App Store staging go ahead without it.
### Open
- none

## Tasks

### T-01 Fix the coordinator-switch hang
- AC: AC-01 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/OrchestratorSwitcher.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift, apps/ios/SWCKit/Tests/SWCFeaturesTests/NavigationTests.swift, apps/ios/UITests/OrchestratorSwitchUITests.swift | Test: cd apps/ios/SWCKit && swift test

### T-02 Restore the last project and thread on launch
- AC: AC-02, AC-03 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Navigation/LastOpenedStore.swift, apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, apps/ios/SWCKit/Sources/SWCFeatures/AppBootstrap.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Tests/SWCFeaturesTests/LastOpenedTests.swift | Test: cd apps/ios/SWCKit && swift test --filter "Last opened"

### T-03 Show routed messages and secret requests like desktop
- AC: AC-04, AC-05 | Files: apps/ios/SWCKit/Sources/SWCSync/RoutedMessageDisplay.swift, apps/ios/SWCKit/Sources/SWCSync/TranscriptMapper.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift, apps/ios/SWCKit/Sources/SWCWire/TurnItem.swift, apps/ios/SWCKit/Tests/SWCSyncTests/RoutedMessageDisplayTests.swift | Test: cd apps/ios/SWCKit && swift test --filter "RoutedMessageDisplay|SecretRequest"

### T-04 Publish 0.1.5 to TestFlight and stage it for the App Store
- AC: AC-06 | Files: apps/ios/Tools/release.sh, apps/ios/Makefile, apps/ios/project.yml, apps/ios/docs/app-store.md | Test: asc builds info --app 6824245458 --latest

### T-05 Hand over the checkout
- After the upload, leave specwithcode-dev clean on main and send "1258 may branch" to the "Cross-machine launch from chat" thread.

### T-06 Verify and close 1257
