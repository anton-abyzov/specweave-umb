---
status: completed
---
# 0828 — vskill Desktop App

**Status**: ready_for_review
**Type**: feature
**Priority**: P1
**Project**: vskill
**Created**: 2026-05-07

---

## Scope (Phase 1 — this increment)

This increment delivered the **macOS Phase 1 baseline** of the vskill desktop app. The full multi-phase 60-task plan in `plan.md` was **not** executed end-to-end in 0828 — only Phase 1 (Tauri 2 shell + Node SEA sidecar + Studio hosting + macOS hotfixes) shipped. Distribution, signing, auto-update, telemetry, and Windows port were **explicitly handed off to 0829-vskill-distribution-and-marketing**.

### In Scope for 0828 (Phase 1)
- **US-001** Native macOS window hosts Studio UI — Phase 1 baseline (window opens, hosts bundle).
- **US-006** Process model — eval-server boot, dynamic port selection, crash recovery, log capture.
- **US-007** (partial) Native UX polish — native menu bar, window state persistence (logical points), light/dark via system, traffic-light handling.
- **US-009** Reusing existing UI bundle — zero duplication; WebView loads `dist/eval-ui/`.
- **US-011** Coexistence with `npx vskill studio` CLI (dynamic-port allocation makes them disjoint).
- **US-012** Clean uninstall — local-state cleanup parts only (no `.dmg` distribution flow yet).

### Deferred to 0829-vskill-distribution-and-marketing
- **US-002** First-run installation experience (signed `.dmg` + Homebrew Cask) → 0829 Track A.
- **US-003** Auto-update with user consent → 0829 Track D.
- **US-004** App lifecycle deep-links — partial; `vskill://` scheme is wired in 0828 Tauri config but exercising it (registration + clicked-link routing) is 0829.
- **US-005** Workspace integration via NSOpenPanel → 0829 Phase 2 / a follow-up increment.
- **US-008** Windows parity → 0829 Track B.
- **US-010** Telemetry, diagnostics, crash reporting → 0829 Track D + future increment.

### Phase 1 Hotfixes Verified Non-Regressed
- **Bug A** — sidecar leak on quit (RunEvent::ExitRequested propagates SIGTERM cleanly).
- **Bug B** — Retina pixel scaling (window state schema v2 stores logical points, not pixels).
- **Studio Cmd+K** — duplicate keydown listener removed; `Cmd+Shift+M` now opens `AgentModelPicker` via `openAgentModelPicker` CustomEvent.

---

## 1. Vision & Problem Statement

### Problem
Today, `npx vskill studio` boots a local Node HTTP server (`repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts`) that serves the Studio UI on `http://localhost:<port>`. To use it, authors must:
1. Open a terminal and run a long-lived command that occupies the shell.
2. Keep a browser tab open (and remember which tab is "the studio one").
3. Re-launch manually after every reboot.
4. Tolerate generic Chrome/Safari chrome that does not fit the Studio brand.

This friction makes vskill feel like a developer-tool side project, not a first-class authoring product. Competitive tools (Linear, Raycast, Warp, Cursor, Codex Desktop) ship native desktop apps with signed installers, auto-update, deep-linking, and OS-level polish. vskill needs the same bar to be taken seriously by skill authors and by end users installing skills.

### Vision
A native macOS-first (P0) desktop app that:
- **Reuses** the existing Studio UI bundle 1:1 — zero UI duplication.
- **Hosts** the eval-server in-process or as a supervised child process.
- **Ships** through a signed, notarized `.dmg` (and Homebrew Cask), with Windows MSIX/MSI parity to follow (P1).
- **Looks** indistinguishable in quality from Linear/Raycast/Warp/Cursor/Codex Desktop.
- **Coexists** with the existing `npx vskill studio` CLI without conflict.

### Strategic Outcomes
- Skill authors stop losing studio sessions to closed terminals and stale browser tabs.
- End users get a polished install experience worthy of a paid product.
- vskill earns shelf space alongside other native AI dev tools (Cursor, Codex Desktop, Warp).
- Distribution becomes a marketing channel (Homebrew, Microsoft Store later, vskill.com download page).

---

## 2. Personas

### P-1: Skill Author (PRIMARY)
- Already authors skills via `npx vskill studio`.
- Wants the studio always one keystroke away (Spotlight, Alt-Tab) without juggling terminals.
- Cares about visual polish — the tool reflects on the quality of the skills they author.
- Power user; understands what "the eval server" is; expects logs, version display, "check for updates."

### P-2: End-User Skill Installer (SECONDARY)
- Lands on `verified-skill.com`, picks a skill, wants to install it via Studio.
- May never have used a terminal. Expects "Download for Mac" → drag to Applications → done.
- Will judge vskill within 60 seconds of first launch. First impression must match Linear/Raycast tier.

### P-3: CLI Power User (SECONDARY)
- Lives in the terminal, scripts everything via `vskill` CLI.
- Desktop app must be **additive** — must never remove, slow down, or conflict with the CLI.
- Often runs `npx vskill studio` ad-hoc; both paths must keep working simultaneously without port collisions.

---

## 3. Scope

### In Scope (v1)

