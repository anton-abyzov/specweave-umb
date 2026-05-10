# Spec: WorkOS SSO + SCIM + Audit Log UI (Enterprise Tier)

**Increment**: 0842-workos-sso-enterprise
**Phase**: P4 — Enterprise readiness
**Priority**: P4 (gated; cold spec)
**Status**: planned (may stay planned indefinitely)
**Repository**: `repositories/anton-abyzov/vskill-platform`

---

## 1. Trigger and Gating (READ FIRST)

**This increment does NOT begin implementation on creation.**

- **Trigger**: First paying enterprise Letter of Intent (LOI). Until that moment, the spec is a "drawer-ready" plan — fully specified, dependencies wired, but `status: planned`.
- **Why gated**: WorkOS list price is $125/connection/month. Each Enterprise customer recoups it many-fold, but pre-revenue we should not pay for an empty pool. SOC 2 Type II is a separate multi-month compliance track and is explicitly **out of scope here**.
- **Stay-planned policy**: This increment may sit in `planned` for weeks or months. Do NOT auto-promote it on schedule, on cron, or because it is the next number in line. The team-lead / Anton must explicitly flip `status` to `active` once an LOI is signed (or a serious enterprise pilot agrees in writing to underwrite the WorkOS bill).
- **Re-validation on activation**: Before flipping to `active`, re-read this spec end-to-end. WorkOS pricing, SDK shape, and our schema may have drifted; budget half a day to refresh.

## 2. Dependencies

| Increment | What it provides | Why this increment needs it |
| --- | --- | --- |
| **0840-stripe-billing-mvp** | Tier model (FREE/PRO/TEAM/ENTERPRISE), Stripe subscription on Tenant, `tenant.tier` field | Enterprise gating in middleware reads `tenant.tier === ENTERPRISE`. No tier model = no gate. |
| **0841-per-org-seat-licensing** | `OrgMember`, `OrgRole`, seat counts, per-org billing | SCIM provisions OrgMember rows; without the multi-org membership model SCIM has nowhere to write. |
| **0826-skill-studio-private-repos** | `AuditEvent` model + 14 action types + 7-year R2 retention + `/api/v1/tenants/[tenantId]/audit-log` and `/export` endpoints | This increment adds the **UI surface only**. The data layer is already live. |

**Hard rule**: do not begin 0842 implementation while 0840 or 0841 are not closed. The schema migrations interleave (0841 adds OrgMember, 0842 references it from SCIM handler). 0826 is already closed.

## 3. Problem Statement

Enterprise buyers (companies with > ~50 paying seats, IT-led purchasing, SOC 2 / ISO27001 vendor reviews) refuse to onboard a SaaS product that:

1. Forces every IT user to keep an extra password (no SSO).
2. Requires manual user provisioning when an employee joins or leaves (no SCIM).
3. Cannot show "who did what when" over the last 12 months in their own UI (audit log buried in our database).

This is industry-table-stakes for B2B SaaS. The same vendor that solves it for Cursor Teams, Continue.dev Team, Linear, Notion, and most modern dev-tool platforms is **WorkOS** — it terminates SAML against any IdP (Okta, Azure AD, Google Workspace, OneLogin, Ping, JumpCloud) and exposes a single normalized profile + a single SCIM webhook stream. We BUY rather than BUILD.

## 4. Goals

- Enterprise tenants complete IdP setup self-serve via WorkOS Admin Portal handoff (no engineering touch per customer).
- Their users sign in at `/auth/sso?org=<slug>` and land in an authenticated session, identical to a GitHub OAuth login session.
- Adding/removing a user from the IdP group propagates to our `OrgMember` rows within minutes (SCIM webhook).
- Org admins view and export the audit log for their tenant, filtered by action / actor / time, surfaced from the existing data layer.
- Tier gate is enforced server-side; non-Enterprise tenants cannot reach `/sso` or `/audit-log` UIs.
- We pay $125/connection/month only when a connection is actually attached to a paying tenant.

