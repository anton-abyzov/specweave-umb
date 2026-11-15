# Mac app installs itself into Applications on first launch

## Problem

People who open SpecWithCode straight from the downloaded disk image run it from `/Volumes/...` or from an App Translocation copy. That copy cannot update itself (`apps/desktop/src/updates/macSwapInstall.ts:99-106` refuses with "Copy it to Applications to get updates"), disappears when the disk image is ejected, and the app never offers to fix it. The DMG window asks people to drag, which many skip. Phase 1 step 1.1 of the install plan approved by Anton on November 14, 2026 (project memory `decision_install_path.md`; plan sections "1b" and "Phased plan" in `2026-11-14-specwithcode-install-options-evaluation`) makes the app its own installer.

## Scope

In: a native "Install SpecWithCode" step in the Electron main process when the app runs from a disk image or a translocated copy; replacing an older installed copy and earlier-named (legacy) bundles in the documented swap order; the `~/Applications` fallback for users who cannot write `/Applications`, with Launch Services and LaunchAgent re-registration before the disk image is ejected; relaunch from the installed copy; copy in the app's nine languages; DMG window text "Double-click to install"; the Electron CVE-2026-34779 check.

Out: download stub, `.pkg`, CLI tool (1343), Windows and Linux downloads and Insiders button (1344), data folder choice, Mac uninstall.

## Acceptance Criteria

- [ ] AC-01: A packaged Mac build started from `/Volumes/...` or an `/AppTranslocation/` path shows one native "Install SpecWithCode" dialog after Electron is ready and before the bundle rename, update setup (`updates.configure`, first check about 15 s later) and backend bootstrap. Builds in Applications, development builds, other platforms and `STUDIO_SELF_INSTALL=off` skip it.
- [ ] AC-02: Install copies the running bundle beside the destination (`<dir>/.SpecWithCode.app-<version>-install`, quarantine dropped), verifies it (`codesign --verify --deep --strict`, same bundle id and version as the running app) and only then renames it to `<dir>/SpecWithCode.app`; a failed copy or check leaves the destination untouched and the app keeps running as today.
- [ ] AC-03: An older `SpecWithCode.app` at the destination that is not running is renamed aside, replaced, and moved to the Trash only after the new copy is in place; a failed rename puts it back.
- [ ] AC-04: When the installed copy is the same or a newer version, the step offers "Open it" instead of replacing it; when it is running, the step offers to switch to it; when an older installed copy is running, the step asks the person to quit it first and checks again. "Open it" or "switch" opens the installed copy and quits the disk-image copy.
- [ ] AC-05: Earlier-named bundles from `LEGACY_BUNDLE_SUCCESSORS` with the same bundle id beside the destination are handled like the installed copy (running, newer, older), and an older one goes to the Trash as part of the install, so two same-id apps never sit side by side. A different app under the same name is never touched.
- [ ] AC-06: When `/Applications` is not writable, the step says so and installs into `~/Applications` (created if missing) for this user only, warning that a Dock item for the disk-image copy must be replaced.
- [ ] AC-07: Before relaunching, the step unregisters the old bundle path and registers the new one with Launch Services, and rewrites and reloads any `~/Library/LaunchAgents/com.specweave.studio*.plist` that names the old bundle path. Only then does a detached script wait for the app to exit, open the installed copy and eject the disk image (only a mounted disk image, never another volume).
- [ ] AC-08: "Not now" continues startup exactly as today, including the run-from-DMG update refusal.
- [ ] AC-09: Every dialog string exists in English, Russian, Spanish, Simplified Chinese, Japanese, Brazilian Portuguese, Korean, German and French, chosen from the system's preferred languages with English as the fallback.
- [ ] AC-10: The DMG window's main instruction reads "Double-click to install" and keeps the Applications link for people who drag.
- [ ] AC-11: The PR states whether Electron 44.4.2 carries the CVE-2026-34779 fix and why the app does or does not call `app.moveToApplicationsFolder()`.
- [ ] AC-12: Evidence from a quarantined, signed DMG on this Mac: install, relaunch from Applications, no Keychain prompt, a Screen Recording grant made before the move still valid after it, the legacy-bundle case and the existing-app case; untested macOS versions are listed.

## Approach

New `apps/desktop/src/install/macSelfInstall.ts` holds the pure plan (location, destination, conflicts), the swap and re-registration steps and the detached relaunch script; `macSelfInstallCopy.ts` holds the nine-language strings. `apps/desktop/src/app/DesktopApp.ts` runs it right after `whenReady`. Detection uses `app.isInApplicationsFolder()` plus the bundle path. `scripts/build-desktop-artifact.ts` is not changed; only the DMG background SVGs change.

Rejected: calling `app.moveToApplicationsFolder()`. In Electron 44.4.2 (`shell/browser/ui/cocoa/electron_bundle_mover.mm`) it trashes the installed app before copying the new one (the order that broke an install on October 27, 2026, see `docs/studio/releasing.md` "Swapping the desktop app"), always targets `/Applications` and falls back to an administrator password prompt instead of `~/Applications`, quits before the app can re-register anything, and does not know about legacy bundle names.

Risks: copying a ~500 MB bundle from a disk image takes seconds with no window; TCC and Keychain identity follow the code signature, not the path, which the evidence must confirm.

## Decisions

### Asked
- D-01 Go on Phase 1 → yes, as recommended (Anton, November 14, 2026).
### Defaulted (change any before sw-do)
- D-02 Own swap-order installer instead of `moveToApplicationsFolder()` → see Approach (reversible).
- D-03 "Not now" is not remembered; a disk-image launch asks every time (reversible).
- D-04 Opt-out for automation: `STUDIO_SELF_INSTALL=off` (reversible).
- D-05 Reviewer → Meta Muse Wonder 1.0 at max effort (coordinator, November 14, 2026). GPT-6.1 Sol was out of reach (Codex limit on this Mac until December 5, 2026; ministorm refused a second machine hop; Devin credits spent), and a Claude reviewer cannot gate this Claude-written PR.
### Open
- none

## Tasks

### T-01 Plan and copy
- AC: AC-01, AC-04, AC-05, AC-06, AC-09 | Files: apps/desktop/src/install/macSelfInstall.ts, apps/desktop/src/install/macSelfInstallCopy.ts, apps/desktop/src/install/macSelfInstall.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/install/macSelfInstall.test.ts

### T-02 Swap install, re-registration and relaunch
- AC: AC-02, AC-03, AC-07 | Files: apps/desktop/src/install/macSelfInstall.ts, apps/desktop/src/install/macSelfInstall.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/install/macSelfInstall.test.ts

### T-03 Startup gate
- AC: AC-01, AC-08 | Files: apps/desktop/src/app/DesktopApp.ts | Test: node node_modules/typescript/bin/tsc --noEmit --project apps/desktop/tsconfig.json

### T-04 DMG window text
- AC: AC-10 | Files: apps/desktop/resources/dmg/dmg-background-latest.svg, apps/desktop/resources/dmg/dmg-background-nightly.svg | Test: sips -s format png apps/desktop/resources/dmg/dmg-background-latest.svg --out /tmp/dmg-latest.png

### T-05 Docs and CVE note
- AC: AC-11 | Files: docs/studio/mac-self-install.md | Test: grep -n "Install SpecWithCode" docs/studio/mac-self-install.md

### T-06 Quarantined DMG evidence
- AC: AC-12 | Files: .specweave/increments/1345-mac-app-installs-itself-into-applications-on-first-launch/reports/evidence.md | Test: test -s .specweave/increments/1345-mac-app-installs-itself-into-applications-on-first-launch/reports/evidence.md
