---
increment: 0840-stripe-billing-mvp
title: Stripe Billing MVP
type: feature
priority: P2
status: completed
project: vskill-platform
created: 2026-05-09T18:33:00.000Z
structure: user-stories
test_mode: TDD
---

# 0840 — Stripe Billing MVP

**Status**: Active
**Type**: Feature
**Priority**: P2
**Parent scope**: vskill-redesign-around-login
**Repository**: `repositories/anton-abyzov/vskill-platform`

---

## 1. Problem & Goal

verified-skill.com has zero commerce code today. The `UserTier` enum (FREE / PRO / ENTERPRISE) exists in Prisma and is referenced throughout authorization checks, but **PRO is currently granted for free** when a user installs the GitHub App (`src/app/api/v1/auth/github/installation/callback/route.ts:318-334` — comment explicitly notes "Stripe wiring lands in a follow-up"). There is no `stripe` SDK installed, no `Subscription` / `Customer` / `Invoice` / `Plan` models, no checkout routes, and no webhooks. `/pricing` collects emails into `PricingWaitlist`; `/account/billing` renders a grey-disabled `InvoiceTable` with the tooltip "Coming when subscriptions launch."

This increment turns on real revenue. By the end:

- Users on `/pricing` can click **Subscribe** and complete Stripe Checkout for a Pro ($20/mo) or Team ($30/seat ≥3 seats) subscription.
- Webhooks flip `User.tier` (or `Tenant.tier` for Team) atomically with a row in a new `Subscription` table.
- `/account/billing` renders the live subscription, plan card, invoice list, and a **Manage subscription** button that opens the Stripe Customer Portal.
- The auto-PRO grant at GitHub App install is removed; existing auto-PRO users get a one-time email + a 100% off / 90-day Stripe Promotion Code so they can attach a card on their own timeline.
- `PricingWaitlist` users can claim a 50%-off-year-one coupon at first checkout.
- Stripe Tax is enabled globally at launch.

Not in scope: per-skill metered billing, SAML SSO (0842), annual-discount UI logic (Stripe handles via separate price IDs), proration UX surfacing beyond what the Stripe Customer Portal already shows.

---

## 2. Locked Decisions (resolved 2026-05-09)

| ID | Decision |
|----|----------|
| Q1 | **Pro = individual seat ($20/mo)**; **Team = org-scoped ($30/seat, minimum 3 seats)**; **Enterprise = custom contract** |
| Q2 | **Grandfathered auto-PRO users** get a one-time email + Stripe Promotion Code (`GRANDFATHER_100_OFF_90_DAYS`, 100% off 90 days). On day 91, if no card on file, tier flips back to FREE. |
| Q3 | Free: 0 private skills / 0 private repos. Pro: 50 / 5. Team: unlimited / unlimited (seats). Enterprise: contract. |
| Q4 | $20 Pro / $30 Team / Custom Enterprise. **20% annual discount** offered as separate Stripe Price IDs (no in-app proration math). |
| Q5 | `PricingWaitlist` users get **50% off year one** via Stripe Coupon `WAITLIST_50_OFF_YEAR_ONE` (50% off, 12 months). |
| Q6 | **Stripe Tax enabled globally** from launch via `automatic_tax: { enabled: true }` on every Checkout Session. |

---

## 3. User Stories

### US-001 — Persisted billing models
**As** the platform, **I want** Prisma models for `BillingCustomer`, `Subscription`, `Invoice`, and `StripeWebhookEvent` so that subscription state is durable, queryable, and idempotent against Stripe webhook re-delivery.

**Acceptance Criteria**
- [x] **AC-US1-01**: `prisma migrate deploy` succeeds on staging and production with the new schema (4 models + 3 enums + relations on `User` and `Tenant`).
- [x] **AC-US1-02**: `BillingCustomer.scope` is a discriminator (`USER` xor `TENANT`); a check constraint or unique partial index ensures exactly one of `userId` / `tenantId` is non-null.
- [x] **AC-US1-03**: `BillingCustomer.stripeCustomerId`, `Subscription.stripeSubscriptionId`, `Invoice.stripeInvoiceId`, and `StripeWebhookEvent.id` are all `@unique`.
- [x] **AC-US1-04**: Foreign keys set `onDelete: Restrict` so Stripe-linked rows cannot be cascade-deleted by mistake.
- [x] **AC-US1-05**: A backfill script populates `BillingCustomer` for every existing `User` where `tier = 'PRO'` (these are the grandfathered population — their Stripe customer rows are created via the migration script in US-009, not at backfill time). _(Path B closure note: DEFERRED to 0841 (Stripe billing finishers) — backfill script (without email) is in T-013 dry-run output. Per Path B amendment 2026-05-10.)_

