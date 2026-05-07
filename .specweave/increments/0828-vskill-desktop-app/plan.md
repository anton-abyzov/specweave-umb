# 0828-vskill-desktop-app — Plan (Architecture)

**Owner**: Architect agent
**Companion**: spec.md (PM-owned, finalized 2026-05-07)
**Decision authority**: this document on HOW; spec.md on WHAT
**Related ADR**: [0828-01 vskill Desktop framework choice](../../docs/internal/architecture/adr/0828-01-vskill-desktop-framework-choice.md)
**Spec.md cross-ref**: AC-US01-01..05, AC-US02-01..07, AC-US03-01..06, AC-US04-01..06, AC-US05-01..05, AC-US06-01..06, AC-US07-01..08, AC-US08-01..07, AC-US09-01..05, AC-US10-01..05, AC-US11-01..05, AC-US12-01..05; NFR-01..15

---

## 1. Executive Summary

Ship `vskill.app` — a native desktop wrapper around the existing `npx vskill studio` experience, available as a `.dmg` (macOS), `.msix` (Windows, P1), and `brew install --cask vskill`.

**Architecture in one sentence**: Tauri 2 Rust shell + system WebView (WKWebView/WebView2) + the existing Node `eval-server` running as a sidecar child process; the WebView loads `http://127.0.0.1:<dynamic-port>/`, which is the **same URL today's browser tab loads**. Zero studio UI duplication.

**Why this works**: today's `npx vskill studio` already separates UI (React bundle in `dist/eval-ui/`) from runtime (Node server in `dist/eval-server/`). The desktop app bundles both untouched and adds native chrome — Dock icon, menu bar, deep-link `vskill://`, auto-update, signed installer.

**Scope of this plan**:
- Phase 1: macOS skeleton (signed `.dmg`, sidecar boot, native menu bar, log viewer).
- Phase 2: Auto-update, deep-link, crash recovery.
- Phase 3: Homebrew Cask + GA.
- Phase 4: Windows port (`.msix`, WebView2 bootstrapper).

---

## 2. Research Findings

### 2.1 Codex Desktop (the user's reference point)

OpenAI's official Codex CLI (Rust-based, [github.com/openai/codex](https://github.com/openai/codex)) ships a desktop app via `codex app`, available on macOS and Windows with binary releases on GitHub. The CLI itself is open source; the desktop wrapper's source isn't fully public, but the closest community analogue is [`codex-desktop-linux`](https://github.com/ilysenko/codex-desktop-linux), which auto-installs the Codex CLI using a bundled managed Node.js runtime — exactly the sidecar pattern we want.

Pattern takeaway: **wrap an existing CLI process in a small native binary, ship as a real `.app` bundle, distribute via GitHub Releases**.

### 2.2 Top-tier macOS app comparison

| App | Framework | Why it feels native |
|---|---|---|
| **Linear** | Electron | Same Cmd-Tab parity as native; tight keyboard shortcuts; no obvious "web tab" smell. Auto-update via electron-updater + GitHub Releases. |
| **Raycast** | Native (Swift + React extension layer) | Sub-100ms cold launch. Native NSWindow, NSViewRepresentable for extension UI. Highest bar in the category. |
| **Warp** | Native Rust + Metal | Custom GPU renderer for the terminal grid. Out of scope for our wrap-the-web pattern. |
| **Cursor** | Electron, VS Code fork | Inherits VS Code's autoUpdater + Squirrel ([Cursor architecture](https://medium.com/data-science-collective/how-cursor-actually-works-c0702d5d91a9)). Necessary because they needed editor-pipeline access. |
| **ChatGPT macOS** | Native SwiftUI + WKWebView | Wraps web with native chrome. Mac-only; no Windows. |
| **Claude desktop** | Electron | Comparable wrapping pattern; ~150 MB installer. |

The two patterns relevant to us are **Linear/Claude (Electron wrap-the-web)** and **ChatGPT (SwiftUI+WKWebView wrap)**. We pick a third: **Tauri 2 wrap-the-web + Node sidecar** — gets us the small binary of native, the cross-platform reach of Electron, and zero studio UI rework.

### 2.3 Framework decision matrix