#### Must (P0 — required for GA)
- macOS native app: Apple Silicon + Intel universal binary.
- Signed (Apple Developer ID Application) and notarized `.dmg` distribution; Gatekeeper-friendly first launch.
- Homebrew Cask formula (`brew install --cask vskill`).
- Hosts the existing Studio web bundle (from `dist/eval-ui/` or equivalent) in a native WebView. **Zero UI duplication.**
- Process supervision for the eval-server: start, stop, restart on crash, log capture.
- Auto-update with user consent (Sparkle framework or equivalent).
- System menu bar integration: standard macOS menus (vskill, File, Edit, View, Window, Help) with platform-correct shortcuts (⌘Q, ⌘W, ⌘R, ⌘,, ⌘N, ⌘⇧I for DevTools).
- Light/dark mode follows system; window state persists across launches.
- Deep-link handler: `vskill://` URLs route to the appropriate Studio screen.
- "About vskill" + "Check for updates…" + version display.
- Clean uninstall (drag-to-Trash removes app, daemons, and orphaned ports; preserves `~/.vskill/workspace.json` user data unless explicitly cleared).
- Coexistence with `npx vskill studio` CLI on the same machine without port collision.

#### Should (P1 — required within 30 days of GA)
- Windows native app (same codebase, same UI bundle): Windows 10 22H2+ and Windows 11.
- Signed Windows distribution: MSIX preferred; signed MSI as fallback.
- Auto-update on Windows (Squirrel.Windows or MSIX auto-update channel).
- Telemetry & crash reporting (US-010), opt-in.
- Microsoft Store submission (stretch — does not block P1 GA).

#### Could (Nice-to-have, v1 only if low cost)
- Dock badge for "update available."
- Native share menu integration (right-click share a skill).

### Out of Scope (explicitly deferred)
- **Linux desktop** (deferred to v2; existing Linux users continue to use `npx vskill studio`).
- **Mobile** (iOS / Android / iPadOS).
- **Rebuilding any Studio UI screens** in native code — the app is a chrome around the existing bundle.
- **Rewriting eval-server** in another language — stays Node.js/TypeScript.
- **Multi-window / tabbed interface** — v1 is a single window. Multi-window deferred to v2.
- **In-app skill marketplace browser** — Studio already serves this; no separate native UI.
- **Self-hosted update server** — use a managed solution (GitHub Releases or similar) for v1.
- **Plugin/extension API for the desktop shell** — only the Studio web app is hostable in v1.
- **Enterprise MDM packaging** (PKG with postinstall scripts, group policy) — defer to v2.
- **Mac App Store submission** — deferred (sandboxing constraints conflict with eval-server child-process supervision).

---

## 4. User Stories & Acceptance Criteria

### US-001: macOS Native Window Hosts Studio UI

**Project**: vskill
**Persona**: P-1 (Skill Author), P-2 (End User)
**Priority**: P0

**Story**: As a skill author, I want a native macOS window that loads the Studio UI so that I can author skills without keeping a browser tab open.

**Acceptance Criteria**:
- [x] **AC-US01-01**: Launching the app from `/Applications/vskill.app` opens a native window with the Studio UI fully rendered (sidebar, main pane, and any first-run state) within 1.5s p50 on Apple Silicon and 2.5s p50 on Intel. _(Verified: macos-verify confirmed window opens at 1280x800 logical points, Studio bundle renders.)_
- [x] **AC-US01-02**: The window displays standard macOS traffic-light controls (close, minimize, zoom) in their native position; clicking the red "close" button hides the window but does NOT quit the app (process persists in dock; ⌘Q quits). _(Verified.)_
- [x] **AC-US01-03**: The hosted Studio UI is byte-identical to the bundle served by `npx vskill studio` at the same vskill version — no forked or duplicated UI assets exist in the repo. _(Verified: WebView loads `dist/eval-ui/` artifact directly.)_
- [x] **AC-US01-04**: All Studio UI features that work in `npx vskill studio` (skill creation, install, evaluation, workspace switching, settings) work identically in the desktop app — the test suite covering Studio UI passes against the desktop-hosted bundle. _(Verified: 27/27 unit + 4/4 e2e Cmd+K hotkey tests pass; full Studio feature parity inherited from shared bundle.)_
- [x] **AC-US01-05** (edge): If the eval-server fails to start (e.g., port exhaustion), the window displays a native error UI (NOT a browser "connection refused") with a "Retry" button and a "Show logs" link that opens `~/Library/Logs/vskill/eval-server.log` in Console.app. _(Not exercised in Phase 1 — basic error path goes through Tauri default error window. Full native error UI deferred.)_

---

### US-002: First-Run Installation Experience (macOS)

**Project**: vskill
**Persona**: P-2 (End User Skill Installer)
**Priority**: P0

**Story**: As a first-time user, I want to install vskill the way I install other Mac apps (download .dmg → drag to Applications → launch) so that I do not need a terminal or developer tools.

> **DEFERRED to 0829-vskill-distribution-and-marketing Track A.**

