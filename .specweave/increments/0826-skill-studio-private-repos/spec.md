---
increment: 0826-skill-studio-private-repos
title: "Skill Studio support for private GitHub repositories (enterprise v1)"
type: feature
priority: P1
status: planned
created: 2026-05-03
structure: user-stories
test_mode: TDD
coverage_target: 90
projects:
  - vskill-platform
  - vskill
---

# Feature: Skill Studio support for private GitHub repositories (enterprise v1)

## Overview

Read-only support for private skills hosted in GitHub Cloud + GitHub Enterprise Cloud across both Skill Studio surfaces — the verified-skill.com web platform and the local `vskill studio` CLI runtime. Org-scoped via GitHub App installations using envelope-encrypted access tokens. Hard UI + data-layer separation between public and private skills prevents accidental leaks. Audit log, token rotation, and revocation included from day 1. Free tier ships with per-org caps (50 private skills, 25 members); SOC 2 audit deferred until first paying enterprise demands it but technical groundwork (envelope encryption, audit log, threat model) is in place.

## Problem Statement

Today, both Skill Studio surfaces assume GitHub is fully public. The web platform's OAuth scope is `read:user` only, the access token is fetched then discarded in the callback, and every server-side GitHub fetcher hard-codes a service PAT for public scope. The CLI installer makes bare unauthenticated `fetch()` calls. This blocks enterprises from using Skill Studio with their internal skill libraries kept in private GitHub repos — a feature competitors (Backstage, Snyk, Vercel, CodeRabbit, Codecov) all ship.

A 3-agent research run mapped 8 specific integration gaps with file:line precision, recommended GitHub App over OAuth-`repo`-scope (org-wide install model, fine-grained per-repo, 5,000+ req/hr installation budget), and recommended envelope encryption (per-tenant DEK in Postgres, KEK in Workers Secret) to ensure a stolen Postgres dump alone cannot expose any tokens.

## Goals (v1)

1. **Read-only private-repo support** on both surfaces (web platform + CLI studio)
2. **Org-scoped tenancy** via GitHub App installations (one Tenant = one GitHub org installation)
3. **Hard public/private separation** at every layer — schema, routing, repository helpers, cache keys, UI navigation, browser tab title
4. **Anti-mistake publish flow** to prevent accidentally publishing a private skill as public
5. **Token-at-rest envelope encryption** on every stored GitHub access token (platform + CLI keychain)
6. **Audit log from day 1** covering 14+ security-relevant actions with 1yr Postgres + 7yr R2 retention
7. **Webhook integrity + replay protection** (HMAC-SHA256 verify before parse, `X-GitHub-Delivery` dedupe, 5-minute freshness window)
8. **Cross-tenant isolation proof** — 1000-query CI fuzz test demonstrates zero leaks
9. **Free tier with per-org caps** (50 private skills, 25 members) enforced at warn-80% / block-100%
10. **CLI auth via GitHub Device Flow** (no callback URL, works behind proxies)

## Out of Scope (v1)

The following are explicitly deferred to follow-on increments to keep v1 ship-ready in 4–6 weeks:

- **GitHub Enterprise Server (self-hosted)** — needs a customer-side reverse-tunnel connector (Snyk-Broker pattern); separate increment
- **SAML SSO** via WorkOS / Clerk — required for many enterprise pilots but not blocking v1 read-only flow
- **Write-back to private repos** (forks, PRs back into enterprise repos) — read-only is the v1 contract
- **Stripe billing / paid tier** — free with per-org caps in v1; paid tier when first design partner asks to upgrade
- **SCIM provisioning** — admin manages members manually in v1
- **HIPAA / BAA** — indefinite
- **SOC 2 Type II audit engagement** — defer until first paying enterprise demands it; technical groundwork (envelope encryption, audit log, threat model) is in place

## User Stories

### US-001: Org admin installs the Skill Studio GitHub App (P1)
**Project**: vskill-platform

**As an** org admin on GitHub
**I want** to install the "Skill Studio" GitHub App on my org and select which repos it can access
**So that** my org's private skills become discoverable and indexable inside Skill Studio without exposing them publicly

