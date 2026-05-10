# Plan: WorkOS SSO + SCIM + Audit Log UI

**Increment**: 0842-workos-sso-enterprise
**Repository**: `repositories/anton-abyzov/vskill-platform`
**Stack**: Next.js 15 (App Router), Cloudflare Workers (OpenNext), Prisma, Postgres, Vitest, Playwright

> **Activation reminder**: this plan is cold. Re-read [`spec.md`](spec.md) §1 (Trigger and Gating) before doing anything. Pin `@workos-inc/node` to the latest version on activation day and update §6 below.

---

## 1. Architecture Overview

```
                ┌──────────────────────────────────────────────────────────┐
                │                  Buyer's IT (browser)                     │
                │                                                            │
                │   1. /auth/sso?org=acme   2. callback   3. /account/sso   │
                └──────────────┬───────────────┬────────────────┬───────────┘
                               │ 302           │ GET            │ click "Configure"
                ┌──────────────▼───────────────▼────────────────▼───────────┐
                │            verified-skill.com (Cloudflare Worker)          │
                │                                                            │
                │  src/app/auth/sso/page.tsx           ─────┐                │
                │  src/app/api/v1/auth/sso/callback        ─┤  WorkOS SDK    │
                │  src/app/api/v1/auth/sso/portal-link     ─┤  @workos-inc/  │
                │  src/app/api/v1/auth/scim/webhook        ─┤  node          │
                │                                            │                │
                │  middleware.ts (tier gate ENTERPRISE-only) │                │
                │  src/lib/workos/{client,scim-handler}.ts   │                │
                └────────────────────────────────────────────┼────────────────┘
                                                              ▼
                                                    ┌──────────────────┐
                                                    │     WorkOS       │
                                                    │  (SAML, SCIM,    │
                                                    │   Admin Portal)  │
                                                    └────────┬─────────┘
                                                              │ SCIM webhooks (signed)
                                                              ▼
                                                    POST /api/v1/auth/scim/webhook
```

**Trust boundary**: WorkOS is source of truth for IdP connection state, SAML cert rotation, SCIM event delivery. We mirror only `ssoConnectionId` and `workosOrganizationId`.

## 2. File Plan

### Schema (`prisma/schema.prisma`)

```prisma
model Tenant {
  id                    String  @id @default(cuid())
  // ... existing fields
  ssoConnectionId       String? @unique               // WorkOS Connection ID
  workosOrganizationId  String? @unique               // WorkOS Organization ID
  scimGroupMapping      Json?                         // { "<dirGroupId>": "OWNER|ADMIN|MEMBER" }
}

model User {
  id                String           @id @default(cuid())
  // ... existing fields
  workosUserId      String?          @unique
  identityProvider  IdentityProvider @default(EMAIL)
  deletedAt         DateTime?
}

enum IdentityProvider {
  GITHUB
  SSO
  EMAIL
}

model WorkosEvent {
  id          String   @id @default(cuid())
  eventId     String   @unique
  eventType   String
  receivedAt  DateTime @default(now())
  processedAt DateTime?
  payload     Json
  lastError   String?
  attempts    Int      @default(0)

  @@index([eventType, receivedAt])
}
```

Migration name: `20260509_workos_sso_enterprise`. Additive; reversible.

### New code

| Path | Purpose |
| --- | --- |
| `src/lib/workos/client.ts` | `getWorkOSClient()` returns a singleton `WorkOS` instance reading env secrets. Uses fetch HTTP client (Cloudflare-compatible). |
| `src/lib/workos/scim-handler.ts` | `handleScimEvent(event)` — central dispatch for `dsync.user.{created,updated,deleted}`. Idempotent via `WorkosEvent` upsert. |
| `src/lib/workos/group-mapping.ts` | `resolveRoleForUser(tenant, dirGroupIds): OrgRole` — applies `scimGroupMapping` JSON, defaults to `MEMBER`, enforces last-owner safeguard. |
| `src/lib/workos/state-jwt.ts` | Sign / verify the SSO state JWT (tenantId + nonce + exp). HS256 with internal secret. |
| `src/app/auth/sso/page.tsx` | Public SSO entry (server component). Resolves tenant, 404s when not configured, 302s to WorkOS authorize URL. |
| `src/app/api/v1/auth/sso/callback/route.ts` | OAuth callback. Verifies state JWT, exchanges code for profile, upserts User, links OrgMember, mints session JWT, sets cookie. |
| `src/app/api/v1/auth/sso/portal-link/route.ts` | POST — issues WorkOS Admin Portal link. Lazy-creates `workosOrganizationId`. Audit emits hash only. |
| `src/app/api/v1/auth/scim/webhook/route.ts` | POST — signature verify (FIRST), idempotency check, dispatch to `scim-handler`. |
| `src/app/account/orgs/[tenantId]/sso/page.tsx` | Tenant settings: "Configure SSO" button + connection status. Enterprise-only. |
| `src/app/account/orgs/[tenantId]/audit-log/page.tsx` | Audit log viewer. Server component shell + `AuditLogClient.tsx` for filters/pagination. |
| `src/app/account/orgs/[tenantId]/audit-log/AuditLogClient.tsx` | Client component: filters (action, actor typeahead, date range), table, export buttons. |
| `src/app/admin/tenants/[tenantId]/provision-enterprise/route.ts` | Ops-only POST — flips tier, attaches Stripe sub, audit. Requires `confirm: true` + `loiReference`. |
| `src/app/admin/tenants/[tenantId]/downgrade/route.ts` | Ops-only POST — flips tier back, preserves WorkOS IDs. |
| `src/app/auth/error/page.tsx` (extend) | Surface `?reason=<code>` for SSO failures. |
| `middleware.ts` (extend) | Add tier-gate matcher for `/account/orgs/[tenantId]/(sso\|audit-log)` — 403 if `tenant.tier !== 'ENTERPRISE'`. |

