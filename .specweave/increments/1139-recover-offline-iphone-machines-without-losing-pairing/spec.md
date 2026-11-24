# Recover offline iPhone machines without losing pairing

## Problem
IMG_9348.PNG shows a native iPhone offline chat overflowing horizontally, clipping navigation and leaving reconnect as its only visible action. A saved pairing does not prove reachability.

## Scope
Native iOS layout, offline/loading escape routes, persistent per-machine disconnect/reconnect, direct and Connect recovery guidance, fixture/transport checks, and latest merged-source in-place installation on Anton’s iPhoneA. Preserve pairing, drafts, histories and other owners’ sessions. No server account or VPN configuration changes.

## Acceptance Criteria
- [ ] AC-01: Offline and loading chats stay inside compact phone bounds with readable wrapping and reachable machine controls, including large text.
- [ ] AC-02: Disconnect stops retries locally without deleting pairing or drafts, survives restart, and Connect discovery does not re-enable it; reconnect explicitly resumes.
- [ ] AC-03: Direct-only, Connect-only, mixed routes, expired pairing, signed-out and unsupported machines offer accurate recovery actions. Pair again remains reachable without a working machine.
- [ ] AC-04: Focused Swift and native simulator regression checks pass; latest merged source plus fixes builds and installs in place on iPhoneA with independent version readback.
- [ ] AC-05: SpecWithCode Connect is the primary connection and recovery path; direct LAN/Tailscale pairing is a fallback, including accurate sign-in and outage guidance.

## Approach
Isolated app worktree /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/iphone-offline-recovery-app from origin/main c7e8136fff. Use the existing MachineRecord.enabled persistence and MachineConnection supervisor; expose temporary disconnect separately from forgetting pairing. Constrain native transcript width at the scroll container and wrap placeholder text. Keep recovery navigation available during attempts. Use an owned headless simulator; no visible browser. Apple guidance calls for actionable feedback when loading stalls; Tailscale VPN On Demand can restore VPN on network/hostname changes but cannot wake a powered-off host. SpecWithCode Connect is the primary route and recovery path; saved LAN/Tailscale pairing is a fallback. Neither path proves host health.

## Decisions
### Defaulted
- Disconnect is local to this phone and retains credentials; Remove machine remains a separate confirmed action.
- Re-pairing requires a fresh link from the intended computer; never clear a pairing merely because a network is down.
- Install over the existing iPhoneA release bundle, preserving its app data. Physical network acceptance remains separate from simulator proof.
### Open
- none

### Owner correction, 2026-10-29
- Build 12 was not accepted: the recovery screen led with Tailscale. SpecWithCode Connect must be primary; Tailscale is only a fallback. Update transport priority as well as the visible recovery path, then install the corrected build.

## Tasks
### T-01 Implement and verify native offline recovery
- AC: AC-01, AC-02, AC-03 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Machines/MachineViews.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Settings.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Connect.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Fleet.swift, apps/ios/SWCKit/Sources/SWCTransport/MachineRegistry.swift, apps/ios/SWCKit/Sources/SWCTransport/MachinePairing.swift, apps/ios/SWCKit/Tests/SWCTransportTests/MachineRegistryTests.swift, apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, apps/ios/SWCKit/Sources/SWCSync/MachineRecovery.swift, apps/ios/SWCKit/Sources/SWCFeatures/Support/Mapping.swift, apps/ios/SWCKit/Tests/SWCSyncTests/OfflineRecoveryTests.swift, apps/ios/UITests/OfflineRecoveryUITests.swift, apps/ios/README.md | Test: swift test --package-path apps/ios/SWCKit --enable-code-coverage; owned simulator OfflineRecoveryUITests
### T-02 Build and install latest iPhone candidate
- AC: AC-04 | Files: reports/ | Test: signed iOS Release build, in-place install, independent device version readback
### T-03 Verify and close 1139
- AC: AC-01, AC-02, AC-03, AC-04 | Files: reports/ | Test: specweave verify, fresh-context review, manual native acceptance

### T-04 Keep composer visible across recovery navigation
- AC: AC-02, AC-04 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Support/Chrome.swift | Test: owned simulator OfflineRecoveryUITests, ComposerUITests and AdaptiveLayoutUITests

### T-05 Observe the keyboard in the app's own window
- AC: AC-02, AC-04 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Support/KeyboardInsetReader.swift | Test: owned simulator OfflineRecoveryUITests, ComposerUITests and AdaptiveLayoutUITests

### T-06 Make SpecWithCode Connect primary
- AC: AC-03, AC-04, AC-05 | Files: apps/ios/SWCKit/Sources/SWCTransport/MachineConnection.swift, apps/ios/SWCKit/Sources/SWCSync/MachineRecovery.swift, apps/ios/SWCKit/Sources/SWCFeatures/Machines/MachineViews.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, apps/ios/SWCKit/Tests/SWCTransportTests/ConnectPriorityTests.swift, apps/ios/SWCKit/Tests/SWCSyncTests/OfflineRecoveryTests.swift, apps/ios/UITests/OfflineRecoveryUITests.swift, apps/ios/README.md | Test: Swift suite with coverage, native offline/keyboard/Connect navigation tests, signed build 13 and in-place device install

### T-07 Expose Connect before any cached chat loads
- AC: AC-01, AC-05 | Files: apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift | Test: native cold-start recovery navigation and signed iOS build