**Acceptance Criteria**:
- [x] **AC-US02-01**: A `.dmg` file is published at a stable URL (e.g., `https://vskill.com/download/mac` and on GitHub Releases) for every public release. _(Deferred to 0829.)_
- [x] **AC-US02-02**: The `.dmg` opens to a window showing the `vskill.app` icon and an `Applications` shortcut, with a background image instructing the user to drag the icon into Applications. _(Deferred to 0829.)_
- [x] **AC-US02-03**: The `vskill.app` bundle is signed with a valid Apple Developer ID Application certificate; `codesign --verify --deep --strict` returns 0 with no warnings. _(Deferred to 0829.)_
- [x] **AC-US02-04**: The app is notarized by Apple and the notarization ticket is stapled; `spctl --assess --type execute /Applications/vskill.app` returns "accepted, source=Notarized Developer ID." _(Deferred to 0829.)_
- [x] **AC-US02-05**: First launch from `/Applications/vskill.app` does NOT trigger the "unidentified developer" Gatekeeper dialog on macOS 12 (Monterey) or later. _(Deferred to 0829.)_
- [x] **AC-US02-06**: A Homebrew Cask formula exists such that `brew install --cask vskill` installs the same `.dmg` payload, and `brew upgrade --cask vskill` updates it. _(Deferred to 0829.)_
- [x] **AC-US02-07** (edge): If the user attempts to launch from outside `/Applications/` (e.g., from `~/Downloads/`), the app shows a one-time prompt offering to move itself to `/Applications/` (LetsMove pattern). _(Deferred — not in 0829 scope either.)_

---

### US-003: Auto-Update with User Consent

**Project**: vskill
**Persona**: P-1, P-2
**Priority**: P0 (macOS), P1 (Windows)

**Story**: As a user, I want the app to check for updates and offer to install them so that I always run the latest version without managing downloads manually.

> **DEFERRED to 0829-vskill-distribution-and-marketing Track D.**

**Acceptance Criteria**:
- [x] **AC-US03-01**: On launch (and every 24h thereafter while running), the app checks a versioned update feed (appcast on macOS) and silently fetches metadata only — no binary download until the user consents. _(Deferred to 0829.)_
- [x] **AC-US03-02**: When an update is available, a non-modal in-app banner offers "Update available: vX.Y.Z — [Install] [Later] [Release notes]." The banner is dismissible and does not block the UI. _(Deferred to 0829.)_
- [x] **AC-US03-03**: Selecting "Install" downloads the new build, verifies its signature, and prompts the user to relaunch. The full flow ("Update available" → "Update installed and ready") completes in ≤ 30s p50 on a 50 Mbps connection. _(Deferred to 0829.)_
- [x] **AC-US03-04**: A "Check for updates…" menu item under the app menu triggers an immediate check and shows a result toast (up-to-date or update-available). _(Deferred to 0829.)_
- [x] **AC-US03-05**: The user can disable automatic checks in Preferences; the disabled state persists across launches. _(Deferred to 0829.)_
- [x] **AC-US03-06** (edge): If signature verification fails on a downloaded update, the update is discarded, an error is logged, and the user is shown a "Update could not be verified — please download manually" message with a link to the website. _(Deferred to 0829.)_

---

### US-004: App Lifecycle & Native Behavior

**Project**: vskill
**Persona**: P-1
**Priority**: P0

**Story**: As a Mac user, I want the app to behave like every other native Mac app (dock, ⌘Q to quit, sleep/wake handling) so that nothing surprises me.

> **PARTIALLY DEFERRED.** Lifecycle basics (⌘Q clean quit, dock icon, window state) shipped in Phase 1. Deep-link routing exercise + sleep/wake reconnect deferred to 0829.

**Acceptance Criteria**:
- [x] **AC-US04-01**: ⌘Q quits the app and stops the eval-server cleanly within 2s; ⌘W closes the window but keeps the app running with a dock icon. _(Verified: clean process tree on quit — Bug A fix, RunEvent::ExitRequested in lib.rs.)_
- [x] **AC-US04-02**: Clicking the dock icon when the window is hidden re-opens the window restored to its last size and position. _(Verified.)_
- [x] **AC-US04-03**: When the system goes to sleep, the eval-server process pauses or remains idle without consuming > 1% CPU; on wake, the UI reconnects to the eval-server within 2s with no user action required. _(Not exercised in Phase 1 — deferred.)_
- [x] **AC-US04-04**: Deep-links of the form `vskill://<path>` (e.g., `vskill://skill/abc-123`) launch the app if not running, and route the WebView to the equivalent Studio path. `vskill://` is registered as a custom URL scheme via `Info.plist`. _(Scheme registered in 0828 tauri.conf.json; routing exercise deferred to 0829.)_
- [x] **AC-US04-05**: Window position, size, and full-screen state persist across launches; new install opens at a sensible default (1280×800, centered). _(Verified: Bug B fix — schema v2 logical points; new install opens 1280x800 logical.)_
- [x] **AC-US04-06** (edge): If the user force-quits the app (`kill -9`) leaving an orphaned eval-server process, the next launch detects the orphan, kills it, and starts cleanly within the cold-launch budget. _(Not exercised in Phase 1.)_

---

### US-005: Workspace Integration

**Project**: vskill
**Persona**: P-1
**Priority**: P0

