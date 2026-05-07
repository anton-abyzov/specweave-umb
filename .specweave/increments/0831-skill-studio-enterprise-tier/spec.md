---
increment: 0831-skill-studio-enterprise-tier
title: "Skill Studio enterprise tier — GitHub OAuth + smart folder picker + private repo support + 50-skill free-tier"
type: feature
priority: P0
status: planned
created: 2026-05-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio enterprise tier — GitHub OAuth + smart folder picker + private repo support + 50-skill free-tier

## Overview

Skill Studio v1.0.13 just shipped as a signed macOS desktop app with working auto-update — that's the distribution win. This increment adds the **monetization seam**: a GitHub-based identity layer, project/repo awareness in the UI, and the tier gate that converts free users into paying customers.

The flow is: user signs in with GitHub via device-flow (no client secret in the binary), opens a project folder (the picker disambiguates personal-scope `~/.claude/skills/` from project roots so the sidebar doesn't conflate global skills with project skills), sees the connected GitHub repo visualized in the sidebar (name, branch, public/private badge, sync state), and bumps into the 50-skill free-tier ceiling — at which point a paywall offers Pro for unlimited skills + private-repo connections via the existing GitHub App install. The vskill-platform side exposes a `/api/v1/billing/quota` endpoint and a "Coming Soon" pricing page placeholder. No Stripe wiring in v1 — this increment ships the seam, not the checkout.

## Problem Statement

- **No monetization layer.** Skill Studio is fully free with no identity, tier, or quota — there's no way to charge enterprises even though the product is ready for them.
- **Folder picker conflates scopes.** Picking `~` (home directory) shows personal-scope skills (`~/.claude/skills/`) as if they were project skills, which is technically wrong and confusing to users managing both kinds.
- **No repo connection visibility.** Even when a user opens a folder that IS a git repo with a GitHub remote, the studio gives no visual indication that it's connected, what branch is checked out, whether it's public or private, or what the sync state is.
- **Can't gate features by tier.** Without sign-in there's no way to enable private-repo support for paid users while restricting free users to public repos.
- **No upgrade path.** Even if a user wanted to pay for private-repo support today, there's no surface in the app or on verified-skill.com that lets them do so.

## Goals (v1)

1. Ship secure GitHub sign-in via OAuth device-flow (no client secret in the desktop binary).
2. Disambiguate personal-scope vs project-scope in the folder picker; warn before treating `~` as a project root.
3. Visualize connected GitHub repos in the studio sidebar: name, branch, public/private badge, sync state.
4. Track skill count locally and enforce a 50-skill free-tier ceiling with a hard block on the 51st create.
5. Expose `/api/v1/billing/quota` on vskill-platform so the desktop app can verify tier + count without trusting local storage.
6. Wire the existing GitHub App install flow as the durable backend for private-repo access (paid tier only).
7. Show clear, non-nagging tier-aware gates in the UI (private-repo connection blocked with "Upgrade" callout for free).
8. Land a "Coming Soon" pricing page on verified-skill.com so users know Pro/Enterprise are real and inbound.

## Out of Scope (v1)

- **Stripe billing UI / checkout flow.** Pricing page is placeholder-only. Real billing comes in a follow-up increment.
- **Team accounts / org-level subscriptions.** v1 is single-user Pro upgrade. Enterprise multi-seat licensing is deferred.
- **SSO (SAML/OIDC).** Sign-in is GitHub-only in v1.
- **Audit log / activity history.** No admin-facing usage tracking surface in v1.
- **On-prem / self-hosted vskill-platform.** v1 assumes verified-skill.com SaaS as the only backend.
- **Non-GitHub git hosts (GitLab, Bitbucket, Gitea).** v1 only recognizes `github.com` remotes.
- **Bulk skill import / migration.** Grandfathered skills above 50 stay visible but no import-from-disk wizard.

## Inherited Givens

- **Skill Studio v1.0.13** is shipped: signed macOS .dmg, auto-update working, Tauri 2 runtime.
- **Device-flow endpoints** already exist on vskill-platform: `/api/v1/auth/github/device-flow/code` and `/api/v1/auth/github/device-flow/token`.
- **GitHub App** already exists at `vskill-platform/src/app/api/v1/auth/github/installation/`.
- **Tauri shell plugin** (`@tauri-apps/plugin-shell::open`) is available for launching the user's browser to `github.com/login/device`.
- **vskill-platform users table** exists with GitHub identity columns (from increment 0233).
- **Increment 0702 KeyStore module** provides cross-platform secure storage (macOS Keychain).
- **verified-skill.com** is live (Next.js 15, Cloudflare Workers) with marketing pages.

## Personas

- **P-1 — Free Hobbyist (Maria).** Indie dev exploring skill authoring. Public repos only. Manages ~10–30 skills across a couple of side projects. Cap of 50 is "more than I'll ever need" and she's the long-tail evangelist who tweets about Skill Studio. Never signs up for paid.
- **P-2 — Pro Indie (Devon).** Solo consultant building skills for client work in private GitHub repos. Hits the 50 cap within weeks. Will pay $X/month for unlimited skills + private-repo connections. Buys via verified-skill.com once Stripe is wired.
- **P-3 — Enterprise Admin (Priya).** Engineering manager at a 50-person team that wants standardized skills across private monorepos. Needs centralized billing, per-seat licensing, and SOC2-grade auditability. Reads the pricing page in v1 and books a sales call; full enterprise tier ships in a later increment.

## User Stories

### US-001: Sign in with GitHub via device flow (P0)
**Project**: vskill

**As a** Skill Studio user
**I want** to sign in with my GitHub account using the device-flow code
**So that** I can be identified by Skill Studio without exposing OAuth client secrets in the desktop binary

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Sign-in button in the studio menu/sidebar opens a "Sign in with GitHub" panel showing an 8-character user code and a copy-to-clipboard control.
- [ ] **AC-US1-02**: Clicking "Open GitHub" launches the user's default browser to `https://github.com/login/device` via the Tauri shell plugin (no embedded webview, no client secret in the binary).
- [ ] **AC-US1-03**: The studio polls `/api/v1/auth/github/device-flow/token` at the cadence returned by GitHub (typically 5s) and stops on success, denial, or expiry.
- [ ] **AC-US1-04**: On successful authorization, the access token is stored in the OS keychain via the 0702 KeyStore (never written to plain settings.json or logs).
- [ ] **AC-US1-05**: After sign-in the sidebar shows the user's GitHub avatar + login + tier badge (Free / Pro), pulled from `/api/v1/billing/quota`.
- [ ] **AC-US1-06**: If device-flow polling fails (network, denial, expiry), an inline error message is shown with a "Try again" button — the studio never crashes or hangs.

---

### US-002: Sign out and revoke token (P0)
**Project**: vskill

**As a** signed-in Skill Studio user
**I want** to sign out and have my access token revoked
**So that** my GitHub credentials are not left on disk after I'm done

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A "Sign out" control is available from the user-menu in the studio sidebar after sign-in.
- [ ] **AC-US2-02**: Sign-out calls GitHub's token revocation endpoint and on success removes the token from the OS keychain.
- [ ] **AC-US2-03**: Sign-out clears any cached repo metadata (connected-repo widget reverts to "Sign in to connect").
- [ ] **AC-US2-04**: If revocation fails (offline / GitHub 5xx), the local token is still removed and a toast informs the user "Local sign-out complete; remote revocation will retry on next launch".
- [ ] **AC-US2-05**: After sign-out, all tier-gated features visibly revert to free-tier state (private-repo connections become locked, paywall behaviour returns).

---

### US-003: Smart folder picker with home-directory disambiguation (P0)
**Project**: vskill

**As a** Skill Studio user
**I want** the folder picker to recognize when I've selected my home directory and warn me
**So that** my personal-scope skills don't get confused with project-scope skills

**Acceptance Criteria**:
- [ ] **AC-US3-01**: The "Open project folder" picker shows a modal warning when the selected path resolves to the OS home directory (`os.homedir()`): _"This is your home directory — Skill Studio shows personal skills here. Pick a specific project subfolder instead."_
- [ ] **AC-US3-02**: The warning modal offers two actions: **"Pick again"** (reopens the picker) and **"Use home anyway"** (proceeds with the home dir as the root, with a persistent banner inside the studio noting "Personal scope").
- [ ] **AC-US3-03**: If the picked folder is `~/.claude/skills/`, `~/.claude/agents/skills/`, or any path under `~/.claude/`, the studio treats it as **personal-scope** and labels it as such in the sidebar (no project-connect attempt).
- [ ] **AC-US3-04**: For any other folder, the studio treats it as a **project root** and runs git-remote detection (US-004).
- [ ] **AC-US3-05**: The picker remembers the last 5 picked folders and surfaces them as "Recent" without the home-dir warning re-firing for already-confirmed paths.
- [ ] **AC-US3-06**: Picking a non-existent path or a file (not a directory) shows an inline error and does not enter the studio's project state.

---

### US-004: Connected-repo sidebar widget (P0)
**Project**: vskill

**As a** signed-in Skill Studio user with a project folder open
**I want** the sidebar to visualize the GitHub repo my project is connected to
**So that** I always know which repo my skill changes will go to

**Acceptance Criteria**:
- [ ] **AC-US4-01**: When a project folder contains a `.git/` directory and `git remote get-url origin` returns a `github.com` URL, the sidebar widget shows: repo name (`owner/repo`), current branch, and a status icon.
- [ ] **AC-US4-02**: A **lock icon** is shown when the repo is private (visibility determined via the GitHub API using the signed-in user's OAuth scope).
- [ ] **AC-US4-03**: A **green check** is shown when the repo is public AND found in the verified-skill.com registry; a neutral icon otherwise.
- [ ] **AC-US4-04**: The widget shows sync state derived from `git status` and `git rev-list`: one of "up to date with origin/{branch}", "{N} commits ahead", "{N} commits behind", "{N} ahead, {M} behind", "uncommitted changes", "no upstream".
- [ ] **AC-US4-05**: If the folder is git but has no remote, the widget shows "Local-only (no remote)". If the remote is non-GitHub, it shows "External git ({host})" with no lock/check badges.
- [ ] **AC-US4-06**: If the folder is not a git repo at all, the widget shows "Not a git project" with a helpful "Initialize git" link (opens documentation, no auto-init in v1).
- [ ] **AC-US4-07**: The widget refreshes on file-system change events (debounced) and on a manual "Refresh" button click — no continuous polling.

---

### US-005: Free-tier 50-skill counter and paywall on 51st create (P0)
**Project**: vskill

**As a** free-tier Skill Studio user
**I want** to be informed when I'm approaching the 50-skill limit and blocked at 51 with a clear upgrade path
**So that** I can either stay within the free tier intentionally or upgrade to Pro

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A skill counter is visible in the studio's status bar showing `{used}/{limit}` (e.g. `47/50`) for free-tier users; signed-in Pro users see `Unlimited` (no number).
- [ ] **AC-US5-02**: At skill counts 45–50, the counter color shifts to a warning state (yellow) with hover text "Approaching free-tier limit".
- [ ] **AC-US5-03**: Attempting to create the 51st skill opens a paywall modal: "You've reached the 50-skill free tier. Upgrade to Skill Studio Pro for unlimited skills + private repo support." with **"Upgrade"** (opens verified-skill.com pricing page in browser) and **"Maybe later"** (closes modal) actions.
- [ ] **AC-US5-04**: The 51st skill create operation is **hard-blocked** for free users — no skill file is written, no skill registry entry created, until the user is on Pro.
- [ ] **AC-US5-05**: Existing skills above the limit (grandfathered users from before this increment) remain visible and editable; only NEW creates are blocked.
- [ ] **AC-US5-06**: The counter is a sum of: skills under all opened project roots + skills in the personal-scope `~/.claude/skills/` tree, deduplicated by skill identity (`name@version` per the existing skill manifest).
- [ ] **AC-US5-07**: Counter is computed locally (no per-create API call) and reconciled with `/api/v1/billing/quota` periodically (cadence to be specified by the architect).

---

### US-006: Billing quota endpoint on vskill-platform (P0)
**Project**: vskill-platform

**As the** Skill Studio desktop app
**I want** a `/api/v1/billing/quota` endpoint on vskill-platform
**So that** I can verify the signed-in user's tier and authoritative skill count without trusting local-only state

**Acceptance Criteria**:
- [ ] **AC-US6-01**: `GET /api/v1/billing/quota` requires an authenticated GitHub OAuth bearer token and returns `{ tier: "free"|"pro"|"enterprise", skillCount: number, skillLimit: number|null, gracePeriodDaysRemaining: number }`.
- [ ] **AC-US6-02**: For free tier, `skillLimit` is `50`; for pro/enterprise, `skillLimit` is `null` (unlimited).
- [ ] **AC-US6-03**: The endpoint accepts an optional `POST` with `{ skillCount: number }` so the desktop app can push its locally-computed count for server-side reconciliation; the server records the latest reported count per user.
- [ ] **AC-US6-04**: 401 response for missing/invalid token; 429 with `Retry-After` header on rate-limit (rate-limit policy specified by architect).
- [ ] **AC-US6-05**: Endpoint is documented in vskill-platform OpenAPI spec and has integration tests covering all four tiers (anonymous, free, pro, enterprise).
- [ ] **AC-US6-06**: Response includes a `serverNow` ISO timestamp the desktop app can use as the basis for offline grace-period accounting.

---

### US-007: GitHub App install flow for private repos (P1)
**Project**: vskill

**As a** Pro-tier Skill Studio user
**I want** to install the verified-skill GitHub App on my private repos
**So that** Skill Studio can read and write skills in those repos

**Acceptance Criteria**:
- [ ] **AC-US7-01**: When a Pro-tier user opens a folder whose `git remote` is a private GitHub repo and the verified-skill GitHub App is NOT installed on it, the connected-repo widget shows an "Install GitHub App" CTA.
- [ ] **AC-US7-02**: Clicking the CTA launches the user's browser to the GitHub App install URL (`https://github.com/apps/verified-skill/installations/new` with a state token); no embedded webview.
- [ ] **AC-US7-03**: After install, the platform's `/api/v1/auth/github/installation/` callback completes the link and the studio detects the new installation on next refresh (or via a deep-link callback if the user returns to the app).
- [ ] **AC-US7-04**: Post-install the connected-repo widget shows the lock icon + "GitHub App connected" badge and unlocks read/write skill operations on that repo.
- [ ] **AC-US7-05**: Free-tier users attempting to access a private repo see a tier gate (per US-008), not the install CTA.
- [ ] **AC-US7-06**: Uninstall on github.com is detected on the next quota sync; the studio reverts the repo to "Install GitHub App" state.

---

### US-008: Tier-aware feature gates in the studio (P0)
**Project**: vskill

**As a** Skill Studio user
**I want** the UI to clearly indicate which features are tier-gated and offer an upgrade path
**So that** I understand why something isn't working without feeling tricked or nagged

**Acceptance Criteria**:
- [ ] **AC-US8-01**: When a free-tier user opens a folder whose remote is a private GitHub repo, the connected-repo widget shows a locked state with **"Private repos are a Pro feature"** and an **"Upgrade"** button (no install CTA).
- [ ] **AC-US8-02**: Tier gates are non-modal — they appear inline in the affected widget, not as full-screen interrupts (the only modal interrupt is the 51st-skill paywall in US-005).
- [ ] **AC-US8-03**: The "Upgrade" buttons across the studio all link to the same canonical pricing URL on verified-skill.com (single source of truth).
- [ ] **AC-US8-04**: Anonymous (signed-out) users attempting any tier-gated action are first prompted to sign in; the gate logic only applies after sign-in.
- [ ] **AC-US8-05**: A `tierFeatures` lookup defines which capabilities require which tier; the UI components consume that lookup so adding/changing gates in the future is a single-file change.
- [ ] **AC-US8-06**: All tier-gate copy is reviewed for non-nagging tone — no dark patterns, no countdown timers, no "act now" pressure.

---

### US-009: Pricing page placeholder on verified-skill.com (P1)
**Project**: vskill-platform

**As a** Skill Studio user clicking "Upgrade"
**I want** to land on a pricing page that explains Pro and Enterprise tiers
**So that** I understand what I'd be buying — even if checkout isn't live yet

**Acceptance Criteria**:
- [ ] **AC-US9-01**: A `/pricing` page exists on verified-skill.com showing three columns: Free, Pro, Enterprise, with feature comparison rows including (skills cap, public repos, private repos, GitHub App install, support tier).
- [ ] **AC-US9-02**: The Pro and Enterprise CTAs read **"Coming Soon — Notify me"** and submit an email to a waitlist (existing email-collection endpoint or a new minimal one).
- [ ] **AC-US9-03**: Page has metadata for SEO (title, description, OG image) and is linked from the verified-skill.com main nav.
- [ ] **AC-US9-04**: The page renders without JavaScript (server-rendered) so it's indexable and works for users with JS disabled.
- [ ] **AC-US9-05**: A "Manage subscription" link is present but disabled with "Available once billing launches" — placeholder route exists at `/account/subscription`.

---

### US-010: Local quota check with offline grace period (P1)
**Project**: vskill

**As a** signed-in Skill Studio user
**I want** the app to keep working when I'm offline for short periods without nagging me
**So that** I don't lose productivity on a flaky connection or during travel

**Acceptance Criteria**:
- [ ] **AC-US10-01**: After sign-in the studio caches the latest `/api/v1/billing/quota` response with a `cachedAt` timestamp.
- [ ] **AC-US10-02**: On startup the studio uses the cached tier+limit if a quota sync has happened in the last 7 days; older than 7 days, the studio prompts the user to "Reconnect to refresh your subscription".
- [ ] **AC-US10-03**: Within the 7-day grace period, free-tier users still get hard-blocked at the 51st skill; Pro users still get unlimited — tier is enforced from cache.
- [ ] **AC-US10-04**: A successful quota sync resets the 7-day grace clock.
- [ ] **AC-US10-05**: The studio attempts a quota sync on app launch, after sign-in, after sign-out, and on a periodic background timer (cadence specified by the architect).
- [ ] **AC-US10-06**: Quota syncs are silent on success and produce a single non-intrusive toast on failure; failures do not block the user from working within their cached tier.

## Glossary

- **device-flow** — OAuth 2.0 Device Authorization Grant (RFC 8628). The user enters an 8-character code at `github.com/login/device` to authorize a desktop app without the app holding a client secret.
- **free-tier** — Anonymous or signed-in users with `tier: "free"`. Capped at 50 skills, public repos only, no GitHub App install.
- **paid-tier** — Signed-in users with `tier: "pro"` or `tier: "enterprise"`. Unlimited skills, private repo support, GitHub App install.
- **connected-repo** — A project folder where `.git/` exists, `git remote get-url origin` returns a `github.com` URL, and (for private repos) the verified-skill GitHub App is installed.
- **personal-scope** — Skills stored under the user's home directory (typically `~/.claude/skills/` and siblings); shared across all projects on this machine.
- **project-scope** — Skills stored inside a project folder, version-controlled with the project's git repo.
- **github-app** — The verified-skill GitHub App (already deployed) that grants Skill Studio durable read/write access to repos the user installs it on. Used for private-repo support on the paid tier.
- **oauth-scopes** — For device-flow sign-in, free-tier requests `read:user` + `public_repo`; paid-tier private-repo access uses GitHub App installation tokens (not extra OAuth scopes).

## Open Questions (for architect)

1. **Token storage location.** OS keychain via the 0702 KeyStore module is the strong default. Confirm the 0702 KeyStore exposes a Tauri-compatible interface and define the key namespace (e.g. `vskill.github.access_token`).
2. **Periodic quota sync cadence.** What's the right cadence for background sync to `/api/v1/billing/quota`? Options: every app-launch only / 1h while the studio is running / on each skill-create. Trade-off is server load vs accuracy of the count.
3. **Offline grace-period mechanic.** 7 days is the proposed window. Is the timer based on `cachedAt` or `serverNow` from the last sync? How is clock-skew handled if the user's machine clock is wrong?
4. **Paywall double-check.** Should the 51st-skill paywall do a synchronous quota sync before blocking (to handle "user just upgraded but cache is stale") or always block on cached state and rely on the user manually refreshing? Recommend the architect choose based on UX research.
