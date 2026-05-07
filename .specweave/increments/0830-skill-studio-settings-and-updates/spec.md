---
increment: 0830-skill-studio-settings-and-updates
title: >-
  Skill Studio — native Preferences, auto-update UI, autostart & settings
  persistence
type: feature
priority: P0
status: completed
created: 2026-05-07T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
projects:
  - vskill
parent: 0829-vskill-distribution-and-marketing
---

# Feature: Skill Studio — native Preferences, auto-update UI, autostart & settings persistence

## Overview

0829 shipped the distribution rails (signed `.dmg` / `.msi` / `.deb`, GitHub Actions release pipeline, minisign-signed manifest, `tauri-plugin-updater` declared in config). This increment builds the **user-facing surface** that lets people actually live inside the desktop app over the long haul: a native Preferences window, a polished "Check for Updates" experience, cross-platform launch-at-login, and a single source of truth for app settings persisted to `~/.vskill/settings.json`.

The increment also closes the dead-code gap from `LAUNCH_CHECKLIST.md §0` (wiring the `tauri-plugin-updater` crate into `Cargo.toml` + the Builder chain) so the auto-update plumbing is exercisable end-to-end.

> **Brand note**: Per user direction in `metadata.json`, all user-visible copy uses **"Skill Studio"** (not "vSkill"). The internal product/repo names remain `vskill` until the rename increment lands as a separate spawn_task.

## Problem Statement

After 0828 (desktop shell) + 0829 (distribution + marketing), the app boots, signs, and ships — but it has **no user-controllable settings surface and no usable update flow**:

1. **No Preferences window.** The macOS App menu has no `Preferences…` item; the only configurability the user has is via `~/.claude/settings.json` (Claude Code plugin state), which is a developer file, not a product surface.
2. **`Check for Updates...` is a stub.** `menu.rs` registers the menu item and emits a `menu-action` event to the webview, but no UI handles it. The user sees nothing.
3. **Auto-update is dead code.** `tauri.conf.json` declares the full `plugins.updater` block (endpoints, pubkey, dialog), but the Rust crate is missing from `src-tauri/Cargo.toml` and not registered on the Builder. No update prompts ever reach the user — `LAUNCH_CHECKLIST.md §0` flags this as P0.
4. **No launch-at-login control.** Power users routinely expect this on a tray-class developer tool.
5. **No app-level settings persistence.** `useStudioPreferences.ts` already documents this explicitly: *"BLOCKING_ISSUE: The team-lead spec calls for a project-local `.vskill/studio.json` persisted via the eval-server so preferences survive across browsers."* Today every preference is single-browser localStorage and disappears on a desktop reinstall, a different webview cache, or `studio.json` migration.

Until this increment ships, "Skill Studio" cannot legitimately call itself a product the user *configures* — only one they *launch*.

## Goals (v1)

1. **Native Preferences window** (Tauri secondary webview) with 4 tabs: General, Updates, Privacy, Advanced — opened from `Skill Studio → Preferences…` (macOS, ⌘,) and a tray equivalent on Win/Linux.
2. **Working `Check for Updates…` flow** — manual check from the menu, toast if up-to-date, modal if an update is available, "Install & Restart" wires through `tauri-plugin-updater`, signature-verifies the bundle, and relaunches.
3. **`tauri-plugin-updater` crate wired in** — closes `LAUNCH_CHECKLIST.md §0` (5-min code change) and unblocks any release ≥ v0.1.0 from shipping silent dead-code auto-update.
4. **Cross-platform launch-at-login toggle** via `tauri-plugin-autostart` — LaunchAgent on macOS, Run registry on Windows, `.desktop` file on Linux. State reflected in Preferences and persisted.
5. **Settings persisted to `~/.vskill/settings.json`** with atomic writes, schema validation, 0600 perms on Unix, and a single Tauri command surface (`get_settings`, `set_setting`, `reset_settings`) shared between the desktop app and the studio runtime.
6. **Studio runtime gracefully degrades** when running in a plain browser (`npx vskill studio` without the desktop wrapper) — settings UI reads same shape but writes via existing localStorage hook + a "Install desktop app to persist" callout.
7. **First-class update channel selector** (`stable` / `beta`) — the existing manifest URL is per-channel, so this maps to an additional manifest endpoint and is recorded in settings.
8. **Telemetry opt-out** — single boolean in Privacy tab, persisted, honored by every emitter (zero telemetry today, but the toggle ships now so opt-in/out is settled before any telemetry lands).

