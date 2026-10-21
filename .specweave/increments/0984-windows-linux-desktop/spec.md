# Windows and Linux SpecWithCode desktop apps

## Problem

The user (October 20, 2026): build installable, fully working Windows and Linux SpecWithCode applications that match macOS functionality, with platform caveats stated, including pairing, the project coordinator and threads, and full test suites running on both operating systems. October 21: "complete the job".

State on October 21: PR anton-abyzov/specwithcode-dev#477 (draft, branch `feat/windows-linux-desktop`, worktree `~/.specwithcode/m4/worktrees/windows-linux`) builds an unsigned NSIS installer and a Linux AppImage/.deb that install and launch in CI, but the full platform run fails on Windows (about 100 test files across server, desktop, web and packages) and one Linux scripts test; the installed-app end-to-end check and the background-service check have not run on a real OS; the CLI single-exe build is broken on main (zod/v3 subpaths), so Windows and Linux CLI archives can't be produced.

## Scope

In: the SpecWithCode app repository (`anton-abyzov/specwithcode-dev`): Windows/Linux test fixes, platform behavior fixes, installed-app end-to-end checks in CI, the Windows/Linux release workflow, CLI archives, user docs with OS caveats, merge and a coordinated release with artifact readback.

Out:
- code signing for Windows (no certificate; installers are unsigned and SmartScreen warns) and Linux package repositories;
- macOS signing and notarization changes (gates stay as they are);
- remote machines, new accounts or paid services;
- computer use on Windows/Linux (macOS-only by design; the app says so);
- iOS and mobile.

## Acceptance Criteria

- [ ] AC-01: CI builds the Windows x64 NSIS installer and the Linux x64 AppImage and .deb from the PR head; each installs silently on windows-2025 / ubuntu-24.04 and the installed app starts its backend and main window.
- [ ] AC-02: The installed-app end-to-end check runs against the installed binary on Windows and Linux in CI: pairs a headless browser through the bundled CLI, a thread answers a message from an offline provider, and the project coordinator answers a message.
- [ ] AC-03: The app-owned background service starts and stops on a real OS: Windows Task Scheduler entry with tray, Linux systemd user service; checked in CI.
- [ ] AC-04: Every suite (desktop, web, packages, server 1-4) passes on windows-2025 and ubuntu-24.04 in one run of `platform-tests.yml`, with no assertion weakened; a test skipped on an OS names the OS-only feature it covers.
- [ ] AC-05: Platform behavior: Windows pairing command line, computer use reported as macOS-only, Linux update guidance, Windows npm install detection, and the relevant upstream T3 Windows fixes (terminal kill timeouts, file links with drive letters and backslashes, atomic save against scanners, PATH case, OpenCode on Windows) are covered by tests.
- [ ] AC-06: Windows and Linux CLI archives build (the zod/v3 single-exe break is fixed) or the release states precisely why they are absent.
- [ ] AC-07: `release-windows-linux.yml` publishes Windows and Linux assets beside the macOS release without changing macOS signing and notarization gates; a release is dispatched only after coordination with the project coordinator and current release owners, and its assets are read back (download, checksum, install smoke).
- [ ] AC-08: User docs list install steps and OS caveats (unsigned Windows installer, computer use macOS-only, Linux update path, service differences).
- [ ] AC-09: PR #477 passes required checks, gets a fresh-context review (Claude Opus 5.5 high, or Codex high when Claude is out of usage) with findings resolved, and is merged to main.

## Approach

- Integrate the lane branches (`feat/wl-*`) and current main into `feat/windows-linux-desktop`; lanes that died keep their work as WIP commits on their own branches.
- Fix Windows failures at the cause (path flavour, POSIX modes, process kill, line endings, shell quoting) with injected platform seams; iterate with `windows-tests.yml` on lane branches and `platform-tests.yml` on the PR.
- Wire `scripts/desktop-e2e/installed-e2e.mjs` and a service start/stop check into `desktop-windows-linux.yml`.
- Workers prefer local Claude Code, claude-opus-5-5, high effort. When Claude is out of usage, work continues on Codex (GPT, high effort) instead of stopping, and returns to Claude after its reset (owner's decision, 2026-10-21). Copilot Free and paid API keys are not used for this job without asking.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Windows installers ship unsigned; docs name the SmartScreen prompt.
- D-02: A test of logic that only exists on one OS may skip elsewhere; logic tests run on every OS with injected paths.

## Tasks

### T-01 Integrate lanes and main
- AC: AC-04 | Files: feat/windows-linux-desktop merge commits | Test: vp test run apps/server/src/cloud/bootService.test.ts; vp run -r typecheck

### T-02 Windows server tests, area A (providers, orchestration, project, preview, terminal, vcs, mcp, device, mods, persistence, git, textGeneration)
- AC: AC-04, AC-05 | Files: apps/server/src/** outside fleet/cli/cloud/environment | Test: windows-tests.yml apps/server on the lane branch

### T-03 Windows server tests, area B (fleet, cli, cloud, environment, root server files)
- AC: AC-04 | Files: apps/server/src/{fleet,cli,cloud,environment}/**, apps/server/src/*.ts | Test: windows-tests.yml apps/server on the lane branch

### T-04 Windows desktop, web and packages tests, Linux scripts test
- AC: AC-04 | Files: apps/desktop/**, apps/web/**, packages/**, scripts/** | Test: windows-tests.yml desktop/web/packages; platform-tests.yml Linux packages

### T-05 Installed-app end-to-end and service checks on both OSes
- AC: AC-01, AC-02, AC-03 | Files: .github/workflows/desktop-windows-linux.yml, scripts/desktop-e2e/** | Test: desktop-windows-linux.yml green with results.json uploaded

### T-06 Upstream T3 Windows fixes
- AC: AC-05 | Files: apps/server/src/terminal/**, file link and atomic save modules | Test: targeted vp test runs on Windows CI

### T-07 Windows and Linux CLI archives
- AC: AC-06 | Files: apps/server/scripts/cli.ts build-exe, release-windows-linux.yml | Test: build-exe on windows-2025 and ubuntu-24.04

### T-08 Docs and caveats
- AC: AC-08 | Files: docs/user/** | Test: docs build

### T-09 Review and merge PR #477
- AC: AC-09 | Files: PR #477 | Test: required checks green; fresh-context review

### T-10 Coordinated release and artifact readback
- AC: AC-07 | Files: release-windows-linux.yml run | Test: download, checksum and install smoke of published assets

### T-11 Verify and close 0984
- AC: AC-01..AC-09 | Files: .specweave/increments/0984-windows-linux-desktop | Test: specweave verify; fresh-context review; specweave complete
