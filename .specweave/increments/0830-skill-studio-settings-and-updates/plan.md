# 0830-skill-studio-settings-and-updates — Plan (Architecture)

**Owner**: Architect agent
**Companion**: spec.md (PM-owned, finalized 2026-05-07)
**Decision authority**: this document on HOW; spec.md on WHAT
**Related ADRs**:
- [0830-01 Preferences window architecture](../../docs/internal/architecture/adr/0830-01-preferences-window-architecture.md)
- [0830-02 Settings persistence strategy](../../docs/internal/architecture/adr/0830-02-settings-persistence-strategy.md)
- Inherits: [0828-01 Tauri framework choice](../../docs/internal/architecture/adr/0828-01-vskill-desktop-framework-choice.md), [0829-01 Updater manifest](../../docs/internal/architecture/adr/0829-01-update-manifest-hosting.md)

**Spec.md cross-ref**: AC-US1-01..06, AC-US2-01..07, AC-US3-01..08, AC-US4-01..04, AC-US5-01..05, AC-US6-01..09, AC-US7-01..06, AC-US8-01..06, AC-US9-01..06.

---

## 0. Dependencies — READ THIS FIRST

This increment **cannot ship in isolation** — it consumes inputs from 0829 that are documented but not yet in the source tree. Implementer agents must verify these gates before any task begins.

| Gate | Source | Status (2026-05-07) | Action if missing |
|---|---|---|---|
| `tauri-plugin-updater = "2"` in `src-tauri/Cargo.toml` | 0829 LAUNCH_CHECKLIST.md §0 (P0) | **MISSING** — verified by reading `src-tauri/Cargo.toml` lines 18–30. The plugin is referenced in `tauri.conf.json` `plugins.updater` but the crate itself is absent and the Builder never registers it. | This increment's US-007 closes the gap as a P0 task. **No US-002 or US-003 work can begin until US-007's T-D-01 lands.** |
| `tauri-plugin-autostart = "2"` in `src-tauri/Cargo.toml` | net-new dependency for this increment | MISSING (expected — this increment introduces it) | Added by this increment's US-002 task T-G-01. |
| `tauri-plugin-clipboard = "2"` in `src-tauri/Cargo.toml` | net-new for AC-US5-03 | MISSING (expected) | Added by US-005 task T-A-01. |
| Minisign keypair + `TAURI_SIGNING_PRIVATE_KEY` GH secret | 0829 §3.3 | Documented in 0829 LAUNCH_CHECKLIST §0; key generation runbook owned by 0829, not us | **Required for US-009's e2e signature-verification test.** If the keypair is not yet generated when 0830 starts implementation, the implementer agent uses a throwaway local keypair for the e2e test fixture and substitutes the production pubkey at release time. The throwaway pubkey is checked in at `src-tauri/test-fixtures/updater-test.pub` — never used in production. |
| `tauri.conf.json` `plugins.updater.pubkey` placeholder replaced | 0829 §0 P0 | Placeholder still present (`<MINISIGN_PUBKEY_PLACEHOLDER>` per spec inheritance section). | AC-US7-06 enforces this at increment closure; CI runs `grep -c PLACEHOLDER` and fails the gate if non-zero. Replacement is a release-time operation, not an implementation-time one. |
| `verified-skill.com/desktop/latest.json` Cloudflare Worker route | 0829 §6.4 | Routing/Worker config is owned by 0829's release pipeline. | If the route isn't live, US-009's smoke test substitutes a local manifest server (`scripts/test-fixtures/manifest-server.ts`); production e2e is gated on 0829. |

**One-line summary**: 0829 must complete LAUNCH_CHECKLIST §0 (the 5-minute Cargo.toml + Builder edit and minisign keypair generation) before 0830's release-blocking ACs can be verified. The implementation work in 0830 unblocks itself via US-007 — but the production-signed end-to-end test (AC-US9-01..05) needs the 0829 plumbing.

---

## 1. Executive Summary

Build the user-facing settings + updates surface for Skill Studio: a 4-tab native Preferences window opened from `Skill Studio → Preferences…` (⌘,), a working `Check for Updates…` flow, cross-platform launch-at-login, and a `~/.vskill/settings.json` persistence layer with atomic writes and `0600` perms.

**Architecture in one sentence**: a separate Tauri `WebviewWindow` labelled `preferences` (per [ADR 0830-01](../../docs/internal/architecture/adr/0830-01-preferences-window-architecture.md)) loads a dedicated Preferences entrypoint inside the existing `dist/eval-ui/` bundle; a new Rust `settings.rs` module (per [ADR 0830-02](../../docs/internal/architecture/adr/0830-02-settings-persistence-strategy.md)) owns `~/.vskill/settings.json` via atomic-write tmp+fsync+rename and a 250ms debouncer; `tauri-plugin-updater`, `tauri-plugin-autostart`, and `tauri-plugin-clipboard` are added to the Cargo.toml + Builder chain, and Tauri commands wrap each one for AC-traceability.

**Why this is the right shape**:
- Reuses 0828 patterns (atomic write from `lifecycle.rs`, command surface from `commands.rs`, menu wiring from `menu.rs`) — no architectural drift.
- Closes the LAUNCH_CHECKLIST §0 dead-code gap as a P0 sub-task (US-007), unblocking 0829's release pipeline.
- Single React component tree for Preferences renders identically in the desktop window and a browser-mode modal (US-008), via a `useDesktopBridge()` adapter swap. Zero duplication.
- Each tab is an independent React component reading + writing through one `useSettings` facade — implementer can parallelize across tabs in Phase 4.

**Scope of this plan**:
- Phase 1: Cargo deps + Tauri plugin registration + IPC commands skeleton (settings + updater + autostart + clipboard).
- Phase 2: `settings.rs` persistence backend (atomic write, debouncer, schema migration, perm-fix).
- Phase 3: Preferences window scaffold + tab framework + `useSettings` facade + `useDesktopBridge` runtime detect.
- Phase 4: Four tabs in parallel — General (US-002), Updates (US-003), Privacy (US-004), Advanced (US-005).
- Phase 5: Update flow state machine wiring + `Install & Restart` + signature-verification UX.
- Phase 6: Browser-mode degradation (US-008) — `aria-disabled` flips, callouts.
- Phase 7: i18n stub — every user-visible string flows through `t()`, English-only catalog ships, infra ready for future languages.
- Phase 8: Testing — Rust unit (settings.rs, command wrappers), Vitest (hooks, components), Playwright e2e (Preferences flow + auto-update smoke US-009).

---

## 2. Research Findings

### 2.1 Tauri 2 multi-window — `WebviewWindowBuilder`

