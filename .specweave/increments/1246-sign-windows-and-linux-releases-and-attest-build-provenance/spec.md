# Sign Windows and Linux releases and attest build provenance

## Problem

A commenter on the Russian reel (Instagram, November 2026) pointed out that the SpecWithCode Windows and Linux installers are unsigned and that nobody can check a download was built from the published code. macOS is already Developer ID signed and notarized. Windows users get SmartScreen "unknown publisher" warnings, Linux users have only an unsigned `SHA256SUMS-windows-linux` file, and no platform has build provenance.

## Scope

In:
- Windows: Azure Artifact (Trusted) Signing for the NSIS installers, every `.exe` in the app, the uninstaller and the CLI zip executables, through the signing path `release-windows-linux.yml` already has. Azure account, certificate profile, CI service principal and the seven GitHub secrets.
- Linux: detached ASCII-armored GPG signatures (`.asc`) for each AppImage, `.deb` and `SHA256SUMS-windows-linux`, made with the release key from PR #1256 (`LINUX_UPDATE_SIGNING_KEY`). The public key and fingerprint published as a release asset and in the docs.
- Build provenance: `actions/attest-build-provenance` on every Windows and Linux asset and on the macOS assets, run only while the repository is public.
- Release notes and the specwithcode.com download page: checksums, signature status and how to verify a download on each platform.

Out:
- An apt or rpm repository. No `.rpm` is shipped, and #1256's spec rejected an apt repository with unattended upgrades. Detached signatures give the same check.
- Embedded AppImage signatures (`appimagetool --sign`). Nothing checks them by default, so they add no protection over the detached `.asc` file.
- Moving builds to the public mirror. The development repository goes public under MIT (owned by "Open-source SpecWithCode (MIT)"), and attestations come from its own release builds.
- Changing the repository's visibility.

## Acceptance Criteria

- [x] AC-01: A real release run with all seven `AZURE_*` secrets set produces `SpecWithCode-X.Y.Z-x64.exe`, `-arm64.exe`, the app's `.exe` files and the CLI zips' executables, for which `Get-AuthenticodeSignature` on a Windows runner reports `Valid` with the configured publisher name. `latest.yml` hashes match the signed files.
- [x] AC-02: Each Linux AppImage and `.deb`, and `SHA256SUMS-windows-linux`, has a `.asc` beside it on both releases, and `gpg --verify` with the published `specwithcode-release-key.asc` succeeds. A real run fails when the key is missing or a signature does not verify.
- [x] AC-03: When the repository is public, every Windows, Linux and macOS release asset has a build provenance attestation, and `gh attestation verify <file> --repo anton-abyzov/specwithcode` passes. While the repository is private, the attestation steps are skipped with a notice and the release still succeeds.
- [x] AC-04: The release notes of every release list the SHA-256 of each download, say whether it is signed, and link to the verification steps. The download page at specwithcode.com/code/download shows the same steps for Windows, macOS and Linux.
- [x] AC-05: No secret value appears in a log, a commit or a doc. Secrets live only in GitHub secrets, Keychain or Azure.

## Approach

1. Azure (no code): signing account `specwithcode` (Basic, East US, `https://eus.codesigning.azure.net/`) in resource group `rg-specwithcode-signing`, Founders Hub subscription `ffe7567b-1f77-4ea3-8cd0-e01b290d7390`, tenant `e9698dc9-58d2-41ee-88d0-9dd7bc3935e5`. Service principal `specwithcode-release-signing` (appId `d445a0c9-c298-465c-abcb-2334c1702671`) with "Artifact Signing Certificate Profile Signer" on the account; its secret is in Keychain `specwithcode-azure-signing-sp` (expires November 2028). After Anton's identity validation is approved: create the Public Trust certificate profile, then set all seven secrets in one go, because Plan fails on a partial set.
2. `release-windows-linux.yml`: in the Linux job, import `LINUX_UPDATE_SIGNING_KEY` and write `.asc` files for the AppImage and `.deb`. In publish, sign `SHA256SUMS-windows-linux`, check every signature against the public key, upload the `.asc` files and the key. Add `id-token: write` and `attestations: write` to publish, plus an `actions/attest-build-provenance` step over the assets gated on `github.event.repository.private == false`.
3. `release-stage.yml` (publish.candidate stage): attest the macOS DMG, zip and service assets under the same gate.
4. `scripts/release-windows-linux.ts` and its test: add the `.asc` and key names to the expected asset list.
5. `scripts/release/release.sh` notes: append a "Verify your download" section with the SHA-256 table and links.
6. `docs/user/install.md` and `docs/studio/releasing.md`: verification steps and key fingerprint. specweave `docs-site/src/pages/code/download.tsx`: the same steps on the download page.

Key decision: the service principal with a client secret, because the workflow and `build-desktop-artifact.ts` already use `EnvironmentCredential`. OIDC federation would mean reworking every signing step for the same result.

Risks: #1256 is open with merge conflicts and owns `LINUX_UPDATE_SIGNING_KEY`, so step 2 builds on it once it lands. Identity validation can take days. Attestations stay off until the visibility change lands.

## Decisions

### Asked
- D-01 How to give provenance while the build repository is private → keep builds in specwithcode-dev; it goes public under MIT, and attestations are gated on public visibility (Anton, November 6, 2026).
- D-02 Azure account and the Basic monthly fee → approved (Anton).
### Defaulted (change any before sw-do)
- D-03 Subscription → Founders Hub sponsorship `ffe7567b-1f77-4ea3-8cd0-e01b290d7390`, the az default (reversible).
- D-04 CI auth → service principal secret, 2 years (reversible).
### Open
- none

## Tasks

### T-01 Create the certificate profile and set the seven Windows signing secrets
- AC: AC-01, AC-05 | Files: none (Azure, GitHub secrets) | Test: `gh secret list -R anton-abyzov/specwithcode | grep -c AZURE_` prints 7

### T-02 GPG-sign Linux assets and SHA256SUMS in the release workflow
- AC: AC-02, AC-05 | Files: .github/workflows/release-windows-linux.yml, scripts/release-windows-linux.ts, scripts/release-windows-linux.test.ts | Test: `pnpm vitest run scripts/release-windows-linux.test.ts`

### T-03 Attest build provenance for Windows, Linux and macOS when public
- AC: AC-03 | Files: .github/workflows/release-windows-linux.yml, .github/workflows/release-stage.yml | Test: `actionlint .github/workflows/release-windows-linux.yml .github/workflows/release-stage.yml`

### T-04 Verification steps in release notes, docs and the download page
- AC: AC-04 | Files: scripts/release/release.sh, docs/user/install.md, docs/studio/releasing.md, specweave docs-site/src/pages/code/download.tsx | Test: `bash -n scripts/release/release.sh && grep -q 'Verify your download' scripts/release/release.sh`

### T-05 Release and verify signatures and attestations
- AC: AC-01, AC-02, AC-03 | Files: none | Test: Windows runner `Get-AuthenticodeSignature` is Valid; `gpg --verify` passes; `gh attestation verify` passes once public

### T-06 Verify and close 1246
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: `specweave verify 1246-sign-windows-and-linux-releases-and-attest-build-provenance`
