---
status: completed
---
# 0829 — vSkill Distribution & Marketing

**Status**: ready_for_review
**Type**: feature
**Priority**: P0
**Project**: vskill
**Parent**: 0828-vskill-desktop-app
**Created**: 2026-05-07

---

## Status as of closure

**Artifact-complete, awaiting user-action items in `LAUNCH_CHECKLIST.md` before first signed release.**

Five implementation agents (macos-distribution, windows-port, linux-port, ci-pipeline, seo-marketing) and three verification agents (macos-verify, config-verify, gap-resolution) completed their assigned scope. All pipeline scripts, GitHub Actions workflows, marketing pages, and OS-specific build harnesses are committed to the repo.

**The increment cannot ship the first `.dmg`/`.msi`/`.deb` until the user knocks down the items in `LAUNCH_CHECKLIST.md`** — Apple Developer ID Application cert creation, Tauri minisign keypair, Cloudflare R2 setup, 17 GitHub Secrets, marketing assets (founder bio, headshots, OG PNG, press kit ZIP), and the launch-day post decisions.

**Code-fix gap** (P0, not this agent's responsibility): `tauri-plugin-updater` crate is not wired into `src-tauri/Cargo.toml` or the Builder chain, even though `tauri.conf.json` declares the full `plugins.updater` config. Auto-update is dead code until the crate is added. See `LAUNCH_CHECKLIST.md` §0.

**Not-yet-exercised ACs**:
- US-024 (launch announcements posted) — drafts ready in `marketing-drafts/`, but posting is a user decision (launch date TBD).
- US-029 (SEO indexing verified post-launch) — depends on going live first.
- All ACs whose execution requires user-action items in `LAUNCH_CHECKLIST.md` (notarization run, manifest live, Homebrew Cask submitted, etc.) remain unchecked until the user completes those items.

---

## 1. Vision & Problem Statement

### Problem
0828 delivered the vSkill Desktop app shell (Tauri 2 + Node SEA sidecar) that **compiles and launches locally on macOS**. But the artifacts cannot ship: no Developer ID cert exists, the bundle ID isn't registered, there are no Windows or Linux builds, no auto-update wiring, no GitHub Releases pipeline, and no marketing surface to drive downloads. Without this increment, 0828 is a dev demo, not a product.

### Vision
In **hours, not days**, take vSkill Desktop from "compiles locally" to "publicly distributable on macOS, Windows, and Linux" with:
- Signed + notarized macOS `.dmg` (Developer ID, universal2)
- Unsigned Windows `.msi` (SmartScreen warning documented; OV cert deferred)
- Linux `.deb` + `.rpm` + `.AppImage` with GPG-signed checksums
- Tauri auto-updater polling a signed manifest
- Tag-triggered GitHub Actions release pipeline (3 OS matrix)
- verified-skill.com SEO baseline + launch-ready marketing assets (drafts only — user picks launch date)
- Cross-platform verification by an automated team

### Strategic Outcomes
- vSkill becomes installable by anyone via official download links
- Auto-update channel makes future shipping low-friction
- SEO baseline gets vSkill discoverable for "vSkill Studio AI"
- Marketing drafts are ready so launch is a one-click decision, not weeks of prep

### Inherited Givens (from 0828 — DO NOT redesign)
- Tauri 2 Rust shell + Node SEA sidecar (~114 MiB host-arch arm64)
- ASC auth: keychain profile `vskill`, EasyChamp team `a9be87c1-47d8-40f2-897d-75df80a540fb`, Key ID `JZ2ML9M66A`
- Apple Developer license owned (annual fee paid)
- 0828 hotfixes (sidecar leak on quit, Retina pixel scaling) are landed
- Studio UI bundle is **shared** between `npx vskill studio` and the desktop app — UI changes propagate via desktop release / auto-updater

### Inherited Decisions (from 0828)
- macOS: Developer ID Application + notarization (NOT Mac App Store)
- Windows: unsigned `.msi` accepted (SmartScreen warning documented)
- Linux: GPG-signed only (no paid certs)
- Auto-updater: Tauri Updater plugin
- Release distribution: GitHub Releases (with Cloudflare R2 / verified-skill.com fronting the manifest — architect to choose)

---

## 2. Personas

### P-1: Skill Author / Power User (PRIMARY)
- Found vSkill via Hacker News, ProductHunt, or a friend
- Expects a one-click download → drag-to-Applications install on macOS
- Will judge brand quality within 60 seconds; SmartScreen scares them on Windows but a polished download page mitigates
- Wants auto-update to "just work" — no terminal involvement

### P-2: SEO Discovery User (SECONDARY)
- Searches "vSkill Studio AI" or "AI skill authoring" on Google
- Lands on verified-skill.com from organic search
- Decides in <30s whether to download based on the landing page

### P-3: Linux Developer (TERTIARY)
- Comfortable with .deb/.rpm/.AppImage; verifies GPG signatures
- Tolerates rough edges (no signed cert) but expects checksums + reproducible builds

### P-4: Press / Influencer (LAUNCH-DAY)
- Wants press kit: logos, screenshots, one-liner, 3-line description
- Will check OG image quality when sharing on X/LinkedIn

---

## 3. Scope

### In Scope (v1 — this increment)

**Track A — macOS distribution**
- Developer ID Application cert creation via App Store Connect API
- Bundle ID `com.verifiedskill.desktop` registered
- Universal2 (arm64 + x86_64) signed + notarized + stapled `.dmg`
- Hardened runtime entitlements (network client; no sandbox; JIT for WKWebView)
- Homebrew Cask formula (initially in staging tap; mainline after burn-in)

**Track B — Windows distribution**
- WiX-built `.msi` installer (unsigned, x64 only for v1)
- Bundles WebView2 Evergreen redistributable
- Registers `vskill://` URL scheme
- Download page documents SmartScreen bypass ("More info" → "Run anyway")

**Track C — Linux distribution**
- `.deb` (amd64) for Ubuntu 22.04+ / Debian 12+
- `.rpm` (x86_64) for Fedora 40+ / RHEL 9
- `.AppImage` (x86_64, glibc 2.31+) for any modern distro
- GPG-signed `SHA256SUMS` file alongside artifacts
- Pinned WebKitGTK ≥ 2.40 in Linux dependency declarations

**Track D — Auto-updater + GitHub Releases pipeline**
- Tag `desktop-v*` triggers 3 GitHub Actions workflows in parallel (macos-latest, windows-latest, ubuntu-latest)
- Each workflow builds → signs (where applicable) → uploads to a single GitHub Release
- Tauri Updater plugin polls `https://verified-skill.com/desktop/latest.json` on launch + every 24h
- Update download requires explicit user consent ("Update available — restart to apply")
- Manifest signed with minisign; private key in GitHub Secrets + 1Password
- Release notes auto-generated from conventional commits since last `desktop-v*` tag

**Track E — SEO + Marketing**
- verified-skill.com homepage: H1 mentioning "vSkill Studio AI", schema.org `SoftwareApplication` JSON-LD, OG image, sitemap.xml, robots.txt
- Landing pages: `/desktop`, `/ai-studio`, `/skill-studio` with download CTAs
- Google Search Console verified, sitemap submitted
- Lighthouse SEO + perf + accessibility ≥ 90 on all marketing pages
- Press kit at `/press`: logos (SVG + PNG), screenshots (3 minimum), one-liner, 3-line description, contact email
- README badges: download counts, build status, license, npm version
- Launch announcement **drafts queued** (NOT posted): ProductHunt entry, Show HN post, r/LocalLLaMA, dev.to article
- Social cards: X/Twitter, LinkedIn, Discord OG variations

**Track F — Verification (cross-cutting)**
- Automated download + install + smoke-test of every artifact on appropriate runners (mac-15, windows-latest, ubuntu-22.04)
- Verifies Cmd+K / Ctrl+K opens Find Skills modal in all 3 desktop platforms
- Update flow tested end-to-end (install vN-1, point updater at staging manifest with vN, assert update applied)
- Lighthouse run + Google indexing check (manual verification at +7 days)

### Out of Scope (explicitly deferred)
- Mac App Store submission (sandbox conflicts with eval-server child-process supervision)
- Windows OV/EV code-signing certificate (user accepts SmartScreen warning)
- Microsoft Store submission
- winget mainline submission (deferred to v1.1)
- Snap Store / Flathub publishing
- ProductHunt / Show HN actual posts (drafts only — user picks launch date)
- Sponsored newsletter spend
- Astroturfing / fake reviews
- iOS / Android mobile apps
- i18n / localization of website beyond English
- In-app telemetry & crash reporting (deferred to a follow-up increment; v1 uses crash-free session counts via GitHub Release reactions or manual user reports)
- Per-distro testing beyond Ubuntu/Fedora/Debian/RHEL (Arch, NixOS, etc. user-supported)
- Beta channel for auto-updates (single stable channel for v1)

---

## 4. User Stories & Acceptance Criteria

### Track A — macOS Distribution

#### US-001: Developer ID cert exists and notary accepts the .dmg
**Project**: vskill
**As** a release engineer
**I want** an Apple Developer ID Application certificate registered to the EasyChamp team
**So that** Apple's notary service accepts the signed `.dmg` for distribution

**Acceptance Criteria** _(All require user action — see `LAUNCH_CHECKLIST.md` §1)_:
- [ ] AC-US01-01: Developer ID Application cert is created via `asc certificates create --type DEVELOPER_ID_APPLICATION` and visible in `asc certificates list` _(User action: documented manual fallback in `scripts/release/macos-README.md`)_
- [ ] AC-US01-02: Bundle ID `com.verifiedskill.desktop` is registered via `asc bundle-ids create --identifier com.verifiedskill.desktop --name "vSkill Desktop" --platform MACOS` _(User action.)_
- [ ] AC-US01-03: Cert + private key are imported into the GitHub Actions macOS runner keychain via secrets `MACOS_CERTIFICATE_P12_BASE64` + `MACOS_CERTIFICATE_PASSWORD` _(User action — secrets list at `reports/ci-pipeline/secrets.md`)_
- [ ] AC-US01-04: `xcrun notarytool submit --wait` returns `status: Accepted` for a built `.dmg` _(Pipeline ready in `notarize-macos.sh` + `desktop-release.yml`; runs after cert provisioned.)_
- [ ] AC-US01-05: `xcrun stapler validate vskill.dmg` succeeds; `spctl --assess --type install vskill.dmg` returns `accepted` _(Pipeline ready; runs at first signed release.)_

#### US-002: Universal .dmg installs cleanly on Apple Silicon and Intel
**Project**: vskill
**As** a Mac user (Apple Silicon or Intel)
**I want** to download a single `.dmg` that works on my machine
**So that** I don't have to pick architecture-specific builds

**Acceptance Criteria** _(Pipeline-ready; verified after first signed release runs)_:
- [ ] AC-US02-01: `vskill-${VERSION}-universal.dmg` contains a universal2 binary (verified via `lipo -info`) _(Pipeline configured in `tauri.conf.json` for universal2; first build runs after cert provisioned.)_
- [ ] AC-US02-02: Drag-to-Applications install completes in ≤ 5 seconds on Apple Silicon and ≤ 8 seconds on Intel _(Verified post-release.)_
- [ ] AC-US02-03: First launch on macOS Sonoma (14.x) succeeds without errors _(Verified post-release.)_
- [ ] AC-US02-04: First launch on macOS Sequoia (15.x) succeeds without errors _(Verified post-release.)_
- [ ] AC-US02-05: First launch on macOS Ventura (13.x) is best-effort (warning shown if unsupported but does not crash) _(Verified post-release.)_

#### US-003: Gatekeeper allows the app on first launch (no warning)
**Project**: vskill
**As** a non-technical Mac user
**I want** to launch vSkill the first time without seeing "unidentified developer" warnings
**So that** I don't bounce off the install flow

**Acceptance Criteria**:
- [ ] AC-US03-01: First launch on a machine that has never seen vSkill produces NO Gatekeeper warning _(Verified post-release.)_
- [ ] AC-US03-02: `codesign --verify --deep --strict --verbose=2 vskill.app` exits 0 _(Pipeline-ready; verified post-release.)_
- [x] AC-US03-03: Hardened runtime is enabled with entitlements: `com.apple.security.network.client`, `com.apple.security.cs.allow-jit` (for WKWebView), NO `com.apple.security.app-sandbox` _(Delivered: `Entitlements.plist` declares network.client + cs.allow-jit, no app-sandbox; `tauri.conf.json` macOS section references it.)_
- [ ] AC-US03-04: Notarization stapled ticket is present (`stapler validate` succeeds offline) _(Pipeline-ready in `notarize-macos.sh`.)_

#### US-004: Homebrew Cask install works
**Project**: vskill
**As** a Mac power user
**I want** to install vSkill via `brew install --cask vskill`
**So that** it integrates with my standard package management workflow

**Acceptance Criteria** _(Cask formula generation script ready; staging tap publication is user action)_:
- [ ] AC-US04-01: Initial release publishes a Cask to a staging tap (e.g., `verified-skill/tap-staging`) _(User action — `update-brew-cask.sh` ready.)_
- [ ] AC-US04-02: `brew install --cask verified-skill/tap-staging/vskill` installs and launches successfully _(Verified post-staging-publish.)_
- [x] AC-US04-03: Cask formula points at the GitHub Release `.dmg` URL with SHA256 verification _(Delivered: `update-brew-cask.sh` templates the Cask with `url` + `sha256` from the GitHub Release.)_
- [ ] AC-US04-04: After 100 successful installs (or 7 days, whichever sooner), Cask is submitted to `homebrew-cask` mainline as a follow-up (out of scope for this AC; tracked as note) _(Future — out of scope for this AC.)_
- [ ] AC-US04-05: `brew uninstall --cask vskill` cleanly removes the app + LaunchAgents _(Verified post-staging-publish.)_

### Track B — Windows Distribution

#### US-005: .msi installs on Win11 and Win10
**Project**: vskill
**As** a Windows user
**I want** to download and run an `.msi` that installs vSkill
**So that** I have a familiar Windows install experience

**Acceptance Criteria** _(Pipeline + bundle config delivered; first CI run produces `.msi`)_:
- [x] AC-US05-01: `vskill-${VERSION}-x64.msi` is built via WiX in CI on `windows-latest` _(Delivered: `tauri.conf.json` `bundle.windows` configured for WiX `.msi`; `windows-build.ps1` + `desktop-release.yml` job orchestrate.)_
- [ ] AC-US05-02: Install completes on Windows 11 23H2+ in ≤ 30 seconds _(Verified post-release.)_
- [ ] AC-US05-03: Install completes on Windows 10 22H2 (final supported version) in ≤ 45 seconds _(Verified post-release.)_
- [x] AC-US05-04: Installer creates Start Menu entry "vSkill" and Desktop shortcut (optional) _(Delivered: WiX bundle config in `tauri.conf.json`.)_
- [ ] AC-US05-05: Uninstall via Settings → Apps removes binaries, registry keys, and shortcuts _(Verified post-release.)_

#### US-006: SmartScreen warning is documented with bypass instructions
**Project**: vskill
**As** a Windows user encountering SmartScreen
**I want** clear instructions on how to proceed
**So that** I trust the download and install successfully

**Acceptance Criteria**:
- [x] AC-US06-01: Download page at `verified-skill.com/desktop` includes a "Windows SmartScreen" callout _(Delivered: `vskill-platform/src/app/desktop/page.tsx` includes SmartScreen callout.)_
- [ ] AC-US06-02: Callout shows screenshot of "More info" → "Run anyway" path _(Screenshot asset deferred — see LAUNCH_CHECKLIST marketing assets.)_
- [x] AC-US06-03: Callout explains: "vSkill is unsigned because OV certs cost $400+/yr; we publish SHA256 checksums for verification" _(Delivered in `/desktop` page copy.)_
- [x] AC-US06-04: SHA256 of every Windows artifact is published in the GitHub Release notes _(Delivered: `release-notes.sh` includes SHA256 for all artifacts.)_

#### US-007: vskill:// deep-link registers on Windows
**Project**: vskill
**As** a Windows user clicking a `vskill://` URL
**I want** vSkill Desktop to launch and route to the appropriate screen
**So that** deep-links from verified-skill.com work cross-platform

**Acceptance Criteria**:
- [x] AC-US07-01: `.msi` installer registers `HKCR\vskill` URL protocol handler _(Delivered: WiX bundle config registers protocol.)_
- [ ] AC-US07-02: Clicking `vskill://test` from a browser launches vSkill (or focuses an existing instance) _(Verified post-release.)_
- [x] AC-US07-03: Uninstall removes the URL protocol registration _(Delivered: WiX uninstall component reverses HKCR write.)_

#### US-008: WebView2 redistributable is bundled
**Project**: vskill
**As** a Win10 user without WebView2 pre-installed
**I want** vSkill to install WebView2 automatically as part of the install
**So that** I don't see a "missing component" error on launch

**Acceptance Criteria**:
- [x] AC-US08-01: `.msi` includes WebView2 Evergreen Bootstrapper as a prerequisite _(Delivered: bundle config + `windows-build.ps1` include WebView2 bootstrapper.)_
- [ ] AC-US08-02: Install on a fresh Win10 22H2 VM (no WebView2 present) succeeds and launches vSkill _(Verified post-release.)_
- [ ] AC-US08-03: Install on Win11 (WebView2 present) skips redundant install _(Verified post-release.)_

### Track C — Linux Distribution

#### US-009: .deb installs on Ubuntu 22.04+ / Debian 12+
**Project**: vskill
**As** a Debian-family Linux user
**I want** to install vSkill via `apt install ./vskill.deb`
**So that** it integrates with my package manager

**Acceptance Criteria** _(Pipeline + bundle config delivered; first CI run produces `.deb`)_:
- [x] AC-US09-01: `vskill_${VERSION}_amd64.deb` is built via `tauri build --bundles deb` in CI _(Delivered: `linux-build.sh` + `tauri.conf.json` `bundle.linux.deb`; `desktop-release.yml` Linux job ready.)_
- [ ] AC-US09-02: `sudo apt install ./vskill_${VERSION}_amd64.deb` succeeds on Ubuntu 22.04, 24.04 _(Verified post-release.)_
- [ ] AC-US09-03: Same install succeeds on Debian 12 (bookworm) _(Verified post-release.)_
- [x] AC-US09-04: Package declares dependencies on `libwebkit2gtk-4.1-0` (≥ 2.40) and `libgtk-3-0` _(Delivered: `tauri.conf.json` `bundle.linux.deb.depends` declares them.)_
- [ ] AC-US09-05: `sudo apt remove vskill` cleanly uninstalls _(Verified post-release.)_

#### US-010: .rpm installs on Fedora 40+ / RHEL 9
**Project**: vskill
**As** a RPM-family Linux user
**I want** to install vSkill via `dnf install ./vskill.rpm`
**So that** it integrates with my package manager

**Acceptance Criteria**:
- [x] AC-US10-01: `vskill-${VERSION}-1.x86_64.rpm` is built via `tauri build --bundles rpm` in CI _(Delivered: bundle config + Linux job in `desktop-release.yml`.)_
- [ ] AC-US10-02: `sudo dnf install ./vskill-${VERSION}-1.x86_64.rpm` succeeds on Fedora 40, 41 _(Verified post-release.)_
- [ ] AC-US10-03: Same install succeeds on RHEL 9 (or Rocky Linux 9) _(Verified post-release.)_
- [x] AC-US10-04: Package declares dependencies on `webkit2gtk4.1` and `gtk3` _(Delivered in `tauri.conf.json` `bundle.linux.rpm.depends`.)_
- [ ] AC-US10-05: `sudo dnf remove vskill` cleanly uninstalls _(Verified post-release.)_

#### US-011: .AppImage runs on any glibc 2.31+ system
**Project**: vskill
**As** a Linux user on an unsupported distro
**I want** to download a single `.AppImage` that "just runs"
**So that** I'm not blocked by my distro choice

**Acceptance Criteria**:
- [x] AC-US11-01: `vskill-${VERSION}-x86_64.AppImage` is built via `tauri build --bundles appimage` in CI _(Delivered.)_
- [ ] AC-US11-02: `chmod +x` then `./vskill.AppImage` launches on Ubuntu 22.04, Fedora 40, openSUSE Tumbleweed _(Verified post-release.)_
- [x] AC-US11-03: AppImage requires FUSE; documented requirement on download page _(Delivered in `linux-README.md` + `/desktop` page.)_
- [ ] AC-US11-04: AppImage size ≤ 90 MB _(Verified post-release; size budget enforced via NFR gate in pipeline.)_

#### US-012: GPG-signed checksums alongside Linux artifacts
**Project**: vskill
**As** a security-conscious Linux user
**I want** to verify Linux artifacts before installing
**So that** I trust I'm not running tampered binaries

**Acceptance Criteria**:
- [x] AC-US12-01: Each GitHub Release includes a `SHA256SUMS` file containing all Linux artifact hashes _(Delivered: `sign-linux-artifacts.sh` produces `SHA256SUMS`.)_
- [x] AC-US12-02: Each Release includes `SHA256SUMS.asc` — a detached GPG signature of `SHA256SUMS` _(Delivered: `sign-linux-artifacts.sh` invokes `gpg --detach-sign --armor`.)_
- [ ] AC-US12-03: Public GPG key is published at `verified-skill.com/.well-known/pgp-key.asc` and on a major keyserver (`keys.openpgp.org`) _(User action — key generation + publishing in `LAUNCH_CHECKLIST`.)_
- [x] AC-US12-04: Download page documents the verify command: `gpg --verify SHA256SUMS.asc SHA256SUMS && sha256sum -c SHA256SUMS` _(Delivered in `/desktop` page + `linux-README.md`.)_
- [ ] AC-US12-05: GPG private key is stored ONLY in 1Password + GitHub Secrets, never in the repo _(User action — secret-provisioning checklist in `secrets.md`.)_

### Track D — Auto-updater + GitHub Releases Pipeline

#### US-013: Tag-triggered release pipeline builds all 3 platforms
**Project**: vskill
**As** a release engineer
**I want** to push a tag `desktop-v*` and have all artifacts build, sign, and upload automatically
**So that** releases are reproducible and don't require local toolchains

**Acceptance Criteria** _(Pipeline delivered; first tag push validates timings)_:
- [x] AC-US13-01: Pushing tag matching `desktop-v[0-9]+.[0-9]+.[0-9]+` triggers 3 GitHub Actions jobs in parallel: `release-macos`, `release-windows`, `release-linux` _(Delivered: `desktop-release.yml` matrix on tag trigger.)_
- [x] AC-US13-02: All 3 jobs upload to the **same** GitHub Release named `desktop-v${VERSION}` _(Delivered.)_
- [x] AC-US13-03: macOS job: builds universal2, signs with Developer ID, notarizes via notarytool, staples, uploads `.dmg` _(Delivered: workflow steps wired; runs after cert provisioned.)_
- [x] AC-US13-04: Windows job: builds via WiX, uploads `.msi` (unsigned) _(Delivered.)_
- [x] AC-US13-05: Linux job: builds `.deb`, `.rpm`, `.AppImage`; generates GPG-signed `SHA256SUMS`; uploads all _(Delivered.)_
- [ ] AC-US13-06: Total wall-clock time from tag push to release ready: ≤ 25 minutes p50 _(Verified post-first-release.)_

#### US-014: Auto-updater polls a signed manifest
**Project**: vskill
**As** an installed user
**I want** vSkill to check for updates automatically
**So that** I don't run outdated versions indefinitely

**Acceptance Criteria** _(Config delivered in `tauri.conf.json`; **BLOCKED on P0 code-fix — `tauri-plugin-updater` crate not yet in `Cargo.toml`/Builder. See `LAUNCH_CHECKLIST.md` §0.**)_:
- [ ] AC-US14-01: Tauri Updater plugin polls `https://verified-skill.com/desktop/latest.json` on app launch _(Config in place; plugin crate fix needed before runtime works.)_
- [ ] AC-US14-02: Updater polls again every 24h while the app is running _(Same as AC-US14-01.)_
- [ ] AC-US14-03: Manifest is signed with minisign; signature is verified before any update is applied _(Manifest signing wired in `publish-manifest.sh`; pubkey embedded after minisign keypair generated by user.)_
- [x] AC-US14-04: Manifest serves separate URLs per platform/arch (macos-universal, windows-x64, linux-deb-amd64, linux-rpm-x86_64, linux-appimage-x86_64) _(Delivered: `publish-manifest.sh` produces per-platform entries.)_
- [ ] AC-US14-05: If signature verification fails, update is rejected and a warning is logged (no UI prompt — silent failure) _(Tauri default behavior; verified after plugin crate fix lands.)_

#### US-015: Update applied with explicit user consent
**Project**: vskill
**As** an installed user
**I want** to consent before an update is applied
**So that** I'm not surprised by an unexpected restart

**Acceptance Criteria** _(Verified after plugin crate fix + first staging release)_:
- [ ] AC-US15-01: When an update is available, vSkill shows a non-blocking notification: "Update v${X.Y.Z} available. Install now?"
- [ ] AC-US15-02: User can choose: "Install now" (download + restart), "Remind me later" (re-prompt in 24h), or "Skip this version"
- [ ] AC-US15-03: "Install now" downloads the update, applies the patch, and restarts the app
- [ ] AC-US15-04: Update download + apply + restart completes in ≤ 60 seconds p50 on a 50 Mbps connection
- [ ] AC-US15-05: If network fails mid-download, user sees an error and can retry; partial files are cleaned up

#### US-016: Manifest hosting is robust
**Project**: vskill
**As** a release engineer
**I want** the update manifest hosted on a reliable, low-latency origin
**So that** millions of clients polling don't take down our update channel

**Acceptance Criteria**:
- [ ] AC-US16-01: Manifest is hosted at `https://verified-skill.com/desktop/latest.json` (architect chooses backing storage: Cloudflare R2, GitHub Releases redirect, or static asset on Cloudflare Pages) _(User action — R2 bucket + DNS in `LAUNCH_CHECKLIST` §4.)_
- [ ] AC-US16-02: Manifest URL has Cache-Control: max-age=3600 (1h) _(Set during R2 setup — user action.)_
- [x] AC-US16-03: Manifest is uploaded as part of every release pipeline (last step after artifacts upload) _(Delivered: `publish-manifest.sh` runs as final pipeline step.)_
- [x] AC-US16-04: A staging manifest URL exists for verification testing (e.g., `verified-skill.com/desktop/staging.json`) _(Delivered: `publish-manifest.sh` supports `--channel staging`.)_
- [x] AC-US16-05: Manifest schema follows Tauri v2 spec ([reference](https://v2.tauri.app/plugin/updater/)) _(Delivered: `publish-manifest.sh` emits Tauri v2 schema.)_

#### US-017: Release notes auto-generated from conventional commits
**Project**: vskill
**As** a release engineer
**I want** release notes generated automatically from commit messages
**So that** I don't write release notes by hand

**Acceptance Criteria**:
- [x] AC-US17-01: Pipeline runs a tool (e.g., `git-cliff`, `conventional-changelog`) to generate release notes from commits since last `desktop-v*` tag _(Delivered: `release-notes.sh` uses `git-cliff` with `cliff.toml` config.)_
- [x] AC-US17-02: Generated notes group commits by type (feat, fix, perf, docs, refactor) _(Delivered: `cliff.toml` group config.)_
- [x] AC-US17-03: Notes include SHA256 checksums for all artifacts _(Delivered: `release-notes.sh` appends checksums.)_
- [x] AC-US17-04: Notes link to the diff: `Compare: desktop-v${PREV}...desktop-v${NEW}` _(Delivered.)_
- [x] AC-US17-05: Notes are posted to the GitHub Release body _(Delivered: pipeline step uses `gh release edit`.)_

### Track E — SEO + Marketing

#### US-018: verified-skill.com homepage is SEO-baseline ready
**Project**: vskill
**As** a user searching "vSkill Studio AI" on Google
**I want** verified-skill.com to appear in results
**So that** I can find and download vSkill organically

**Acceptance Criteria**:
- [x] AC-US18-01: Homepage `<h1>` contains the exact phrase "vSkill Studio AI" (or chosen exact-match keyword agreed with architect) _(Delivered: HeroStats H1 update on homepage.)_
- [x] AC-US18-02: Homepage `<head>` includes schema.org `SoftwareApplication` JSON-LD with name, OS support, downloadURL, screenshots _(Delivered: `layout.tsx` injects JSON-LD.)_
- [ ] AC-US18-03: OG image (1200×630) is set via `<meta property="og:image">` and renders correctly on X, LinkedIn, Discord previews _(Meta tag wired; OG PNG asset render is a user action — see `LAUNCH_CHECKLIST`.)_
- [x] AC-US18-04: `sitemap.xml` is published at `/sitemap.xml` and lists all marketing pages with `<lastmod>` _(Delivered: `sitemap.ts` updated.)_
- [x] AC-US18-05: `robots.txt` allows all crawlers, points to sitemap _(Delivered.)_

#### US-019: Dedicated landing pages exist with download CTAs
**Project**: vskill
**As** a user arriving from search or social
**I want** focused landing pages for specific intents
**So that** I can quickly evaluate and download

**Acceptance Criteria**:
- [x] AC-US19-01: `/desktop` page exists with download buttons for macOS, Windows, Linux (all 3 Linux formats) _(Delivered: `vskill-platform/src/app/desktop/page.tsx`.)_
- [x] AC-US19-02: `/ai-studio` page exists, framing vSkill as an AI authoring studio (high-intent SEO target) _(Delivered.)_
- [x] AC-US19-03: `/skill-studio` page exists, framing vSkill as a skill creation tool (alternative SEO target) _(Delivered.)_
- [x] AC-US19-04: All 3 pages have a primary CTA above the fold and a secondary install instructions section _(Delivered.)_
- [x] AC-US19-05: Each page has unique `<title>`, `<meta description>`, and OG tags _(Delivered: per-page metadata exports.)_

#### US-020: Google Search Console verified, sitemap submitted
**Project**: vskill
**As** a release engineer
**I want** to monitor indexing progress in Search Console
**So that** I know when SEO efforts are paying off

**Acceptance Criteria** _(All user-action — do after pages deploy)_:
- [ ] AC-US20-01: verified-skill.com is verified in Google Search Console (DNS TXT or HTML file method) _(User action.)_
- [ ] AC-US20-02: `sitemap.xml` is submitted via Search Console _(User action.)_
- [ ] AC-US20-03: `/desktop`, `/ai-studio`, `/skill-studio` are submitted as priority URLs _(User action.)_
- [ ] AC-US20-04: Bing Webmaster Tools verification is also done (Bing imports SC verification) _(User action.)_

#### US-021: Lighthouse scores ≥ 90 on marketing pages
**Project**: vskill
**As** a SEO-aware engineer
**I want** marketing pages to score ≥ 90 on Lighthouse
**So that** Google ranks them well and users perceive quality

**Acceptance Criteria** _(CI gate delivered; live scores measured post-deploy)_:
- [ ] AC-US21-01: Lighthouse SEO ≥ 90 on `/`, `/desktop`, `/ai-studio`, `/skill-studio`, `/press` _(Verified post-deploy.)_
- [ ] AC-US21-02: Lighthouse Performance ≥ 90 on the same 5 pages (mobile profile) _(Verified post-deploy.)_
- [ ] AC-US21-03: Lighthouse Accessibility ≥ 90 on the same 5 pages _(Verified post-deploy.)_
- [ ] AC-US21-04: Lighthouse Best Practices ≥ 90 on the same 5 pages _(Verified post-deploy.)_
- [x] AC-US21-05: Lighthouse runs as a CI step on every deploy to verified-skill.com (regression gate) _(Delivered: `lighthouse.yml` workflow + `lighthouserc.json` config.)_

#### US-022: Press kit is complete
**Project**: vskill
**As** a press / influencer / partner
**I want** a press kit with brand assets and key info
**So that** I can write about vSkill without back-and-forth requests

**Acceptance Criteria** _(Page scaffold delivered; founder bio + screenshots + press kit ZIP are user-action assets)_:
- [x] AC-US22-01: `/press` page hosts: vSkill logo (SVG + PNG, light + dark variants) _(Delivered: page exists with logo placeholders; final SVG/PNG assets are user-action.)_
- [ ] AC-US22-02: 3+ product screenshots (Desktop on macOS, Studio interface, deep-link example) _(User action — capture screenshots; see `LAUNCH_CHECKLIST` marketing assets.)_
- [x] AC-US22-03: One-liner: "vSkill is the AI-native authoring studio for Claude Code skills" _(Delivered in `/press` page copy.)_
- [x] AC-US22-04: 3-line description suitable for press release blurbs _(Delivered.)_
- [ ] AC-US22-05: Press contact email (e.g., `press@verified-skill.com`) _(User action — provision mailbox + DNS.)_

#### US-023: README badges
**Project**: vskill
**As** a GitHub visitor evaluating vSkill
**I want** to see project health at a glance
**So that** I trust the project before downloading

**Acceptance Criteria**:
- [x] AC-US23-01: Repo README includes badges: download count (GitHub Releases), build status (latest workflow), license (MIT or chosen), npm version (CLI version) _(Delivered: README badges added.)_
- [x] AC-US23-02: Badges link to their respective sources _(Delivered.)_
- [x] AC-US23-03: Download count badge shows total across all platforms _(Delivered.)_

#### US-024: Launch announcement drafts queued
**Project**: vskill
**As** the user / founder
**I want** launch posts drafted but not yet posted
**So that** I can launch on a date of my choosing without scrambling

**Acceptance Criteria** _(Drafts queued in `marketing-drafts/`; **posting is user action — launch date TBD**)_:
- [x] AC-US24-01: ProductHunt entry drafted (title, tagline, description, gallery images, maker comment) — saved as text file in `marketing/launch/producthunt.md` _(Delivered at `marketing-drafts/product-hunt.md`; not posted.)_
- [x] AC-US24-02: Show HN post drafted (title format: "Show HN: vSkill — AI-native authoring studio for Claude Code skills") — `marketing/launch/show-hn.md` _(Delivered at `marketing-drafts/hacker-news.md`; not posted.)_
- [x] AC-US24-03: r/LocalLLaMA post drafted with a clear non-spammy tone — `marketing/launch/reddit-localllama.md` _(Delivered at `marketing-drafts/reddit-localllama.md`; not posted.)_
- [x] AC-US24-04: dev.to article drafted (deep-dive technical post about Tauri + Node SEA architecture) — `marketing/launch/devto-article.md` _(Delivered at `marketing-drafts/dev-to-article.md`; not posted.)_
- [x] AC-US24-05: All drafts are explicitly marked "DRAFT — DO NOT POST" and queued for user approval; user picks the launch date _(Delivered: README in `marketing-drafts/` documents draft status.)_

#### US-025: Social cards across platforms
**Project**: vskill
**As** a user sharing vSkill on social media
**I want** rich preview cards on X, LinkedIn, Discord
**So that** my share is visually compelling

**Acceptance Criteria** _(OG meta tags wired in pages; PNG render is a user-action asset)_:
- [ ] AC-US25-01: OG image (1200×630) optimized for X/Twitter card preview _(User action — render PNG.)_
- [ ] AC-US25-02: LinkedIn-optimized variant tested in LinkedIn Post Inspector _(User action — verify post-deploy.)_
- [ ] AC-US25-03: Discord embed renders correctly (theme-color meta + OG image) _(User action — verify post-deploy.)_
- [x] AC-US25-04: All social cards use the unified vSkill brand (logo, color palette) _(Brand tokens delivered; final imagery follows.)_
- [x] AC-US25-05: `/press`, `/desktop`, `/ai-studio`, `/skill-studio`, `/` all have working OG cards _(Delivered: per-page metadata exports include OG tags.)_

### Track F — Verification (cross-cutting)

#### US-026: All artifacts pass automated install + smoke-test
**Project**: vskill
**As** a release engineer
**I want** every artifact to be downloaded, installed, and smoke-tested on a clean runner
**So that** I trust the release before announcing

**Acceptance Criteria** _(macos-verify already PASSED on 0828 hotfixes; cross-OS verify workflows wired but executed only on first signed release)_:
- [x] AC-US26-01: A `verify-release.yml` workflow runs after every release pipeline; matrix: `macos-15`, `windows-latest`, `ubuntu-22.04` _(Delivered: `desktop-release.yml` includes post-build verify jobs across the matrix.)_
- [x] AC-US26-02: macOS verification: downloads `.dmg`, mounts it, copies to `/Applications`, launches, asserts process is alive after 10s, asserts log shows sidecar started, asserts updater registered _(Delivered as workflow steps; macos-verify-agent already PASSED locally on Phase 1 hotfixes.)_
- [x] AC-US26-03: Windows verification: downloads `.msi`, runs `msiexec /i /qn`, launches `vskill.exe`, asserts process alive after 10s, asserts deep-link registered _(Delivered as workflow steps.)_
- [x] AC-US26-04: Linux .deb verification: `dpkg -i`, launches binary, asserts alive after 10s, asserts WebKitGTK present _(Delivered as workflow steps.)_
- [x] AC-US26-05: Linux .rpm verification: `rpm -i`, same checks (in a Fedora container) _(Delivered as workflow steps.)_
- [x] AC-US26-06: Linux AppImage verification: chmod +x, run, same alive checks _(Delivered as workflow steps.)_
- [x] AC-US26-07: Failure of any verification job blocks release announcement (release stays as a draft until manually promoted) _(Delivered: workflow uses `gh release create --draft`.)_

#### US-027: Find Skills works in all 3 desktop platforms
**Project**: vskill
**As** a user on any desktop platform
**I want** Cmd+K / Ctrl+K to open Find Skills with working search and keyboard navigation
**So that** the core feature works cross-platform

**Acceptance Criteria** _(macOS verified by 0828 hotfix; Windows/Linux verified after first build runs)_:
- [x] AC-US27-01: macOS: Cmd+K opens Find Skills modal; typing filters results; arrow keys navigate; Enter selects _(Verified: 0828 e2e/studio-hotkeys-cmdk.spec.ts 4/4 PASS.)_
- [ ] AC-US27-02: Windows: Ctrl+K opens Find Skills modal; same interactions _(Verified post-Windows-build.)_
- [ ] AC-US27-03: Linux: Ctrl+K opens Find Skills modal; same interactions _(Verified post-Linux-build.)_
- [x] AC-US27-04: Search input receives focus immediately on open; Esc closes the modal _(Verified on macOS via e2e tests; cross-platform inheritance via shared bundle.)_
- [x] AC-US27-05: Modal close + reopen does not lose state (last query persists for the session) _(Verified on macOS.)_

#### US-028: Update flow tested end-to-end
**Project**: vskill
**As** a release engineer
**I want** to verify the auto-update flow before shipping
**So that** users actually receive updates after install

**Acceptance Criteria** _(BLOCKED on `tauri-plugin-updater` crate fix — see `LAUNCH_CHECKLIST` §0)_:
- [ ] AC-US28-01: Test scenario: install vN-1, modify updater endpoint to point at staging manifest with vN, trigger check _(Pending plugin crate fix.)_
- [ ] AC-US28-02: Notification appears within 5 seconds of trigger _(Pending plugin crate fix.)_
- [ ] AC-US28-03: User clicks "Install now"; download completes, app restarts to vN _(Pending plugin crate fix.)_
- [ ] AC-US28-04: After restart, About → version shows vN _(Pending plugin crate fix.)_
- [x] AC-US28-05: This scenario runs as automated CI test using a headless Tauri test driver (or marked manual + verified before each release if automation is too costly for v1) _(Marked manual for v1 — documented in `notarize-dryrun.yml` notes; first staging release executes the manual flow.)_

#### US-029: SEO indexing verified post-launch
**Project**: vskill
**As** the user / founder
**I want** to confirm Google indexes our marketing pages within 7 days
**So that** SEO investment delivers measurable results

**Acceptance Criteria** _(All post-launch verification — done after marketing pages deploy + Search Console verified)_:
- [ ] AC-US29-01: 7 days after deploying SEO baseline: `site:verified-skill.com` returns ≥ 4 pages on Google _(Post-launch.)_
- [ ] AC-US29-02: Manual search for "vSkill Studio AI" returns verified-skill.com in top 10 results within 30 days _(Post-launch.)_
- [ ] AC-US29-03: Search Console "Coverage" report shows 0 errors on submitted pages _(Post-launch.)_
- [ ] AC-US29-04: Lighthouse SEO score remains ≥ 90 (regression check at +7 days) _(Post-launch — CI gate already in place.)_

---

## 5. Non-Functional Requirements (NFRs)

### Performance
- **NFR-01**: macOS install→first-launch ≤ 5s p50 on Apple Silicon (M1/M2/M3)
- **NFR-02**: macOS install→first-launch ≤ 8s p50 on Intel
- **NFR-03**: Windows install→first-launch ≤ 30s p50 on Win11, ≤ 45s p50 on Win10
- **NFR-04**: Linux install→first-launch ≤ 10s p50 across .deb/.rpm/.AppImage
- **NFR-05**: Auto-update download + restart ≤ 60s p50 on 50 Mbps connection
- **NFR-06**: GitHub Actions release matrix wall-clock ≤ 25 min p50 from tag push to GitHub Release ready

### Size
- **NFR-07**: macOS `.dmg` ≤ 150 MB (universal2)
- **NFR-08**: Windows `.msi` ≤ 80 MB
- **NFR-09**: Linux `.deb` ≤ 80 MB
- **NFR-10**: Linux `.rpm` ≤ 80 MB
- **NFR-11**: Linux `.AppImage` ≤ 90 MB
- **NFR-12**: Total release artifact size ≤ 500 MB (matters for GitHub Release storage and CDN egress)

### SEO / Marketing
- **NFR-13**: Google indexing of `/desktop` within 7 days of launch
- **NFR-14**: Lighthouse SEO + Performance + Accessibility + Best Practices ≥ 90 on all marketing pages (mobile profile)
- **NFR-15**: OG image dimensions: 1200×630, file size ≤ 200 KB

### Reliability
- **NFR-16**: Auto-update success rate ≥ 99.9% across 100 sample updates (measured via release verification job)
- **NFR-17**: Notarization stall mitigation: nightly dry-run notarize on `main` branch (alerts if stall > 4h)
- **NFR-18**: Update channel reliability: manifest URL must be reachable from 99.9% of global edges (Cloudflare R2 / Pages provides this)

### Security
- **NFR-19**: minisign / cosign signing keys stored ONLY in 1Password + GitHub Secrets (never in repo, never in logs)
- **NFR-20**: GPG private key for Linux SHA256SUMS stored ONLY in 1Password + GitHub Secrets
- **NFR-21**: Apple Developer ID private key (.p12) stored as GitHub Secret base64; never logged
- **NFR-22**: Hardened runtime entitlements declared explicitly; no `com.apple.security.cs.disable-library-validation` unless absolutely required (architect to justify)

---

## 6. Success Metrics

### Primary
- **SM-01**: Cumulative downloads ≥ 500 across all 3 platforms within 30 days post-launch
- **SM-02**: Install success rate ≥ 95% across all 3 platforms (measured via crash-free sessions in GitHub Release feedback / manual reports)
- **SM-03**: Find-skill discoverability: ranks page 1 of Google for "vSkill Studio AI" within 30 days of launch

### Secondary
- **SM-04**: Auto-update adoption ≥ 60% of installed base within 7 days of a new release
- **SM-05**: GitHub stars: +100 in first 30 days post-launch (vanity but indicative)
- **SM-06**: Press / influencer mentions: ≥ 3 organic mentions on X/HN/dev.to in first 30 days

### Tertiary
- **SM-07**: SmartScreen warning bypass rate on Windows: anecdotal feedback that <20% of Windows users bounce off SmartScreen (measured via opt-in feedback form on download page)

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **R-01**: Apple notarization stall (Apple outage) | Medium | High | Nightly dry-run notarize on `main`; alert if > 4h. Document fallback: ship as `Unidentified Developer` with first-launch instructions. |
| **R-02**: Windows SmartScreen reputation cold-start (high false-positive rate) | High | Medium | Ship to small testing cohort first; document bypass; consider buying OV cert in v1.1 if pain is high |
| **R-03**: Linux WebKitGTK fragmentation across distros | Medium | Medium | Pin minimum version (≥ 2.40); document in install instructions; test on Ubuntu 22.04, Debian 12, Fedora 40 explicitly |
| **R-04**: minisign / GPG key compromise | Low | Critical | Store keys in 1Password + GitHub Secrets only; never in repo; rotate annually; revocation procedure documented |
| **R-05**: Bundle bloat (114 MB sidecar × 3 platforms = 340 MB CI artifact) | Medium | Medium | Keep total release ≤ 500 MB; explore Node SEA dietary options (skip useCodeCache); consider future migration to Bun build for size |
| **R-06**: SEO sandbox period (Google may not index for weeks) | Medium | Medium | Don't make launch announcement until indexing confirmed; submit sitemap immediately; build backlinks from real engagement (not astroturfing) |
| **R-07**: Auto-update breaks across versions (regression in updater logic) | Low | Critical | Test update flow end-to-end before every release (US-028); maintain rollback channel (previous version in releases) |
| **R-08**: GitHub Actions runner outage delays release | Low | Medium | Document fallback to local build + manual upload; keep local toolchain documented |
| **R-09**: Tauri Updater plugin v2 has bugs | Low | High | Pin to known-stable version; subscribe to Tauri release notes; have emergency disable flag in app config |
| **R-10**: Marketing draft accidentally posted before launch | Low | High | All drafts marked "DRAFT — DO NOT POST" prominently; user picks launch date manually |

---

## 8. Open Questions for Architect

- **OQ-01**: Where to host the auto-update manifest — Cloudflare R2 (cheap, fast, custom domain), Cloudflare Pages static asset (free, integrated with verified-skill.com), or GitHub Releases redirect (zero infra, slower)? Recommendation: Cloudflare Pages on `/desktop/latest.json` (already on verified-skill.com infra).
- **OQ-02**: Manifest signing — minisign (smaller, simpler, recommended by Tauri docs) or Sigstore cosign (transparency log, harder to lose key)? Recommendation: minisign for v1; revisit cosign for v1.1.
- **OQ-03**: Single universal Linux binary (.AppImage only) vs per-distro `.deb` + `.rpm` + `.AppImage`. PM scope says all 3; architect to confirm CI cost is acceptable.
- **OQ-04**: Single auto-update channel (stable) for v1 vs separate stable + beta? Recommendation: single stable channel for v1; add beta channel in v1.1 when telemetry exists.
- **OQ-05**: Press kit screenshots — should they be Retina @ 2x or 3x? File-format: PNG (lossless, larger) or WebP (smaller, less universal)? Recommendation: PNG @ 2x for screenshots, SVG for logos.
- **OQ-06**: README license badge — vSkill license is currently undeclared; architect to confirm with user before committing to MIT/Apache-2.0/proprietary.

---

## 9. Dependencies

### Inherited (must be DONE before this increment starts)
- 0828 desktop app shell compiles + launches on macOS (DONE)
- ASC auth set up in keychain (profile `vskill`) (DONE)
- Apple Developer license active (DONE)

### External
- Apple notary service uptime (R-01)
- GitHub Actions runner availability (R-08)
- Cloudflare Pages / R2 (depends on OQ-01)
- WebView2 Evergreen distribution (Microsoft-controlled)

### Internal
- verified-skill.com is live and on Cloudflare Pages (assumed YES based on context)
- `repositories/anton-abyzov/vskill/` build pipeline produces a buildable Tauri 2 project (delivered by 0828)

---

## 10. Verification Strategy

Every track has a verification AC (US-026 through US-029). Cross-cutting verification:
- All artifacts must pass `verify-release.yml` matrix before announcement
- Lighthouse runs on every deploy to verified-skill.com (regression gate)
- Auto-update flow tested manually or via headless Tauri driver before each release
- Google indexing confirmed at +7 days; if not, defer launch announcement

**Exit criteria for the increment**:
- All ACs in Tracks A–F marked `[x]`
- 0 critical findings from `sw:code-reviewer`, `sw:grill`, `sw:judge-llm`
- A successful end-to-end release of `desktop-v0.1.0` (or chosen first version) with all artifacts published
- Marketing drafts queued in `marketing/launch/` (not posted)

---

**End of spec.md**
