---
project: vskill-platform
status: completed
---

# 0841 — Per-Org Seat Licensing

## Context

After 0840-stripe-billing-mvp ships, organization admins can purchase the **Team plan** ($30/seat/mo, ≥3 seats). Today the `Tenant` model has hardcoded caps (`privateSkillLimit=50`, `memberLimit=25`, set in 0826) that don't move with subscription state. This increment makes seats real: enforced on member add, reconciled to Stripe, tier-aware caps that follow subscription lifecycle.

**Dependency**: This increment depends on **0840-stripe-billing-mvp**. We assume 0840 has shipped and the following exist:
- `BillingCustomer`, `Subscription`, `Invoice`, `StripeWebhookEvent` Prisma models
- Stripe SDK installed and `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` configured
- Working `/api/v1/billing/webhooks/stripe` route with idempotency on `StripeWebhookEvent`
- `BillingCustomer.scope` discriminator (`USER` | `TENANT`) and `Subscription.planCode` (`FREE`|`PRO`|`TEAM`|`ENTERPRISE`)
- `Subscription.seats: Int?` and `Subscription.tenantId: String?` columns

If 0840 ships without all of the above, 0841 must amend the schema in T-001 instead of relying on it.

## Goals

- Make `Subscription.seats` enforced at member-invite time (402 Payment Required at the cap)
- Provide an idempotent reconciler that pushes the actual member count to Stripe `subscription.items.quantity`
- Detect and auto-correct drift between local seat count and Stripe via cron (every 15 min)
- Replace hardcoded `Tenant.privateSkillLimit` / `Tenant.memberLimit` with **tier-derived** caps via a single helper
- Surface seat usage and upgrade CTAs in `/account/orgs/:tenantId`
- Flip Tenant tier on subscription lifecycle (`active` → TEAM, `canceled+expired` → FREE)

## Non-Goals (Out of Scope)

- **SCIM-driven seat changes** — defer to 0842-workos-sso-enterprise
- **Per-role pricing** ("viewer = free seat" Vercel-style) — all roles count as a seat for v1
- **Seat self-service downgrade UI** — admins reduce seats by removing members + running sync; no in-app slider in v1
- **Proration controls** — Stripe's default proration behavior applies
- **USER-scope subscription tier flip** — already handled in 0840 for Pro; this increment only adds TENANT-scope flip

## User Stories & Acceptance Criteria

### US-001: Subscription.seats enforced on OrgMember.create

As an org admin, when I try to invite the (N+1)th member while my Team subscription has `seats=N`, the API blocks me with a clear upgrade prompt.

- [x] **AC-US1-01**: `POST /api/v1/tenants/:tenantId/members/invite` reads the active `Subscription` for the tenant; if `count(OrgMember WHERE tenantId=:id) >= Subscription.seats`, returns **HTTP 402 Payment Required** with body `{ error: "seats_exhausted", current, limit, upgradeUrl }` _(error slug standardized to lowercase snake_case for consistency with `team_min_seats` / `installation_removed` / `seat_usage_unavailable` siblings)_
- [x] **AC-US1-02**: When tenant has **no active TEAM subscription** (status != `ACTIVE` or planCode != `TEAM`), the existing 0826 free-tier cap (`memberLimit`, default 25) applies — no regression
- [x] **AC-US1-03**: When current count is at ≥80% of seat limit, the response (on the successful invite preceding the cap) includes `X-Vskill-Seats-Warn: 0.8` header and the next member-list view shows a yellow banner: "8/10 seats used — consider upgrading" _(header uses `X-Vskill-*` prefix per existing platform convention)_
- [x] **AC-US1-04**: A `tenant.seats.cap_reached` audit event is emitted with `outcome=DENIED` and metadata `{ current, limit, planCode }`
- [x] **AC-US1-05**: The route uses a single read-modify transaction (`prisma.$transaction`) so two simultaneous invites cannot both squeeze in at the cap (FOR UPDATE on `Subscription` row, or atomic `OrgMember.create` with a unique constraint backstop)

### US-002: /api/v1/billing/seats/sync reconciler

As an org admin, I can manually reconcile my member count to Stripe (e.g., after bulk-removing members) so my next invoice reflects reality.

- [x] **AC-US2-01**: `POST /api/v1/billing/seats/sync` requires authenticated session + tenant `OWNER` or `ADMIN` role (403 otherwise); body: `{ tenantId: string }`
- [x] **AC-US2-02**: Handler counts `OrgMember WHERE tenantId=:id`, calls `stripe.subscriptionItems.update(itemId, { quantity })`, then writes the new value to `Subscription.seats`
- [x] **AC-US2-03**: Idempotent — calling twice with the same `(tenantId, count)` is a no-op (skip the Stripe call when `seats` already matches actual count); response is `200` with `{ tenantId, seats, changed: false }`
- [x] **AC-US2-04**: Audit log emits `tenant.seats.synced` with metadata `{ previous, current, source: "manual" }`
- [x] **AC-US2-05**: When tenant has no active TEAM subscription, returns **400** `{ error: "NO_TEAM_SUBSCRIPTION" }` — sync is meaningless
- [x] **AC-US2-06**: Stripe API failures surface as 502 with the Stripe error code; no partial state written (transaction rolls back)

### US-003: Drift detection cron

