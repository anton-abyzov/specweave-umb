# Tasks — 0864 Desktop update banner + reliable re-check

### T-001: Foreground re-check cadence in useAppUpdater
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a mounted desktop AppUpdaterProvider, When window `focus`
fires, Then `checkForUpdates` is called again; When a second focus fires within
30min, Then no extra check; When the hourly interval elapses, Then a check runs.
**Test**: `__tests__/useAppUpdater.recheck.test.tsx`

### T-002: Split banner-dismiss from pill visibility
**AC**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given an available update, When `dismissBanner()` is called, Then
`bannerVisible` is false but `available` stays true (pill remains). When a higher
`latestVersion` arrives, Then `bannerVisible` is true again.
**Test**: `__tests__/useAppUpdater.recheck.test.tsx`

### T-003: UpdateBanner component
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given `bannerVisible`, Then `app-update-banner` renders with the
version and an "Update now" button; clicking installs then restarts; an install
error keeps it visible and retryable; when not available it renders null.
**Test**: `__tests__/UpdateBanner.test.tsx`

### T-004: Wire banner into App.tsx, remove floating toast
**AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given the studio shell, Then the banner mounts in the StudioLayout
banner slot and `AppUpdateToast` is no longer mounted; `AppUpdateButton` pill
still present.
**Test**: build + existing AppUpdateButton test green; AppUpdateToast test removed.

### T-005: Rust auto-check error backoff
**AC**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given the auto-check loop, When a check errors, Then the loop
sleeps the short retry (~1h); When it succeeds, Then the 24h cadence is kept.
**Test**: `cargo build` green + updater.rs constant test.

### T-006: Build + unit verification
**AC**: AC-US5-01 | **Status**: [x] completed
**Test Plan**: `npm run build`, `npm run build:eval-ui`, `npx vitest run src/eval-ui`,
`cargo build` (src-tauri) all green.

### T-007: Publish desktop v1.0.52
**AC**: AC-US5-02 | **Status**: [x] completed
**Test Plan**: `bash scripts/release/release-desktop.sh 1.0.52`; then
`curl https://verified-skill.com/desktop/latest.json` serves version 1.0.52.

### T-008: Scoped remote-updater capability (studio window IPC)
**AC**: AC-US6-01, AC-US6-02 | **Status**: [x] completed
**Test Plan**: Given the studio main window (localhost remote origin), When the
`studio-updater` capability + `allow-updater-commands` permission are added,
Then `check_for_updates`/`get_settings`/`get_app_metadata` invoke successfully
and the banner renders; cargo check validates the ACL. Verified on a real
notarized build: v1.0.51 demo → click Update now → updated to v1.0.52.

### T-009: Publish desktop v1.0.53 (capability fix)
**AC**: AC-US6-03 | **Status**: [x] completed (CI building → live)
**Test Plan**: `bash scripts/release/release-desktop.sh 1.0.53`; then
`curl https://verified-skill.com/desktop/latest.json` serves 1.0.53.

### T-010: Header-integrated highlighted update chip
**AC**: AC-US7-01..04 | **Status**: [x] completed
**Test Plan**: Given a desktop update is available, Then the highlighted chip
renders in the top rail's left group after the project picker (NOT the right
cluster); the full-width banner is gone; clicking installs+restarts.
**Test**: TopRail.updateBell.test.tsx (left-group placement), AppUpdateButton.test.tsx,
useAppUpdater.recheck.test.tsx — all green; eval-ui builds.

### T-011: Publish desktop v1.0.54 (header chip)
**AC**: AC-US7-05 | **Status**: [x] completed (v1.0.54 LIVE)
**Test Plan**: `bash scripts/release/release-desktop.sh 1.0.54`; live manifest
serves 1.0.54; chip visible on a real build.
