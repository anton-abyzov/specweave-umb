# Installed pages run as their own macOS apps

## Problem

On macOS an installed page is a window of the SpecWithCode process. Its launcher in `~/Applications/SpecWithCode Apps/<Name>.app` is a shell script that runs `open specwithcode-app://<id>` and exits. So the Dock, the app switcher and the menu bar all show SpecWithCode, not the page. Before 1499 added its Command-Q intercept, Command-Q in a page quit SpecWithCode and every window. The owner hit this ("if I close it, it seems like it's closing the whole SpecWeave Code application").

Claude desktop 6.28899.6 makes each installed artifact its own app with Electron's app-shim, from the REA in `1499-motion-slide-pages/reports/owner-questions-reports-and-installed-apps.md`. The bundle's executable is Electron's `app_shim_loader`. The shim connects to Claude's app-shim server, Claude checks its code hash and opens a window inside the shim. That gives the page its own Dock icon, menu bar and Command-Q. On November 27, 2026 the owner approved the same model for SpecWithCode ("implement it similar to Claude's implementation ... implement fully as recommended").

Evidence that it works on our stack:

- Electron 44.10.1 (`apps/desktop/package.json`) has `app.startAppShimServer`, `app-shim-connected`, `AppShimHost` and the `appShim` window option.
- The packaged SpecWithCode.app ships `Contents/Frameworks/Electron Framework.framework/Versions/A/Helpers/app_shim_loader`.
- A scratch proof with Electron 44.10.1 worked (`~/.specwithcode/m4/scratch/2026-11-27-app-shim-poc/`):
  - an ad-hoc signed shim bundle connected;
  - `satisfiesCodeRequirement('cdhash H"<hash>"')` was true for its hash and false for another;
  - a window opened inside the shim;
  - `shim.quit()` closed the window and emitted `disconnected`;
  - a shim started with the host not running launched the host with its `ElectronAppShimHostArguments` and connected.

## Scope

In:

- macOS launchers built from Electron's shim loader, ad-hoc signed, with the code hash recorded.
- A shim server in SpecWithCode that checks every shim before opening its window.
- A per-page menu bar.
- Quitting a page quits only that page.
- Pages that were open come back after SpecWithCode restarts.
- Existing script launchers are upgraded at start.
- A message when SpecWithCode was updated while running.

Out:

- Windows and Linux, which keep their shortcut and desktop-entry launchers.
- Claude's "accessory" mode, where a cold launch by a page hides SpecWithCode's own Dock icon. SpecWithCode opens normally; this is a deliberate difference.
- Page-chosen window styles.
- `putAway` (hide instead of close).
- Full computer access for pages, which waits for the owner.

## Acceptance Criteria

- [ ] AC-01: **Shim launcher.** On macOS, in a packaged build whose shim loader exists, installing a page writes `<Name>.app`. The bundle's executable is a copy of `app_shim_loader`. Its Info.plist carries:
  - `ElectronAppShimHostPath` (the running SpecWithCode.app);
  - `ElectronAppShimHostBundleIdentifier`;
  - `ElectronAppShimServerName` (`<bundle id>.artifact-apps`);
  - `ElectronAppShimHostArguments` (`["--specwithcode-artifact-app-launch"]`);
  - the existing install-id key.

  The bundle is ad-hoc signed and its CDHash is recorded in a desktop-only file, `artifact-app-shims.json` (0600), never in the client-facing record. A development build, or a build with no loader, keeps today's script launcher.
- [ ] AC-02: **Only our shims open windows.** SpecWithCode starts its shim server once the app is ready. For each connecting shim it:
  - finds the install whose launcher path is the shim's `bundlePath`;
  - checks `satisfiesCodeRequirement('cdhash H"<recorded>"')`.

  An unknown bundle, a changed bundle, or one whose hash does not match is turned away with `shim.quit()` and opens nothing. The check runs only after the main window exists, like every other launch.
- [ ] AC-03: **The window belongs to the page.** A verified shim gets the install's window created with the `appShim` option, so the Dock, app switcher and menu bar show the page's name and icon. If a window for that install is already open outside a shim, it is closed and replaced. Revealing a shim window never calls `app.focus`, which would bring SpecWithCode forward.
- [ ] AC-04: **Per-page menu bar.** The shim's menu bar has:
  - an app menu named after the page: About, Show App in Finder, Uninstall, Hide, Hide Others, Show All, Quit;
  - Edit with the standard roles;
  - View: Reload, Actual Size, Zoom In, Zoom Out, Enter Full Screen;
  - Window: Minimize, Zoom, Close.

  Show App in Finder and Uninstall call the installer's `reveal` and `uninstall`. Command-Q quits the shim, which closes only that page; SpecWithCode keeps running.