## Out of Scope (v1)

- **Sync settings across machines** (would require account + server) — defer to post-launch cloud sync increment.
- **Per-project preferences override** — single global `~/.vskill/settings.json` only. Project-local overrides are a follow-on.
- **System tray icon** on macOS/Windows/Linux — follow-on increment; this one keeps the existing dock-only behavior.
- **Auto-start with project pre-loaded** — "launch at login" only opens the app; deep-restoring the last project belongs in a session-state increment.
- **Crash reporting / telemetry pipeline** — only the user-facing opt-out switch ships; the actual emitter is not built here.
- **Beta channel infrastructure** — the **selector** ships, but the `beta` manifest endpoint stays a 404 stub until a beta release is actually cut. Selecting `beta` shows "no beta channel yet" toast until then.
- **In-app changelog viewer** — the update modal links to the GitHub Release page; an embedded viewer is post-launch.
- **Granular update verification UI** (signature progress bar, etc.) — single status string per state is enough for v1.

## Inherited Givens (do NOT redesign)

- Tauri 2 Rust shell + Node SEA sidecar (from 0828)
- `tauri.conf.json` `plugins.updater` block already declared with endpoint `https://verified-skill.com/desktop/latest.json` and `<MINISIGN_PUBKEY_PLACEHOLDER>` (placeholder replaced at release time per 0829 §2)
- Existing menu: `Skill Studio → Check for Updates...` already emits `menu-action` event with `action: "check_for_updates"` to the main webview
- `useStudioPreferences` hook in `src/eval-ui/src/hooks/` (localStorage-only) is the existing client surface — extend, don't replace
- 0702 keychain (`KeyStore`) handles secrets — settings.json must NOT store any secret
- `tauri-plugin-single-instance` already prevents two desktop instances (no settings-write race)
- `tauri-plugin-shell`, `tauri-plugin-dialog`, `tauri-plugin-notification`, `tauri-plugin-deep-link` already in the Builder

## Personas

### P-1: Skill Author / Power User (PRIMARY)
Already running the desktop app daily. Wants Skill Studio to launch at login, auto-update silently, never lose their preferred theme/model. Will dig into Preferences exactly once on first install and expect everything to be where they look.

### P-2: Cautious Enterprise User (SECONDARY)
Installed via IT-approved download. Privacy-conscious — first thing they do is open Preferences → Privacy and confirm telemetry is off (or stays off). May be on a corp-managed macOS where launch-at-login is blocked by MDM; expects a clear explanation, not a silent failure.

### P-3: Browser-only Studio User (TERTIARY)
Runs `npx vskill studio` and never installs the desktop app. Lands on the same Preferences UI inside the studio runtime; expects every desktop-only field (autostart, update channel, log folder reveal) to be greyed out with a "this requires the desktop app" hint, not broken or hidden.

### P-4: Release Manager (LAUNCH-DAY ONLY)
Tags `desktop-v0.2.0`, watches GitHub Actions push the manifest. Wants to verify within 5 minutes that running v0.1.0 instances see the update prompt, install cleanly, and relaunch on the new version. End-to-end smoke test is on this increment.

## User Stories

---

### US-001: Open the Preferences window from the menu (P0)
**Project**: vskill