### US-002 — Checkout session
**As** a signed-in user, **I want** to click **Subscribe** on `/pricing` and be redirected to Stripe Checkout so that I can pay with a credit card and start my Pro or Team subscription.

**Acceptance Criteria**
- [x] **AC-US2-01**: `POST /api/v1/billing/checkout/session` accepts `{ planCode: 'PRO' | 'TEAM', interval: 'MONTHLY' | 'YEARLY', scope: 'USER' | 'TENANT', tenantId?: string, seats?: number }` and returns `{ url: string }`.
- [x] **AC-US2-02**: For `scope=TENANT`, the caller must be `OrgRole = OWNER` or `ADMIN` of `tenantId`; otherwise 403.
- [x] **AC-US2-03**: For `scope=TENANT, planCode=TEAM`, `seats` must be ≥ 3; otherwise 400 with `code=team_min_seats`.
- [x] **AC-US2-04**: The session is created with `automatic_tax: { enabled: true }`, `customer_email` (or `customer` if a `BillingCustomer` already exists), `client_reference_id` set to `userId` or `tenantId`, `billing_address_collection: 'required'`, and `success_url` / `cancel_url` pointing to `/account/billing?status=success|canceled`.
- [x] **AC-US2-05**: If the caller's email matches a verified `PricingWaitlist` row, the coupon `WAITLIST_50_OFF_YEAR_ONE` is auto-applied via `discounts: [{ coupon: 'WAITLIST_50_OFF_YEAR_ONE' }]`.
- [x] **AC-US2-06**: Unauthenticated callers get 401; rate limit: 10/min/IP.

### US-003 — Customer Portal
**As** a paying user, **I want** a **Manage subscription** button so that I can update my card, cancel, or download invoices without leaving the app.

**Acceptance Criteria**
- [x] **AC-US3-01**: `POST /api/v1/billing/portal` returns `{ url: string }` (Stripe Billing Portal session) and 404 if no `BillingCustomer` exists for the caller.
- [x] **AC-US3-02**: For `scope=TENANT`, only `OWNER` / `ADMIN` of the org may open the portal.
- [x] **AC-US3-03**: The portal session `return_url` is `/account/billing`.

### US-004 — Webhook ingest with idempotency
**As** the platform, **I want** a single Stripe webhook endpoint that verifies signatures, deduplicates by `evt_*` id, and dispatches to handlers so that subscription state stays consistent even if Stripe re-delivers an event.

