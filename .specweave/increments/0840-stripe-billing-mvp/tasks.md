# 0840 — Tasks (Backend / Schema / Webhooks)

**Companion file**: `tasks-frontend.md` (UI tasks F-001 … F-008)

**Repository**: `repositories/anton-abyzov/vskill-platform`

---

### T-001: Install Stripe SDK + add env vars
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] pending
**AC**: AC-US2-04
**Test Plan**: Given `package.json` lacks `stripe` → When I run `npm i stripe@latest` → Then `stripe` appears in dependencies and `import Stripe from 'stripe'` typechecks. `wrangler.jsonc` lists `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO_MONTHLY`, `STRIPE_PRICE_PRO_YEARLY`, `STRIPE_PRICE_TEAM_MONTHLY`, `STRIPE_PRICE_TEAM_YEARLY` as bound vars/secrets. `.env.example` documents all six.

### T-002: Prisma schema additions (4 models, 3 enums, TenantTier, UserTier extension)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Test Plan**: Given the schema additions in plan.md §2 → When I run `prisma migrate dev --name billing_models` → Then 4 new tables exist with correct unique indexes, `User` and `Tenant` have new optional `billingCustomer` relations, `Tenant.tier` defaults to `FREE`, and `prisma generate` produces typed client. Verify via `prisma studio` and a Vitest that introspects the generated client types.

### T-003: Append XOR CHECK constraint to migration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**AC**: AC-US1-02
**Test Plan**: Given the generated migration file → When I append the `ALTER TABLE "BillingCustomer" ADD CONSTRAINT "BillingCustomer_scope_xor" CHECK (...)` SQL → Then attempting to insert a row with both `userId` and `tenantId` non-null raises a Postgres `23514` constraint violation in a Vitest integration test against the local test DB.

### T-004: Stripe SDK singleton with fetch HTTP client
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**AC**: AC-US4-01
**Test Plan**: Given `src/lib/stripe/client.ts` exports a memoised `getStripe()` → When called from a Cloudflare Worker context (simulated via `@cloudflare/workers-types` test harness) → Then it returns a `Stripe` instance configured with `httpClient: Stripe.createFetchHttpClient()` and `apiVersion` pinned. Vitest unit asserts singleton identity across calls and reads `STRIPE_SECRET_KEY` from env (mocked).

### T-005: tierFlip() helper with row-level lock
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [ ] pending
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05
**Test Plan**: Given `src/lib/stripe/tier-flip.ts` exports `tierFlip({ principal: { kind, id }, toTier, stripeEventId, reason })` → When invoked → Then it opens a `prisma.$transaction`, runs `SELECT ... FOR UPDATE` on the principal row, updates the tier, and writes an `AuditEvent` with `action='tier.flip'`, `metadata: { from, to, stripeEventId, reason }`, all atomically. Vitest unit verifies: (a) atomicity (failed audit rolls back tier), (b) FOR UPDATE prevents concurrent flips (use two parallel transactions in test DB), (c) ENTERPRISE flips require `reason='ops_manual'` else throws.

