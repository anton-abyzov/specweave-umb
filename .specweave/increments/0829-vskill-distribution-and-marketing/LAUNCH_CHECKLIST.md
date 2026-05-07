# Skill Studio — LAUNCH CHECKLIST

> Punch list of every user-action item flagged by 0828 + 0829 implementation agents. Knock these out in order; the runbook at the bottom triggers your first signed release.

**Scope**: macOS .dmg (notarized) + Windows .msi (unsigned v1) + Linux .deb/.rpm/.AppImage (GPG-signed) + Tauri auto-updater + Cloudflare R2 hosting + ProductHunt/HN/Reddit launch.

---

## Time-to-launch estimate

| Phase | Estimate |
|---|---|
| P0 code fixes (`tauri-plugin-updater` crate + minisign placeholder + DRY_RUN sequencing) | **~15 min** |
| All BLOCKING setup items (Apple, Tauri, GPG, R2, GH Secrets, repo config) | **3.5–5 hours** of focused work |
| Marketing assets (OG PNGs, founder bio, screenshots, press kit) | **2–4 hours** |
| Marketing posts (review/customize 7 drafts) | **1–2 hours** |
| First-release rc1 dry-run + smoke test | **1–2 hours** (most is CI wait) |
| **Total to signed launch-ready** | **~8–13 hours**, splittable across 1–3 days |