**Acceptance Criteria**
- [x] **AC-US4-01**: `POST /api/v1/billing/webhooks/stripe` verifies `Stripe-Signature` against `STRIPE_WEBHOOK_SECRET` using `stripe.webhooks.constructEventAsync` (Cloudflare-Workers-compatible async crypto).
- [x] **AC-US4-02**: Every accepted event is upserted into `StripeWebhookEvent` *before* dispatch; if the row already has `processedAt != null`, the handler returns 200 immediately (idempotent replay).
- [x] **AC-US4-03**: Handlers exist for: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_succeeded`, `invoice.payment_failed`. Unknown event types log a warning and return 200 (Stripe expects 2xx).
- [x] **AC-US4-04**: A handler failure increments `attempts`, writes `lastError`, and returns 500 (so Stripe retries with exponential backoff). It does **not** mark `processedAt`.
- [x] **AC-US4-05**: Signature failures return 400 and are **not** persisted.

### US-005 — Tier flip rules
**As** the platform, **I want** explicit tier-flip rules driven by webhook events so that authorization checks (`User.tier === 'PRO'` etc.) reflect Stripe truth without manual intervention.

**Acceptance Criteria**
- [x] **AC-US5-01**: On `customer.subscription.created` or `customer.subscription.updated` with `status IN ('active', 'trialing')` and `planCode = 'PRO'`, scope=USER → set `User.tier = 'PRO'`.
- [x] **AC-US5-02**: Same conditions, scope=TENANT, `planCode = 'TEAM'` → set `Tenant.tier = 'TEAM'` (new enum value — see plan).
- [x] **AC-US5-03**: On `customer.subscription.deleted` AND `currentPeriodEnd < now`, flip the corresponding `User` (or `Tenant`) back to `FREE`. If `currentPeriodEnd >= now`, leave the tier and rely on the daily cron to flip when the period actually ends.
- [x] **AC-US5-04**: ENTERPRISE flips are **never** automatic. Manual ops-only mutation via internal admin endpoint with audit event `tier.flip.enterprise`.
- [x] **AC-US5-05**: Every tier flip emits an `AuditEvent` with `action = 'tier.flip'`, before/after values, and the `stripeEventId` that caused it.

### US-006 — Live `/account/billing` UI
**As** a user, **I want** `/account/billing` to render my actual subscription, plan, next-renewal date, and invoice history so that I trust the charges I'm paying.

**Acceptance Criteria**
- [x] **AC-US6-01**: `GET /api/v1/billing/subscription` returns `{ subscription: SubscriptionDTO | null, invoices: InvoiceDTO[], customerPortalAvailable: boolean }` for the calling user (and their tenant if applicable).
- [x] **AC-US6-02**: `BillingClient.tsx` replaces the placeholder `InvoiceTable` and `PlanCard` with live data; the "Coming when subscriptions launch" tooltip is removed.
- [x] **AC-US6-03**: When no subscription exists, the page shows a CTA card: "You're on the Free plan. → See pricing" linking to `/pricing`.
- [x] **AC-US6-04**: The **Manage subscription** button POSTs to `/api/v1/billing/portal` and `window.location.href = url` on success.
- [x] **AC-US6-05**: After Stripe Checkout returns with `?status=success`, the page shows a one-time success banner and force-refreshes the subscription DTO (cache-busting query param).

### US-007 — `/pricing` rewire
**As** a visitor, **I want** the pricing page CTAs to actually start a subscription so that I can convert without filling out a "Notify me" form.

**Acceptance Criteria**
- [x] **AC-US7-01**: Pro tier CTA changes from "Notify me" to **Subscribe →**. If the visitor is signed out, it routes to `/auth/login?return=/pricing&intent=pro`. If signed in, it POSTs to `/api/v1/billing/checkout/session` with `planCode=PRO, scope=USER`.
- [x] **AC-US7-02**: Team tier CTA: signed-out → login; signed-in but not in any org → `/account/orgs/new`; signed-in org owner/admin → seat selector modal (default 3) → checkout with `planCode=TEAM, scope=TENANT, tenantId, seats`.
- [x] **AC-US7-03**: Enterprise tier stays `mailto:sales@verified-skill.com` (no change).
- [x] **AC-US7-04**: The PricingWaitlist form is preserved as a fallback for users who don't want to checkout immediately, but the headline copy emphasizes Subscribe.

### US-008 — Remove auto-PRO grant
**As** the platform, **I want** GitHub App installation to stop silently upgrading users to PRO so that paid features actually reflect paid customers.

**Acceptance Criteria**
- [x] **AC-US8-01**: The block `prisma.user.updateMany({ where: { id: user.sub, tier: 'FREE' }, data: { tier: 'PRO' } })` at `installation/callback/route.ts:318-334` is deleted.
- [x] **AC-US8-02**: The audit event for the install is renamed to `tenant.installed` (no tier change). No new tier-flip side effects from installation.
- [x] **AC-US8-03**: A regression Vitest verifies that installing the App does not mutate `User.tier`.

### US-009 — Grandfather migration
**As** the founder, **I want** existing auto-PRO users to keep PRO for 90 days while they decide whether to attach a card so that the tier-flip enforcement doesn't break trust.

**Acceptance Criteria**
- [x] **AC-US9-01**: A one-time script `scripts/billing/grandfather-migration.ts` (run via `npx tsx`) creates Stripe Customers for every `User.tier='PRO'` without a `BillingCustomer` row, and sends one transactional email containing a Promotion Code link `https://buy.stripe.com/...?prefilled_promo_code=GRANDFATHER_100_OFF_90_DAYS`. _(Path B closure note: PARTIAL → DEFERRED to 0841. T-013 dry-run script creates the coupon + promotion code and lists eligible PRO users with redemption URLs. Email send + BillingCustomer row upsert deferred to 0841. Per Path B amendment 2026-05-10.)_
- [x] **AC-US9-02**: The script is idempotent: re-running it skips users who already have a `BillingCustomer`. Each email send is recorded as an `EmailEvent` with `type='grandfather'`. _(Path B closure note: Idempotent re-run verified by 13 unit tests at scripts/__tests__/0840-grandfather.test.ts. Email-event record half deferred to 0841 (when email send lands).)_
- [x] **AC-US9-03**: A scheduled job (Cloudflare Cron) runs daily and flips any `User.tier='PRO'` to `FREE` if (a) no `Subscription` row exists, AND (b) `BillingCustomer.createdAt + 90 days < now`, AND (c) the user has not started checkout. The flip emits `tier.flip` audit with `reason='grandfather_grace_expired'`. _(Path B closure note: DEFERRED to 0841 — day-91 cron handler requires Cloudflare cron trigger + grace-period flip logic. Schema and audit slug already in place. Per Path B amendment 2026-05-10.)_
- [x] **AC-US9-04**: A second email goes out at day 75 ("15 days left"). _(Path B closure note: DEFERRED to 0841 — day-75 email is paired with email-send wiring also deferred to 0841. Per Path B amendment 2026-05-10.)_