### Tests

| Path | Layer |
| --- | --- |
| `tests/unit/workos/scim-handler.test.ts` | All four event types, idempotency replay, group-mapping fallback, last-owner safeguard. |
| `tests/unit/workos/group-mapping.test.ts` | Mapping with/without match, defaults, owner protection. |
| `tests/unit/workos/state-jwt.test.ts` | Sign/verify roundtrip, expired token rejection, tampering rejection. |
| `tests/unit/api/sso-callback.test.ts` | State mismatch → /auth/error; first SSO login creates User + OrgMember; existing GitHub user linked by email; identityProvider not downgraded. |
| `tests/unit/api/scim-webhook.test.ts` | Unsigned body → 401 without DB read; signed → dispatch; replay returns 200 fast. |
| `tests/unit/middleware/tier-gate.test.ts` | Non-Enterprise hitting /sso, /audit-log → 403; Enterprise → 200. |
| `tests/integration/migration.test.ts` | Apply + rollback `20260509_workos_sso_enterprise`. |
| `tests/integration/scim-end-to-end.test.ts` | Full create/update/delete flow against test DB. Verifies AuditEvent rows preserved on user.deleted. |
| `tests/e2e/sso-sign-in.spec.ts` | Playwright: mock WorkOS hosted login → callback → /dashboard with session cookie. |
| `tests/e2e/audit-log-ui.spec.ts` | Playwright: filter by action, paginate, export CSV; verify export emits audit event. |
| `tests/e2e/sso-tier-gate.spec.ts` | Playwright: PRO tenant hitting /sso → paywall card, link to /pricing. |

### Docs / runbooks

| Path | Purpose |
| --- | --- |
| `.specweave/docs/internal/architecture/adr/ADR-NEW-001-workos-vs-diy-saml.md` | Buy decision rationale. |
| `.specweave/docs/internal/architecture/adr/ADR-NEW-002-scim-deprovision-strategy.md` | Soft-delete + OrgMember disconnect; preserve AuditEvent 7y. |
| `.specweave/dev/workos-tunnel.md` | Cloudflare tunnel + WorkOS sandbox local dev runbook. |
| `.specweave/dev/workos-orphan-connection-reconcile.md` | Monthly ops script to flag billable connections without active Enterprise tenant. |

## 3. ADRs

### ADR-NEW-001 — Buy WorkOS vs build SAML in-house

**Status**: Proposed (decision: buy).

**Context**: Enterprise buyers demand SAML SSO + SCIM. Building in-house means per-IdP integration tickets (Okta, Azure AD, Google, OneLogin, Ping, JumpCloud) — each with cert rotation, AssertionConsumerService URLs, ID format quirks, and SP metadata negotiation. SCIM 2.0 is its own spec with attribute mapping idiosyncrasies. Realistic estimate: 2-4 engineering months for a working SAML + SCIM stack, plus ongoing maintenance for IdP edge cases.

**Decision**: Buy WorkOS. They normalize SAML across all major IdPs, expose one SDK call (`getAuthorizationUrl`), one webhook stream (`workos.events`), and one Admin Portal handoff. Pricing is $125/connection/month at list. Customer-funded — Enterprise tier prices in this cost. Used by Cursor Teams, Continue.dev Team, Linear, Notion, and most modern dev-tool platforms.

