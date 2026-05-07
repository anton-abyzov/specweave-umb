# vSkill Desktop — Next 30 Days

> Companion to LAUNCH_CHECKLIST.md. Maps the punch list onto a calendar.

---

## Day 0 — Internal rc1 (unsigned, fastest feedback)

**Goal**: prove the build matrix works end-to-end without waiting on Apple Developer cert turnaround.

- Tag `desktop-v0.0.1-rc1` with current `tauri.conf.json` (placeholder cert OK — macOS job will build unsigned + skip notarize for this dry-run).
- Watch GH Actions matrix (~30 min).
- Distribute the unsigned macOS .app + Windows .msi + Linux .AppImage to 3–5 internal testers via Drive / Slack / direct.
- Collect: install friction, app launch time, sidecar boot time, any crashes.
- **Output**: list of bugs to fix before signed rc2.

> **Note**: The CI matrix will fail-fast on macOS notarize because cert + secrets aren't set yet. That's expected — the .app artifact still gets built and uploaded as a build artifact in Actions. Pull from there.

---

## Day 1–3 — Setup blockers (Apple + R2 + GPG)

**Goal**: complete LAUNCH_CHECKLIST §1–§5.

- **Day 1 (1.5 hrs)**: Sit-down 1 — Apple Developer ID cert + Tauri minisign keypair + 1Password backup + secure-wipe local copies.
- **Day 2 (1.5 hrs)**: Sit-down 2 — GPG keypair + Cloudflare R2 bucket + custom domain + GitHub Secrets propagation + staging Homebrew tap repo.
- **Day 3 (1 hr)**: tag `desktop-v0.0.2-rc2` (signed). Watch matrix complete. Smoke-test signed artifacts on real macOS / Windows / Linux boxes.
- **Output**: signed, notarized, verifiable releases on all 3 platforms.

---

## Day 4–7 — Marketing asset prep

**Goal**: complete LAUNCH_CHECKLIST §7.

- **Day 4 (~1 hr)**: render OG images (SVG → PNG via Remotion) + push to vskill-platform.
- **Day 5 (~2 hrs)**: write founder bio + capture portrait + 4 product screenshots → press page.
- **Day 6 (~30 min)**: assemble `vskill-press-kit.zip` + provision `press@verified-skill.com`.
- **Day 7 (~1 hr)**: review/customize all 7 marketing drafts (LAUNCH_CHECKLIST §8). Schedule launch date for next Tuesday.
- **Output**: press page live, press kit downloadable, marketing posts ready to ship.

---

## Day 8 — ProductHunt launch (Tuesday)

**Goal**: maximum coverage on the highest-leverage day.

- **12:01 AM PT** — submit ProductHunt post. Maker comment ready.
- **08:30–10:00 AM ET** — Show HN.
- **10:00 ET** — Twitter thread.
- **14:00 ET** — dev.to deep-dive.
- **17:00 ET** — r/ClaudeAI.
- All day — reply to comments fast (HN ranking is very response-time sensitive in first 4 hrs).
- **Output**: launched. Track ProductHunt votes, HN points, dev.to reactions, Twitter engagement.

---

## Day 9 — Reddit (LocalLLaMA window)

**Goal**: reach LLM-runner audience without front-loading channels.

- **Day +1 ET afternoon**: monitor and reply to HN/PH/dev.to backlog. Tier 1 awesome-list PRs (e.g. `awesome-tauri`, `awesome-claude`, etc — see `awesome-lists.md`).
- **Day +2 (Sat/Sun afternoon ET)**: post to r/LocalLLaMA (lower urgency; weekend community is more active).
- **Output**: sustained discussion volume past launch-day spike.

---

## Day 10–11 — Tier 2 awesome-lists + community amplification

**Goal**: long-tail SEO + GitHub-discoverability.

- Open Tier 2 awesome-list PRs.
- Quote-tweet community posts that organically mention vSkill.
- Reply to issue/discussion posts on r/ClaudeAI, r/LocalLLaMA threads.
- Submit to https://github.com/topics with relevant tags (`tauri`, `claude`, `skill-runner`, etc.).

---

## Day 12–30 — Monitor + iterate

**Goal**: convert traffic into installs, stabilize crash-free %, accumulate SmartScreen reputation.

### Metrics to watch (weekly)
- **Crash-free %** (via desktop Sentry or in-app telemetry, if wired).
- **Install conversion**: GitHub Releases download count vs. ProductHunt view-count and HN unique-visitor estimate.
- **R2 egress**: should be flat after launch spike. If spiky, investigate updater poll cadence.
- **SmartScreen reputation**: Windows downloads accumulate trust. After ~1k clean downloads SmartScreen warning typically diminishes.
- **SEO indexing**: search "vSkill Studio AI" on Google — verified-skill.com should be top-3 within 2 weeks.

### Things that might come up
- **macOS notarize stalls** — Apple's queue periodically jams. The release workflow has a 3× retry built in; manual recovery via `xcrun notarytool history` (see `scripts/release/macos-README.md` §Troubleshooting).
- **Windows "this app might be malicious"** — expected for unsigned v1. SmartScreen reputation builds over time. Plan §5.3 + R-D10 accept this trade-off until v1.1+ Authenticode cert.
- **Linux package manager complaints** — `.deb` users running `sudo apt remove vskill` may see post-uninstall residue if user-data folder wasn't deleted. Document in FAQ.
- **Auto-updater rollouts** — first time you ship desktop-v0.1.1, watch the manifest signature verify + percentage-rollout work as expected. If anything's off, you can pull the manifest update via R2 dashboard (atomic swap).

### Decision points around day 21
- **Authenticode signing for Windows** — if SmartScreen friction is causing measurable install drop-off (>20%), prioritize OV/EV cert ($300–700/yr) for v1.1.
- **Snap / Flatpak / distro-repo Linux** — only revisit if Linux install volume is high enough to justify per-distro maintenance.
- **Windows arm64** — only if Win11 arm64 install requests appear.

---

## Risk register (top items, prioritized)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Apple notarize quota throttle in first week | Medium | High (delays release) | Don't notarize per-PR — only on tagged releases. CI matrix already enforces this. |
| Minisign private key leaked | Low | Critical (forced rotation requires shipping a "trampoline" release with old key) | 1Password storage + secure-wipe local copies. Documented rotation runbook in `secrets.md`. |
| R2 custom domain DNS propagation delay | Medium | Blocks updater for 0–24 hrs | Provision Day 2; verify via `curl` before Day 3 rc2. |
| ProductHunt accidentally throttled / shadow-flagged | Low | High (loses launch-day momentum) | No astroturfing, no vote rings — strict per-architect brief. |
| Windows SmartScreen stays loud | Medium | Medium (install drop-off) | Documented bypass in README §1.3. SHA256 + GPG verification path. Authenticode is v1.1+. |

---

## Definition of "launched"

By Day 30, the following should be true:

- [ ] Signed, notarized, verifiable releases live for macOS / Windows / Linux at `verified-skill.com/desktop`.
- [ ] Auto-updater operational; minisign signature verifies on a real install.
- [ ] ProductHunt + HN + Reddit + dev.to + Twitter posts live with sustained reply engagement.
- [ ] Press kit downloadable; press@ alias active.
- [ ] At least one external bloggers / awesome-list / community post not initiated by you.
- [ ] Crash-free % above 95% (or no crashes at all if telemetry not wired).
- [ ] SEO: verified-skill.com ranks top-3 for "vSkill Studio AI".
