# Installed pages: desktop powers with per-version consent

## Problem

Slice 1 (1475, PR anton-abyzov/specwithcode#927) installs a SpecWithCode page as its own desktop app, but the page can still only do what it can in a browser. On November 24, 2026 Anthropic shipped "Install as app" in Claude for Mac and Windows. The official article (claude.com/resources/articles/install-as-app) and Felix Rieseberg's launch thread describe three levels:

- **Default:** browser-only.
- **App permissions:** "always-on-top windows, listening for global shortcuts, or sending notifications"; "notifications or add items to your menu bar or system tray".
- **Full computer access:** run programs, read or change files.

Consent is per app and per version: "Claude asks again after every update, even your own edits". The article also states: "You don't have to package or sign it."

Felix's demos (a menu bar break reminder, desktop pets in transparent windows, a terminal, a file manager) use exactly these powers. A SpecWithCode page installed today cannot remind, sit on top, answer a shortcut or live in the menu bar, so it is a window and not yet an app.

## Scope

In:

- The app-permissions level for installed pages: notifications, a menu bar or tray item with a small menu, always on top, and global shortcuts.
- Each power is declared by the page, granted by the person in a native dialog, and granted again for every new page version.
- It is shown and revocable from the installed page's window.
- It works the same on macOS, Windows and Linux.

Out:

- Full computer access (run programs, files) and pages calling agents or connectors (owner decision, D-01).
- Sharing an installed page with other people or accounts (1480 C4, named end-to-end invites).
- Transparent or frameless windows.
- Per-OS packaged binaries and signing: Claude ships none, and slice 1's launcher needs none (D-02).

## Acceptance Criteria

- [ ] AC-01: A page declares the powers it wants in a manifest. The manifest is `<script type="application/specwithcode-app+json">{"permissions":[...]}</script>`, where each permission is one of `notifications`, `tray`, `always-on-top` or `global-shortcuts`. The shell reads the manifest from the page's file, never from the frame. Unknown names, duplicates and malformed JSON are ignored, and at most 4 shortcuts are allowed.
- [ ] AC-02: When an installed page opens a version (attachment) whose declared powers are not yet granted, the shell shows a native dialog listing them in plain words. Cancel is the default. The answer is recorded for that install, that version and the sha256 of the bytes the shell read. A newer version, or the same version whose file changed, asks again, and a version that declares nothing never asks.
- [ ] AC-03: The page asks through the existing html_render JSON-RPC channel (`window.parent.postMessage`). The view accepts a message only from its own frame. The shell runs a request only for the calling installed-page window's install, only when the current version's grant includes that power and the file still has the granted hash. It refuses anything else with an error reply. Any error while reading the grant, the manifest or the file, or while looking up the window, means no power. A test covers both the view gate and the shell refusal.
- [ ] AC-04: `notifications`: `app/notify {title, body}` shows a native notification titled with the app name. Clicking it focuses the page's window. A page may show at most 10 per minute.
- [ ] AC-05: `tray`: `app/tray/set {title?, tooltip, items:[{id,label}]}` shows one menu bar or tray item per install with the SpecWithCode icon. It has at most 12 items plus Open and Close app. A click on an item posts `app/tray/clicked {id}` to the page. The item goes away when the window closes or the grant ends.
- [ ] AC-06: `always-on-top`: `app/window/always-on-top {on}` keeps the page's window above others, or stops doing so.
- [ ] AC-07: `global-shortcuts`: `app/shortcut/register {accelerator}` registers an accelerator that passes Electron's checks and is not used by the app or another install. A press posts `app/shortcut/pressed {accelerator}`. All of a page's shortcuts are released when its window closes, the version changes or the grant ends.
- [ ] AC-08: The installed page's header has a Permissions menu that lists the powers granted to this version and offers "Turn off all". Turning them off removes the grant, the tray item and the shortcuts at once. Uninstalling forgets the grants.
- [ ] AC-09: The installed page's frame cannot navigate away from its own version. The shell blocks every subframe navigation in an installed-page window except to that version's own URL, whether by script, form or refresh, so new content never inherits the page's powers.

## Approach

- **Desktop, `apps/desktop/src/artifactApps/`:**
  - `ArtifactAppPowers.ts` (pure): manifest parse, request validation, plain-word labels.
  - `ArtifactAppGrants.ts`: a 0600 JSON store of `{installId, attachmentId, powers}`, built on the same atomic write as `ArtifactAppRecords`.
  - `ArtifactAppPowersHost.ts`: the Electron seam for Notification, Tray, `globalShortcut` and `setAlwaysOnTop`, faked in tests.
  - IPC: `artifactAppPower` and `artifactAppPermissions` in `ipc/methods/artifactApps.ts`, answered only for page windows through `ArtifactAppWindows.installIdForWebContents`.
  - Consent dialog on version open: through the installer's dialog seam.
- **Contracts:** `packages/contracts/src/artifactApps.ts` gains the power names, the request and reply union, and the bridge methods.
- **Web:**
  - `ArtifactAppView.tsx` listens on the frame's channel and forwards only from its own frame.
  - `components/artifactApps/ArtifactAppPermissions.tsx` is the header menu.
  - A pure `artifactAppPowerMessages.ts` defines the JSON-RPC shapes.
- **html_render tool description:** a short paragraph tells agents how to declare and call powers.
- **Rejected:**
  - Per-OS packaged binaries, CI builds and signing per page: hundreds of MB each, no shared sign-in, and Claude doesn't do it either.
  - Exposing Electron APIs to the frame: the frame stays sandboxed without same-origin.
  - Granting once per install: Claude asks per version, and a page's code can change.
- **Risks:**
  - Global shortcuts can collide with other apps; registration refuses rather than steals.
  - The file is hashed when a request runs, but the frame may hold bytes it loaded earlier. A page rewritten between load and request runs its old, granted code; a page rewritten before load fails the hash and is refused.
  - Linux tray support depends on the desktop environment, so a failed tray shows an error reply.

## Decisions

### Asked
- none yet
### Defaulted (change any before sw-do)
- D-01: Full computer access (programs, files) and pages calling agents or connectors stay out. Both widen what a page can do on the machine, and they wait for the owner.
- D-02: No per-OS packaging or signing. Claude's article says "You don't have to package or sign it", and slice 1's launcher is a few unsigned files plus an ad-hoc macOS signature. This changes the owner's "per-OS packaging and signing, Windows and Linux builds via CI" ask, for the reason above.
- D-03: Consent is per version, as Claude does. A version is the attachment id plus the sha256 of its bytes, because an attachment file is not immutable: agents run as the same user and can rewrite it under the same id.
### Open
- none

## Tasks

### T-01 Manifest, request validation and grants store
- AC: AC-01, AC-02, AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/artifactApps.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppPowers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppGrants.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppPrivateFile.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppRecords.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ArtifactAppPowers.test.ts apps/desktop/src/artifactApps/ArtifactAppGrants.test.ts

### T-02 Powers host, consent and IPC in the shell
- AC: AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppInstaller.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/artifactApps.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppPowersHost.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppPowerService.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/artifactApps.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/main.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/DesktopIpcHandlers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppInstaller.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ apps/desktop/src/ipc/methods/artifactApps.test.ts

### T-03 Page channel and Permissions menu in the installed page's window
- AC: AC-03, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/ArtifactAppView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/artifactAppPowerMessages.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/ArtifactAppPermissions.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/html/tools.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/artifactApps/
