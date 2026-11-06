# Fix pop-up display and audit presentation

## Problem

The November 3, 2026 iPad screenshot shows the Photo Library / Take Photo confirmation halfway up the split view, detached from the composer Attach button. ChatView attaches attachmentPickers to the full transcript screen. SwiftUI therefore has the screen as the presentation source instead of the button. The earlier React Activity portal leak is a separate web lifecycle issue.

## Scope

In: native attachment anchor repair; audit every native confirmation and menu family, and shared web menus, popovers, dialogs, tooltips, select and combobox wrappers; reproduce and fix confirmed related defects. Out: release dispatch, live account actions, existing unrelated owner edits, fabricated screenshot proof.

## Acceptance Criteria

- [ ] AC-01: On iPad split view, Attach choices originate beside the pressed attachment control in either chat column and remain on screen after rotation; iPhone selection, cancellation and photo delivery still work.
- [ ] AC-02: Every native confirmation and shared popup family has an explicit audit disposition with measured visual checks or a named unverified limitation; confirmed broad-anchor defects are repaired without changing destructive actions.
- [ ] AC-03: Web popup switching checks cover menus, popovers, dialogs, tooltips, selects and comboboxes in light/dark and narrow/wide views; no confirmed hidden-page portal survives navigation.
- [ ] AC-04: Changes have focused passing tests, native build evidence, a fresh exact-head review and a PR against the approved existing base branch.

## Approach

First secure an owned checkout without switching the shared feat/server-linked-sync branch. Move attachment presentation to the actual Attach control: add a narrowly scoped attachment-control customization point to Weave ComposerBar if required, and keep photo decoding/upload state in SWCFeatures. Audit the eight other confirmationDialog sites, preferring trigger-local anchoring or a centered alert for confirmations without a stable trigger. Do not blanket-change Menu or contextMenu, which already own their labels/rows.

Inspect shared web wrappers and retained-page lifecycle. Select and Combobox currently bypass usePagePopup; reproduce before changing their registration because Base UI action APIs may differ. Preserve separate close and unmount commits. Add a dedicated synthetic popup fixture only where existing checks cannot exercise the behavior. Native screenshots must come from the real SwiftUI app, not a browser imitation. Use isolated sample data and simulators; never touch the live database or provider accounts.

## Decisions

### Asked
- None. Coordinator must resolve repository ownership and base branch operationally.

### Defaulted
- Use verified SpecWeave 3.1.20 via session-local npx; installed 3.1.17 stays unchanged.
- Save before/after evidence in this increment reports directory. Browser checks are headless with PWDEBUG=0 and PLAYWRIGHT_HTML_OPEN=never.

### Open
- None. User authorized a dedicated worktree on November 3, 2026. GitHub confirms main as the app default branch. Worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/1213-popup-anchors`.

## Tasks

### T-01 Repair native popup anchors and verify affected confirmations
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatAttachments.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/Weave/Components/ComposerBar.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Connect/ConnectViews.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Machines/MachineViews.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Settings/ProjectSettingsSheet.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Settings/ConnectPhonesCard.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/UITests/PopupPresentationTests.swift | Test: xcodebuild test -project apps/ios/SpecWithCode.xcodeproj -scheme SpecWithCode -only-testing:SpecWithCodeUITests/PopupPresentationTests (with dedicated simulator destination and result bundle)

### T-02 Audit web popup families and repair reproduced lifecycle gaps
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/KeptProjectPages.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/select.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/combobox.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/pagePopups.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/pagePopups.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/popover-switch-check.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/popup-presentation/index.html, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/popup-presentation/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/popup-presentation/fixture.css, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/popup-presentation/vite.config.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/popup-presentation/verify.mjs | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/ui/pagePopups.test.tsx; PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node apps/web/tests/project-workspace/popover-switch-check.mjs

### T-03 Review, deliver PR, verify and close 1213
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/reports/investigation.md | Test: specweave verify 1213; fresh-context exact-head review; specweave complete 1213