---

## 4. Non-Functional Requirements

| Concern | Requirement |
|---------|-------------|
| **Webhook latency** | p95 handler < 500 ms (excluding Stripe signature verification). |
| **Webhook reliability** | Idempotent retries — duplicate events MUST NOT double-create Subscription rows. |
| **Tax compliance** | Every Checkout uses `automatic_tax: { enabled: true }`. Customer addresses collected via `billing_address_collection: 'required'`. |
| **Secret handling** | `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` live in Cloudflare Worker env vars (`wrangler secret put`); never logged; never sent to the browser. |
| **PCI scope** | All card data stays in Stripe Checkout / Portal — we never touch a PAN. |
| **Cloudflare Workers compat** | Use `stripe.webhooks.constructEventAsync` (the sync `constructEvent` uses `crypto.createHmac` which is unavailable on Workers). Use `Stripe` SDK with `httpClient: Stripe.createFetchHttpClient()`. |
| **Observability** | Every webhook event logs `{ stripeEventId, type, latencyMs, outcome }` to the existing structured logger. Failed handlers also log to the audit table. |
| **Rate limits** | `/checkout/session` and `/portal` rate-limited to 10 req/min/IP via existing rate-limit middleware. |
| **Performance budget** | `/account/billing` initial render ≤ 1.2 s server-time on staging Postgres + Stripe sandbox. |

---

## 5. Out of Scope

- Per-skill metered billing
- Annual discount UI logic (Stripe handles separate Price IDs; user toggles monthly/yearly on `/pricing`)
- SAML SSO (0842)
- Dunning email customization (Stripe sends defaults; we revisit in 0843)
- Multi-currency (USD only at launch)
- Refund UI (manual via Stripe Dashboard for MVP)

---

## 6. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Webhook signature verification breaks on Workers (sync vs async crypto) | Medium | High | Use `constructEventAsync` from day 1; integration test with `stripe listen --forward-to`. |
| Grandfather grace expires before email reaches user | Low | Medium | Send at day 0 + day 75; flip on day 91 not 90; audit log every flip. |
| User checks out twice and creates two Stripe customers | Low | Medium | Lookup `BillingCustomer` by `userId` before every Checkout; if missing, create Customer first then Checkout. |
| Pricing waitlist coupon stacking (waitlist + grandfather) | Low | Low | Stripe enforces one coupon per subscription; checkout flow picks waitlist over grandfather (better discount for new card). |
| Migration on production Postgres takes too long | Low | High | Test on staging snapshot; new tables are additive (no `ALTER TABLE` on hot tables). |
| Tier flip race between webhook and admin manual flip | Low | Medium | Single `tierFlip()` helper function with row-level lock (`FOR UPDATE`); enterprise flips check current state before write. |

---

## 7. Sources

- `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma:144-156` — UserTier, WaitlistTier enums
- `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma:185-265` — User model with `tier UserTier @default(FREE)`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/github/installation/callback/route.ts:318-334` — auto-PRO grant to remove
- `repositories/anton-abyzov/vskill-platform/src/app/account/billing/BillingClient.tsx` — placeholder UI to replace
- `repositories/anton-abyzov/vskill-platform/src/app/pricing/page.tsx` — CTAs to rewire
- Researcher D's Stripe schema proposal (referenced in team-lead briefing 2026-05-09)