**As a** Skill Studio user
**I want** to open a native Preferences window from `Skill Studio → Preferences…` (⌘,) or a Settings entry on Win/Linux
**So that** I have a single place to configure the app without editing JSON files by hand

**Acceptance Criteria**:
- [x] **AC-US1-01**: macOS menu builder adds a `Preferences…` item to the `Skill Studio` submenu with accelerator `Cmd+,`, positioned above `Services` and below `About Skill Studio` (matches Apple HIG)
- [x] **AC-US1-02**: On Windows and Linux, the same item is added to a top-level `Edit` (or platform-equivalent) submenu with accelerator `Ctrl+,` — Tauri menu API takes the platform-specific position
- [x] **AC-US1-03**: Clicking `Preferences…` (or pressing the accelerator) opens a secondary webview labelled `preferences` with title `Skill Studio — Preferences`, dimensions 720×560, non-resizable, centred over the main window
- [x] **AC-US1-04**: If the Preferences window is already open, the menu action focuses the existing window instead of opening a duplicate (Tauri `Manager::get_webview_window("preferences")` short-circuits)
- [x] **AC-US1-05**: Closing the Preferences window does not close the main app; closing the main app closes the Preferences window if it is open (lifecycle owned by the main window)
- [x] **AC-US1-06**: First paint of the Preferences UI happens within 200ms of the menu click (no network calls during open) — measured via a Playwright timer in the desktop e2e suite

---

### US-002: General tab — launch at login + theme + default project folder (P0)
**Project**: vskill

**As a** daily user
**I want** to toggle "Launch Skill Studio at login", pick a UI theme (System / Light / Dark), and set a default project folder
**So that** the app integrates with my workflow without me editing config files

**Acceptance Criteria**:
- [x] **AC-US2-01**: General tab renders three controls: a checkbox `Launch at login`, a segmented control `Theme: System | Light | Dark`, and a folder-picker labelled `Default project folder` showing the current path or `(not set)`
- [x] **AC-US2-02**: Toggling `Launch at login` ON registers the app with `tauri-plugin-autostart` (LaunchAgent on macOS, Run registry on Windows, `.desktop` file on Linux); toggling OFF unregisters it
- [x] **AC-US2-03**: If `tauri-plugin-autostart` returns an error (e.g., MDM-blocked on a corp-managed Mac), the checkbox reverts to its previous state and a toast appears: *"Couldn't change launch-at-login. Your administrator may have disabled this."* with a `Open System Settings` action that deeplinks to the relevant settings pane
- [x] **AC-US2-04**: Theme change applies immediately to both the Preferences window and the main window (CSS `data-theme` attribute on `<html>`); persisted to `~/.vskill/settings.json` under `general.theme`
- [x] **AC-US2-05**: `System` theme follows the OS appearance (live updates when the user toggles dark mode in OS settings) via Tauri's `theme()` event
- [x] **AC-US2-06**: Folder-picker uses `tauri-plugin-dialog`'s native picker; selected path is validated to exist + be writable, persisted to `~/.vskill/settings.json` under `general.defaultProjectFolder`; invalid path shows inline error and is not persisted
- [x] **AC-US2-07**: All three controls reflect their persisted value on Preferences open (no flicker — values are read synchronously before first paint)

---

### US-003: Updates tab — check, channel, and "Install & Restart" (P0)
**Project**: vskill

**As a** Skill Studio user
**I want** to manually check for updates, see the current version + latest version, pick a channel (stable / beta), and install an available update with a single click
**So that** I am never trapped on a stale version and have agency over when an update lands

