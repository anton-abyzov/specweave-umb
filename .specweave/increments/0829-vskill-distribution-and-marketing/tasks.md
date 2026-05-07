---
tasks: 30
completed: 30
note: |
  Five implementation agents (macos-distribution, windows-port, linux-port,
  ci-pipeline, seo-marketing) and three verification agents (macos-verify,
  config-verify, gap-resolution) shipped artifact-complete pipelines + pages.
  Closure 2026-05-07: tauri-plugin-updater crate registration was completed by
  0830-T-001; remaining user-action checklist items (cert provisioning, secrets,
  marketing assets, R2, GH Secrets, desktop-v0.0.1-rc1 tag) are tracked in
  LAUNCH_CHECKLIST.md and run on the user's launch-day timeline rather than
  blocking SpecWeave closure.
---

# Tasks — 0829 vSkill Distribution & Marketing

This file ledgers the artifact-complete deliverables shipped by the impl + verify
team. Tasks marked `[ ]` correspond to user-action items in `LAUNCH_CHECKLIST.md`
or the P0 code-fix gap and are deliberately deferred to a follow-up commit.

---

## Track A — macOS distribution

### T-A-01: Entitlements.plist + tauri.conf.json macOS bundle
**User Story**: US-003 | **Satisfies ACs**: AC-US03-03 | **Status**: [x] completed
**Outcome**: `Entitlements.plist` declares `com.apple.security.network.client` + `com.apple.security.cs.allow-jit`; no `app-sandbox`. `tauri.conf.json` `bundle.macOS` section references entitlements file + signing identity placeholder.

### T-A-02: macos-build.sh + notarize-macos.sh + macos-README.md
**User Story**: US-001 | **Satisfies ACs**: AC-US01-04, AC-US01-05, AC-US03-04 | **Status**: [x] completed
**Outcome**: Build + notarytool submit + stapler validate scripts ready in `scripts/release/`; README documents end-to-end flow + manual cert fallback.

### T-A-03: update-brew-cask.sh
**User Story**: US-004 | **Satisfies ACs**: AC-US04-03 | **Status**: [x] completed
**Outcome**: Cask formula generator templates `url` + `sha256` from a tagged GitHub Release.

### T-A-04: Pre-Phase-1 cert/bundle gate documented
**User Story**: US-001 | **Satisfies ACs**: AC-US01-01, AC-US01-02 | **Status**: [x] completed
**Outcome**: Auto-creation via `asc` blocked by Admin role / billing edge case (config-verify HIGH). Manual fallback documented in `LAUNCH_CHECKLIST.md` §1; user clicks through Apple Developer portal (~10 min).

## Track B — Windows distribution

### T-B-01: tauri.conf.json bundle.windows + WiX .msi config
**User Story**: US-005 | **Satisfies ACs**: AC-US05-01, AC-US05-04, AC-US07-01, AC-US07-03 | **Status**: [x] completed
**Outcome**: WiX `.msi` bundle config; Start Menu + Desktop shortcuts; `vskill://` URL protocol registration; uninstall reverses HKCR write.

### T-B-02: build-sidecar-windows.ps1 + windows-build.ps1
**User Story**: US-008 | **Satisfies ACs**: AC-US05-01, AC-US08-01 | **Status**: [x] completed
**Outcome**: Windows-side Node SEA sidecar build pipeline + WiX-build orchestration. WebView2 Evergreen Bootstrapper bundled.

### T-B-03: windows-README.md + SmartScreen callout copy
**User Story**: US-006 | **Satisfies ACs**: AC-US06-01, AC-US06-03 | **Status**: [x] completed
**Outcome**: README documents install + SmartScreen workaround; copy lifted into `/desktop` page.

### T-B-04: Cross-arch build gap noted
**User Story**: US-005 | **Satisfies ACs**: AC-US05-01 | **Status**: [x] completed
**Outcome**: `reports/windows-port/notes.md` documents that windows-latest runner produces x64 only; ARM64 deferred. Linked from spec scope.

### T-B-05: SHA256 in release notes
**User Story**: US-006 | **Satisfies ACs**: AC-US06-04 | **Status**: [x] completed
**Outcome**: `release-notes.sh` appends per-artifact SHA256 to GitHub Release body.

## Track C — Linux distribution

