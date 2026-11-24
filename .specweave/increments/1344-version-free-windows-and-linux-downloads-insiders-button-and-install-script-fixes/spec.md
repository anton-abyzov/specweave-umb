# Version-free Windows and Linux downloads, Insiders button and install script fixes

## Problem

Phase 1 steps 1.2 and 1.4 of the approved install plan (report `.specweave/reports/threads/2026-11-14-specwithcode-install-options-evaluation-ce5cc9-a444a5.md`; Anton's go on November 14, 2026, memory `decision_install_path.md`).

- Only the Mac installer has a version-free name (`SpecWithCode-arm64.dmg`). Windows and Linux installers carry the version (`SpecWithCode-1.0.300-x64.exe`), so a `releases/latest/download/` link cannot reach them and the download page has to compute versioned links of an older release.
- The download page does not say "Apple silicon only" next to the Mac button unless it detects an Intel Mac (Chromium only), and has no Insiders download.
- `scripts/install.ps1` is not attached to any release and its header names `studio.invalid`; `docs/user/install.md` says Windows has no one-liner.
- `scripts/install.sh` restarts an interrupted download from zero and gives no way to report a failure.
- The Mac `SHA256SUMS` has no detached signature, unlike `SHA256SUMS-windows-linux.asc`.
- `docs/studio/updates.md:15` says the app checks hourly (the code checks when the last check is over 10 minutes old, `apps/desktop/src/updates/DesktopUpdates.ts`), and `:77` says every build is unsigned.

## Scope

In: version-free Windows and Linux asset names on every release; the live download page (spec-weave.com/code/download, docs-site in anton-abyzov/specweave) on `releases/latest/download` names with a fallback; the "Apple silicon only" line and Intel Mac message; Windows x64 or arm64 pick; an Insiders download button; `install.ps1` published with a real URL; `install.sh` download resume and a failure-report line (also in `install.ps1`); a GPG signature for the Mac `SHA256SUMS`; the two `updates.md` fixes; the unpublished `apps/marketing` download page kept consistent.

Out: Mac self-install (1.1, another worker), the CLI tool (1.3, another worker), deep links and carrying the Insiders track into the app (Phase 2.5), new telemetry, a universal Mac build, signing of the version-free Linux copies (their bytes are in the signed `SHA256SUMS-windows-linux`).

## Acceptance Criteria

- [ ] AC-01: Every Release Windows and Linux run attaches `SpecWithCode-x64.exe`, `SpecWithCode-arm64.exe`, `SpecWithCode-x86_64.AppImage`, `SpecWithCode-arm64.AppImage`, `SpecWithCode-amd64.deb` and `SpecWithCode-arm64.deb`, byte-identical to the versioned files and listed in `SHA256SUMS-windows-linux`. A new attach without them is refused; a release attached before this change still counts as complete.
- [ ] AC-02: The updater feeds (`latest.yml`, `latest-linux.yml`, `latest-linux-arm64.yml`) still list only the versioned files, and `latest-mac.yml` and `SHA256SUMS` stay unchanged (the workflow's existing check), so the release train's manifest checks are unaffected.
- [ ] AC-03: Each release gets `SHA256SUMS.asc`, a detached signature of that release's own `SHA256SUMS` made with the key that signs `SHA256SUMS-windows-linux`, checked with `gpgv` against the published key before upload.
- [ ] AC-04: Each release gets `install.ps1` (listed in `SHA256SUMS-windows-linux`); its header shows `irm https://github.com/anton-abyzov/specwithcode/releases/latest/download/install.ps1 | iex`, and `docs/user/install.md` documents that line instead of "Windows has no install.sh one-liner".
- [ ] AC-05: `install.sh` retries an interrupted download once with `curl -C -` (or `wget -c`), keeping the bytes it has, before the checksum check; a 404 is not retried.
- [ ] AC-06: When `install.sh` or `install.ps1` fails, it prints one "Report this failure" line with a GitHub new-issue link prefilled with the error, version and platform. Nothing is sent automatically.
- [ ] AC-07: `docs/studio/updates.md` says the app checks about 15 seconds after launch and then once a minute whenever the last successful check is over 10 minutes old (the service agent stays hourly), and no longer says every build is unsigned.
- [ ] AC-08: The download page links Windows and Linux installers through `releases/latest/download/<version-free name>` when the newest stable release carries them, and otherwise through the versioned files of the newest release that has all six (no broken link while 1.0.x releases attach Windows and Linux later). The release watch still reads which release a deployed page shows.
- [ ] AC-09: On a Mac the page says "Apple silicon only" next to the Mac button; a Mac reported as Intel gets a plain "will not run on this Mac" message; Windows picks x64 or arm64 from `navigator.userAgentData` high-entropy architecture, falls back to x64, and keeps the other architecture's link visible.
- [ ] AC-10: Next to the Stable button, an "Insiders" button downloads the newest Insiders build (a GitHub prerelease newer than the stable release) for the visitor's platform, with one line explaining Insiders. With no such prerelease, or none carrying the visitor's file, the button is hidden; no link points at a missing file.
- [ ] AC-11: Headless Chromium screenshots of the rendered download page with Mac (Apple silicon and Intel), Windows (x64 and arm64) and Linux user agents are saved in this increment's `reports/`.
- [ ] AC-12: After merge, release and deploy, each version-free link on the live page downloads a real file of the expected size in headless Chromium, and the live Insiders button is hidden or downloads a real file.

## Approach

App repo (`repositories/anton-abyzov/specwithcode`, PR to `main`):

1. `scripts/release-windows-linux.ts`: `versionFreeAssetName(name, version)`; `collect` copies each installer to its version-free name; `isWindowsLinuxAssetName` accepts the six names and `install.ps1`; `planUpload` requires them on a new attach; `attachState` checks them against the checksum file only when present, so older releases stay complete. Copies are made in `collect`, not in `scripts/build-desktop-artifact.ts`, so the 1.1 worker's DMG changes there do not conflict and local builds are unchanged.
2. `.github/workflows/release-windows-linux.yml`: fetch `scripts/install.ps1` at the run's commit into the assets; after the upload, sign each release's `SHA256SUMS` with the release key, `gpgv` it, upload `SHA256SUMS.asc`.
3. `scripts/install.sh`, `scripts/install.ps1`: resume once; report line. Tests in `scripts/install.test.ts` and `scripts/release-windows-linux.test.ts`.
4. Docs: `docs/user/install.md`, `docs/studio/updates.md`, `docs/studio/releasing.md`.
5. `scripts/download-stats/lib.mjs` classifies the new names.
6. `apps/marketing/src/pages/download.astro` (not deployed, `git.deploymentEnabled: false`) gets the same names and the Apple silicon line.

Specweave repo (`repositories/anton-abyzov/specweave`, PR to `develop`), docs-site:

1. `src/data/specwithcodeReleasePick.mjs`: the desktop pick records whether it is the newest stable release and carries the version-free names (`latest`); a new `insiders` pick: newest non-draft prerelease with a plain version newer than the stable Mac release, with the files it carries.
2. `src/data/specwithcodeRelease.ts`: `buildDesktopRelease` builds `releases/latest/download` URLs when `latest`; `DESKTOP_LATEST` and Insiders constants for the build-time fallback, written by `scripts/sync-specwithcode-release.mjs`.
3. `src/data/specwithcodeInstaller.ts`, `src/pages/code/download.tsx`: Apple silicon line, Intel message wording, Windows other-arch link, Insiders button. `data-desktop-version` on the page so `linkedReleases` keeps reading the shown release.
4. Translations for new strings in `i18n/*/code.json`.

Risk: before 1.1.0 a new Latest 1.0.x release has no Windows or Linux files for about twenty minutes; the `latest` flag is false then, so the page uses the versioned files of the previous release. From 1.1.0 the train promotes only releases that already carry all feeds.

## Decisions

### Asked
- D-01 Phase 1, Apple silicon only, real Insiders button, no telemetry → yes, as recommended (Anton, November 14, 2026).
### Defaulted (change any before sw-do)
- D-02 Version-free names keep electron-builder's arch words (`x86_64` AppImage, `amd64` deb), like the Mac rule: drop the version, keep the rest.
- D-03 Without a newer Insiders prerelease the Insiders button is hidden rather than pointing at Stable.
- D-04 An installed Insiders build still defaults to the Stable track (`resolveDefaultDesktopUpdateChannel` maps only `-nightly.` versions to `nightly`). Recorded as a follow-up for Phase 2.5, not built here.
### Open
- none

## Tasks

### T-01 Version-free Windows and Linux assets, install.ps1 and the Mac sums signature in the release workflow
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/scripts/release-windows-linux.ts, repositories/anton-abyzov/specwithcode/scripts/release-windows-linux.test.ts, repositories/anton-abyzov/specwithcode/.github/workflows/release-windows-linux.yml, repositories/anton-abyzov/specwithcode/scripts/download-stats/lib.mjs, repositories/anton-abyzov/specwithcode/scripts/download-stats/lib.test.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run scripts/release-windows-linux.test.ts && node --test scripts/download-stats/lib.test.mjs

### T-02 install.sh resume and failure line; install.ps1 URL and failure line
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/scripts/install.sh, repositories/anton-abyzov/specwithcode/scripts/install.ps1, repositories/anton-abyzov/specwithcode/scripts/install.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run scripts/install.test.ts scripts/release-windows-linux.test.ts

### T-03 Install and update docs
- AC: AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode/docs/user/install.md, repositories/anton-abyzov/specwithcode/docs/studio/updates.md, repositories/anton-abyzov/specwithcode/docs/studio/releasing.md, repositories/anton-abyzov/specwithcode/apps/marketing/src/pages/download.astro | Test: cd repositories/anton-abyzov/specwithcode && node scripts/studio-brand-audit.mjs

### T-04 Download page: latest links, architecture lines, Insiders button
- AC: AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specweave/docs-site/src/data/specwithcodeReleasePick.mjs, repositories/anton-abyzov/specweave/docs-site/src/data/specwithcodeRelease.ts, repositories/anton-abyzov/specweave/docs-site/src/data/specwithcodeLiveRelease.ts, repositories/anton-abyzov/specweave/docs-site/src/data/specwithcodeInstaller.ts, repositories/anton-abyzov/specweave/docs-site/src/pages/code/download.tsx, repositories/anton-abyzov/specweave/docs-site/scripts/sync-specwithcode-release.mjs, repositories/anton-abyzov/specweave/docs-site/src/data/__tests__/, repositories/anton-abyzov/specweave/docs-site/i18n/ | Test: cd repositories/anton-abyzov/specweave/docs-site && npx vitest run src/data && npx tsc --noEmit -p .

### T-05 Headless page check on Mac, Windows and Linux user agents
- AC: AC-11 | Files: .specweave/increments/1344-version-free-windows-and-linux-downloads-insiders-button-and-install-script-fixes/reports/ | Test: node <scratch>/download-page-check.mjs against the built docs-site, screenshots in reports/

### T-06 Review, merge, release and live verification
- AC: AC-12 | Files: .specweave/increments/1344-version-free-windows-and-linux-downloads-insiders-button-and-install-script-fixes/reports/ | Test: headless Chromium download of each version-free link on spec-weave.com/code/download
- Reviewer: Meta Muse Wonder 1.0 (`muse-wonder-1.0`, max effort) for both PRs (specwithcode#426, specweave#2296). GPT-6.1 Sol was out of reach and a Claude model does not count for a Claude-written PR.