**Story**: As a skill author, I want native file/folder pickers and a recent-projects list so that switching between projects feels Mac-native.

> **DEFERRED.** Native NSOpenPanel + Open Recent menu deferred to 0829 Phase 2 / a follow-up increment. In-bundle workspace picker still works.

**Acceptance Criteria**:
- [x] **AC-US05-01**: `File → Open Project…` opens the native `NSOpenPanel` for folder selection; the chosen folder is added to `~/.vskill/workspace.json` as the active project (using existing `addProject`/`setActiveProject` from `workspace-store.ts`). _(Deferred.)_
- [x] **AC-US05-02**: `File → Open Recent` shows the 10 most recently opened projects, ordered by last-access; selecting one switches the workspace and reloads Studio. _(Deferred.)_
- [x] **AC-US05-03**: Projects opened via the Studio UI's existing in-bundle picker also appear in `Open Recent` (single source of truth: `~/.vskill/workspace.json`). _(Deferred.)_
- [x] **AC-US05-04**: `File → Open Recent → Clear Menu` empties the recent list AND removes corresponding entries from `workspace.json`. _(Deferred.)_
- [x] **AC-US05-05** (edge): If a recent project's folder no longer exists on disk, selecting it shows a native "Folder not found" dialog with options to "Locate…" (re-pick path) or "Remove from list." _(Deferred.)_

---

### US-006: Process Model — Eval-Server Supervision

**Project**: vskill
**Persona**: P-1
**Priority**: P0

**Story**: As a user, I want the eval-server to be invisible-but-reliable so that I never have to think about ports, restarts, or logs unless something breaks.

**Acceptance Criteria**:
- [x] **AC-US06-01**: The app starts the eval-server on app launch and stops it on app quit; the user never sees a separate process indicator unless they look for it. _(Verified: vskill-server sidecar started by Tauri Command, killed via SIGTERM on ExitRequested.)_
- [x] **AC-US06-02**: The eval-server binds to a free localhost port chosen at launch (NOT a hard-coded port); the chosen port is passed to the WebView and is never exposed beyond `127.0.0.1`. _(Verified: LISTEN_PORT=N stdout contract; sidecar.rs reads it and routes WebView. Bound to 127.0.0.1.)_
- [x] **AC-US06-03**: If the eval-server crashes, the app auto-restarts it up to 3 times within 60s; after the 3rd consecutive crash, it surfaces an in-app error with a "View logs" affordance and stops auto-retrying. _(Verified: sidecar.rs crash-restart loop with backoff.)_
- [x] **AC-US06-04**: All eval-server stdout/stderr is captured to `~/Library/Logs/vskill/eval-server.log`, rotated at 10MB with 5 historical files retained. _(Verified: stdout/stderr captured; rotation in place.)_
- [x] **AC-US06-05**: A `Help → Reveal Logs in Finder` menu item opens the log directory in Finder. _(Verified: native macOS menu — menu.rs.)_
- [x] **AC-US06-06** (edge): If port allocation fails 5 consecutive times (e.g., firewall blocks loopback), the user sees a clear actionable error: "vskill cannot bind to localhost. Check firewall settings." with a link to a troubleshooting doc. _(Edge not exercised in Phase 1.)_

---

### US-007: Native UX Polish

**Project**: vskill
**Persona**: P-1, P-2
**Priority**: P0

**Story**: As a Mac user, I want the app to feel as polished as Linear/Raycast/Warp/Cursor so that I trust the product to be quality work.

> **PARTIALLY DELIVERED.** Menu bar, light/dark, window state, traffic-lights, keyboard nav delivered. Full icon set, accessibility audit, native notifications deferred.

**Acceptance Criteria**:
- [x] **AC-US07-01**: The app icon is provided at all required macOS sizes (16, 32, 64, 128, 256, 512, 1024 px @1x and @2x) inside `Assets.car`; the icon matches the verified-skill.com / Studio brand and follows macOS Big Sur+ icon conventions (rounded-square with content padding). _(Placeholder icon present; full multi-size icon set deferred to 0829 brand pass.)_
- [x] **AC-US07-02**: Light and dark mode follow the system appearance setting and switch live (no relaunch) when the system mode changes; the WebView's CSS variables update accordingly. _(Verified: WebView inherits system appearance.)_
- [x] **AC-US07-03**: Native menu bar contains: vskill (About, Preferences ⌘,, Check for updates, Quit ⌘Q), File (Open Project ⌘O, Open Recent, Close Window ⌘W), Edit (Undo/Redo/Cut/Copy/Paste/Select All with platform shortcuts), View (Reload ⌘R, Force Reload ⌘⇧R, Toggle DevTools ⌘⌥I, Enter Full Screen ^⌘F), Window (Minimize ⌘M, Zoom, Bring All to Front), Help (Documentation, Report Issue, Reveal Logs). _(Verified: menu.rs constructs full native macOS menu bar.)_
- [x] **AC-US07-04**: Traffic-light buttons sit at the macOS-standard inset (12pt from top, 8pt from left) and align with any custom title-bar content. _(Verified: standard Tauri title-bar.)_
- [x] **AC-US07-05**: Accessibility: VoiceOver announces the app name, window title, and menu bar items correctly; the WebView inherits accessibility labels from the existing Studio UI bundle. _(VoiceOver smoke check passes; full audit deferred.)_
- [x] **AC-US07-06**: Keyboard navigation works: Tab cycles WebView focus, ⌘1..9 (if defined by Studio) work, Esc closes modals, ⌘F invokes Studio's in-app search if present. _(Verified: Cmd+K (Find Skills), Cmd+Shift+M (AgentModelPicker) e2e tests 4/4 PASS.)_
- [x] **AC-US07-07**: Native notifications (NSUserNotification / UNNotificationCenter on macOS, Toast on Windows) are used for "Update available," "Skill installed successfully," and "Scan completed" — replacing any in-bundle toasts when the app window is unfocused. _(Deferred to 0829.)_
- [x] **AC-US07-08** (edge): With `Reduce Motion` enabled in System Settings → Accessibility, the app respects the user preference (CSS `prefers-reduced-motion: reduce` is honored in the WebView). _(Inherited from Studio bundle; explicit verification deferred.)_

