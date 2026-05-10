# 0840 — Plan

**Repository**: `repositories/anton-abyzov/vskill-platform`
**Stack**: Next.js 15, Cloudflare Workers (OpenNext), Prisma + Postgres, Vitest, Playwright

---

## 1. Architecture Overview

```
Browser /pricing or /account/billing
         │
         │ POST /api/v1/billing/checkout/session    (Pro/Team checkout)
         │ POST /api/v1/billing/portal              (Manage Subscription)
         │ GET  /api/v1/billing/subscription        (Live billing DTO)
         ▼
Next.js API routes  ──►  src/lib/stripe/client.ts (Stripe SDK + fetch HTTP client)
         │                       │
         │                       ▼
         │              api.stripe.com  (Checkout / Portal / Customers / Subscriptions)
         │
         ▼
Postgres (Prisma)
   BillingCustomer
   Subscription
   Invoice
   StripeWebhookEvent

         ▲
         │  POST /api/v1/billing/webhooks/stripe
         │  (signature verify → upsert StripeWebhookEvent → dispatch handler → tierFlip)
         │
   api.stripe.com → webhook delivery
```

**Single source of truth**: Stripe. Postgres mirrors what Stripe tells us via webhooks. We never reverse-engineer state from `User.tier`; `User.tier` is a *cache* of Stripe state.

**Tier flip rule**: only the webhook handler (and the Cloudflare Cron for grandfather-grace expiry, and the ops-only ENTERPRISE endpoint) may mutate `User.tier` / `Tenant.tier` going forward. The auto-PRO grant at install is removed.

---

## 2. Prisma Schema Additions (verbatim into `prisma/schema.prisma`)

### 2.1 New enums

```prisma
enum BillingScope {
  USER
  TENANT
}

enum SubscriptionStatus {
  TRIALING
  ACTIVE
  PAST_DUE
  CANCELED
  UNPAID
  PAUSED
  INCOMPLETE
  INCOMPLETE_EXPIRED
}

enum PlanCode {
  FREE
  PRO
  TEAM
  ENTERPRISE
}
```

### 2.2 Extend existing `UserTier` enum (additive)

```prisma
enum UserTier {
  FREE
  PRO
  TEAM        // NEW — granted only via TENANT-scoped subscription seat
  ENTERPRISE
}
```

> Rationale: `Tenant.tier` (added below) is the authoritative tier for org-scoped Team subs; `User.tier = TEAM` is a derived convenience flag used by middleware so per-request authorization can short-circuit without a tenant join.

### 2.3 New models

```prisma
model BillingCustomer {
  id                String        @id @default(cuid())
  scope             BillingScope
  userId            String?       @unique
  tenantId          String?       @unique
  stripeCustomerId  String        @unique
  email             String
  createdAt         DateTime      @default(now())
  updatedAt         DateTime      @updatedAt

  user              User?         @relation(fields: [userId], references: [id], onDelete: Restrict)
  tenant            Tenant?       @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  subscriptions     Subscription[]
  invoices          Invoice[]

  @@index([scope])
  @@index([email])
}

model Subscription {
  id                     String              @id @default(cuid())
  billingCustomerId      String
  stripeSubscriptionId   String              @unique
  stripePriceId          String
  planCode               PlanCode
  status                 SubscriptionStatus
  seats                  Int                 @default(1)
  currentPeriodStart     DateTime
  currentPeriodEnd       DateTime
  cancelAtPeriodEnd      Boolean             @default(false)
  trialEnd               DateTime?
  hasDiscount            Boolean             @default(false)
  discountCouponId       String?
  createdAt              DateTime            @default(now())
  updatedAt              DateTime            @updatedAt

  billingCustomer        BillingCustomer     @relation(fields: [billingCustomerId], references: [id], onDelete: Restrict)

  @@index([billingCustomerId])
  @@index([status])
  @@index([currentPeriodEnd])
}

model Invoice {
  id                String           @id @default(cuid())
  billingCustomerId String
  stripeInvoiceId   String           @unique
  number            String?
  amountDue         Int              // cents
  amountPaid        Int              // cents
  currency          String           // 'usd'
  status            String           // 'draft' | 'open' | 'paid' | 'uncollectible' | 'void'
  hostedInvoiceUrl  String?
  periodStart       DateTime
  periodEnd         DateTime
  paidAt            DateTime?
  createdAt         DateTime         @default(now())
  updatedAt         DateTime         @updatedAt

  billingCustomer   BillingCustomer  @relation(fields: [billingCustomerId], references: [id], onDelete: Restrict)

  @@index([billingCustomerId])
  @@index([status])
}

model StripeWebhookEvent {
  id           String    @id            // Stripe evt_* id (NOT cuid)
  type         String
  payload      Json
  processedAt  DateTime?
  attempts     Int       @default(0)
  lastError    String?
  receivedAt   DateTime  @default(now())

  @@index([type])
  @@index([processedAt])
}
```