**Acceptance Criteria**:
- [x] **AC-US3-01**: Updates tab shows: current version (read from `tauri::app::package_info().version`), latest version (from manifest, `(checking…)` while in flight, `(unknown)` on error), last-check timestamp in local time, channel selector `stable | beta`, primary button `Check for Updates`, and a status row reflecting one of: `up-to-date`, `update-available`, `error`
- [x] **AC-US3-02**: Clicking `Check for Updates` calls a `check_for_update` Tauri command that invokes `tauri-plugin-updater`'s `check()`; on success with no update, status row reads `Skill Studio is up to date.`; with an update, status reads `Update available: v.X.Y.Z` and a secondary button `Install & Restart` appears with release notes (markdown, scrollable)
- [x] **AC-US3-03**: Clicking `Install & Restart` downloads and verifies the update via `tauri-plugin-updater`'s `download_and_install()`; on success the app exits and relaunches on the new version; on signature-verification failure the status row shows `Update signature invalid — refusing to install` and an entry is written to `~/Library/Logs/vSkill/updater.log` (or platform equivalent) with the rejected signature/version
- [x] **AC-US3-04**: Channel selector defaults to `stable`; switching to `beta` updates `updates.channel` in settings.json and re-points the manifest URL to `https://verified-skill.com/desktop/beta.json`. If that endpoint returns 404, the next check shows `No beta releases yet — staying on your current build.` (no error toast)
- [x] **AC-US3-05**: An automatic check runs at app boot if `Date.now() - lastCheckedAt > 24h`; runs in the background (no UI) and stores the result so the Updates tab is pre-populated when next opened. The 24h interval is fixed in v1 (no user control)
- [x] **AC-US3-06**: Only one update check / install can be in flight at a time, enforced by a Rust-side mutex in the updater command. A second click while the first is in flight is a no-op (button disabled with spinner)
- [x] **AC-US3-07** (functionally complete; v1.1 polish — see DoD): Existing `Skill Studio → Check for Updates...` menu item routes through the same code path as the tab button (single source of truth) — clicking it opens the Preferences window on the Updates tab and triggers the check
- [x] **AC-US3-08**: When no update is available, last-check timestamp updates and persists; when an error occurs (network down, manifest 5xx, signature mismatch), last-check is NOT updated and the user can retry immediately

---

### US-004: Privacy tab — telemetry opt-out + log folder reveal (P0)
**Project**: vskill

**As a** privacy-conscious user
**I want** to confirm telemetry is off (or turn it off) and reveal the log folder so I can audit what's recorded
**So that** I can use Skill Studio without worrying about silent data collection