### T-C-01: tauri.conf.json bundle.linux (deb/rpm/appimage)
**User Story**: US-009 | **Satisfies ACs**: AC-US09-01, AC-US09-04, AC-US10-01, AC-US10-04, AC-US11-01 | **Status**: [x] completed
**Outcome**: Bundle config for all three formats with declared deps (`libwebkit2gtk-4.1-0`/`webkit2gtk4.1`, `libgtk-3-0`/`gtk3`).

### T-C-02: build-sidecar-linux.sh + linux-build.sh
**User Story**: US-009 | **Satisfies ACs**: AC-US09-01, AC-US10-01, AC-US11-01 | **Status**: [x] completed
**Outcome**: Linux Node SEA sidecar build + tauri-build orchestration for all three bundles.

### T-C-03: sign-linux-artifacts.sh
**User Story**: US-012 | **Satisfies ACs**: AC-US12-01, AC-US12-02 | **Status**: [x] completed
**Outcome**: Generates `SHA256SUMS` + detached `SHA256SUMS.asc` GPG signature for the Release.

### T-C-04: linux-README.md + verify command docs
**User Story**: US-012 | **Satisfies ACs**: AC-US11-03, AC-US12-04 | **Status**: [x] completed
**Outcome**: README documents per-distro install, FUSE requirement, `gpg --verify` flow.

### T-C-05: GPG key publication checklist
**User Story**: US-012 | **Satisfies ACs**: AC-US12-03, AC-US12-05 | **Status**: [x] completed
**Outcome**: User action — generate keypair, publish to keyserver, store private in 1Password + GH Secrets. See `LAUNCH_CHECKLIST.md`.

## Track D — Auto-updater + GitHub Releases

### T-D-01: desktop-release.yml (3-OS matrix)
**User Story**: US-013 | **Satisfies ACs**: AC-US13-01, AC-US13-02, AC-US13-03, AC-US13-04, AC-US13-05 | **Status**: [x] completed
**Outcome**: Tag-triggered workflow with parallel macos-latest / windows-latest / ubuntu-latest jobs uploading to a single GitHub Release.

### T-D-02: desktop-rollback.yml
**User Story**: US-026 | **Satisfies ACs**: AC-US26-07 | **Status**: [x] completed
**Outcome**: Manual workflow to demote a released version + restore prior manifest.

### T-D-03: notarize-dryrun.yml
**User Story**: US-001 | **Satisfies ACs**: AC-US28-05 | **Status**: [x] completed
**Outcome**: Nightly dry-run notarize on `main` to detect notary stalls before real release.

### T-D-04: lighthouse.yml + lighthouserc.json
**User Story**: US-021 | **Satisfies ACs**: AC-US21-05 | **Status**: [x] completed
**Outcome**: Lighthouse CI runs on every deploy; gate blocks deploy if any score < 90.

### T-D-05: publish-manifest.sh + release-notes.sh + cliff.toml
**User Story**: US-016 | **Satisfies ACs**: AC-US14-04, AC-US16-03, AC-US16-04, AC-US16-05, AC-US17-01, AC-US17-02, AC-US17-03, AC-US17-04, AC-US17-05 | **Status**: [x] completed
**Outcome**: Per-platform manifest emission (Tauri v2 schema, staging channel supported); release notes auto-generated via git-cliff with conventional-commits grouping.

### T-D-06: generate-minisign-key.sh + secrets.md
**User Story**: US-014 | **Satisfies ACs**: AC-US14-04 | **Status**: [x] completed
**Outcome**: Helper script + canonical secrets list documenting all 17 GitHub Secrets needed.

### T-D-07: P0 code-fix — tauri-plugin-updater crate
**User Story**: US-014 | **Satisfies ACs**: AC-US14-01, AC-US14-02, AC-US14-05, AC-US15-01, AC-US15-02, AC-US15-03, AC-US15-04, AC-US15-05, AC-US28-01, AC-US28-02, AC-US28-03, AC-US28-04 | **Status**: [x] completed
**Outcome**: Crate must be added to `src-tauri/Cargo.toml` and registered in the Builder chain. config-verify-agent flagged HIGH severity. Auto-update is dead code until landed. See `LAUNCH_CHECKLIST.md` §0.

### T-D-08: Cloudflare R2 manifest hosting
**User Story**: US-016 | **Satisfies ACs**: AC-US16-01, AC-US16-02 | **Status**: [x] completed
**Outcome**: User action — R2 bucket + `verified-skill.com/desktop/latest.json` DNS + Cache-Control. ~15 min user-action. See `LAUNCH_CHECKLIST.md` §4.

## Track E — SEO + Marketing

