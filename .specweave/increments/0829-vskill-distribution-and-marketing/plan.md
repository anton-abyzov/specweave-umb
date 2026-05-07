# 0829-vskill-distribution-and-marketing — Plan (Architecture)

**Owner**: Architect agent
**Companion**: spec.md (PM-owned, finalized 2026-05-07, 29 user stories US-01..US-29, ACs AC-US01-01..AC-US29-04)
**Decision authority**: this document on HOW; spec.md on WHAT
**Parent increment**: 0828-vskill-desktop-app (Phase 1 macOS skeleton — assumed delivered)
**Related ADRs**:
- [0828-01 vskill Desktop Framework Choice](../../docs/internal/architecture/adr/0828-01-vskill-desktop-framework-choice.md) (Tauri 2 selection)
- [0829-01 Auto-Update Manifest Hosting and Signing](../../docs/internal/architecture/adr/0829-01-update-manifest-hosting.md) (R2 + minisign)
- [0829-02 Linux Package Format Strategy](../../docs/internal/architecture/adr/0829-02-linux-package-formats.md) (deb/rpm/AppImage)
**Spec.md AC cross-ref summary**:
- Track A (macOS) → US-01 cert/notarize, US-02 dmg/install, US-03 gatekeeper, US-04 brew Cask
- Track B (Windows) → US-05 msi/install, US-06 SmartScreen UX, US-07 deep-link registry, US-08 WebView2 bootstrap
- Track C (Linux) → US-09 deb, US-10 rpm, US-11 AppImage, US-12 GPG sig
- Track D (Updater + Releases) → US-13 release pipeline, US-14 updater client, US-15 update UX, US-16 manifest hosting, US-17 changelog automation
- Track E (SEO + Marketing) → US-18 SEO baseline, US-19 landing pages, US-20 search-console, US-21 Lighthouse, US-22 press kit, US-23 README badges, US-24 launch drafts, US-25 social cards
- Track F (Verification) → US-26 release verify CI, US-27 Cmd/Ctrl-K parity, US-28 update flow E2E, US-29 SEO post-deploy verify

---

## 1. Executive Summary

0828 delivered an unsigned local Tauri shell. 0829 makes it **shippable, distributable, discoverable, and verifiable** — across macOS / Windows / Linux — with auto-update on every platform, SEO foundations on verified-skill.com to drive organic discovery, and a marketing-asset draft pack ready for launch day.

**Architecture in one sentence**: One GitHub Actions workflow (`desktop-release.yml`) builds, signs, and publishes per-OS artifacts on every `desktop-v*` tag; a Cloudflare R2 bucket fronted by `verified-skill.com/desktop/*` hosts the binaries and a minisign-signed `latest.json` manifest that the Tauri Updater plugin polls daily; verified-skill.com gains a `/desktop` landing page + structured data + press kit; a verification team installs and smoke-tests every signed artifact post-release.

**Six tracks (parallelizable after Phase 1 cert/bundle ID gate)**:

- **Track A — macOS**: Developer ID cert, hardened runtime + entitlements, notarytool/staple, universal `.dmg` with custom layout, Homebrew Cask staging tap.
- **Track B — Windows**: WiX MSI with embedded WebView2 bootstrapper, `vskill://` registry, unsigned-but-documented for v1, README "Run anyway" guidance.
- **Track C — Linux**: `.deb` + `.rpm` + `.AppImage` from one `cargo tauri build` on `ubuntu-22.04`, GPG-signed artifacts + SHA256SUMS.
- **Track D — Auto-updater + Releases**: Tauri Updater + minisign + R2-hosted `latest.json`, single matrixed `desktop-release.yml` workflow, three-version rollback path, conventional-commits CHANGELOG.
- **Track E — SEO + Landing**: `/desktop` and `/ai-studio` and `/skill-studio` landing pages on verified-skill.com with OS-detection download CTAs, schema.org `SoftwareApplication` JSON-LD, OG/Twitter cards, Lighthouse CI gate, press kit at `/press`, README badge refresh.
- **Track F — Verification**: Three platform-test agents (mac/win/linux) run on real GitHub runners post-release; one SEO verifier runs Lighthouse + Google indexing checks.

The 0828 architectural foundation (sidecar process tree, deep-link contract, lifecycle, IPC commands) is **frozen** for 0829 — no redesign, only delivery scaffolding around it.

---

## 2. Inherited Context (from 0828)

The architect read 0828's plan.md fully before drafting this. Key invariants that 0829 implementation MUST preserve:

| Invariant | Source | 0829 implication |
|---|---|---|
| Process tree: Tauri Rust + WKWebView/WebView2 + Node sidecar (`dist/eval-server/`) | 0828 plan §3.1 | All three OS bundles include the same three components; only OS-specific Node binary changes per arch. |
| `dist/eval-ui/` is the source of truth for the WebView surface | 0828 plan §10 | No 0829 frontend changes to the Tauri-rendered UI — only verified-skill.com (vskill-platform) for SEO. |
| `~/.vskill/workspace.json` schema | 0828 plan §10 | Untouched. |
| `boot-preflight.ts` MUST be the first import in eval-server.ts | 0828 plan §10 | Untouched. |
| Cmd-W hides window, Cmd-Q full shutdown via `/api/shutdown` | 0828 plan §3.2 | Verified by Track F agents — regression gate. |
| Updater public key embedded in `tauri.conf.json` | 0828 plan §2.6 | 0829 generates the keypair (this is "Phase 1 cert + key gen" gate before any release CI). |
| 0828 `tauri.conf.json` already has `bundle.targets: ["app", "dmg"]` and `bundle.windows.webviewInstallMode: embedBootstrapper` | `repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json` | 0829 extends with macOS signing identity + entitlements + Linux `deb`/`rpm`/`appimage` bundle config + updater plugin. |
| Bundle ID `com.verifiedskill.desktop`, identifier already set | same | Used as App ID for cert request. |
| ASC profile `vskill` already authenticated; team a9be87c1-47d8-40f2-897d-75df80a540fb; key JZ2ML9M66A in keychain | metadata.json | 0829 Phase 1 calls `asc certificates create` from this profile. |

---

## 3. Pre-Phase 1 Gate — Cert + Bundle ID + Updater Keypair

**Why a separate gate**: every track downstream consumes secrets that don't exist yet. This is a one-shot synchronous step gated on Anton (or architect) running ASC commands. ~15 min if no surprises.

### 3.1 Apple Developer ID Application certificate

```bash
# From any shell with the asc profile already authed (per metadata.json)
asc certificates create \
  --type DEVELOPER_ID_APPLICATION \
  --profile vskill \
  --output ~/.certs/vskill-developer-id.cer

# Convert .cer → .p12 (requires the CSR-side private key, ASC handles via keychain)
# Outputs: ~/.certs/vskill-developer-id.p12 + password
asc certificates export \
  --certificate-id <id-from-create-output> \
  --profile vskill \
  --format p12 \
  --output ~/.certs/vskill-developer-id.p12 \
  --password-to-stdout > ~/.certs/vskill-developer-id.p12.password
```

Once created:
- Verify via `security find-identity -v -p codesigning` — should list `Developer ID Application: EasyChamp, Inc. (a9be87c1-47d8-40f2-897d-75df80a540fb)`.
- Base64-encode `.p12` for GH Actions: `base64 -i ~/.certs/vskill-developer-id.p12 | pbcopy`.

### 3.2 Bundle ID registration

```bash
asc bundle-ids create \
  --identifier com.verifiedskill.desktop \
  --name "Skill Studio" \
  --platform MACOS \
  --profile vskill
```

Already in `tauri.conf.json` as `identifier`. Registration is the missing piece.

### 3.3 Tauri Updater minisign keypair

```bash
# Local (architect or Anton)
mkdir -p ~/.tauri
tauri signer generate -w ~/.tauri/vskill-updater.key
# Outputs:
#   private: ~/.tauri/vskill-updater.key   (passphrase-protected)
#   public:  printed to stdout — paste into tauri.conf.json
```

- **Public key** → committed to `src-tauri/tauri.conf.json.plugins.updater.pubkey` (safe).
- **Private key + passphrase** → 1Password Family vault (item: "vskill Tauri Updater") + GH Actions secrets `TAURI_SIGNING_PRIVATE_KEY` (file content) + `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`.

### 3.4 GPG key for Linux artifacts (per ADR 0829-02)

```bash
gpg --batch --quick-gen-key 'vSkill Releases <releases@verified-skill.com>' ed25519 sign 0
# Capture fingerprint
gpg --list-secret-keys --with-colons | grep '^fpr' | head -1 | cut -d':' -f10
```

- **Public fingerprint** → committed to `docs/RELEASING-DESKTOP.md` and rendered on `/security` page.
- **Private key** → 1Password vault + GH Actions secret `GPG_PRIVATE_KEY` (base64 of ASCII-armored secret).

### 3.5 Cloudflare R2 bucket setup

```bash
wrangler r2 bucket create vskill-desktop --location-hint us-east-1
# Attach custom domain via Cloudflare dashboard:
#   R2 → vskill-desktop → Settings → Custom Domains → Add
#   Hostname: verified-skill.com (subpath /desktop/* via Worker route, see Track D §6.4)
```

