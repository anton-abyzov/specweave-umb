# Architecture Plan — Skill Studio Private GitHub Repos (Enterprise v1)

**Increment**: `0826-skill-studio-private-repos`
**Affects projects**: `vskill-platform` (web) + `vskill` (CLI)
**Status**: planned
**Estimated effort**: 4–6 weeks
**Source of truth**: spec.md (user stories + ACs), this plan.md (architecture + ADRs), tasks.md (TDD breakdown)

> Companion to `~/.claude/plans/squishy-scribbling-haven.md` (approved scope) and `interview-0826-skill-studio-private-repos.json` (6/6 categories pre-answered, bypass justified by 3-agent research run).

---

## 1. Architecture Overview

The feature spans two surfaces that share a single GitHub App registration:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         GitHub Cloud / Enterprise Cloud                      │
│  ┌────────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ App "Skill Studio" │  │ Installation API │  │ Webhook deliveries       │  │
│  │ (one registration) │  │ /app/installs/...│  │ push, installation,      │  │
│  │  RS256 private key │  │  /access_tokens  │  │ installation_repositories│  │
│  └────────┬───────────┘  └────────┬─────────┘  └──────────┬───────────────┘  │
└───────────┼───────────────────────┼─────────────────────────┼────────────────┘
            │ JWT (≤10min, RS256)   │ POST mints 1-hr token   │ HMAC-SHA256 sig
            ▼                       ▼                         ▼
╔════════════════════════════════════════════════════════════════════════════╗
║  vskill-platform  (Next.js + Cloudflare Workers, OpenNext)                ║
║  ┌────────────────────────────────────────────────────────────────────┐    ║
║  │ /api/v1/auth/github/* (existing user OAuth — UNCHANGED)            │    ║
║  │ /api/v1/auth/github/installation/callback  (NEW)                   │    ║
║  │ /api/v1/webhooks/github  (EXTEND 0708/0727 route — new event types)│    ║
║  │ /api/v1/skills/*  (PUBLIC — hard WHERE tenantId IS NULL filter)    │    ║
║  │ /api/v1/tenants/[tenantId]/skills/**  (NEW — withTenant() guarded) │    ║
║  │ /api/v1/auth/device-flow/{start,poll}  (NEW — proxied for CLI)     │    ║
║  └────────────────────────────────────────────────────────────────────┘    ║
║  ┌────────────────────────────────────────────────────────────────────┐    ║
║  │ src/lib/github-app.ts        — JWT signing, installation token mint│    ║
║  │ src/lib/envelope-crypto.ts   — AES-KW (KEK→DEK), AES-GCM (DEK→tok) │    ║
║  │ src/lib/with-tenant.ts       — membership-asserting query helper   │    ║
║  │ src/lib/audit-log.ts         — fire-and-forget AuditEvent emitter  │    ║
║  │ src/lib/installation-token.ts— getInstallationToken(tenantId)+cache│    ║
║  └────────────────────────────────────────────────────────────────────┘    ║
║  ┌──────────────────────┐  ┌────────────────┐  ┌────────────────────────┐  ║
║  │ Postgres (Hyperdrive)│  │ Cloudflare KV  │  │ Workers Secrets / Store│  ║
║  │ Tenant, Installation,│  │ tenant-prefix  │  │ APP_PRIVATE_KEY,       │  ║
║  │ OrgMember, AuditEvent│  │ token cache    │  │ WEBHOOK_SECRET, KEK    │  ║
║  │ Skill.tenantId nul.  │  │ 50-min TTL     │  │ (rotatable)            │  ║
║  └──────────────────────┘  └────────────────┘  └────────────────────────┘  ║
║  ┌────────────────────────────────────────────────────────────────────┐    ║
║  │ WEBHOOK_DEDUP_DO  — atomic anti-replay (REUSE 0727)                │    ║
║  │ Queues: scan-high (existing), tenant-events (NEW for installation) │    ║
║  │ Cron: */10 → polling fallback for orgs without inbound webhook     │    ║
║  └────────────────────────────────────────────────────────────────────┘    ║
╚════════════════════════════════════════════════════════════════════════════╝
            ▲                                          ▲
            │ HTTPS (server-to-server, public)         │ HTTPS, server-side
            │                                          │ proxy w/ Authorization