As the platform, I auto-correct drift between Stripe seats and actual member counts so admins don't get surprise invoices.

- [x] **AC-US3-01**: Cloudflare Worker cron runs every **15 minutes** (`*/15 * * * *`) and scans `Subscription` rows where `planCode=TEAM AND status=ACTIVE`
- [x] **AC-US3-02**: For each row, compute `actualCount = count(OrgMember WHERE tenantId=:id)`; if `actualCount !== Subscription.seats`, attempt the same flow as US-002 (Stripe update + DB write)
- [x] **AC-US3-03**: On success, emit audit `tenant.seats.drift.corrected` with `{ previous, current, source: "cron" }`
- [x] **AC-US3-04**: On Stripe failure (rate limit, payment method declined for proration), log and emit `tenant.seats.drift.flagged` and skip — does NOT retry inline; next cron tick retries
- [x] **AC-US3-05**: Cron processes in batches of 50 tenants per tick to stay under Cloudflare Worker CPU budget; stable ordering (`ORDER BY updatedAt ASC`)
- [x] **AC-US3-06**: Drift cron is **disabled** when `BILLING_ENABLED=false` env (mirrors 0840's billing flag)

### US-004: Tier-aware tenant caps

As the platform, `Tenant.privateSkillLimit` and `Tenant.memberLimit` follow the subscription tier instead of being editable Int columns.

- [x] **AC-US4-01**: A new helper `getTenantCaps(tenant: Tenant, subscription: Subscription | null): { privateSkillLimit: number; memberLimit: number; tier: TenantTier }` lives in `src/lib/tenant-caps.ts` and replaces all direct reads of `Tenant.privateSkillLimit` / `Tenant.memberLimit`
- [x] **AC-US4-02**: Caps by tier:
  - **FREE** (no active sub): `privateSkillLimit=5`, `memberLimit=10` (tightened from legacy 50/25 to drive a clearer upgrade signal — see migration backfill in T-001; matches AC-US5-01 "5/10 seats used" example and the FREE_TIER_CAPS constant in `src/lib/tenant-caps.ts`)
  - **PRO** (USER-scope only): not applicable to Tenant; Tenants can't be PRO
  - **TEAM**: `privateSkillLimit=Infinity` (represented as `Number.MAX_SAFE_INTEGER`), `memberLimit=Subscription.seats`
  - **ENTERPRISE**: read overrides from `Tenant.privateSkillLimitOverride` / `Tenant.memberLimitOverride` (new nullable columns); fall back to TEAM defaults if null
- [x] **AC-US4-03**: `Tenant.privateSkillLimit` and `Tenant.memberLimit` columns are **migrated to overrides** (renamed) — existing rows' values become `*Override` so trial grants persist
- [x] **AC-US4-04**: Existing 0826 cap-check call sites (`/skills` create, member invite) updated to call `getTenantCaps()` instead of reading raw columns — verified by grep: zero remaining `tenant.privateSkillLimit` / `tenant.memberLimit` reads outside the helper
- [x] **AC-US4-05**: Unit tests cover all 4 tier branches incl. ENTERPRISE override fallthrough

### US-005: /account/orgs/:tenantId UI surface

As an org admin, I can see seat usage and upgrade my plan from the org settings page.

- [x] **AC-US5-01**: `/account/orgs/:tenantId` shows a **Seats widget**: "5/10 seats used" with a progress bar; reads from `getTenantCaps()` + `count(OrgMember)`
- [x] **AC-US5-02**: When `current >= memberLimit`, the **Invite member** button is disabled with a tooltip: "You've reached your seat limit. Upgrade your plan to add more."
- [x] **AC-US5-03**: When tier is FREE and tenant has any members, an **Upgrade to Team** CTA links to `/account/billing?upgrade=team&tenantId=<id>`
- [x] **AC-US5-04**: When tier is TEAM and seats are at ≥80%, a yellow banner shows "Approaching seat limit — [Upgrade seats]" linking to the same billing page
- [x] **AC-US5-05**: A "Sync seats" button (visible to OWNER/ADMIN) calls `POST /api/v1/billing/seats/sync` and shows result toast — useful after manual member removals

### US-006: Per-org tier flip on subscription lifecycle

As the platform, when a Tenant's TEAM subscription becomes active or canceled, the Tenant's effective tier follows.

- [x] **AC-US6-01**: Stripe webhook `customer.subscription.created` / `customer.subscription.updated` for a `BillingCustomer.scope=TENANT` row writes `Subscription.status` and `Subscription.seats` and is idempotent on `StripeWebhookEvent.id`
- [x] **AC-US6-02**: When status flips to `ACTIVE` and `planCode=TEAM`, no extra Tenant column update is needed — `getTenantCaps()` derives tier from the live Subscription row
- [x] **AC-US6-03**: When status flips to `CANCELED` and `currentPeriodEnd < now()`, subsequent `getTenantCaps()` calls return FREE caps; existing members above the new cap **stay** but the next invite returns 402 (no auto-removal)
- [x] **AC-US6-04**: A `tenant.tier.changed` audit event fires on each effective tier transition (computed by comparing the result of `getTenantCaps()` before and after the webhook applies)
- [x] **AC-US6-05**: Webhook handler tested with a fixture for TENANT-scope subscription created → active → canceled → expired cycle