Generate R2 access keys with read+write scope to `vskill-desktop` only:
```bash
wrangler r2 api-token create "vskill-desktop-publisher" \
  --permission "Object Read & Write" \
  --bucket vskill-desktop
```

→ GH Actions secrets `CLOUDFLARE_R2_ACCOUNT_ID`, `CLOUDFLARE_R2_ACCESS_KEY_ID`, `CLOUDFLARE_R2_SECRET_ACCESS_KEY`.

### 3.6 Gate output

After 3.1–3.5 complete:
```
✅ Developer ID Application cert in keychain + base64 in GH secret APPLE_CERTIFICATE
✅ Bundle ID com.verifiedskill.desktop registered with ASC
✅ tauri.conf.json.plugins.updater.pubkey populated
✅ TAURI_SIGNING_PRIVATE_KEY + _PASSWORD in GH Actions secrets
✅ GPG key generated + fingerprint published + GPG_* secrets set
✅ R2 bucket vskill-desktop exists + custom domain attached + CLOUDFLARE_R2_* secrets set
```

Tracks A, B, C, D, E, F can now run in parallel.

---

## 4. Track A — macOS Distribution

**Owner sub-agent**: `desktop-release-mac-agent`
**Spec ACs**: AC-US01-01..05 (cert + notarize), AC-US02-01..05 (universal `.dmg` + first-launch matrix), AC-US03-01..04 (Gatekeeper + hardened runtime + stapled), AC-US04-01..05 (Homebrew Cask staging + uninstall).

### 4.1 `tauri.conf.json` changes

```jsonc
"bundle": {
  "macOS": {
    "minimumSystemVersion": "13.0",
    "signingIdentity": "Developer ID Application: EasyChamp, Inc. (a9be87c1-47d8-40f2-897d-75df80a540fb)",
    "entitlements": "Entitlements.plist",
    "providerShortName": null,
    "exceptionDomain": "",
    "frameworks": [],
    "dmg": {
      "background": "../assets/dmg-background.png",
      "windowSize": { "width": 660, "height": 400 },
      "appPosition": { "x": 180, "y": 170 },
      "applicationFolderPosition": { "x": 480, "y": 170 }
    }
  }
}
```

### 4.2 `src-tauri/Entitlements.plist` (NEW file)

Hardened runtime ON. Minimal entitlements — only what the Node sidecar requires:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <!-- WKWebView WebAssembly + JIT support -->
  <key>com.apple.security.cs.allow-jit</key>
  <true/>
  <!-- Node's V8 generates writable+executable pages; required for sidecar -->
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
  <true/>
  <!-- Node's native modules (@napi-rs/keyring, etc.) load dylibs at runtime -->
  <key>com.apple.security.cs.disable-library-validation</key>
  <true/>
  <!-- Network client (HTTP to localhost + verified-skill.com) -->
  <key>com.apple.security.network.client</key>
  <true/>
  <!-- Read user-selected files (NSOpenPanel project picker from 0828) -->
  <key>com.apple.security.files.user-selected.read-write</key>
  <true/>
</dict>
</plist>
```

**Explicitly NOT enabled**:
- `com.apple.security.app-sandbox` — would break the Node sidecar child process and `~/.vskill/` access. We are Developer ID distribution, not Mac App Store, so sandbox is optional.
- `com.apple.security.cs.allow-dyld-environment-variables` — not needed; eval-server's `boot-preflight.ts` reads env from `~/.vskill/keys.env` directly.

**`disable-library-validation` justification (per spec NFR-22 — architect-required justification)**:
The Node sidecar uses `@napi-rs/keyring` (native module, dlopen-loaded `.dylib`s into Node's process at runtime) and Node itself dlopens its own internal modules signed with the Node project's signing identity, NOT ours. Without `disable-library-validation`, the Node binary would refuse to load these libraries because their signatures don't match `Developer ID Application: EasyChamp, Inc.`. This is a fundamental constraint of using Node-as-sidecar — Tauri's [Node sidecar guide](https://v2.tauri.app/learn/sidecar-nodejs/) explicitly documents this entitlement requirement.

Mitigation: the Node binary itself is bundled and signed by us (re-signed during `tauri-action`'s codesign step), and our `boot-preflight.ts` boot order means no third-party module loads before our supervisor confirms the binary's expected hash. This is the same posture Electron apps adopt and is accepted Apple Developer ID practice. **Recorded in ADR 0828-01 §"Why not the alternatives"** for permanence; this plan's entitlement decision merely implements that ADR.

### 4.3 Notarization flow

`tauri-action@v0` handles signing + notarization in one step. Workflow snippet (full file in §7):

```yaml
- uses: tauri-apps/tauri-action@v0
  env:
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
    APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
    APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
    APPLE_SIGNING_IDENTITY: "Developer ID Application: EasyChamp, Inc. (a9be87c1-47d8-40f2-897d-75df80a540fb)"
    TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
    TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
  with:
    args: --target ${{ matrix.target }} --bundles app,dmg
    tagName: ${{ github.ref_name }}
    releaseName: 'Skill Studio ${{ github.ref_name }}'
    releaseDraft: true
    prerelease: false
```

Notarytool retry strategy: `tauri-action` calls `xcrun notarytool submit --wait --keychain-profile ...` internally. If submission stalls (Feb 2026 outage precedent — see [Apple developer forums notarization topic](https://developer.apple.com/forums/topics/code-signing-topic/code-signing-topic-notarization)), our workflow retries up to 3 times with a 10-minute backoff before failing the release. Custom retry wrapper:

```yaml
- name: Notarize with retry
  run: |
    for attempt in 1 2 3; do
      if tauri-action ... ; then break; fi
      echo "Notarization attempt $attempt failed; sleeping 600s before retry"
      sleep 600
    done
```

Verification gate (every release, blocking):

```bash
codesign --verify --deep --strict --verbose=4 vSkill.app
spctl -a -t exec -vv vSkill.app   # MUST output "accepted, source=Notarized Developer ID"
```

### 4.4 Universal `.dmg` — REVISED to match spec AC-US02-01

Spec.md AC-US02-01 explicitly requires a **universal2 binary** (`vskill-${VERSION}-universal.dmg` containing both archs, verified via `lipo -info`). Architect's earlier per-arch preference is overridden by the spec contract.

Implementation:
- Build target: `universal-apple-darwin` (Tauri's "lipo" mode — produces a single `.app` with both archs merged).
- Runner: `macos-14` (Apple Silicon) — `tauri-action` cross-compiles x86_64 portion via Xcode SDK + `lipo` merge in one step.
- Bundle output: single `vskill-${VERSION}-universal.dmg` (no `_aarch64` / `_x86_64` suffixed dmgs in v1).
- Bundle size: targeting ≤80 MB compressed per spec NFR-Size (verified in §6).

Architect's prior per-arch suggestion is documented here as **Plan B** in case bundle size breaches NFR — fallback ships per-arch dmgs at ~45 MB each, OS detection on the `/desktop` page selects the right one.

Homebrew Cask `Casks/vskill.rb` uses a single `url` (no per-arch variants) since the dmg is universal.

### 4.5 `.dmg` background image

Generated from a Remotion still — keeps brand parity per `project_video_brand_decisions_2026_04`. 660×400 PNG, subtle Studio gradient, "Drag vSkill to Applications →" arrow. Asset path: `repositories/anton-abyzov/vskill/assets/dmg-background.png` (NEW). Template source: `repositories/anton-abyzov/vskill/scripts/release/render-dmg-background.ts` (Remotion CLI invocation).

### 4.6 Homebrew Cask — staging tap

Per 0828 plan §5.4 (already approved in 0828): first 2-3 releases ship to `antonabyzov/homebrew-vskill-staging` (tap repo). Mainline `homebrew/cask` PR opens after 30+ days zero-crash + 98% install-success.

`Casks/vskill.rb` (single url, universal dmg per AC-US02-01):

```ruby
cask "vskill" do
  version "1.0.0"
  sha256 "<sha256 of universal dmg>"

  url "https://verified-skill.com/desktop/v#{version}/vskill-#{version}-universal.dmg"
  name "vSkill"
  desc "Verified AI skill marketplace and studio (desktop)"
  homepage "https://verified-skill.com"

  auto_updates true
  depends_on macos: ">= :ventura"

  app "vSkill.app"

  zap trash: [
    "~/.vskill",
    "~/Library/Logs/vSkill",
    "~/Library/Caches/com.verifiedskill.desktop",
    "~/Library/Preferences/com.verifiedskill.desktop.plist",
  ]
end
```

Cask hosted in **`verified-skill/homebrew-tap-staging`** tap (per AC-US04-01 — staging tap; mainline `homebrew/cask` after AC-US04-04 promotion criteria met: 100 successful installs OR 7 days clean).

CI step using [`macauley/action-homebrew-bump-cask@v1`](https://github.com/marketplace/actions/homebrew-bump-cask):

```yaml
- uses: macauley/action-homebrew-bump-cask@v1
  with:
    token: ${{ secrets.HOMEBREW_BUMP_PAT }}     # PAT, not GITHUB_TOKEN — Homebrew rule
    tap: verified-skill/homebrew-tap-staging
    cask: vskill
    tag: ${{ github.ref_name }}
    revision: ${{ github.sha }}
    livecheck: true