**Consequences**:
- We do NOT own SAML cert rotation, AssertionConsumerService routing, or SCIM attribute parsing.
- We DO own the trust boundary: signature verification on inbound webhooks, audit logging on every action, tier gating on UI.
- Vendor lock-in is real but acceptable: migration to a competitor (Auth0, FusionAuth, in-house) would mean re-issuing portal links and re-onboarding IdPs. Mitigation: keep `Tenant.workosOrganizationId` separate from any internal IDs so swap-out is a one-column migration.
- Compliance-wise, WorkOS is SOC 2 Type II — they cover the IdP integration leg of our future SOC 2.

### ADR-NEW-002 — SCIM auto-deprovision: soft-delete + OrgMember disconnect

**Status**: Proposed (decision: soft-delete).

**Context**: SCIM `dsync.user.deleted` fires when an IT admin removes a user from the IdP group. Three options:
1. Hard-delete User row (and cascade-delete projects, audit events, etc.).
2. Soft-delete User (`deletedAt`), disconnect `OrgMember` for this tenant only, preserve everything else.
3. Disconnect `OrgMember` only, leave User row untouched.

**Decision**: Option 2.

**Why**:
- Hard-delete (option 1) destroys audit trail. Compliance-fatal — buyer's vendor risk team needs the 7-year audit retention from 0826.
- OrgMember-only (option 3) leaves `User.deletedAt = null`, so the user could still authenticate via personal GitHub login if they ever had one. For an off-boarded employee this is wrong: the IT admin's intent is "this person is gone".
- Soft-delete + OrgMember disconnect (option 2): user can no longer sign in (auth checks `deletedAt`), tenant-specific audit history preserved, AuditEvent rows for that user remain queryable, other tenants the user belongs to are unaffected (membership scoped per tenant).

**Consequences**:
- Auth path must check `User.deletedAt IS NULL` on session validation — add to existing JWT verification middleware.
- Audit log queries should still resolve `actorId` to email even when User is soft-deleted (display "alice@acme.com (deactivated)").
- Users who appear in multiple tenants are partially deactivated when one tenant deprovisions them. This is intentional — SCIM events are tenant-scoped, not global.
- Re-provisioning (user re-added to IdP group) clears `deletedAt` and recreates `OrgMember`.

## 4. Tier Gate (middleware)

`middleware.ts` matcher additions:

```ts
const ENTERPRISE_PATHS = [
  /^\/auth\/sso(\?|$)/,
  /^\/account\/orgs\/[^/]+\/sso/,
  /^\/account\/orgs\/[^/]+\/audit-log/,
];

if (ENTERPRISE_PATHS.some(re => re.test(pathname))) {
  const tenant = await resolveTenantForRequest(req);
  if (!tenant || tenant.tier !== 'ENTERPRISE') return NextResponse.redirect(new URL('/pricing?gate=enterprise', req.url));
}
```

`/auth/sso?org=<slug>` is a public route but tenant-scoped; the gate resolves by `org` query param rather than session.

`/audit-log` adds an additional check: requesting user must be `OrgMember.role IN ('OWNER', 'ADMIN')` for that tenant — that check lives in the page route handler, not middleware (needs DB lookup).

## 5. Audit Events Added

| Event | Source | Notes |
| --- | --- | --- |
| `tenant.sso.connection_linked` | US-001 | Manual/admin action |
| `tenant.sso.connection_unlinked` | US-001 | Manual/admin action |
| `tenant.sso.portal_link_issued` | US-003 | Stores hash, never URL |
| `tenant.tier.upgraded` | US-006 | reason: `enterprise_loi`, includes loiReference |
| `tenant.tier.downgraded` | US-006 | |
| `tenant.member.added` | US-004 | source: `scim` |
| `tenant.member.removed` | US-004 | source: `scim` |
| `tenant.scim.owner_demote_blocked` | US-004 | Last-owner safeguard |
| `tenant.scim.email_collision` | US-004 | Skipped collision |
| `tenant.audit_log.exported` | US-005 | Format: csv \| json |
| `auth.sso.failed` | US-002 | reason from WorkOS |
| `auth.sso.state_mismatch` | US-002 | Replay/tamper detection |
| `auth.provider.linked` | US-002 | GitHub user signs in via SSO |

All flow through existing 0826 AuditEvent emitter. No new storage.

## 6. Dependencies (pin at activation)

- `@workos-inc/node` — record exact version on activation day. Latest stable at spec write: TBD.
- `jose` — already in project for JWT signing/verification (used for state JWT).
- No other new deps.

## 7. Secrets

