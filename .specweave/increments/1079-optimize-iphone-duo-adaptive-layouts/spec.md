# 1079 Optimize SpecWithCode for iPhone Duo

## Problem
The native iOS client is portrait-only and overlays its navigation on every window size. Anton receives iPhone Duo November 3 and wants simulator-first readiness. Theo's linked posts demonstrate remote iOS simulator access; they do not establish this app's compatibility. M4 has Xcode 26.3 without Duo. The authorized M1 now has Xcode 27.1 and the installed iOS 27.1 Duo runtime.

## Scope
In: adaptive native navigation, rotation, asymmetric safe areas, isolated simulator regression checks, source-backed research and an explicit Duo acceptance matrix. Out: unrelated rendering and project-partition work, live data, authentication changes. Full acceptance stays open until the simulator matrix and manual/hardware checks pass.

## Acceptance Criteria
- [ ] AC-01: Wide regular-width windows show usable navigation beside chat; compact windows retain the drawer. Resizing preserves chat/navigation/draft state and does not leave content hidden from accessibility.
- [ ] AC-02: Portrait and both landscape orientations are supported; foreground content respects leading and trailing safe areas.
- [ ] AC-03: Native simulator checks cover compact navigation, rotation, keyboard/draft continuity and expanded navigation with saved results; surrogate results are distinguished from Duo results.
- [ ] AC-04: Research identifies both Theo posts and Apple guidance; an executable Duo simulator gate rejects an absent SDK/device type, and the November 3 hardware matrix remains explicit.

## Approach
Use an isolated worktree /tmp/swc-iphone-duo, branch codex/iphone-duo, based on origin/main ed1622b9f0. Preserve 1066 DrawerView ownership and active rendering work. Adapt the existing DrawerContainer in place, retaining one content subtree across size changes. Use current geometry and size classes, never device identity or main-screen dimensions. Enable landscape in XcodeGen. Verify with owned headless native simulators, and require Xcode 27.1 for real Duo tests. No broad web/server changes. M1 testing uses only /tmp/swc-1079-duo-e43516d037 and owned simulator SWC-1079-Duo (4692FC3F-6D84-43EA-81FE-C657192445C8).

## Decisions
### Defaulted
- Optimize the native SpecWithCode iOS app in this workspace.
- A persistent navigation column requires regular width and enough room for a readable chat; compact layouts remain modal.
- iOS 26 remains the deployment minimum; build with the newer SDK when available.
- iPad simulator can exercise expanded layout via a test-only build override; it is not Duo proof or iPad product expansion.
### Open
- none

## Tasks

### T-01 Research and implement adaptive navigation
- AC: AC-01, AC-02, AC-04 | Files: apps/ios/SWCKit/Sources/Weave/Components/DrawerContainer.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Support/Chrome.swift, apps/ios/project.yml, apps/ios/docs/IPHONE-DUO.md, apps/ios/Tools/duo-readiness.sh | Test: cd /tmp/swc-iphone-duo/apps/ios && make sim-build SIM_NAME=SWC-1079-Compact

### T-02 Verify native simulator behavior
- AC: AC-01, AC-02, AC-03 | Files: apps/ios/UITests/AdaptiveLayoutUITests.swift, apps/ios/App/Tests/AdaptiveDrawerTests.swift, apps/ios/Tools/test-duo-readiness.py, apps/ios/Tools/duo-readiness.sh, apps/ios/docs/IPHONE-DUO.md | Test: cd /tmp/swc-iphone-duo/apps/ios && make sim-test SIM_NAME=SWC-1079-Compact ONLY=SpecWithCodeUITests/AdaptiveLayoutUITests

### T-03 Verify and close 1079
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1079-optimize-iphone-duo-adaptive-layouts/evidence | Test: specweave verify 1079