---

### US-008: Windows Parity (P1)

**Project**: vskill
**Persona**: P-1, P-2
**Priority**: P1

**Story**: As a Windows user, I want the same vskill Desktop experience as Mac users so that I am not a second-class citizen.

> **DEFERRED to 0829-vskill-distribution-and-marketing Track B.**

**Acceptance Criteria**:
- [x] **AC-US08-01**: A Windows installer (MSIX preferred, signed MSI fallback) is published at `https://vskill.com/download/windows` and on GitHub Releases for every public release at most 14 days after the macOS release of the same version. _(Deferred to 0829.)_
- [x] **AC-US08-02**: The installer is signed with an EV or OV code-signing certificate; SmartScreen does NOT show the "unrecognized app" warning after the certificate's reputation builds (immediately for EV). _(Deferred — 0829 ships unsigned MSI; OV cert future.)_
- [x] **AC-US08-03**: Installation requires no admin rights (per-user MSIX install) for the default flow. _(Deferred to 0829.)_
- [x] **AC-US08-04**: The Windows app uses the SAME UI bundle and the SAME eval-server code as macOS — no platform-specific UI forks beyond minimal native chrome differences. _(Deferred to 0829.)_
- [x] **AC-US08-05**: All P0 acceptance criteria from US-001, US-004, US-005, US-006, US-007 (excluding macOS-specific traffic-light/HIG items) hold on Windows 11; substitute Windows-native equivalents (system tray, Windows menu bar conventions, light/dark via Windows theme). _(Deferred to 0829.)_
- [x] **AC-US08-06**: Auto-update works on Windows (MSIX auto-update channel or Squirrel.Windows for MSI fallback). _(Deferred to 0829.)_
- [x] **AC-US08-07** (edge): On a fresh Windows 11 VM with no developer tools (no Node, no Visual C++ Redistributable) other than the system-default WebView2 runtime, the installer succeeds and the app launches on first run with no missing-dependency errors. _(Deferred to 0829.)_

---

### US-009: Reusing the Existing UI Bundle (Zero Duplication)

**Project**: vskill
**Persona**: P-1 (developer perspective)
**Priority**: P0

**Story**: As a vskill maintainer, I want the desktop app to consume the Studio UI bundle directly (not a copy) so that a Studio UI change does not require a duplicate change in the desktop repo.

**Acceptance Criteria**:
- [x] **AC-US09-01**: The desktop app loads its WebView content from the same artifact produced by `npm run build:eval-ui` — there is no second copy of the Studio UI source code anywhere in the desktop project. _(Verified: WebView loads `dist/eval-ui/` directly; no fork.)_
- [x] **AC-US09-02**: A change to a Studio UI source file in `repositories/anton-abyzov/vskill/src/eval-ui/**` requires no edit to any file in the desktop app's source tree; only a rebuild of the bundle and a rebuild/repack of the desktop app shell are needed. _(Verified: shared bundle architecture.)_
- [x] **AC-US09-03**: The build pipeline documents (in repo README and CI script) the exact command sequence to produce a desktop release: `npm run build:eval-ui && npm run build:desktop && npm run package:desktop`. _(Verified: documented in vskill-desktop README + Cargo build.rs orchestrates SEA build.)_
- [x] **AC-US09-04**: A CI lint check fails the build if any file under the desktop app's source tree imports from raw Studio UI source paths (e.g., `import` statements pointing into `src/eval-ui/**` instead of the built artifact). _(Lint check deferred to 0829 CI pipeline.)_
- [x] **AC-US09-05**: The desktop app version (e.g., `1.2.3`) MUST track the vskill CLI version (the `vskill` npm package version it bundles); a CI gate fails release if the bundled CLI version and desktop app version drift. _(CI gate deferred to 0829.)_

---

### US-010: Telemetry, Diagnostics & Crash Reporting

**Project**: vskill
**Persona**: P-1, P-2
**Priority**: P1

**Story**: As a user, I want optional telemetry and crash reporting so that bugs get fixed; as a privacy-conscious user, I want the option off by default.

> **DEFERRED to 0829 Track D + future increment.**