**Acceptance Criteria**:
- [x] **AC-US4-01**: Privacy tab renders: a checkbox `Send anonymous usage telemetry` (default OFF, persisted to `privacy.telemetryEnabled`), a `Reveal log folder` button, and a static disclosure paragraph: *"Skill Studio v1 does not currently emit any telemetry. This setting is reserved so your preference is honored when telemetry is added in a future release."*
- [x] **AC-US4-02**: Toggling `Send anonymous usage telemetry` persists immediately to `~/.vskill/settings.json` under `privacy.telemetryEnabled`. No additional UI feedback (the disclosure paragraph already explains it's a no-op today)
- [x] **AC-US4-03**: Clicking `Reveal log folder` opens the platform-native file manager at `~/Library/Logs/vSkill/` (macOS), `%LOCALAPPDATA%\vSkill\Logs\` (Windows), or `~/.cache/vskill/logs/` (Linux) via `tauri-plugin-shell`'s `open()` — same path used by `commands::log_dir`
- [x] **AC-US4-04**: If the log folder does not yet exist, it is created (recursively) before the file manager opens — no `directory not found` error reaches the user

---

### US-005: Advanced tab — log level, factory reset, settings file path (P1)
**Project**: vskill

**As a** developer or support escalation user
**I want** to crank up the log level when debugging, see exactly where my settings live, and reset everything back to defaults if I corrupt my config
**So that** I can self-serve troubleshooting without waiting on support

**Acceptance Criteria**:
- [x] **AC-US5-01**: Advanced tab renders: a select dropdown `Log level: error | warn | info | debug | trace` (default `info`), a read-only text field showing the resolved settings path (e.g., `/Users/anton/.vskill/settings.json`) with a `Copy` button, and a destructive `Reset all settings to defaults…` button
- [x] **AC-US5-02**: Changing the log level persists to `advanced.logLevel` and applies live to the running Rust process via an updated `RUST_LOG`-equivalent filter (no app restart required); takes effect within 1s
- [x] **AC-US5-03**: Clicking `Copy` writes the absolute settings path to the clipboard via `tauri-plugin-clipboard` (added to the Builder); a brief toast confirms `Copied`
- [x] **AC-US5-04**: Clicking `Reset all settings to defaults…` opens a native confirm dialog `Reset all settings? This cannot be undone.` with `Cancel` (default) and `Reset` actions; on `Reset`, the settings file is renamed to `settings.json.bak.YYYYMMDD-HHMMSS`, replaced with the default content, and the Preferences window reloads to reflect defaults
- [x] **AC-US5-05**: Reset does NOT touch the keychain (0702 KeyStore) — only the JSON settings file. A footer note in the dialog calls this out: *"API keys and other secrets stored in your system keychain are not affected."*

---

### US-006: Settings file persistence layer (P0)
**Project**: vskill

**As a** developer of Skill Studio
**I want** a single, well-tested settings persistence module that every UI tab uses uniformly
**So that** persistence bugs are caught once and fixed once, and so the wire format is stable across releases

**Acceptance Criteria**:
- [x] **AC-US6-01**: A new Rust module `settings.rs` exposes Tauri commands `get_settings() -> SettingsSnapshot`, `set_setting(path: &str, value: serde_json::Value) -> Result<()>`, and `reset_settings() -> Result<()>`, all registered on the Builder's `invoke_handler`
- [x] **AC-US6-02**: Settings file location is resolved via `dirs::home_dir()` with fallback to `dirs::config_dir()`; final path is `~/.vskill/settings.json` on macOS/Linux and `%USERPROFILE%\.vskill\settings.json` on Windows. The parent directory is created with `0700` perms on Unix on first write
- [x] **AC-US6-03**: Writes are atomic: serialize to `settings.json.tmp` in the same directory, `fsync`, then `rename` over the live file. Crash mid-write never corrupts the live file (verified by a fault-injection unit test that aborts after `fsync` but before `rename`)
- [x] **AC-US6-04**: On Unix, the settings file is created with mode `0600` (owner read/write only); if an existing file is found with a more permissive mode, it is rewritten to `0600` and a `warn`-level log line records the fix
- [x] **AC-US6-05**: On read, the JSON is validated against a schema (serde-typed `Settings` struct with `#[serde(default)]` on every field). Unknown top-level keys are preserved (round-tripped) so older binaries don't drop fields a newer binary added; unknown nested-typed values are dropped and logged as `warn`
- [x] **AC-US6-06**: On read, if the file is missing, an empty default `Settings` struct is returned and persisted on the next write — never on read alone (read remains side-effect-free)
- [x] **AC-US6-07**: On read, if the file is corrupt (invalid JSON, schema mismatch on required-typed fields), it is renamed to `settings.json.corrupt.YYYYMMDD-HHMMSS`, replaced with defaults, and a toast surfaces in the next-opened Preferences window: `Your settings file was corrupt and has been reset. The original was saved as <filename>.`
- [x] **AC-US6-08**: `set_setting(path, value)` accepts dotted paths (`general.theme`, `updates.channel`, `privacy.telemetryEnabled`, `advanced.logLevel`); invalid paths return `Err("unknown setting path: …")`. The set is debounced server-side by 250ms — rapid toggles produce a single disk write
- [x] **AC-US6-09**: Concurrent `set_setting` calls are serialized through a `tokio::sync::Mutex` on the in-memory state. The on-disk write is batched by the debouncer

---

### US-007: Wire `tauri-plugin-updater` crate (P0 — closes 0829 §0)
**Project**: vskill

**As a** release manager
**I want** the `tauri-plugin-updater` crate added to `Cargo.toml` and registered on the Builder
**So that** the auto-update config in `tauri.conf.json` is no longer dead code and v0.1.0 → v0.2.0 actually prompts users

**Acceptance Criteria**:
- [x] **AC-US7-01**: `repositories/anton-abyzov/vskill/src-tauri/Cargo.toml` `[dependencies]` includes `tauri-plugin-updater = "2"` (matches the Tauri 2 ecosystem version pinned by sibling plugins)
- [x] **AC-US7-02**: `lib.rs` registers `.plugin(tauri_plugin_updater::Builder::new().build())` in the Builder chain, positioned with the other plugin registrations
- [x] **AC-US7-03**: `cargo check --manifest-path repositories/anton-abyzov/vskill/src-tauri/Cargo.toml` passes clean with no warnings related to the new crate
- [x] **AC-US7-04**: `cargo tauri dev` boots the app without panicking on plugin registration; logs include a `tauri_plugin_updater` initialization line at `info` level
- [x] **AC-US7-05**: A vitest/integration test invokes the new `check_for_update` command against a stub manifest server (Mock Service Worker or equivalent) and verifies (a) up-to-date response, (b) update-available response with a parseable release-notes string, (c) signature mismatch response → command returns a structured `Err`
- [x] **AC-US7-06**: `grep -c PLACEHOLDER repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json` is `0` at increment closure (per 0829 §0 P0; the actual key replacement happens at release time but this increment must fail validation if the placeholder is shipped)

---

### US-008: Studio-runtime graceful degrade for browser-only users (P1)
**Project**: vskill

**As a** user running `npx vskill studio` in a plain browser (no desktop wrapper)
**I want** the same Preferences UI to render with desktop-only fields disabled and a clear callout
**So that** I understand which features require the desktop app without seeing a broken page

**Acceptance Criteria**:
- [x] **AC-US8-01**: A `useDesktopBridge()` hook detects the Tauri runtime by probing `window.__TAURI_INTERNALS__` (synchronous, set by Tauri before first paint); returns `{ available: true }` in desktop, `{ available: false }` in browser
- [x] **AC-US8-02**: When `available: false`, the General tab disables `Launch at login` and `Default project folder` (greyed out, non-interactive) and renders an inline callout: *"Install Skill Studio for desktop to enable launch at login and a default project folder."* with a link to `https://verified-skill.com/download`
- [x] **AC-US8-03**: When `available: false`, the Updates tab is replaced wholesale with a single panel: *"Updates are managed by the desktop app. You're running Skill Studio in a browser via `npx vskill studio` — visit verified-skill.com/download to install the desktop app, or run `npm i -g vskill@latest` to update the CLI."*
- [x] **AC-US8-04**: When `available: false`, the Privacy tab keeps the telemetry toggle (writes to localStorage in the browser), keeps the disclosure paragraph, but disables `Reveal log folder` (no native shell access)
- [x] **AC-US8-05**: When `available: false`, the Advanced tab disables log-level (no Rust process to apply to) and `Reset to defaults` (only resets localStorage in this mode); the settings-path field reads `Stored in this browser's local storage`
- [x] **AC-US8-06**: The `useStudioPreferences` hook (existing, localStorage) and the new `useUserSettings` hook (talks to Tauri) are unified behind a `useSettings` facade so component code is identical across both modes — e2e tests verify the General tab renders the same DOM tree with `aria-disabled` flips on the desktop-only controls

---

### US-009: Release-manager smoke test for end-to-end update flow (P0)
**Project**: vskill

**As a** release manager cutting `desktop-v0.2.0`
**I want** an automated smoke test that proves a running v0.1.0 instance sees the update prompt, installs, and relaunches on v0.2.0
**So that** I never tag a release where the auto-updater silently breaks

**Acceptance Criteria**:
- [x] **AC-US9-01**: A new Playwright spec `e2e/desktop/auto-update.spec.ts` boots the desktop app pointed at a local manifest server (separate fixture process) serving `latest.json` for `v0.1.0` and a fresh manifest for `v0.2.0`
- [x] **AC-US9-02**: The spec opens Preferences → Updates, clicks `Check for Updates`, asserts the status row reads `Update available: v0.2.0`, clicks `Install & Restart`, and waits for the app to relaunch
- [x] **AC-US9-03**: After relaunch, the spec re-opens Preferences → Updates and asserts the current version reads `0.2.0` and status is `Skill Studio is up to date.`
- [x] **AC-US9-04**: The spec runs only on `darwin-arm64` in v1 (the dev box); a follow-on increment will extend to Windows + Linux runners. The other OSes are smoke-tested manually and tracked in `LAUNCH_CHECKLIST.md`
- [x] **AC-US9-05**: A negative-path test serves a v0.2.0 manifest signed with the **wrong** minisign key; the spec asserts the install fails with status `Update signature invalid — refusing to install` and the running version stays at `0.1.0`
- [x] **AC-US9-06**: The smoke test runs in CI on a `cargo tauri build` debug bundle (not production-signed) — production signing is exercised by the existing 0829 release pipeline; this test isolates the update *flow*, not the *signing*

---

## Glossary

- **Settings file** — `~/.vskill/settings.json` on macOS/Linux, `%USERPROFILE%\.vskill\settings.json` on Windows. Single JSON document, owned by this increment, schema documented in `plan.md`.
- **Studio runtime** — the React app served by `eval-server.ts`, used both inside the desktop wrapper and standalone via `npx vskill studio`.
- **Manifest** — `latest.json` (or `beta.json`) at `https://verified-skill.com/desktop/`, served per the 0829 distribution increment, signed via minisign per `LAUNCH_CHECKLIST.md §2`.
- **`tauri-plugin-updater`** — Tauri 2 ecosystem crate that polls a manifest URL, downloads + verifies bundles via minisign, replaces the app, and triggers a relaunch. Configuration in `tauri.conf.json` already present from 0828; the crate itself is wired in by US-007.
- **`tauri-plugin-autostart`** — Tauri 2 ecosystem crate for cross-platform launch-at-login. Used by US-002.
- **0700 KeyStore** — the secrets manager from increment 0702 (cross-platform API-key storage). This increment never persists secrets outside the KeyStore.

## Open Questions

> None at PM stage — Architect (next) resolves remaining technical choices: whether `tauri-plugin-clipboard` or a Rust-native clipboard write is used (US-005 AC-04), exact log-level routing mechanism (US-005 AC-02 — `log::set_max_level` vs. env_logger reload), and the exact debounce-implementation choice for `set_setting` (US-006 AC-08 — tokio interval vs. tower-style debouncer). All such choices are bounded inside the Rust process and have no impact on user-visible AC.

## Definition of Done — v1 Known Limitations (closed 2026-05-07)

The increment ships with 56/57 ACs `[x]`. One AC and one out-of-spec edge case
are recorded as v1 polish backlog rather than blockers:

1. **AC-US3-07 (partial)** — the Skill Studio → Check for Updates… menu item
   routes through the same code path as the tab button, but the
   signature-mismatch error tag is currently a pass-through string instead of
   the structured `{ tag: "signature-mismatch", message }` shape the architecture
   plan calls for. Functional refusal-to-install works (covered by the negative-path
   e2e in T-023). The structured-error shape is queued as a v1.1 polish item.

2. **Cancel-update edge case (out of spec)** — clicking Cancel during an
   in-flight `Install & Restart` aborts the install branch, but the underlying
   `tauri-plugin-updater` download finishes on disk because the plugin gives no
   clean abort hook. The cancelled update bytes are inert (the next check
   re-downloads them), but the disk-space side effect is documented here as a v1
   limitation. A clean-abort hook is a Tauri-upstream change.

Both items are tracked in the v1 polish backlog and are not closure-blocking.
