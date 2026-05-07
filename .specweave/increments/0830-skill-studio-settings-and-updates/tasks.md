---
tasks: 25
completed: 25
note: |
  Closure-prep tasks ledger for 0830. Implementation shipped across 6 phases
  (Cargo deps + plugin registration, settings.rs persistence backend, Preferences
  window scaffold, four tabs in parallel, update-flow state machine, browser-mode
  degrade). 31 Rust preferences tests pass. 2 desktop e2e (auto-update happy +
  signature-mismatch) pass. preferences-*.js (67.7 kB / 21.9 kB gzip) ships in
  dist/eval-ui/assets/.

  Two ACs flagged partial (acceptable for v1, recorded in DoD):
    - AC-US3-07: signature-mismatch error tag is currently a pass-through string
      not the structured { tag: "signature-mismatch", message } shape. Functional
      refusal-to-install works.
    - AC-US3-10: cancel-update aborts the install branch but the underlying
      Tauri-plugin-updater download finishes on disk (no clean abort hook).

  User-side launch checklist (Apple Developer ID cert, minisign keypair, R2,
  17 GitHub Secrets, marketing assets, desktop-v0.0.1-rc1 tag) deferred to the
  user-action items in 0829 LAUNCH_CHECKLIST.md.
---

# Tasks — 0830 Skill Studio Settings and Updates

This file ledgers the implementation work shipped across Phases 1–6 of
`plan.md`. Each task references the user story and ACs it satisfies; the two
partial ACs (US3-07, US3-10) are not flipped in spec.md and are tracked as v1
polish backlog items rather than blockers.

---

## Phase 1 — Cargo deps + plugin registration + IPC skeleton

### T-001: Wire `tauri-plugin-updater` crate (closes LAUNCH_CHECKLIST §0)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-06 | **Status**: [x] completed
**Test**: Given an app build → When `cargo check --manifest-path src-tauri/Cargo.toml` runs → Then it finishes with no warnings and `lib.rs` registers `tauri_plugin_updater::Builder::new().build()` in the Builder chain.

### T-002: Wire `tauri-plugin-autostart` crate
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given the cargo manifest → When the Builder boots → Then `tauri_plugin_autostart::Builder::new()` is registered with `MacosLauncher::LaunchAgent` and the `set_autostart` command is exposed via `invoke_handler`.

### T-003: Wire clipboard support for AC-US5-03
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test**: Given the Advanced tab → When the user clicks Copy on the resolved settings path → Then the absolute path lands on the clipboard via Tauri clipboard plugin and a "Copied" toast briefly appears.

### T-004: IPC command skeleton
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**Test**: Given `lib.rs` invoke_handler → When the bundle is inspected → Then `get_settings`, `set_setting`, `reset_settings`, `check_for_update`, `install_and_restart`, and `set_autostart` are all registered.

---

## Phase 2 — settings.rs persistence backend

### T-005: Atomic-write + fsync + rename
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03 | **Status**: [x] completed
**Test**: Given a fault-injection unit test that aborts after fsync but before rename → When the test runs → Then the live `settings.json` is never observed in a corrupt state and the tmp file is left behind for forensic inspection.

### T-006: 0600 perm enforcement on Unix
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**Test**: Given a settings file with mode 0644 → When the persistence layer loads it → Then it is rewritten to 0600 and a warn-level log line records the fix (`test_loose_perms_get_tightened_on_load`).

### T-007: Schema-versioned read with unknown-key round-trip
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05, AC-US6-06, AC-US6-07 | **Status**: [x] completed
**Test**: Given a settings.json with a top-level key the binary doesn't know about → When loaded and saved → Then the unknown key round-trips intact (`test_unknown_top_level_keys_round_trip`); given a future schema_version the payload is discarded (`test_schema_future_version_discards_payload`).

### T-008: Debounced writes + concurrent-set serialization
**User Story**: US-006 | **Satisfies ACs**: AC-US6-08, AC-US6-09 | **Status**: [x] completed
**Test**: Given five rapid `set_setting` calls within 250ms → When the debouncer flushes → Then exactly one disk write is observed (`test_debounced_writes_collapse_within_250ms`); given two concurrent set_setting calls → Then they are serialized via the tokio Mutex (`test_concurrent_set_serializes`).

### T-009: Reset to defaults with timestamped backup
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05, AC-US6-07 | **Status**: [x] completed
**Test**: Given a populated settings.json → When `reset_settings()` is invoked → Then the live file is renamed to `settings.json.bak.YYYYMMDD-HHMMSS`, replaced with default content, and the keychain is untouched (`test_reset_writes_defaults_and_backs_up`).

---

## Phase 3 — Preferences window scaffold

### T-010: Preferences `WebviewWindow` builder + macOS menu wiring
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test**: Given a running desktop app → When the user activates `Skill Studio → Preferences…` (⌘,) → Then a 720×560 non-resizable centred webview labelled `preferences` opens within 200ms; given the window already exists → Then `Manager::get_webview_window("preferences")` short-circuits and focuses the existing window (verified by the desktop e2e suite).

### T-011: Win/Linux Edit menu position
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given the Tauri menu API on Win/Linux → When the menu is built → Then a `Settings` item is added to a top-level `Edit` submenu with accelerator `Ctrl+,`.

### T-012: useSettings facade + useDesktopBridge runtime probe
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-06 | **Status**: [x] completed
**Test**: Given the Preferences UI mounted in the desktop wrapper → When `useDesktopBridge()` is called → Then it returns `{ available: true }` because `window.__TAURI_INTERNALS__` is set; given a plain browser → Then `{ available: false }` and the same component tree renders with `aria-disabled` flips on desktop-only controls.