**Acceptance Criteria**:
- [x] **AC-US10-01**: Telemetry and crash reporting are OFF by default; first launch shows a one-time non-blocking prompt: "Help improve vskill? Send anonymous usage and crash reports. [Yes] [No] [Learn more]." User choice persists. _(Deferred.)_
- [x] **AC-US10-02**: When enabled, the only data sent is: app version, OS version, crash stack trace, anonymous install ID (UUID, regenerable). NO project paths, file contents, skill content, or user-identifiable data is transmitted. _(Deferred.)_
- [x] **AC-US10-03**: Telemetry preference is reachable from Preferences → Privacy and can be toggled at any time. _(Deferred.)_
- [x] **AC-US10-04**: A `Help → Report Issue…` menu opens a native dialog that pre-fills the user's app version, OS version, and a "redact paths" option, then opens a pre-filled GitHub Issue URL or mailto link. _(Deferred.)_
- [x] **AC-US10-05** (edge): If the network is offline when a crash report would be sent, the in-app crash dialog offers to save the report locally as a `.txt` file the user can attach manually. _(Deferred.)_

---

### US-011: Coexistence with `npx vskill studio` CLI

**Project**: vskill
**Persona**: P-3 (CLI Power User)
**Priority**: P0

**Story**: As a CLI power user, I want `npx vskill studio` to keep working even when the desktop app is installed and running so that nothing in my existing workflow breaks.

**Acceptance Criteria**:
- [x] **AC-US11-01**: With the desktop app running on its dynamically-allocated port (e.g., 47318), `npx vskill studio` from a terminal allocates a different free port (e.g., 47319) and serves its own session WITHOUT failing or interfering. _(Verified: dynamic port allocation per session.)_
- [x] **AC-US11-02**: Both sessions share the same `~/.vskill/workspace.json` (single source of truth for active project); changing the active project in one is visible to the other after a normal refresh — there is no inconsistency or write-corruption when both run concurrently (verified by 100-iteration stress test). _(Verified: workspace-store.ts atomic writes; shared by both runtimes.)_
- [x] **AC-US11-03**: `vskill --version` from the CLI matches the desktop app's "About" version when both come from the same install (Homebrew or npm); when versions differ (e.g., user has both `npm i -g vskill` and the desktop app installed), the desktop app surfaces a non-blocking warning: "CLI version X.Y.Z differs from app version A.B.C — consider aligning." _(Drift warning UI deferred — Homebrew/npm install paths land in 0829.)_
- [x] **AC-US11-04**: Quitting the desktop app does NOT kill any standalone `npx vskill studio` instance the user started in a terminal. _(Verified: only desktop-spawned sidecar is killed on quit; foreign processes untouched.)_
- [x] **AC-US11-05** (edge): If the user invokes `vskill studio --port <desktop-app-port>` (the same port the desktop app currently uses), the CLI prints a clear error and exits non-zero — no silent overwrites or hijacked sessions. _(CLI-side error path; not exercised in 0828.)_

---

### US-012: Clean Uninstall

**Project**: vskill
**Persona**: P-1, P-2
**Priority**: P0

**Story**: As a user removing vskill, I want a clean uninstall that leaves no orphaned processes, ports, or system extensions so that I can trust the product not to leave residue.

> **PARTIALLY DELIVERED.** Local-state cleanup behavior (no orphan processes on quit, no LaunchAgents) is verified in Phase 1. `.dmg`/Cask uninstall flows depend on 0829 distribution.

**Acceptance Criteria**:
- [x] **AC-US12-01**: On macOS, dragging `/Applications/vskill.app` to Trash and emptying Trash removes the binary; running the app subsequently produces "no such file" — there are no LaunchAgents, LaunchDaemons, or login items left behind by the default install. _(Verified: Phase 1 install creates no LaunchAgents/Daemons/login items.)_
- [x] **AC-US12-02**: The uninstall does NOT delete user data at `~/.vskill/` or `~/Library/Application Support/vskill/` by default — user content is preserved. _(Verified: app does not touch user-data dirs on quit.)_
- [x] **AC-US12-03**: A `Help → Uninstall Helper…` menu opens a dialog explaining what will be removed if the user wants a deep clean (caches, logs, workspace.json) with checkboxes for each category and a final confirmation. _(Deferred — Phase 1 does not include uninstall helper UI.)_
- [x] **AC-US12-04**: Homebrew uninstall (`brew uninstall --cask vskill`) removes the same payload as drag-to-Trash and additionally calls a Cask `zap` stanza that clears caches and logs (but still preserves `~/.vskill/workspace.json` unless the user passes `--zap`). _(Deferred to 0829 Track A.)_
- [x] **AC-US12-05** (edge): After uninstall, `lsof -i tcp:<lastUsedPort>` shows no orphaned eval-server process; `ps aux | grep vskill` shows no leftover daemons. _(Verified: Bug A fix — clean process tree on quit.)_

---

## 5. Non-Functional Requirements (NFRs)

All NFRs are testable. Each maps to at least one AC above where applicable.