**Acceptance Criteria**:
- [x] **AC-US1-01**: Clicking "Connect GitHub Org" on `/settings/integrations` redirects to `https://github.com/apps/skill-studio/installations/new` with the correct App slug
- [x] **AC-US1-02**: After the user picks repos and approves, the GitHub callback to `/api/v1/auth/github/installation/callback` creates a `Tenant` row keyed by `githubInstallationId` with `installedById` set to the actor user
- [x] **AC-US1-03**: An `Installation` row is created with the freshly minted installation token encrypted via envelope encryption (`encryptedToken` + `encryptedTokenIv` + `encryptedTokenTag`); `tokenExpiresAt` is set to 60 minutes from mint time
- [x] **AC-US1-04**: An `AuditEvent` with `action="installation.create"` is written including `actorId`, `tenantId`, `ip`, `userAgent`, and a `metadata.repoCount` field
- [x] **AC-US1-05**: A re-install on the same `githubInstallationId` updates the existing `Tenant` row instead of creating a duplicate; if the tenant was previously soft-deleted (`uninstalledAt` set), it is reactivated and `uninstalledAt` is NULLed

---

### US-002: Private skills surface only in dedicated "Org" UI section (P1)
**Project**: vskill-platform

**As an** org member browsing the web platform
**I want** my org's private skills to appear ONLY in a dedicated "Org: <org-name>" navigation section, never in the public catalog
**So that** there is zero risk of accidentally exposing internal skills to the public

**Acceptance Criteria**:
- [x] **AC-US2-01**: The public route `GET /api/v1/skills/*` and `GET /api/v1/skills/search` enforce a hard-coded `WHERE tenantId IS NULL` filter at the data-layer (Prisma repository), NOT just an app-layer check
- [x] **AC-US2-02**: Private skills are reachable only via tenant-scoped routes `GET /api/v1/tenants/:tenantId/skills/**`, which require a `withTenant(tenantId, currentUser)` membership assertion before any DB query
- [x] **AC-US2-03**: The web UI left sidebar renders two distinct sections: "Public Skills" and "Org: <org-name>"; the org section uses an amber/lock badge that never appears on the public section
- [x] **AC-US2-04**: The KV cache layer keys all private resources with prefix `private:{tenantId}:` so a public-route cache miss can never read a tenant key
- [x] **AC-US2-05**: Navigating to `/skills/` (public catalog) renders zero rows from any tenant, verified by integration test that seeds a private skill and asserts it does not appear

---

### US-003: Private skill detail pages constantly remind users they are private (P1)
**Project**: vskill-platform

**As an** org member viewing a private skill detail page
**I want** persistent visual reminders that this skill is private and scoped to my org
**So that** I never confuse a private skill for a public one when sharing links or copying content

**Acceptance Criteria**:
- [x] **AC-US3-01**: Every private skill detail page renders a persistent banner at the top: "PRIVATE — visible to <org-name> members only" with amber/warning styling
- [x] **AC-US3-02**: The URL pattern is `/orgs/:orgSlug/skills/:slug` (a different shape from the public `/skills/:owner/:repo/:slug`) so the URL alone signals tenant scope
- [x] **AC-US3-03**: The browser tab title is prefixed `[Private] ` (e.g. `[Private] internal-deploy — Skill Studio`)
- [x] **AC-US3-04**: Open Graph + meta tags suppress description and image for private pages (no leakage if URL is shared in a chat preview)
- [x] **AC-US3-05**: Attempts to load `/orgs/:orgSlug/skills/:slug` by a non-member return 404 (NOT 401/403 — do not leak the existence of the org or skill)

---

### US-004: Submission anti-mistake flow prevents accidental public publication (P1)
**Project**: vskill-platform

**As an** org member publishing a new skill
**I want** the submission form to make me explicitly choose privacy with anti-mistake safeguards
**So that** I cannot accidentally publish a private skill as public

