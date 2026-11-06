# Linux updates install without a password prompt

## Problem

Every Restart or Update on a `.deb` install opens the Linux "Authentication Required" dialog. The photo (`IMG_0052.HEIC`, Ministorm, November 2, 2026) reads: "Authentication is needed to run `/bin/bash -c dpkg -i /home/anton/.cach...ending/SpecWithCode-1.0.164-amd64.deb` as the super user".

Cause: electron-updater's `DebUpdater.doInstall` runs `pkexec --disable-internal-agent /bin/bash -c 'dpkg -i <pending deb>'`. Ministorm's journal has one such `pkexec` entry for each of its five restart runs on November 2, 2026, with a sixth pending. Service restarts raise no prompt: the server runs from `~/.specwithcode/ministorm/runtime` under a user systemd unit. The only root step in normal use is this package install, and that install checks no signature, only the sha512 from the feed.

## Scope

In: unattended install of a signed newer `.deb`, signing in the release workflow, packaging, tests, the release proof and docs.

Out: per-user Linux install, apt repository, AppImage changes, changes to `/etc/sudoers` or machine polkit configuration, the CLI service update path.

## Acceptance Criteria

- [ ] AC-01: On a `.deb` install that has the helper, Restart and Update install a signed newer package through `pkexec` on the update helper, with no password prompt in an active local session.
- [ ] AC-02: The helper installs only a package whose detached signature verifies against the root-owned pinned key, whose Package is `studio`, whose Architecture is this machine's, and whose Version is newer than the installed one; anything else installs nothing and exits non-zero.
- [ ] AC-03: The helper never opens a caller-supplied path as root, works on a root-only copy, and sanitizes its environment; the polkit action names exactly that one program, allows it only in an active local session, and needs admin authentication elsewhere. No sudoers entry and no `.rules` file ships.
- [ ] AC-04: A package with a missing or bad signature does not fall back to the password prompt. The update fails and says why. A deliberate downgrade the helper refuses as not newer, or an install where polkit denies the action, still asks for the password as before.
- [ ] AC-05: A real release fails if the signing secret is missing or the signature does not verify against the key inside the built `.deb`; `latest-linux.yml` and `latest-linux-arm64.yml` carry the signature.
- [ ] AC-06: Installs without the helper (every release before this one) and AppImages keep their current update path. Moving to the helper needs only the normal update: one last password. User data and the user service are untouched.
- [ ] AC-07: The release proof shows the helper path on clean Ubuntu 22.04 and 24.04 with no `pkexec` run of `/bin/bash`, and a tampered package refused.

## Approach

Options compared against Ministorm (Ubuntu 26.04, no `libfuse2`, deb install with its AppArmor profile):

| Option | Password in normal use | Sandbox on default Ubuntu 24.04+ | Update on click | Cost |
|---|---|---|---|---|
| Per-user install, no root | Never | Blocked by the userns restriction; needs `--no-sandbox` or a root-installed AppArmor profile for a user-writable binary | Yes | Moves everyone, weakens or breaks the sandbox |
| AppImage self-update | Never | Same restriction; also needs FUSE 2, absent by default | Yes | Same, plus a root `apt install libfuse2t64` |
| Signed apt repo + unattended upgrades | Never | Works | No, daily timer; files replaced under a running app | New hosted repo and third-party origin config, wrong for several releases a day |
| Polkit action for one signed-update helper, shipped in the `.deb` | Never after the one update that installs it | Works, keeps today's AppArmor profile and sandbox | Yes | A signing key to guard |

Decision: the polkit action. It keeps the install users already have and adds no machine setup step beyond the package itself. The app does not need a system install to run, but the Chromium sandbox on default Ubuntu needs a root-owned AppArmor profile for a root-owned binary, which is what rules out the per-user options.

Threat model: any process of the active user can run the helper, but it can only move this package forward to a release this project signed. That grants no capability the user's next normal update would not. A leaked signing key would give root on every Linux install at its next update, as a leaked apt repo key would, so the key is only in one Actions secret, used only by the release Linux job. Rotation ships a new pinned key in a release signed by the old one.

Files:

1. `apps/desktop/resources/linux/update-helper` (POSIX `sh`), `com.specwithcode.studio.update.policy`, `update-key.gpg`.
2. `scripts/build-desktop-artifact.ts`: fpm mappings to `/usr/lib/specwithcode/` and `/usr/share/polkit-1/actions/`, `gpgv` in Depends.
3. `apps/desktop/src/updates/signedDebInstall.ts`, wired in `apps/desktop/src/electron/ElectronUpdater.ts`: replaces `doInstall` on the deb updater, writes the feed's signature beside the download.
4. `.github/workflows/release-windows-linux.yml` and `scripts/release-windows-linux.ts`: sign the `.deb`, check against the packaged key, add `debSignature` to the feed.
5. `scripts/linux-update-proof.mjs` and its workflow: new `signed` phase.
6. `docs/user/install.md`, `docs/studio/releasing.md`.

The signature travels in the feed file, so there is no new asset, download or token path.

## Decisions

### Asked
- none. The chosen option does not change how Linux is installed.
### Defaulted (change any before sw-do)
- D-01 Mechanism → polkit action plus signed helper, shipped in the `.deb`.
- D-02 Signature format → detached OpenPGP checked with `gpgv`, which `apt` already depends on.
- D-03 Non-admin active-session users may trigger the helper → yes; it only moves to a newer signed release.
### Open
- none

## Tasks

### T-01 Update helper, polkit action and pinned key
- AC: AC-02, AC-03 | Files: apps/desktop/resources/linux/update-helper, apps/desktop/resources/linux/com.specwithcode.studio.update.policy, apps/desktop/resources/linux/update-key.gpg, scripts/linux-update-helper.test.ts | Test: vp test run scripts/linux-update-helper.test.ts

### T-02 App installs through the helper
- AC: AC-01, AC-04, AC-06 | Files: apps/desktop/src/updates/signedDebInstall.ts, apps/desktop/src/updates/signedDebInstall.test.ts, apps/desktop/src/electron/ElectronUpdater.ts | Test: vp test run apps/desktop/src/updates/signedDebInstall.test.ts

### T-03 Package the helper
- AC: AC-03 | Files: scripts/build-desktop-artifact.ts, scripts/build-desktop-artifact.test.ts | Test: vp test run scripts/build-desktop-artifact.test.ts

### T-04 Sign in the release
- AC: AC-05 | Files: .github/workflows/release-windows-linux.yml, scripts/release-windows-linux.ts, scripts/release-windows-linux.test.ts | Test: vp test run scripts/release-windows-linux.test.ts

### T-05 Release proof covers the helper
- AC: AC-07 | Files: scripts/linux-update-proof.mjs, .github/workflows/linux-update-proof.yml | Test: gh workflow run linux-update-proof.yml on the PR branch, or the release gate

### T-06 Docs
- AC: AC-06 | Files: docs/user/install.md, docs/studio/releasing.md | Test: vp test run scripts/release-windows-linux.test.ts

### T-07 Verify and close 1189
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1189-linux-updates-install-without-a-password-prompt/spec.md | Test: specweave verify 1189