### T-006: Coupon resolution helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
**AC**: AC-US2-05
**Test Plan**: Given `src/lib/stripe/coupons.ts` exports `resolveCouponForCheckout({ userId, email })` → When the user's email matches a verified `PricingWaitlist` row → Then it returns `'WAITLIST_50_OFF_YEAR_ONE'`. When it doesn't match → returns `null`. Vitest unit covers both branches and the precedence rule (waitlist > grandfather; grandfather is *never* auto-applied at checkout — it's only redeemable via the email-shipped Promotion Code).

### T-007: POST /api/v1/billing/checkout/session
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [ ] pending
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Test Plan**: Given the route handler at `src/app/api/v1/billing/checkout/session/route.ts` → When called with valid body and authenticated user → Then it (a) looks up or creates a `BillingCustomer`, (b) calls `stripe.checkout.sessions.create` with `automatic_tax`, `billing_address_collection`, `client_reference_id`, optional discount, `success_url`/`cancel_url`, (c) returns `{ url }`. Vitest integration with mocked Stripe SDK covers: success (USER scope), success (TENANT scope as OWNER), 403 (TENANT scope as MEMBER), 400 (TEAM with seats=2), 401 (no auth), waitlist coupon auto-applied, rate-limit (10/min/IP) returns 429.

### T-008: POST /api/v1/billing/portal
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**AC**: AC-US3-01, AC-US3-02, AC-US3-03
**Test Plan**: Given the route handler at `src/app/api/v1/billing/portal/route.ts` → When the caller has a `BillingCustomer` → Then it calls `stripe.billingPortal.sessions.create({ customer, return_url })` and returns `{ url }`. Vitest integration covers: success, 404 if no `BillingCustomer`, 403 if TENANT scope and caller is plain MEMBER, return_url is `/account/billing`.

### T-009: Webhook handlers for 6 events + idempotency + signature verification
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [ ] pending
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US5-01, AC-US5-02, AC-US5-03
**Test Plan**: Given `src/app/api/v1/billing/webhooks/stripe/route.ts` and `src/lib/stripe/webhook-handlers.ts` → When Stripe delivers each of the 6 events with valid signature → Then (a) signature verified via `constructEventAsync`, (b) `StripeWebhookEvent` upserted before dispatch, (c) handler runs and writes Subscription/Invoice rows + calls `tierFlip` per AC-US5-01..03, (d) `processedAt` set on success. Vitest integration covers: each of 6 event types end-to-end, signature failure (400, no DB write), replay (200 immediate, no double-write), unknown event type (200 + warning log), handler failure (500, attempts+1, lastError set, processedAt remains null). Test uses a real `whsec_test` and Stripe's `stripe.webhooks.generateTestHeaderString` to sign payloads.

### T-010: GET /api/v1/billing/subscription DTO
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [ ] pending
**AC**: AC-US6-01
**Test Plan**: Given the route at `src/app/api/v1/billing/subscription/route.ts` → When called by an authenticated user → Then it returns `{ subscription: SubscriptionDTO | null, invoices: InvoiceDTO[], customerPortalAvailable: boolean }`. Vitest integration covers: user with active sub (returns populated DTO + last 12 invoices), user with no sub (subscription=null, invoices=[], customerPortalAvailable=false), tenant-scoped sub (joins via OrgMember when caller is OWNER/ADMIN), 401 unauth.

### T-011: Remove auto-PRO grant in installation callback
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [ ] pending
**AC**: AC-US8-01, AC-US8-02, AC-US8-03
**Test Plan**: Given `src/app/api/v1/auth/github/installation/callback/route.ts:318-334` → When I delete the `prisma.user.updateMany({ where: { id, tier: 'FREE' }, data: { tier: 'PRO' } })` block → Then the regression Vitest at `__tests__/api/auth/github/installation-callback.regression.test.ts` confirms a FREE user remains FREE after install completes successfully. Also: audit event still emitted with renamed payload (`tenant.installed` reason field), no other behavior changes.

### T-012: Ops-only ENTERPRISE tier flip endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05 | **Status**: [ ] pending
**AC**: AC-US5-04, AC-US5-05
**Test Plan**: Given `src/app/api/v1/admin/billing/tier/route.ts` → When called by a user with `AdminRole.SUPERADMIN` and body `{ userId, toTier: 'ENTERPRISE' | 'FREE', reason }` → Then `tierFlip` runs with `reason='ops_manual'` and emits `AuditEvent.action='tier.flip.enterprise'`. Vitest integration covers: 200 happy path, 403 non-admin, 400 invalid toTier (only ENTERPRISE or FREE allowed via this endpoint), audit row inserted.

### T-013: Grandfather migration script + day-75 + day-91 cron
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04 | **Status**: [ ] pending
**AC**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04
**Test Plan**: Given `scripts/billing/grandfather-migration.ts` and `src/app/api/v1/cron/grandfather-grace/route.ts` → When the migration script runs against a DB seeded with 3 PRO users (none with BillingCustomer) → Then it creates 3 Stripe Customers (mocked), upserts 3 BillingCustomer rows, sends 3 emails, writes 3 EmailEvent rows. Re-running is idempotent (0 new ops). When the cron handler runs against a DB where one user's `BillingCustomer.createdAt` is 91 days ago and has no Subscription → it flips that user to FREE with audit `reason='grandfather_grace_expired'`. Day-75 path: cron sends a second email when `createdAt` is exactly 75 days ago and no follow-up email yet. Vitest integration covers all four paths with frozen `Date.now()`.

---

## Status

- **Total tasks (this file)**: 13
- **Companion**: `tasks-frontend.md` — 8 frontend tasks (F-001 … F-008)
- **Grand total**: 21 tasks