```

Mainline submission (manual, post-staging period):
```bash
brew bump-cask-pr --version 1.0.0 vskill
```

### 4.7 Track A deliverables

- [ ] T-A-01: `Entitlements.plist` created at `src-tauri/Entitlements.plist` — covers AC-US03-03
- [ ] T-A-02: `tauri.conf.json` updated with macOS signing identity + entitlements + dmg layout — covers AC-US01-03
- [ ] T-A-03: `assets/dmg-background.png` rendered + committed (or generated in CI) — visual portion of AC-US02-02
- [ ] T-A-04: GitHub Actions job `desktop-release-mac` (target: universal-apple-darwin) — covers AC-US01-04, AC-US02-01, AC-US13-03
- [ ] T-A-05: Notarization retry wrapper + `spctl` verification gate — covers AC-US01-04, AC-US01-05, AC-US03-01, AC-US03-04
- [ ] T-A-06: `Casks/vskill.rb` template + `verified-skill/homebrew-tap-staging` tap repo created — covers AC-US04-01, AC-US04-03
- [ ] T-A-07: Cask bump CI step on every release tag — covers AC-US04-02
- [ ] T-A-08: `Casks/vskill.rb` zap stanza removes ~/.vskill, ~/Library/Logs/vSkill, prefs — covers AC-US04-05
- [ ] T-A-09: `docs/RELEASING-DESKTOP.md` macOS section with cert rotation runbook + notarization timeout playbook
- [ ] T-A-10: First-launch matrix test on macOS 13/14/15 (`spctl` + `codesign --verify` runs on each) — covers AC-US02-03..05

---

## 5. Track B — Windows Distribution

**Owner sub-agent**: `desktop-release-win-agent`
**Spec ACs**: AC-US05-01..05 (.msi build + install + Start Menu + uninstall), AC-US06-01..04 (SmartScreen UX + SHA256), AC-US07-01..03 (`vskill://` registry), AC-US08-01..03 (WebView2 bootstrapper).

### 5.1 `tauri.conf.json` Windows config

```jsonc
"bundle": {
  "windows": {
    "wix": {
      "language": "en-US",
      "template": null,
      "componentRefs": [],
      "componentGroupRefs": [],
      "featureGroupRefs": [],
      "featureRefs": [],
      "mergeRefs": []
    },
    "nsis": null,
    "webviewInstallMode": {
      "type": "embedBootstrapper",
      "silent": false
    }
  }
}
```

`embedBootstrapper` adds ~1.8 MB to the .msi (already accepted in 0828 plan §5.5). Trade vs `offlineInstaller`: +127 MB but no internet on first run. Default acceptable for our user base (developers with internet). Bumps to `offlineInstaller` only if support requests pile up.

### 5.2 `vskill://` registry registration

Tauri's [`tauri-plugin-deep-link`](https://v2.tauri.app/plugin/deep-linking/) handles Windows registry writes during install. Verified by inspection of 0828's Cargo.toml — `tauri-plugin-deep-link = "2"` is already present. WiX template additions:

```xml
<RegistryKey Root="HKCU" Key="Software\Classes\vskill" Action="createAndRemoveOnUninstall">
  <RegistryValue Type="string" Value="URL:vSkill Protocol" />
  <RegistryValue Name="URL Protocol" Type="string" Value="" />
  <RegistryKey Key="shell\open\command">
    <RegistryValue Type="string" Value="&quot;[INSTALLDIR]vSkill.exe&quot; &quot;%1&quot;" />
  </RegistryKey>
</RegistryKey>
```

This is auto-generated by the deep-link plugin when `plugins.deep-link.desktop.schemes: ["vskill"]` is set (already set in current 0828 config). No custom WiX work required.

### 5.3 Unsigned strategy + SmartScreen UX

Per user direction (0829 metadata): **no paid Windows OV cert in v1.** Result: SmartScreen shows "Windows protected your PC" for first-time downloads.

Three mitigations:

1. **Documented "Run anyway" UX path** in README + `/desktop` landing page:
   - Right-click `.msi` → Properties → check "Unblock" → OK → double-click.
   - Or: SmartScreen dialog → "More info" → "Run anyway".
2. **SHA256 + GPG sig published** alongside the unsigned `.msi` (same GPG key as Linux, per ADR 0829-02). README documents how to verify.
3. **Reputation accrual via volume** — SmartScreen reputation accrues per binary signature OR file hash even without a cert. After ~1k clean downloads on the same hash, the warning typically diminishes. Documented in `docs/RELEASING-DESKTOP.md`.

### 5.4 winget — deferred

Per user direction, winget submission is **out of v1**. The `microsoft/winget-pkgs` PR template requires a signed installer for high-trust manifests; we'd be in the lower trust pool unsigned. Defer until either (a) we buy an OV cert, or (b) reputation is established and we submit anyway.

### 5.5 Track B deliverables

- [ ] T-B-01: `tauri.conf.json` Windows config validated (already mostly there from 0828 — only add WiX `language` field) — covers AC-US05-01
- [ ] T-B-02: GitHub Actions job `desktop-release-win` on `windows-2022` runner — see §7 — covers AC-US05-01, AC-US13-04
- [ ] T-B-03: SHA256 of `.msi` published in GitHub Release notes — covers AC-US06-04
- [ ] T-B-04: README "Installing on Windows" section with SmartScreen "Run anyway" walkthrough + SHA256 verification — covers AC-US06-01..04
- [ ] T-B-05: `/desktop` landing page Windows download card with SmartScreen callout + screenshot — covers AC-US06-01, AC-US06-02
- [ ] T-B-06: WiX template `RegistryKey HKCR\vskill` for URL protocol (auto-generated by `tauri-plugin-deep-link`) — covers AC-US07-01..03
- [ ] T-B-07: WebView2 evergreen bootstrapper bundled via `webviewInstallMode: embedBootstrapper` — covers AC-US08-01..03
- [ ] T-B-08: WiX install creates Start Menu entry "vSkill" + optional Desktop shortcut — covers AC-US05-04
- [ ] T-B-09: Uninstall via Settings → Apps removes binaries + registry keys + shortcuts — covers AC-US05-05, AC-US07-03
- [ ] T-B-10: Install timing test on Win 11 23H2 + Win 10 22H2 VMs — covers AC-US05-02, AC-US05-03

---

## 6. Track C — Linux Distribution

**Owner sub-agent**: `desktop-release-linux-agent`
**Spec ACs**: AC-US09-01..05 (.deb), AC-US10-01..05 (.rpm), AC-US11-01..04 (.AppImage), AC-US12-01..05 (GPG + SHA256SUMS).

Per [ADR 0829-02](../../docs/internal/architecture/adr/0829-02-linux-package-formats.md) — full design lives there; this section is the build/CI surface only.

### 6.1 `tauri.conf.json` Linux config

```jsonc
"bundle": {
  "targets": ["app", "dmg", "deb", "rpm", "appimage"],
  "linux": {
    "deb": {
      "depends": [
        "libwebkit2gtk-4.1-0",
        "libgtk-3-0",
        "libayatana-appindicator3-1"
      ]
    },
    "rpm": {
      "depends": [
        "webkit2gtk4.1",
        "gtk3",
        "libappindicator-gtk3"
      ]
    },
    "appimage": {
      "bundleMediaFramework": false
    }
  }
}
```

### 6.2 CI build deps (ubuntu-22.04)

```yaml
- name: Install Linux build dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      libwebkit2gtk-4.1-dev \
      libsoup-3.0-dev \
      libjavascriptcoregtk-4.1-dev \
      build-essential curl wget file \
      libxdo-dev libssl-dev \
      libayatana-appindicator3-dev \
      librsvg2-dev libgtk-3-dev \
      rpm
```

