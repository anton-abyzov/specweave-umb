# Install a SpecWithCode page as a desktop app

## Problem

On November 24, 2026 Anthropic shipped "Install as app" (beta) in Claude Desktop 6.28899: an artifact becomes a Mac or Windows app with its own icon and window that always shows the newest published version. SpecWithCode agents publish the same kind of pages (html_render reports, dashboards, small tools), but a person can only reach one by opening its thread and pressing Open report. A page a person checks every morning has no icon of its own, no window of its own and disappears into the thread history.

Evidence: the research and clean-room spec in this increment's `reports/` (web research, a static look at the shipped Claude 6.28899.6 bundle, and a design with options). Claude's version is macOS and Windows only; SpecWithCode ships on macOS, Windows and Linux.

## Scope

In:

- Install as app for an html_render report page, from the report's header in the desktop app.
- A private install record per machine and a per-OS launcher: a macOS `.app` bundle in `~/Applications/SpecWithCode Apps/`, Windows Start menu and Desktop shortcuts with their own taskbar identity, and a Linux desktop entry.
- A launcher passes only a random install id through the app's URL scheme; the app opens one window per install showing the newest page with that title in that thread, in the same sandboxed frame the thread uses.
- Uninstall and reveal from the app window; a calm state when the thread, page or machine is gone.

Out (later slices): desktop powers for pages (notifications, tray, global shortcuts, always on top, files and processes) with a declared manifest and per-version consent; a persistent macOS launcher with its own Dock identity; agents asking to install a page; importing a Claude artifact; installing design studio pages, sheets or whiteboards; the web and phone clients.

## Acceptance Criteria

- [ ] AC-01: A page title becomes a safe app name: Unicode normalized, path separators and control characters removed, leading dots and a trailing `.app` trimmed, at most 64 characters, an "Untitled page" fallback, and " (Page)" appended when it imitates SpecWithCode, Apple, Microsoft, Finder, System Settings or another installed app (case and homoglyph folded); a counter keeps it unique.
- [ ] AC-02: The install record lives in the app's user data as a 0600 JSON file with a random 128-bit hex install id, the environment, thread, page title, page attachment id, launcher name and time; malformed entries are dropped on read and writes are atomic.
- [ ] AC-03: The launcher generators produce, from an install id and name only: a macOS `Info.plist` (bundle id per install, the SpecWithCode icon) and launcher script that opens `<scheme>://app/artifact-app/<installId>`; a Linux `.desktop` entry with the same URL; Windows shortcut options that start SpecWithCode with that URL and a per-install AppUserModelID. No generator accepts a path, URL or page id from outside.
- [ ] AC-04: The app accepts an artifact-app URL from `open-url`, a second launch's argv or its own start argv, parses only a well-formed install id, ignores ids not in the record, and opens or focuses that install's window; at most 10 such windows are open at once.
- [ ] AC-05: An installed-page window has role `artifact-app`, uses the same sandbox, context isolation and preload as project windows, sends any navigation away from its route and any new window to the system browser, and is titled with the app name; on Windows it carries the install's AppUserModelID.
- [ ] AC-06: The window's route resolves the install through the bridge, shows the newest completed html_render page in that thread with the same title (falling back to the attachment id from install time) full-window in the existing sandboxed page frame, and shows a plain message when the install, thread or page is not available.
- [ ] AC-07: In the desktop app, a report's header offers Install as app; the shell asks the person to confirm in a native dialog (Cancel is the default), writes the launcher, records the install and opens the window. Installing the same page again says it is already installed. Web and phone clients show no install control.
- [ ] AC-08: Uninstall (from the installed-page window) removes the launcher (macOS bundle to the Trash, Windows shortcuts and the Linux entry deleted), forgets the record and closes the window; reveal shows the launcher in the file manager.

## Approach

The design and its rejected options are in `reports/install-as-app-research-and-design.md`. Summary:

- Option A (chosen): the app owns the window and the page; the launcher is a few files that open the app's URL with an install id. Rejected: a generated Electron app per page (hundreds of MB each, no shared sign-in or data), a Tauri stub per page (toolchains per OS; kept for a later offline export), and a browser PWA install (no system access, needs a hosted origin).
- Contracts: `packages/contracts/src/artifactApps.ts` (schemas and the bridge methods); `DesktopBridge` extends it and `getWindowRole` gains `artifact-app`.
- Desktop, new folder `apps/desktop/src/artifactApps/`: pure `ArtifactAppName.ts`, `ArtifactAppLaunchers.ts`, `ArtifactAppUrl.ts`; `ArtifactAppRecords.ts` (record store); `ArtifactAppInstaller.ts` (writes and removes launchers, ad-hoc `codesign` on macOS when present, `shell.writeShortcutLink` on Windows); `ArtifactAppWindows.ts` (window manager); IPC methods in `apps/desktop/src/ipc/methods/artifactApps.ts`; URL routing beside the existing `open-url` and `second-instance` handlers. `DesktopWindow.ts` is already over 1,500 lines and is not touched.
- Web: route `artifact-app.$installId.tsx`, a bare layout for it in `__root.tsx`, the view in `components/artifactApps/`, and the install button in `HtmlRenderFrame.tsx`.
- Security: the launcher carries only an install id that must be in the record; the page stays in the sandboxed iframe (`allow-scripts allow-forms`), never top-level, so it is never same-origin with the app; signed asset URLs are minted per window by the existing path.
- Risks and proof limits: the macOS launcher exits after opening the URL, so the window shows under SpecWithCode in the Dock (Claude keeps a persistent shim). Windows behaviour is checked by generator tests, not on a Windows machine. No test opens a launcher against the live app.

## Decisions

### Asked
- none (the owner asked to implement it as Claude Code does, on every OS)
### Defaulted (change any before sw-do)
- D-01: Identity is environment + thread + page title; the newest page with that title is shown (Claude shows the newest published version on each launch). The install-time attachment id is the fallback.
- D-02: Slice 1 gives the page no desktop powers beyond what it has inline today.
- D-03: macOS install folder `~/Applications/SpecWithCode Apps/` (Claude uses `~/Applications/Claude Apps/`); Windows Start menu folder "SpecWithCode Apps" plus a Desktop shortcut; Linux `~/.local/share/applications/`.
### Open
- none

## Tasks

### T-01 Name, URL, launcher generators and record store
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/artifactApps.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppName.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppUrl.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppLaunchers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppRecords.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ArtifactAppName.test.ts apps/desktop/src/artifactApps/ArtifactAppUrl.test.ts apps/desktop/src/artifactApps/ArtifactAppLaunchers.test.ts apps/desktop/src/artifactApps/ArtifactAppRecords.test.ts

### T-02 Installer, windows, URL routing and IPC in the desktop shell
- AC: AC-04, AC-05, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppInstaller.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppRouting.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/artifactApps.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/DesktopIpcHandlers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/main.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ && node node_modules/typescript/bin/tsc --noEmit --project apps/desktop/tsconfig.json

### T-03 Installed-page route, view and Install as app button
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/routes/artifact-app.$installId.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/__root.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/ArtifactAppView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/artifactAppPage.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/InstallAsAppButton.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HtmlRenderFrame.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/artifactApps/ && cd .. && cd .. && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json