- [ ] AC-05: **One lifetime.** Closing the page window quits its shim, so no Dock icon is left with no window. Uninstall closes the window and quits the shim. A click on the shim's Dock icon, or a second launch, focuses its window, or reopens it if it is gone.
- [ ] AC-06: **Reopen after restart.** When SpecWithCode quits, the install ids of open shim windows are written to `artifact-apps-reopen.json` (0600). At the next start, after the main window exists, each id that is still recorded and whose launcher is still owned is opened again by launching its bundle. The file is then removed.
- [ ] AC-07: **Existing launchers are upgraded.** At start on macOS with shims available, each recorded install is rebuilt as a shim through the same staging, ownership check, sign and swap path. This covers a script launcher, and a shim whose recorded host path is no longer the running app. A launcher that is not owned (changed by hand or missing) is left alone and logged. A failed upgrade keeps the old launcher working.
- [ ] AC-08: **Updated while running.** On `app-shim-version-mismatch`, SpecWithCode shows "<Name> could not open because SpecWithCode was updated. Quit and reopen SpecWithCode, then open <Name> again." It finds the name by bundle path, and shows at most one message per bundle per run.
- [ ] AC-09: **Unchanged elsewhere.** Old launchers (`open-url`), Windows shortcuts and Linux desktop entries open windows as before. The Command-Q intercept from 1499 still applies to windows that are not in a shim.

## Approach

Files, in order:

1. `apps/desktop/src/artifactApps/ArtifactAppLaunchers.ts`:
   - `macArtifactAppBundle` takes an optional `shim: { hostAppPath, hostBundleId, serverName }`.
   - With it, the executable entry is a new `LauncherFile` kind, `"shim-loader"`, copied from the loader, and the plist gains the four keys.
   - The generators stay pure and validate every path and name.
2. `apps/desktop/src/artifactApps/ArtifactAppShimRecords.ts` (new): the private `artifact-app-shims.json` (installId to `{hostAppPath, serverName, cdHash}`) and `artifact-apps-reopen.json`. Written like the grants file (`makeArtifactAppPrivateFileWriter`).
3. `apps/desktop/src/artifactApps/ArtifactAppInstaller.ts`:
   - The host gains `appShim: Option<{ loaderPath, hostAppPath, hostBundleId, serverName }>` and `readCdHash(bundlePath)` (`codesign -d -vvv`, the `CDHash=` line).
   - `locateLauncher` builds the shim bundle from the install's shim record, so ownership checks compare exactly what was written.
   - Install writes the shim, signs it (failure fails the install), reads the hash and records it.
   - New methods: `shimInstallFor(bundlePath)` (installId and cdHash) and `upgradeLaunchers`.
4. `apps/desktop/src/artifactApps/ArtifactAppWindows.ts`:
   - `open(installId, { appShim })`.
   - The shim menu, built by a pure `artifactAppShimMenuTemplate`.
   - Close quits the shim. A shim-aware reveal.
   - The shim's `activate` handling.
5. `apps/desktop/src/artifactApps/ArtifactAppShims.ts` (new layer):
   - Starts the server and handles `app-shim-connected` (waiting for the main window, as `ArtifactAppRouting` does) and `app-shim-version-mismatch`.
   - Writes the reopen list on `before-quit`, reopens at start, and runs `upgradeLaunchers`.
   - Wired in `apps/desktop/src/main.ts`.

Key decisions:

- The hash is checked against the running process (`satisfiesCodeRequirement`), not the bundle on disk.
- The shim record lives outside `DesktopArtifactAppSchema`, because the contracts say paths stay in the shell.
- Unpackaged development builds keep the script launcher, because their Electron is ad-hoc signed and Launch Services will not cold-launch it (seen in the proof).

Risks:

- The app-shim API is experimental in Electron.
- A shim built by one SpecWithCode version keeps working after an update, because the loader loads the host's framework. A mismatch during a running update is AC-08.

## Decisions

### Asked
- D-01: Move macOS installs to Electron's app-shim like Claude desktop? Answer: yes, implement fully (owner, November 27, 2026).
### Defaulted (change any before sw-do)
- D-02: Closing the page window quits its shim (single-window app), rather than leaving a windowless Dock icon. Reversible.
- D-03: A cold launch by a page shows SpecWithCode normally (no accessory mode). Reversible.
- D-04: Signing or hash-read failure fails a shim install with the generic install error, instead of writing an unchecked bundle.
### Open
- none

## Tasks

### T-01 Shim launcher bundle and private shim records
- AC: AC-01 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppLaunchers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppLaunchers.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppShimRecords.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppShimRecords.test.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ArtifactAppLaunchers.test.ts apps/desktop/src/artifactApps/ArtifactAppShimRecords.test.ts

### T-02 Installer writes, signs, records, finds and upgrades shims
- AC: AC-01, AC-07 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppInstaller.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppInstaller.test.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ArtifactAppInstaller.test.ts

### T-03 Windows in shims, per-page menu, one lifetime
- AC: AC-03, AC-04, AC-05, AC-09 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.test.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ArtifactAppWindows.test.ts

### T-04 Shim server, verification, reopen and version mismatch
- AC: AC-02, AC-05, AC-06, AC-08 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppShims.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppShims.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/main.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/artifactApps/ArtifactAppShims.test.ts

### T-05 Real Electron proof, docs, review, merge and release
- AC: AC-01..AC-09 | Files: [repositories/anton-abyzov/specwithcode/docs/studio/installed-pages.md, .specweave/increments/1503-installed-page-app-shims/reports/] | Test: scratch Electron 44.10.1 proof drives the real ArtifactAppShims code path headlessly where possible; cross-family review; CI green; request-release.sh