Tauri 2 exposes `WebviewWindowBuilder::new(app, label, WebviewUrl::App(path))` for creating additional WKWebView/WebView2 windows ([Tauri v2 webview docs](https://v2.tauri.app/learn/window-customization/), [`WebviewWindowBuilder` Rust API](https://docs.rs/tauri/latest/tauri/webview/struct.WebviewWindowBuilder.html)). Builder methods cover everything we need: `.title()`, `.inner_size()`, `.resizable(false)`, `.center()`, `.theme()`, `.always_on_top(false)`. Capability `core:webview:allow-create-webview-window` must be in `capabilities/main.json` for the spawn to succeed at runtime — without it the call fails with a permission error ([Tauri discussion #9601](https://github.com/orgs/tauri-apps/discussions/9601)).

The `Manager::get_webview_window(label)` lookup is `O(1)` by label and is how AC-US1-04's "focus existing window" path works without state-tracking.

### 2.2 Tauri Updater plugin v2 — `check()` / `download_and_install()` / `DownloadEvent`

Verified via [Tauri v2 updater docs](https://v2.tauri.app/plugin/updater/) and [`@tauri-apps/plugin-updater`](https://v2.tauri.app/reference/javascript/updater/). Rust API surface:

```rust
use tauri_plugin_updater::UpdaterExt;

let update = app.updater()?.check().await?;     // Result<Option<Update>>
if let Some(update) = update {
    update.download_and_install(
        |chunk_length, content_length| { /* per-chunk progress */ },
        || { /* finished */ },
    ).await?;
    app.restart();                                // schedules a graceful restart
}
```

JS API surface:

```js
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

const update = await check();
if (update) {
    await update.downloadAndInstall((event) => {
        // event.event ∈ { 'Started', 'Progress', 'Finished' }
    });
    await relaunch();
}
```

`DownloadEvent` enum (Rust serialization): `Started { content_length }`, `Progress { chunk_length }`, `Finished`. Enough for our progress UI in US-003.

Config in `tauri.conf.json` is already complete from 0828/0829:
```jsonc
"plugins": {
  "updater": {
    "active": true,
    "endpoints": ["https://verified-skill.com/desktop/latest.json"],
    "dialog": false,                      // we render our own UI
    "pubkey": "<MINISIGN_PUBKEY_PLACEHOLDER>",
    "allowDowngrades": true
  }
}
```

`dialog: false` because spec AC-US3-02..03 specifies in-Preferences-window UI, not the OS-level modal Tauri ships by default.

**Signature verification cannot be disabled** ("Tauri's updater needs a signature to verify that the update is from a trusted source. This cannot be disabled."). Good — AC-US3-03 and AC-US9-05 rely on this.

### 2.3 Tauri Autostart plugin v2

Per [Tauri v2 autostart docs](https://v2.tauri.app/plugin/autostart/) and [crate docs](https://docs.rs/tauri-plugin-autostart/latest/tauri_plugin_autostart/index.html), supports macOS / Windows / Linux. macOS has two launcher modes:

- `MacosLauncher::LaunchAgent` — generates `~/Library/LaunchAgents/<bundle-id>.plist` directly. Standard, well-understood, plays well with macOS Sequoia's Login Items management (System Settings → General → Login Items). **We pick this.**
- `MacosLauncher::AppleScript` — uses Apple Events to talk to System Events / Login Items. Subject to TCC permission prompts and version-fragile across macOS releases. **Rejected.**

Init:
```rust
.plugin(tauri_plugin_autostart::init(
    MacosLauncher::LaunchAgent,
    None,    // no extra command-line args; we want the plain launch
))
```

JS API: `enable()`, `disable()`, `isEnabled()` from `@tauri-apps/plugin-autostart`. Each is a single async call to a plugin command. AC-US2-02..03 covers the toggle wiring + MDM-blocked recovery toast.

**MDM caveat**: on Apple-managed corp Macs, the Login Items API can be blocked via MDM profile; `enable()` will return `Err`. Spec AC-US2-03 spells out the recovery UX (revert toggle, toast, deeplink to System Settings). We open `x-apple.systempreferences:com.apple.LoginItems-Settings.extension` via `tauri-plugin-shell` for the deeplink.

### 2.4 Settings persistence — hand-rolled vs `tauri-plugin-store`

Decision and rationale in [ADR 0830-02](../../docs/internal/architecture/adr/0830-02-settings-persistence-strategy.md). Summary: hand-rolled wins because the plugin's auto-save model fights our debouncer (AC-US6-08), its default paths fight our `~/.vskill/` convention (AC-US6-02), and its lack of fault-injection hooks fails AC-US6-03's test requirement. The atomic-write pattern is already proven in `src-tauri/src/lifecycle.rs:128-137` — we extract it into a shared helper.

### 2.5 i18n — `react-i18next`

Per [auto18n's React i18n in 2026 comparison](https://www.auto18n.com/en/blog/react-i18n-2026), the three serious options are `react-i18next`, `react-intl` (FormatJS), and LinguiJS. We pick **`react-i18next`** for these reasons:

- **Namespace + lazy loading**: each tab loads its own namespace (`general`, `updates`, `privacy`, `advanced`) on demand. FormatJS has no namespaces — every locale is one flat object.
- **Vite-native**: dynamic `import('./locales/<lang>/<ns>.json')` works out of the box ([SimpleLocalize 2026 guide on Vite + lazy loading](https://simplelocalize.io/blog/posts/lazy-loading-resources/)).
- **Battle-tested for desktop apps with offline-first behavior**: bundles all catalogs in `dist/eval-ui/locales/` so no network required at runtime.
- **Hooks API**: `useTranslation('general')` returns `{ t }`, exactly the shape component code expects.

For v1 we ship **English-only** (`en/common.json`, `en/general.json`, `en/updates.json`, `en/privacy.json`, `en/advanced.json`). Infrastructure-only spike — no translation work in scope. Settings field `general.language` is reserved (default `auto`) but reads system locale via `navigator.language` for now and only falls back to `en`.

### 2.6 System tray (US deferral note)

Spec out-of-scope §3 confirms tray icon is OUT of v1. We do NOT load `TrayIconBuilder` in this increment. Documented here so a future implementer doesn't accidentally adopt it from a research detour.

### 2.7 Notifications

The notification plugin is already initialized (0828 plan §3.6.3). For v1 of US-003, "update available" surfaces inline in the Preferences Updates tab — **no native notification**. Reason: Preferences is an active context (the user just clicked Check for Updates); a notification would be redundant noise. We hold the notification path in reserve for the daily-poll auto-check (AC-US3-05) and surface it only when the user is unfocused — same gating logic as 0828 plan §3.6.3.

---

## 3. Architecture

### 3.1 Module + file layout

New + modified files in `repositories/anton-abyzov/vskill/`:

```
src-tauri/
├── Cargo.toml                                   ← +3 deps (updater, autostart, clipboard)
├── src/
│   ├── lib.rs                                   ← +3 plugins, +new commands, +open_preferences setup
│   ├── commands.rs                              ← +open_preferences, +get_app_metadata
│   ├── menu.rs                                  ← +Preferences item w/ ⌘, accelerator
│   ├── settings.rs                              ← NEW (per ADR 0830-02)
│   └── updater.rs                               ← NEW (wraps tauri-plugin-updater for our UX)
├── capabilities/
│   └── main.json                                ← +core:webview:allow-create-webview-window
└── tauri.conf.json                              ← already done in 0828/0829, no changes here

src/eval-ui/
├── preferences.html                             ← NEW entrypoint (multi-entry Vite)
├── vite.config.ts                               ← +rollupOptions.input.preferences
└── src/
    ├── preferences/                             ← NEW directory
    │   ├── main.tsx                             ← React mount point
    │   ├── PreferencesApp.tsx                   ← layout + tab nav
    │   ├── tabs/
    │   │   ├── GeneralTab.tsx                   ← US-002
    │   │   ├── UpdatesTab.tsx                   ← US-003
    │   │   ├── PrivacyTab.tsx                   ← US-004
    │   │   └── AdvancedTab.tsx                  ← US-005
    │   ├── locales/
    │   │   └── en/{common,general,updates,privacy,advanced}.json
    │   └── i18n.ts                              ← react-i18next bootstrap
    └── hooks/
        ├── useSettings.ts                       ← unified facade (Tauri vs localStorage)
        ├── useDesktopBridge.ts                  ← runtime detect (US-008)
        ├── useUserSettings.ts                   ← Tauri-mode adapter
        └── useStudioPreferences.ts              ← existing, kept (browser-mode adapter)
```

### 3.2 Cargo.toml additions

```toml
# (additions to existing [dependencies])
tauri-plugin-updater   = "2"      # US-007 — closes 0829 §0 dead-code
tauri-plugin-autostart = "2"      # US-002 — launch at login
tauri-plugin-clipboard-manager = "2"  # US-005 AC-US5-03 — copy settings path

# version-pin all three to "2" matching sibling plugins (dialog/shell/notification/deep-link)
# already in this file. CI's cargo-audit step is unaffected — these are first-party crates.
```

`cargo-deny` policy: tauri-apps maintainers; same trust tier as the plugins already accepted. No new advisory exposure.

### 3.3 IPC — Tauri command surface

Extends `commands.rs`. Naming follows existing `snake_case_verb_noun` pattern (`get_server_port`, `restart_server`).

| Command | Direction | Purpose | Spec AC |
|---|---|---|---|
| `open_preferences(tab: Option<String>)` | JS / menu → Rust | Open or focus the Preferences window; optionally pre-select a tab. | AC-US1-03..04, AC-US3-07 |
| `get_settings() -> SettingsSnapshot` | JS → Rust | Read `~/.vskill/settings.json` (cached after first load). | AC-US6-01 |
| `set_setting(path: String, value: serde_json::Value) -> Result<()>` | JS → Rust | Dotted-path write; debounced flush. | AC-US6-01, AC-US6-08 |
| `reset_settings() -> Result<()>` | JS → Rust | Rename live to `.bak.<ts>`, write defaults, emit `settings-reset` event. | AC-US5-04, AC-US6-01 |
| `get_app_metadata() -> AppMetadata` | JS → Rust | `{ version, target, arch, build_date, commit_sha }`. | AC-US3-01, AC-US5-01 |
| `check_for_update() -> Result<UpdateInfo, String>` | JS → Rust | Wraps `app.updater()?.check()`. | AC-US3-02, AC-US7-05 |
| `install_update_and_restart() -> Result<(), String>` | JS → Rust | Wraps `download_and_install` + `app.restart()`; serialized via mutex. | AC-US3-03, AC-US3-06 |
| `cancel_update_check()` | JS → Rust | Sets a cancellation token consulted by the in-flight check task. | implementation-only, no AC |
| `set_autostart(enabled: bool) -> Result<(), String>` | JS → Rust | `tauri-plugin-autostart::enable()`/`disable()` with error mapping. | AC-US2-02..03 |
| `is_autostart_enabled() -> bool` | JS → Rust | For first-paint sync (AC-US2-07). | AC-US2-07 |
| `set_log_level(level: String) -> Result<(), String>` | JS → Rust | Live-reconfigures `env_logger` filter via `log::set_max_level`. | AC-US5-02 |
| `pick_default_project_folder() -> Option<String>` | JS → Rust | Wraps `tauri-plugin-dialog`'s folder picker. | AC-US2-06 |
| `open_log_folder()` | JS → Rust | Already exists as `open_logs_folder` — alias for Privacy tab clarity. | AC-US4-03..04 |
| `copy_settings_path() -> Result<(), String>` | JS → Rust | Wraps `tauri-plugin-clipboard-manager::write_text`. | AC-US5-03 |

**Events emitted (Rust → JS)**:
- `settings-changed` — fires after each successful debounced disk write; payload `{ paths: string[] }`. Studio runtime subscribes to live-update its UI when another window changes settings.
- `update-check-started`, `update-progress` (`{ chunk, total }`), `update-error` (`{ message }`), `update-installed` — drive the Updates tab status row.
- `theme-changed` — fires on settings.general.theme write so main window can flip CSS `data-theme` (AC-US2-04).

### 3.4 Settings schema v1

Single `Settings` struct (Rust) ⇋ TypeScript interface (mirrored at `src/eval-ui/src/preferences/types.ts`). Schema version pinned at `1`.

```jsonc
// ~/.vskill/settings.json — wire format
{
  "version": 1,
  "general": {
    "theme": "system",                 // "system" | "light" | "dark"
    "language": "auto",                // "auto" | ISO 639-1 (e.g. "en"); v1 reserved
    "defaultProjectFolder": null,      // string | null — absolute path
    "launchAtLogin": false             // boolean — mirrored from autostart plugin state
  },
  "updates": {
    "channel": "stable",               // "stable" | "beta"
    "lastCheckedAt": null,             // ISO-8601 string | null
    "lastKnownVersion": null,          // string | null — last manifest version we observed
    "skippedVersion": null             // string | null — for skip-this-version (post-v1)
  },
  "privacy": {
    "telemetryEnabled": false          // boolean — defaults OFF (AC-US4-01)
  },
  "advanced": {
    "logLevel": "info"                 // "error" | "warn" | "info" | "debug" | "trace"
  }
}
```

**Rust mirror**:
```rust
#[derive(Serialize, Deserialize, Default, Clone, Debug)]
#[serde(default)]
pub struct Settings {
    #[serde(default = "default_version")]
    pub version: u32,
    pub general: GeneralSettings,
    pub updates: UpdateSettings,
    pub privacy: PrivacySettings,
    pub advanced: AdvancedSettings,
    #[serde(flatten)]
    pub _unknown: HashMap<String, serde_json::Value>,  // round-trip per AC-US6-05
}
```

**Migration policy**: schema version bump (`1 → 2 → ...`) handled by a function `migrate(input: serde_json::Value, from: u32) -> Settings`. v1 only — no migration code yet, but the dispatch slot exists for future increments.

### 3.5 Settings persistence — atomic-write + debouncer

Detail in ADR 0830-02. Operational shape:

1. **Load** (`SettingsStore::load()`): read file, parse JSON. On JSON-parse error → rename to `.corrupt.YYYYMMDD-HHMMSS`, return `Settings::default()` (AC-US6-07). On missing → return defaults, do NOT write yet (AC-US6-06). On success → check Unix mode; if more permissive than `0600`, rewrite file with correct mode and `warn`-level log (AC-US6-04).
2. **Get** (`SettingsStore::get()`): acquire `Mutex<Settings>` read lock, clone snapshot. Tauri command returns over IPC.
3. **Set** (`SettingsStore::set(path, value)`): validate dotted path against allow-list (`general.theme`, `general.language`, `general.defaultProjectFolder`, `general.launchAtLogin`, `updates.channel`, `updates.lastCheckedAt`, `updates.lastKnownVersion`, `privacy.telemetryEnabled`, `advanced.logLevel`); on unknown → `Err("unknown setting path: …")` (AC-US6-08). On valid → acquire lock, mutate field via `serde_json::Value::pointer_mut`, send `()` on `write_tx` channel.
4. **Debouncer** (background task, started at `load()`): `tokio::sync::mpsc::Receiver` drained every 250ms; if any signals received → atomic-write current `Settings` snapshot. Multiple sets in 250ms collapse into one disk write (AC-US6-08).
5. **Atomic write** (`atomic_write_json<T: Serialize>(path, value)`):
   ```rust
   let tmp = path.with_extension("json.tmp");
   {
       let mut file = std::fs::OpenOptions::new().create(true).write(true).truncate(true).open(&tmp)?;
       #[cfg(unix)] file.set_permissions(std::fs::Permissions::from_mode(0o600))?;
       serde_json::to_writer_pretty(&mut file, value)?;
       file.sync_all()?;                    // fsync — AC-US6-03
   }
   std::fs::rename(&tmp, path)?;            // atomic on POSIX rename(2) and Windows ReplaceFile
   ```
   Helper lives in a new `src-tauri/src/atomic_io.rs` module. `lifecycle.rs` is updated to call this helper (net code dedup).
6. **Reset** (`SettingsStore::reset()`): acquire lock, rename live file to `settings.json.bak.YYYYMMDD-HHMMSS`, write defaults atomically, emit `settings-reset` event so any open Preferences window reloads.

**Concurrency**: `Mutex<Settings>` serializes all in-memory mutations (AC-US6-09). The disk write is a single sequential task draining the channel — never concurrent.

**Fault-injection test** (AC-US6-03): under `cfg(feature = "fault-inject-write")`, the atomic-write helper inserts a `panic!("fault inject")` between `sync_all` and `rename`. Test asserts: (a) live file contents unchanged (still old version), (b) `.tmp` file may or may not exist (cleanup runs in next load).

### 3.6 Preferences window — open / focus / lifecycle

Per ADR 0830-01, separate `WebviewWindow` with label `preferences`.

```rust
// commands.rs (sketch)
#[tauri::command]
pub async fn open_preferences(app: AppHandle, tab: Option<String>) -> Result<(), String> {
    if let Some(existing) = app.get_webview_window("preferences") {
        let _ = existing.set_focus();
        if let Some(tab) = tab {
            let _ = existing.emit("preferences-select-tab", tab);
        }
        return Ok(());
    }
    let url = match tab {
        Some(t) => WebviewUrl::App(format!("preferences.html?tab={t}").into()),
        None    => WebviewUrl::App("preferences.html".into()),
    };
    WebviewWindowBuilder::new(&app, "preferences", url)
        .title("Skill Studio — Preferences")
        .inner_size(720.0, 560.0)
        .resizable(false)
        .center()
        .build()
        .map_err(|e| e.to_string())?;
    Ok(())
}
```

**Menu wiring** (replaces existing stub in `menu.rs`):
- `Skill Studio → Preferences…` (⌘,) → `open_preferences(None)` (AC-US1-01).
- `Skill Studio → Check for Updates…` → `open_preferences(Some("updates".into()))` + `emit("preferences-trigger-check")` (AC-US3-07).
- Win/Linux: `Edit → Preferences…` (Ctrl+,) (AC-US1-02). The platform branch in menu.rs uses `cfg!(target_os = "macos")` to position the item correctly.

**Lifecycle ownership** (AC-US1-05): main window's existing close handler in `lifecycle.rs` walks `app.webview_windows()` and closes the `preferences` window if present. The Preferences window's own close handler is a no-op (destruction is fine — settings are already persisted).

**Capability** (`capabilities/main.json` add):
```json
{
  "permissions": [
    "core:default",
    "core:webview:allow-create-webview-window",
    "core:webview:allow-set-webview-focus"
  ]
}
```

### 3.7 Update flow — state machine

State machine for the Updates tab. Transitions are owned by Rust (the source of truth on async progress); the JS UI is a pure projection of `UpdateStatus` events.

```
┌─────────┐  user clicks Check         ┌──────────┐
│  Idle   ├──────────────────────────► │ Checking │
└────▲────┘                             └─────┬────┘
     │                          ┌─────────────┼──────────────┐
     │                          │             │              │
     │                  no update      update available    error
     │                          │             │              │
     │                          ▼             ▼              ▼
     │                    ┌─────────┐  ┌─────────────┐  ┌────────┐
     │                    │ UpToDate│  │ UpdateReady │  │ Error  │
     │                    └────▲────┘  └──────┬──────┘  └───┬────┘
     │                         │              │             │
     │                         │   user clicks Install      │
     │                         │              │             │
     │                         │              ▼             │
     │                         │     ┌──────────────┐       │
     │                         │     │ Downloading  │       │
     │                         │     └──────┬───────┘       │
     │                         │            │               │
     │                         │   ┌────────┼───────┐       │
     │                         │  done   sig fail  net err  │
     │                         │   │        │       │       │
     │                         │   ▼        ▼       ▼       │
     │                         │ ┌──────┐ ┌────┐  ┌────────┐│
     │                         │ │ Inst │ │SigE│  │ DLErr  ││
     │                         │ └──┬───┘ └─┬──┘  └────┬───┘│
     │                         │    │       │          │    │
     │                         │    │ relaunch         │    │
     │                         │    ▼                  │    │
     │                         │  (process exits)      │    │
     │                         │                       │    │
     └─────────────────────────┴───────────────────────┴────┘
                                  user dismisses error / retries
```

**Concurrency lock** (AC-US3-06): `static INSTANCE: tokio::sync::Mutex<()> = ...`. `check_for_update` and `install_update_and_restart` both `try_lock()` — second click → no-op. JS surface: button disabled when `inflight === true`, derived from event stream.

**Persistence** (AC-US3-05, AC-US3-08): on each successful (non-error) check, `updates.lastCheckedAt` is updated via `set_setting`. On error, NOT updated — the user can retry immediately. The 24h boot-time auto-check (AC-US3-05) reads `lastCheckedAt`, computes elapsed; if >24h, runs the check in the background with no UI surface (results land in `lastKnownVersion`); next time the user opens Updates tab, the status row pre-populates from cached state.

**Channel switching** (AC-US3-04): on channel write, the Rust side re-points the updater plugin's manifest URL via `app.updater_builder().endpoints(vec![channel_url]).build()?`. For `beta` we hardcode `https://verified-skill.com/desktop/beta.json`. 404 from this endpoint → status row reads `No beta releases yet — staying on your current build.` (no error toast); the channel preference still persists.

**Signature failure** (AC-US3-03): the updater plugin returns `Err` on signature mismatch; we map this to `UpdateStatus::SigError` and write a structured entry (`{ ts, version, error }`) to `~/Library/Logs/vSkill/updater.log`. The log file is the same one the Privacy tab's "Reveal log folder" surfaces.

### 3.8 Autostart — cross-platform

Plugin init:
```rust
.plugin(tauri_plugin_autostart::init(
    MacosLauncher::LaunchAgent,
    None,
))
```

Per-platform behavior (delegated to plugin internals):
- **macOS**: `~/Library/LaunchAgents/com.verifiedskill.vskill.plist` is generated/removed by the plugin. `RunAtLoad: true` with `KeepAlive: false` (we want launch-once-at-login, not daemonize).
- **Windows**: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` registry value `vSkill` set to the install path; removed on disable.
- **Linux**: `~/.config/autostart/skillstudio.desktop` desktop entry created; removed on disable. Honors XDG.

**Tauri commands** (US-002 wrappers — keep auth + error mapping centralized):
```rust
#[tauri::command]
pub async fn set_autostart(app: AppHandle, enabled: bool) -> Result<(), String> {
    use tauri_plugin_autostart::ManagerExt;
    let manager = app.autolaunch();
    if enabled { manager.enable().map_err(|e| e.to_string())? }
    else       { manager.disable().map_err(|e| e.to_string())? }
    // mirror to settings.json so UI is consistent on next launch
    let store = app.state::<SettingsStore>();
    store.set("general.launchAtLogin", serde_json::json!(enabled)).await
        .map_err(|e| e.to_string())?;
    Ok(())
}
```

**MDM-blocked recovery** (AC-US2-03): on `Err` path, JS UI:
1. Reverts the toggle visually (stays at previous state).
2. Shows toast: `Couldn't change launch-at-login. Your administrator may have disabled this. [Open System Settings]`.
3. Click → opens `x-apple.systempreferences:com.apple.LoginItems-Settings.extension` via `tauri-plugin-shell::open()` on macOS; on Windows opens `ms-settings:startupapps`; on Linux is a no-op (no equivalent deeplink).

### 3.9 Theme propagation

Two windows now exist (main + preferences). Theme change in Preferences must take effect in both. Implementation:

1. User selects theme in General tab → `set_setting("general.theme", value)`.
2. Rust emits `settings-changed { paths: ["general.theme"] }`.
3. Both windows subscribe via `useSettings` → recompute resolved theme (`system` → `prefers-color-scheme`, else literal) → write `data-theme` attribute on `<html>`.
4. AC-US2-05 (system theme follows OS): a Tauri webview event `tauri://theme-changed` fires when OS dark mode toggles; the hook re-reads `prefers-color-scheme` and updates.

No CSS rewrites needed — existing eval-ui CSS variables already key off `data-theme` (per 0828 plan §3.6.1).

### 3.10 Browser-mode degradation (US-008)

`useDesktopBridge.ts`:
```ts
export function useDesktopBridge() {
  // Tauri 2 sets __TAURI_INTERNALS__ before first paint
  return { available: typeof window !== 'undefined'
                       && '__TAURI_INTERNALS__' in window };
}
```

`useSettings.ts` (facade):
```ts
export function useSettings() {
  const { available } = useDesktopBridge();
  return available ? useUserSettings() : useStudioPreferences();
}
```

Each tab component renders the same DOM tree; per-control `disabled={!available}` flips. The greyed-out controls show inline callouts (AC-US8-02..05). No conditional rendering of entire tabs — keeps test surface uniform (AC-US8-06: `aria-disabled` flips, identical DOM tree).

**Preferences entry in browser mode**: the studio's existing sidebar gains a new "Preferences" item (gear icon, bottom of sidebar). On click → opens a Radix-Dialog modal containing `<PreferencesApp />`. Focus trap + ESC-to-close handled by Radix Dialog. ⌘,/Ctrl+, keyboard shortcut wired via a `useKeyboardShortcut` hook so the same accelerator works in browser mode.

### 3.11 i18n bootstrap

`src/eval-ui/src/preferences/i18n.ts`:
```ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  lng: 'en',
  fallbackLng: 'en',
  ns: ['common', 'general', 'updates', 'privacy', 'advanced'],
  defaultNS: 'common',
  resources: {
    en: {
      common:   await import('./locales/en/common.json'),
      general:  await import('./locales/en/general.json'),
      updates:  await import('./locales/en/updates.json'),
      privacy:  await import('./locales/en/privacy.json'),
      advanced: await import('./locales/en/advanced.json'),
    },
  },
  interpolation: { escapeValue: false },  // React already escapes
});
```

Component usage:
```tsx
const { t } = useTranslation('general');
<label>{t('launchAtLogin.label')}</label>
<p>{t('launchAtLogin.help')}</p>
```

Catalog files are committed to git as English source of truth. A future i18n increment adds `lazyLoad` via `i18next-http-backend` and translator workflow — not in 0830 scope.

---

## 4. Visual Design Notes (frontend-design)

**Layout** (matching macOS System Settings idiom):
- 720×560 fixed. No traffic-lights customization (standard Tauri title bar).
- Left sidebar: 200px wide, vertical icon+label nav. Active tab highlighted with brand accent (Studio Remotion colors per project memory `project_video_brand_decisions_2026_04`).
- Right pane: 520px wide, content area with subtle 1px divider above bottom toolbar.
- Bottom toolbar: optional `Reset` / `Done` buttons per tab — but most tabs have no toolbar; settings persist on change (no Save button).
- Content padding: 24px horizontal, 20px vertical.

**Form controls** (cross-platform, but visually adapted):
- Toggle: macOS native-feeling (rounded pill, slide animation). Library: Radix `<Switch />` styled with CSS — works on all platforms.
- Segmented control (theme picker): three buttons, single-select, accent on selected.
- Folder picker: read-only text field + "Browse…" button → invokes `pick_default_project_folder` Tauri command.
- Select dropdowns (channel, log level): Radix `<Select />` for accessible keyboard nav.
- Buttons: primary (filled) for `Check for Updates`, `Install & Restart`; secondary (outline) for `Reset`; destructive (red) for `Reset all settings`.

**Accent color**: the studio remotion brand accent (per project memory) — propagated via CSS custom property `--accent`.

**Accessibility** (NFR alignment with 0828 NFR-07):
- Every interactive control has an `aria-label` or wraps a `<label htmlFor>`.
- Tab navigation order matches visual order.
- Sections navigable via ⌘1/2/3/4 (Cmd+digit on macOS, Ctrl+digit elsewhere).
- Disabled controls in browser mode use `aria-disabled="true"` + `tabindex="-1"`, not `disabled` attribute, so screen readers announce them.
- Update status row uses `role="status"` (polite) so VoiceOver announces transitions without interrupting.

**Wireframes** (text-only, intentionally — no PNGs):

```
┌─ Skill Studio — Preferences ──────────────────────────  ◯ ◯ ◯ ┐
│                                                                │
│  ┌────────────┐  ┌──────────────────────────────────────────┐ │
│  │ ◐ General  │  │  Theme              [System] Light Dark  │ │
│  │   Updates  │  │                                          │ │
│  │   Privacy  │  │  Default project folder                  │ │
│  │   Advanced │  │  /Users/anton/projects        [Browse…]  │ │
│  │            │  │                                          │ │
│  │            │  │  ☐  Launch Skill Studio at login         │ │
│  │            │  │     System Settings can override this    │ │
│  └────────────┘  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

```
Updates tab:
┌────────────────────────────────────────────────────┐
│  Current version    0.1.0                          │
│  Latest version     0.2.0                          │
│  Last checked       Today at 3:42 PM               │
│  Channel            ( • ) Stable   ( ) Beta        │
│                                                    │
│  ┌────────────────┐  ┌────────────────────┐       │
│  │Check for Update│  │Install & Restart   │       │
│  └────────────────┘  └────────────────────┘       │
│                                                    │
│  Update available: 0.2.0                          │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔               │
│  ## Release notes                                  │
│  - Adds preferences window                         │
│  - Fixes restart-on-update                         │
│  - …                                               │
└────────────────────────────────────────────────────┘
```

---

## 5. Implementation Phases

Decomposition for downstream `sw-planner` agent. Phases 4 and 5 can parallelize across sub-agents (one per tab for Phase 4; updater module is independent for Phase 5).

### Phase 1 — Cargo deps + plugin registration + IPC skeleton (US-007 + scaffolding)

**Goal**: `cargo check` passes with new deps, `cargo tauri dev` boots, all command stubs return placeholder data.
**Spec ACs**: AC-US7-01..04 (P0 — closes 0829 §0).

Tasks:
- T-D-01: Add `tauri-plugin-updater = "2"`, `tauri-plugin-autostart = "2"`, `tauri-plugin-clipboard-manager = "2"` to `Cargo.toml`.
- T-D-02: Register all three plugins in `lib.rs` Builder chain. Plugin order: existing plugins → updater → autostart → clipboard.
- T-D-03: Add `core:webview:allow-create-webview-window` and `core:webview:allow-set-webview-focus` to `capabilities/main.json`.
- T-D-04: Stub all new Tauri commands (returning `Ok(())` or `Err("not implemented")`) and register them in `invoke_handler`.
- T-D-05: `cargo check` + `cargo clippy` clean.
- T-D-06: `cargo tauri dev` launches without panic; logs include all three plugin init lines.

**Exit**: dead-code gap closed; commands callable from JS; nothing user-visible yet.

### Phase 2 — `settings.rs` persistence backend (US-006)

**Spec ACs**: AC-US6-01..09.

Tasks:
- T-S-01: New module `src-tauri/src/atomic_io.rs` with `atomic_write_json<T: Serialize>(path, value)` (fsync between write and rename).
- T-S-02: Refactor `lifecycle.rs` to use `atomic_write_json` (net code dedup).
- T-S-03: New module `src-tauri/src/settings.rs` with `Settings` struct (mirrored from §3.4), `SettingsStore::load/get/set/reset`, `0600` perm enforcement on Unix, corrupt-file recovery.
- T-S-04: Background debouncer task (250ms tick, drains `mpsc::Receiver`).
- T-S-05: `SettingsStore` registered as `app.manage(...)` so commands access it via `State<SettingsStore>`.
- T-S-06: Wire `get_settings`, `set_setting`, `reset_settings` Tauri commands.
- T-S-07: Unit tests:
  - load missing → defaults
  - load corrupt → recovery rename + defaults
  - load with mode 0644 → rewrite to 0600 + warn log
  - round-trip unknown top-level key
  - debouncer collapses 10 sets into 1 disk write
  - concurrent `set_setting` calls serialize correctly
  - reset preserves keychain (no calls to KeyStore made)
  - dotted-path validation rejects unknown paths
  - **fault-injection**: panic between fsync and rename → live file unchanged (cfg-flag test).

**Exit**: `cargo test settings` all green; no JS UI yet.

### Phase 3 — Preferences window scaffold + tab framework + hooks

**Spec ACs**: AC-US1-01..06, AC-US8-01..06.

Tasks:
- T-W-01: New entrypoint `src/eval-ui/preferences.html` + `src/eval-ui/src/preferences/main.tsx`.
- T-W-02: `vite.config.ts` multi-entry update (`rollupOptions.input: { main: ..., preferences: ... }`).
- T-W-03: `PreferencesApp.tsx` — sidebar nav, tab routing via URL `?tab=` query, ⌘1..4 shortcuts.
- T-W-04: `open_preferences` Tauri command (Rust) + JS `openPreferences()` helper.
- T-W-05: Menu wiring — `Skill Studio → Preferences…` (⌘,) + `Edit → Preferences…` (Ctrl+,) on Win/Linux.
- T-W-06: `useDesktopBridge.ts` hook (probes `window.__TAURI_INTERNALS__`).
- T-W-07: `useSettings.ts` facade + `useUserSettings.ts` adapter (Tauri-side).
- T-W-08: Browser-mode modal route — sidebar gear icon → Radix Dialog wraps `<PreferencesApp />`.
- T-W-09: Theme propagation wiring (`settings-changed` event → `data-theme` on `<html>` in both windows).
- T-W-10: `i18n.ts` bootstrap + English-only catalog files for `common.json`.
- T-W-11: Playwright e2e: open Preferences from menu → assert window appears with title/size/non-resizable; second invocation focuses existing.
- T-W-12: First-paint timing test (AC-US1-06): assert `<200ms` from menu click to first content paint.

**Exit**: empty Preferences window opens via menu, first paint < 200 ms, browser-mode modal works.

### Phase 4 — Four tabs in PARALLEL (US-002, US-003, US-004, US-005)

Each tab is a separate sub-agent's responsibility. Independent React components reading + writing through the unified `useSettings`. No cross-tab coupling.

**Phase 4a — General tab (US-002)** — `GeneralTab.tsx`. Spec ACs: AC-US2-01..07.
- T-G-01: Render Theme segmented control + Folder picker + Launch-at-login toggle.
- T-G-02: Wire `set_autostart` Tauri command + MDM-blocked recovery toast.
- T-G-03: Wire `pick_default_project_folder` (existing dialog plugin).
- T-G-04: Theme live-update verification (system mode tracks OS toggle).
- T-G-05: First-paint values read synchronously (AC-US2-07).
- T-G-06: Vitest: hook coverage for autostart toggle including error path.

**Phase 4b — Updates tab (US-003)** — `UpdatesTab.tsx` + `src-tauri/src/updater.rs`. Spec ACs: AC-US3-01..08.
- T-U-01: `updater.rs` module wrapping `tauri-plugin-updater` with our state machine + serialization mutex.
- T-U-02: `check_for_update` + `install_update_and_restart` Tauri commands.
- T-U-03: Channel switch → re-point updater endpoints.
- T-U-04: 24h boot-time background check (AC-US3-05).
- T-U-05: Updates tab UI — current/latest/last-checked rows, status row, channel selector, primary button + secondary install button, scrollable release notes.
- T-U-06: Menu `Check for Updates…` opens Preferences on Updates tab + triggers check (AC-US3-07).
- T-U-07: 404-on-beta → "no beta releases yet" status (no toast).
- T-U-08: Vitest: `useUpdater` hook handles all 5 states (Idle/Checking/UpToDate/UpdateReady/Error) and 3 error sub-states (sig fail, dl fail, manifest 404).
- T-U-09: Playwright e2e (subset of US-009 — full e2e in Phase 8).

**Phase 4c — Privacy tab (US-004)** — `PrivacyTab.tsx`. Spec ACs: AC-US4-01..04.
- T-P-01: Render telemetry checkbox + disclosure paragraph + Reveal Log Folder button.
- T-P-02: Wire `open_log_folder` + create-on-missing logic.
- T-P-03: Vitest: telemetry toggle persists; reveal opens correct path per platform.

**Phase 4d — Advanced tab (US-005)** — `AdvancedTab.tsx`. Spec ACs: AC-US5-01..05.
- T-A-01: Render log-level select + settings-path read-only field + Copy button + Reset button.
- T-A-02: Wire `set_log_level` (live-reconfigure `env_logger`).
- T-A-03: Wire `copy_settings_path` via clipboard plugin.
- T-A-04: Wire `reset_settings` with native confirm dialog.
- T-A-05: Vitest: log-level applies live; reset preserves keychain (mock `KeyStore`).

**Exit**: all 4 tabs functional in desktop mode; settings round-trip through `~/.vskill/settings.json`.

### Phase 5 — Browser-mode degradation (US-008)

Already mostly handled by Phase 3's adapter design. Phase 5 verifies and fills gaps.

**Spec ACs**: AC-US8-01..06.

Tasks:
- T-B-01: Sidebar gear icon → Radix Dialog with focus trap + ESC handling.
- T-B-02: `aria-disabled` flips on desktop-only controls per tab.
- T-B-03: Inline callouts for greyed-out fields (General, Updates wholesale-replaced, Privacy, Advanced).
- T-B-04: Settings-path field reads `Stored in this browser's local storage` (AC-US8-05).
- T-B-05: e2e: open studio in browser → verify Preferences modal opens, tabs render, desktop-only controls greyed.

**Exit**: identical Preferences UI in browser-mode `npx vskill studio`.

### Phase 6 — Release-manager smoke test (US-009)

**Spec ACs**: AC-US9-01..06.

Tasks:
- T-R-01: New e2e fixture `e2e/fixtures/manifest-server.ts` — local HTTP server serving `latest.json` for v0.1.0 and v0.2.0.
- T-R-02: New e2e fixture: build two debug bundles (`vskill-test-v0.1.0`, `vskill-test-v0.2.0`) with throwaway minisign keys.
- T-R-03: `e2e/desktop/auto-update.spec.ts` — full e2e per AC-US9-01..06.
- T-R-04: Negative-path: wrong-key signed v0.2.0 → assert install fails, version stays at 0.1.0, `updater.log` line written.
- T-R-05: CI integration: runs only on `darwin-arm64` runner in v1; manual smoke on win/linux tracked in `LAUNCH_CHECKLIST.md`.

**Exit**: full e2e signs off the auto-update flow before any production release.

### Phase 7 — Documentation + i18n catalog finalize

**Spec ACs**: none directly; supports overall NFR-fitness.

Tasks:
- T-X-01: English locale catalogs (`general.json`, `updates.json`, `privacy.json`, `advanced.json`) — every user-visible string from §3 wireframes.
- T-X-02: Update `repositories/anton-abyzov/vskill/README.md` with Preferences walkthrough.
- T-X-03: Update `LAUNCH_CHECKLIST.md` §0 to mark `tauri-plugin-updater` wired (no longer a P0 gap).
- T-X-04: Living docs sync — `.specweave/docs/internal/specs/*.md` updated for the new settings module + Preferences UI.

### Phase 8 — Final test pass + closure

**Spec ACs**: full coverage verification.

Tasks:
- T-Z-01: Full test suite: `cargo test`, `cargo clippy`, `npm test`, `npx playwright test`.
- T-Z-02: AC traceability spreadsheet — every AC-USn-mm cited by ≥1 task; CI script asserts no orphans.
- T-Z-03: AC-US7-06 verification: `grep -c PLACEHOLDER repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json` returns 0 OR is waived because release-time substitution hasn't happened (decision documented in increment closure notes).
- T-Z-04: `code-review` agent + `simplify` + `grill` quality gates per project policy.

---

## 6. Risk Register

PM spec gave us no risks; architect adds:

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-A1 | `tauri-plugin-updater` crate prerequisite (0829 §0 P0 gap) | High (already known) | This increment cannot ship without it | US-007 (T-D-01..06) closes the gap as P0 task in Phase 1 — we don't depend on 0829 to land it; we land it ourselves. |
| R-A2 | Tauri 2 single-instance plugin re-focuses MAIN window when a 2nd app launch happens, but Preferences is a separate window — second-launch behavior with Preferences open is undefined | Medium | UX glitch (Preferences may stay focused while user expected main) | Test: open Preferences, run `vskill` again from terminal. Document expected behavior: main window comes forward, Preferences window stays where it is (unfocused). Add e2e test if behavior diverges. |
| R-A3 | macOS Sequoia (15.x) Login Items API changes | Low | Autostart silently fails on newest macOS | tauri-plugin-autostart wraps `~/Library/LaunchAgents/...plist` directly — Sequoia's System Settings → Login Items reads from this path. Verified compatible. Manual smoke test on Sequoia before release. |
| R-A4 | Settings file race during atomic write (process killed between fsync and rename) | Low | tmp file orphans, but live file safe | Atomic-write design guarantees live file is unchanged. On next load, orphan `settings.json.tmp` is detected and deleted (housekeeping). Fault-injection test in T-S-07. |
| R-A5 | Update flow during long-running operation in studio (e.g., skill install in progress) | Medium | User clicks Install & Restart mid-operation, loses work | v1: button is enabled regardless. Acceptable because studio operations are transactional (skill install commits before the long-running phase). Future enhancement: studio runtime exposes `/api/busy` flag; updater consults before allowing install. Tracked as a follow-on idea, not blocking. |
| R-A6 | Two webview windows × WKWebView memory cost | Medium | Memory budget per 0828 NFR-03 (<250 MB combined) tightened | Preferences window destroyed on close (not hidden), so memory is reclaimed when not in use. Idle delta ≈ 0. Active delta when open ≈ +30 MB peak — within budget. |
| R-A7 | i18n bootstrap delays first paint | Low | AC-US1-06 (200ms) miss | English-only v1 ships catalogs as static imports (synchronous, in-bundle), not async loads. First paint unaffected. Async loading is a Phase 7 follow-on increment concern. |
| R-A8 | `tauri-plugin-clipboard-manager` Linux platform fragility (Wayland vs X11) | Low | Copy button silent failure on Wayland | Plugin uses `xclip`/`xsel`/`wl-copy` per environment; native enough for v1. Spec AC-US5-03's toast appears regardless — user can verify via paste. Document caveat in Linux release notes. |
| R-A9 | Capability misconfiguration → `WebviewWindowBuilder::build()` fails at runtime with permission denied | Medium | Preferences won't open on production builds | T-D-03 explicitly adds capabilities; e2e in T-W-11 catches before release. |
| R-A10 | 24h boot-time background update check (AC-US3-05) introduces network call on cold launch | Low | Cold launch budget (NFR-01 from 0828: <1.5s) impacted | Background check runs on a separate `tokio::spawn` after the main window paints. Zero impact on cold-launch timing. Verified by 0828 cold-launch test, unchanged here. |
| R-A11 | Settings `version` field future-incompatibility — older binary opens settings written by newer binary, unknown nested keys are dropped per AC-US6-05 | Medium | Silent setting loss on downgrade | We surface a `warn`-level log line for each dropped key (AC-US6-05). v2 plan: emit a notification to user if downgrade detected. Out of v1 scope. |
| R-A12 | Tauri capability for `core:webview:allow-create-webview-window` is a security-sensitive grant — any future webview open call works | Low | Privilege creep | Only one call site (`open_preferences`); added a comment in `commands.rs` warning future contributors. Capability surface reviewed in code-review gate. |

---

## 7. Open Questions

PM spec said "none at PM stage". Architect resolves bounded technical choices:

- **OQ-A1: Clipboard mechanism** (US-005 AC-US5-03) → resolved: `tauri-plugin-clipboard-manager`. Reason: cross-platform parity, Wayland support out-of-the-box. Cargo dep: `tauri-plugin-clipboard-manager = "2"`. JS: `@tauri-apps/plugin-clipboard-manager`.

- **OQ-A2: Log-level live reload** (US-005 AC-US5-02) → resolved: `env_logger`'s `Builder::filter_level` cannot be re-applied after `init()`, but `log::set_max_level(level)` on the global facade does take effect immediately for any `log!()` call. We use `log::set_max_level` for the live update; the `env_logger` filter remains as the floor (so trace logs aren't actually emitted unless `RUST_LOG` was permissive on startup). Acceptable for v1: most users want to bump to `debug` from `info`, both within env_logger's default filter.

- **OQ-A3: Debouncer implementation** (US-006 AC-US6-08) → resolved: `tokio::sync::mpsc::Receiver` + `tokio::time::interval(250ms)`. The interval task drains the channel, writes if any signals received in the window, restarts the interval. Self-rate-limits to one disk write per 250ms regardless of `set_setting` cadence. Simpler than tower-style debouncers for our needs.

- **OQ-A4: Settings cache invalidation across windows** → resolved: the `settings-changed` event (Rust → JS, broadcasts to all windows) plus a 50ms post-event re-fetch in each window's `useSettings` hook. Belt-and-suspenders against any race between two windows toggling the same setting concurrently. (Single-instance plugin already prevents two app instances; this only matters between main + preferences within one app instance.)

- **OQ-A5: AC-US7-06 PLACEHOLDER enforcement timing** — when does the placeholder check fail? At every PR? At increment closure? → resolved: at increment closure only. Implementation can land with placeholder; release pipeline (0829) substitutes the real key. A pre-merge CI check would block normal development.

- **OQ-A6: System theme tracking on Linux** (AC-US2-05) — Linux desktops vary on dark-mode signaling. → resolved: read `gsettings get org.gnome.desktop.interface color-scheme` for GNOME; fall back to `prefers-color-scheme` from the webview (which respects FreeDesktop portal on most modern distros). KDE Plasma uses a different mechanism — accept that "system" mode on KDE may not track live OS theme changes; user can manually select Light/Dark. Documented caveat for Linux release notes.

---

## 8. Contract Summary (for downstream agents)

**Implementer must NOT change**:
- `tauri.conf.json` `plugins.updater.endpoints` URL — owned by 0829 release pipeline.
- `tauri.conf.json` `plugins.updater.pubkey` placeholder substitution — release-time only.
- Existing `commands::open_logs_folder`, `commands::quit`, `commands::restart_server`, `commands::get_server_port` signatures — referenced by JS in 0828 + this increment.
- `~/.vskill/desktop-window-state.json` schema — 0828's surface, lifecycle.rs ownership.
- `~/.vskill/workspace.json` schema — 0828's surface.
- `eval-server.ts` boot-preflight import order — 0828 contract.
- `KeyStore` from 0702 — settings.json never persists secrets (AC-US5-05).

**Implementer MUST add**:
- `src-tauri/Cargo.toml` deps: `tauri-plugin-updater = "2"`, `tauri-plugin-autostart = "2"`, `tauri-plugin-clipboard-manager = "2"`.
- `src-tauri/capabilities/main.json`: `core:webview:allow-create-webview-window` and `core:webview:allow-set-webview-focus`.
- `src-tauri/src/atomic_io.rs` (new) — `atomic_write_json<T: Serialize>` helper.
- `src-tauri/src/settings.rs` (new) — `Settings` struct, `SettingsStore`, debouncer.
- `src-tauri/src/updater.rs` (new) — wrappers around `tauri-plugin-updater` with state machine + mutex.
- `src/eval-ui/preferences.html` (new entrypoint).
- `src/eval-ui/src/preferences/` (new directory tree per §3.1).
- `src/eval-ui/src/hooks/{useSettings,useDesktopBridge,useUserSettings}.ts` (new).
- `vite.config.ts` multi-entry update.
- New Tauri commands: `open_preferences`, `get_settings`, `set_setting`, `reset_settings`, `get_app_metadata`, `check_for_update`, `install_update_and_restart`, `cancel_update_check`, `set_autostart`, `is_autostart_enabled`, `set_log_level`, `pick_default_project_folder`, `copy_settings_path`.
- New events (Rust → JS): `settings-changed`, `settings-reset`, `update-check-started`, `update-progress`, `update-error`, `update-installed`, `theme-changed`, `preferences-select-tab`, `preferences-trigger-check`.
- Refactor `lifecycle.rs` to use new `atomic_write_json` helper (net code dedup).
- Replace `menu.rs`'s `check_for_updates` stub with `open_preferences("updates")` + check trigger.

**Test budget gates**:
- Preferences first paint < 200 ms (AC-US1-06) — Playwright timer.
- Settings write debounced to ≤1 disk write per 250ms window (AC-US6-08) — Rust unit test.
- Atomic-write fault injection: live file unchanged on simulated crash between fsync and rename (AC-US6-03) — Rust unit test (cfg-flag).
- Auto-update e2e on darwin-arm64: vN-1 → vN flow under 60 s (AC-US9-02..03) — Playwright spec.
- Signature-mismatch negative path: install refused, log entry written, version stays at vN-1 (AC-US9-05) — Playwright spec.
- Coverage target: 90% per metadata.json.

---

## 9. References

- Spec.md (this increment): `.specweave/increments/0830-skill-studio-settings-and-updates/spec.md`
- ADR 0830-01: Preferences window architecture
- ADR 0830-02: Settings persistence strategy
- 0828 plan.md (parent: desktop shell baseline)
- 0829 plan.md (parent: distribution + LAUNCH_CHECKLIST §0 inheritance)
- [Tauri v2 — webview windows](https://v2.tauri.app/learn/window-customization/)
- [Tauri v2 Updater plugin](https://v2.tauri.app/plugin/updater/)
- [Tauri v2 Autostart plugin](https://v2.tauri.app/plugin/autostart/)
- [Tauri v2 Store plugin](https://v2.tauri.app/plugin/store/) — rejected per ADR 0830-02
- [`WebviewWindowBuilder` Rust API](https://docs.rs/tauri/latest/tauri/webview/struct.WebviewWindowBuilder.html)
- [react-i18next 2026 comparison](https://www.auto18n.com/en/blog/react-i18n-2026)
- [Vite + i18next lazy loading guide](https://simplelocalize.io/blog/posts/lazy-loading-resources/)
- macOS HIG — App menu (Preferences position, ⌘, accelerator)