### 2.4 Relations on existing models

Add to `User`:
```prisma
billingCustomer  BillingCustomer?
```

Add to `Tenant`:
```prisma
billingCustomer  BillingCustomer?
tier             TenantTier       @default(FREE)
```

Add new enum next to `UserTier`:
```prisma
enum TenantTier {
  FREE
  TEAM
  ENTERPRISE
}
```

### 2.5 Discriminator constraint

Prisma cannot express XOR natively. Add a CHECK constraint via raw SQL migration:

```sql
ALTER TABLE "BillingCustomer"
  ADD CONSTRAINT "BillingCustomer_scope_xor"
  CHECK (
    (scope = 'USER' AND "userId" IS NOT NULL AND "tenantId" IS NULL) OR
    (scope = 'TENANT' AND "tenantId" IS NOT NULL AND "userId" IS NULL)
  );
```

---

## 3. ADRs

### ADR-0840-01 — One Stripe Customer per principal (User XOR Tenant), never both
**Decision**: `BillingCustomer.scope` is a hard discriminator. A `User` who is also a Tenant owner has two separate `BillingCustomer` rows (their personal Pro sub + the Tenant's Team sub) with two distinct `stripeCustomerId`s. The unique partial indexes on `userId` and `tenantId` enforce one-to-one within scope.
**Why**: Mixing personal + org payments on a single Stripe customer creates legal/billing chaos (whose card pays for whose subscription? whose tax jurisdiction applies?). Stripe customers are cheap; principals are not.
**Trade-off**: A user who pays for both a personal Pro and is the billing contact for a Team has two Stripe portals to manage. Acceptable for MVP.

### ADR-0840-02 — Tier flips are webhook-driven, not synchronous
**Decision**: `POST /checkout/session` does NOT flip the user's tier. Tier flips happen *only* in webhook handlers (`customer.subscription.created` / `.updated` / `.deleted`) and the daily grandfather cron and the ops-only ENTERPRISE endpoint. Until the webhook arrives (typically <2s after checkout success), the user remains on FREE.
**Why**: Stripe is the source of truth. Letting the success-redirect synchronously flip tier would diverge state if Stripe later voids the session (e.g. dispute, bad card retry). Webhooks are at-least-once; we de-dupe via `StripeWebhookEvent.id`.
**Trade-off**: 1-3s window after checkout where `/account/billing` may render "FREE plan" before the webhook lands. Mitigated by AC-US6-05 (success banner + cache-busting refresh).

### ADR-0840-03 — Cloudflare Workers requires async webhook signature verification
**Decision**: Use `stripe.webhooks.constructEventAsync(body, sig, secret)` (returns Promise). The synchronous `constructEvent` uses `crypto.createHmac` which is unavailable in Workers runtime.
**Why**: `vskill-platform` deploys to Cloudflare Workers via OpenNext. The Workers runtime has WebCrypto (`crypto.subtle.*`) but not the Node `crypto` module. Stripe's async API uses WebCrypto under the hood.
**Trade-off**: None — the async API is the official Stripe-recommended path for edge runtimes since stripe-node v12.

### ADR-0840-04 — `User.tier=TEAM` is a derived flag, `Tenant.tier=TEAM` is authoritative
**Decision**: For a Team-subscribed org, every member's `User.tier` is set to `max(User.tier, TEAM)` so per-request middleware can do `if (user.tier === 'TEAM' || user.tier === 'PRO') ...` without a tenant join. The Tenant row is the source of truth; the User flag is a denormalized cache rebuilt by webhook handlers when seats are added/removed.
**Why**: Authorization checks run on every request; a Tenant join would 2x the auth-middleware cost. We pay the storage + cache-invalidation cost once at subscription change.
**Trade-off**: A user who is in two orgs (one Team, one Free) shows `User.tier=TEAM` — correct, since they have Team access via the paying org.

---

## 4. File Plan

### 4.1 Schema + migrations
- `prisma/schema.prisma` — add 4 models, 3 enums, `TenantTier`, extend `UserTier`, relations
- `prisma/migrations/<timestamp>_billing_models/migration.sql` — generated by `prisma migrate dev` + raw SQL CHECK constraint appended

### 4.2 Stripe wrapper
- `src/lib/stripe/client.ts` — Stripe SDK singleton with `Stripe.createFetchHttpClient()`, env-loaded `STRIPE_SECRET_KEY`
- `src/lib/stripe/webhook-handlers.ts` — dispatch table for the 6 event types
- `src/lib/stripe/tier-flip.ts` — `tierFlip({ principal, fromTier, toTier, stripeEventId, reason })` — single helper, row-level lock via `prisma.$transaction` + `SELECT ... FOR UPDATE`
- `src/lib/stripe/coupons.ts` — coupon resolution (waitlist > grandfather precedence)
- `src/lib/stripe/types.ts` — DTO types: `SubscriptionDTO`, `InvoiceDTO`, `CheckoutBody`

### 4.3 API routes
- `src/app/api/v1/billing/checkout/session/route.ts` — POST handler (US-002)
- `src/app/api/v1/billing/portal/route.ts` — POST handler (US-003)
- `src/app/api/v1/billing/webhooks/stripe/route.ts` — POST handler (US-004); `runtime = 'nodejs'` flag NOT needed since we use async API on Workers
- `src/app/api/v1/billing/subscription/route.ts` — GET handler returning live DTO (US-006)
- `src/app/api/v1/admin/billing/tier/route.ts` — POST ops-only ENTERPRISE flip (US-005)

### 4.4 UI
- `src/app/account/billing/BillingClient.tsx` — REWRITE — fetch `/api/v1/billing/subscription`, render `<PlanCard live />`, `<InvoiceTable invoices=... />`, `<ManageSubscriptionButton />`, `<SuccessBanner show={status==='success'} />`
- `src/components/account/PlanCard.tsx` — extend to accept live `subscription` prop; render renewal date + cancel-at-period-end flag
- `src/components/account/InvoiceTable.tsx` — remove placeholder "Coming when subscriptions launch"; render `Invoice[]` with `hostedInvoiceUrl` link
- `src/components/account/ManageSubscriptionButton.tsx` — NEW — POSTs to `/api/v1/billing/portal`
- `src/components/billing/CheckoutButton.tsx` — NEW — used on `/pricing` and `/account/billing`; handles signed-out redirect, seat-modal-for-Team
- `src/components/billing/SeatSelectorModal.tsx` — NEW — Team checkout (default 3 seats, min 3, max 100)
- `src/app/pricing/page.tsx` — REWIRE Pro and Team CTAs (US-007); preserve `WaitlistForm` as fallback

### 4.5 Auth callback (US-008)
- `src/app/api/v1/auth/github/installation/callback/route.ts` — DELETE lines 318-334 (the `prisma.user.updateMany` block); rename audit action `INSTALLATION_CREATE` payload reason field if needed; add a regression Vitest

### 4.6 Grandfather migration (US-009)
- `scripts/billing/grandfather-migration.ts` — one-shot tsx script: list `User.tier='PRO'` without `BillingCustomer`, create Stripe Customers, send email with promo code link, write `EmailEvent`
- `src/app/api/v1/cron/grandfather-grace/route.ts` — Cloudflare Cron Trigger handler — daily check for grace expiry → `tierFlip` → audit
- `wrangler.jsonc` — add cron trigger `0 9 * * *` (09:00 UTC daily)
- Email template additions to existing emailer (`src/lib/email/templates/grandfather-welcome.ts`, `grandfather-day75.ts`)

### 4.7 Tests
- `__tests__/lib/stripe/tier-flip.test.ts` — Vitest unit (pure logic, locked transitions)
- `__tests__/lib/stripe/webhook-handlers.test.ts` — Vitest unit (handler dispatch, idempotency)
- `__tests__/api/billing/checkout-session.test.ts` — Vitest integration with mocked Stripe SDK
- `__tests__/api/billing/portal.test.ts` — Vitest integration
- `__tests__/api/billing/webhooks-stripe.test.ts` — Vitest integration including signature failure, replay, unknown event
- `__tests__/api/billing/subscription.test.ts` — Vitest integration
- `__tests__/api/auth/github/installation-callback.regression.test.ts` — Vitest unit asserting `User.tier` not mutated
- `e2e/billing-checkout-happy-path.spec.ts` — Playwright: login → /pricing → click Subscribe → Stripe Checkout (test mode) → webhook → /account/billing shows ACTIVE
- `e2e/billing-cancel-flow.spec.ts` — Playwright: existing sub → portal → cancel → webhook → tier reverts at period end
- `e2e/billing-team-seat-checkout.spec.ts` — Playwright: org admin → Team CTA → seat modal → checkout

---

## 5. Stripe Configuration (one-time, manual + scripted)

### 5.1 Products + Prices (Stripe Dashboard or `scripts/billing/provision-stripe.ts`)
| Product | Price ID env var | Amount | Interval |
|---------|------------------|--------|----------|
| `verified-skill-pro` | `STRIPE_PRICE_PRO_MONTHLY` | $20.00 | month |
| `verified-skill-pro` | `STRIPE_PRICE_PRO_YEARLY` | $192.00 | year (= $16/mo, 20% off) |
| `verified-skill-team` | `STRIPE_PRICE_TEAM_MONTHLY` | $30.00 | per_unit, month |
| `verified-skill-team` | `STRIPE_PRICE_TEAM_YEARLY` | $288.00 | per_unit, year (20% off) |

### 5.2 Coupons
| Coupon ID | Discount | Duration |
|-----------|----------|----------|
| `WAITLIST_50_OFF_YEAR_ONE` | 50% off | repeating, 12 months |
| `GRANDFATHER_100_OFF_90_DAYS` | 100% off | repeating, 3 months |

Promotion Codes (customer-facing) created from the coupons; the grandfather code is the one shipped in the migration email.

### 5.3 Webhook endpoint
- Production URL: `https://verified-skill.com/api/v1/billing/webhooks/stripe`
- Staging URL: `https://staging.verified-skill.com/api/v1/billing/webhooks/stripe`
- Events to subscribe: the 6 listed in AC-US4-03
- `STRIPE_WEBHOOK_SECRET` stored via `wrangler secret put STRIPE_WEBHOOK_SECRET --env production`

### 5.4 Stripe Tax
- Enable Tax in Stripe Dashboard (Settings → Tax)
- Configure origin address (US, DE)
- All Checkout Sessions pass `automatic_tax: { enabled: true }` and `billing_address_collection: 'required'`

### 5.5 Local dev
```bash
stripe listen --forward-to localhost:3000/api/v1/billing/webhooks/stripe
# emits a temporary whsec_… for STRIPE_WEBHOOK_SECRET (.env.local)
```

---

## 6. Migration Plan

1. **Local**: `prisma migrate dev --name billing_models` — generates SQL migration; manually append the CHECK constraint.
2. **Staging**: `prisma migrate deploy` against staging Postgres. Run `scripts/billing/backfill-billing-customer.ts --dry-run` first; review row count; re-run without `--dry-run`. New tables are additive — no risk to hot tables.
3. **Verification on staging**: end-to-end Stripe test-mode checkout; confirm webhook lands; confirm `User.tier` flips; confirm `/account/billing` renders; confirm `Manage Subscription` opens portal.
4. **Production**: `prisma migrate deploy`. Backfill runs automatically as part of the same deploy via Cloudflare Worker post-deploy hook.
5. **Grandfather migration**: run `scripts/billing/grandfather-migration.ts` (sends emails, creates Stripe Customers). Monitor `EmailEvent` table for sends.
6. **Day 75 reminder**: scheduled email goes out automatically via cron handler (or one-shot script run manually).
7. **Day 91 grace expiry**: cron flips tier; audit log shows reason. Slack alert on first batch flip.

---

## 7. Test Strategy

- **Unit (Vitest)**: `tier-flip.ts`, `webhook-handlers.ts`, `coupons.ts` — pure logic, no DB, no network
- **Integration (Vitest + test DB)**: API routes with mocked Stripe SDK (using `vi.mock('stripe', ...)` via `vi.hoisted`); each route's happy path + 2 error paths
- **Regression (Vitest)**: installation callback no longer flips tier
- **E2E (Playwright)**: 3 specs — happy path, cancel, Team seat checkout. Run against `npm run dev` + `stripe listen` forwarding to localhost.
- **Coverage targets**: unit ≥95%, integration ≥90%, E2E covers 100% of US-002, US-003, US-006, US-007 ACs.

---

## 8. Observability + Rollback

- **Logs**: every webhook event → `{ stripeEventId, type, latencyMs, outcome, attempts }` to existing structured logger.
- **Audit**: every tier flip → `AuditEvent` with `action='tier.flip'`, `metadata: { from, to, stripeEventId, reason }`.
- **Metrics**: counters for `billing.checkout.created`, `billing.webhook.received`, `billing.webhook.duplicated`, `billing.tier.flipped`.
- **Rollback**: schema additions are additive, so reverting code does not break the DB. To roll back the auto-PRO removal, redeploy previous version and run `UPDATE "User" SET tier='PRO' WHERE …` ad-hoc — but this should not be needed because the grandfather grace gives a 90-day cushion.
- **Feature flag**: NONE for MVP. The new endpoints simply don't exist on prior versions; `/pricing` rewire is a code change; auto-PRO removal is a code change. If revenue is critical, roll back via `git revert` + redeploy.

---

## 9. Out-of-Scope (re-stated)

- Per-skill metered billing
- Annual-discount in-app math (Stripe handles via separate Price IDs)
- SAML SSO (0842)
- Custom dunning emails
- Multi-currency
- Refund UI

---

## 10. Task Splits

Tasks are split into two files because the work spans backend-heavy schema/webhook implementation AND frontend rewire:

- **`tasks.md`** — backend, schema, webhooks, tier-flip helper, grandfather migration, ops endpoint (Tasks T-001 … T-013)
- **`tasks-frontend.md`** — UI rewires (`BillingClient.tsx`, `/pricing`, components, E2E specs) (Tasks F-001 … F-008)

Total: 21 tasks across both files. Each file caps at 15.