╔════════════════════════════════════════════════════════════════════════════╗
║  vskill  (CLI + local Studio runtime, Node.js)                             ║
║  ┌────────────────────────────────────────────────────────────────────┐    ║
║  │ src/commands/auth.ts   — login (Device Flow), status, logout (NEW) │    ║
║  │ src/lib/keychain.ts    — @napi-rs/keyring + 0600 fallback (NEW)    │    ║
║  │ src/lib/github-fetch.ts— addAuth() helper used by ALL fetch sites  │    ║
║  │ src/commands/add.ts    — wires addAuth() at every github.com fetch │    ║
║  │ src/eval-server/platform-proxy.ts — injects Authorization for      │    ║
║  │   /api/v1/private/* and /api/v1/tenants/* prefixes                 │    ║
║  │ src/eval-server/api-routes.ts — adds /api/v1/private/* prefix list │    ║
║  └────────────────────────────────────────────────────────────────────┘    ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### Component boundaries

| Boundary | Owner | Trust | Storage |
|---|---|---|---|
| GitHub App registration | one per environment (prod, staging) | external (GitHub) | App private key in Workers Secret |
| Webhook receiver | vskill-platform (route + DO) | public ingress, HMAC-gated | KV (delivery dedup, 5min) + DO (atomic) |
| Envelope crypto | vskill-platform server runtime | server-only | KEK in Workers Secret; DEK ciphertext in Postgres |
| Tenant isolation | data layer (Prisma helper) + route layer | server-only | Postgres + KV (tenant-prefixed keys) |
| Audit log | append-only emitter | server-only | Postgres (1y hot) → R2 (7y cold lifecycle) |
| CLI keychain | OS-level secure storage on the user's box | local user only | macOS Keychain / Win DPAPI / libsecret; fallback `~/.vskill/keys.env` 0600 |

### Sequence — Install flow (web)

```
Org admin                Browser              vskill-platform           GitHub App
   │                       │                       │                       │
   │ click "Connect"       │                       │                       │
   ├──────────────────────►│                       │                       │
   │                       │ GET /settings/integ   │                       │
   │                       ├──────────────────────►│                       │
   │                       │ 302 → github.com/apps │                       │
   │                       ◄──────────────────────┤                       │
   │ pick repos            │                       │                       │
   ├──────────────────────────────────────────────────────────────────────►│
   │                       │ 302 → /api/v1/auth/github/installation/cb     │
   │                       │       ?installation_id=N&setup_action=install │
   │                       ├──────────────────────►│                       │
   │                       │                       │ JWT-sign → POST       │
   │                       │                       │ /app/installs/N/      │
   │                       │                       │ access_tokens         │
   │                       │                       ├──────────────────────►│
   │                       │                       │ 1-hr token            │
   │                       │                       ◄──────────────────────┤
   │                       │                       │ generate DEK,         │
   │                       │                       │ wrap under KEK,       │
   │                       │                       │ encrypt token,        │
   │                       │                       │ Tenant.upsert,        │
   │                       │                       │ Installation.create,  │
   │                       │                       │ AuditEvent.emit       │
   │                       │ 302 → /settings/integ │                       │
   │                       ◄──────────────────────┤                       │
```

### Sequence — Token refresh (lazy, in-band)

```
caller (any fetcher)         getInstallationToken(tenantId)         GitHub
   │                                  │                                │
   │ need token for tenant T          │                                │
   ├─────────────────────────────────►│                                │
   │                                  │ KV.get("itoken:T")             │
   │                                  ├──┐                             │
   │                                  │  │ hit (TTL>0)                 │
   │                                  ◄──┘                             │
   │ token (cached)                   │                                │
   ◄─────────────────────────────────┤                                │
                       — OR —
   │ need token for tenant T          │                                │
   ├─────────────────────────────────►│                                │
   │                                  │ KV miss → load Installation,   │
   │                                  │ unwrap DEK with KEK, decrypt   │
   │                                  │ token (or token expired) →     │
   │                                  │ JWT-sign → POST mint           │
   │                                  ├───────────────────────────────►│
   │                                  │ {token, expires_at(60min)}     │
   │                                  ◄───────────────────────────────┤
   │                                  │ KV.put("itoken:T",token,50min) │
   │                                  │ AuditEvent("token.refresh")    │
   │ token                            │                                │
   ◄─────────────────────────────────┤                                │
```

### Sequence — Webhook delivery (extends 0727 receiver)

```
GitHub               /api/v1/webhooks/github       WEBHOOK_DEDUP_DO    Queue
   │                       │                              │              │
   │ POST + sig + delivery │                              │              │
   ├──────────────────────►│                              │              │
   │                       │ verify HMAC-SHA256           │              │
   │                       │ 401 if bad ─────────► AuditEvent("webhook.signature_invalid")
   │                       │ require X-GitHub-Delivery    │              │
   │                       │ stub.fetch dedup-and-record  │              │
   │                       ├─────────────────────────────►│              │
   │                       │ {firstSeen}                  │              │
   │                       ◄─────────────────────────────┤              │
   │                       │ duplicate → 200 ok=true,duplicate=true     │
   │                       │                              │              │
   │                       │ switch(event):                              │
   │                       │   "push"     → existing scan-high path     │
   │                       │   "installation"             → tenant-events
   │                       │   "installation_repositories"→ tenant-events
   │                       │   "repository" (visibility)  → tenant-events
   │                       ├─────────────────────────────────────────────►│
   │ 200 enqueued          │                                              │
   ◄──────────────────────┤                                              │
```

### Sequence — Cross-tenant query attempt (defense in depth)

```
attacker A (member of T1) → GET /api/v1/tenants/T2/skills/x
   ├─ route guard:  withTenant(T2, sessionUser)
   │     └─ SELECT 1 FROM OrgMember WHERE tenantId=T2 AND userId=A → 0 rows
   │     └─ 404 (NOT 401 — don't leak existence)
   │     └─ AuditEvent("auth.cross_tenant_denied")
   └─ never reaches data layer

attacker B (anon)         → GET /api/v1/skills/<privateSlug>
   ├─ data-layer filter:  WHERE tenantId IS NULL
   └─ 404 (private skill never appears in public catalog)

CI fuzz test              → 1000 random (tenant, slug) pairs
   └─ assertion: zero private rows reachable from public routes
```

---

## 2. Architecture Decision Records

> 9 ADRs total. Numbering will be assigned at increment closure (next free in `.specweave/docs/internal/architecture/adr/`; current top is 0073, but 0708/0727/0813 increments add concurrent files — final IDs to be reserved at PR time). Refer to them in tasks.md as `ADR-NEW-1` … `ADR-NEW-9` until then.

### ADR-NEW-1: GitHub App over OAuth-`repo`-scope

**Context.** Both surfaces today rely on either an unscoped public PAT (vskill-platform `GITHUB_TOKEN` secret used by 5 fetchers) or unauthenticated `fetch()` (vskill CLI). To read private repos we must escalate. The two natural escalations are (a) widen the existing user OAuth scope from `read:user` to `repo`, or (b) register a GitHub App and let orgs install it.

**Decision.** Register a single GitHub App ("Skill Studio") on github.com with:
- Permissions: `Contents: Read`, `Metadata: Read`, `Members: Read` (for OrgMember sync); no write scopes in v1.
- Events subscribed: `push`, `installation`, `installation_repositories`, `repository`.
- Webhook URL: `https://verified-skill.com/api/v1/webhooks/github` (existing 0708/0727 route — extend, do not duplicate).
- Webhook secret: `VSKILL_GITHUB_APP_WEBHOOK_SECRET` (NEW; the existing `GITHUB_WEBHOOK_SECRET` stays for the legacy 0708 first-party push path so we can roll over independently).
- Authentication: RS256 JWT (`iat`, `exp ≤ iat+10min`, `iss=appId`) signed with App private key in Workers Secret `VSKILL_GITHUB_APP_PRIVATE_KEY`. Mint installation tokens via `POST /app/installations/:id/access_tokens` (1-hr TTL).
- CLI: a separate **public** OAuth app entry (or the App's user-flow) backs the Device Flow — different credential, different keychain slot.

**Consequences.**
- ✅ Org-wide install model: one user action grants access to selected repos for the whole org; no per-user re-auth.
- ✅ Granular scopes per repo, not org-wide; aligns with least-privilege and SOC 2 groundwork.
- ✅ Higher rate budget (5,000–15,000 req/hr/installation vs 5,000 req/hr/user); web platform won't share the budget across orgs.
- ✅ Webhook delivery to a single endpoint regardless of org — no per-tenant URL provisioning.
- ❌ Two GitHub credentials to manage (App private key + per-installation tokens) instead of one OAuth token.
- ❌ Slightly more onboarding friction for the org admin (App install screen vs OAuth consent screen) — mitigated by clear `/settings/integrations` UX with screenshots.

**Alternatives considered.**
1. **Widen user OAuth to `scope=repo`.** Rejected: org-wide, every member must re-consent; can't gate per-repo; tokens can read all of the user's private repos, not just the org's; weak auditability.
2. **Per-org PAT supplied by admin.** Rejected: admin churn (PAT rotation), no native webhook delivery, no granular per-repo scoping, cannot revoke without admin involvement.
3. **GitHub Apps + OAuth user tokens dual-mode.** Deferred to v2: the App alone covers v1 read-only browsing; user tokens unlock write-back features (forks, PR creation) not yet in scope.

---

### ADR-NEW-2: Envelope encryption for installation tokens

**Context.** Installation tokens are short-lived (1 hr) but still highly sensitive — a leaked token grants the App's permissions on the org's private repos. Storing them in plaintext in Postgres means a single DB dump leaks all current tokens. Storing them in Workers Secret directly is impractical (per-tenant key rotation isn't atomic).

**Decision.** Two-tier envelope encryption:
- **KEK (Key Encryption Key)**: account-level, 32-byte AES-KW key, stored in Workers Secret `VSKILL_TOKEN_KEK_V1` (and `_V2` during rotation windows). Optional migration path: Cloudflare Secrets Store for native rotation tooling.
- **DEK (Data Encryption Key)**: per-tenant 32-byte AES-GCM key, generated at install time. The DEK is wrapped (encrypted) under the KEK via AES-KW; the wrapped DEK lives in `Tenant.wrappedDek` (Bytes) with `Tenant.dekVersion` recording which KEK version wrapped it.
- **Token at rest**: the GitHub installation token is encrypted under the DEK with AES-GCM (random 12-byte IV). `Installation.encryptedToken/encryptedTokenIv/encryptedTokenTag` store the three components.
- **Decryption path**: `unwrap(KEK, Tenant.wrappedDek) → DEK; AES-GCM-decrypt(DEK, iv, ct, tag) → plaintext`. Never materialize plaintext outside `getInstallationToken(tenantId)`.

**Consequences.**
- ✅ Stolen Postgres dump alone yields ciphertext only — leak requires both DB access and KEK exfiltration.
- ✅ KEK rotation does NOT require re-encrypting tokens: only re-wrapping per-tenant DEKs (1 AES-KW op per tenant). Bumps `Tenant.dekVersion`. Documented runbook with dual-key (V1+V2) safety window.
- ✅ Per-tenant key separation: compromise of one tenant's DEK does not affect others.
- ✅ Pattern matches AWS KMS / GCP KMS DEK-from-CMK workflow — auditor-friendly for SOC 2 groundwork.
- ❌ Two-tier means slightly more code; mitigated by `envelope-crypto.ts` exposing `encryptToken(tenantId, plaintext)` / `decryptToken(tenantId, parts)` and hiding the wrap/unwrap step.
- ❌ Workers Secret has a size cap; 32-byte KEK is far below it.

**Alternatives considered.**
1. **Single layer (AES-GCM with KEK directly).** Rejected: KEK rotation requires re-encrypting every token; per-tenant separation lost.
2. **Cloudflare D1 with row-level encryption via libsodium.** Rejected: D1 not used for relational data here (Postgres via Hyperdrive is); nothing to gain.
3. **External KMS (AWS, GCP).** Rejected for v1: adds cross-cloud egress cost + secondary failure mode; revisit when first paying enterprise demands BYOK.

---

### ADR-NEW-3: Hard route + data-layer separation for public vs private

**Context.** Anton's directive is unambiguous: *"if by mistake they put something into public, it's going to be a huge blunder."* A single forgotten `WHERE` clause must not leak a private skill into the public catalog. Defense in depth across schema, routing, repository helpers, cache keys, and CI fuzzing.

**Decision.** Five reinforcing barriers:

1. **Schema barrier.** `Skill.tenantId` is nullable. `null` means public, non-null means private to that tenant. `Skill.privacy` enum (`PUBLIC`/`PRIVATE`) duplicates the signal for human readability and for transactional invariant checks.
2. **Route barrier.** Public routes live under `/api/v1/skills/*` (existing). Private routes live under `/api/v1/tenants/[tenantId]/skills/**` (new, app-router segment). Different URL shape signals different scope to humans, CDN caches, log aggregators, and analytics.
3. **Data-layer barrier.** Every public-route Prisma call appends `where: { tenantId: null }`. This is enforced via a thin wrapper `publicSkillsQuery()` in `src/lib/skills-repo.ts` rather than relying on each call site to remember.
4. **Membership barrier.** Every private-route handler runs `await withTenant(params.tenantId, session.userId)` first. The helper does `SELECT 1 FROM OrgMember WHERE tenantId=? AND userId=?`; on miss, returns 404 (not 401 — do not leak tenant existence). All subsequent DB calls are scoped via `db.skill.findMany({ where: { tenantId, ... } })`.
5. **Cache barrier.** All KV keys for private resources are prefixed `private:{tenantId}:`. Public keys retain existing prefixes (`skill:`, `search:`, …). A string-prefix lint rule rejects any code path that constructs a private key without the prefix.

**Consequences.**
- ✅ Five independent barriers — any one alone catches the leak; an attacker needs to defeat all five for a real exposure.
- ✅ CI fuzz test (1000 random tenant-id × public-route pairs) is added in `tests/integration/cross-tenant-fuzz.test.ts`. Asserts zero private rows ever appear.
- ✅ Compatible with existing `/api/v1/skills/*` consumers (web frontend, Studio CLI proxy) — no breaking changes to the public surface.
- ❌ More code to maintain (4 helpers + lint rule + fuzz test). Mitigated by centralizing the helpers; cost is paid once.

**Alternatives considered.**
1. **App-layer filter only (`skills.filter(s => !s.tenantId)` in the controller).** Rejected: prone to forgetfulness; one missed call site = leak. Defense at the data layer must be the floor, not the ceiling.
2. **Postgres Row-Level Security (RLS) with session variables.** Rejected for v1: Hyperdrive connection pooling does not reliably propagate `SET LOCAL` per request — risk of bleed across pooled connections. Revisit after Hyperdrive native-RLS lands.
3. **Single `/api/v1/skills/*` with `?scope=` parameter.** Rejected: same URL shape for both contexts → human errors in copy-paste, in log filters, in reverse-proxy rules.

---

### ADR-NEW-4: Anti-mistake publish flow

**Context.** The submission form today defaults to public publication. With private repos in scope, an org member could trivially flip a switch and expose an internal skill. Anton's directive is to make this mistake essentially impossible without intent.

**Decision.** Three-stage protection:

1. **Required ternary at submit.** The privacy field is a required radio with three options: PUBLIC, PRIVATE (org-name), and ASK_LATER. Default = PRIVATE if the user has any active installation; default = PUBLIC if they have none. The form will not submit until a choice is made.
2. **Name-confirmation on PRIVATE → PUBLIC switch.** Switching from PRIVATE to PUBLIC reveals an inline confirm box: *"To publish `internal-deploy` as PUBLIC, type the skill name below."* Submit button stays disabled until the typed string matches `Skill.name`. (Pattern borrowed from GitHub's repo-delete flow.)
3. **Backend cross-validation.** The submission API resolves `repoUrl` against the org's installation repo list (or via unauthenticated `GET /repos/:owner/:repo` for non-private repos). Mismatch (`repoUrl` is private but `privacy = PUBLIC`) → `400 { error: "repo_visibility_mismatch", suggestion: "switch to PRIVATE or change repo visibility on GitHub first" }`. Public repo → private is allowed but flagged with a UI warning ("you are publishing a public repo as private — content remains public on GitHub").

**Consequences.**
- ✅ Three independent gates — UX nudge, friction on dangerous switch, server-side cross-check. A determined user can still publish public-from-private (by changing GitHub visibility first), but no accidental exposure path remains.
- ✅ Audit trail captures which gate each submission passed (`AuditEvent("private_skill.publish_attempt", outcome)`).
- ❌ Slightly slower happy path (one extra confirmation for users intentionally switching to PUBLIC). Acceptable trade-off for the threat surface.

**Alternatives considered.**
1. **Soft warning only.** Rejected: existing UX pattern across many tools shows users dismiss warnings without reading.
2. **Two-person review for PUBLIC publication of private-repo content.** Deferred: useful at enterprise tier; v1 free tier is single-actor.

---

### ADR-NEW-5: Device Flow over loopback redirect for CLI auth

**Context.** The CLI needs a GitHub user token to read private repos via `vskill add` and to authenticate the Studio's platform proxy. Two viable flows: (a) Device Flow (GitHub shows a code, user pastes into a verification URL), (b) loopback redirect (CLI spins up a local HTTP server, opens a browser, captures the OAuth callback).

**Decision.** Device Flow exclusively. `vskill auth login`:
1. POST `https://github.com/login/device/code` with `client_id` and `scope=read:user`.
2. Display: `Visit https://github.com/login/device and enter A1B2-C3D4` (formatted user code).
3. Poll `https://github.com/login/oauth/access_token` every `interval` seconds (default 5s) until success/expiry.
4. Persist the resulting token in OS keychain via `@napi-rs/keyring` (service `verified-skill.com`, account `github-user-token`). On platforms without keyring (or when the user's session has no keyring daemon — common on headless Linux), fall back to `~/.vskill/keys.env` with mode `0600` and a yellow-text warning.

**Consequences.**
- ✅ No callback URL registration in the GitHub App — works from any machine.
- ✅ No port-conflict failure mode (loopback redirects fail if 8000-range ports are taken).
- ✅ Works behind corporate proxies, in WSL2, in Docker containers, on remote SSH sessions.
- ✅ User code is short and easy to type; verification URL is memorable.
- ❌ Slightly more steps for the user vs a one-click loopback. Acceptable trade-off; matches how `gh auth login`, `kubectl`, and most modern CLIs work.

**Alternatives considered.**
1. **Loopback redirect.** Rejected: callback URL registration drift, port conflicts, broken behind proxies.
2. **PAT prompt.** Rejected: classic PATs are wide-scope by default, hard to revoke per-CLI, and require manual user creation flow.

---

### ADR-NEW-6: Webhooks-first with polling fallback (extends existing 0727 receiver)

**Context.** The platform must react to GitHub events on private repos: `push` (re-scan changed skill), `installation` (tenant lifecycle), `installation_repositories` (repo selection changed), `repository` (visibility flipped public→private or vice versa). An existing webhook receiver at `/api/v1/webhooks/github/route.ts` (introduced in 0708, hardened in 0727) already handles HMAC verification, X-GitHub-Delivery atomic anti-replay via `WEBHOOK_DEDUP_DO`, and `push` event dispatch to `SCAN_HIGH_QUEUE`. Some orgs (corporate VPN-only, behind firewalls without inbound webhook ingress) cannot receive webhooks.

**Decision.** Three-part receiver strategy:

1. **Extend the existing 0727 receiver, do not duplicate.** Add an event-type switch after the existing dedup check:
   - `push` → existing path (unchanged).
   - `installation` (action: `created`/`deleted`/`suspend`/`unsuspend`) → enqueue to NEW `tenant-events` queue.
   - `installation_repositories` (added/removed) → enqueue to `tenant-events`.
   - `repository` (action: `privatized`/`publicized`) → enqueue to `tenant-events`; consumer flips affected `Skill.privacy` and emits audit event.
   - Other events (ping, etc.) → 200 ignored (existing behavior).
2. **HMAC secret rollover.** Add `VSKILL_GITHUB_APP_WEBHOOK_SECRET` alongside existing `GITHUB_WEBHOOK_SECRET`. Verifier tries both; logs which one matched in dev only. Lets us migrate the 0708 first-party publisher to the App's signature key without a global outage.
3. **Polling fallback.** Hourly cron task in `verified-skill-com` Worker (`5,15,25,35,45,55 * * * *` heavy cohort already runs every 10 min) iterates installations where `Tenant.webhooksReceived == 0` for >24h, ETag-conditional `GET /repos/:owner/:repo/commits/:branch` per tracked skill. 304 → no-op (zero rate-limit cost); 200 → enqueue scan-high. Per-installation cap: 4500 req/hr (90% of 5000 budget) enforced in `getInstallationToken` via Worker-side counter in KV.

**Consequences.**
- ✅ Single endpoint, single dedup mechanism, single HMAC verifier — no parallel-route drift.
- ✅ Polling fallback bounds rate-limit consumption via ETag (304 is free in GitHub's accounting).
- ✅ Existing tests in `__tests__/route.test.ts` (≥10 cases) continue to pass; new tests stack on top.
- ❌ The combined receiver is now ~400 LOC; we'll factor out per-event handlers into `src/lib/webhooks/handlers/{push,installation,installation_repositories,repository}.ts` to keep the route file readable.

**Alternatives considered.**
1. **New separate receiver for installation events.** Rejected: two HMAC secrets, two dedup DOs, two routes to monitor; unnecessary divergence.
2. **Polling-only, no webhooks.** Rejected: polling cost scales O(installations × repos) and creates user-visible latency on push events.

---

### ADR-NEW-7: GHES (self-hosted GitHub Enterprise Server) deferred to v2

**Context.** Some prospects run GitHub Enterprise Server on-prem behind their own firewall. The platform Worker cannot make outbound calls to a network it cannot reach.

**Decision.** v1 supports GitHub Cloud (`api.github.com`) and GitHub Enterprise Cloud only. GHES is explicitly out of scope. Detection: when a webhook delivery includes `X-GitHub-Enterprise-Version` header, return `403 { error: "GitHub Enterprise Server not supported in v1" }` and log to AuditEvent. The CLI honors a future `VSKILL_GITHUB_BASE_URL` env var stub (no-op in v1) so v2 can add GHES support without a breaking change.

**Consequences.**
- ✅ Keeps v1 ship-ready in 4–6 weeks.
- ✅ Most enterprises start on GitHub Cloud or are willing to pilot there.
- ❌ Loses some prospects (enterprise on-prem). Mitigated by documenting v2 roadmap (Snyk-Broker reverse-tunnel pattern) and offering an explicit waitlist.

**Alternatives considered.**
1. **Customer-side reverse-tunnel connector.** Deferred to v2 increment 0827E (proposed).
2. **VPN-into-customer-network.** Rejected: massive ops burden; never viable at scale.

---

### ADR-NEW-8: Audit log as first-class system, fire-and-forget emission

**Context.** SOC 2 readiness (even without a formal audit yet) requires comprehensive, tamper-resistant audit trails for security-relevant actions. The audit log must not block user-facing requests; lost events are unacceptable.

**Decision.** Append-only `AuditEvent` model in Postgres with 14 mandatory action types (see Section 5). Emission rules:

1. **Fire-and-forget**: every emission point calls `emitAudit(event)` which returns immediately. The function buffers to in-memory queue; a `ctx.waitUntil()` flush sends to Postgres asynchronously. Buffer overflow (>1000 events) flushes synchronously before accepting more.
2. **Schema**: `id (uuid), tenantId?, actorId?, actorType (USER|SYSTEM|WEBHOOK|CRON), action (dotted namespace), resourceType?, resourceId?, ip?, userAgent?, metadata (json), outcome (SUCCESS|FAILURE|DENIED), ts`. Indexes: `(tenantId, ts DESC)` for tenant viewer; `(action, ts DESC)` for security investigation.
3. **Retention**: 1 year hot in Postgres. R2 lifecycle rule moves rows >1y to cold storage as gzipped NDJSON, partitioned by `tenantId/yyyy-mm`. Total retention 7 years.
4. **Viewer**: `/settings/audit-log` page (vskill-platform) with filters (action, actor, date range), pagination, CSV/JSON export. Per-tenant scoping via `withTenant()`.

**Consequences.**
- ✅ User-facing latency unchanged (fire-and-forget).
- ✅ All security-relevant events captured with consistent schema; auditor-friendly.
- ✅ R2 lifecycle keeps Postgres lean.
- ❌ Brief window where an event is in-memory but not persisted — acceptable for v1 (single-region Worker; restart drops <1s of events). Revisit with Cloudflare Durable Object–backed buffer if zero-loss becomes a hard requirement.

**Alternatives considered.**
1. **Synchronous DB write per event.** Rejected: adds DB latency to every request.
2. **Cloudflare Analytics Engine only.** Rejected: AE is observability, not audit (no record-level retention guarantees, no per-tenant export).

---

### ADR-NEW-9: Free-tier caps enforced at admit time, not runtime

**Context.** Free tier caps: 50 private skills per tenant, 25 active org members. Enforcement could be at admit time (block install/invite when over cap) or runtime (let actions succeed but warn). Anton's directive favors hard caps to prevent abuse.

**Decision.** Cap enforcement happens at the admit boundary:

- **Skill cap**: Submission API rejects with `403 { error: "tenant_skill_cap_exceeded", limit: 50, current: 50 }` when private submission would push the tenant past the cap. Webhook `installation_repositories` event also re-enforces — if a tenant adds repos pushing them over cap, the over-cap repos are flagged but no skills are auto-deleted (admin must remove them manually).
- **Member cap**: 25-member cap is informational in v1 (no invite system yet — members are auto-derived from `OrgMember` table populated via `Members: Read`). Cap UI shows a warning at 80% (20 members) and a hard block on the future invite flow at 100%.

UI warning band at 80%; hard block at 100% with `CTA: contact us about Team plan` (placeholder for future Stripe billing in increment 0830E).

**Consequences.**
- ✅ Predictable cost containment for the free tier.
- ✅ Clear upgrade signal.
- ❌ Hard block is user-visible friction — mitigated by 80% warning and "contact us" CTA.

**Alternatives considered.**
1. **Soft cap with overage billing.** Deferred to billing increment.
2. **Per-skill quota in metadata.** Rejected: simpler to enforce cardinality.

---

## 3. Schema Additions (Prisma)

All additions are non-breaking (new models, nullable fields on existing models). Migration order: schema → backfill (no-op, no existing data) → KEK provisioning → App registration → feature-flag flip.

```prisma
// ─── Tenants & Installations ──────────────────────────────

enum OrgRole {
  OWNER    // GitHub org owner
  ADMIN    // GitHub org admin
  MEMBER   // GitHub org member
}

enum ActorType {
  USER
  SYSTEM
  WEBHOOK
  CRON
  CLI
}

enum AuditOutcome {
  SUCCESS
  FAILURE
  DENIED
}

enum SkillPrivacy {
  PUBLIC
  PRIVATE
}

/// A GitHub org (or user) that has installed the Skill Studio App.
model Tenant {
  id                   String    @id @default(uuid())
  githubInstallationId Int       @unique /// GitHub's installation_id (numeric)
  githubOrgLogin       String    /// e.g., "acme-corp"
  githubOrgId          Int       @unique /// GitHub's org id
  githubOrgType        String    /// "Organization" | "User"
  /// Wrapped per-tenant DEK (32 bytes plaintext, AES-KW wrapped under KEK).
  wrappedDek           Bytes
  /// Which KEK version wrapped the current DEK; bumped on KEK rotation.
  dekVersion           Int       @default(1)

  /// User who clicked "Connect GitHub Org" — used for the founder's audit trail.
  installedById        String
  installedAt          DateTime  @default(now())
  uninstalledAt        DateTime? /// Soft-deletion marker; data purge is delayed.

  /// Webhook receipt tracker; if 0 for >24h, polling fallback kicks in.
  webhooksReceived     Int       @default(0)
  lastWebhookAt        DateTime?

  /// Free-tier caps (ADR-NEW-9). Editable by ops to grant trials.
  privateSkillLimit    Int       @default(50)
  memberLimit          Int       @default(25)

  installation         Installation?
  members              OrgMember[]
  skills               Skill[]      @relation("TenantSkills")
  auditEvents          AuditEvent[]

  createdAt            DateTime  @default(now())
  updatedAt            DateTime  @updatedAt

  @@index([uninstalledAt])
  @@index([lastWebhookAt])
}

/// The current installation token for a tenant. One-to-one with Tenant.
/// Updated lazily by getInstallationToken(); kept for audit history.
model Installation {
  id                  String    @id @default(uuid())
  tenantId            String    @unique
  tenant              Tenant    @relation(fields: [tenantId], references: [id], onDelete: Cascade)

  encryptedTokenIv    Bytes     /// AES-GCM IV (12 bytes random)
  encryptedToken      Bytes     /// AES-GCM ciphertext
  encryptedTokenTag   Bytes     /// AES-GCM auth tag (16 bytes)
  tokenExpiresAt      DateTime  /// 1 hour from mint time

  permissions         Json      /// Snapshot of granted permissions
  repositorySelection String    /// "all" | "selected"

  refreshedAt         DateTime  @default(now())
  refreshCount        Int       @default(0)

  @@index([tokenExpiresAt]) /// For sweeper/refresher cron
}

/// GitHub org membership snapshot, refreshed on auth + on installation events.
model OrgMember {
  tenantId  String
  tenant    Tenant   @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  role      OrgRole

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@id([tenantId, userId])
  @@index([userId]) /// Fast "what tenants does this user belong to?"
  @@index([tenantId])
}

/// Append-only audit trail. See ADR-NEW-8 for action namespace.
model AuditEvent {
  id           String       @id @default(uuid())
  tenantId     String?
  tenant       Tenant?      @relation(fields: [tenantId], references: [id])
  actorId      String?      /// User.id or "system"/"cron"/"webhook"
  actorType    ActorType
  action       String       /// dotted namespace, e.g. "installation.create"
  resourceType String?      /// "skill", "tenant", "member", ...
  resourceId   String?
  ip           String?
  userAgent    String?
  metadata     Json         @default("{}")
  outcome      AuditOutcome
  ts           DateTime     @default(now())

  @@index([tenantId, ts(sort: Desc)])
  @@index([action, ts(sort: Desc)])
  @@index([actorId, ts(sort: Desc)])
}

// ─── EXTEND existing User model ───────────────────────────

// ADD relation to OrgMember (not shown — Prisma adds via OrgMember side).

// ─── EXTEND existing Skill model ──────────────────────────

model Skill {
  // ...existing fields unchanged...

  /// NEW: null = public, non-null = scoped to tenant (ADR-NEW-3).
  tenantId String?
  tenant   Tenant?      @relation("TenantSkills", fields: [tenantId], references: [id], onDelete: Cascade)

  /// NEW: redundant signal of privacy for human readers + invariant checks.
  privacy  SkillPrivacy @default(PUBLIC)

  /// NEW: index for the public-route hard filter (WHERE tenantId IS NULL is
  /// satisfied by NULL placement at the top of the BTree — partial index helps
  /// further but is optional in v1).
  @@index([tenantId])
  @@index([privacy, tenantId])
}
```

**Migration**: single Prisma migration `20260503_add_tenants_and_private_skills` introduces all of the above. Backfill is a no-op (no rows to set). `Skill.tenantId IS NULL` is the existing (implicit) state for every row.

---

## 4. API Surface

### NEW routes (vskill-platform)

| Method | Path | Auth | Purpose | AC reference |
|---|---|---|---|---|
| GET | `/api/v1/auth/github/installation/callback` | Session cookie | Handles GitHub App install redirect; mints first token; creates `Tenant`+`Installation` rows. | install flow ACs |
| POST | `/api/v1/auth/github/installation/uninstall` | Session cookie + `withTenant` | Manual uninstall trigger (the App cannot force-uninstall — this just sets local state to match webhook). | uninstall ACs |
| GET | `/api/v1/tenants/[tenantId]/skills` | Session + `withTenant` | List tenant's private skills (paginated). | private catalog AC |
| GET | `/api/v1/tenants/[tenantId]/skills/[slug]` | Session + `withTenant` | Private skill detail. | private detail AC |
| GET | `/api/v1/tenants/[tenantId]/audit-log` | Session + `withTenant`+ admin role | Audit log viewer; supports `?action=`, `?actor=`, `?from=`, `?to=`, `?format=csv\|json`. | audit AC |
| POST | `/api/v1/auth/device-flow/start` | Public (CLI) | Proxies `POST /login/device/code` to GitHub; returns `{device_code, user_code, verification_uri, interval}`. Adds local rate-limit per IP (10/min). | CLI auth AC |
| POST | `/api/v1/auth/device-flow/poll` | Public (CLI) | Proxies `POST /login/oauth/access_token` poll; returns `{access_token}` on success or `{error: "authorization_pending"\|"slow_down"}`. | CLI auth AC |

### MODIFIED routes (vskill-platform)

| Method | Path | Change |
|---|---|---|
| GET | `/api/v1/skills/*` (all 7 sub-paths) | Add hard `WHERE tenantId IS NULL` at the data-access layer via `publicSkillsQuery()` helper. App-layer code paths cannot opt out. |
| GET | `/api/v1/skills/search` | Same hard filter; also strip `tenantId` from any query parameter (request normalization). |
| POST | `/api/v1/submissions` (or whatever the existing submit path is) | Privacy ternary required; name-confirmation token validated; cross-validate `repoUrl` visibility against installation. (See ADR-NEW-4.) |
| POST | `/api/v1/webhooks/github` | Add event-type switch for `installation`, `installation_repositories`, `repository`. Add per-installation rate-limit counter (4500/hr cap). Reuse existing HMAC + DO dedup. |

### NEW server-side helpers (vskill-platform)

| Module | Exports | Purpose |
|---|---|---|
| `src/lib/github-app.ts` | `signAppJwt()`, `mintInstallationToken(installationId)` | RS256 JWT signing, token mint |
| `src/lib/installation-token.ts` | `getInstallationToken(tenantId)` | Cached token retrieval; refresh on miss/expiry; emits audit |
| `src/lib/envelope-crypto.ts` | `wrapDek(kek, dek)`, `unwrapDek(kek, wrapped)`, `encryptToken(dek, plaintext)`, `decryptToken(dek, ct, iv, tag)`, `generateDek()` | AES-KW + AES-GCM primitives |
| `src/lib/with-tenant.ts` | `withTenant(tenantId, userId): Promise<{role}>` | Membership assertion; throws `404` (not `401`) on miss |
| `src/lib/audit-log.ts` | `emitAudit(event)` | Fire-and-forget audit emitter with in-memory buffer + `waitUntil` flush |
| `src/lib/skills-repo.ts` | `publicSkillsQuery(filters)`, `privateSkillsQuery(tenantId, filters)` | Wrappers that enforce the public/private invariant |
| `src/lib/webhooks/handlers/installation.ts` | `handleInstallation(event)` | Tenant lifecycle (create/delete/suspend) |
| `src/lib/webhooks/handlers/installation-repositories.ts` | `handleInstallationRepositories(event)` | Repo selection changes |
| `src/lib/webhooks/handlers/repository.ts` | `handleRepository(event)` | Visibility flips (public ↔ private) |

### NEW CLI commands (vskill)

| Command | Purpose |
|---|---|
| `vskill auth login` | Device Flow; stores token in keychain |
| `vskill auth status` | Shows current GitHub account (login, scopes, expiry-if-known) |
| `vskill auth logout` | Clears keychain entry |

### MODIFIED CLI modules (vskill)

| Module | Change |
|---|---|
| `src/commands/add.ts` | Replace 13 raw `fetch(...)` calls with `githubFetch(url)` from new `src/lib/github-fetch.ts` which injects `Authorization: Bearer <keychain.token>` when available. |
| `src/eval-server/platform-proxy.ts` | Add `/api/v1/private/` and `/api/v1/tenants/` to `PROXY_PREFIXES`. In `pickHeadersForUpstream`, inject `Authorization: Bearer <keychain.token>` for these prefixes only. |
| `src/eval-server/api-routes.ts` | Add private-section route handlers (404 placeholder when not authed; pass-through when authed). |
| `src/commands/keys.ts` | Add `github` provider slot to the keys subcommand registry (so `vskill keys list` shows the GitHub auth status). |
| `src/lib/github-fetch.ts` (NEW) | `githubFetch(url, init?)`: injects auth header from keychain when present; preserves SSRF allowlist (`api.github.com`, `raw.githubusercontent.com`); central retry on 401 with `vskill auth login` hint message. |
| `src/lib/keychain.ts` (NEW) | `getGithubToken()`, `setGithubToken(t)`, `clearGithubToken()`. Wraps `@napi-rs/keyring`; falls back to `~/.vskill/keys.env` 0600. Emits a one-time warning when fallback is used. |
| `src/commands/auth.ts` (NEW) | The three subcommands above. |

---

## 5. Integration Points (file:line precision)

> Verified at plan-time against the current code in `repositories/anton-abyzov/{vskill-platform,vskill}/`. All line refs are accurate as of 2026-05-03; CI will re-verify.

### vskill-platform — files to MODIFY

| File:Line | Current behavior | Change |
|---|---|---|
| `src/lib/github-oauth.ts:49` | `scope=read:user` for the user OAuth flow | Unchanged — user OAuth stays for login. The App is a separate credential. |
| `src/app/api/v1/auth/github/callback/route.ts:53-73` | Exchanges code for token, fetches user, discards token | Unchanged — same user OAuth login flow. |
| `src/lib/popularity-fetcher.ts:114-119` | Bare `fetch(api.github.com/repos/...)` with optional `process.env.GITHUB_TOKEN` PAT | Wrap with `getInstallationToken(skill.tenantId)` when `skill.tenantId` is non-null; falls through to existing PAT path when public. |
| `src/lib/github-metrics.ts:47` (`fetchGitHubStars`) | Same pattern, optional token param | Caller must pass `await getInstallationToken(tenantId)` for private; existing public path unchanged. |
| `src/lib/github-metrics.ts:91` (`fetchGitHubMetricsDetailed`) | Same | Same. |
| `src/lib/repo-health-checker.ts:40` | Same with `User-Agent: vskill-platform` | Same wrapping pattern. |
| `src/lib/external-scan-dispatch.ts:150` | Uses `GITHUB_ACTIONS_TOKEN` env | Add a code path: when dispatching for a private skill, send the installation token instead so the GH Actions workflow can clone. (Token TTL = 1 hr; workflow must complete in time or re-mint via callback API.) |
| `src/app/api/v1/webhooks/github/route.ts:139-289` | HMAC verify + DO dedup + push-only | After `event !== "push"` short-circuit (line 214), add cases for `installation`, `installation_repositories`, `repository` BEFORE the 200-ignored return. Factor each handler into `src/lib/webhooks/handlers/*.ts` to keep the route lean. |
| `wrangler.jsonc` | Bindings for KV, Queues, DOs | Add NEW Queue producer/consumer `tenant-events`. Add NEW Workers Secrets: `VSKILL_GITHUB_APP_ID`, `VSKILL_GITHUB_APP_PRIVATE_KEY`, `VSKILL_GITHUB_APP_WEBHOOK_SECRET`, `VSKILL_TOKEN_KEK_V1`. (Optionally: `VSKILL_TOKEN_KEK_V2` slot kept empty for rotation.) |
| `prisma/schema.prisma` | (See section 3) | Append all new models; add `tenantId` + `privacy` to `Skill`. Single migration. |

### vskill-platform — files to CREATE

| New file | Purpose |
|---|---|
| `src/lib/github-app.ts` | JWT signing + installation token mint |
| `src/lib/installation-token.ts` | `getInstallationToken(tenantId)` with KV cache (50min TTL) |
| `src/lib/envelope-crypto.ts` | AES-KW + AES-GCM helpers; ESLint banner forbidding `console.log` of any function output |
| `src/lib/with-tenant.ts` | Membership assertion |
| `src/lib/audit-log.ts` | Fire-and-forget emitter + 14 named action constants |
| `src/lib/skills-repo.ts` | `publicSkillsQuery` + `privateSkillsQuery` |
| `src/lib/webhooks/handlers/installation.ts` | Handle `created`/`deleted`/`suspend`/`unsuspend` |
| `src/lib/webhooks/handlers/installation-repositories.ts` | Repo selection changes |
| `src/lib/webhooks/handlers/repository.ts` | Visibility flips |
| `src/app/api/v1/auth/github/installation/callback/route.ts` | Install redirect handler |
| `src/app/api/v1/auth/github/installation/uninstall/route.ts` | Manual uninstall |
| `src/app/api/v1/tenants/[tenantId]/skills/route.ts` | Private list |
| `src/app/api/v1/tenants/[tenantId]/skills/[slug]/route.ts` | Private detail |
| `src/app/api/v1/tenants/[tenantId]/audit-log/route.ts` | Audit viewer + CSV export |
| `src/app/api/v1/auth/device-flow/start/route.ts` | Device Flow proxy (start) |
| `src/app/api/v1/auth/device-flow/poll/route.ts` | Device Flow proxy (poll) |
| `src/app/orgs/[orgSlug]/page.tsx` | Org dashboard (private skills list) |
| `src/app/orgs/[orgSlug]/skills/[slug]/page.tsx` | Private skill detail page with persistent banner |
| `src/app/settings/integrations/page.tsx` | "Connect GitHub Org" flow + post-install state |
| `src/app/settings/audit-log/page.tsx` | Audit viewer UI |
| `src/components/PrivacyTernaryField.tsx` | Submit form privacy radio with name-confirmation logic |
| `src/components/PrivateBadge.tsx` | Amber lock badge |
| `src/components/PrivateBanner.tsx` | "PRIVATE — visible to <org> members only" banner |
| `tests/integration/cross-tenant-fuzz.test.ts` | 1000-query fuzz harness |
| `tests/unit/lib/envelope-crypto.test.ts` | TDD red→green unit tests |
| `tests/unit/lib/with-tenant.test.ts` | Membership unit tests |
| `tests/integration/webhook-installation.test.ts` | Webhook receiver round-trip |
| `tests/integration/installation-token-cache.test.ts` | KV cache hit/miss/refresh |

### vskill (CLI) — files to MODIFY

| File:Line | Change |
|---|---|
| `src/commands/add.ts:81` | `isGitHubDownloadUrl` allowlist unchanged (still `api.github.com` + `raw.githubusercontent.com`). |
| `src/commands/add.ts` (13 fetch sites: lines 107, 137, 152, 168, 258, 437, 548, 556, 576, 1131, 1523, 1580, 1627, plus 1727/1775/1799/2681 — verify exact count via `git grep -n "fetch(" src/commands/add.ts`) | Replace each with `githubFetch(url)` from new `src/lib/github-fetch.ts`. The helper inserts `Authorization: Bearer <keychain.token>` when the hostname is `api.github.com` or `raw.githubusercontent.com` AND a token is available. |
| `src/eval-server/platform-proxy.ts:91-100` | Extend `PROXY_PREFIXES` to include `/api/v1/tenants/` and `/api/v1/private/`. |
| `src/eval-server/platform-proxy.ts:103-116` | In `pickHeadersForUpstream`, when the path starts with `/api/v1/tenants/` or `/api/v1/private/`, read keychain token and set `Authorization: Bearer <token>`. Never log the token. |
| `src/commands/keys.ts` | Register `github` provider slot. |

### vskill (CLI) — files to CREATE

| New file | Purpose |
|---|---|
| `src/commands/auth.ts` | `vskill auth {login,status,logout}` subcommands |
| `src/lib/github-fetch.ts` | `githubFetch(url, init?)` with keychain auth injection |
| `src/lib/keychain.ts` | `@napi-rs/keyring` wrapper + 0600 fallback |
| `tests/unit/lib/github-fetch.test.ts` | Auth-injection unit tests (mock keychain) |
| `tests/unit/commands/auth.test.ts` | Device Flow happy + denied paths |

---

## 6. Cross-Cutting Concerns

### Token caching

- **Where**: `installation-token.ts` uses KV namespace `SUBMISSIONS_KV` (existing) under key `itoken:{tenantId}`. TTL = 50 minutes (10-minute safety margin before GitHub's 60-min expiry).
- **Cache shape**: `{token: string, expiresAt: number /* ms */}`. JSON-serialized, gzipped if needed.
- **Miss handling**: serialize per-tenant via a `Promise.all` cache in the Worker (one inflight refresh per tenant); 100 simultaneous request only mints one token.
- **Failure handling**: refresh failure → propagate `503 token_unavailable`; emit `AuditEvent("token.refresh", FAILURE)`; retry 30s later.

### Rate-limit budget

- **Per installation**: cap usage at 4,500 req/hr (90% of GitHub's 5,000 budget). Counter in KV `ratebudget:itoken:{tenantId}:{hour-bucket}`. When counter ≥ 4,500, queue rejects new requests with `429 rate_budget_exhausted` and `Retry-After: <seconds-until-next-hour>`.
- **Polling fallback**: heavy cron iterates installations; per-installation budget shared with on-demand fetchers. Skip installations at ≥80% utilization.
- **/search/code is forbidden**: ESLint rule + runtime guard in `github-fetch.ts` ban any URL containing `/search/code` (10/min hard cap from GitHub).
- **ETag everywhere**: `installation-token.ts` exposes a helper `conditionalGet(url, cachedSha?)` that sends `If-None-Match`. 304 responses don't count toward rate limit.

### Tenant-prefixed cache keys

- **Public**: existing prefixes (`skill:`, `search:`, `metrics:`).
- **Private**: ALL keys MUST start with `private:{tenantId}:`. Lint rule (custom ESLint plugin) rejects any `kv.put`/`kv.get` whose key argument is a string literal not matching `/^(skill|search|metrics|stats|...|private):/`.
- **Eviction**: on `installation.deleted` webhook, the consumer wipes `private:{tenantId}:*` via KV list-and-delete (cap 1000 keys per cron tick; iterates if >1000).

### Audit log emission points (14 actions)

| # | Action | Trigger | Actor |
|---|---|---|---|
| 1 | `installation.create` | Install callback success | USER |
| 2 | `installation.update` | Webhook `installation_repositories` (added/removed) | WEBHOOK |
| 3 | `installation.delete` | Webhook `installation` (deleted) OR manual uninstall | WEBHOOK / USER |
| 4 | `installation.suspend` / `installation.unsuspend` | Webhook | WEBHOOK |
| 5 | `token.refresh` | `getInstallationToken` cache miss/expiry | SYSTEM |
| 6 | `token.rotate` | KEK-rotation runbook step | SYSTEM |
| 7 | `private_skill.view` | `GET /api/v1/tenants/.../skills/[slug]` 200 | USER |
| 8 | `private_skill.clone` | Successful private skill download | USER / CLI |
| 9 | `private_skill.publish_attempt` | Submission submit (success / failure / denied) | USER |
| 10 | `member.role_change` | `OrgMember` role update from webhook | WEBHOOK |
| 11 | `auth.login` / `auth.failed` | OAuth callback success/failure | USER |
| 12 | `auth.cross_tenant_denied` | `withTenant` 404 for non-member | USER |
| 13 | `webhook.received` (at INFO) / `webhook.signature_invalid` (at WARN) | Webhook receiver | WEBHOOK |
| 14 | `repository.visibility_change` | Webhook `repository` (privatized/publicized) | WEBHOOK |

Action namespacing is dotted, lowercase, snake-cased after the verb. Constants in `src/lib/audit-log.ts` exported as `AUDIT_ACTIONS.INSTALLATION_CREATE` etc.

### Threat model — top 5

| # | Threat | Mitigation |
|---|---|---|
| 1 | Stolen Cloudflare API key (full account compromise) | KEK in Workers Secret (separate from D1/Postgres); CF API access does not grant Postgres access; quarterly rotation; alert on unusual API activity via existing 0807 alerts. |
| 2 | Stolen App private key | Workers Secret only; dual-key rotation (V1+V2 both valid during rollover); GitHub allows 5 pending private keys; documented runbook. |
| 3 | Cross-tenant cache leak via shared KV | Tenant-prefixed keys + lint rule + 1000-query CI fuzz test. |
| 4 | Webhook spoofing | HMAC verify before parse + constant-time compare + X-GitHub-Delivery atomic dedup via `WEBHOOK_DEDUP_DO`. |
| 5 | Session hijack → access another user's tenants | Existing httpOnly+Secure+SameSite=Lax cookies; `UserRefreshToken` already rotates per-use; require fresh re-auth (within 5 min) before sensitive ops (uninstall, audit export). |

### KEK rotation runbook

1. Provision new KEK as Workers Secret `VSKILL_TOKEN_KEK_V2`. Code path now reads V1 OR V2 (both exist for the rotation window).
2. Run a one-shot Worker job (manual cron-tick): for each `Tenant` where `dekVersion = 1`, unwrap DEK with V1, re-wrap with V2, set `dekVersion = 2`. Done in batches of 100 tenants/sec; job emits AuditEvent per batch.
3. Wait 24h for any in-flight references to settle.
4. Drop V1 from Workers Secret. Rollback path: keep V1 stashed in 1Password until +30d.

---

## 7. Migration & Rollout

### Feature flag

`ENABLE_PRIVATE_REPOS` env var (Workers env binding):

- `false` (default): new routes return `404`. Submission form privacy radio defaults to PUBLIC. CLI `auth login` surfaces "feature in private beta" message.
- `true`: full feature available.

### Database migration order

1. `prisma migrate deploy` for new schema migration.
2. Provision `VSKILL_TOKEN_KEK_V1` via `wrangler secret put`.
3. Register the GitHub App; capture App ID + private key + webhook secret.
4. Provision `VSKILL_GITHUB_APP_*` secrets via `wrangler secret put`.
5. Deploy worker with `ENABLE_PRIVATE_REPOS=false`.
6. Run smoke test against staging.
7. Flip flag to `true` for design partners (allowlist by `userId`).

### 3 design partners → GA

- **Phase A (week 4)**: 3 design partners onboard via direct Anton outreach. Free tier caps lifted for them. Daily check-ins.
- **Phase B (week 5)**: address blockers; ship UI polish.
- **Phase C (week 6)**: GA flag flip; announcement post.

### Rollback plan

- Feature-flag flip to `false` disables all NEW routes; existing data is untouched.
- DB rollback: drop new tables (data loss for installations — acceptable in private beta).
- KEK rotation: V2 stays valid; V1 rollback impossible because we drop V1 plaintext after rotation. Mitigation: the Workers Secret value is itself stashed in 1Password.

---

## 8. Testing Strategy

### Unit (Vitest, target ≥95%)

| Module | Tests |
|---|---|
| `envelope-crypto.ts` | Round-trip encrypt/decrypt; tamper detection (mutate ciphertext → AES-GCM authTag failure); KEK rotation (V1 wrap → V2 unwrap → V1 unwrap fail); reject empty key; reject undersized DEK. |
| `github-app.ts` | JWT correctness (`iat`, `exp`, `iss`); RS256 signature verifiable with public key derived from private; reject `exp > iat + 10min`. |
| `with-tenant.ts` | Member returns role; non-member throws 404; missing tenant throws 404; SQL injection-safe parameter binding (Prisma handles, but assertion test). |
| `audit-log.ts` | Buffer overflow flushes synchronously; `waitUntil` invocation; metadata redaction (no token-typed values pass through). |
| `installation-token.ts` | Cache hit; cache miss → mint; expiry-near refresh; concurrent requests → single mint (mock 100 callers); failure → 503. |
| `github-fetch.ts` (CLI) | Auth header injected when token present; not injected when host outside allowlist; clear error message on 401. |

### Integration (Vitest with miniflare/test bindings)

| Surface | Tests |
|---|---|
| `/api/v1/webhooks/github` | Valid `installation.created` → Tenant created + audit event; replay (same X-GitHub-Delivery) → 200 duplicate; bad signature → 401; missing X-GitHub-Delivery → 400; missing DO binding → 503; `installation_repositories.added` → updates Installation; `repository.privatized` → flips Skill.privacy. |
| `/api/v1/auth/github/installation/callback` | Successful install creates Tenant + Installation + AuditEvent; user not authed → redirect to login; cross-user attempt (session A, install_id B) → 403. |
| `/api/v1/tenants/[tenantId]/skills` | Member access → 200; non-member → 404 (NOT 401); query params honored; cap enforcement at submission. |

### E2E (Playwright)

| Scenario | Steps | Pass criteria |
|---|---|---|
| Install flow | Sign in → `/settings/integrations` → "Connect GitHub Org" → mock-GitHub install → callback → Tenant visible in nav | Tenant row exists in DB; nav shows org name; audit log shows `installation.create`. |
| Private skill view | Authed as member of tenant → `/orgs/acme/skills/internal-deploy` → page renders | "PRIVATE" banner present; tab title `[Private] ...`; no "Edit on GitHub" public link. |
| Anti-mistake publish | Submit form with private repo + privacy=PUBLIC → server rejects | `400 repo_visibility_mismatch`; UI shows actionable error. |
| Cross-tenant browse | Authed as member of T1 → `/orgs/T2/skills/x` | 404 page; AuditEvent `auth.cross_tenant_denied`. |
| CLI auth | `vskill auth login` → device code + URL → simulated visit → `vskill auth status` | Status shows GitHub login. |
| CLI add private | `vskill auth login` → `vskill add https://github.com/acme-corp/internal-deploy` | Skill installed locally; Authorization header sent. |