### T-04 Fix Xcode 27.1 compilation and verify on M1
- AC: AC-03, AC-04 | Files: apps/ios/SWCKit/Sources/Weave/Components/AppearanceTile.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, apps/ios/SWCKit/Sources/SWCFeatures/Support/Chrome.swift, apps/ios/SWCKit/Sources/Weave/Components/DrawerContainer.swift, apps/ios/App/Tests/AdaptiveDrawerTests.swift, apps/ios/SWCKit/Tests/SWCFeaturesTests/ScreenLogicTests.swift, apps/ios/docs/IPHONE-DUO.md, apps/ios/Tools/duo-readiness.sh, apps/ios/UITests/AdaptiveLayoutUITests.swift | Test: python3 /tmp/swc-duo-m1.py /tmp/swc-duo-m1-verify.py

### T-05 Correct composer tap targets found by full native audit
- AC: AC-03 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift | Test: cd /tmp/swc-iphone-duo/apps/ios && make sim-test SIM_NAME=SWC-1079-Compact ONLY=SpecWithCodeUITests/HitTargetAuditUITests


### T-06 Preserve accessible sender identity and current navigation assertions
- AC: AC-03 | Files: apps/ios/SWCKit/Sources/Weave/Components/MessageBubble.swift, apps/ios/UITests/ThreadUITests.swift, apps/ios/UITests/ThreadMenuUITests.swift | Test: cd /tmp/swc-iphone-duo/apps/ios && make sim-test SIM_NAME=SWC-1079-Compact ONLY=SpecWithCodeUITests/ThreadUITests

The full send check found the message present, but sought a removed legacy `You:` text prefix. Preserve Markdown/link descendants; label the existing user-message container once, give it a stable author-role identifier, and require the sent text inside that user container. This retains both sender and exact-content assertions rather than matching arbitrary assistant text.

The delete check already returned to the overview; its failure tree uses the current “Waiting on you” heading. Refresh that renamed heading selector and retain deleted-row absence and Working-count assertions; no navigation implementation change is needed.

### T-07 Deliver native UI test taps to visible target centers
- AC: AC-03 | Files: apps/ios/UITests/SWCUITestCase.swift, apps/ios/UITests/AdaptiveLayoutUITests.swift, apps/ios/docs/IPHONE-DUO.md | Test: cd /tmp/swc-iphone-duo/apps/ios && make sim-test SIM_NAME=SWC-1079-Compact ONLY=SpecWithCodeUITests/AdaptiveLayoutUITests

Independent M1 diagnostics showed UIKit and SwiftUI counter buttons accepting XCTest taps. The real app Menu element tap failed, while a public XCUICoordinate tap at that exact element's center passed. Use the visible target center after existence/hittability checks; retain drawer, accessibility, draft and geometry assertions.

### T-08 Verify wide compact traits independently of screen width
- AC: AC-01, AC-03 | Files: apps/ios/App/Tests/AdaptiveDrawerTests.swift, apps/ios/UITests/AdaptiveLayoutUITests.swift, apps/ios/docs/IPHONE-DUO.md | Test: cd /tmp/swc-iphone-duo/apps/ios && make sim-test SIM_NAME=SWC-1079-Compact ONLY=SpecWithCodeTests/AdaptiveDrawerTests

A 678-point landscape outer display remains compact. Width alone cannot predict its navigation mode. Native component tests explicitly supply wide compact and regular traits; UI tests must verify the presented navigation mode and its outcome without treating every wide viewport as regular.

### T-09 Verify Duo background, deep-link and drawer timing outcomes
- AC: AC-03 | Files: apps/ios/UITests/AideHistoryUITests.swift, apps/ios/UITests/DrawerUITests.swift, apps/ios/docs/IPHONE-DUO.md | Test: cd /tmp/swc-iphone-duo/apps/ios && SIM_NAME=SWC-1079-Compact bash Tools/sim.sh test -only-testing:SpecWithCodeUITests/AideHistoryUITests -only-testing:SpecWithCodeUITests/DrawerUITests

The exact-source Duo full run exposed background-state, short-landscape approval visibility and immediate post-dismissal assertions. Preserve lifecycle, exact-draft, approval and composer usability outcomes; account for legitimate suspended background state, scrolling and asynchronous hit-test updates. Record actual states and failure details rather than relaxing outcome checks.