(Note `rpm` package — needed for Tauri's RPM bundler on Ubuntu hosts.)

### 6.3 GPG sign all three artifacts

```yaml
- name: GPG sign artifacts
  env:
    GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
    GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
    GPG_KEY_ID: ${{ secrets.GPG_KEY_ID }}
  run: |
    echo "$GPG_PRIVATE_KEY" | base64 -d | gpg --batch --import
    cd src-tauri/target/release/bundle
    for f in deb/*.deb rpm/*.rpm appimage/*.AppImage; do
      echo "$GPG_PASSPHRASE" | gpg --batch --yes --pinentry-mode loopback \
        --passphrase-fd 0 --local-user "$GPG_KEY_ID" \
        --detach-sign --armor "$f"
    done
    sha256sum deb/*.deb rpm/*.rpm appimage/*.AppImage > SHA256SUMS
    echo "$GPG_PASSPHRASE" | gpg --batch --yes --pinentry-mode loopback \
      --passphrase-fd 0 --local-user "$GPG_KEY_ID" \
      --detach-sign --armor SHA256SUMS
```

### 6.4 Track C deliverables

- [ ] T-C-01: `tauri.conf.json` Linux bundle config (deb/rpm/appimage with deps) — covers AC-US09-04, AC-US10-04
- [ ] T-C-02: GitHub Actions job `desktop-release-linux` on `ubuntu-22.04` runner — see §7 — covers AC-US09-01, AC-US10-01, AC-US11-01, AC-US13-05
- [ ] T-C-03: GPG sign step + SHA256SUMS aggregate (`SHA256SUMS` + `SHA256SUMS.asc` in every Release) — covers AC-US12-01, AC-US12-02
- [ ] T-C-04: GPG public key published at `verified-skill.com/.well-known/pgp-key.asc` + uploaded to keys.openpgp.org — covers AC-US12-03
- [ ] T-C-05: GPG private key in 1Password + GH Actions secret only (never repo) — covers AC-US12-05
- [ ] T-C-06: `/desktop` page documents `gpg --verify SHA256SUMS.asc SHA256SUMS && sha256sum -c SHA256SUMS` — covers AC-US12-04
- [ ] T-C-07: AppImage size budget assertion `[ $(stat -c%s vskill-*.AppImage) -le 94371840 ]` (≤90 MB per AC-US11-04)
- [ ] T-C-08: AppImage FUSE requirement documented on `/desktop` Linux card — covers AC-US11-03
- [ ] T-C-09: Verify on Ubuntu 22.04 + 24.04 + Debian 12 (`.deb`), Fedora 40+41 + RHEL 9 (`.rpm`), Ubuntu 22.04 + Fedora 40 + openSUSE Tumbleweed (`.AppImage`) — Track F covers, AC-US09-02..03, AC-US10-02..03, AC-US11-02
- [ ] T-C-10: `apt remove` / `dnf remove` clean uninstall verified — covers AC-US09-05, AC-US10-05

---

## 7. Track D — Auto-Updater + GitHub Releases

**Owner sub-agent**: `desktop-release-orchestrator-agent` (also responsible for Track A/B/C workflow assembly)
**Spec ACs**: AC-US13-01..06 (release pipeline matrix + ≤25min wall-clock), AC-US14-01..05 (Tauri Updater client + minisign verify), AC-US15-01..05 (update notification UX + retry + cleanup), AC-US16-01..05 (manifest hosting + cache + staging), AC-US17-01..05 (changelog automation + diff link).

Per [ADR 0829-01](../../docs/internal/architecture/adr/0829-01-update-manifest-hosting.md) — full design lives there; this section is the workflow + manifest publisher.

### 7.1 `tauri.conf.json` updater config

```jsonc
"plugins": {
  "deep-link": { "desktop": { "schemes": ["vskill"] } },
  "updater": {
    "active": true,
    "endpoints": [
      "https://verified-skill.com/desktop/latest.json"
    ],
    "dialog": false,
    "pubkey": "<paste public key from §3.3 here>",
    "allowDowngrades": true
  }
}
```

`dialog: false` because the in-app banner UX (0828 plan §3.7) is custom-rendered by the studio bundle, not the default OS modal.

### 7.2 GitHub Actions — `desktop-release.yml`

Single workflow, three matrix jobs (mac/win/linux) + a final `publish-manifest` job that depends on all three.

Skeleton (full file generated by implementer in T-D-02):

```yaml
name: Desktop Release

on:
  push:
    tags:
      - 'desktop-v*'

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - { os: macos-14, target: aarch64-apple-darwin,    platform: darwin-aarch64 }
          - { os: macos-13, target: x86_64-apple-darwin,     platform: darwin-x86_64  }
          - { os: windows-2022, target: x86_64-pc-windows-msvc, platform: windows-x86_64 }
          - { os: ubuntu-22.04, target: x86_64-unknown-linux-gnu, platform: linux-x86_64 }
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - uses: dtolnay/rust-toolchain@stable
        with: { targets: ${{ matrix.target }} }

      - name: Install Linux build deps
        if: startsWith(matrix.os, 'ubuntu')
        run: |
          sudo apt-get update && sudo apt-get install -y \
            libwebkit2gtk-4.1-dev libsoup-3.0-dev libjavascriptcoregtk-4.1-dev \
            build-essential curl wget file libxdo-dev libssl-dev \
            libayatana-appindicator3-dev librsvg2-dev libgtk-3-dev rpm

      - name: Build studio bundle + sidecar
        run: |
          npm ci
          npm run build
          npm run build:eval-ui
          npm run desktop:sidecar:build

      - name: Build + sign + (mac) notarize
        uses: tauri-apps/tauri-action@v0
        env:
          # macOS
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          # Tauri updater (all platforms)
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
        with:
          args: --target ${{ matrix.target }}
          tagName: ${{ github.ref_name }}
          releaseName: 'Skill Studio ${{ github.ref_name }}'
          releaseDraft: true
          prerelease: false

      - name: Verify signing (macOS)
        if: startsWith(matrix.os, 'macos')
        run: |
          DMG=$(ls src-tauri/target/${{ matrix.target }}/release/bundle/dmg/*.dmg)
          spctl -a -t open -vv --context context:primary-signature "$DMG"

      - name: GPG sign (Linux)
        if: startsWith(matrix.os, 'ubuntu')
        env:
          GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
          GPG_KEY_ID: ${{ secrets.GPG_KEY_ID }}
        run: bash scripts/release/gpg-sign-linux.sh

      - name: GPG sign (Windows .msi)
        if: startsWith(matrix.os, 'windows')
        run: bash scripts/release/gpg-sign-windows.sh
        env:
          GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
          GPG_KEY_ID: ${{ secrets.GPG_KEY_ID }}

      - name: Upload to R2
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.CLOUDFLARE_R2_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.CLOUDFLARE_R2_SECRET_ACCESS_KEY }}
          R2_ENDPOINT: https://${{ secrets.CLOUDFLARE_R2_ACCOUNT_ID }}.r2.cloudflarestorage.com
        run: bash scripts/release/upload-r2.sh ${{ matrix.platform }} ${{ github.ref_name }}

      - name: Emit platform manifest fragment
        run: bash scripts/release/emit-platform-fragment.sh ${{ matrix.platform }} ${{ github.ref_name }} > platform-${{ matrix.platform }}.json
      - uses: actions/upload-artifact@v4
        with:
          name: manifest-fragment-${{ matrix.platform }}
          path: platform-${{ matrix.platform }}.json

  publish-manifest:
    needs: build
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { pattern: manifest-fragment-* }
      - name: Assemble latest.json
        run: bash scripts/release/assemble-manifest.sh ${{ github.ref_name }} > latest.json
      - name: Upload manifest atomically
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.CLOUDFLARE_R2_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.CLOUDFLARE_R2_SECRET_ACCESS_KEY }}
          R2_ENDPOINT: https://${{ secrets.CLOUDFLARE_R2_ACCOUNT_ID }}.r2.cloudflarestorage.com
        run: bash scripts/release/publish-manifest.sh ${{ github.ref_name }}
      - name: Promote draft Release → published
        run: gh release edit ${{ github.ref_name }} --draft=false
        env: { GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} }

  bump-cask:
    needs: publish-manifest
    runs-on: macos-14
    steps:
      - uses: macauley/action-homebrew-bump-cask@v1
        with:
          token: ${{ secrets.HOMEBREW_BUMP_PAT }}
          tap: antonabyzov/homebrew-vskill-staging
          cask: vskill
          tag: ${{ github.ref_name }}
          revision: ${{ github.sha }}
          livecheck: true
```

### 7.3 Manifest publisher scripts

Five new shell scripts under `scripts/release/`:

| Script | Purpose |
|---|---|
| `gpg-sign-linux.sh` | Detached-armored sign each `.deb`/`.rpm`/`.AppImage` + SHA256SUMS. |
| `gpg-sign-windows.sh` | Detached-armored sign `.msi`. |
| `upload-r2.sh <platform> <version>` | `aws s3 cp` (S3 API → R2 endpoint) bundle + sig to `s3://vskill-desktop/desktop/v<version>/`. |
| `emit-platform-fragment.sh <platform> <version>` | Output single-platform JSON: `{ platform: { signature, url } }` with minisign sig from `tauri-action`'s `*.tar.gz.sig` output. |
| `assemble-manifest.sh <version>` | Merge fragments + version + pub_date + notes from `git tag -n9` → `latest.json`. |
| `publish-manifest.sh <version>` | Atomic publish: upload `v<version>/latest.json`, then `cp` to `latest.json` and `history/v<version>.json` (per ADR 0829-01 §3). |

Notes-from-commits: spec AC-US17-01 requires automated generation via `git-cliff` (Rust-based, conventional-commits aware) or `conventional-changelog`. **Architect picks `git-cliff`** — single-file binary, no node deps, faster CI, cleaner output for our markdown-heavy notes. Config at `cliff.toml` groups by `feat`, `fix`, `perf`, `docs`, `refactor` (AC-US17-02). Notes script:

```bash
# scripts/release/generate-release-notes.sh
PREV=$(git describe --tags --abbrev=0 --match='desktop-v*' HEAD^)
NEW=${1:-$(git describe --tags --abbrev=0 --match='desktop-v*')}
git-cliff "${PREV}..${NEW}" --tag "$NEW" --strip header > notes-body.md

# Append SHA256 checksums (AC-US17-03)
cat >> notes-body.md <<EOF

## Checksums
\`\`\`
$(sha256sum dist/release/*)
\`\`\`

## Diff
[Compare ${PREV}...${NEW}](https://github.com/anton-abyzov/vskill/compare/${PREV}...${NEW})
EOF

gh release edit "$NEW" --notes-file notes-body.md  # AC-US17-05
```

### 7.4 Rollback workflow

Separate `desktop-rollback.yml` with `workflow_dispatch` input `version`:

```yaml
on:
  workflow_dispatch:
    inputs:
      target_version:
        description: "Version to roll back TO (must already exist in /desktop/history/)"
        required: true
jobs:
  rollback:
    runs-on: ubuntu-22.04
    steps:
      - run: |
          aws --endpoint-url $R2_ENDPOINT s3 cp \
            s3://vskill-desktop/desktop/history/v${{ inputs.target_version }}.json \
            s3://vskill-desktop/desktop/latest.json
```

### 7.5 Track D deliverables

- [ ] T-D-01: Updater config in `tauri.conf.json` with public key + R2 endpoint — covers AC-US14-01, AC-US14-03
- [ ] T-D-02: `.github/workflows/desktop-release.yml` — full workflow per §7.2 — covers AC-US13-01..06, AC-US16-03
- [ ] T-D-03: Six publisher scripts in `scripts/release/` (gpg-sign-linux/windows, upload-r2, emit-platform-fragment, assemble-manifest, publish-manifest, generate-release-notes) — covers AC-US16-05, AC-US17-01..05
- [ ] T-D-04: `.github/workflows/desktop-rollback.yml` (workflow_dispatch with `target_version` input)
- [ ] T-D-05: `docs/RELEASING-DESKTOP.md` runbook (publish, rollback, key rotation, notarization stall recovery)
- [ ] T-D-06: Updater client polls every 24h while running — verified via Tauri `pubdate` log assertion — covers AC-US14-02
- [ ] T-D-07: Per-platform manifest URLs use Tauri's contract keys (`darwin-x86_64`, `darwin-aarch64`, `windows-x86_64`, `linux-x86_64-deb`, `linux-x86_64-rpm`, `linux-x86_64-appimage`) — covers AC-US14-04 (note: spec lists per-format Linux URLs explicitly; we expand the manifest to include all three Linux variants since Tauri Updater on Linux can target the user's installed format)
- [ ] T-D-08: Signature verification failure logs warning + rejects update silently (no UI) — covers AC-US14-05
- [ ] T-D-09: In-app update notification with "Install now" / "Remind me later" / "Skip this version" — implemented in `dist/eval-ui/` studio bundle wired to `update-available` event from 0828 plan §3.3 — covers AC-US15-01..02
- [ ] T-D-10: Update download progress UI + retry on network failure + cleanup of partial downloads — covers AC-US15-03..05
- [ ] T-D-11: Cache-Control header `public, max-age=3600` on `latest.json` (Cloudflare Worker route or R2 metadata) — covers AC-US16-02
- [ ] T-D-12: Staging manifest at `verified-skill.com/desktop/staging.json` (used by US-28 update-flow E2E) — covers AC-US16-04
- [ ] T-D-13: First end-to-end dry-run on `desktop-v0.0.0-rc1` tag — gates Phase 5 + Track F
- [ ] T-D-14: `cliff.toml` config for `git-cliff` with feat/fix/perf/docs/refactor groupings — covers AC-US17-02
- [ ] T-D-15: `.github/workflows/notarize-dry-run.yml` nightly cron job with stall alert to Anton's email — covers NFR-17

