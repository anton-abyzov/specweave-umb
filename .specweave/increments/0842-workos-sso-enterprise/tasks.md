# Tasks: WorkOS SSO + SCIM + Audit Log UI

**Increment**: 0842-workos-sso-enterprise
**Status**: planned (do not start until LOI trigger fires — see [spec.md §1](spec.md#1-trigger-and-gating-read-first))
**Test Mode**: TDD (RED → GREEN → REFACTOR)

> **Activation checklist before T-001**:
> 1. Re-read spec.md and plan.md end-to-end.
> 2. Pin `@workos-inc/node` to current latest stable; record version in plan.md §6.
> 3. Confirm 0840 and 0841 are closed (`grep status .specweave/increments/084{0,1}-*/metadata.json`).
> 4. Provision WorkOS sandbox account; capture API key, client ID, webhook secret.
> 5. Flip metadata.json status to `active`.

---

## Phase 1 — Schema and infrastructure (US-001, US-007)

### T-001: Prisma migration for WorkOS schema
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given a fresh test DB → When `prisma migrate dev` runs `20260509_workos_sso_enterprise` → Then `Tenant.ssoConnectionId`, `Tenant.workosOrganizationId`, `Tenant.scimGroupMapping`, `User.identityProvider`, `User.workosUserId`, `User.deletedAt`, and `WorkosEvent` table all exist with correct types and unique indexes; rollback removes them cleanly with no data loss on existing rows.
**AC**: AC-US1-01, AC-US1-05

### T-002: Provision Cloudflare Worker secrets
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [ ] pending
**Test Plan**: Given staging Cloudflare environment → When `wrangler secret put` runs for `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `WORKOS_WEBHOOK_SECRET`, `WORKOS_REDIRECT_URI` → Then `wrangler secret list` shows all four; CI lint rule fires on PR if any of these names appear in committed source outside the documented allowlist.
**AC**: AC-US7-01, AC-US7-06

### T-003: WorkOS client singleton
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 (foundation) | **Status**: [ ] pending
**Test Plan**: Given `WORKOS_API_KEY` in env → When `getWorkOSClient()` is called twice → Then the same instance is returned (singleton); HTTP client is `fetch` (Cloudflare-compatible); missing env throws a typed error at boot.
**File**: `src/lib/workos/client.ts`

### T-004: State JWT sign/verify helpers
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-05 | **Status**: [ ] pending
**Test Plan**: Given a tenantId and nonce → When `signSsoState({tenantId, nonce})` produces a JWT and `verifySsoState(jwt)` parses it → Then payload roundtrips intact; expired tokens (exp < now) reject; tampered tokens reject; missing claims reject.
**File**: `src/lib/workos/state-jwt.ts`

## Phase 2 — SSO sign-in flow (US-002)

### T-005: `/auth/sso` entry route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test Plan**: Given a tenant with `ssoConnectionId` set → When `GET /auth/sso?org=<slug>` is called → Then response is 302 to a URL matching `^https://api.workos.com/sso/authorize` containing `client_id`, `connection`, `redirect_uri`, `state` params; `state` is a verifiable JWT containing the tenantId. Given a tenant with `ssoConnectionId` null → Then 404 with copy "SSO not configured for this organization". Given a non-existent org slug → Then 404.
**File**: `src/app/auth/sso/page.tsx`

### T-006: SSO callback handler — first-login path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-06 | **Status**: [ ] pending
**Test Plan**: Given a valid state JWT and mocked WorkOS `getProfileAndToken` returning a fresh email → When `GET /api/v1/auth/sso/callback?code=X&state=Y` is called → Then a new User row is created with `identityProvider = SSO`, `workosUserId` set; `OrgMember(tenantId, userId, role: MEMBER)` is created; session JWT cookie is set with `Secure; HttpOnly; SameSite=Lax; Max-Age=2592000`; response 302s to `/dashboard`.
**File**: `src/app/api/v1/auth/sso/callback/route.ts`

### T-007: SSO callback — existing GitHub user link path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] pending
**Test Plan**: Given an existing User with `identityProvider = GITHUB` and matching email → When SSO callback fires for that email → Then `workosUserId` is set on the existing row; `identityProvider` remains `GITHUB` (not downgraded); `OrgMember` is created if missing; `auth.provider.linked` audit event is emitted.

### T-008: SSO callback — failure paths
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
**Test Plan**: Given an invalid/expired/tampered state JWT → When callback fires → Then response is 302 to `/auth/error?reason=state_mismatch`; `auth.sso.state_mismatch` audit emitted. Given a valid state but WorkOS `getProfileAndToken` throws → Then 302 to `/auth/error?reason=<workos-code>`; `auth.sso.failed` audit emitted with reason.

### T-009: Auth error page surfaces reason
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
**Test Plan**: Given `/auth/error?reason=state_mismatch` → When rendered → Then page shows human-readable copy mapped from the reason code; unknown reasons show generic "Sign-in failed" copy.
**File**: `src/app/auth/error/page.tsx` (extend existing)

### T-010: User.deletedAt check in session validation
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US4-04 (auth side) | **Status**: [ ] pending
**Test Plan**: Given a User with `deletedAt != null` → When their existing session JWT hits any authenticated route → Then 401, cookie cleared. Given `deletedAt = null` → Normal flow.

## Phase 3 — Tier gate (US-001, US-005)

### T-011: Middleware tier-gate matcher
**User Story**: US-005, US-001 | **Satisfies ACs**: AC-US3-01, AC-US5-01, AC-US5-05, AC-US1-04 | **Status**: [ ] pending
**Test Plan**: Given a tenant with `tier = 'PRO'` → When request hits `/account/orgs/<id>/sso` → Then 302 to `/pricing?gate=enterprise`. Given `tier = 'ENTERPRISE'` → Then request proceeds. Given a tenant on Enterprise that just downgraded → Then 302 to /pricing; `ssoConnectionId` and `workosOrganizationId` are NOT cleared from DB.
**File**: `middleware.ts`

### T-012: Audit log role-gate (OWNER/ADMIN only)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [ ] pending
**Test Plan**: Given an Enterprise tenant and a requesting user with `OrgMember.role = MEMBER` → When `/account/orgs/<id>/audit-log` is hit → Then 403. Given role IN (OWNER, ADMIN) → Then 200.

## Phase 4 — Admin Portal handoff (US-003)

### T-013: SSO settings page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [ ] pending
**Test Plan**: Given an Enterprise tenant → When `/account/orgs/<id>/sso` is rendered → Then "Configure SSO" button visible; current connection state (Configured/Not configured/Pending) shown. Given non-Enterprise → Then paywall card with "/pricing" link.
**File**: `src/app/account/orgs/[tenantId]/sso/page.tsx`

### T-014: Portal-link API endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04, AC-US3-05 | **Status**: [ ] pending
**Test Plan**: Given Enterprise tenant with `workosOrganizationId = null` → When `POST /api/v1/auth/sso/portal-link` → Then `workos.organizations.createOrganization` is called with `{name: tenant.name, externalId: tenant.id}`; returned ID persisted; `createPortalLink({organization, intent: 'sso'})` called; response includes URL + 5-min expiry timestamp; `tenant.sso.portal_link_issued` audit emitted with hashed link only (regex assert that full URL is NOT in metadata). Given existing `workosOrganizationId` → Skip create, go straight to portal link.
**File**: `src/app/api/v1/auth/sso/portal-link/route.ts`

### T-015: Connection link/unlink audit hooks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given a tenant whose `ssoConnectionId` is updated from null → "conn_123" → Then `tenant.sso.connection_linked` audit emitted with `actorId` and `connectionId` in metadata. Given update from "conn_123" → null → Then `tenant.sso.connection_unlinked` audit emitted.

### T-015a: WorkOS-as-source-of-truth invariant (no IdP cert/config caching)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test Plan**: Given the schema → When grep / static-analysis runs across `prisma/schema.prisma` and `src/lib/workos/**` → Then no fields named `samlCertificate`, `idpMetadata`, `samlCert`, `idpEntityId`, or any other IdP config payload exist on Tenant or any cached model; only `ssoConnectionId` (the WorkOS pointer) and `workosOrganizationId` are persisted. Given a runtime SSO sign-in flow → When traced → Then the code never reads SAML certs from our DB; all IdP state is fetched fresh via the WorkOS SDK on each authorize/callback. CI lint rule `scripts/lint-no-saml-cert-cache.ts` added that fails the build if forbidden field names appear in `prisma/schema.prisma`.

## Phase 5 — SCIM webhook (US-004, US-007)

### T-016: SCIM webhook signature verification (FIRST)
**User Story**: US-004, US-007 | **Satisfies ACs**: AC-US4-01, AC-US7-02 | **Status**: [ ] pending
**Test Plan**: Given a request to `POST /api/v1/auth/scim/webhook` with no signature → Then 401; assert no DB queries were issued (use Prisma query interceptor / spy). Given a request with invalid signature → Then 401, no DB. Given a valid signature → Proceed.
**File**: `src/app/api/v1/auth/scim/webhook/route.ts`

### T-017: WorkosEvent idempotency
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
**Test Plan**: Given a webhook with `eventId = "evt_1"` processed once → When the same event is delivered again → Then the second call returns 200 within 50ms with no side effects (no audit event re-emitted, no OrgMember mutation).

### T-018: Group-mapping resolver
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [ ] pending
**Test Plan**: Given `tenant.scimGroupMapping = {"grp_1": "ADMIN"}` and a user in groups `["grp_1"]` → Then resolved role is ADMIN. Given groups `["grp_unknown"]` → Then MEMBER. Given mapping null → Then MEMBER. Given multiple mapped groups → Highest role wins (OWNER > ADMIN > MEMBER).
**File**: `src/lib/workos/group-mapping.ts`

### T-019: Last-owner safeguard
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [ ] pending
**Test Plan**: Given a tenant with exactly one OWNER (Alice) and a SCIM event that would demote Alice to MEMBER → When the handler processes it → Then Alice's role is unchanged; `tenant.scim.owner_demote_blocked` audit emitted with `actorId: 'system:scim'`.

### T-020: SCIM `dsync.user.created` handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**Test Plan**: Given a `dsync.user.created` event with `email = "bob@acme.com"` and group memberships → Then User upserted by email (existing User reused, fields merged); `OrgMember(tenantId, userId, resolvedRole)` created; `tenant.member.added` audit emitted with `source: 'scim'`.

### T-021: SCIM `dsync.user.updated` handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06 | **Status**: [ ] pending
**Test Plan**: Given a `dsync.user.updated` event changing group membership → Then `OrgMember.role` is recomputed via group-mapping resolver. Given the event changes email → Then `User.email` updated; if collision (another User has that email) → log `tenant.scim.email_collision` and skip the email change (other fields proceed).

### T-022: SCIM `dsync.user.deleted` handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given a `dsync.user.deleted` event → Then `User.deletedAt = now()`; ALL `OrgMember` rows for `(tenantId, userId)` deleted (just this tenant); other tenants' OrgMember rows untouched; AuditEvent rows for this user remain queryable; `tenant.member.removed` audit emitted with `source: 'scim'`.

### T-023: Webhook latency budget
**User Story**: US-004 | **Satisfies ACs**: AC-US4-07, AC-US4-08 | **Status**: [ ] pending
**Test Plan**: Given a SCIM event end-to-end against test DB → When measured → Then p95 < 5s across 100 sequential events. Given handler throws post-validation → Then 500 returned; WorkOS retry contract documented in code comment.

### T-024: WAF rate limit on webhook endpoint
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03 | **Status**: [ ] pending
**Test Plan**: Given Cloudflare WAF config → When 201 requests/min hit `/api/v1/auth/scim/webhook` from a single IP → Then 429 on the 201st. Configured via `wrangler.toml` or Cloudflare dashboard; verified via staging traffic test.

### T-024a: WorkOS IP allowlist WAF rule documented but DISABLED in v1
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04 | **Status**: [ ] pending
**Test Plan**: Given `.specweave/dev/workos-tunnel.md` (or a sibling runbook) → When reviewed → Then it documents the optional Cloudflare WAF IP allowlist rule referencing the current published WorkOS IP ranges; explicitly notes the rule is DISABLED in v1 (their IPs drift and would break webhook delivery); flags it as a future hardening step with a clear "enable only after monitoring WorkOS's published IP-change cadence for ≥ 90 days" guard. Given staging Cloudflare config → When inspected → Then no WorkOS IP allowlist rule is active.
**File**: `.specweave/dev/workos-tunnel.md` (extend) or `.specweave/dev/workos-waf-allowlist.md` (new)

## Phase 6 — Audit log UI (US-005)

### T-025: Audit log server page shell
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-05 | **Status**: [ ] pending
**Test Plan**: Given Enterprise tenant + OWNER user → When `/account/orgs/<id>/audit-log` rendered → Then page shows `AuditLogClient` mounted; non-Enterprise sees paywall; non-OWNER/ADMIN sees 403.
**File**: `src/app/account/orgs/[tenantId]/audit-log/page.tsx`

### T-026: AuditLogClient — table + pagination
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-07 | **Status**: [ ] pending
**Test Plan**: Given existing `/api/v1/tenants/<id>/audit-log` returning 50 rows + nextCursor → When AuditLogClient mounts → Then 50 rows render sorted recent-first; each row shows timestamp (relative + absolute on hover), actor (email + avatar), action (human label), target (link if applicable), metadata (expandable). "Load more" triggers next-cursor fetch.
**File**: `src/app/account/orgs/[tenantId]/audit-log/AuditLogClient.tsx`

### T-027: AuditLogClient — filters
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] pending
**Test Plan**: Given the filter UI → When user selects 2 actions, 1 actor, and a from/to range → Then the API call includes those query params; URL state reflects filter selection (deep-linkable). Given `to - from > 365 days` → Then UI clamps to 365 and shows a hint.

### T-028: AuditLogClient — empty + loading states
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [ ] pending
**Test Plan**: Given API returns zero rows → Then "No audit events match these filters" + "Clear filters" link. Given pending request → Then skeleton rows render until response.

### T-029: AuditLogClient — export buttons
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [ ] pending
**Test Plan**: Given current filter state → When user clicks Export CSV → Then browser downloads via `/api/v1/tenants/<id>/audit-log/export?format=csv&...filters`; `tenant.audit_log.exported` audit event emitted with `format: 'csv'` in metadata. Same for JSON.

## Phase 7 — Ops admin (US-006)

### T-029a: `/pricing` Enterprise card stays mailto (no self-serve checkout)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [ ] pending
**Test Plan**: Given `/pricing` → When the Enterprise card is rendered → Then its CTA is exactly `mailto:enterprise@verified-skill.com` (no Stripe checkout link, no self-serve form). Given the page → When E2E inspects all CTAs by tier → Then no Enterprise CTA POSTs to `/api/v1/billing/checkout/session` or any other self-serve endpoint. Snapshot test asserts the link href and copy.
**File**: `src/app/pricing/page.tsx` (extend / verify)

### T-030: Provision-Enterprise admin endpoint
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-03, AC-US6-05 | **Status**: [ ] pending
**Test Plan**: Given staff user (User.isStaff = true) → When `POST /admin/tenants/<id>/provision-enterprise` with body `{confirm: true, loiReference: "LOI-2026-001"}` → Then `tenant.tier = 'ENTERPRISE'`; Stripe subscription attached via existing 0840 wrapper using `STRIPE_ENTERPRISE_PRICE_ID`; `tenant.tier.upgraded` audit emitted with `reason: 'enterprise_loi'` and `loiReference` in metadata; admin-actions log stream entry written. Given non-staff user → 403. Given missing confirm or loiReference → 400.
**File**: `src/app/admin/tenants/[tenantId]/provision-enterprise/route.ts`

### T-031: Downgrade admin endpoint
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [ ] pending
**Test Plan**: Given an Enterprise tenant with `ssoConnectionId` and `workosOrganizationId` set → When `POST /admin/tenants/<id>/downgrade` runs → Then `tenant.tier` reverts; `ssoConnectionId` and `workosOrganizationId` are PRESERVED (not nulled); `tenant.tier.downgraded` audit emitted.

## Phase 8 — Local dev + ops runbooks (US-007)

### T-032: Cloudflare tunnel runbook
**User Story**: US-007 | **Satisfies ACs**: AC-US7-05 | **Status**: [ ] pending
**Test Plan**: Given the runbook at `.specweave/dev/workos-tunnel.md` → When followed end-to-end by a fresh engineer → Then they can receive a SCIM webhook at localhost within 30 minutes; runbook is verified by Anton walking through it on activation day.
**File**: `.specweave/dev/workos-tunnel.md`

### T-033: Orphan-connection reconciliation runbook
**User Story**: US-007 | **Satisfies ACs**: (DoD §12.6) | **Status**: [ ] pending
**Test Plan**: Given the runbook describes how to list WorkOS connections and cross-check against tenants with `tier = 'ENTERPRISE'` → When run monthly → Then any orphan connection (billable but no active Enterprise tenant) is flagged for revocation.
**File**: `.specweave/dev/workos-orphan-connection-reconcile.md`

### T-034: Rollback runbook
**User Story**: US-007 | **Satisfies ACs**: (DoD §12.7) | **Status**: [ ] pending
**Test Plan**: Given a production incident requiring SSO + audit-log routes disabled → When the rollback runbook is followed → Then `/auth/sso`, `/account/orgs/<id>/(sso|audit-log)`, and the SCIM webhook return 503 within 5 minutes; existing sessions remain valid; documented kill-switch is a feature flag, not a code revert.
**File**: `.specweave/dev/workos-rollback.md`

### T-035: Weekly Playwright cron against acme-staging
**User Story**: US-007 | **Satisfies ACs**: AC-US7-07 | **Status**: [ ] pending
**Test Plan**: Given a scheduled GitHub Actions workflow → When it runs weekly against `acme-staging` (a real Okta dev tenant connected via WorkOS sandbox) → Then full SSO + SCIM joiner/leaver flow verified; failure pings #ops Slack channel.

## Phase 9 — ADRs and compliance docs

### T-036: ADR-NEW-001 — WorkOS vs DIY SAML
**User Story**: (architecture) | **Satisfies ACs**: spec §12.3 | **Status**: [ ] pending
**Test Plan**: Given the ADR file at `.specweave/docs/internal/architecture/adr/ADR-NEW-001-workos-vs-diy-saml.md` → When reviewed → Then it captures context, decision (buy), consequences, and migration-out plan, matching plan.md §3.

### T-037: ADR-NEW-002 — SCIM auto-deprovision
**User Story**: (architecture) | **Satisfies ACs**: spec §12.3, AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given the ADR file → Then it documents soft-delete + OrgMember disconnect, AuditEvent preservation, multi-tenant scoping, re-provisioning behavior, matching plan.md §3.

## Phase 10 — Closure gates

### T-038: `/sw:grill` report
**Status**: [ ] pending
**Test Plan**: Given all Phase 1-9 tasks complete and tests green → When `/sw:grill` runs → Then `grill-report.json` produced with no critical/high/medium findings unaddressed.

### T-039: `/sw:judge-llm` report (or waiver)
**Status**: [ ] pending
**Test Plan**: Given the increment ready for closure → When `/sw:judge-llm` runs (or consent declined) → Then `judge-llm-report.json` produced or waived per CLAUDE.md policy.

### T-040: Manual verification gate
**Status**: [ ] pending
**Test Plan**: Given staging environment with real Okta dev tenant → When Anton signs in via SSO and adds/removes a user from an Okta group → Then session cookie set and `OrgMember` row appears/disappears within 60s with correct audit events. Anton confirms in writing (commit message or PR comment).

### T-041: WorkOS bill reconciliation (month-1 post-launch)
**Status**: [ ] pending
**Test Plan**: Given the first calendar month post-launch → When WorkOS invoice is reviewed → Then every billable connection maps to an active Enterprise tenant; orphan connections (if any) revoked per T-033 runbook.

---

## Skipped / Deferred (not tasks for this increment)

- SOC 2 Type II audit prep (separate compliance increment).
- Group-mapping admin UI editor (JSON-edit-by-ops in v1; ship UI follow-up if churn).
- Cloudflare Queue async SCIM processing (v1 is synchronous within 5s budget).
- WorkOS IP allowlist WAF rule (documented in plan.md §11; brittle).
- Audit log SCIM-event separation (default: same log, action prefix `tenant.scim.*`).