**Top 3 blocking items** (do these first — everything else waits on them):
1. **P0 code fix — `tauri-plugin-updater` crate missing.** `tauri.conf.json` declares full `plugins.updater` config but the Rust crate is not in `src-tauri/Cargo.toml` and not registered in the Builder chain. Auto-update is dead-code until fixed. 5-min code change. See [§0](#0-p0-code-fixes-before-first-release).
2. **Apple Developer ID Application certificate** — without it the macOS release job cannot sign or notarize. Path: developer.apple.com → 10–15 min after Admin role confirmed. See [§1](#1-apple-developer-pre-phase-1-macos-gate).
3. **Tauri minisign keypair** — without it the auto-updater cannot ship; baked into `tauri.conf.json` so a rebuild is needed if you change it later. 5 min. See [§2](#2-tauri-updater-minisign-pre-phase-1).

(Cloudflare R2 + custom domain — see [§4](#4-cloudflare-r2-manifest-hosting), 15–20 min — is also blocking but ranks just behind the above three.) Everything else (Linux GPG, GitHub Secrets propagation, marketing) can run in parallel after them.

---

## Source documents (reference list)

| Path | Purpose |
|---|---|
| `repositories/anton-abyzov/vskill/scripts/release/macos-README.md` | macOS pipeline + manual cert fallback |
| `repositories/anton-abyzov/vskill/scripts/release/linux-README.md` | Linux package install + GPG verification |
| `repositories/anton-abyzov/vskill/scripts/release/windows-README.md` | Windows .msi install + SmartScreen UX |
| `repositories/anton-abyzov/vskill/scripts/desktop/README.md` | Sidecar SEA build contract |
| `.specweave/increments/0829-vskill-distribution-and-marketing/reports/ci-pipeline/secrets.md` | Full GH Actions secrets list |
| `.specweave/increments/0829-vskill-distribution-and-marketing/reports/windows-port/notes.md` | Windows port notes + cross-arch gap |
| `.specweave/increments/0829-vskill-distribution-and-marketing/marketing-drafts/README.md` | Marketing draft index + open questions |

---

## 0. P0 Code fixes (before first release)

> **Blocking for desktop-v0.1.0** — these are code-fix items (not user-action), surfaced by config-verify-agent. Land as a small follow-up commit before tagging the first signed release. Estimated total: ~10–15 min.

### P0 — `tauri-plugin-updater` crate missing (HIGH severity)

`tauri.conf.json` declares full `plugins.updater` config (endpoints, pubkey, dialog), but the Rust crate is NOT wired in. Auto-update is silently dead-code until this lands. Without it:
- Tauri does not register the updater plugin at runtime.
- The minisign keypair from §2 is generated but never consumed.
- Users will never see an update prompt; new releases will not be picked up.

**Fix** (5-min code change):

- [ ] Edit `repositories/anton-abyzov/vskill/src-tauri/Cargo.toml` `[dependencies]` to add:
  ```toml
  tauri-plugin-updater = "2"
  ```
- [ ] Edit `repositories/anton-abyzov/vskill/src-tauri/src/lib.rs` and add to the Builder chain:
  ```rust
  .plugin(tauri_plugin_updater::Builder::new().build())
  ```
- [ ] Verify with `cargo check --manifest-path repositories/anton-abyzov/vskill/src-tauri/Cargo.toml` — should pass clean.
- [ ] Smoke-test: `cargo tauri dev` starts the app without panicking on plugin registration.

### P0 — Replace `<MINISIGN_PUBKEY_PLACEHOLDER>` in tauri.conf.json

The placeholder value MUST be replaced with the real public key from §2 BEFORE tagging any release. If the placeholder ships, every shipped binary trusts an undefined key and the auto-updater will reject all updates (or, worse, accept arbitrary signatures depending on Tauri's parsing fallback).

- [ ] Confirm `tauri.conf.json` → `plugins.updater.pubkey` no longer contains `<MINISIGN_PUBKEY_PLACEHOLDER>` after §2 step 2 is complete. Grep check: `grep -c PLACEHOLDER repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json` should print `0`.

### MEDIUM — `publish-manifest.sh` DRY_RUN sequencing

Env-var checks fire before the `DRY_RUN` short-circuit, so a credential-less dry-run still errors. Low-impact (you'll just see a clearer error after you set the secrets), but worth fixing for ergonomics.

- [ ] Edit `repositories/anton-abyzov/vskill/scripts/release/publish-manifest.sh` to move the `if [ -n "${DRY_RUN:-}" ]` short-circuit ABOVE the env-var validation block. Confirm `DRY_RUN=1 bash scripts/release/publish-manifest.sh 0.0.0 ./fake-artifacts/` exits 0 with a clear "[dry-run] would upload …" log without requiring R2 / Apple secrets to be populated.

---

## 1. Apple Developer (Pre-Phase-1 macOS gate)

> **Blocking** — macOS release job won't run without these. Estimated total: ~30 min after Admin role.
> Source: `scripts/release/macos-README.md` §"Manual fallback".

- [ ] **Confirm Admin role on EasyChamp team** at developer.apple.com → Membership. The ASC API key may need elevation to create a Developer ID cert non-interactively. (~2 min)  *(blocking)*
- [ ] **Register bundle ID `com.verifiedskill.desktop`** at developer.apple.com → Identifiers → `+` → App IDs → App. Description: "Skill Studio". Platform: macOS. App services: none. *(blocking, ~3 min)*
- [ ] **Generate a CSR** via Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority. Email: `anton.abyzov@gmail.com`. Common Name: `Anton Abyzov` (or `EasyChamp, Inc.`). Save to `~/.certs/vskill-developer-id.csr`. *(blocking, ~3 min)*
- [ ] **Create the Developer ID Application cert** at developer.apple.com → Certificates → `+` → Developer ID Application. Upload the `.csr`. Download the `.cer`. *(blocking, ~5 min)*
- [ ] **Install the .cer** by double-clicking → Keychain Access opens → confirm install in `login` keychain. *(blocking, ~1 min)*
- [ ] **Verify the cert is recognized** with `security find-identity -v -p codesigning | grep "Developer ID Application"`. Expected: `Developer ID Application: EasyChamp, Inc. (TEAMID)`. *(blocking, ~30 sec)*
- [ ] **Export to .p12 for CI**: in Keychain Access, right-click identity → Export → format `.p12` → set a strong password. Save to `~/.certs/vskill-developer-id.p12`. *(blocking, ~2 min)*
- [ ] **Update `tauri.conf.json` → `bundle.macOS.signingIdentity`** to the exact identity string from `security find-identity` (only if it differs from the current value `Developer ID Application: EasyChamp, Inc. (NMCB2JZ7QG)`). *(blocking if team-id differs, ~2 min)*
- [ ] **Get `APPLE_TEAM_ID`** from developer.apple.com → Membership → Team ID (10-char). *(blocking, ~30 sec)*
- [ ] **Generate `APPLE_APP_SPECIFIC_PASSWORD`** at appleid.apple.com → Sign-In and Security → App-Specific Passwords → "+ Generate" → label "vSkill notarize CI". *(nice-to-have — fallback to ASC API key path; ~2 min)*

> Note: ASC keys (`ASC_KEY_ID = JZ2ML9M66A`, `ASC_ISSUER_ID = a9be87c1-47d8-40f2-897d-75df80a540fb`) already exist in `~/.private_keys/AuthKey_JZ2ML9M66A.p8`. Preferred over app-specific password.

---

## 2. Tauri Updater minisign (Pre-Phase-1)

> **Blocking** — auto-updater is baked into `tauri.conf.json` at build time; changing it later requires rebuilding all desktop releases. Estimated total: ~10 min.
> Source: `scripts/release/macos-README.md` §"Pre-Phase-1 status" + `reports/ci-pipeline/secrets.md` §3.

- [ ] **Run `bash scripts/release/generate-minisign-key.sh`** locally (one-time). Set a strong passphrase you can recall. Output: `minisign-priv.key` + `minisign-pub.txt`. *(blocking, ~2 min)*
- [ ] **Paste the public key** (last line of `minisign-pub.txt`) into `repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json` → `plugins.updater.pubkey` (replace `<MINISIGN_PUBKEY_PLACEHOLDER>`). *(blocking, ~2 min)*
- [ ] **Save private key + passphrase to 1Password** in a "vSkill Updater Signing" item. The minisign-priv file + the passphrase + the corresponding `minisign-pub.txt` should all be attached. *(blocking — single source of truth; ~3 min)*
- [ ] **Securely wipe the local private key**: `rm -P minisign-priv.key` (macOS overwrites then deletes). Keep ONLY the 1Password copy + the GH Actions secret copy. *(blocking, ~30 sec)*

---

## 3. GPG signing (Linux)

> **Blocking for Linux releases** — `.deb`/`.rpm`/`.AppImage` ship with GPG detached signatures. Estimated total: ~20 min.
> Source: `scripts/release/linux-README.md` + `reports/ci-pipeline/secrets.md` §4.

- [ ] **Generate or pick a GPG key** for vSkill releases. New key: `gpg --full-generate-key` → ed25519 → 2y expiry → `vSkill Releases <releases@verified-skill.com>`. *(blocking, ~5 min)*
- [ ] **Capture the fingerprint**: `gpg --list-secret-keys --with-fingerprint --with-colons | awk -F: '/^fpr:/ { print $10; exit }'`. *(blocking, ~30 sec)*
- [ ] **Export public key** to `~/.certs/vskill-pgp-key.asc`: `gpg --armor --export <FINGERPRINT> > ~/.certs/vskill-pgp-key.asc`. *(blocking, ~30 sec)*
- [ ] **Publish public key** at `https://verified-skill.com/.well-known/pgp-key.asc` (commit to vskill-platform `public/.well-known/pgp-key.asc`, push, deploy). Required by Linux verification flow. *(blocking, ~5 min)*
- [ ] **Update `scripts/release/linux-README.md`** §"Verify the GPG signature" to fill in the real fingerprint where it currently says `<TBD — pending GPG key generation>`. *(blocking, ~1 min)*
- [ ] **Submit public key to keys.openpgp.org** (mirror) so users can `--recv-keys`. *(nice-to-have, ~3 min)*

---

## 4. Cloudflare R2 (manifest hosting)

> **Blocking** — `verified-skill.com/desktop/latest.json` is the auto-updater manifest endpoint. Without it the Tauri updater cannot find new versions. Estimated total: ~20 min.
> Source: `reports/ci-pipeline/secrets.md` §5.

- [ ] **Create R2 bucket `vskill-desktop`** at Cloudflare dashboard → R2 → Create bucket. Region: auto. *(blocking, ~2 min)*
- [ ] **Add custom domain mapping** so `verified-skill.com/desktop` serves the bucket. Cloudflare dashboard → R2 → bucket → Settings → Custom Domains → Connect domain → `verified-skill.com/desktop`. Verify TLS cert provisions (~1 min after add). *(blocking, ~5 min)*
- [ ] **Get `CLOUDFLARE_R2_ACCOUNT_ID`** from Cloudflare dashboard → R2 → top-right Account ID. *(blocking, ~30 sec)*
- [ ] **Create R2 API token** at R2 → Manage R2 API Tokens → "Create API token". Permissions: Object Read & Write. Specify bucket: `vskill-desktop` (NOT account-wide). Copy `Access Key ID` + `Secret Access Key` immediately (Secret shown ONCE). *(blocking, ~3 min)*
- [ ] **Verify the manifest endpoint resolves** AFTER first release: `curl -fsSL https://verified-skill.com/desktop/latest.json | jq .` should return JSON. (Safe to skip until rc1.) *(verification, ~30 sec)*

---

## 5. GitHub Secrets (vskill repo only)

> **Blocking** — every release workflow reads these. Set on `anton-abyzov/vskill` repo only; never org-wide. Estimated total: ~15 min after all sources are in hand.
> Source: `reports/ci-pipeline/secrets.md` (definitive list).

For each secret use:
```bash
gh secret set <NAME> --body "<value>" --repo anton-abyzov/vskill
# or for file inputs:
gh secret set <NAME> < /path/to/file --repo anton-abyzov/vskill
```

For .p12 / .p8 / minisign / GPG file values, base64-encode first:
```bash
base64 -i <file> | tr -d '\n' | pbcopy   # macOS
```

### Apple — codesigning (macOS)
- [ ] `APPLE_CERTIFICATE` — `base64 -i ~/.certs/vskill-developer-id.p12 | tr -d '\n' | pbcopy` *(blocking, ~30 sec)*
- [ ] `APPLE_CERTIFICATE_PASSWORD` — the password set during .p12 export *(blocking, ~30 sec)*
- [ ] `APPLE_SIGNING_IDENTITY` — output of `security find-identity -v -p codesigning | grep "Developer ID Application"` (full string) *(blocking, ~1 min)*
- [ ] `APPLE_ID` — `anton.abyzov@gmail.com` (Apple Developer account email) *(blocking, ~30 sec)*
- [ ] `APPLE_APP_SPECIFIC_PASSWORD` — generated at appleid.apple.com (see §1) *(nice-to-have, ~30 sec)*
- [ ] `APPLE_TEAM_ID` — 10-char from developer.apple.com Membership *(blocking, ~30 sec)*

### Apple — notarytool (preferred over app-specific password)
- [ ] `ASC_KEY_ID` — `JZ2ML9M66A` (already-existing key) *(blocking, ~30 sec)*
- [ ] `ASC_ISSUER_ID` — `a9be87c1-47d8-40f2-897d-75df80a540fb` *(blocking, ~30 sec)*
- [ ] `ASC_PRIVATE_KEY_BASE64` — `base64 -i ~/.private_keys/AuthKey_JZ2ML9M66A.p8 | tr -d '\n' | pbcopy` *(blocking, ~30 sec)*

> Verify locally first: `xcrun notarytool history --key ~/.private_keys/AuthKey_JZ2ML9M66A.p8 --key-id JZ2ML9M66A --issuer a9be87c1-47d8-40f2-897d-75df80a540fb`

### Tauri Updater — minisign
- [ ] `TAURI_SIGNING_PRIVATE_KEY` — `base64 -i minisign-priv.key | tr -d '\n' | pbcopy` *(blocking, ~30 sec)*
- [ ] `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` — passphrase set during `generate-minisign-key.sh` *(blocking, ~30 sec)*

### Linux — GPG
- [ ] `GPG_PRIVATE_KEY` — `gpg --armor --export-secret-keys <FINGERPRINT> | pbcopy` *(blocking, ~30 sec)*
- [ ] `GPG_KEY_FPR` — fingerprint string from §3 *(blocking, ~30 sec)*

### Cloudflare R2
- [ ] `CLOUDFLARE_R2_ACCOUNT_ID` — from Cloudflare dashboard *(blocking, ~30 sec)*
- [ ] `CLOUDFLARE_R2_ACCESS_KEY_ID` — from R2 API token *(blocking, ~30 sec)*
- [ ] `CLOUDFLARE_R2_SECRET_ACCESS_KEY` — from R2 API token (one-time display) *(blocking, ~30 sec)*

### Homebrew Cask bump (staging tap)
- [ ] `HOMEBREW_BUMP_PAT` — Fine-grained PAT at GitHub → Settings → Developer settings → PATs → Fine-grained. Repo: `antonabyzov/homebrew-vskill-staging` (or `anton-abyzov/homebrew-tap-staging`). Permissions: Contents read+write. *(blocking for Homebrew channel, ~3 min)*

### Verification (after all secrets set)
- [ ] Run `gh secret list --repo anton-abyzov/vskill` and confirm 14 secrets present. *(verification, ~30 sec)*

---

## 6. Repository setup

> Required infrastructure before first release. Estimated total: ~30 min.

- [ ] **Create staging Homebrew tap repo** `github.com/anton-abyzov/homebrew-tap-staging` (or `antonabyzov/homebrew-vskill-staging` — match `HOMEBREW_BUMP_PAT` scope). Empty repo, default branch `main`. *(blocking for Homebrew, ~3 min)*
- [ ] **Configure CODEOWNERS** at `repositories/anton-abyzov/vskill/.github/CODEOWNERS`. At minimum `* @anton-abyzov`. *(nice-to-have, ~3 min)*
- [ ] **Configure branch protection on `main`** at github.com/anton-abyzov/vskill → Settings → Branches → Add rule. Require status checks: `desktop-release` matrix passing, no force-push. *(nice-to-have, ~5 min)*
- [ ] **Provision `press@verified-skill.com` email alias** in domain DNS (forwards to `anton.abyzov@gmail.com`). Flagged in spec OQ-A5. *(nice-to-have, ~5 min)*

---

## 7. Marketing assets

> Required before public launch. Estimated total: ~2–4 hours of creative work.
> Source: `marketing-drafts/README.md` §"Open questions" + spec OQ-A4..A9.

- [ ] **Render OG images to PNG** from the existing SVG sources at `repositories/anton-abyzov/vskill-platform/public/og/`. Currently 4 SVGs (`default.svg`, `desktop.svg`, `ai-studio.svg`, `skill-studio.svg`); social previews need PNG. Use Remotion or similar — instructions in `vskill-platform/public/og/README.md`. Output: same names with `.png`. *(blocking for ProductHunt + HN preview cards, ~30 min)*
- [ ] **Write founder bio** for `/press` (~150 words). Replace 2-line generic placeholder in `repositories/anton-abyzov/vskill-platform/src/app/press/page.tsx`. *(blocking for press kit, ~30 min)*
- [ ] **Provide 512×512 founder portrait** (square crop). Save to `vskill-platform/public/press/founder-portrait@2x.png`. *(blocking for press kit, ~10 min if photo exists)*
- [ ] **Capture 4 product screenshots** of the desktop app: home, eval/run view, settings, post-eval result. Use 0828 testing reports as source. Each at `@2x.png` (Retina). Save to `vskill-platform/public/press/`. *(blocking for press kit, ~30 min)*
- [ ] **Generate `/press/vskill-press-kit.zip`** containing: founder bio (.txt), portrait (.png), 4 screenshots, OG images, fact-sheet (one-pager). Host at `verified-skill.com/press/vskill-press-kit.zip`. *(blocking for media outreach, ~30 min)*

---

## 8. Marketing posts (drafts ready, NOT POSTED)

> All 7 drafts already exist at `.specweave/increments/0829-vskill-distribution-and-marketing/marketing-drafts/`. **You pick the launch date.** Estimated total: 1–2 hours review + posting day-of.
> Source: `marketing-drafts/README.md` §"Sequencing recommendation".

- [ ] **Pick launch date** — Tuesday recommended for ProductHunt (12:01 AM PT). HN Show HN best Tue/Wed 8:30–10:00 AM ET. *(blocking, ~5 min)*
- [ ] **Review/customize `product-hunt.md`** — verify tagline, gallery images, maker comment. *(blocking, ~15 min)*
- [ ] **Review/customize `hacker-news.md`** — Show HN format, opening line, links. *(blocking, ~10 min)*
- [ ] **Review/customize `reddit-claude.md`** — context-fit for r/ClaudeAI norms. *(blocking, ~10 min)*
- [ ] **Review/customize `reddit-localllama.md`** — relevance to LLM-runner audience. *(blocking, ~10 min)*
- [ ] **Review/customize `dev-to-article.md`** — deep-dive technical post. *(blocking, ~15 min)*
- [ ] **Review/customize `twitter-thread.md`** — 5–10 tweet thread. *(blocking, ~10 min)*
- [ ] **Review `awesome-lists.md`** — list of awesome-* PRs to open. Tier 1 (week of launch), Tier 2 (week +1). *(blocking, ~5 min)*

### Posting sequence (day-of)
- [ ] **09:00 ET** — Submit Show HN
- [ ] **12:01 AM PT** (or your timezone-equivalent maker-awake window) — ProductHunt launch
- [ ] **10:00 ET** — Twitter thread
- [ ] **14:00 ET** — dev.to deep-dive
- [ ] **17:00 ET** — r/ClaudeAI
- [ ] **Day +1** — Reply backlog in HN/PH/dev.to + Tier 1 awesome-list PRs
- [ ] **Day +2 (Sat/Sun afternoon)** — r/LocalLLaMA
- [ ] **Day +3** — Tier 2 awesome-list PRs

> **Constraints from architect's brief**: NO astroturfing, NO vote rings, NO paid hunters, NO keyword-stuffing. Natural founder voice only.

---

## First-release rc1 runbook

> Once §1–§5 are complete, this is the minimum-viable-test that everything is wired correctly. ~1–2 hours including CI wait time.

### Step 1 — local credential dry-run (no upload)
```bash
cd repositories/anton-abyzov/vskill
DRY_RUN=1 bash scripts/release/publish-manifest.sh 0.0.0 ./fake-artifacts/
```
Expected: prints credential checks + the exact upload commands without contacting R2 or Apple. If anything errors, fix that secret before tagging.

### Step 2 — local notarize dry-run (macOS)
```bash
xcrun notarytool history \
  --key ~/.private_keys/AuthKey_JZ2ML9M66A.p8 \
  --key-id JZ2ML9M66A \
  --issuer a9be87c1-47d8-40f2-897d-75df80a540fb
```
Expected: lists previous submissions (or empty list if first time). If permission error, ASC API key needs Admin role.

### Step 3 — tag a release-candidate
```bash
git tag desktop-v0.0.1-rc1
git push origin desktop-v0.0.1-rc1
gh run watch
```
Expected: matrix job kicks off — `macos-14`, `windows-2022`, `ubuntu-22.04` build in parallel. Total ~25–35 min.

### Step 4 — verify outputs
```bash
# Manifest reachable + correct cache headers
curl -fsSL https://verified-skill.com/desktop/latest.json | jq .
curl -fsSL https://verified-skill.com/desktop/latest.json -I | grep -i cache-control

# Artifacts downloadable
curl -fsSL -o /tmp/test.dmg https://verified-skill.com/desktop/v0.0.1-rc1/vSkill_0.0.1-rc1_universal.dmg
shasum -a 256 /tmp/test.dmg
```

### Step 5 — smoke-test artifacts on real devices
- [ ] **macOS**: download .dmg, open, drag-to-Applications, launch. Verify Gatekeeper says "accepted" (not blocked).
  ```bash
  spctl -a -t exec -vv /Applications/vSkill.app
  # expect: "accepted, source=Notarized Developer ID"
  ```
- [ ] **Windows** (need a Win11 box or VM): download .msi, verify SHA256 matches published, install via right-click → Properties → Unblock → install. Confirm Start Menu entry + `vskill://` registry key (`Get-ItemProperty "HKCU:\Software\Classes\vskill"`).
- [ ] **Linux** (Ubuntu 22.04+ or Fedora 40+): download .AppImage + `.asc`, verify GPG signature, run.
  ```bash
  curl -fsSL https://verified-skill.com/.well-known/pgp-key.asc | gpg --import
  gpg --verify SHA256SUMS.asc SHA256SUMS
  sha256sum -c SHA256SUMS
  chmod +x vSkill_*.AppImage && ./vSkill_*.AppImage
  ```

### Step 6 — promote to v0.1.0 when green
```bash
git tag desktop-v0.1.0
git push origin desktop-v0.1.0
gh run watch
```
This is the version users will see in ProductHunt / HN / press.

---

## Bundle suggestions (for batching the work)

If you want to do this in two sit-downs instead of piecemeal:

**Sit-down 1 — "Apple + Tauri + Wipe" (1.5 hrs)**: §1 (Apple cert) → §2 (Tauri minisign) → secure-wipe local copies → 1Password backup.

**Sit-down 2 — "GPG + R2 + Secrets + Repo" (1.5 hrs)**: §3 (GPG) → §4 (R2 + custom domain) → §5 (paste all 14 GH Secrets in one shot from a `secrets.env` scratch file you `rm -P` after) → §6 (staging tap repo + branch protection).

**Sit-down 3 — "Marketing prep" (2–4 hrs, separate day)**: §7 (assets) → §8 review (drafts).

**Sit-down 4 — "Launch day"**: tag rc1 → smoke-test → tag v0.1.0 → post sequence.

---

## Bundle: skipping channels

You can ship without:
- **Linux GPG** → drop §3, §5 GPG_*, ship .deb/.rpm/.AppImage unsigned (Linux users will see verification failure but can override).
- **Homebrew** → drop §6 staging tap + §5 HOMEBREW_BUMP_PAT. Brew cask is post-v1 anyway.
- **press@ alias** → drop §6 last item; use `anton.abyzov@gmail.com` in press kit.

Cannot ship without:
- §1 Apple cert, §2 Tauri minisign, §4 R2 — these are baked into the binary or the URL contract.