---

## 8. Track E — SEO + Marketing Site

**Owner sub-agent**: `seo-landing-agent`
**Spec ACs**: AC-US18-01..05 (SEO baseline: H1 keyword + JSON-LD + OG + sitemap + robots), AC-US19-01..05 (3 landing pages: /desktop, /ai-studio, /skill-studio), AC-US20-01..04 (Search Console + Bing Webmaster), AC-US21-01..05 (Lighthouse ≥90 on 5 pages), AC-US22-01..05 (press kit), AC-US23-01..03 (README badges), AC-US24-01..05 (launch drafts NO POSTING), AC-US25-01..05 (social cards).

**Project**: `repositories/anton-abyzov/vskill-platform/` (Next.js 15 / OpenNext / Cloudflare).

### 8.1 Site state inventory

The platform already has solid SEO foundations:
- `src/app/robots.ts` allows `/`, disallows `/api/`, `/admin/`, `/auth/`. Sitemap referenced. (AC-US18-05 — already passes.)
- `src/app/sitemap.ts` enumerates static pages with priorities; `/skills`, `/docs`, `/studio`, `/publishers`, `/insights`, `/watch`, `/trust`, `/queue`, `/submit`, `/blocklist`. (AC-US18-04 — already passes; we extend with new URLs.)
- Homepage (`src/app/page.tsx`) has `WebSite` + `@graph` JSON-LD already. **AC-US18-02 requires `SoftwareApplication` JSON-LD on the homepage as well** — we extend the `@graph` to add a `SoftwareApplication` node alongside the existing `WebSite` node.
- `next.config.ts` has redirects (`/learn` → `/watch`).

**Homepage H1 keyword decision (AC-US18-01)**: spec leaves the exact phrase open ("Skill Studio" or chosen exact-match keyword). Architect's recommendation: use **"Skill Studio"** as the homepage `<h1>` exact-match keyword. Rationale: it's the spec's default suggestion, captures the high-intent "AI Studio" search pool, and aligns with the `/ai-studio` SEO bridge (so internal links across the site reinforce the same exact-match phrase). PM confirms in OQ-08.

**Missing for desktop launch**: `/desktop`, `/ai-studio`, `/skill-studio`, `/security`, `/press` pages. (Note: `/skill-studio` may overlap with the existing `/studio` route — see §8.2 disambiguation.)

### 8.2 Three landing pages

#### `/desktop` — primary marketing landing for Skill Studio

`src/app/desktop/page.tsx`:

- **H1**: "Skill Studio — your skill marketplace, native"
- **Hero**: 30s screencast loop (existing `public/product-demo/` asset reused) + OS-detect download CTA.
- **Three download cards** (primary + alternates):
  - macOS (auto-detected arch) — `.dmg` from latest GitHub Release / R2.
  - Windows — `.msi` + SmartScreen warning + GPG verification snippet.
  - Linux — three buttons (`.deb`, `.rpm`, `.AppImage`) + GPG verification snippet.
- **Feature strip**: native Dock/menu bar / auto-update / signed installer / vskill:// deep links.
- **Footer**: link to GitHub Releases (manual download), `/security` (GPG + minisign keys), Homebrew install command.

OS-detect via UA in a Server Component on first paint; CTA hydrates client-side for arch detection (`navigator.userAgentData.architecture` on Chromium, fallback to `navigator.platform`).

#### `/ai-studio` — repositioning page for "AI Studio" search keyword

A SEO-focused page targeting users searching "ai studio" / "claude skill ai studio" — explains what Skill Studio is, links to `/studio` (the in-product flagship surface) and `/desktop`. No new product surface, just an SEO bridge.

#### `/skill-studio` — repositioning page for "skill studio" keyword

Same pattern: SEO-targeted entry that explains the product and routes to `/studio` (existing) + `/desktop`.

#### Disambiguation note

Existing `/studio` is the flagship surface (priority 0.95 in sitemap). `/ai-studio` and `/skill-studio` are pure SEO redirect-ish pages — they should use `<link rel="canonical" href="/studio" />` if their content is materially the same, or stand on their own with unique copy targeting their search keyword. **Architect recommends**: stand-alone copy targeting the search term, with prominent CTA to `/studio` and `/desktop`. This avoids canonical penalties and captures both keyword pools.