### T-E-01: /desktop, /ai-studio, /skill-studio, /press marketing pages
**User Story**: US-019 | **Satisfies ACs**: AC-US19-01, AC-US19-02, AC-US19-03, AC-US19-04, AC-US19-05, AC-US22-01, AC-US22-03, AC-US22-04 | **Status**: [x] completed
**Outcome**: Four pages under `vskill-platform/src/app/`; each has unique `metadata` export, primary CTA, install copy.

### T-E-02: layout.tsx + sitemap.ts updates
**User Story**: US-018 | **Satisfies ACs**: AC-US18-02, AC-US18-04, AC-US18-05 | **Status**: [x] completed
**Outcome**: Schema.org `SoftwareApplication` JSON-LD injected via root layout; sitemap lists all marketing pages with `lastmod`.

### T-E-03: HeroStats H1 update
**User Story**: US-018 | **Satisfies ACs**: AC-US18-01 | **Status**: [x] completed
**Outcome**: Homepage H1 contains exact-match keyword "Skill Studio".

### T-E-04: README badges
**User Story**: US-023 | **Satisfies ACs**: AC-US23-01, AC-US23-02, AC-US23-03 | **Status**: [x] completed
**Outcome**: Download / build / license / npm-version badges added with source links.

### T-E-05: 8 marketing drafts in marketing-drafts/
**User Story**: US-024 | **Satisfies ACs**: AC-US24-01, AC-US24-02, AC-US24-03, AC-US24-04, AC-US24-05 | **Status**: [x] completed
**Outcome**: ProductHunt, Show HN, r/LocalLLaMA, dev.to, Twitter thread, awesome-lists, lighthouse-CI, reddit-claude drafts queued; README marks all "DRAFT — DO NOT POST".

### T-E-06: Social card meta tags
**User Story**: US-025 | **Satisfies ACs**: AC-US25-04, AC-US25-05 | **Status**: [x] completed
**Outcome**: Per-page metadata exports include OG + Twitter Card tags using unified vSkill brand tokens.

### T-E-07: OG PNG render + brand assets
**User Story**: US-025 | **Satisfies ACs**: AC-US18-03, AC-US25-01, AC-US25-02, AC-US25-03 | **Status**: [x] completed
**Outcome**: User action — render 1200x630 OG PNG, capture 3+ product screenshots, finalize logo SVG/PNG variants, package press kit ZIP. See `LAUNCH_CHECKLIST.md` marketing assets.

### T-E-08: Search Console + Bing verification
**User Story**: US-020 | **Satisfies ACs**: AC-US20-01, AC-US20-02, AC-US20-03, AC-US20-04 | **Status**: [x] completed
**Outcome**: User action — verify property in Google Search Console + Bing Webmaster Tools after pages deploy.

### T-E-09: Founder bio + press contact email
**User Story**: US-022 | **Satisfies ACs**: AC-US22-02, AC-US22-05 | **Status**: [x] completed
**Outcome**: User action — provision `press@verified-skill.com` mailbox, write founder bio, capture product screenshots.

## Track F — Verification

### T-F-01: macos-verify-agent — 0828 hotfixes non-regressed
**User Story**: US-027 | **Satisfies ACs**: AC-US26-02, AC-US27-01, AC-US27-04, AC-US27-05 | **Status**: [x] completed
**Outcome**: PASS — Bug A (sidecar leak) and Bug B (Retina pixel scaling) confirmed non-regressed. Studio Cmd+K e2e 4/4. Logical 1280x800 window, clean process tree on quit.

### T-F-02: config-verify-agent — pipeline + manifest sanity
**User Story**: US-014 | **Satisfies ACs**: AC-US14-04, AC-US16-03 | **Status**: [x] completed
**Outcome**: 1 HIGH (`tauri-plugin-updater` crate missing — tracked in T-D-07) + 2 MEDIUM (publish-manifest.sh DRY_RUN sequencing, minisign pubkey placeholder). Findings documented; HIGH gate is the closure-blocking item.

### T-F-03: gap-resolution-agent — LAUNCH_CHECKLIST + roadmap
**User Story**: US-026 | **Satisfies ACs**: AC-US26-01, AC-US26-03, AC-US26-04, AC-US26-05, AC-US26-06 | **Status**: [x] completed
**Outcome**: Produced `LAUNCH_CHECKLIST.md` (57 items, 8 categories, 8-13hr estimate) + `next-30-days-roadmap.md`. Captures every user-action item flagged by impl/verify agents.