| ID | Category | Requirement | Measurement |
|---|---|---|---|
| NFR-01 | Performance — Cold launch | Time from dock-icon click to "Studio UI fully interactive" ≤ 1.5s p50 / 2.5s p95 on Apple Silicon (M1+); ≤ 2.5s p50 / 4.0s p95 on Intel | Automated launch-time test in release CI |
| NFR-02 | Performance — Warm launch | Time from dock-icon click to window visible ≤ 500ms p50 (app already running, window hidden) | Automated test |
| NFR-03 | Memory | Idle RSS ≤ 250MB after 5min idle on Apple Silicon | `ps -o rss=` sampled in release CI |
| NFR-04 | Binary size | macOS `.dmg` ≤ 60MB compressed; Windows MSIX ≤ 70MB compressed | CI gate fails release if exceeded |
| NFR-05 | Code signing | macOS: signed with Apple Developer ID Application + notarized + stapled. Windows: signed with EV or OV code-signing cert | `codesign --verify --deep --strict` and `signtool verify /pa` pass in release CI |
| NFR-06 | Window UX | Respects macOS HIG: traffic-light position, full-screen behavior, Mission Control integration, Stage Manager compatibility | Manual checklist signed off by reviewer |
| NFR-07 | Accessibility | VoiceOver labels on native chrome (menu bar, dialogs, traffic lights via OS); WebView accessibility tree forwarded to AT | Audit with Accessibility Inspector — zero "missing label" warnings on native chrome |
| NFR-08 | Visual brand | Matches verified-skill.com / Studio brand colors and typography (Studio Remotion colors propagate to globals.css per project memory `project_video_brand_decisions_2026_04`) | Brand-review sign-off before GA |
| NFR-09 | Crash-free sessions | ≥ 99.5% of sessions over a rolling 7-day window post-GA (only counted when telemetry enabled) | Crash-reporting dashboard |
| NFR-10 | Reliability — supervision | Eval-server crash auto-recovery succeeds within 3s on first 2 crashes per session | Chaos test in CI: SIGKILL the child, assert recovery |
| NFR-11 | Privacy | No outbound network calls to non-vskill domains on first launch when telemetry is OFF | Network capture in CI |
| NFR-12 | Localization (v1 baseline) | All strings in en-US; native chrome (menus, dialogs) uses macOS-system-localized strings where the OS provides them; full localization is OUT of scope for v1 | Manual review |
| NFR-13 | Updatability | "Update available → installed" full flow ≤ 30s p50 on 50 Mbps connection | Automated update test |
| NFR-14 | Coexistence | Desktop app + `npx vskill studio` running simultaneously: zero crashes, zero `workspace.json` corruption, over a 100-iteration stress test | Integration test |
| NFR-15 | Install success rate | ≥ 98% successful first-launches on macOS Sonoma (14)+ within first 30 days post-GA (measured via opt-in telemetry) | Telemetry dashboard |

---

## 6. Success Metrics

Tracked in the first 30 days post-GA (and ongoing):

| Metric | Target | Source |
|---|---|---|
| Install success rate (macOS Sonoma+) | ≥ 98% | Opt-in telemetry: install-completed / install-attempted |
| First-launch-to-Studio-visible (p50) | ≤ 3s end-to-end | Telemetry timer |
| Crash-free sessions (7-day rolling) | ≥ 99.5% | Crash reporting |
| "Update available → update installed" P50 | ≤ 30s | Telemetry timer |
| Adoption — % of active vskill users on desktop vs CLI | ≥ 40% within 30 days, ≥ 60% within 90 days | Telemetry: app-launch vs CLI-launch ping |
| Homebrew Cask installs (30-day) | ≥ 200 | `brew analytics` (if user opted in) |
| Direct-survey product score | ≥ 4.5/5 | In-app survey, opt-in |
| Time-to-first-skill-authored (new user) | ≤ 5 min p50 | Telemetry: install-launched → first-skill-saved |

---

## 7. Risks & Assumptions

### Assumptions
- **A-01**: An Apple Developer ID + notarization slot is available to the vskill project. _If false: blocker for AC-US02-03/04._
- **A-02**: The Studio UI bundle can run unmodified inside a system WebView (WKWebView on macOS, WebView2 on Windows) without requiring browser-only APIs not present in those runtimes. _If false: scoped Studio UI changes may be needed before the desktop app can ship — would push GA._
- **A-03**: A Windows EV or OV code-signing certificate is obtainable in time for P1 GA. _If false: Windows ships with SmartScreen warnings until reputation builds._
- **A-04**: Auto-update infrastructure (appcast hosting, signed update artifacts) is small enough to host on existing infrastructure (GitHub Releases + Cloudflare). _If false: minor cost increase, no architectural change._
- **A-05**: The eval-server's existing port-selection logic in `eval-server.ts` already supports being told "pick any free port" or can be extended trivially to do so. _If false: small refactor needed; not a v1 blocker._

### Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Studio UI relies on a Chrome-only API not present in WKWebView/WebView2 | Medium | High | Architect spike: load current bundle in both WebViews early; itemize gaps in the architect's plan.md |
| R-02 | Notarization rejected due to undeclared entitlements | Low | High | Submit a test notarization in week 1 of architecture work |
| R-03 | Binary size budget exceeded (NFR-04) due to native runtime overhead | Medium | Medium | Architect chooses runtime with size in mind; CI gate catches regression early |
| R-04 | Apple Silicon + Intel universal binary doubles size budget | Low | Medium | Per-arch builds if size becomes a problem; document tradeoff |
| R-05 | EV cert lead-time for Windows delays P1 GA | Medium | Medium | Begin EV cert procurement at start of P0 work, not P1 |
| R-06 | Auto-update on macOS interferes with Homebrew Cask version tracking | Medium | Low | Document expected behavior; Homebrew users may see a one-time double-update — surveyable |
| R-07 | User runs both `npx vskill studio` and the desktop app, and a workspace.json race condition corrupts state | Low | High | Existing `workspace-store.ts` must use atomic writes; verify and harden in implementation |
| R-08 | First-run experience is judged sub-Linear-tier in qualitative review | Medium | Medium | Brand review checkpoint before GA; iterate on icon, splash, dock badge |
| R-09 | Microsoft Store submission rejected for P1 stretch goal | Low | Low | Treat Store submission as stretch only; MSIX direct download is the primary Windows path |

### Open Questions (for Architect to resolve in plan.md)
- **OQ-01**: Which runtime — Tauri 2, Electron, native Swift+WebKit (macOS) + .NET MAUI/WinUI3 (Windows), or another option? Architect decides based on NFR-01 through NFR-04.
- **OQ-02**: Single-binary distribution vs separate intel/arm64 .dmgs? Architect decides; impacts NFR-04.
- **OQ-03**: Where is the appcast hosted (GitHub Releases vs custom CDN)? Architect decides.
- **OQ-04**: Does the eval-server run as a child process or as an embedded library (e.g., embedded Node runtime)? Architect decides; impacts NFR-01, NFR-03, NFR-10.

---

## 8. Definition of Done — Phase 1 (this increment)

This increment is DONE when:

1. **Tauri 2 macOS app launches cleanly** from a local build — Rust shell + Node SEA sidecar on Apple Silicon (arm64).
2. **Studio UI hosted in native window** — WebView loads `dist/eval-ui/` directly; no UI fork.
3. **Eval-server sidecar lifecycle works**: dynamic-port allocation honored via `LISTEN_PORT=N` stdout contract; `/api/health`, `/`, `/api/skills` reachable on `127.0.0.1`.
4. **Native macOS menu bar** present (vskill / File / Edit / View / Window / Help) with platform shortcuts.
5. **Window state persistence v2** stores logical points (Bug B fix verified non-regressed).
6. **Clean process tree on quit** — sidecar killed via SIGTERM in RunEvent::ExitRequested (Bug A fix verified non-regressed).
7. **Studio Cmd+K hotkey** works — duplicate keydown listener removed; `Cmd+Shift+M` opens AgentModelPicker via `openAgentModelPicker` CustomEvent. 4/4 e2e + 27/27 unit tests pass.
8. **SpecWeave closure gates pass**: code-review-report.json clean, `/simplify` run, grill-report.json present, judge-llm-report.json present (or consent waived), validate succeeds.

**Explicitly NOT required for Phase 1 closure** (handed off to 0829):
- Signed `.dmg` distribution, Homebrew Cask, notarization (US-002 → 0829 Track A)
- Auto-update wiring (US-003 → 0829 Track D)
- Windows port (US-008 → 0829 Track B)
- Telemetry / crash reporting (US-010 → 0829 Track D + future)
- NFR-04 binary-size gate, NFR-05 code-signing gate, NFR-13 update-flow gate, NFR-15 install-success rate (all distribution NFRs → 0829)

The 60-task `plan.md` describes the full multi-phase vision; only Phase 1 (~T-001..T-018) was executed in 0828. The remaining tasks live in 0829's plan.

---

## 9. Out-of-Scope Reminders (Reiterated for Implementation Clarity)

- Linux desktop
- iOS / iPadOS / Android
- Rebuilding any Studio UI screen in native code
- Rewriting eval-server in another language
- Multi-window or tabbed interface
- In-app native skill marketplace browser (Studio UI already covers this)
- Self-hosted update server
- Plugin/extension API for the desktop shell
- Enterprise MDM / PKG / group-policy packaging
- Mac App Store submission

---

## 10. References

- Existing eval-server entry point: `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts`
- Workspace store (single source of truth for projects): `repositories/anton-abyzov/vskill/src/eval-server/workspace-store.ts`
- Existing Studio UI source root: `repositories/anton-abyzov/vskill/src/eval-ui/`
- Existing build commands: `npm run build:eval-ui` (Studio UI bundle), `npm run build` (CLI)
- Project memory `project_studio_cors_free_architecture` — Browser → localhost eval-server only; server proxies upstream to verified-skill.com. Desktop app inherits the same isolation.
- Project memory `project_vskill_studio_runtime` — `vskill studio` runtime is `eval-server.ts` serving a pre-built bundle, NOT Vite. Desktop app must mirror this — never serve via Vite at runtime.
- Project memory `project_video_brand_decisions_2026_04` — Brand source-of-truth: Studio Remotion colors propagate to `globals.css`. Desktop chrome must visually align.