### 8.3 Structured data on `/desktop`

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Skill Studio",
  "operatingSystem": "macOS, Windows, Linux",
  "applicationCategory": "DeveloperApplication",
  "applicationSubCategory": "AI Tooling",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": null,   // backfill once we have ratings
  "downloadUrl": "https://verified-skill.com/desktop",
  "softwareVersion": "1.0.0",
  "fileSize": "45 MB",
  "screenshot": [
    "https://verified-skill.com/images/desktop/hero.png",
    "https://verified-skill.com/images/desktop/menu.png"
  ],
  "creator": {
    "@type": "Organization",
    "name": "Verified Skill",
    "url": "https://verified-skill.com"
  }
}
```

Inject via `<script type="application/ld+json">` in the page's `metadata` export, following the homepage pattern.

### 8.4 OG / Twitter cards

Per page (Next.js 15 `metadata` export):

```ts
export const metadata = {
  title: "Skill Studio — Native skill marketplace for macOS, Windows, Linux",
  description: "Install AI skills with one click. Native Dock icon, signed installer, auto-update, vskill:// deep links.",
  openGraph: {
    title: "Skill Studio",
    description: "...",
    url: "https://verified-skill.com/desktop",
    siteName: "Verified Skill",
    images: [{ url: "https://verified-skill.com/images/desktop/og.png", width: 1200, height: 630 }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Skill Studio",
    description: "...",
    images: ["https://verified-skill.com/images/desktop/og.png"],
  },
};
```

OG image: 1200×630 PNG, generated from a Remotion still consistent with `/dmg-background.png` to maintain brand cohesion.

### 8.5 Sitemap updates

`src/app/sitemap.ts` adds:

```ts
{ url: `${base}/desktop`, changeFrequency: "weekly", priority: 0.95 },
{ url: `${base}/ai-studio`, changeFrequency: "monthly", priority: 0.7 },
{ url: `${base}/skill-studio`, changeFrequency: "monthly", priority: 0.7 },
{ url: `${base}/security`, changeFrequency: "yearly", priority: 0.5 },
{ url: `${base}/press`, changeFrequency: "monthly", priority: 0.5 },
```

`/desktop` at 0.95 because it's a primary product entry-point alongside `/skills` and `/studio`.

### 8.6 Press kit at `/press`

Static page with:
- Logo: SVG + 1024×1024 PNG + 256×256 PNG (transparent + on-light + on-dark variants, 6 PNGs total).
- Screenshots: 3 product screenshots from 0828 install-test (1280×800 PNG).
- One-liner: "Skill Studio is the native AI skill marketplace for macOS, Windows, and Linux."
- Three-line description.
- Founder bio: 100 words about Anton Abyzov + headshot (Anton-provided).
- Contact email: `press@verified-skill.com` (alias to `anton.abyzov@gmail.com`).

Assets stored at `public/press/`.

### 8.7 Lighthouse CI (per AC-US21-01..05)

`.github/workflows/lighthouse.yml` on PR + main, hitting **5 pages** per spec: `/`, `/desktop`, `/ai-studio`, `/skill-studio`, `/press`. **Mobile profile** per AC-US21-02.

```yaml
name: Lighthouse
on: { pull_request: { branches: [main] }, push: { branches: [main] } }
jobs:
  lhci:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - run: npm ci
      - run: npx lhci autorun \
          --collect.url=https://verified-skill.com/ \
          --collect.url=https://verified-skill.com/desktop \
          --collect.url=https://verified-skill.com/ai-studio \
          --collect.url=https://verified-skill.com/skill-studio \
          --collect.url=https://verified-skill.com/press \
          --collect.settings.preset=mobile \
          --collect.numberOfRuns=2 \
          --assert.preset=lighthouse:recommended \
          --assert.assertions.categories:performance.minScore=0.90 \
          --assert.assertions.categories:accessibility.minScore=0.90 \
          --assert.assertions.categories:seo.minScore=0.90 \
          --assert.assertions.categories:best-practices.minScore=0.90
```

**Score thresholds (mobile)**: Performance ≥0.90, Accessibility ≥0.90, SEO ≥0.90, Best Practices ≥0.90. Fail PR on regression.

Twice-run with `numberOfRuns=2` absorbs CI runner variance; LHCI takes the median by default.

### 8.8 README badge refresh on vskill repo

Add to `repositories/anton-abyzov/vskill/README.md` top:

```markdown
[![npm version](https://img.shields.io/npm/v/vskill.svg)](https://www.npmjs.com/package/vskill)
[![GitHub stars](https://img.shields.io/github/stars/anton-abyzov/vskill.svg?style=social)](https://github.com/anton-abyzov/vskill/stargazers)
[![Downloads](https://img.shields.io/github/downloads/anton-abyzov/vskill/total.svg)](https://github.com/anton-abyzov/vskill/releases)
[![License](https://img.shields.io/github/license/anton-abyzov/vskill.svg)](https://github.com/anton-abyzov/vskill/blob/main/LICENSE)
[![CI](https://github.com/anton-abyzov/vskill/actions/workflows/ci.yml/badge.svg)](https://github.com/anton-abyzov/vskill/actions/workflows/ci.yml)
[![Desktop Release](https://github.com/anton-abyzov/vskill/actions/workflows/desktop-release.yml/badge.svg)](https://github.com/anton-abyzov/vskill/actions/workflows/desktop-release.yml)
```

### 8.9 Track E deliverables

- [ ] T-E-01: Homepage `<h1>` set to "Skill Studio" — covers AC-US18-01
- [ ] T-E-02: Homepage `@graph` JSON-LD extended with `SoftwareApplication` node — covers AC-US18-02
- [ ] T-E-03: `src/app/desktop/page.tsx` with hero, OS-detect CTA, feature strip, JSON-LD, 3 download CTAs (mac/win/linux × 3 formats) — covers AC-US19-01, AC-US19-04, AC-US19-05
- [ ] T-E-04: `src/app/ai-studio/page.tsx` SEO bridge with primary CTA + install instructions section — covers AC-US19-02, AC-US19-04, AC-US19-05
- [ ] T-E-05: `src/app/skill-studio/page.tsx` SEO bridge with primary CTA + install instructions section — covers AC-US19-03, AC-US19-04, AC-US19-05
- [ ] T-E-06: `src/app/security/page.tsx` (GPG fingerprint at `.well-known/pgp-key.asc`, minisign pubkey, threat model)
- [ ] T-E-07: `src/app/press/page.tsx` + logo SVG/PNG (light + dark) in `public/press/` — covers AC-US22-01
- [ ] T-E-08: 3+ product screenshots on `/press` — covers AC-US22-02
- [ ] T-E-09: One-liner + 3-line description on `/press` — covers AC-US22-03, AC-US22-04
- [ ] T-E-10: Press contact email rendered (`press@verified-skill.com` alias) — covers AC-US22-05
- [ ] T-E-11: Sitemap additions (5 new URLs) — covers AC-US18-04
- [ ] T-E-12: `<meta og:image>` 1200×630 PNG renderer (Remotion still) committed to `public/images/desktop/og.png` and rendered on `/`, `/desktop`, `/ai-studio`, `/skill-studio`, `/press` — covers AC-US18-03, AC-US25-01..05
- [ ] T-E-13: LinkedIn Post Inspector + Discord embed verification screenshots committed to `docs/marketing/social-card-proof/` — covers AC-US25-02, AC-US25-03
- [ ] T-E-14: `.github/workflows/lighthouse.yml` Lighthouse CI gate at ≥90 across 4 categories on 5 pages — covers AC-US21-01..05
- [ ] T-E-15: Search Console verification (DNS TXT or HTML file) — Anton handoff in Phase 6 — covers AC-US20-01
- [ ] T-E-16: Sitemap submitted via Search Console — Anton handoff — covers AC-US20-02, AC-US20-03
- [ ] T-E-17: Bing Webmaster Tools verification — Anton handoff — covers AC-US20-04
- [ ] T-E-18: README badge refresh (download count, build status, license, npm version) — covers AC-US23-01..03
- [ ] T-E-19: Launch drafts in `repositories/anton-abyzov/vskill/marketing/launch/` — `producthunt.md`, `show-hn.md`, `reddit-localllama.md`, `devto-article.md`. ALL marked "DRAFT — DO NOT POST". — covers AC-US24-01..05

---

## 9. Track F — Verification Team

**Owner sub-agent**: `verification-orchestrator-agent` (spawns 4 sub-agents in parallel post-release)

Runs **after** Track D produces a successful published release. Pure post-deployment validation, no code changes.

### 9.1 Four parallel verifier agents

| Agent | Runner | Mission |
|---|---|---|
| **macos-verify-agent** | local macos-14 (architect's machine) — uses computer-use MCP | Download `.dmg` from latest release, `hdiutil attach`, drag to /Applications, launch via `open`, AppleScript window check, simulate `Cmd+K` (with ATCC permission caveat documented), assert studio loads, assert `Find Skills` opens. Capture screenshots for proof. |
| **windows-verify-agent** | dispatched via `windows-verify.yml` workflow on `windows-2022` runner | Download `.msi`, install via `msiexec /i ... /qn`, launch via `Start-Process`, `Get-Process vSkill`, assert HTTP server reachable on hashed port, capture screenshot. |
| **linux-verify-agent** | dispatched via `linux-verify.yml` workflow on `ubuntu-22.04` runner | Three sub-jobs: `.deb` install via `dpkg -i`; `.rpm` install via `rpm -ivh` (in Fedora container); `.AppImage` `chmod +x && ./vSkill_*.AppImage --no-sandbox`. xvfb headless. Assert process tree + HTTP server. |
| **seo-verify-agent** | local — uses claude-in-chrome MCP | Lighthouse against `/desktop`, `/ai-studio`, `/skill-studio`, `/`, `/studio`. Manual Google search for "Skill Studio" / "vskill desktop" — record SERP position (likely 0 results day 1; scheduled re-check 2 weeks later). Bing same. Verify sitemap.xml has new URLs. Verify Google Search Console submission (manual handoff to Anton). |

### 9.2 Verification report

Each agent emits `verify-report-<platform>.json`:

```json
{
  "platform": "macos-aarch64",
  "version": "1.0.0",
  "downloadOk": true,
  "installOk": true,
  "launchOk": true,
  "studioLoadOk": true,
  "deepLinkOk": true,
  "autoUpdateOk": true,
  "screenshotPath": ".specweave/increments/0829-vskill-distribution-and-marketing/reports/verify-macos.png",
  "issues": []
}
```

Orchestrator aggregates → `.specweave/increments/0829-vskill-distribution-and-marketing/reports/verify-summary.md`.

### 9.3 Track F deliverables

- [ ] T-F-01: `verify-release.yml` GH Actions workflow with matrix `macos-15`, `windows-latest`, `ubuntu-22.04` — covers AC-US26-01
- [ ] T-F-02: macOS verification: hdiutil mount + cp to /Applications + launch + 10s alive + log-shows-sidecar + updater-registered assertions — covers AC-US26-02
- [ ] T-F-03: Windows verification: msiexec /i /qn + launch + 10s alive + deep-link-registered assertion — covers AC-US26-03
- [ ] T-F-04: Linux .deb verification (dpkg -i + 10s alive + WebKitGTK present) — covers AC-US26-04
- [ ] T-F-05: Linux .rpm verification in Fedora container — covers AC-US26-05
- [ ] T-F-06: Linux AppImage verification (chmod +x + run) — covers AC-US26-06
- [ ] T-F-07: Failure of any verification job blocks release announcement (release stays as draft until manually promoted) — covers AC-US26-07
- [ ] T-F-08: Cmd+K (mac) / Ctrl+K (win/linux) "Find Skills" modal parity test — covers AC-US27-01..05
- [ ] T-F-09: Update-flow E2E test (install vN-1 → point at staging manifest with vN → trigger check → verify notification → install → restart → verify version) — covers AC-US28-01..05
- [ ] T-F-10: Post-deploy SEO verification at +7d and +30d (Google `site:verified-skill.com` count, "Skill Studio" SERP position, Search Console coverage report, Lighthouse SEO regression check) — covers AC-US29-01..04
- [ ] T-F-11: First-release verification report aggregated to `.specweave/increments/0829-vskill-distribution-and-marketing/reports/verify-summary.md`

---

## 10. Implementation Phases

The downstream `sw-planner` agent will produce `tasks.md` from this. Six phases mapped roughly to tracks:

### Phase 1 — Pre-flight gates (cert, bundle ID, keypairs, R2)

**Sequential, ~1 day, BLOCKING.** Architect or Anton runs the commands in §3. Output is the GH Actions secret matrix populated.

**Spec ACs covered**: cert-created, bundle-id-registered, updater-pubkey-embedded, gpg-key-published, r2-bucket-live.

### Phase 2 — Track A/B/C config (parallel)

Three parallel sub-agents update `tauri.conf.json` per-platform, write `Entitlements.plist`, write GPG sign scripts, validate locally with `npm run desktop:build`. **Per-platform validation only** — no CI yet.

**Spec ACs covered**: macOS-config, windows-config, linux-config.

### Phase 3 — Track D (auto-updater + release workflow)

Single agent assembles `desktop-release.yml`, the five publisher scripts, the rollback workflow. First end-to-end dry-run on a `desktop-v0.0.0-rc1` pre-release tag.

**Spec ACs covered**: auto-update-config, release-workflow, manifest-publisher, rollback-runbook.

### Phase 4 — Track E (SEO + landing pages)

Single agent builds the four new pages on `vskill-platform`, sitemap updates, OG image rendering, Lighthouse CI, README badges, marketing draft copy.

**Spec ACs covered**: desktop-landing, ai-studio-landing, skill-studio-landing, security-page, press-kit, lighthouse-gate, readme-badges.

### Phase 5 — First real release (`desktop-v1.0.0`)

Architect (or Anton) tags `desktop-v1.0.0`. CI runs Phase 1-2 outputs end-to-end. Manual smoke check on a single platform before the verification team kicks off.

**Spec ACs covered**: first-release-published, all-three-platforms-built, manifest-live.

### Phase 6 — Track F (verification team)

Four parallel verifier agents per §9. Aggregated report. Any P0 issue → emergency rollback (Track D §7.4) + back to Phase 5.

**Spec ACs covered**: verification-passed-mac, verification-passed-win, verification-passed-linux, lighthouse-scores, seo-discoverable.

### Phase 7 (post-launch, out of v1 critical path) — Polish

- Mainline Homebrew Cask submission (after 30 days staging clean).
- winget submission (only if OV cert acquired, which is out of v1 scope).
- ProductHunt draft → live posting (out of v1 per scope cut).
- Beta channel manifest URL.

---

## 11. Risk Register

Inherits 0828's R1–R10. New 0829-specific risks:

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-D1 | First notarization fails on entitlement combo | Medium | Phase 5 release blocked | Phase 3 dry-run on `desktop-v0.0.0-rc1` exercises the full path before real tag. Specific failure modes from [Apple notarization forum](https://developer.apple.com/forums/topics/code-signing-topic/code-signing-topic-notarization) documented in `RELEASING-DESKTOP.md`. |
| R-D2 | Linux WebKitGTK 4.1 missing on older distros | Medium (Debian 11, RHEL 8) | Subset of users can't run app | Documented minimum: Ubuntu 22.04+, Debian 12+, Fedora 38+ in `/desktop` page Linux card + README. AppImage's portability is glibc-bound (per ADR 0829-02). |
| R-D3 | Tauri Updater private key compromise | Low | All future updates compromised | Key in 1Password Family vault + repo-only GH secret. Rotation runbook in `RELEASING-DESKTOP.md`. "Freeze updates" procedure: ship `tauri.conf.json` with 404'd endpoint + new pubkey, force users to manual reinstall. |
| R-D4 | Google indexing delay 1-2 weeks post-launch | High | Day-1 SEO score is 0 | Pre-warm via internal links from `/`, `/skills`, `/studio` to `/desktop` at deploy time. Manual Google Search Console + Bing Webmaster Tools submission day 1 (Anton handoff in Phase 6). |
| R-D5 | R2 bucket bandwidth misconfigured (egress charges) | Low | Surprise bill | R2 is zero-egress by default ([R2 pricing](https://developers.cloudflare.com/r2/pricing/)). Custom domain via Cloudflare CDN inherits zero-egress. Verified via Cloudflare bill alert at $10. |
| R-D6 | Bundle bloat: per-arch macOS .dmg = 2x artifacts | Accepted | Larger release page | User accepts (per scope cut analysis §4.4). |
| R-D7 | tauri-action notarization stall mid-release (Feb 2026 precedent) | Medium | Phase 5 delay | 3-attempt retry with 600s backoff per §4.3. If all 3 fail, release is held (manual retry next day). |
| R-D8 | Homebrew bump-cask PAT scope drift | Low | Cask updates fail silently | PAT scoped to `repo` + `public_repo` on the staging tap repo only. Rotated annually, calendar reminder in 1Password. |
| R-D9 | Lighthouse CI flakiness on slow CI runners | Medium | False CI failures | Run twice with `--collect.numberOfRuns=2`, take best score. Performance threshold tuned to 0.85 (not 0.90) to absorb runner variance. |
| R-D10 | SmartScreen reputation cold-start hurts Windows installs | High | First-month Windows conversion drops | Per scope cut: accepted. README + `/desktop` Windows card explains "Run anyway". Reputation accrues automatically; OV cert deferred. |
| R-D11 | First Homebrew Cask reviewer rejects style nits | Medium | Mainline submission delay | Stage on `antonabyzov/homebrew-vskill-staging` for 30+ days first; first mainline PR addresses any style nits in review. |

---

## 12. Open Questions

Architect's resolutions for spec.md §8 OQ-01..06 + new architect-OQ items:

### Resolutions of spec OQ-01..06

1. **Spec OQ-01 (manifest hosting)** → **RESOLVED by ADR 0829-01**: Cloudflare R2 with custom domain `verified-skill.com/desktop/*` (zero egress + CDN inherited). NOT Cloudflare Pages — R2 is purpose-built for this and gives finer control over Cache-Control per object.
2. **Spec OQ-02 (signing system)** → **RESOLVED by ADR 0829-01**: minisign for v1. Tauri 2 Updater natively supports minisign with no plugin work; cosign would require a custom verifier crate. Revisit cosign in v1.1+ if enterprise customers demand transparency logs.
3. **Spec OQ-03 (Linux strategy)** → **RESOLVED by ADR 0829-02**: ship all three formats (`.deb` + `.rpm` + `.AppImage`). Marginal CI cost ~30s, broad reach, single `cargo tauri build` invocation produces all three.
4. **Spec OQ-04 (single vs multi-channel)** → **RESOLVED**: single `stable` channel for v1. `beta` channel deferred until telemetry exists (out of v1 scope).
5. **Spec OQ-05 (press kit screenshots format)** → **RESOLVED**: PNG @2x for screenshots (lossless, universal browser support, sub-200KB after `pngquant`), SVG for logos (scalable, zero quality loss). WebP rejected — minor size win not worth the LinkedIn/email-client compatibility hit for press use.
6. **Spec OQ-06 (license)** → **RESOLVED**: vskill repo `LICENSE` is already MIT (`Copyright (c) 2026 Anton Abyzov`). README badge uses MIT. No action needed.

### New architect OQs (not in spec)

7. **OQ-A1 (SmartScreen mitigation strategy)** → **Open for PM**: stick with unsigned + documented "Run anyway" UX (architect default per spec AC-US06-01..04), or invest in closed-cohort warm-up first (0828 R8 strategy)? Architect leans documented-only for v1 since cohort coordination is operational overhead and reputation accrues with public downloads anyway. Spec R-02 hints "consider buying OV cert in v1.1" — cohort approach can be deferred along with that.
8. **OQ-A2 (`/ai-studio` vs `/skill-studio` content disambiguation)** → **Open for PM**: spec AC-US19-02..03 requires both pages exist with unique titles/meta — does PM want stand-alone unique copy (architect default, captures both keyword pools) or canonical-to-`/studio` (simpler but loses one keyword pool)? Architect leans stand-alone.
9. **OQ-A3 (homepage H1 exact-match keyword)** → architect picked `"Skill Studio"` per spec AC-US18-01's default. PM confirms?
10. **OQ-A4 (press kit founder bio + headshot)** → **Open for Anton**: needs his copy + photo. Track E ships `/press` with a placeholder TODO marker for Anton to fill.
11. **OQ-A5 (`releases@verified-skill.com` email alias)** → **Open for Anton**: needs setup before Phase 1 GPG key (used as the GPG UID email). Alternative: use Anton's primary email; users verify by fingerprint, not email. Architect leans alias-route since it survives email-provider migrations.
12. **OQ-A6 (cohort warm-up + ProductHunt timing)** → spec AC-US24-05 explicitly says "user picks the launch date" and "DRAFT — DO NOT POST." Architect respects that gate; no action item.

---

## 13. Contract Summary (for downstream agents)

### Tracks A/B/C/D implementer MUST NOT change:

- 0828's process tree (Tauri shell + Node sidecar + WebView).
- `dist/eval-ui/` source code — desktop loads it verbatim.
- `boot-preflight.ts` import order.
- `~/.vskill/workspace.json` schema or atomic-write pattern.
- `/api/shutdown` POST contract.
- 0828's already-set `tauri.conf.json` fields: `productName`, `version`, `identifier`, `bundle.targets` (will be EXTENDED, not replaced — see §6.1), `bundle.windows.webviewInstallMode`, `plugins.deep-link`.

### Tracks A/B/C/D implementer MUST add:

- `src-tauri/Entitlements.plist` (Track A).
- `tauri.conf.json` extensions: `bundle.macOS.signingIdentity`, `bundle.macOS.entitlements`, `bundle.macOS.dmg`, `bundle.linux.{deb,rpm,appimage}`, `plugins.updater`.
- `assets/dmg-background.png` (Track A).
- `.github/workflows/desktop-release.yml`, `.github/workflows/desktop-rollback.yml` (Track D).
- `.github/workflows/windows-verify.yml`, `.github/workflows/linux-verify.yml` (Track F).
- `scripts/release/{gpg-sign-linux.sh, gpg-sign-windows.sh, upload-r2.sh, emit-platform-fragment.sh, assemble-manifest.sh, publish-manifest.sh}` (Track D).
- `docs/RELEASING-DESKTOP.md` runbook (Track D).
- `docs/marketing/{announcement-tweet.md, producthunt-draft.md}` (Track E, drafts only — no posting).

### Track E implementer MUST add (vskill-platform repo):

- `src/app/desktop/page.tsx` + co-located components.
- `src/app/ai-studio/page.tsx`.
- `src/app/skill-studio/page.tsx`.
- `src/app/security/page.tsx`.
- `src/app/press/page.tsx` + `public/press/{logo-*.svg,-png, screenshot-*.png}`.
- Sitemap additions in `src/app/sitemap.ts`.
- OG image renderer at `scripts/render-og-images.ts` (Remotion).
- `.github/workflows/lighthouse.yml`.

### Track E implementer MUST NOT change:

- Existing `/studio` route (flagship surface, untouched).
- Existing JSON-LD schema on `/` (only ADD `/desktop` schema).
- Existing redirects (`/learn` → `/watch`).

### Test budget gates (anchored to spec NFRs):

| Gate | Budget | Spec NFR |
|---|---|---|
| macOS install→first-launch (Apple Silicon) | ≤5s p50 | NFR-01 |
| macOS install→first-launch (Intel) | ≤8s p50 | NFR-02 |
| Windows install→first-launch (Win 11) | ≤30s p50 | NFR-03 |
| Windows install→first-launch (Win 10) | ≤45s p50 | NFR-03 |
| Linux install→first-launch | ≤10s p50 | NFR-04 |
| Auto-update download + restart | ≤60s p50 @ 50 Mbps | NFR-05 |
| GitHub Actions release matrix wall-clock | ≤25 min p50 | NFR-06, AC-US13-06 |
| macOS `.dmg` (universal2) | ≤150 MB | NFR-07 |
| Windows `.msi` | ≤80 MB | NFR-08 |
| Linux `.deb` | ≤80 MB | NFR-09 |
| Linux `.rpm` | ≤80 MB | NFR-10 |
| Linux `.AppImage` | ≤90 MB | NFR-11, AC-US11-04 |
| Total release artifact size | ≤500 MB | NFR-12 |
| Google indexing of `/desktop` | ≤7 days | NFR-13, AC-US29-01 |
| Lighthouse all categories (mobile) on 5 marketing pages | ≥90 | NFR-14, AC-US21-01..04 |
| OG image size | ≤200 KB @ 1200×630 | NFR-15 |
| Auto-update success rate | ≥99.9% on 100 samples | NFR-16 |
| Notarization stall alert | nightly dry-run, alert if >4h | NFR-17 |
| Manifest URL global reachability | ≥99.9% | NFR-18 |

**Nightly dry-run notarization** (NFR-17): adds `.github/workflows/notarize-dry-run.yml` running on cron `0 6 * * *` UTC against `main`, building an unreleased `.dmg` and submitting to notarytool. Alerts to `releases@verified-skill.com` (Anton's email) if submission stalls >4h. Fixed cost: ~1 macos-14 runner-minute/day (~$0.30/mo).

---

## 14. Sources Cited During Research

- [Tauri 2 GitHub Actions tauri-action](https://github.com/tauri-apps/tauri-action) — confirms cross-platform matrix support; `macos-14`, `windows-2022`, `ubuntu-22.04` runners are the 2026 standard.
- [Tauri 2 Updater plugin](https://v2.tauri.app/plugin/updater/) — confirms minisign as native signing path; `latest.json` schema; client-side verification.
- [Tauri 2 Linux Debian distribution](https://v2.tauri.app/distribute/debian/) — `.deb` dependency declaration syntax.
- [Tauri 2 prerequisites — Linux](https://v2.tauri.app/start/prerequisites/) — required APT packages.
- [Tauri 2 alpha-3 webkit2gtk-4.1 migration note](https://v2.tauri.app/blog/tauri-2-0-0-alpha-3/) — minimum WebKit version + Ubuntu 22.04 baseline.
- [Tauri 2 bundle discussion #10026](https://github.com/orgs/tauri-apps/discussions/10026) — confirms `cargo tauri build` produces `.deb`/`.rpm`/`.AppImage` in one invocation; AppImage glibc portability semantics.
- [Cloudflare R2 custom domains](https://developers.cloudflare.com/r2/buckets/public-buckets/#custom-domains) — zero-egress + CDN.
- [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/) — Class A/B operations pricing; no egress fees.
- [Apple notarization forum (notarytool topic)](https://developer.apple.com/forums/topics/code-signing-topic/code-signing-topic-notarization) — Feb 2026 outage precedent + retry guidance.
- [Apple notarytool man page](https://keith.github.io/xcode-man-pages/notarytool.1.html) — `--keychain-profile`, `--wait`, `--timeout` semantics.
- [TN3147 migrating to notarytool](https://developer.apple.com/documentation/technotes/tn3147-migrating-to-the-latest-notarization-tool) — `altool` → `notarytool` migration confirmed.
- [Homebrew bump-cask GitHub Action (macauley)](https://github.com/marketplace/actions/homebrew-bump-cask) — auto-PR workflow.
- [Homebrew How-To Open a Pull Request](https://docs.brew.sh/How-To-Open-a-Homebrew-Pull-Request) — mainline submission flow.
- [minisign reference](https://jedisct1.github.io/minisign/) — Ed25519 signature spec.
- 0828 plan (`/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0828-vskill-desktop-app/plan.md`) — foundational architecture.
- 0828 ADR-01 (`/Users/antonabyzov/Projects/github/specweave-umb/.specweave/docs/internal/architecture/adr/0828-01-vskill-desktop-framework-choice.md`) — Tauri 2 framework rationale.