## 5. Non-Goals (Out of Scope)

- **DIY SAML / OIDC.** No `samlify`, no `passport-saml`, no per-IdP integration tickets. ADR-NEW-001 records this.
- **SOC 2 Type II audit.** Compliance track. Starts only after first enterprise LOI. Separate increment.
- **Custom hosted SSO domain** (e.g. `sso.acme.com`). WorkOS supports it but is a paid add-on; not requested.
- **Group-mapping admin UI.** Per-tenant directory-group → `OrgRole` mapping is configured via JSON in `Tenant.scimGroupMapping` — no UI editor in v1.
- **Audit log retention beyond 7 years.** 0826 already standardized 7y on R2; we re-use.
- **Hard-delete on SCIM `user.deleted`.** We soft-delete via `User.deletedAt` and disconnect `OrgMember`; AuditEvent rows preserved.
- **Multi-IdP per tenant.** One Tenant ↔ one `ssoConnectionId`. Not exposed.
- **JIT provisioning without SCIM.** SCIM is the contract.

## 6. Personas

- **IT admin (buyer's side)**: configures Okta / Azure AD against a WorkOS Admin Portal link emailed to them. Never logs into our app.
- **Enterprise end-user**: opens `https://verified-skill.com/auth/sso?org=acme`, gets bounced through their IdP, lands signed in.
- **Tenant owner (our customer's project owner)**: clicks "Configure SSO" in `/account/orgs/:tenantId/sso`, hands the portal link to IT, monitors the audit log.
- **Anton / ops**: provisions Enterprise tier post-LOI via `/admin/tenants/:tenantId/provision-enterprise`.
- **Compliance reviewer (buyer's vendor risk)**: requests audit log export; tenant owner downloads CSV/JSON and emails it.

## 7. User Stories

### US-001 — `Tenant.ssoConnectionId` mirrors WorkOS Connection
**As** a tenant owner of an Enterprise tier tenant
**I want** my tenant row to point at a WorkOS Connection
**So that** the SSO sign-in flow can resolve my tenant slug → IdP → session

**Acceptance Criteria**
- [ ] AC-US1-01: `Tenant.ssoConnectionId String? @unique` migration applied; nullable for non-Enterprise tenants.
- [ ] AC-US1-02: WorkOS is treated as source of truth for connection state (active, pending, revoked); we mirror only the ID. We never cache the IdP cert/config.
- [ ] AC-US1-03: Setting/unsetting `ssoConnectionId` writes a `tenant.sso.connection_linked` / `tenant.sso.connection_unlinked` audit event.
- [ ] AC-US1-04: Disabling Enterprise tier (downgrade) does NOT delete `ssoConnectionId` — it just makes the `/auth/sso` route 403. Re-upgrading reactivates.
- [ ] AC-US1-05: Schema migration is reversible (down migration drops the column without data loss; existing rows are nullable).

### US-002 — SSO sign-in route at `/auth/sso`
**As** an enterprise end-user
**I want** to sign in via my company IdP at a stable URL
**So that** I never have to remember a password specific to this product

**Acceptance Criteria**
- [ ] AC-US2-01: `GET /auth/sso?org=<slug>` resolves Tenant by slug; if `tenant.ssoConnectionId` is null → 404 with copy "SSO not configured for this organization".
- [ ] AC-US2-02: With a valid connection, the route calls `workos.sso.getAuthorizationUrl({ connection: tenant.ssoConnectionId, redirectUri, state })` and 302-redirects. `state` is a signed JWT containing `tenantId` + nonce; verified on callback.
- [ ] AC-US2-03: Callback `GET /api/v1/auth/sso/callback?code=...&state=...` verifies state JWT, calls `workos.sso.getProfileAndToken({ code })`, upserts User by `(workosUserId)` then by `email` fallback, links `OrgMember(tenantId, userId, role: MEMBER)` if missing, mints our JWT identical to GitHub callback path, sets cookie, redirects to `/dashboard`.
- [ ] AC-US2-04: `User.identityProvider` enum (`GITHUB | SSO | EMAIL`) — SSO logins set it to `SSO`. Existing GitHub users who later sign in via SSO are linked by email with an `auth.provider.linked` audit event but `identityProvider` is NOT downgraded.
- [ ] AC-US2-05: Failed callback (state mismatch, expired code, WorkOS error) → redirect to `/auth/error?reason=<code>` with the WorkOS error code surfaced; emit `auth.sso.failed` audit event with the reason.
- [ ] AC-US2-06: Session cookie attributes match GitHub flow (`Secure`, `HttpOnly`, `SameSite=Lax`, 30-day expiry).

### US-003 — WorkOS Admin Portal handoff
**As** a tenant owner
**I want** a one-click button that gives my IT admin a configuration link
**So that** I can hand off SSO setup without engineering tickets

**Acceptance Criteria**
- [ ] AC-US3-01: `/account/orgs/:tenantId/sso` page renders only for `tenant.tier === 'ENTERPRISE'`. Other tiers see a paywall card linking to `/pricing`.
- [ ] AC-US3-02: "Configure SSO" button calls `POST /api/v1/auth/sso/portal-link` which proxies to `workos.organizations.createPortalLink({ organization: tenant.workosOrganizationId, intent: 'sso' })`. Server response includes the portal URL and a 5-minute expiry timestamp.
- [ ] AC-US3-03: Clicking opens the URL in a new tab (`target="_blank" rel="noopener noreferrer"`); the link is one-time-use per WorkOS docs.
- [ ] AC-US3-04: Portal-link generation writes audit event `tenant.sso.portal_link_issued` with `actorId` and a redacted link hash (never the full URL — it is a credential).
- [ ] AC-US3-05: If `tenant.workosOrganizationId` is null, the API auto-creates a WorkOS Organization (`workos.organizations.createOrganization({ name: tenant.name, externalId: tenant.id })`) and persists the returned ID before issuing the portal link.

### US-004 — SCIM Directory Sync
**As** an IT admin
**I want** my IdP's directory (group memberships, joiners, leavers) to be the source of truth for who has access
**So that** off-boarding takes effect within minutes without filing a ticket

**Acceptance Criteria**
- [ ] AC-US4-01: WorkOS webhook receiver at `POST /api/v1/auth/scim/webhook` validates signature via `workos.events.verifyHeader(rawBody, signatureHeader, WORKOS_WEBHOOK_SECRET)` BEFORE parsing; invalid signatures → 401.
- [ ] AC-US4-02: Handler is idempotent — keyed on `(eventId)` stored in a `WorkosEvent` table with unique index; replays are no-ops.
- [ ] AC-US4-03: `dsync.user.created` → upsert User by `email`, create `OrgMember(tenantId, userId, role)` where role comes from group mapping (see AC-US4-05). Emits `tenant.member.added` audit event with `source: 'scim'`.
- [ ] AC-US4-04: `dsync.user.deleted` → set `User.deletedAt = now()`, remove all `OrgMember` rows for this user **scoped to this tenant only**, preserve all `AuditEvent` records (7y retention). Emits `tenant.member.removed` audit event with `source: 'scim'`. Other tenants the user belongs to are unaffected.
- [ ] AC-US4-05: `Tenant.scimGroupMapping Json?` stores `{ "<groupId>": "OWNER" | "ADMIN" | "MEMBER" }`. Default if no mapping or no match → `MEMBER`. Owners cannot be demoted by SCIM if they are the last owner of the tenant — emits `tenant.scim.owner_demote_blocked` audit and skips the role change.
- [ ] AC-US4-06: `dsync.user.updated` events that change group membership re-evaluate role per AC-US4-05. Email changes update `User.email`; uniqueness collisions log `tenant.scim.email_collision` and skip.
- [ ] AC-US4-07: Webhook latency budget: handler returns 200 within 5s p95. Heavy work runs synchronously within that budget — if it ever exceeds, queue to a Cloudflare Queue; not in v1.
- [ ] AC-US4-08: Webhook failures (post-validation) return 500; WorkOS retries with exponential backoff per their contract. We rely on their retries — no internal retry queue in v1.

### US-005 — Audit log UI surface
**As** a tenant owner
**I want** to see and export who did what in my org
**So that** I can answer compliance questions without filing a support ticket

**Acceptance Criteria**
- [ ] AC-US5-01: `/account/orgs/:tenantId/audit-log` page renders only for `tenant.tier === 'ENTERPRISE'` AND requesting user is `OrgMember.role IN ('OWNER', 'ADMIN')`. Otherwise 403.
- [ ] AC-US5-02: Reads paginated data from existing `GET /api/v1/tenants/[tenantId]/audit-log` (built in 0826 — do not duplicate). Page size 50, cursor-based.
- [ ] AC-US5-03: Filters: `action` (multi-select dropdown of all 14+ action types), `actorId` (typeahead user search within tenant), `from` / `to` (date range picker, max 365 days per query). All filters applied server-side.
- [ ] AC-US5-04: "Export" button calls existing `GET /api/v1/tenants/[tenantId]/audit-log/export?format=csv|json` with current filters. Browser downloads the file. Export emits a `tenant.audit_log.exported` audit event.
- [ ] AC-US5-05: Tier gate enforced server-side in middleware (single source of truth) AND mirrored client-side as a UX hint (paywall card for non-Enterprise). Server gate is the security boundary.
- [ ] AC-US5-06: Empty state copy: "No audit events match these filters" with a "Clear filters" link. Loading state uses skeleton rows.
- [ ] AC-US5-07: Default sort: most recent first. Each row shows `timestamp (relative + absolute on hover)`, `actor (email + avatar)`, `action (human label)`, `target (entity link if applicable)`, `metadata (expand to JSON)`.

### US-006 — Enterprise tier provisioning workflow
**As** Anton (ops)
**I want** to flip a tenant to Enterprise tier after I receive a signed LOI / contract
**So that** the WorkOS UI and audit-log UI become accessible to that tenant

**Acceptance Criteria**
- [ ] AC-US6-01: `/pricing` Enterprise card remains "Talk to sales" `mailto:enterprise@verified-skill.com` — no self-serve checkout.
- [ ] AC-US6-02: `POST /admin/tenants/:tenantId/provision-enterprise` (admin-only — gated by `User.isStaff`) sets `tenant.tier = 'ENTERPRISE'`, attaches a custom Stripe subscription via Stripe API (price ID from `process.env.STRIPE_ENTERPRISE_PRICE_ID`), and emits `tenant.tier.upgraded` audit event with `reason: 'enterprise_loi'`, `actorId: <staff user>`, and a freeform `notes` field for the LOI reference.
- [ ] AC-US6-03: Admin endpoint requires double confirmation: request body must include `confirm: true` AND `loiReference: <string>`. Missing either → 400.
- [ ] AC-US6-04: Downgrade path (`POST /admin/tenants/:tenantId/downgrade`) sets tier back, preserves `ssoConnectionId` and `workosOrganizationId` (don't burn the IdP setup if they re-up later), emits `tenant.tier.downgraded`.
- [ ] AC-US6-05: All admin endpoints log to a separate `admin-actions` log stream (Cloudflare tail logs in production) AND to AuditEvent.

### US-007 — Pre-built dependency / security checklist for WorkOS
**As** the engineer flipping this increment to active
**I want** the secrets, signature verification, and rollout safety items pre-listed
**So that** integration day doesn't turn into a security incident

**Acceptance Criteria**
- [ ] AC-US7-01: `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `WORKOS_WEBHOOK_SECRET` provisioned as Cloudflare Worker secrets via `wrangler secret put`. None of these appear in `.env.example`, source, or logs. CI lint rule fails the build if `WORKOS_*` strings appear in committed files outside the documented allowlist.
- [ ] AC-US7-02: `workos.events.verifyHeader` is the FIRST line of the webhook handler — before JSON parse, before any DB read. Test asserts that an unsigned body returns 401 without touching DB.
- [ ] AC-US7-03: Webhook endpoint is rate-limited at the Cloudflare WAF layer (200 req/min per IP) as defense-in-depth on top of WorkOS's own retry semantics.
- [ ] AC-US7-04: WorkOS IP allowlist (current published ranges) configured as an optional WAF rule that we keep DISABLED in v1 (their IPs change). Documented as a future hardening step in plan.md.
- [ ] AC-US7-05: Local dev uses WorkOS sandbox + Cloudflare tunnel for webhook delivery. `.specweave/dev/workos-tunnel.md` runbook captures the setup.
- [ ] AC-US7-06: SDK pinned: `@workos-inc/node` at the version current as of activation date — record exact version in plan.md when activating.
- [ ] AC-US7-07: A staging-only tenant (`acme-staging`) with a real Okta dev tenant connected via WorkOS sandbox runs end-to-end weekly via Playwright cron. If it breaks, we know before customers do.

## 8. Architecture Decisions Required (full ADRs in plan.md)

- **ADR-NEW-001**: Buy WorkOS vs build SAML in-house. Decision: **buy**.
- **ADR-NEW-002**: SCIM auto-deprovision strategy. Decision: **soft-delete + OrgMember disconnect, preserve AuditEvent for 7y**.

## 9. Test Stack

- **Unit (Vitest)**: WorkOS SDK methods mocked at module boundary. Webhook signature verifier called with synthetic signed payloads.
- **Integration (Vitest + test DB)**: Migration applies and rolls back cleanly. SCIM handler creates/updates/deletes `OrgMember` rows. Owner-demote safeguard triggers correctly.
- **E2E (Playwright)**: Mock WorkOS hosted login server (or use their sandbox); flow: visit `/auth/sso?org=acme-staging` → mock IdP → callback → land on `/dashboard` with session cookie. Audit log UI: filter by action, paginate, export CSV.
- **Manual gate (mandatory)**: Real Okta dev tenant ↔ WorkOS sandbox ↔ our staging environment. End-to-end sign-in by Anton. SCIM joiner/leaver flow verified by adding/removing a test user from an Okta group and observing OrgMember row + audit event within 60s.

## 10. Coverage Targets

- Unit: 95%
- Integration: 90%
- E2E: 100% of US-002, US-004, US-005 ACs
- Manual verification: 100% of US-002, US-003, US-004 (per CLAUDE.md "Manual Verification Gates" — auth changes require manual)

## 11. Open Questions (resolve at activation, not now)

- **OQ-1**: Do we want `/auth/sso` discoverable on the home page or only via direct link from the buyer's IT email? Default: hidden link in footer + direct deep-link only.
- **OQ-2**: Does first enterprise customer want SAML or OIDC? WorkOS supports both transparently — answer informs WorkOS plan tier we sign for.
- **OQ-3**: Group-mapping JSON UX — do we need an admin UI in v1 or is "ops edits a JSON column on request" acceptable? Default: JSON, ship UI in a follow-up if churn.
- **OQ-4**: Do we surface SCIM event log in the audit log UI (US-005), or keep them in a separate "Sync events" tab? Default: same audit log, action prefix `tenant.scim.*`.

## 12. Acceptance Summary

Increment is "done" when:
1. All 7 user stories' ACs pass automated tests.
2. Manual verification gate passes against a real Okta dev tenant.
3. ADR-NEW-001 and ADR-NEW-002 are committed under `.specweave/docs/internal/architecture/adr/`.
4. `/sw:grill` and `/sw:judge-llm` reports clear (with consent or waiver).
5. Anton has personally signed in via SSO at least once on staging.
6. The WorkOS bill for the month after launch reflects only the connections that should be billable (no orphan connections).