### Security fuzz

| Test | Iterations | Pass criteria |
|---|---|---|
| Cross-tenant query fuzz (`tests/integration/cross-tenant-fuzz.test.ts`) | 1000 random `(public_route, random_tenant_id)` pairs | Zero private rows ever appear in public results. |
| Webhook signature fuzz | 1000 mutated payloads (bit-flips, length extensions, replay with stale UUID) | 100% reject rate. |
| KV key prefix lint | `eslint-plugin-private-cache-keys` (custom) | All `kv.put`/`kv.get` calls use a recognized prefix. |

### Coverage targets

- Unit: ≥95% lines on new modules.
- Integration: ≥90% of route handlers exercised end-to-end.
- E2E: 100% of AC scenarios covered.

---

## 9. References

- Approved plan: `~/.claude/plans/squishy-scribbling-haven.md`
- Interview state: `.specweave/state/interview-0826-skill-studio-private-repos.json`
- Existing webhook receiver: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts`
- Existing dedup DO: `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/webhook-dedup-do.ts`
- Existing webhook auth helper: `repositories/anton-abyzov/vskill-platform/src/lib/webhook-auth.ts`
- Existing user OAuth: `repositories/anton-abyzov/vskill-platform/src/lib/github-oauth.ts`
- Existing GitHub fetchers: `popularity-fetcher.ts`, `github-metrics.ts`, `repo-health-checker.ts`, `external-scan-dispatch.ts`
- Existing CLI fetch sites: `repositories/anton-abyzov/vskill/src/commands/add.ts` (13+ sites)
- Existing platform proxy: `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts`
- Existing wrangler config: `repositories/anton-abyzov/vskill-platform/wrangler.jsonc`

---

**Document status**: Draft — pending PM agent's spec.md to confirm AC IDs and any UX refinements. Architecture decisions in this plan are independent of spec.md text and remain valid regardless of which AC IDs the PM ultimately assigns.