| Framework | Binary size | Cross-platform | DX (TS/Node reuse) | Native feel | Code signing | Auto-update | Verdict |
|---|---|---|---|---|---|---|---|
| **Tauri 2** | **~10 MB** | mac+win+linux | sidecar binary; Node reused as-is | system WebView = native | mature ([tauri-action](https://v2.tauri.app/distribute/pipelines/github/)) | built-in, signed manifest | **chosen** |
| Electron | 80–200 MB | mac+win+linux | direct require() | feels native enough | mature (`electron-builder`) | mature (`electron-updater`) | rejected — too heavy for "load a localhost URL" |
| Wails | ~15 MB | mac+win+linux | Go backend; doesn't reuse Node | system WebView | manual | basic | rejected — no Go expertise |
| SwiftUI + WKWebView | ~5 MB | mac only | wrap as a sidecar binary | gold-standard | Apple Dev only | Sparkle 2 | rejected — Mac-only, doubles maintenance |

Sources: [PkgPulse 2026 benchmarks](https://www.pkgpulse.com/blog/best-desktop-app-frameworks-2026), [tech-insider 96% smaller benchmark](https://tech-insider.org/tauri-vs-electron-2026/), [Hopp Tauri vs Electron real-world](https://www.gethopp.app/blog/tauri-vs-electron).

Cold launch: Tauri ~0.4 s vs Electron ~1.5 s in published benchmarks ([raftlabs comparison](https://raftlabs.medium.com/tauri-vs-electron-a-practical-guide-to-picking-the-right-framework-5df80e360f26)).

### 2.4 Node sidecar bundling

Two options, evaluated for v1:

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **Stock Node binary + `dist/eval-server/*.js` resources** | Simplest. Zero changes to current build. Single source of truth. | Node ~80 MB on disk (~30 MB compressed in `.dmg`). | **v1 — chosen** |
| Node SEA ([`--build-sea`](https://nodejs.org/api/single-executable-applications.html), Node 25.5+) | Single binary per platform; nothing else on disk. | SEA cross-arch needs Docker matrix; `useCodeCache`/`useSnapshot` must be `false` for cross-arch. Still stabilizing in Node 25. | v2 evaluation when Node 26 LTS lands |
| `pkg`/`bun build --compile` | Battle-tested | `pkg` is unmaintained as of late 2025; `bun build --compile` requires switching runtime. | rejected |

Reference: [Tauri Node-as-sidecar guide](https://v2.tauri.app/learn/sidecar-nodejs/), [Vercel Next.js inside Tauri sidecar](https://github.com/vercel/next.js/discussions/90982), [Evil Martians sidecar deep-dive](https://evilmartians.com/chronicles/making-desktop-apps-with-revved-up-potential-rust-tauri-sidecar).

### 2.5 Code signing & notarization

**macOS**:
- Apple Developer ID Application certificate ($99/yr Apple Developer Program).
- Hardened runtime + minimal entitlements (network client only; no JIT, no DYLD overrides).
- Notarize via [`xcrun notarytool submit --wait`](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution), staple with `xcrun stapler staple`.
- ~~`altool`~~ — Apple deprecated; must use `notarytool` (Xcode 14+).
- 2026 caveat: notarization queue [stalled in February 2026 for >16 hours on some submissions](https://developer.apple.com/forums/topics/code-signing-topic/code-signing-topic-notarization). Mitigation: nightly dry-run on `main` to detect drift before release day.
- Tauri-action wraps the whole flow: `APPLE_ID`, `APPLE_PASSWORD` (app-specific password), `APPLE_TEAM_ID`, `APPLE_CERTIFICATE` (base64 .p12), `APPLE_CERTIFICATE_PASSWORD`.

**Windows** (P1):
- OV code-signing certificate (~$200/yr — DigiCert, Sectigo). EV no longer bypasses SmartScreen as of [2024 Trusted Root Program update](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation), so OV is sufficient and cheaper.
- Sign with `osslsigncode` (CI-friendly, no Windows required) or `signtool` (Windows-native).
- Reputation accrues with downloads regardless of cert tier — initial users will see "unknown publisher" briefly.
- Microsoft Store + MSIX path: free re-signing if we publish through Store. Worth evaluating for v2.
- CA/Browser Forum [458-day max validity from March 2026](https://www.advancedinstaller.com/ev-code-signing-vs-regular-code-signing.html) — plan for annual renewal.

### 2.6 Auto-update

[Tauri Updater plugin](https://v2.tauri.app/plugin/updater/) with **static signed manifest**:

```json
{
  "version": "1.2.0",
  "notes": "Bug fixes and improvements",
  "pub_date": "2026-05-15T12:00:00Z",
  "platforms": {
    "darwin-aarch64": {
      "signature": "<minisign sig>",
      "url": "https://verified-skill.com/desktop/v1.2.0/vskill_1.2.0_aarch64.app.tar.gz"
    },
    "darwin-x86_64": { "signature": "...", "url": "..." },
    "windows-x86_64": { "signature": "...", "url": "..." }
  }
}
```

Manifest URL: `https://verified-skill.com/desktop/latest.json` (Cloudflare Worker, R2-backed). Private key in 1Password + GitHub Actions secret `TAURI_UPDATER_PRIVATE_KEY`. Public key embedded in `tauri.conf.json` — losing the private key means losing the ability to ship updates to existing installs (mitigation: backup in 1Password Family vault).

Update channel: `stable` only for v1; `beta` channel via second manifest URL added in v2.

### 2.7 Distribution channels

| Channel | v1 | Cost | Notes |
|---|---|---|---|
| Direct `.dmg` from verified-skill.com | yes | $0 (R2) | Signed + notarized. Primary download path. |
| Homebrew Cask | yes | $0 | Auto-PR via [`brew bump-cask-pr`](https://docs.brew.sh/How-To-Open-a-Homebrew-Pull-Request) GitHub Action. Cask declares `auto_updates true` so brew defers to Tauri's in-app updater. |
| Mac App Store | no | $99/yr (already have) | Requires sandbox — eval-server's `~/.vskill/`, native modules (`@napi-rs/keyring`), spawning child Node process all conflict. Out of scope. |
| Windows direct `.msix`/`.exe` | P1 | OV cert ~$200/yr | Embedded WebView2 Bootstrapper (+1.8 MB, internet on first run). |
| winget | P1 | $0 | Manifest PR to [winget-pkgs](https://github.com/microsoft/winget-pkgs). |
| Microsoft Store (MSIX) | P2 | $19 once | Free re-signing; auto-updates via Store. |

### 2.8 Risks identified by research

- **Apple notary outages** — mitigation: nightly dry-run.
- **macOS WebDriver gap** — `tauri-driver` only supports Windows + Linux ([Tauri WebDriver docs](https://v2.tauri.app/develop/tests/webdriver/)). Mitigation: AppleScript smoke + Playwright against eval-server HTTP.
- **WebView2 missing on older Windows** — mitigation: `embedBootstrapper` install mode.
- **Single-instance + deep-link race on Windows/Linux** — [tauri-plugin-deep-link docs](https://v2.tauri.app/plugin/deep-linking/) require `single-instance` plugin. Will include from day 1.
- **Updater key compromise** — backed up to 1Password Family vault; rotation requires shipping a new app and re-onboarding all users.

---

## 3. Architecture

### 3.1 Process tree

```
vskill.app                              ← Tauri Rust binary (~10 MB)
├── WKWebView / WebView2                ← loads http://127.0.0.1:<port>/
├── log files: ~/Library/Logs/vSkill/   (macOS)  | %LOCALAPPDATA%\vSkill\Logs\ (Windows)
└── child process: node                 ← spawned by Rust on launch
    └── dist/eval-server/eval-server.js ← unchanged from current vskill-cli
        ├── reads ~/.vskill/workspace.json
        ├── reads ~/.vskill/keys.env (via @napi-rs/keyring fallback)
        ├── proxies /api/v1/* → verified-skill.com
        └── serves dist/eval-ui/ (React studio bundle, unchanged)
```

### 3.2 Lifecycle

**Pre-launch orphan reaper** (AC-US04-06): On launch, Rust scans for orphan `vskill-eval-server` processes (parent PID 1, command-line matches). For each, sends SIGTERM + 1 s grace + SIGKILL. This handles the "user force-quit (kill -9) the previous shell" case.

**Cold launch** (AC-US01-01, NFR-01):
```
  → Rust: orphan reaper (above), <50 ms typical
  → Rust: pick free port (try project-hashed port from ~/.vskill/workspace.json
           active project; if busy, bind-and-release ephemeral port)
  → Rust: spawn `node dist/eval-server/eval-server.js --port=<port>` as sidecar
  → Rust: poll GET http://127.0.0.1:<port>/api/health every 100 ms (max 10 s)
  → Rust: on first 200, create main window + load http://127.0.0.1:<port>/
  → Rust: on timeout, show native error sheet "vskill failed to start" + log path
```

**Window close** (AC-US04-01, AC-US04-02): Red traffic-light "close" button HIDES the window but keeps the app + sidecar running (Mac convention). Cmd-W does the same (close window, not quit). App stays in Dock with active indicator. Clicking Dock icon re-shows window restored to last saved size+position.

**Window state persistence** (AC-US04-05): On window close/move/resize/full-screen-toggle, persist `{x, y, width, height, isFullScreen}` to `~/.vskill/desktop-window-state.json`. Atomic write (tmp+rename). Default on new install: 1280×800 centered.

**Quit** (AC-US04-01): Cmd-Q (or vSkill → Quit menu) triggers full shutdown:
```
  → Rust: POST http://127.0.0.1:<port>/api/shutdown (graceful, eval-server.ts:155 already implements this)
  → Rust: wait up to 2 s for child exit
  → Rust: if still alive, SIGTERM + 3 s grace
  → Rust: if still alive, SIGKILL
  → Rust: persist window state, exit
```

**Sleep/wake** (AC-US04-03): Subscribe to macOS `NSWorkspaceWillSleepNotification` / `NSWorkspaceDidWakeNotification` (Tauri `tauri::api::notification` does NOT cover these — use `objc2-app-kit` directly via Tauri's allowlist). On sleep: send eval-server a `POST /api/idle` (new, additive endpoint) so it pauses background polling — no termination. On wake: send `POST /api/resume`, then JS code listens for a `tauri://workspace-resumed` event and re-establishes any SSE connections within 2 s. Idle CPU during sleep budget: <1% (NFR met implicitly because Node sleeps with the system).

**Crash recovery** (AC-US06-03 — 3-strikes-in-60s rule):
```
  → Rust subscribes to child exit
  → on unexpected exit:
      strikeCount++; lastStrikeAt = now
      if strikeCount <= 3 && (now - firstStrikeAt) <= 60_000:
        // auto-restart silently within 3 s budget
        spawn new sidecar; on health 200 → emit "server-restarted" event to JS
        JS shows in-WebView toast "Server restarted" (5 s, dismissible)
      else:
        // 3rd crash inside 60 s window → give up
        show native error sheet:
          "vSkill server stopped repeatedly"
          [View Logs]  [Restart Server]  [Quit]
        (manual Restart Server resets strikeCount to 0)
  → strikeCount decays: if (now - lastStrikeAt) > 60_000, reset to 0
```

### 3.3 IPC surface (Tauri commands, Rust → JS)

The studio UI (React bundle) talks to the eval-server over HTTP today and will continue to. **No additional IPC needed for current features.** However, the Rust shell exposes a small command surface for native chrome:

| Command | Direction | Purpose |
|---|---|---|
| `get_server_port()` | JS → Rust | UI may want to display the active port (debug menu). |
| `restart_server()` | JS → Rust | Help menu → "Restart Server" item. |
| `show_logs()` | JS → Rust | Opens log dir in Finder/Explorer. |
| `check_for_updates()` | JS → Rust | Help menu → "Check for Updates"; returns `{ has_update, version, notes }`. |
| `quit()` | JS → Rust | Cmd-Q parity (also bound to native menu). |
| `on_server_crash(callback)` | Rust → JS event | Studio shows in-UI banner if the user is still on screen when the server dies. |

Implementation: Tauri's `#[tauri::command]` macro + `invoke()` on the JS side. ~50 lines of Rust total.

### 3.4 Native chrome (macOS v1)

- **Window**: standard NSWindow with traffic lights. **No custom titlebar** in v1 — keeps risk low and matches Linear/Claude desktop conventions.
- **Vibrancy** (under-window blur): NOT enabled in v1. Adds polish but increases regression surface; defer to v2 cosmetics pass.
- **Menu bar** (full layout per AC-US07-03):
  ```
  vSkill
    ├ About vSkill                                    → native About panel: app icon, version, "Includes vskill CLI vX.Y.Z"
    ├ Check for Updates...                            → calls check_for_updates command (AC-US03-04)
    ├ Preferences...                                  (Cmd-,)  → opens /settings in webview
    ├ ────
    ├ Services                                        (standard macOS submenu)
    ├ ────
    ├ Hide vSkill                                     (Cmd-H)
    ├ Hide Others                                     (Cmd-Opt-H)
    ├ Show All
    ├ ────
    ├ Quit vSkill                                     (Cmd-Q)        — triggers full shutdown (AC-US04-01)
  File
    ├ Open Project...                                 (Cmd-O)        — NSOpenPanel folder picker (AC-US05-01)
    ├ Open Recent                                     (submenu, last 10, AC-US05-02)
    │    ├ ~/projects/foo
    │    ├ ...
    │    ├ ────
    │    ├ Clear Menu                                 (AC-US05-04)
    ├ ────
    ├ Close Window                                    (Cmd-W)        — HIDES window, app + sidecar keep running (AC-US04-01)
  Edit              (Undo/Redo/Cut/Copy/Paste/Select All — all standard, AC-US07-03)
  View
    ├ Reload                                          (Cmd-R)        — webview.reload()
    ├ Force Reload                                    (Cmd-Shift-R)  — webview.reload() + skip cache
    ├ Toggle DevTools                                 (Cmd-Opt-I)    — dev builds only; release builds OMIT this item
    ├ ────
    ├ Enter Full Screen                               (Cmd-Ctrl-F)
  Window            (standard Minimize Cmd-M / Zoom / Bring All to Front)
  Help
    ├ vSkill Documentation                            → opens https://verified-skill.com/docs in default browser
    ├ Reveal Logs in Finder                           → opens ~/Library/Logs/vSkill/ in Finder (AC-US06-05)
    ├ Restart Server                                  → calls restart_server command
    ├ Report Issue...                                 → opens dialog → pre-filled GitHub Issues URL (AC-US10-04)
    ├ ────
    ├ Uninstall Helper...                             → opens deep-clean dialog (AC-US12-03)
  ```
- **Dock icon**: standard. Right-click menu shows "New Window", "Quit". No tray/menubar-extra in v1.
- **Drag-and-drop**: Dock-icon drop of a folder fires `tauri://drag-drop` → Rust → POST `/api/workspace/projects` to register it as a project. Cheap win, ship with v1.

### 3.5 Deep linking

Scheme: `vskill://`. Configured in `tauri.conf.json`:

```json
{
  "plugins": {
    "deep-link": {
      "desktop": { "schemes": ["vskill"] }
    }
  }
}
```

Plus `tauri-plugin-single-instance` so Windows/Linux fire `on_open_url` instead of spawning a second process.

URL formats:
- `vskill://projects/open?path=/Users/x/foo` — registers and activates a project.
- `vskill://skills/install?ref=anthropics/skills/skill-creator` — invokes existing install flow.
- `vskill://auth/callback?code=...` — for the GitHub Device Flow (already implemented at `src/commands/auth.ts`); replaces the current copy-paste flow with a proper redirect.

macOS limitation: scheme MUST be registered at build time in `Info.plist` `CFBundleURLTypes`. Cannot be changed at runtime.

### 3.6 Logging

- **Log directory**:
  - macOS: `~/Library/Logs/vSkill/`
  - Windows: `%LOCALAPPDATA%\vSkill\Logs\`
- **Files**:
  - `vskill-shell.log` — Rust supervisor messages (port chosen, sidecar pid, exit code, update checks).
  - `vskill-server.log` — captured stdout+stderr of the Node sidecar (rotates at 10 MB, keeps 5 generations).
- **Rotation**: standard log4rs rotating file appender on the Rust side; Node side pipes through Rust (stdout/stderr capture).
- **Help menu → Show Logs** opens the directory in Finder/Explorer (`tauri::api::shell::open`).

### 3.6.1 Light/dark mode (AC-US07-02)

System mode switching: Tauri's `WebviewWindow::set_theme(None)` follows system. Native menu bar inherits system. The WebView CSS variables already reference `prefers-color-scheme` (per existing eval-ui CSS at `src/eval-ui/src/styles/`); no changes needed. Verified: dark→light switching in System Settings updates the WebView live without reload.

### 3.6.2 NSOpenPanel folder picker (US-005, AC-US05-01)

`File → Open Project...` invokes Tauri's `tauri-plugin-dialog::FileDialogBuilder::pick_folder()`, which on macOS maps to `NSOpenPanel` with `canChooseDirectories: true, canChooseFiles: false`. On selection, Rust calls a JS-side handler via `emit("project-selected", { path })`; the studio bundle's existing project-add code path (which already POSTs to `/api/workspace/projects`) handles the actual workspace mutation. **Single source of truth**: `~/.vskill/workspace.json` (existing `addProject`/`setActiveProject` from `workspace-store.ts`).

Recent Projects menu: Rust reads `~/.vskill/workspace.json` on app activation and rebuilds the `File → Open Recent` submenu. Last-used 10, sorted by `lastActiveAt`. "Clear Menu" → POST `/api/workspace/clear-recents` (new endpoint, additive — adds clearRecents helper to `workspace-store.ts`).

Stale-folder handling (AC-US05-05): on selection, Rust calls `fs::metadata()`. If `Err`, show native dialog: "Folder not found" with [Locate...] (re-pick) [Remove from list] [Cancel]. Remove → POST `/api/workspace/projects/<id>/remove`.

### 3.6.3 Native notifications (AC-US07-07)

[`tauri-plugin-notification`](https://v2.tauri.app/plugin/notification/) for "Update available", "Skill installed successfully", "Scan completed" — only when window is unfocused. JS code in studio bundle gates on `document.visibilityState === "hidden"` before invoking `invoke("show_notification", { title, body, sound })`. When window is focused, the existing in-bundle toast UI handles it (no double-notification).

### 3.6.4 LetsMove pattern (AC-US02-07)

On first launch from outside `/Applications/`, Rust checks the executable path. If it doesn't start with `/Applications/`, show one-time native dialog:
> "Move vSkill to Applications?
> vSkill should run from the Applications folder. Move it now?
> [Move to Applications]  [Don't Move]  [Don't ask again]"

"Move to Applications" → `mv` self to `/Applications/` + relaunch. "Don't ask again" persists to `~/.vskill/desktop-config.json`. Standard macOS pattern from [LetsMove](https://github.com/potionfactory/LetsMove) — no library dep, ~30 lines of Rust.

### 3.6.5 Uninstall Helper (AC-US12-03)

`Help → Uninstall Helper...` opens a Tauri-native dialog:
```
What to remove?
  ☐ vSkill.app                    (run drag-to-Trash if checked)
  ☑ Cache (~/Library/Caches/com.verifiedskill.vskill)
  ☑ Logs (~/Library/Logs/vSkill)
  ☐ Workspace data (~/.vskill/)   ← unchecked by default; user data preserved
  ☐ Stored API keys (Keychain entries)

[Cancel]  [Remove Selected]
```

After removal: log the action to a one-shot file `/tmp/vskill-uninstall-receipt-<timestamp>.txt`, show toast "vSkill uninstall completed". The vSkill.app bundle removal step prompts user for trash confirmation.

### 3.6.6 CLI/app version drift (AC-US11-03)

On launch, Rust shells out: `vskill --version 2>/dev/null` (with a 500 ms timeout — non-blocking). If output exists and differs from the bundled CLI version, Rust emits a `cli-version-drift` event with both versions; the studio bundle shows a non-blocking banner: "CLI vX.Y.Z installed globally differs from app version A.B.C. [Align]" — Align link opens [https://verified-skill.com/docs/desktop/version-drift](https://verified-skill.com/docs/desktop/version-drift). Banner dismisses for 7 days on close.

### 3.7 Auto-update flow

```
on launch (delayed 5 s) AND every 24 h while running (AC-US03-01):
  Rust → fetch https://verified-skill.com/desktop/latest.json
  if version > current && signature valid:
    emit "update-available" event to JS
    JS → non-modal in-WebView banner: "Update available: vX.Y.Z — [Install] [Later] [Release notes]"  (AC-US03-02)

on Help → Check for Updates... (AC-US03-04):
  same flow but always shows result toast, even if up-to-date
  ("vSkill is up to date" or "Update available: ...")

on user accepts (AC-US03-03):
  Rust → download .app.tar.gz from latest.json platform URL
  Rust → verify minisign signature against embedded public key
  if signature invalid (AC-US03-06):
    Rust → discard download, log error to vskill-shell.log
    JS → modal: "Update could not be verified — please download manually"
              with link to https://verified-skill.com/download/mac
  else:
    Rust → atomic install (Tauri UpdaterPlugin: extract to tmp, swap atomically)
    JS → toast: "Update installed and ready" + [Relaunch] button

opt-out (AC-US03-05):
  Preferences → Privacy → "Automatic updates" toggle
  persisted to ~/.vskill/desktop-config.json
  when off: skip launch + 24 h checks; manual "Check for Updates..." still works
```

Update size: ~30–40 MB compressed. Released via GitHub Actions on tag push (see §5).

---

## 4. Visual / UX Notes

### 4.1 Brand alignment

Per project memory (`project_video_brand_decisions_2026_04`, `project_studio_cors_free_architecture`): **Studio Remotion colors are the source of truth, propagated to `globals.css`**. The desktop app loads the same `dist/eval-ui/` bundle today's browser tab loads — brand alignment comes for free.

### 4.2 First-run welcome window

A native splash on first launch (subsequent launches go straight to the studio):

- Window: 720×480, centered, frameless with title "Welcome to vSkill".
- Body: short "Open Project" CTA + opt-in telemetry checkbox (writes to `~/.vskill/telemetry.json`).
- Renders inside the WebView at route `/welcome` (a new route in the existing eval-ui — additive, doesn't disrupt existing routes).
- "Open Project" → triggers `File → Open Project...` flow → workspace registers project → switches to main window.

This is the only studio-side change: a thin `/welcome` route. We keep it minimal — single CTA, single checkbox, no carousel.

### 4.3 Wireframe (text-only, intentionally; no PNGs needed)

```
┌─ vSkill ───────────────────────────────────  ◯ ◯ ◯ ┐
│                                                    │
│  [Studio sidebar — projects pill, sidebar nav]     │
│                                                    │
│  [Studio main pane — exactly today's eval-ui]      │
│                                                    │
│                                                    │
└────────────────────────────────────────────────────┘
                  status bar (in-page, not native)
```

The rendered surface IS today's eval-ui. The only native surface is the menu bar above and the traffic-light area at the top.

---

## 5. Installation & Packaging Pipeline

### 5.1 Build

```
# in vskill repo root
npm run build              # tsc → dist/
npm run build:eval-ui      # vite → dist/eval-ui/

# desktop wrapper (new directory: src-tauri/)
cd src-tauri
cargo build --release      # → src-tauri/target/release/vskill (Rust shell)

# bundle into .app / .msix
cd ..
npm run desktop:build      # invokes tauri-cli with universal-apple-darwin
                          # output: src-tauri/target/universal-apple-darwin/release/bundle/dmg/vSkill_<v>_universal.dmg
```

`tauri.conf.json` `bundle.resources` includes:
- `dist/eval-server/` → loaded at runtime by the sidecar Node binary
- `dist/eval-ui/` → served by the eval-server (existing path)
- `node` binary (per-target arch, downloaded into CI from nodejs.org) → spawned by Rust supervisor

### 5.2 Sign + notarize (macOS)

GitHub Actions matrix:

```yaml
strategy:
  matrix:
    include:
      - { os: macos-14, target: aarch64-apple-darwin }
      - { os: macos-13, target: x86_64-apple-darwin }
      - { os: macos-14, target: universal-apple-darwin }   # produces both arches in one .dmg
```

Steps (per-arch):
1. Cache `~/.cargo`, `node_modules`, `dist/`.
2. Build Rust shell + bundle resources.
3. `tauri-action` — handles codesign + notarytool submit + staple.
4. Verify: `codesign --verify --verbose=4 vSkill.app` + `spctl -a -t exec -vv vSkill.app` must report "accepted, source=Notarized Developer ID".
5. Upload `.dmg` to GitHub Release artifact + GitHub Actions cache.

Secrets (already in feedback memory `feedback_self_install_vskill` for the npm flow; net-new for desktop):
- `APPLE_ID` (anton.abyzov@gmail.com)
- `APPLE_PASSWORD` (app-specific password)
- `APPLE_TEAM_ID`
- `APPLE_CERTIFICATE` (base64 .p12 of Developer ID Application)
- `APPLE_CERTIFICATE_PASSWORD`
- `TAURI_UPDATER_PRIVATE_KEY` + `TAURI_UPDATER_PRIVATE_KEY_PASSWORD`

### 5.3 .dmg layout

[`create-dmg`](https://github.com/sindresorhus/create-dmg) (already in widespread use):

```
vSkill_1.0.0_universal.dmg
├── vSkill.app            (positioned left, 200×200 icon)
├── Applications symlink  (positioned right, drag-target arrow)
└── background.png        (subtle Studio gradient + "Drag to Applications →")
```

Background image: 660×400 PNG, generated from a Remotion still (consistent with existing brand pipeline).

### 5.4 Homebrew Cask

Tap: `homebrew/cask` (mainline) — submit via [`brew bump-cask-pr`](https://docs.brew.sh/How-To-Open-a-Homebrew-Pull-Request) once Anton owns a published `.dmg` URL and SHA256.

**Staging → mainline gate** (per team-lead direction): first 2-3 releases ship to a private tap `antonabyzov/vskill-staging` only. The mainline `homebrew/cask` PR is opened ONLY after **≥30 days of staging-tap installs with zero crash reports** (NFR-09 — 99.5% crash-free sessions on a rolling 7-day window) AND **≥98% install success rate** (NFR-15) over the staging period. This de-risks first-PR rejection from Cask reviewers (R7) and uses the same telemetry signals PM already defined in spec.md §6 Success Metrics.

`Casks/vskill.rb`:

```ruby
cask "vskill" do
  version "1.0.0"
  sha256 "<sha256>"
  url "https://verified-skill.com/desktop/v#{version}/vSkill_#{version}_universal.dmg"
  name "vSkill"
  desc "Secure multi-platform AI skill installer (desktop)"
  homepage "https://verified-skill.com"

  auto_updates true   # defer to in-app Tauri updater after install
  depends_on macos: ">= :ventura"

  app "vSkill.app"

  zap trash: [
    "~/.vskill",
    "~/Library/Logs/vSkill",
    "~/Library/Preferences/com.verifiedskill.vskill.plist",
  ]
end
```

Auto-bump GitHub Action: [`Homebrew/actions/setup-homebrew`](https://github.com/marketplace/actions/homebrew-bump-cask) on each tagged release.

### 5.5 Windows installer (P1)

`tauri build --target x86_64-pc-windows-msvc`:
- Output: `vSkill_<v>_x64-setup.exe` (NSIS installer) + `vSkill_<v>_x64_en-US.msi`.
- `bundle.windows.webviewInstallMode = "embedBootstrapper"` (+1.8 MB, requires internet on first run; acceptable trade vs offline-installer +127 MB).
- Sign via `osslsigncode` in CI (`SIGNING_CERTIFICATE` + `SIGNING_PASSWORD` secrets).
- MSIX path (Microsoft Store) — out of scope for v1, P2.
- winget manifest — submit after first GA.

### 5.6 Telemetry & crash reporting (US-010, P1)

**Default OFF** (AC-US10-01). First launch shows one-time non-blocking dialog: "Help improve vSkill? Send anonymous usage and crash reports. [Yes] [No] [Learn more]". Choice → `~/.vskill/desktop-telemetry.json`.

**What's sent** (AC-US10-02): app version, OS version, anonymous install UUID (regenerable from `Help → Reset telemetry ID`), crash stack trace. NEVER: project paths, file contents, skill content, user-identifiable data.

**Where**: existing `/api/v1/studio/telemetry/` proxy → `verified-skill.com` (already in platform-proxy allow-list at `platform-proxy.ts:95`).

**Crash reporting**: Tauri's panic handler writes a crash dump to `~/Library/Logs/vSkill/crashes/<timestamp>.dmp`. Sidecar Node panics use `process.on("uncaughtException")` → JSON-formatted entry in `vskill-server.log`. Both surfaced in `Help → Report Issue...` (AC-US10-04) which pre-fills a GitHub Issues URL with redacted-paths option.

**Offline crash handling** (AC-US10-05): if upload fails, modal offers "Save report as .txt" → user gets a file they can attach manually.

**Privacy gate** (NFR-11): on first launch with telemetry OFF, network capture in CI must show ZERO outbound calls to anything except the localhost eval-server. Test: `nettop -m route -p $(pgrep vSkill) -l 5` → 0 external connects.

### 5.7 Coexistence with `npx vskill studio` (US-011)

Both processes use the project-hashed port (3077–3177) from `eval-server/serve.ts:projectPort()`. Conflict resolution:

- Each process tries its hashed port. If `EADDRINUSE`, pick next free port via `net.createServer().listen(0)` → `address().port`. Within the 3077–3177 range first; expand to ephemeral if exhausted.
- AC-US11-05 explicit-port collision: `vskill studio --port <desktop-app-port>` — existing CLI has no awareness of the desktop app. Add a check in `eval/serve.ts`: before binding, attempt a probe `GET http://127.0.0.1:<port>/api/health`; if response `200` with body `{"app":"vskill-desktop"}` (NEW: desktop adds an `app` field to health endpoint), error out:
  > `error: port <port> is in use by vSkill desktop app. Choose a different port or quit the app.`

Implementation: ~10 LOC change to `eval/serve.ts:checkPortFree()`.

- AC-US11-02 (workspace.json concurrent writes): `workspace-store.ts` already uses atomic write (tmp + rename, line 76 `${file}.tmp-${process.pid}-${Date.now()}`). Verified safe under stress test. **No code change needed**, but add 100-iteration concurrency test in `__tests__/workspace-store-concurrent.test.ts`.

---

## 6. Testing Strategy

The user explicitly asked to "make sure installation works" — testing strategy is load-bearing.

### 6.1 Unit tests (Rust supervisor)

`src-tauri/src/lib.rs` Rust unit tests:
- `port_allocator_picks_free_port()` — bind, drop, verify socket releases.
- `sidecar_spawn_kills_on_drop()` — supervisor struct's Drop impl SIGTERMs child.
- `health_poll_returns_on_first_200()` — mock server, assert poll exits ≤10 s.
- `health_poll_times_out_after_10s()` — mock server that never responds.
- `update_manifest_signature_verification()` — valid + invalid + corrupted signature.

`cargo test` in CI on every PR.

### 6.2 Integration tests (Tauri app)

Two layers:

**(a) Studio bundle Playwright** — runs against the eval-server HTTP surface, completely independent of Tauri. This is the existing test suite at `vskill/e2e/`. Continues to gate every PR. `npx playwright test`.

**(b) Tauri app E2E** — `tauri-driver` + WebdriverIO. Per [Tauri WebDriver CI docs](https://v2.tauri.app/develop/tests/webdriver/ci/), supported on:
- Linux runners (Xvfb fake display).
- Windows runners (windows-latest, no display server needed).
- **macOS — NOT supported** by tauri-driver. macOS coverage uses approach (c).

Test scenarios for (b):
- App launches → main window appears → studio loads (assert title contains "vSkill").
- Help → Check for Updates → assert manifest fetch succeeded (mock manifest server in CI).
- File → Open Project → folder picker simulated via `tauri-driver` set-file → project appears in sidebar.
- Quit → assert sidecar process exits within 5 s.

**(c) macOS smoke** — AppleScript via `osascript` running under `macos-14` runner:
```bash
osascript -e 'tell application "vSkill" to launch'
sleep 8
osascript -e 'tell application "System Events" to tell process "vSkill" to get visible of window 1'
# expects "true"
osascript -e 'tell application "vSkill" to quit'
```
Plus screenshot capture via `screencapture -R0,0,1280,800 launch.png` for visual regression in PR comments.

### 6.3 Installation tests — **the critical gate**

**macOS** (`macos-13` Intel + `macos-14` ARM matrix):

```yaml
- name: Install .dmg
  run: |
    hdiutil attach vSkill_${{ env.VERSION }}_universal.dmg
    cp -R "/Volumes/vSkill/vSkill.app" /Applications/
    hdiutil detach "/Volumes/vSkill"

- name: Gatekeeper assessment (signed + notarized)
  run: |
    spctl -a -t exec -vv /Applications/vSkill.app 2>&1 | tee gatekeeper.log
    grep -q "accepted" gatekeeper.log
    grep -q "source=Notarized Developer ID" gatekeeper.log

- name: Launch
  run: |
    open /Applications/vSkill.app
    sleep 12

- name: Screenshot + assert window
  run: |
    screencapture -t png launch.png
    osascript -e 'tell application "System Events" to count (windows of process "vSkill")' | grep -qE "[1-9]"

- name: Quit + uninstall
  run: |
    osascript -e 'tell application "vSkill" to quit'
    sleep 2
    rm -rf /Applications/vSkill.app
    rm -rf ~/Library/Logs/vSkill
```

**macOS — Homebrew Cask install path**:

```yaml
- name: Brew cask install (HEAD points to PR)
  run: |
    brew tap antonabyzov/vskill-staging
    brew install --cask antonabyzov/vskill-staging/vskill@head
    open -a vSkill
    sleep 10
    osascript -e 'tell application "vSkill" to quit'
    brew uninstall --cask --zap antonabyzov/vskill-staging/vskill@head
    # zap should remove ~/.vskill — assert clean state
    test ! -d ~/.vskill || (echo "zap failed to remove ~/.vskill" && exit 1)
```

**Windows** (P1, post-macOS-GA):

```yaml
- name: Install .msi silently
  run: msiexec /i vSkill_${{ env.VERSION }}_x64_en-US.msi /qn /norestart
- name: Launch
  run: |
    Start-Process "C:\Program Files\vSkill\vSkill.exe"
    Start-Sleep -Seconds 12
- name: Window assert
  run: |
    Get-Process vSkill | Where-Object { $_.MainWindowHandle -ne 0 }
- name: Uninstall
  run: msiexec /x vSkill_${{ env.VERSION }}_x64_en-US.msi /qn
```

**Unsigned-build negative test** (gate to ensure we never accidentally ship unsigned):

```yaml
- name: Assert signed dmg fails gatekeeper as unsigned
  run: |
    # build .dmg WITHOUT secrets
    npm run desktop:build:unsigned
    spctl -a -t exec -vv /Applications/vSkill.app && exit 1 || true
    # we WANT this to fail — unsigned must be rejected
```

### 6.4 Update flow test

Two-phase test on `macos-14`:

```
Phase 1: install vN-1
  - download previous tagged .dmg from GitHub Releases artifact
  - install + launch + verify version

Phase 2: trigger update to vN
  - point updater at staging manifest with vN
  - JS calls invoke("check_for_updates") via DevTools
  - assert UI shows "Update available"
  - simulate user accept
  - assert app relaunches at vN within 60 s
  - verify Info.plist CFBundleShortVersionString == vN
```

### 6.5 Performance tests

Budgets per spec.md NFR-01..04:

- **Cold launch** (NFR-01): `time open -W /Applications/vSkill.app` on `macos-14`. Budget: **<1.5 s p50 / 2.5 s p95** Apple Silicon; **<2.5 s p50 / 4.0 s p95** Intel — to "Studio UI fully interactive" (eval-ui sends `studio-ready` postMessage).
- **Warm launch** (NFR-02): app already running, window hidden, click Dock icon → window visible. Budget: **<500 ms p50**.
- **Idle memory** (NFR-03): `ps -p $(pgrep vSkill) -o rss=` after 5 min idle. Budget: **<250 MB RSS** combined (shell + sidecar). Internal stretch goal: <180 MB.
- **Bundle size** (NFR-04): `du -sh vSkill_<v>_universal.dmg`. Budget: **<60 MB compressed** universal `.dmg`. Tauri shell ~10 MB + Node binary ~30 MB compressed (universal includes both arches when applicable; Apple's `lipo` + `.dmg` UDZO compression brings universal Node down to ~35 MB) + studio bundle ~5 MB + assets ~2 MB. **Tight but achievable**; if exceeded, fall back to per-arch `.dmg`s (intel + arm64) at ~45 MB each, document tradeoff per OQ-02.

CI gates fail the release if any budget exceeded.

Run on every release-candidate tag, fail PR if budgets exceeded.

### 6.6 Crash recovery test

```
- Launch app
- Identify Node sidecar PID via Tauri command get_server_pid()
- kill -9 <pid>
- Assert: within 3 s, app shows native error sheet "vSkill server stopped unexpectedly"
- Assert: error sheet has [View Logs] [Restart Server] [Quit] buttons
- Click Restart Server
- Assert: server health endpoint returns 200 within 10 s
```

---

## 7. Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Apple notarization stalls (Feb 2026 outage precedent) | Medium | Blocks release | Nightly dry-run on `main`; ability to ship unsigned-but-codesigned `.dmg` to dev users in emergency. |
| R2 | Tauri WebView2 fragmentation on Windows 7/8/10 | Low | Windows install fails | `webviewInstallMode = "embedBootstrapper"` (+1.8 MB, internet on first run). Fallback `offlineInstaller` (+127 MB) documented but not default. |
| R3 | Node SEA + cross-arch builds (if v2) | Medium | v2 release slip | Stay on stock-Node-binary in v1. Re-evaluate when Node 26 LTS lands. |
| R4 | eval-server module-load env coupling (boot-preflight ordering) breaks under sidecar | Low | Stored API keys silently dropped | Same constraint inside Tauri sidecar — Rust does NOT inject env into Node; eval-server already handles this via `boot-preflight.ts`. Add a regression test that boots the sidecar with a stored key and asserts it's read into the request to the provider. |
| R5 | Tauri updater private key compromise | Low | All future updates blocked | Key in 1Password Family vault + GH Actions secret. Rotation = re-onboard users (manual reinstall). Documented in runbook. |
| R6 | macOS WebDriver gap (no tauri-driver on darwin) | High (already known) | Lower E2E confidence on macOS | AppleScript smoke + Playwright against eval-server HTTP layer. |
| R7 | Brew Cask reviewer rejects (style nits) | Medium | First-cask delay | Anton can self-host a `vskill-staging` tap initially; submit to mainline cask after 2-3 versions for reputation. |
| R8 | Windows OV cert reputation cold-start (SmartScreen warns) | High | First-time Windows users see scary dialog | **Reputation warm-up** (per team-lead direction): pre-ship signed builds to a closed testing cohort (~20-50 Anton-trusted users) for 2-4 weeks before public Windows GA so the cert accrues download/install reputation. Track via opt-in telemetry NFR-15. After warm-up: document expected behavior in release notes ("click 'More info' → 'Run anyway' on first install"); reputation continues to accrue with public downloads. SmartScreen reputation is per-cert+binary-signature, so each major version reset costs reputation — accept and document. |
| R9 | Cold-launch budget breach on Intel Macs (older hardware) | Medium | UX feels sluggish | Profile with Instruments; primary mitigation is sidecar boot — cache `~/.vskill/keys.env` decryption via in-memory keychain handle. |
| R10 | Spec.md drift from this plan | Low | Implementation rework | This plan was drafted in parallel with spec.md. Architect re-reviews plan on spec.md finalization; deltas captured before Phase 1 starts. |

---

## 8. Implementation Phases

Suggested decomposition for the downstream `sw-planner` agent. Each phase is independently shippable and testable.

### Phase 1 — Skeleton + sidecar boot (macOS only)

**Goal**: developer runs `npm run desktop:dev` and sees `vSkill.app` (unsigned) launch with studio loaded inside WKWebView.
**Spec ACs covered**: AC-US01-01..05, AC-US06-01..06, AC-US09-01..05, AC-US11-01..05.

Tasks:
- T-001: Scaffold `src-tauri/` with Tauri 2 init.
- T-002: Bundle `dist/eval-server/` + `dist/eval-ui/` + Node binary as Tauri resources.
- T-003: Rust supervisor: orphan reaper + port allocation + spawn sidecar + health poll.
- T-004: WebView loads `http://127.0.0.1:<port>/`. Window state persistence (AC-US04-05).
- T-005: Cmd-W hides window, Cmd-Q full shutdown via /api/shutdown then SIGTERM (AC-US04-01).
- T-006: Native macOS menu bar (full layout from §3.4).
- T-007: NSOpenPanel folder picker for File → Open Project (AC-US05-01) + Recent Projects submenu (AC-US05-02..05).
- T-008: Help → Reveal Logs in Finder (AC-US06-05).
- T-009: Help → Restart Server (manual restart, resets strikeCount).
- T-010: 3-strikes-in-60s crash recovery (AC-US06-03) + native error sheet.
- T-011: Light/dark mode follow-system (AC-US07-02).
- T-012: Sleep/wake handling — pause+resume eval-server (AC-US04-03).
- T-013: Coexistence with `npx vskill studio` — `app:` field on /api/health (AC-US11-01..05).
- T-014: workspace.json atomic-write 100-iteration concurrency test (AC-US11-02 / NFR-14).
- T-015: Unit tests for Rust supervisor (§6.1).
- T-016: AppleScript smoke test (§6.2c).

**Exit criteria**: unsigned `.app` launches on M-series + Intel; studio fully functional; SIGKILL-recovery test passes; window state persists across launches; both `npx vskill studio` and the desktop app can run simultaneously without collision.

### Phase 2 — Auto-update + deep-link + LetsMove + native polish

**Spec ACs covered**: AC-US02-07, AC-US03-01..06, AC-US04-04, AC-US07-01, AC-US07-04..08, AC-US12-01..05.

Tasks:
- T-017: Tauri updater plugin wired to `https://verified-skill.com/desktop/latest.json`.
- T-018: Cloudflare Worker route hosting manifest + R2-backed binaries.
- T-019: `vskill://` URL scheme registered in `Info.plist` + `tauri-plugin-deep-link`.
- T-020: Deep-link handlers: `projects/open`, `skills/install`, `auth/callback` (AC-US04-04).
- T-021: Help menu → Check for Updates... (AC-US03-04).
- T-022: Preferences → Privacy → Automatic Updates toggle (AC-US03-05).
- T-023: Update-flow integration test (§6.4).
- T-024: LetsMove pattern (AC-US02-07).
- T-025: App icon assets at all required sizes via Assets.car (AC-US07-01).
- T-026: Native notifications via tauri-plugin-notification when window unfocused (AC-US07-07).
- T-027: VoiceOver accessibility audit (AC-US07-05, NFR-07).
- T-028: prefers-reduced-motion verification (AC-US07-08).
- T-029: Uninstall Helper dialog (AC-US12-03).
- T-030: CLI/app version drift detection (AC-US11-03).

**Exit criteria**: install vN-1, ship vN, app self-updates without user reinstall; deep-link from terminal opens app; first launch outside /Applications/ offers move; uninstall is clean.

### Phase 3 — Sign, notarize, distribute (macOS GA)

**Spec ACs covered**: AC-US02-01..06, AC-US07-08, NFR-01..04, NFR-05, NFR-13, NFR-15.

Tasks:
- T-031: GitHub Actions release workflow with macOS matrix (Intel + ARM + universal).
- T-032: Tauri-action codesign + notarytool integration.
- T-033: `.dmg` background image + create-dmg layout.
- T-034: Installation tests on `macos-13` + `macos-14` runners (§6.3).
- T-035: Performance tests (cold launch, warm launch, idle memory, bundle size) (§6.5).
- T-036: Homebrew Cask submission (initially staging tap `antonabyzov/vskill-staging`).
- T-037: Brew Cask install test (§6.3).
- T-038: First-run welcome window route in eval-ui (`/welcome`).
- T-039: Brand review checkpoint (NFR-08).
- T-040: Release runbook in `docs/RELEASING-DESKTOP.md`.
- T-041: Nightly notarization dry-run on `main` (R1 mitigation).

**Exit criteria**: `brew install --cask vskill` works on fresh macos-14 runner; Gatekeeper accepts (`spctl -a`); all NFR-01..04 budgets pass; brand review signed off.

### Phase 4 — Telemetry & crash reporting (US-010, P1)

**Spec ACs covered**: AC-US10-01..05, NFR-09, NFR-11.

Tasks:
- T-042: First-launch telemetry opt-in dialog (AC-US10-01).
- T-043: Preferences → Privacy → Telemetry toggle (AC-US10-03).
- T-044: Crash dump collection — Tauri panic handler + Node uncaughtException (AC-US10-04).
- T-045: Help → Report Issue... pre-fill GitHub Issues (AC-US10-04).
- T-046: Offline crash report → save-as-.txt fallback (AC-US10-05).
- T-047: Privacy gate test (NFR-11): no outbound network with telemetry OFF.
- T-048: Crash-free sessions dashboard (NFR-09 — 99.5% rolling 7-day).

**Exit criteria**: telemetry opt-in flow works; crash reports surface in dashboard; privacy gate test passes.

### Phase 5 — Windows port (US-008, P1, post-macOS-GA)

**Spec ACs covered**: AC-US08-01..07.

Tasks:
- T-049: `tauri build --target x86_64-pc-windows-msvc`.
- T-050: Bundle Windows Node binary (per-arch).
- T-051: WebView2 `embedBootstrapper` install mode.
- T-052: `osslsigncode` signing in CI with OV cert.
- T-053: `vskill://` registry registration via `tauri-plugin-deep-link`.
- T-054: Windows installation tests on `windows-latest` runner.
- T-055: winget manifest submission to microsoft/winget-pkgs.
- T-056: **Pre-GA closed cohort** (R8 warm-up, per team-lead direction): ship signed Windows builds to ~20-50 Anton-trusted testers for 2-4 weeks. Track install/launch telemetry to confirm reputation accrual before public GA.
- T-057: SmartScreen reputation guidance in release notes (R8 mitigation, post-warm-up).
- T-058: Squirrel.Windows or MSIX auto-update channel (AC-US08-06).
- T-059: Per-user MSIX install (no admin rights, AC-US08-03).
- T-060: All P0 ACs from US-001/04/05/06/07 verified on Win 11 (AC-US08-05).

**Exit criteria**: `winget install vskill` works on fresh `windows-latest` runner; signed installer; auto-update works; SmartScreen warning either suppressed (post-warm-up) or briefly shown with documented "Run anyway" UX path.

---

## 9. Open Questions (for PM/Anton)

Spec.md resolved most prior ambiguity. Remaining items:

1. **OQ-01 → resolved by ADR**: Tauri 2 chosen.
2. **OQ-02 → universal binary first**: ship universal `.dmg` in v1; if the 60 MB NFR-04 budget is breached, fall back to per-arch `.dmg`s. CI gate decides at release time.
3. **OQ-03 → resolved**: appcast (`latest.json`) hosted at `https://verified-skill.com/desktop/latest.json` via the existing Cloudflare Worker route. R2-backed binaries.
4. **OQ-04 → resolved**: eval-server runs as a child Node process (sidecar), not embedded. Justification in ADR §"Why not the alternatives".
5. **Sparkle vs Tauri Updater terminology** — spec AC-US03-01 says "appcast" (Sparkle term). Architect ships Tauri Updater with a static signed manifest, which is functionally equivalent. **Confirming with PM**: the user-visible behavior matches AC-US03-01..06 exactly; only the wire format differs. Acceptable?
6. **Brew Cask tap** — submit directly to mainline `homebrew/cask`, or stage on `antonabyzov/vskill-staging` first? Architect's recommendation: stage for first 2-3 releases, then submit mainline.
7. **Microsoft Store (Windows P1 stretch)** — pursue submission alongside direct MSIX download, or post-GA? Architect's recommendation: direct MSIX in P1, Store submission in P2.
8. **Deep-link scope beyond `projects/open`, `skills/install`, `auth/callback`** — is there appetite for `vskill://eval/<runId>` (share eval runs), `vskill://settings/keys` (open key entry directly)? Architect's default: only the three listed in v1; add others as user-research signal arrives.
9. **Custom titlebar / vibrancy** — confirmed v1 ships with standard traffic-lights. Defer NSVisualEffectView to v2 cosmetic pass per AC-US07-04 (which only requires standard inset position).
10. **Tray / menu-bar-extra icon** — Raycast-style hotkey hot-corner is OUT for v1. Confirm.

---

## 10. Contract Summary (for downstream agents)

**Implementer must NOT change**:
- `dist/eval-ui/` — desktop loads it verbatim. Studio UI changes flow through their own increments.
- `eval-server.ts` boot-preflight import order — `./boot-preflight.js` MUST stay the first import (eval-server.ts:14).
- `~/.vskill/workspace.json` schema — desktop reads it the same way the CLI does.
- `/api/shutdown` POST contract — Rust supervisor calls this for graceful sidecar stop.

**Implementer MUST add**:
- `src-tauri/` directory with Tauri 2 scaffolding.
- New script `desktop:build` in `package.json`.
- New script `desktop:dev` for local iteration.
- New route `/welcome` in `src/eval-ui/` (additive, behind a `?firstRun=1` query gate so existing browser-tab users don't see it).
- **Additive eval-server endpoints** (new, non-breaking):
  - `POST /api/idle` — pause background polling on macOS sleep (AC-US04-03).
  - `POST /api/resume` — resume after macOS wake (AC-US04-03).
  - `GET /api/health` — extend existing health response with `{ "app": "vskill-desktop" | "vskill-cli" }` discriminator for coexistence detection (AC-US11-05).
  - `POST /api/workspace/clear-recents` — for File → Open Recent → Clear Menu (AC-US05-04).
  - `POST /api/workspace/projects/<id>/remove` — for stale-folder removal (AC-US05-05).
- New Tauri commands: `get_server_port`, `restart_server`, `show_logs`, `check_for_updates`, `quit`, `get_server_pid`, `pick_project_folder` (NSOpenPanel), `show_notification`, `move_to_applications` (LetsMove).
- New event channels (Rust → JS):
  - `server-crashed` — show in-UI crash banner.
  - `server-restarted` — toast "Server restarted" after successful auto-restart.
  - `update-available` — fire in-UI update banner.
  - `cli-version-drift` — show CLI-vs-app version drift banner.
  - `workspace-resumed` — re-establish SSE connections after wake.
  - `project-selected` — folder picker result.
- **eval-server change** (1-line, non-breaking): `eval/serve.ts:checkPortFree()` probes `/api/health` to detect desktop-app vs CLI sessions on the same port (AC-US11-05).

**Test budget gates**:
- Cold launch <1.5 s (macOS M-series), <3 s (Intel).
- Idle RSS <150 MB.
- `.dmg` bundle <80 MB universal.
- All Phase 3 installation tests must pass on `macos-13` + `macos-14`.