Cloudflare Worker secrets via `wrangler secret put`:
- `WORKOS_API_KEY`
- `WORKOS_CLIENT_ID`
- `WORKOS_WEBHOOK_SECRET`
- `WORKOS_REDIRECT_URI` (production) — `https://verified-skill.com/api/v1/auth/sso/callback`
- `STRIPE_ENTERPRISE_PRICE_ID` (already provisioned in 0840 if Enterprise SKU exists; if not, create at activation)

Add to `.specweave/dev/secrets-checklist.md`. CI lint: regex match on `WORKOS_` outside `wrangler.toml`, `.env.local` (gitignored), and this plan.

## 8. Local Dev Setup (runbook stub for `.specweave/dev/workos-tunnel.md`)

1. `npm i -D @workos-inc/node` (after pinning).
2. `wrangler secret put WORKOS_API_KEY` (sandbox key from WorkOS dashboard).
3. `cloudflared tunnel --url http://localhost:3000` — get a tunnel URL.
4. In WorkOS dashboard → Webhooks → set endpoint to `https://<tunnel>.trycloudflare.com/api/v1/auth/scim/webhook`.
5. Connect a free Okta dev tenant in WorkOS sandbox.
6. Add yourself to an Okta group; verify SCIM event fires; verify OrgMember row appears.
7. Visit `https://<tunnel>.trycloudflare.com/auth/sso?org=<your-staging-tenant-slug>`; complete IdP login; land on /dashboard.

## 9. Rollout

1. **Pre-LOI** (now): spec frozen, plan committed, status `planned`. No code.
2. **LOI signed**: Anton flips `metadata.json` status to `active`. Pin SDK version. Re-validate spec for drift.
3. **Sprint 1 (3-5 days)**: schema migration on staging, WorkOS client, state JWT, SSO sign-in route + callback, tier gate. E2E sign-in green on staging with WorkOS sandbox.
4. **Sprint 2 (3-5 days)**: SCIM webhook handler, group mapping, owner-demote safeguard, idempotency. Integration tests green.
5. **Sprint 3 (2-3 days)**: Admin Portal handoff UI, audit log UI, exports. Tier gate UI mirroring.
6. **Sprint 4 (1-2 days)**: ops `/admin/provision-enterprise` + `/downgrade`, runbooks, weekly Playwright cron against acme-staging.
7. **Manual gate**: Anton signs in via real Okta dev tenant. SCIM joiner/leaver verified. Audit log export downloads correct CSV.
8. **Production cutover**: provision the LOI customer's WorkOS Organization, hand them the portal link, monitor for the first week.

## 10. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| WorkOS bill spikes from orphan connections (dev tests, abandoned setups) | Monthly reconciliation script (out of scope v1, runbook in §2). |
| WorkOS SDK drift between spec and ship date | Re-pin on activation; spec mandates re-read of [§1](spec.md#1-trigger-and-gating-read-first). |
| SCIM webhook delivery delay > 5 minutes | Surfaced as known limitation in tenant settings copy; if it becomes real pain, queue + Cloudflare Queue follow-up. |
| Last-owner deprovisioning by IdP | Safeguard in `group-mapping.ts`; emits audit; ops-recoverable via admin tier flip. |
| Vendor lock-in to WorkOS | Tenant.workosOrganizationId isolated; migration path documented in ADR-NEW-001. |
| Compliance reviewer asks for SOC 2 before LOI | Punt: spec §5 says SOC 2 is post-LOI. If they need it pre-LOI, increment 0842 is moot — bigger compliance increment first. |

## 11. Out of Scope (Reaffirmed from spec.md §5)

- DIY SAML / OIDC.
- SOC 2 Type II audit prep.
- Custom hosted SSO domain.
- Multi-IdP per tenant.
- JIT provisioning bypassing SCIM.
- Group-mapping admin UI (JSON-edit-by-ops in v1).
- Hard-delete on SCIM user removal.
- Audit log retention beyond 7 years.

## 12. Definition of Done (cross-references spec.md §12)

- [ ] All 7 user stories' ACs pass automated tests (unit 95%, integration 90%, E2E 100% of US-002/004/005).
- [ ] Manual verification gate: Anton signs in via real Okta dev tenant; SCIM joiner/leaver verified end-to-end.
- [ ] ADR-NEW-001 and ADR-NEW-002 committed.
- [ ] `/sw:grill` and `/sw:judge-llm` reports clear (or judge-llm waived with consent).
- [ ] Weekly Playwright cron (`acme-staging` E2E) green for 7 consecutive days before declaring stable.
- [ ] WorkOS bill at end of month 1 reflects only billable connections (no orphans).
- [ ] Rollback runbook (`.specweave/dev/workos-rollback.md`) drafted: how to disable `/auth/sso` and `/audit-log` routes if production incident.
