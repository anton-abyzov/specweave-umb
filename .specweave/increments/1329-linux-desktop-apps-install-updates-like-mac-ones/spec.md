# Linux desktop apps install updates like Mac ones

## Problem

A Linux `.deb` SpecWithCode desktop app installs an update only when it quits. `installDownloadedUpdate` (apps/desktop/src/updates/DesktopUpdates.ts) refuses every idle install for a `.deb` ("legacy Debian installer opens a password dialog") without checking whether the signed pkexec helper (`/usr/lib/specwithcode/update-helper`) and its polkit action, shipped by the `.deb` since the helper landed, are installed. Fleet rollouts never update Linux desktop apps either: the desktop step (`desktop_app_rollout.py`, `desktop_app_update_remote.sh`) is Mac-only, and `linux_rollout.py` updates only the service. On November 12, 2026 the Minisforum app sat on 1.0.245 while its service ran 1.0.253.

## Scope

In: idle install of a `.deb` through the helper when it is ready; a Linux desktop step in `linux_rollout.py` that installs the release `.deb` through the helper, or names exactly why it cannot, and reads the installed version back. Out: AppImage installs, Windows, changing the helper or its polkit policy, the Mac step, release cutting.

## Acceptance Criteria

- [x] AC-01: When the helper, the download's signature and the polkit action allow an install with no prompt, an idle (`beforeQuit`) install of a `.deb` is accepted and quits to install; unit test.
- [x] AC-02: When the helper or its polkit action is missing (or polkit wants a password), the idle install is still refused with `disabled` and nothing quits; unit test.
- [x] AC-03: `linux_rollout.py` runs a desktop step for each worker whose service ends on the version: it installs `SpecWithCode-<v>-<arch>.deb` through the helper after the sha256 and signature checks, quits and reopens the app only if it runs, and reads the version back from dpkg; tests against fake tools.
- [x] AC-04: A worker without the helper, or where polkit wants a password, is reported with that exact reason before anything is downloaded or quit, and the run is incomplete (retry line); a worker without the app is fine; tests.
- [x] AC-05: Proven on linux-mini (a real `.deb` install) without disturbing the live app: helper and polkit present, pkexec runs the helper as root with no password from outside the graphical session, signature and version checks refuse, and a dry run of the desktop step passes end to end.

## Approach

1. `ElectronUpdater` gains `silentInstallReady`, true only on a `.deb` install where the existing `unattendedDebInstallReadiness(downloaded file)` is `ready` (helper, signature, `pkcheck`). The `DesktopUpdates` idle guard refuses only when that is false and the binary is not already replaced.
2. `scripts/studio-fleet/desktop_app_update_linux.sh` (POSIX sh, streamed over SSH like the Mac script). pkexec and pkcheck run inside the user's own manager (`systemd-run --user`), so polkit judges the user's graphical session rather than the SSH session; this was confirmed on linux-mini.
3. `desktop_app_rollout.LinuxDesktopApp` reads `SHA256SUMS-windows-linux`, runs the script, and checks the `RESULT` read-back; `linux_rollout.py` calls it after each service that ends on the version (`--no-desktop-apps` skips it).

Rejected: installing the `.deb` under a running app without quitting it. Quitting and reopening matches the Mac step, and the app's own idle install now covers the case where nobody runs the rollout.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A running app is quit with TERM and reopened via `systemd-run --user`, as the Mac step does. Quitting the app does not stop service work.
- D-02 A desktop step failure makes the `linux_rollout` run incomplete (exit 1), which release.sh only warns about.
### Open
- none

## Tasks

### T-01 Idle .deb install through the helper
- AC: AC-01, AC-02 | Files: apps/desktop/src/electron/ElectronUpdater.ts, apps/desktop/src/updates/DesktopUpdates.ts, apps/desktop/src/updates/DesktopUpdates.deb.test.ts, apps/desktop/src/electron/ElectronUpdater.test.ts | Test: `npx vitest run apps/desktop/src/updates/DesktopUpdates.deb.test.ts apps/desktop/src/electron/ElectronUpdater.test.ts`

### T-02 Linux desktop step in the fleet rollout
- AC: AC-03, AC-04 | Files: scripts/studio-fleet/desktop_app_update_linux.sh, scripts/studio-fleet/desktop_app_rollout.py, scripts/studio-fleet/linux_rollout.py, scripts/studio-fleet/test-linux-rollout.py, docs/studio/releasing.md | Test: `python3 -B scripts/studio-fleet/test-linux-rollout.py`

### T-03 Prove on linux-mini, PR, merge, hand over
- AC: AC-05 | Files: none | Test: dry run of `LinuxDesktopApp` against v1.0.268 plus pkexec helper refusals (exit 3, 65) on linux-mini