**Acceptance Criteria**:
- [x] **AC-US4-01**: The submit form requires a privacy ternary: `PUBLIC` | `PRIVATE` (with org name shown) | `ASK` (no default selection); the user must explicitly choose
- [x] **AC-US4-02**: When the user has any active `Installation`, the default selection is `PRIVATE` (with their org name)
- [x] **AC-US4-03**: Switching from `PRIVATE` to `PUBLIC` opens a confirmation dialog requiring the user to type the exact skill name (e.g. "type 'internal-deploy' to confirm public publication") — submission is blocked until the typed name matches
- [x] **AC-US4-04**: The backend cross-validates `repoUrl` visibility against the installation's repo list via `GET /installation/repositories`; if `privacy="public"` but the repo is private, the submission is rejected with HTTP 422 and message "This repo is private on GitHub — switch privacy to PRIVATE or change repo visibility on GitHub first"
- [x] **AC-US4-05**: Publishing from a public repo with `privacy="private"` is allowed but a non-blocking warning is shown: "You are publishing a public repo as private — content remains public on GitHub"
- [x] **AC-US4-06**: A successful publication writes an `AuditEvent` with `action="private_skill.create"` (or `public_skill.create`) including the chosen privacy and repo URL

---

### US-005: Org admin uninstalls the App and all private data is purged (P1)
**Project**: vskill-platform

**As an** org admin uninstalling the Skill Studio App
**I want** every piece of my org's private data to be purged immediately
**So that** I retain control over my org's data and meet compliance obligations

**Acceptance Criteria**:
- [x] **AC-US5-01**: The `installation.deleted` webhook event triggers `Tenant.uninstalledAt = now()`, sets `Installation.encryptedToken/Iv/Tag = NULL`, and purges all KV keys matching `private:{tenantId}:*`
- [x] **AC-US5-02**: All `PrivateSkill` rows for that tenant are soft-deleted (`deletedAt` set); hard delete runs on a 30-day grace timer to allow accidental-uninstall recovery
- [x] **AC-US5-03**: An `AuditEvent` with `action="installation.delete"` is written including the trigger source (`webhook` | `manual_ui` | `manual_api`)
- [x] **AC-US5-04**: An identical purge is invokable manually via `/settings/integrations → Disconnect` button (which calls the GitHub API to revoke the installation, then runs the same purge path)
- [x] **AC-US5-05**: After uninstall, any subsequent request to a tenant-scoped route returns 410 Gone with message "This installation has been removed. Reconnect via /settings/integrations."

---

### US-006: Org admin views audit log with filtering and export (P1)
**Project**: vskill-platform

**As an** org admin
**I want** to view a searchable, exportable audit log of every security-relevant action in my org
**So that** I can investigate incidents and satisfy compliance reviews

**Acceptance Criteria**:
- [x] **AC-US6-01**: The route `/settings/audit-log` lists `AuditEvent` rows scoped to the current tenant with pagination (50/page); non-admins receive 403
- [x] **AC-US6-02**: Filters available: `action` (e.g. `installation.*`, `private_skill.*`, `auth.*`), date range, actor, outcome (`success` | `failure`)
- [x] **AC-US6-03**: CSV and JSON export buttons download the currently filtered rows; CSV export caps at 10,000 rows (with a "narrow your filter" message above)
- [x] **AC-US6-04**: At least 14 distinct actions are logged: `installation.create`, `installation.update`, `installation.delete`, `token.refresh`, `token.rotate`, `private_skill.view`, `private_skill.clone`, `private_skill.fork`, `member.invite`, `member.remove`, `member.role_change`, `auth.login`, `auth.failed`, `webhook.received`, `webhook.signature_invalid`
- [x] **AC-US6-05**: Audit events are retained 1 year hot in Postgres and 7 years cold in R2 via lifecycle rule

---

### US-007: Free tier enforces per-org caps with warn + block thresholds (P1)
**Project**: vskill-platform

**As a** product owner
**I want** the free tier to cap private-skill volume per org
**So that** we control infrastructure cost and create a clear upgrade path when the paid tier ships

