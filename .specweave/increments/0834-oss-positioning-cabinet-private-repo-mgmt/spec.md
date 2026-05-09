---
increment: 0834-oss-positioning-cabinet-private-repo-mgmt
title: "Open-source positioning + Account cabinet + Private-repo mgmt parity (web + desktop + npx studio)"
type: feature
priority: P0
status: ready_for_review
created: 2026-05-08
structure: user-stories
test_mode: TDD
coverage_target: 90
projects:
  - vskill
  - vskill-platform
parent: 0833-tier-pricing-pivot
---

# Open-source positioning + Account cabinet + Private-repo management parity

## Overview

This increment delivers three tightly-coupled changes:

1. **Pricing pivot v2 — OSS-first.** Make it unmistakable that the product is **free and open source (MIT)**. Reposition Pro to lead with **"Hosted private skill storage from your private GitHub repos"** — that is the actual paid feature, not a 50-skill cap (already removed in 0833) or anything else. Enterprise stays the support tier (SSO + audit + dedicated support + custom contract). Replace any `*@verified-skill.com` email (the domain has no MX records) with `sales@easychamp.com` (Anton's existing business inbox). All "Talk to sales" CTAs route there.

2. **/account cabinet** — a new authenticated user-settings hub at `verified-skill.com/account`. Vercel-style left sidebar with 7 tabs (Profile, Plan & billing, Connected repositories, Skills, API tokens, Notifications, Danger zone). Single source of truth for user identity, billing, integrations, and destructive account actions.

3. **Private-repo management parity** across all three surfaces:
   - **Web** at `/account` → "Connected repositories" tab.
   - **Tauri desktop app** sidebar → "Connected repositories" panel.
   - **`npx vskill studio` browser tab** → same panel via the shared eval-ui component tree.
   All three are clients of the same platform API (`/api/v1/account/*`). One source of truth, three identical-by-construction renderings.

The increment closes the loop on 0831/0833: the user can now self-serve their account from any surface, sees the same connected-repo list everywhere, and has copy on /pricing that accurately reflects what they're paying for.

## Problem statement

1. **Brand confusion** — /pricing today says "free for public skills" but never names the OSS license or links to the source. New visitors can't tell if this is "freemium SaaS" or "open-source with paid hosting" — those are very different commitments.
2. **Email is broken** — every "Contact sales" / "Get in touch" mailto on the platform points at `*@verified-skill.com`. The domain has **no MX records**. Anyone clicking those links sends mail into a black hole.
3. **No /account page exists** — users have a tier on file but no UI to see it, no way to view connected repos, no API token surface, no danger-zone delete-account. Everything is implicit. Stripe is deferred but the *page itself* should ship.
4. **Connected-repos UX scattered** — 0831 shipped `ConnectedRepoWidget` in the desktop app's sidebar (single repo, single status). There's no list-all-repos view anywhere; no way to disconnect; no parity between web and desktop and `npx vskill studio`.
5. **Untrusted permissions copy** — when a user clicks "Connect GitHub", the only permissions explanation lives on github.com itself. Power users want a pre-flight summary that says **what we'll do** and **what we'll never do** in plain English.

## Goals (v1 — must ship today)

1. **Pricing copy v2** with prominent "Open Source · MIT" badge on Free, "Hosted private skill storage" lead on Pro, sales@easychamp.com on Enterprise mailto.
2. **schema.org JSON-LD** stays correct; meta description updated to reflect OSS positioning.
3. **/account page** with all 7 sidebar tabs functional (some may be minimal v1 — Notifications can be a static "coming soon" message — but the page exists, the routes exist, the tabs render).
4. **/api/v1/account/*** endpoints back the page (profile, connected-repos, tokens, notifications, delete).
5. **Connected-repos table** working in all 3 surfaces (web, Tauri, npx studio) with real data from the same endpoint.
6. **Disconnect flow** working (removes our link, does NOT call GitHub uninstall).
7. **Permissions pre-flight page** (the screen we own before redirecting to github.com/apps/...) with verbatim "what we read / what we'll never do" copy.
8. **Email replacement sweep** — every `*@verified-skill.com` mailto in source code → `sales@easychamp.com` (or removed if not Sales-related).
9. **Top-nav avatar dropdown** with "Sign out" + "Account settings" links (the canonical UX pattern — sign-out is NOT inside /account).
10. **Tests** — Vitest for endpoints + components, Playwright e2e for the /account flow.

## Out of scope (deferred)

- **Stripe payment processing** — Pro CTA stays "Notify me" waitlist (already wired in 0831/0833).
- **API token CLI tooling** — tokens render in the table; tokens work via Bearer auth; CLI helpers ship later.
- **Notifications email backend** — checkbox preferences are stored, but no daily digest job ships in v1 (the /api endpoint and /account UI exist).
- **Per-organization seat licensing** — Enterprise tier feature, not v1.
- **OAuth-app ecosystem** for verified-skill — the GitHub App flow is enough for v1.
- **Soft "fair use" warnings** at very high public-skill counts (no warning ships; revisit if abuse).

## Inherited givens

- 0831 shipped: `User.tier` Prisma column, `/api/v1/billing/quota` endpoint, `requireUserOrGithubBearer` middleware, `useTier()` React hook, `PaywallModal`, `QuotaProvider`, keyring-backed token storage in Tauri.
- 0833 pivoted: free-tier `skillLimit: null`, paywall trigger moved to private-repo connect (not skill create), /pricing copy already has tier scaffolding (just needs OSS badge + email fix + Pro lead-bullet rewrite).
- 0832 shipped: studio process lifecycle (lock files, lifecycle modal) — provides the registry of running studio instances we reference in /account "Active sessions" (deferred sub-feature, not blocking v1).
- ADR-0831-04 (server-authoritative quota) — still valid; account page just reads from the same shape.
- GitHub App `verified-skill` is already provisioned; the install URL is `github.com/apps/verified-skill/installations/new` (need to confirm the actual app slug — agent will resolve).

## Personas

### P-1: OSS-curious developer (the reassurance path)
Lands on /pricing from a HN/Twitter link. Wants to verify "is this actually open source or 'open source-ish'?" Sees the MIT badge, clicks the GitHub source link, confirms the LICENSE file. Buys nothing today — but trusts the product enough to install the desktop app or run `npx vskill studio`.

### P-2: Indie consultant (the conversion path — same as 0833)
Has client work in private GitHub repos. Free tier doesn't help them; they need private-repo connections. Hits the paywall first time they try to connect a private repo. Now sees a /pricing page that clearly explains why Pro exists ("Hosted private skill storage"). Likely converts.

### P-3: Power user managing 8 connected repos (the cabinet path)
Already converted. Has 8 repos connected across personal + employer org. Wants to: see the full list, sync a stale repo, disconnect one that left the org, generate a CLI token. Goes to /account → Connected repositories → does it all in one place. Was using github.com/settings/installations before; now uses our cabinet for the verified-skill-specific actions.

### P-4: Enterprise admin (the contact path)
Looking at /pricing for SSO + audit log. Wants to email sales. Clicks the Enterprise CTA → sales@easychamp.com (working inbox) → conversation begins. Today this email bounces silently — major brand damage we're fixing.

### P-5: Privacy-conscious developer (the disconnect path)
Connected a private repo, decided not to use the product. Wants to disconnect cleanly and confirm nothing got stored. Goes to /account → Connected repositories → row kebab → Disconnect → modal explains "skills already published stay published, but we stop syncing". Confirms. Disconnect succeeds; row disappears; receives a confirmation toast.

## User stories

---

### US-001: OSS-first pricing copy + email fix (P0)
**Project**: vskill-platform

**As a** visitor to verified-skill.com/pricing
**I want** to immediately see this is an open-source product
**So that** I can trust the project's long-term direction and pick the right tier for my needs

**Acceptance Criteria**:
- [x] **AC-US1-01**: Free card has a prominent **"Open Source · MIT"** badge above its title (or in a visible secondary line). Card body bullet 1 reads "Free forever. Self-host or use our public registry." with a link reading "View source on GitHub →" that points at `https://github.com/anton-abyzov/vskill`.
- [x] **AC-US1-02**: Pro card lead bullet rewritten to: "Hosted private skill storage from your private GitHub repos." Sub-bullets: "Connect private repos · sync skills automatically · priority email support". Highlight strip stays "MOST POPULAR — for indie devs + consultants". CTA stays "Notify me" (Stripe deferred).
- [x] **AC-US1-03**: Enterprise card lead bullet stays "+ SSO + audit log + dedicated support". CTA changes from any verified-skill.com mailto to **`mailto:sales@easychamp.com?subject=Skill%20Studio%20Enterprise%20Inquiry`**. CTA label stays "Talk to sales" (matches industry pattern: 7/8 surveyed competitors use this phrasing).
- [x] **AC-US1-04**: SEO meta description updated to: "Skill Studio is open source (MIT). Free for public skills and public repos. Pro adds hosted private skill storage from your private GitHub repos."
- [x] **AC-US1-05**: schema.org SoftwareApplication JSON-LD `offers` array includes `softwareLicense: "MIT"` and `softwareSourceCodeRepositoryUrl: "https://github.com/anton-abyzov/vskill"`. Both Free and Pro `offers.price` stay "0" until Stripe ships (Enterprise omits price → "Contact sales").
- [x] **AC-US1-06**: A new section near the top of /pricing (above the three cards) — "Open Source · MIT" hero strip with three sub-points: "Self-host the desktop app · Self-host the studio runtime · Inspect every line of source." Links to GitHub repo + license file.
- [x] **AC-US1-07**: Vitest snapshot/SSR test asserts each tier card's lead bullet, license badge, mailto target, and meta description.

---

### US-002: Email substitution sweep (P0)
**Project**: vskill-platform + vskill

**As a** maintainer
**I want** every `*@verified-skill.com` mailto in source code replaced
**So that** "Contact sales" links don't bounce

**Acceptance Criteria**:
- [x] **AC-US2-01**: `grep -rn "@verified-skill\\.com" repositories/anton-abyzov/{vskill,vskill-platform}/src` returns zero hits in user-facing strings (mailtos, copy, alt text, docs).
- [x] **AC-US2-02**: All such occurrences replaced with `sales@easychamp.com` for sales-related CTAs, removed entirely for placeholder/example uses (no fake addresses left in copy).
- [x] **AC-US2-03**: Test fixtures (`.test.ts` files referencing fake emails) keep their fake `*@example.com` addresses — no churn there.
- [x] **AC-US2-04**: README files in both repos updated to reference sales@easychamp.com for any "Contact" sections.
- [x] **AC-US2-05**: `mailto:` link with `subject=` query string is URL-encoded correctly (no raw spaces). The Enterprise card CTA's `subject` matches exactly: "Skill Studio Enterprise Inquiry".

---

### US-003: /account cabinet shell + sidebar nav (P0)
**Project**: vskill-platform

**As a** signed-in user
**I want** a single place to see my profile, plan, connections, and account actions
**So that** I never have to wonder "where do I change X?"

**Acceptance Criteria**:
- [x] **AC-US3-01**: New page at `verified-skill.com/account` with cookie-auth gate. Anonymous → redirect to `/auth/login?return=/account`. Authenticated → render the cabinet.
- [x] **AC-US3-02**: Page layout: left sidebar (240px desktop, collapsible to top-dropdown on viewport <768px) + right pane.
- [x] **AC-US3-03**: Sidebar has 7 tabs in this exact order: **Profile** · **Plan & billing** · **Connected repositories** · **Skills** · **API tokens** · **Notifications** · **Danger zone**. Active tab has a left-edge accent stripe + bold weight. Each tab is a sub-route: `/account/profile`, `/account/billing`, `/account/repos`, `/account/skills`, `/account/tokens`, `/account/notifications`, `/account/danger`. Default tab is Profile.
- [x] **AC-US3-04**: Persistent header strip (above sidebar+pane) with avatar (24px circle), display name, GitHub handle in tertiary line. Re-renders on every tab — gives users an "anchor".
- [x] **AC-US3-05**: Top-nav avatar dropdown gets two new items: "Account settings" (→ /account/profile) and "Sign out". Sign out clears cookie + redirects to `/`.
- [x] **AC-US3-06**: Empty content slot on `/account` (the index, no sub-route) → redirects to `/account/profile`.
- [x] **AC-US3-07**: Vitest SSR test asserts cookie-gate behaviour, sidebar order, active-tab styling, and avatar-dropdown items.

---

### US-004: /account/profile + /account/billing (P0)
**Project**: vskill-platform

**As a** signed-in user
**I want** to see my GitHub identity and current plan
**So that** I can confirm who I am and what tier I'm on

**Acceptance Criteria**:
- [x] **AC-US4-01**: Profile tab shows: avatar (uploaded from GitHub), display name (editable), GitHub handle (read-only, "Synced from GitHub" caption), public bio (textarea, max 280 chars), "Public profile page" toggle (defaults true).
- [x] **AC-US4-02**: Profile "Save changes" button is disabled when form is pristine; submits to `PATCH /api/v1/account/profile`; on success shows green toast "Profile updated".
- [x] **AC-US4-03**: Plan & billing tab shows current tier as a card at top: tier name (Free/Pro/Enterprise) + green "Active" chip + "What's included" bulleted summary. Below the card: "Upgrade" CTA → routes to /pricing (Stripe deferred).
- [x] **AC-US4-04**: Billing history section: empty state "No invoices yet" for Free users. For Pro/Enterprise: a table with columns Date · Invoice · Amount · Status · Download (download is grey-disabled until Stripe ships, with tooltip "Coming when subscriptions launch").
- [x] **AC-US4-05**: `GET /api/v1/account/profile` returns `{userId, displayName, githubHandle, avatarUrl, bio, publicProfile, tier, createdAt}`. `PATCH /api/v1/account/profile` accepts `{displayName?, bio?, publicProfile?}`. Vitest covers both.

---

### US-005: /account/repos — Connected repositories table (P0)
**Project**: vskill-platform + vskill

**As a** user
**I want** to see every GitHub repo I've connected, with status, and manage them in one place
**So that** I can keep my list clean as projects come and go

**Acceptance Criteria**:
- [x] **AC-US5-01**: New endpoint `GET /api/v1/account/repos` returns a list of `{repoId, ownerLogin, ownerAvatarUrl, repoName, isPrivate, skillsCount, syncStatus: "green"|"amber"|"grey"|"red", lastActivityAt, githubInstallationId}`. Caches 60s in KV. Authenticated.
- [x] **AC-US5-02**: New table component renders rows in this column order: **Repository** (lock icon for private + `owner/name`) · **Skills** (count, `0` shows "—") · **Status** (coloured dot + label "Synced 2m ago" / "Reauth needed" / "Idle" / "Error: <hover>") · **Last activity** (relative time) · **Actions** (kebab menu).
- [x] **AC-US5-03**: Header summary chip above the table: "**N repos connected (P public, Q private)**" with globe icon for public and lock for private. If 0 connected: empty state "No repositories connected yet" with primary CTA "Connect a GitHub repo".
- [x] **AC-US5-04**: Kebab menu has 3 actions: **Open on GitHub** (→ `https://github.com/{owner}/{repo}`), **Resync now** (POST `/api/v1/account/repos/{repoId}/resync` → optimistic spin then refresh), **Disconnect** (opens confirmation modal — see US-006).
- [x] **AC-US5-04b**: "Connect a repository" CTA (button above the table) opens the pre-flight permissions page (see US-007), which then redirects to `github.com/apps/{app-slug}/installations/new`.
- [x] **AC-US5-05**: The desktop Tauri app's sidebar gets a new "Connected repositories" panel that uses the **same React component** as the web table (extracted to `src/eval-ui/src/components/ConnectedReposTable.tsx` and imported by both the platform `/account/repos/page.tsx` and the desktop sidebar). Component is rendering-pure — takes `repos[]` + `onAction` callback as props.
- [x] **AC-US5-06**: `npx vskill studio` browser tab renders the same component when the user is signed in (uses the existing eval-ui shell). Single source of truth: same fetch URL (`{platformBaseUrl}/api/v1/account/repos` — desktop uses verified-skill.com; npx-studio uses verified-skill.com unless env override).
- [x] **AC-US5-07**: Mobile (<640px): table degrades to card-list (each row = one card with label/value pairs). Kebab menu remains accessible.
- [x] **AC-US5-08**: Vitest unit tests for the component cover all 4 status colours, empty state, and kebab interactions. E2E (Playwright) covers the connect → list → resync → disconnect flow against a stubbed API.

---

### US-006: Disconnect flow + confirmation modal (P0)
**Project**: vskill-platform + vskill

**As a** user removing a connected repo
**I want** a clear confirmation that explains what disconnect actually does
**So that** I don't accidentally lose data I cared about

**Acceptance Criteria**:
- [x] **AC-US6-01**: Disconnect kebab action opens modal with title "Disconnect verified-skill from `{owner}/{repo}`?". Body verbatim: "We'll stop syncing this repo's skills. Skills already published to verified-skill stay published. You can reconnect anytime." Two buttons: secondary "Cancel" + danger primary "Disconnect".
- [x] **AC-US6-02**: Confirm calls `DELETE /api/v1/account/repos/{repoId}`. Server removes `ConnectedRepo` row + cancels any in-flight scan jobs. Does **NOT** call GitHub's uninstall API (per Netlify pattern; user uninstalls the App on github.com if they want full removal).
- [x] **AC-US6-03**: On success: row animates out + green toast "Disconnected `{owner}/{repo}`. Existing skills are preserved."
- [x] **AC-US6-04**: On failure (4xx/5xx): modal stays open + red error banner inside modal. User can retry.
- [x] **AC-US6-05**: After disconnect, header summary chip count decrements correctly. Public/private split also recalculates.
- [x] **AC-US6-06**: Test fixtures cover: success path, 404 (repo already gone — treat as success, idempotent), 403 (token expired — show "Reauthenticate then try again"), 5xx (transient — let user retry).

---

### US-007: Pre-flight permissions page + connect flow (P0)
**Project**: vskill-platform

**As a** user clicking "Connect a GitHub repo"
**I want** to see what we'll do with my repo access before I authorize anything
**So that** I trust the integration

**Acceptance Criteria**:
- [x] **AC-US7-01**: New page at `/account/repos/connect` rendered before redirect to github.com. Title: "Connect a GitHub repository". Body has two sections:
- [x] **AC-US7-02**: Section 1 — **"What we'll see in your repos"** with three rows (icon + label + one-line rationale, mirroring Vercel's permission-row style):
   - "Read repository contents" — "to detect installed skills and SKILL.md files."
   - "Read metadata" — "repo names, default branch, language list."
   - "Read pull requests + write commit statuses (optional, only if Skill Validation CI is enabled)" — "so we can post pass/fail checks back to your PRs."
- [x] **AC-US7-03**: Section 2 — **"What we'll never do"** with three rows (red-tinted icon):
   - "Push code to your repos."
   - "Read code outside `.specweave/` and `skills/` directories unless you explicitly opt in."
   - "Share your private code with other accounts or third parties."
- [x] **AC-US7-04**: Primary CTA at bottom: **"Continue to GitHub →"** (large button) → redirects to `https://github.com/apps/{app-slug}/installations/new?state={csrf-token}` with state-cookie verification on callback. Secondary: "Cancel" (back to /account/repos).
- [x] **AC-US7-05**: Callback at `/api/v1/account/repos/github/callback` validates state, fetches installation details from GitHub, persists `ConnectedRepo` rows for each granted repo, redirects to `/account/repos` with success toast.
- [x] **AC-US7-06**: If the user already has installations, the pre-flight page shows a secondary "Add another account" link and retains existing installs.
- [x] **AC-US7-07**: Vitest covers state-token CSRF rejection, callback persistence, and pre-flight render.

---

### US-008: /account/tokens — API tokens (P1)
**Project**: vskill-platform

**As a** developer
**I want** to generate API tokens for CLI / programmatic access
**So that** I can script integrations against verified-skill.com

**Acceptance Criteria**:
- [x] **AC-US8-01**: New `ApiToken` Prisma model: `id`, `userId`, `name`, `tokenHash` (sha256), `tokenPrefix` (first 8 chars, displayed in table), `scopes` (string[] — for now: `"read"`, `"write"`), `lastUsedAt`, `createdAt`, `expiresAt` (default 90 days), `revokedAt`.
- [x] **AC-US8-02**: Endpoints: `GET /api/v1/account/tokens` (list, never returns hash), `POST /api/v1/account/tokens` (create, returns `{plaintext, prefix}` ONCE — only time plaintext is exposed), `DELETE /api/v1/account/tokens/{id}` (revoke).
- [x] **AC-US8-03**: Tokens tab UI: Cloudflare-style table — Name · Scopes · Last used · Created · Actions (Revoke). "Generate new token" button top-right opens modal: name + scopes (checkbox: read/write) + expiry (dropdown: 30/90/365 days/never). Submit shows generated token in a copy-to-clipboard panel with warning "This is the only time you'll see this token. Store it securely."
- [x] **AC-US8-04**: Tokens authenticate against existing `requireUserOrGithubBearer` — extend it to accept verified-skill `vsk_` prefixed bearer tokens (lookup by hash). If verified-skill token is valid, set the same auth context as a user cookie.
- [x] **AC-US8-05**: Empty state "No tokens yet — generate one to use the CLI" with primary CTA.
- [x] **AC-US8-06**: Revoke confirmation modal: "Revoke `{prefix}`?" — explains "Any process using this token will fail immediately."
- [x] **AC-US8-07**: Vitest covers create-rotation, hash-only-storage, list-without-plaintext, revoke-idempotent.

---

### US-009: /account/skills — skill stats hub (P1)
**Project**: vskill-platform

**As a** user
**I want** a quick view of my skills (counts + recent activity)
**So that** the cabinet is a true hub, not just settings

**Acceptance Criteria**:
- [x] **AC-US9-01**: Tab shows two stat tiles at top: **Public skills** (count + "Manage →" link to existing dashboard) · **Private skills** (count, links to /account/repos for source repos).
- [x] **AC-US9-02**: Recent activity list: last 5 publishes/updates (`{skillName, action: "published"|"updated", timestamp}`). "View all →" link to existing skill management UI.
- [x] **AC-US9-03**: Empty state for both tiles: "No public skills yet — install the desktop app to create one." with CTA → /desktop.
- [x] **AC-US9-04**: `GET /api/v1/account/skills/summary` returns `{publicCount, privateCount, recentActivity[]}`. Cached 60s.

---

### US-010: /account/notifications — preferences (P1)
**Project**: vskill-platform

**As a** user
**I want** to control which emails I receive
**So that** I'm not spammed and important alerts still reach me

**Acceptance Criteria**:
- [x] **AC-US10-01**: Tab shows checkbox group: **Weekly digest** (default off) · **Security alerts** (default on, can't be unchecked — explain "We'll always notify you about suspicious account activity") · **Comment replies** (default on) · **Product updates** (default off, marketing).
- [x] **AC-US10-02**: "Save preferences" button persists to `User.notificationPrefs` JSON column via `PATCH /api/v1/account/notifications`. Toast on success.
- [x] **AC-US10-03**: Email backend (digest cron) is **out of scope** — the preferences are stored, but no email job ships in v1. Tooltip on Weekly digest checkbox: "Daily/weekly digest emails ship in a future update."

---

### US-011: /account/danger — destructive actions (P1)
**Project**: vskill-platform

**As a** user
**I want** to sign out everywhere, export my data, or delete my account
**So that** I'm in full control

**Acceptance Criteria**:
- [x] **AC-US11-01**: Tab shows three sections in red-bordered cards (GitHub Danger Zone style):
   - **Sign out of all devices** — button → revokes all cookies + tokens. Toast confirms.
   - **Export my data** — button → enqueues a job that emails a JSON dump within 24h. Empty-state "No export jobs yet". Status table below showing past exports.
   - **Delete account** — large red button → opens modal requiring user to type their GitHub handle exactly. On confirm: soft-delete (`User.deletedAt = now`, retain for 30 days), cascade-disconnect repos, revoke all tokens, sign out. Email confirmation sent (when email backend ships).
- [x] **AC-US11-02**: Endpoints: `POST /api/v1/account/sign-out-all`, `POST /api/v1/account/export`, `POST /api/v1/account/delete`. All require fresh re-auth (last login <5 min) — if older, prompt for re-auth first.
- [x] **AC-US11-03**: Hard-delete cron runs nightly: rows with `deletedAt < now - 30d` get purged. Audit-log entry written.

---

### US-012: Desktop /account mirror + npx studio parity (P1)
**Project**: vskill

**As a** user of the Tauri desktop app or `npx vskill studio`
**I want** the same /account experience inside those surfaces
**So that** I never have to leave the app to manage my account

**Acceptance Criteria**:
- [x] **AC-US12-01**: Desktop sidebar gets a new "Account" entry below "Skills". Click → opens an in-app /account view rendered by the same eval-ui shell as the studio (uses Tauri WebView, fetches from verified-skill.com/api). NOT a browser pop-out.
- [x] **AC-US12-02**: `npx vskill studio` browser tab gets the same "Account" entry in its sidebar. Same component. Same data.
- [x] **AC-US12-03**: Both desktop + npx-studio surfaces use the Bearer token from existing OAuth device-flow (0831 keyring storage on desktop; cookie on npx-studio when signed in via that surface).
- [x] **AC-US12-04**: When offline (desktop): /account shows cached data with banner "Offline — last synced X ago". On reconnect, automatic refresh.
- [x] **AC-US12-05**: Component extraction: `ConnectedReposTable`, `ProfileForm`, `PlanCard`, `TokensTable`, `NotificationsForm`, `DangerZone` all live in `repositories/anton-abyzov/vskill/src/eval-ui/src/components/account/` and are imported by:
   - `repositories/anton-abyzov/vskill-platform/src/app/account/**` (web)
   - desktop sidebar (Tauri WebView)
   - npx studio sidebar
- [x] **AC-US12-06**: `useAccount()` hook in `src/eval-ui/src/hooks/useAccount.ts` provides the data fetching layer; both surfaces use it identically.

---

### US-013: Tests + e2e parity (P0)
**Project**: vskill-platform + vskill

**As a** maintainer
**I want** comprehensive test coverage of the new endpoints + UI
**So that** future refactors don't break user trust

**Acceptance Criteria**:
- [x] **AC-US13-01**: Vitest unit tests cover every new endpoint (≥90% coverage on `/api/v1/account/*`).
- [x] **AC-US13-02**: Vitest component tests cover ConnectedReposTable (all 4 status colours, empty state, kebab actions, mobile responsive snapshot).
- [x] **AC-US13-03**: Vitest SSR tests cover /pricing (license badge, mailto target, meta description) + /account (cookie gate, sidebar order).
- [x] **AC-US13-04**: Playwright e2e tests cover: cookie-auth gate on /account, profile edit + save, connect-repo pre-flight → mocked GitHub callback → row appears, disconnect modal + confirmation, generate-token modal + revoke.
- [x] **AC-US13-05**: E2E tests cover desktop+npx-studio account view parity (using the existing Playwright runner against eval-server).
- [x] **AC-US13-06**: Cargo tests cover the new desktop IPC commands for `account_*` (if any) — at minimum a stub `get_account_url` returning the right URL.

---

## Glossary

- **Cabinet** — the user-settings hub at /account. Term lifted from Anton's "your page with your settings or your cabinet". Each sub-route is a "tab".
- **Connected repo** — a GitHub repository the user has linked via the GitHub App. Rows live in `ConnectedRepo` Prisma table.
- **Pre-flight permissions page** — the screen at /account/repos/connect where we explain what we'll do *before* redirecting to github.com. Mirrors Vercel's permission-row pattern.
- **Status dot** — coloured circle in the connected-repos table indicating sync health (green/amber/grey/red).
- **Source-of-truth API** — `verified-skill.com/api/v1/account/*` is the only data source for account state. Web, desktop, and npx-studio are all clients of it. No local caches in 3 places.
- **Soft-delete** — setting `User.deletedAt` rather than DELETE. Retained 30 days for recovery, then purged by nightly cron.
- **vsk_-prefixed token** — verified-skill API tokens in the form `vsk_xxxxxxxx...`. Distinguishable from GitHub tokens (which start with `ghp_` or `gho_`).

## Open Questions

- **Q1**: Do we surface the GitHub App's "Suspend" feature (soft-disable without uninstall) in /account/repos? **Resolved**: no — none of the surveyed competitors do; collapse to binary connect/disconnect. Suspend stays a power-user feature on github.com.
- **Q2**: Should the desktop app's /account view use a Tauri webview pointing at `verified-skill.com/account` directly, OR render via the eval-ui component tree fed by the API? **Resolved**: eval-ui + API. Two reasons: (a) offline support is impossible with a webview, (b) component extraction makes desktop+studio+web identical-by-construction. The webview-iframe-pointing-at-prod approach is rejected.
- **Q3**: Email change verification (when a user edits their email)? **Resolved**: out of scope for v1 — display name + bio are editable, email comes from GitHub and is read-only. Email changes require changing the connected GitHub identity.
- **Q4**: Stripe wiring? **Resolved**: still deferred. Pro CTA stays "Notify me" waitlist. Plan & billing tab shows current tier + grey-disabled "Manage subscription" with tooltip "Coming when subscriptions launch".
- **Q5**: API token CLI? **Resolved**: tokens are usable as Bearer auth for the existing `/api/*` endpoints. CLI helpers (`vskill auth login --token vsk_...`) ship in a separate increment.
