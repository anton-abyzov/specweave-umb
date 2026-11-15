# Install command-line tool from the desktop app

## Problem

The desktop app puts nothing on `PATH`. Its CLI lives inside the bundle (`app.asar/apps/server/dist/bin.mjs`, run by the app's own executable with `ELECTRON_RUN_AS_NODE=1`; `scripts/install.sh:488-496`, `docs/user/install.md:177-178`). A person with only the desktop app who is told to run `specwithcode fleet invite` or `specwithcode connect link` gets `command not found`, and the workaround (`npm i -g specwithcode`) installs a stale build that rejects current invitation lines (increment 1296, Problem). The approved install plan (November 14, 2026, Phase 1.3, "CLI on PATH" row, review finding R3) asks for an in-app "Install command-line tool" whose CLI always matches the app.

## Scope

In: a shim shipped inside the app bundle on macOS, Windows and Linux (`.deb` and AppImage); an "Install command-line tool" action that puts `specwithcode` on the user's `PATH` without administrator rights; shell `PATH` handling with consent; detection and repair of a stale command; refusal to touch managed wrappers or another `specwithcode`; installed state and Remove on a Command line card in Settings > Machines; an offer at the end of first run; docs; nine languages.

Out: removing the command when the app is uninstalled (1296 AC-34); the per-command "Install command" chips beside every shown command, the once-only notice for older installs and the version-mismatch CLI errors (1296 AC-19, AC-33, AC-34); the Homebrew cask `binary` stanza (Phase 2); changing `install.sh` or the managed wrappers.

## Acceptance Criteria

Shim:

- [ ] AC-01: Every desktop build carries a shim inside the bundle (`Contents/Resources/cli/specwithcode` on macOS, `resources/cli/specwithcode` on Linux, `resources\cli\specwithcode.cmd` on Windows) that runs that bundle's own executable on that bundle's own CLI entry with `ELECTRON_RUN_AS_NODE=1` and `STUDIO_CLI_NAME=specwithcode` (plus `STUDIO_DESKTOP_CLI_LAUNCHER=1` on Windows), passes every argument and the exit code through, and resolves its own location through symlinks. `specwithcode --version` through it prints the app's version.
- [ ] AC-02: The command keeps working across an app update that keeps the install location (Squirrel.Mac swap, NSIS update, `.deb` upgrade, AppImage replaced at the same path), because the per-user entry points at the bundle's location, not at a version.

Install:

- [ ] AC-03: "Install command-line tool" puts `specwithcode` at `~/.local/bin/specwithcode` on macOS and Linux (a symlink to the bundle's shim; for an AppImage, a small launcher that mounts the AppImage and runs the shim inside it) and at `%LOCALAPPDATA%\SpecWithCode\bin\specwithcode.cmd` on Windows, creating the folder if needed, with no administrator password.
- [ ] AC-04: On Windows, installing adds that folder to the user `PATH` (keeping the value's registry type and every other entry) and Remove takes out only that entry.
- [ ] AC-05: On macOS and Linux, when `~/.local/bin` is not on the `PATH` of a new terminal, the card says so and offers "Add to <startup file>" and the exact line to add by hand. The app edits a shell startup file only after that click: it appends one line marked `# Added by SpecWithCode` (zsh: `~/.zprofile` on macOS, `~/.zshrc` on Linux; bash: `~/.bash_profile` on macOS, `~/.bashrc` on Linux; fish: its own `~/.config/fish/conf.d/specwithcode.fish`). Remove deletes only that marked line or that file.
- [ ] AC-06: Install refuses, and explains, when the target is not the app's own: a launcher written by `install.sh` or the fleet installer (managed wrapper) or any other file or link at that path. It never overwrites one.
- [ ] AC-07: When a different `specwithcode` comes earlier on the terminal's `PATH` (for example an npm global install), the card names it and its location and says that it, not the app's command, runs; nothing is changed.
- [ ] AC-08: The app does not install from a temporary location (a disk image under `/Volumes`, an App Translocation path, or a development build); the card says to move the app to Applications first.

State, repair and Remove:

- [ ] AC-09: The Command line card in Settings > Machines shows one of: Not installed; Installed, with the version the command reports and where it is; Installed but not on `PATH` yet; Points at another copy of the app (with where); Broken (points into a deleted or moved app) with Repair; Another command is in the way (with where). Installed shows Remove.
- [ ] AC-10: On every launch of an installed (non-temporary) app, a command that is the app's own and points into a bundle that no longer exists, or at an AppImage path other than the running one when that path is gone, is re-pointed at the running app, including after the Mac self-install moves the app from the disk image or Downloads into Applications. A command that is absent or not the app's own is never created or changed at launch.
- [ ] AC-11: Remove deletes only the app's own command and the `PATH` change the app made, and leaves `~/.local/bin` and everything else in it.

Where it is offered:

- [ ] AC-12: The last first-run step offers "Install command-line tool" using the same component as the card, without repeating any 1297 step; skipping it changes nothing.
- [ ] AC-13: The card and the offer say in one or two sentences what the command is (this app driven from a terminal, the same version as the app, no second copy and no separate sign-in) and exactly what installing changes on disk, and link to a new `docs/user/command-line.md`.
- [ ] AC-14: Every new string exists in all nine language files.

Proof:

- [ ] AC-15: Unit tests cover the shim text, every state above, refusal cases, repair, Remove, startup-file edits and Windows `PATH` handling with `win32` paths, and pass on macOS and on the Windows and Linux CI jobs.
- [ ] AC-16: On this Mac, a built app installs the command, `specwithcode --version` in a fresh login shell prints the app's version, the command still works after an update or relaunch, a broken command is repaired at launch, and Remove leaves nothing behind. Windows and Linux are proven by CI, with what was not tried on a real machine written down.

## Approach

1. **Shim files** (`apps/desktop/resources/cli/specwithcode`, `specwithcode.cmd`), shipped by one `extraResources` entry in `scripts/build-desktop-artifact.ts` (`to: "cli"`), kept small so it does not collide with the 1.1 and 1.2 workers. The POSIX shim follows `$0` through symlinks with `readlink`, then picks the macOS layout (`../../MacOS/<SpecWithCode|SpecWithCode (Nightly)>`, `app.asar`) or the Linux layout (`../../specweave-studio-desktop`, `app.asar`) and `exec`s. The Windows shim derives the install folder from `%~dp0` and runs `SpecWithCode.exe` (or the Nightly name) on `server.asar\apps\server\dist\bin.mjs`, inside `setlocal`. Both carry the marker `specwithcode-desktop-shim`.
2. **`apps/desktop/src/cli/commandLineTool.ts`**: pure logic over an injected file system, process runner and `path` flavour (`posix` or `win32`), so Windows is tested on macOS. `inspect()` returns the state of AC-09; `install()`, `remove()`, `addToShellPath()` and `repairAtLaunch()` act only on entries `classify()` calls the app's own (a symlink whose target ends in `/cli/specwithcode` under an app bundle layout, an AppImage or Windows launcher that carries the marker). The version comes from running the installed command with `--version` (10 second limit). The terminal's `PATH` comes from the user's shell: `$SHELL -l -i -c` on macOS, `$SHELL -i -c` on Linux, with markers around the value and a 5 second limit; Windows reads the user and machine `Path` through PowerShell with `DoNotExpandEnvironmentNames` and writes it back with the same value kind, then nudges a settings broadcast.
3. **IPC**: `desktop:command-line-tool` (`inspect | install | remove | add-to-path`) in `apps/desktop/src/ipc/methods/commandLineTool.ts`, typed in `packages/contracts/src/ipc.ts`, exposed in `preload.ts`. `repairAtLaunch()` runs once after the app is ready, never blocking startup.
4. **Web**: `apps/web/src/components/settings/CommandLineCard.tsx` (one component, `variant="card" | "offer"`), placed in Settings > Machines above This machine, and on the last first-run step. Desktop only; hidden in a browser.
5. **Docs**: `docs/user/command-line.md`, linked from the card; `docs/user/install.md` mentions the action.

Rejected: writing the `env -i` launcher format that `repointShellLaunchers` keeps current (1296 design note 6). Those launchers name a Node and a release folder; the desktop app has neither, and `install.sh` would then read the app's command as its own `ours`/`managed` wrapper. A symlink into the bundle needs no repointing on update. A PATH entry straight into the Windows install folder was rejected: a copied one-line launcher in a stable folder keeps the `PATH` entry fixed if the app moves.

Risks: an interactive shell probe can print noise or hang (markers, stdin closed, 5 second limit, fall back to "unknown, here is the line"); AppImage needs FUSE for `--appimage-mount`, the same as running the AppImage; Electron's GUI executable on Windows leaves stdin unset (handled by `STUDIO_DESKTOP_CLI_LAUNCHER`, `apps/server/src/cli/consoleStdin.ts`).

## Decisions

### Asked
- D-01 CLI name → `specwithcode` for new installs from the app; `specweave-studio` stays where `install.sh` and managed wrappers write it (Anton, November 14, 2026, "Yes, for all of them, do as recommended").
- D-02 Shell startup files → edit only with explicit consent or show the line (plan finding R3, approved with Phase 1).
### Defaulted (change any before sw-do)
- D-03 Windows: install writes the user `PATH` as part of Install, since that is what installing a command means there and needs no administrator; the card says so before the click.
- D-04 Launch repair only fixes the app's own command that points at nothing; a command pointing at another existing copy is shown, and "Use this copy" re-points it on request.
- D-05 This increment builds the launcher and the card that 1296 T-08 names; 1296 T-08 keeps the per-command chips, the notice and uninstall cleanup.
### Open
- none

## Tasks

### T-01 Shim files in every desktop bundle
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/resources/cli/specwithcode, repositories/anton-abyzov/specwithcode/apps/desktop/resources/cli/specwithcode.cmd, repositories/anton-abyzov/specwithcode/scripts/build-desktop-artifact.ts, repositories/anton-abyzov/specwithcode/scripts/build-desktop-artifact.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/cli/commandLineShim.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/cli/commandLineShim.test.ts scripts/build-desktop-artifact.test.ts

### T-02 Install, inspect, repair and remove logic
- AC: AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-15 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/cli/commandLineTool.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/cli/commandLineToolHost.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/cli/commandLineTool.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/cli/commandLineTool.test.ts

### T-03 IPC, contracts and launch repair
- AC: AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/commandLineTool.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/DesktopIpcHandlers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopApp.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/typescript/bin/tsc --noEmit --project apps/desktop/tsconfig.json

### T-04 Command line card and first-run offer
- AC: AC-09, AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/CommandLineCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/CommandLineCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ProjectsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/CommandLineCard.test.tsx src/i18n/i18n.test.ts

### T-05 Docs
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode/docs/user/command-line.md, repositories/anton-abyzov/specwithcode/docs/user/install.md | Test: test -s repositories/anton-abyzov/specwithcode/docs/user/command-line.md

### T-06 Built-app evidence on this Mac, Windows and Linux CI
- AC: AC-15, AC-16 | Files: .specweave/increments/1343-install-command-line-tool-from-the-desktop-app/reports/evidence.md | Test: test -s .specweave/increments/1343-install-command-line-tool-from-the-desktop-app/reports/evidence.md

## Follow-ups

From review round 2 (`reports/review-muse-round2.md`), all low severity, not blocking:
- A: Remove should report `remove-partial` for a startup file over 8 MB instead of success.
- B: The AppImage launcher should print the mounter's own error under the FUSE hint.
- C: The fish file should follow `XDG_CONFIG_HOME`.
- D: Docs should say Remove takes the marked line out of every startup file it finds.