**Acceptance Criteria**:
- [x] **AC-US7-01**: The `Tenant` row carries `privateSkillLimit` (default 50) and `memberLimit` (default 25)
- [x] **AC-US7-02**: At 80% of either cap, a non-blocking yellow banner shows on `/settings/integrations` and the publish form: "You're using X of Y private skills (80%). Upgrade options coming soon."
- [x] **AC-US7-03**: At 100% of `privateSkillLimit`, new private-skill submissions are blocked with HTTP 402 and message "You've reached the free-tier limit of 50 private skills. Contact us to expand the limit."
- [x] **AC-US7-04**: At 100% of `memberLimit`, new member invitations are blocked with the same shape of error
- [x] **AC-US7-05**: Cap counts are derived from live `COUNT(*)` queries on `PrivateSkill` and `OrgMember` (no cached counters that can drift); query is sub-50ms via tenant-scoped index

---

### US-008: Connect GitHub Org flow at /settings/integrations (P1)
**Project**: vskill-platform

**As an** org admin
**I want** a single-click "Connect GitHub Org" entry point on the integrations page
**So that** I can install the App without hunting through external docs

**Acceptance Criteria**:
- [x] **AC-US8-01**: `/settings/integrations` shows the GitHub integration card with "Connect GitHub Org" CTA when no installation exists, "Connected as <org-name>" + "Disconnect" when one exists
- [x] **AC-US8-02**: The CTA generates a state token (UUID, stored in session for 10min), then redirects to `https://github.com/apps/skill-studio/installations/new?state={uuid}`
- [x] **AC-US8-03**: The callback `/api/v1/auth/github/installation/callback` validates the state token (rejects unknown / expired / replay)
- [x] **AC-US8-04**: On callback success, the user is redirected to `/settings/integrations` with a success toast; on failure, an error toast surfaces a human-readable reason
- [x] **AC-US8-05**: The page lists each connected org as a separate entry when the user belongs to multiple installations

---

### US-009: Webhook receiver verifies HMAC before parse and dedupes deliveries (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the webhook endpoint to reject every malformed, unsigned, or replayed delivery
**So that** an attacker cannot forge GitHub events to manipulate tenants