---

## Phase 4 — Four tabs in parallel

### T-013: General tab — launch-at-login + theme + default project folder
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Test**: Given the General tab → When the user toggles `Launch at login` → Then `tauri-plugin-autostart` registers the LaunchAgent (or `.desktop` / Run-registry on Linux/Win); given an MDM-blocked Mac → Then the toggle reverts and a toast appears with `Open System Settings` deeplink; given a theme change → Then the CSS `data-theme` attribute updates immediately on `<html>` and persists to `general.theme`.

### T-014: Updates tab — check, channel, install-and-restart
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-08 | **Status**: [x] completed
**Test**: Given the Updates tab → When the user clicks `Check for Updates` → Then `check_for_update` calls `tauri-plugin-updater::check()` and the status row reflects one of `up-to-date`, `update-available v.X.Y.Z`, or `error`; given an available update → When `Install & Restart` is clicked → Then `download_and_install()` runs, the bundle is signature-verified, and the app exits + relaunches on the new version; given a 24h-stale lastCheckedAt → Then the boot-time auto-check task runs in the background and pre-populates the tab.

### T-015: Privacy tab — telemetry opt-out + log folder reveal
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given the Privacy tab → When the user toggles `Send anonymous usage telemetry` → Then `privacy.telemetryEnabled` is persisted to settings.json with no other UI feedback (the disclosure paragraph already explains it's a no-op today); given a click on `Reveal log folder` → Then the platform file manager opens at `~/Library/Logs/vSkill/` (or platform equivalent), creating the folder first if it does not exist.

### T-016: Advanced tab — log level + path copy + factory reset
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**Test**: Given the Advanced tab → When the user changes the log level → Then it persists to `advanced.logLevel` and applies live to the running Rust process within 1s; given a click on `Copy` → Then the absolute settings path is on the clipboard with a brief Copied toast; given a click on `Reset all settings to defaults…` → Then a native confirm dialog appears, on Reset the settings.json is renamed to `settings.json.bak.YYYYMMDD-HHMMSS`, replaced with defaults, and the Preferences window reloads.

---

## Phase 5 — Update-flow state machine

### T-017: Updater state machine (idle → checking → up-to-date | available | error)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-06 | **Status**: [x] completed
**Test**: Given an idle updater state → When `check_for_update` is invoked → Then state transitions to `checking` and lands on `up-to-date`, `update-available`, or `error` (`test_state_transitions_idle_to_checking`); given an in-flight check → When a second click arrives → Then it is a no-op enforced by a Rust-side mutex.

### T-018: Manual menu item routes through the same code path as the tab button
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 (partial — pass-through string today) | **Status**: [x] completed
**Test**: Given `Skill Studio → Check for Updates...` is clicked → When the menu-action handler fires → Then it opens the Preferences window on the Updates tab and triggers a check via the same command as the tab button.

### T-019: Boot-time 24h auto-check
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test**: Given `lastCheckedAt > 24h` at app boot → When the Builder finishes setup → Then `preferences::updater::spawn_auto_check_task` runs in the background, no UI is shown, and the result is stored so the Updates tab is pre-populated when next opened.

---

## Phase 6 — Browser-mode degrade + i18n stub + e2e

### T-020: Browser-mode aria-disabled flips
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05 | **Status**: [x] completed
**Test**: Given `npx vskill studio` open in a plain browser → When the Preferences UI mounts → Then General tab disables Launch-at-login and Default-project-folder with a callout, Updates tab is replaced with the install/CLI panel, Privacy keeps telemetry but disables Reveal-log-folder, and Advanced disables log-level + Reset.

### T-021: i18n catalog + `t()` flow
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given every user-visible string → When the locale catalog is inspected → Then every string flows through `t()` with an English-only catalog at `src/eval-ui/src/locales/en.json` and the infra is ready for additional languages.

### T-022: Desktop e2e — happy path auto-update
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04, AC-US9-06 | **Status**: [x] completed
**Test**: Given a debug-bundle desktop app pointed at a local manifest server (`scripts/test-fixtures/manifest-server.ts`) → When the spec opens Preferences → Updates → clicks Check for Updates and Install & Restart → Then the status row reads `Update available: v0.2.0`, the app relaunches, and after relaunch the current version reads `0.2.0` and the status reads `Skill Studio is up to date.`

### T-023: Desktop e2e — negative path signature mismatch
**User Story**: US-009 | **Satisfies ACs**: AC-US9-05 | **Status**: [x] completed
**Test**: Given a v0.2.0 manifest signed with the WRONG minisign key → When the spec triggers Install & Restart → Then the install fails, the status row reads `Update signature invalid — refusing to install`, the running version stays at `0.1.0`, and the rejected signature/version is logged to `~/Library/Logs/vSkill/updater.log`.

### T-024: Studio bundle includes preferences entrypoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06 | **Status**: [x] completed
**Test**: Given `npm run build:eval-ui` → When the dist is inspected → Then `dist/eval-ui/assets/preferences-*.js` is emitted (67.7 kB / 21.9 kB gzip) and the desktop window loads it via `WebviewUrl::App("preferences.html")`.

### T-025: Documentation + i18n smoke check
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-07 | **Status**: [x] completed
**Test**: Given the General-tab implementation → When the user opens Preferences for the first time → Then all three controls reflect their persisted values synchronously before first paint with no flicker (no async fetch on open).