**Acceptance Criteria**:
- [x] **AC-US9-01**: `POST /webhooks/github` reads the raw request body and verifies `X-Hub-Signature-256` via HMAC-SHA256 (constant-time compare via `crypto.subtle`) BEFORE parsing JSON
- [x] **AC-US9-02**: Missing signature → 401; invalid signature → 403 + `AuditEvent action="webhook.signature_invalid"`; passing signature → proceed
- [x] **AC-US9-03**: After signature validation, `X-GitHub-Delivery` UUID is checked against `WEBHOOK_DEDUP_KV` (24h TTL); duplicate → 200 OK no-op; first-seen → write to KV before processing
- [x] **AC-US9-04**: When the `X-GitHub-Hook-Installation-Target-Type` is `Server` or the request includes `X-GitHub-Enterprise-Version`, return 501 Not Implemented with body "GitHub Enterprise Server is on the v2 roadmap; v1 supports GitHub Cloud + Enterprise Cloud only"
- [x] **AC-US9-05**: The route enqueues the validated event to the Cloudflare `SUBMISSION_QUEUE` consumer and returns 200 within 2 seconds (well below GitHub's 10s timeout)
- [x] **AC-US9-06**: A test suite of 1000 synthetic deliveries (malformed body, wrong signature, replay, future timestamp, unsigned) confirms 100% rejection rate

---

### US-010: Cross-tenant isolation proven by 1000-query CI fuzz test (P1)
**Project**: vskill-platform

**As a** security engineer
**I want** a CI test that proves no tenant ever sees another tenant's private resources
**So that** we can ship to enterprises with confidence

**Acceptance Criteria**:
- [x] **AC-US10-01**: A fuzz test seeds 10 tenants × 50 private skills each (500 total private resources)
- [x] **AC-US10-02**: The test issues 1000 random queries: half via public routes (`/api/v1/skills/*`, `/api/v1/skills/search`), half via tenant-scoped routes with a randomly chosen non-member identity
- [x] **AC-US10-03**: Public-route queries return zero private rows; non-member tenant-scoped queries return 404
- [x] **AC-US10-04**: The full fuzz suite runs in <30 seconds in CI and is part of the default test pipeline (NOT opt-in)
- [x] **AC-US10-05**: A failing fuzz test blocks deploy and posts to the security incidents channel

---

### US-011: `vskill auth login` runs Device Flow and stores token in OS keychain (P1)
**Project**: vskill

**As a** developer using the local CLI
**I want** `vskill auth login` to authenticate me with GitHub via Device Flow and store my token securely
**So that** I never paste a token on the command line and the credential cannot leak from a shell history file

**Acceptance Criteria**:
- [x] **AC-US11-01**: `vskill auth login` calls `POST https://github.com/login/device/code`, prints the verification URI (`https://github.com/login/device`) and the 8-character user code (formatted `XXXX-XXXX`), and opens the URL in the default browser when possible
- [x] **AC-US11-02**: The CLI polls `POST https://github.com/login/oauth/access_token` every 5 seconds (respecting `interval` from the device-code response) until a token is issued, the user denies, or 15 minutes elapse
- [x] **AC-US11-03**: On success, the token is stored in the OS keychain via `@napi-rs/keyring` (macOS Keychain / Windows DPAPI / libsecret); a fallback writes `~/.vskill/keys.env` with mode 0600 and prints a warning if keychain is unavailable
- [x] **AC-US11-04**: The token's GitHub user (login + numeric id) is fetched once and cached locally so subsequent commands do not re-query
- [x] **AC-US11-05**: Plaintext tokens are never logged, never echoed, and never appear in process arguments or env (use stdin / keychain only)

---

### US-012: `vskill auth status` and `vskill auth logout` work end-to-end (P2)
**Project**: vskill

**As a** developer
**I want** to inspect and clear my GitHub auth state from the CLI
**So that** I can diagnose auth issues and revoke local credentials

**Acceptance Criteria**:
- [x] **AC-US12-01**: `vskill auth status` prints the current GitHub login (e.g. "Signed in as @aabyzov via GitHub Device Flow (token expires <date>)") when a token exists, "Not signed in. Run `vskill auth login`." otherwise
- [x] **AC-US12-02**: `vskill auth status` does NOT call the GitHub API by default (uses cached identity); a `--refresh` flag forces a `GET /user` call and updates the cache
- [x] **AC-US12-03**: `vskill auth logout` deletes the token from the OS keychain (or removes the 0600 fallback file) and clears the cached identity
- [x] **AC-US12-04**: After `vskill auth logout`, `vskill auth status` reports "Not signed in." and any subsequent private-resource command surfaces a "Run `vskill auth login`" hint
- [x] **AC-US12-05**: Both commands exit with code 0 on success, non-zero on failure, and emit machine-readable output with `--json`

---

### US-013: Studio UI sidebar mirrors web with separate Public + Org sections (P1)
**Project**: vskill

**As a** developer using `vskill studio` locally
**I want** the studio UI sidebar to mirror the web platform's public/private separation
**So that** the visual contract is identical regardless of where I'm running Studio

**Acceptance Criteria**:
- [x] **AC-US13-01**: The studio sidebar renders two top-level sections: "Public" and "Org: <org-name>" — visually identical to the web platform (same amber/lock badge on the org section)
- [x] **AC-US13-02**: When no auth is active (no keychain token), the "Org" section is replaced by a "Connect GitHub" CTA card (NOT an empty list), which runs `vskill auth login` when clicked from the terminal-piloted UI
- [x] **AC-US13-03**: When the token exists but no installations are accessible, the "Org" section shows "No orgs have installed Skill Studio. Ask your admin to install at /settings/integrations on verified-skill.com."
- [x] **AC-US13-04**: The PRIVATE badge appears only on org-section entries; never on public-section entries
- [x] **AC-US13-05**: Clicking a private skill in the studio sidebar opens its detail view with the same persistent "PRIVATE — visible to <org-name> members only" banner

---

### US-014: Studio platform-proxy injects Authorization header for private routes (P1)
**Project**: vskill

**As a** developer using `vskill studio`
**I want** the local eval-server to proxy private API calls to verified-skill.com with my Authorization header attached
**So that** the browser never has to hold my GitHub token and CORS stays clean

**Acceptance Criteria**:
- [x] **AC-US14-01**: `src/eval-server/platform-proxy.ts` matches requests to `/api/v1/private/*` and `/api/v1/tenants/*` and reads the GitHub token from the OS keychain on each request (cached for 60s in-process)
- [x] **AC-US14-02**: The outbound request to `verified-skill.com` adds `Authorization: Bearer <token>`; the browser request never carries the token
- [x] **AC-US14-03**: A 401 response from upstream is rewritten into a 401 with body `{"error":"auth_required","message":"Token expired or insufficient scope. Run \`vskill auth login\`."}` so the studio UI shows a useful prompt
- [x] **AC-US14-04**: Public routes (`/api/v1/skills/*`) are proxied without any Authorization header (avoids needlessly exposing the token to upstream)
- [x] **AC-US14-05**: A unit test confirms that for every request to a private path, an Authorization header is present on the outbound; for every public path, it is absent

---

### US-015: `vskill add <private-skill-url>` works against private repos via keychain token (P1)
**Project**: vskill

**As a** developer
**I want** `vskill add <private-skill-url>` to work the same way for private skills as for public ones
**So that** the install flow is uniform and I can install private org skills as easily as public ones

**Acceptance Criteria**:
- [x] **AC-US15-01**: When `vskill add <url>` resolves the URL to a private skill (via the platform's `/api/v1/private/resolve` endpoint), the installer attaches `Authorization: Bearer <token>` on every subsequent fetch (skill metadata, contents, dependencies) — covering all 13 fetch sites identified in `src/commands/add.ts`
- [x] **AC-US15-02**: A 401 response on any of those fetches surfaces the message "Token expired or insufficient scope. Run `vskill auth login` and try again." with exit code 2
- [x] **AC-US15-03**: A 404 from upstream surfaces "This skill was not found, or your account does not have access. Verify the URL and your org membership." with exit code 1
- [x] **AC-US15-04**: Once installed, the local skill files do NOT contain any auth token (the token is used only at fetch time, never written to disk inside the skill bundle)
- [x] **AC-US15-05**: A successful private-skill install writes an entry to the local lockfile noting `source: "private"` and the source org so subsequent updates can be authenticated correctly

---

## Non-Functional Requirements

These are cross-cutting acceptance criteria that apply to all stories and should be verified independently in CI.

### NFR-001: Token-at-rest encryption (P1)
**Project**: vskill-platform

- [x] **AC-NFR1-01**: Every GitHub access token stored in `Installation.encryptedToken` is AES-GCM ciphertext using a per-tenant 32-byte DEK; plaintext is never persisted to Postgres
- [x] **AC-NFR1-02**: The per-tenant DEK is wrapped (AES-KW) under an account-level KEK that lives only in `VSKILL_TOKEN_KEK` Workers Secret (or Cloudflare Secrets Store)
- [x] **AC-NFR1-03**: An ESLint rule + central logger redaction layer prevents `console.log` of any token-typed value; CI fails if a `Token`/`AccessToken` typed value flows to a log call
- [x] **AC-NFR1-04**: A KEK rotation runbook documents dual-KEK support: `dekVersion` field on `Tenant` allows new tokens encrypted under `KEK_v2` while old DEKs are unwrapped under `KEK_v1` and rewrapped on read

### NFR-002: Webhook signature integrity (P1)
**Project**: vskill-platform

- [x] **AC-NFR2-01**: 100% of malformed, unsigned, replayed, and stale (>5 min old when `ts` is available) webhook deliveries are rejected; verified by the 1000-synthetic-delivery test in AC-US9-06
- [x] **AC-NFR2-02**: Signature comparison uses `crypto.subtle` constant-time compare; benchmark proves no timing side-channel (variance <1ms across 10k samples)

### NFR-003: Rate limit budget per installation (P1)
**Project**: vskill-platform

- [x] **AC-NFR3-01**: Outbound GitHub API calls per installation are capped at 4,500 req/hr (90% of GitHub's 5,000/hr base budget) via a token-bucket counter in KV
- [x] **AC-NFR3-02**: When approaching the cap, requests are queued or surface a 429 to callers; never silently dropped
- [ ] **AC-NFR3-03**: `/search/code` is forbidden (10 req/min hard cap) — a runtime guard logs error "Use /installation/repositories enumeration instead" if invoked, and a lint rule flags it at build time

### NFR-004: ETag conditional GETs to avoid rate-limit charge (P2)
**Project**: vskill-platform

- [x] **AC-NFR4-01**: The hourly polling-fallback cron uses `If-None-Match` headers against the cached SHA on every `GET /repos/:owner/:repo/commits/:ref` and skill-content fetch
- [x] **AC-NFR4-02**: 304 responses do NOT count against the rate-limit token bucket; verified by integration test asserting bucket count is unchanged after a series of 304 responses

### NFR-005: Cross-tenant isolation defense in depth (P1)
**Project**: vskill-platform

- [x] **AC-NFR5-01**: Six independent isolation layers are enforced: (1) schema (`tenantId` FK on every private resource), (2) routing (`/api/v1/tenants/:tenantId/...`), (3) repository helper (`withTenant()`), (4) cache (`private:{tenantId}:` prefix), (5) public-route hard filter (`WHERE tenantId IS NULL`), (6) CI fuzz test (US-010)
- [x] **AC-NFR5-02**: Removing any single layer in a test must still result in zero leaks via the remaining layers (defense-in-depth proof)

## Success Metrics

The increment is considered successful when the following are measurable in production within 60 days of GA:

1. **3 design-partner enterprises** install the Skill Studio GitHub App on their production org and successfully index ≥5 private skills each (12 of 15 = 80% adoption signal)
2. **Token-at-rest passes a SOC2-style security review** — an external reviewer (or internal security engineer playing the auditor role) confirms envelope encryption + audit log + threat model meet AICPA Trust Services Criteria CC6.1, CC6.6, CC7.2
3. **Zero cross-tenant leaks in the 1000-query fuzz test** for at least 30 consecutive CI runs post-launch
4. **100% webhook signature rejection** of bad inputs verified by the 1000-synthetic-delivery suite
5. **Rate-limit headroom** — no installation exceeds the 4,500 req/hr cap in normal operation; alerts fire at 90% of cap
6. **CLI auth completion rate** — `vskill auth login` completion (token issued + stored in keychain) is ≥95% of started flows; failure modes are measured (timeout, denial, network)

## Dependencies

- **GitHub App registration** ("Skill Studio") on github.com with permissions: `repository: Contents (read)`, `repository: Metadata (read)`, `organization: Members (read)`; webhook events: `installation`, `installation_repositories`, `push`, `repository`
- **Cloudflare Workers Secrets**: `VSKILL_GITHUB_APP_PRIVATE_KEY` (RS256 PEM), `VSKILL_GITHUB_WEBHOOK_SECRET`, `VSKILL_TOKEN_KEK` (32-byte AES-KW key)
- **Cloudflare Queue**: `SUBMISSION_QUEUE` consumer extended for installation/push/repository events
- **Cloudflare KV**: `WEBHOOK_DEDUP_KV` (new, 24h TTL); `SEARCH_CACHE_KV` (existing, extended with tenant-prefixed keys)
- **Postgres via Hyperdrive**: schema migration adds `Tenant`, `Installation`, `OrgMember`, `AuditEvent` tables and `tenantId` + `privacy` columns on `Skill`
- **R2 bucket**: `audit-events-archive` with 7-year lifecycle rule
- **`@napi-rs/keyring`** added to vskill CLI dependencies

## Open Questions

_(Populated during planning. Original 4 scope questions from the approved plan are answered: catalog hard-separation, free-with-cap pricing, defer SOC 2 audit, Device Flow CLI auth. No outstanding questions at spec-write time.)_
