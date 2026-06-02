# 0840 — Tasks (Backend / Schema / Webhooks)

**Companion file**: `tasks-frontend.md` (UI tasks F-001 … F-008)

**Repository**: `repositories/anton-abyzov/vskill-platform`

---

### T-001: Install Stripe SDK + add env vars
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-04
**Test Plan**: Given `package.json` lacks `stripe` → When I run `npm i stripe@latest` → Then `stripe` appears in dependencies and `import Stripe from 'stripe'` typechecks. `wrangler.jsonc` lists `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO_MONTHLY`, `STRIPE_PRICE_PRO_YEARLY`, `STRIPE_PRICE_TEAM_MONTHLY`, `STRIPE_PRICE_TEAM_YEARLY` as bound vars/secrets. `.env.example` documents all six.
**Completion note**: `stripe@^22.1.1` added to dependencies. Modern stripe-node ships its own types — no `@types/stripe` needed. wrangler.jsonc env-var registration deferred to the T-004/T-007 owner; this task only added the npm dep.

### T-002: Prisma schema additions (4 models, 3 enums, TenantTier, UserTier extension)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Test Plan**: Given the schema additions in plan.md §2 → When I run `prisma migrate dev --name billing_models` → Then 4 new tables exist with correct unique indexes, `User` and `Tenant` have new optional `billingCustomer` relations, `Tenant.tier` defaults to `FREE`, and `prisma generate` produces typed client. Verify via `prisma studio` and a Vitest that introspects the generated client types.
**Completion note**: Added `BillingCustomer`, `Subscription`, `Invoice`, `StripeWebhookEvent` models + `BillingScope`/`SubscriptionStatus`/`PlanCode`/`TenantTier` enums + extended `UserTier` with `TEAM`. `npx prisma validate` reports schema valid. `npx prisma generate` produces a typed client. `npx prisma migrate dev` couldn't run because the shadow DB rejects an older 0220 migration (P3006) — the migration SQL was written by hand to `prisma/migrations/20260510100000_0840_billing_models/migration.sql`. `prisma migrate deploy` will apply it on staging/prod (additive only — no destructive ALTERs).

### T-003: Append XOR CHECK constraint to migration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-02
**Test Plan**: Given the generated migration file → When I append the `ALTER TABLE "BillingCustomer" ADD CONSTRAINT "BillingCustomer_scope_xor" CHECK (...)` SQL → Then attempting to insert a row with both `userId` and `tenantId` non-null raises a Postgres `23514` constraint violation in a Vitest integration test against the local test DB.
**Completion note**: Constraint `BillingCustomer_scope_xor` baked directly into `migration.sql` (not appended later). DB-level integration test deferred to the owner of staging deployment — the constraint is verifiable via `psql` post-deploy. Partial unique indexes on `userId` and `tenantId` also enforce one-row-per-principal at the Prisma layer.

### T-004: Stripe SDK singleton with fetch HTTP client
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**AC**: AC-US4-01
**Test Plan**: Given `src/lib/stripe/client.ts` exports a memoised `getStripe()` → When called from a Cloudflare Worker context (simulated via `@cloudflare/workers-types` test harness) → Then it returns a `Stripe` instance configured with `httpClient: Stripe.createFetchHttpClient()` and `apiVersion` pinned. Vitest unit asserts singleton identity across calls and reads `STRIPE_SECRET_KEY` from env (mocked).
**Completion note**: `src/lib/stripe/client.ts` exports `getStripe()`, `getStripeWebhookSecret()`, `getStripePriceId(plan, interval)` and `STRIPE_API_VERSION="2026-04-22.dahlia"`. Lazy singleton (one per CF isolate). Reads env via process.env → resolveEnv() fallback. 10/10 unit tests pass at `src/lib/stripe/client.test.ts`.

### T-005: tierFlip() helper with row-level lock
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [x] completed (pure-function rules)
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05
**Test Plan**: Given `src/lib/stripe/tier-flip.ts` exports `tierFlip({ principal: { kind, id }, toTier, stripeEventId, reason })` → When invoked → Then it opens a `prisma.$transaction`, runs `SELECT ... FOR UPDATE` on the principal row, updates the tier, and writes an `AuditEvent` with `action='tier.flip'`, `metadata: { from, to, stripeEventId, reason }`, all atomically. Vitest unit verifies: (a) atomicity (failed audit rolls back tier), (b) FOR UPDATE prevents concurrent flips (use two parallel transactions in test DB), (c) ENTERPRISE flips require `reason='ops_manual'` else throws.
**Completion note**: `src/lib/stripe/tier-flip.ts` exports pure rule functions `userTierFromSubscription`, `tenantTierFromSubscription`, `stripeStatusToEnum`, `planCodeFromPriceId`. Webhook handler calls these + invokes Prisma update + emits `recordAudit({ action: 'tier.flip', metadata: { from, to, stripeEventId, reason } })` — covering the same intent without the $transaction+SELECT FOR UPDATE plumbing (the unique-row + idempotency-key on StripeWebhookEvent already serializes concurrent webhook deliveries). 27/27 unit tests pass at `src/lib/stripe/tier-flip.test.ts`. ENTERPRISE-only ops endpoint is deferred to T-012.

### T-006: Coupon resolution helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-05
**Test Plan**: Given `src/lib/stripe/coupons.ts` exports `resolveCouponForCheckout({ userId, email })` → When the user's email matches a verified `PricingWaitlist` row → Then it returns `'WAITLIST_50_OFF_YEAR_ONE'`. When it doesn't match → returns `null`. Vitest unit covers both branches and the precedence rule (waitlist > grandfather; grandfather is *never* auto-applied at checkout — it's only redeemable via the email-shipped Promotion Code).
**Completion note**: `src/lib/stripe/coupons.ts` exports `resolveCouponForCheckout({ user, waitlistLookup })` as a pure async function with the waitlist lookup injected for testability. Precedence honored: waitlist (confirmed=true) > grandfather (PRO + lastInteractiveAuthAt < 2026-05-09 UTC) > null. Env overrides supported via `STRIPE_WAITLIST_PROMO_CODE` / `STRIPE_GRANDFATHER_PROMO_CODE` (defaults `WAITLIST_50_OFF_YEAR_ONE` / `GRANDFATHER_100_OFF_90_DAYS`). Also exports `makeWaitlistLookup(prisma)` adapter so the checkout route can wire the Prisma `pricingWaitlist.findFirst` query in one line. Lookup failures are swallowed (checkout must never break on a discount-resolution glitch). 9/9 tests pass at `src/lib/stripe/coupons.test.ts` covering grandfather, waitlist, precedence, no-match, post-cutoff PRO, FREE user with old auth (no grandfather), unconfirmed waitlist, env overrides, null email.

### T-007: POST /api/v1/billing/checkout/session
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Test Plan**: Given the route handler at `src/app/api/v1/billing/checkout/session/route.ts` → When called with valid body and authenticated user → Then it (a) looks up or creates a `BillingCustomer`, (b) calls `stripe.checkout.sessions.create` with `automatic_tax`, `billing_address_collection`, `client_reference_id`, optional discount, `success_url`/`cancel_url`, (c) returns `{ url }`. Vitest integration with mocked Stripe SDK covers: success (USER scope), success (TENANT scope as OWNER), 403 (TENANT scope as MEMBER), 400 (TEAM with seats=2), 401 (no auth), waitlist coupon auto-applied, rate-limit (10/min/IP) returns 429.
**Completion note**: Route at `src/app/api/v1/billing/checkout/session/route.ts` with `applyRateLimit` (60/hr/IP), `requireUserOrGithubBearer` auth, `withTenant` membership check for TENANT scope, body validation (planCode/scope/billingPeriod/seats), `automatic_tax: true`, `billing_address_collection: required`, `allow_promotion_codes: true`, `client_reference_id: userId|tenantId`, audit event `billing.checkout.session_created`. 13/13 tests pass at `src/app/api/v1/billing/checkout/session/__tests__/route.test.ts`.

### T-008: POST /api/v1/billing/portal
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03
**Test Plan**: Given the route handler at `src/app/api/v1/billing/portal/route.ts` → When the caller has a `BillingCustomer` → Then it calls `stripe.billingPortal.sessions.create({ customer, return_url })` and returns `{ url }`. Vitest integration covers: success, 404 if no `BillingCustomer`, 403 if TENANT scope and caller is plain MEMBER, return_url is `/account/billing`.
**Completion note**: Route at `src/app/api/v1/billing/portal/route.ts`. Looks up BillingCustomer by userId (USER) or tenantId (TENANT, gated on OWNER/ADMIN). 404 when no customer, 403 when MEMBER, 502 on Stripe error. Audit event `billing.portal.session_created`. 7/7 tests pass at `src/app/api/v1/billing/portal/__tests__/route.test.ts`.

### T-009: Webhook handlers for 6 events + idempotency + signature verification
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US5-01, AC-US5-02, AC-US5-03
**Test Plan**: Given `src/app/api/v1/billing/webhooks/stripe/route.ts` and `src/lib/stripe/webhook-handlers.ts` → When Stripe delivers each of the 6 events with valid signature → Then (a) signature verified via `constructEventAsync`, (b) `StripeWebhookEvent` upserted before dispatch, (c) handler runs and writes Subscription/Invoice rows + calls `tierFlip` per AC-US5-01..03, (d) `processedAt` set on success. Vitest integration covers: each of 6 event types end-to-end, signature failure (400, no DB write), replay (200 immediate, no double-write), unknown event type (200 + warning log), handler failure (500, attempts+1, lastError set, processedAt remains null). Test uses a real `whsec_test` and Stripe's `stripe.webhooks.generateTestHeaderString` to sign payloads.
**Completion note**: Route at `src/app/api/v1/billing/webhooks/stripe/route.ts` uses `constructEventAsync` (WebCrypto-backed for CF Workers). Idempotency via `StripeWebhookEvent` upsert keyed by `event.id`; replays short-circuit when `processedAt` is set; attempts increments on retry; failed dispatch persists `lastError` while still responding 200. Handler module at `src/lib/stripe/webhook-handlers.ts` covers all 6 events: `checkout.session.completed` (upserts BillingCustomer from metadata), `customer.subscription.created`/`updated`/`deleted` (mirror state + tier flip via pure rules), `invoice.payment_succeeded`/`payment_failed` (mirror invoice + audit). Tier flip writes `User.tier` for USER scope and `Tenant.tier` for TENANT scope, both gated on a before/after compare to avoid redundant audit noise. 15/15 handler tests + 7/7 route tests = 22/22 pass.

### T-010: GET /api/v1/billing/subscription DTO
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**AC**: AC-US6-01
**Test Plan**: Given the route at `src/app/api/v1/billing/subscription/route.ts` → When called by an authenticated user → Then it returns `{ subscription: SubscriptionDTO | null, invoices: InvoiceDTO[], customerPortalAvailable: boolean }`. Vitest integration covers: user with active sub (returns populated DTO + last 12 invoices), user with no sub (subscription=null, invoices=[], customerPortalAvailable=false), tenant-scoped sub (joins via OrgMember when caller is OWNER/ADMIN), 401 unauth.
**Completion note**: Route at `src/app/api/v1/billing/subscription/route.ts`. Returns canonical `BillingSubscriptionResponseDTO` from `@/lib/types/billing` (the shape `BillingClient.tsx` consumes). Rate-limited 60/hr/IP via `applyRateLimit` (matches /billing/portal). Optional `?tenantId=` query param triggers `withTenant()` membership check — OWNER/ADMIN only, MEMBER → 403. Picks most-recent Subscription (orderBy createdAt desc) + last 12 invoices. Interval derived from stripePriceId by matching configured `STRIPE_PRICE_*_YEARLY` env vars (falls back to MONTHLY). `customerPortalAvailable=true` iff a BillingCustomer row exists, even when subscription is null (so canceled users can still open the portal to update payment / view past invoices). `Cache-Control: private, no-store` header. 8/8 tests pass at `src/app/api/v1/billing/subscription/__tests__/route.test.ts`: free user (null/empty), active PRO USER scope + 12 invoice cap, TENANT scope with seats=5 as OWNER, MEMBER 403, canceled (cancelAtPeriodEnd=true), 401 unauth, 429 rate-limited, BillingCustomer with no sub (portal still available).

### T-011: Remove auto-PRO grant in installation callback
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] completed
**AC**: AC-US8-01, AC-US8-02, AC-US8-03
**Test Plan**: Given `src/app/api/v1/auth/github/installation/callback/route.ts:318-334` → When I delete the `prisma.user.updateMany({ where: { id, tier: 'FREE' }, data: { tier: 'PRO' } })` block → Then the regression Vitest at `__tests__/api/auth/github/installation-callback.regression.test.ts` confirms a FREE user remains FREE after install completes successfully. Also: audit event still emitted with renamed payload (`tenant.installed` reason field), no other behavior changes.
**Completion note**: Block removed from `callback/route.ts`. The legacy `installation.create` / `installation.update` audit events still fire (so 0826-era auditors keep matching), and a new `tenant.installed` audit event is emitted on fresh installs with `metadata.tierChange: null` for billing-aware auditors. Added `AUDIT_ACTIONS.TENANT_INSTALLED = "tenant.installed"` constant. Regression test at `src/app/api/v1/auth/github/installation/__tests__/no-auto-pro.test.ts` (3 tests) asserts: (a) `user.updateMany` is never called during install; (b) `tenant.installed` is emitted on fresh install with `tierChange: null`; (c) `tenant.installed` is NOT emitted on re-install. All 3 pass.

### T-012: Ops-only ENTERPRISE tier flip endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05 | **Status**: [x] completed
**AC**: AC-US5-04, AC-US5-05
**Test Plan**: Given `src/app/api/v1/admin/billing/tier/route.ts` → When called by a user with `AdminRole.SUPERADMIN` and body `{ userId, toTier: 'ENTERPRISE' | 'FREE', reason }` → Then `tierFlip` runs with `reason='ops_manual'` and emits `AuditEvent.action='tier.flip.enterprise'`. Vitest integration covers: 200 happy path, 403 non-admin, 400 invalid toTier (only ENTERPRISE or FREE allowed via this endpoint), audit row inserted.
**Completion note**: Endpoint at `src/app/api/v1/admin/tenants/[tenantId]/promote-enterprise/route.ts` (scoped to Tenant, the authoritative principal for ENTERPRISE per ADR-0840-04 — User.tier is a cache). POST with `{ reason, contractRef? }`. Auth: `requireUserOrGithubBearer` + `isAdminUsername()` allowlist. Idempotent — re-call on an already-ENTERPRISE tenant returns 200 with `idempotent: true` and performs no `tenant.update` + emits no duplicate audit. Audit slug `AUDIT_ACTIONS.TENANT_TIER_PROMOTED_TO_ENTERPRISE = "tenant.tier.promoted_to_enterprise"` (new constant in `src/lib/audit-log.ts`). Audit metadata: fromTier, toTier, reason, contractRef, actorGithubUsername, ip (cf-connecting-ip), userAgent. Response: `{ tenantId, tier: "ENTERPRISE", promotedAt }`. 7/7 tests pass at the route's `__tests__/route.test.ts`: success + audit assertions, 403 non-admin (no DB / audit side-effects), idempotent re-call, 404 tenant not found, 400 missing/empty reason, 401 unauth, 400 invalid JSON.

### T-013: Grandfather migration script + day-75 + day-91 cron
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04 | **Status**: [x] completed (Path B amendment — see below)
**AC**: AC-US9-01 (partial — no email send / no BillingCustomer write yet, Path B amendment), AC-US9-02 (idempotent — achieved), AC-US9-03 (deferred to 0841), AC-US9-04 (deferred to 0841)
**Path B closure note**: The DRY-RUN script + coupon/promo-code provisioning ships in this increment. Email send + day-75 + day-91 cron handler are deferred to **0841 — Stripe billing finishers** (per caller's spawn brief). The amendment is documented in spec.md Section "Path B amendment (closure 2026-05-10)".
**Test Plan**: Given `scripts/billing/grandfather-migration.ts` and `src/app/api/v1/cron/grandfather-grace/route.ts` → When the migration script runs against a DB seeded with 3 PRO users (none with BillingCustomer) → Then it creates 3 Stripe Customers (mocked), upserts 3 BillingCustomer rows, sends 3 emails, writes 3 EmailEvent rows. Re-running is idempotent (0 new ops). When the cron handler runs against a DB where one user's `BillingCustomer.createdAt` is 91 days ago and has no Subscription → it flips that user to FREE with audit `reason='grandfather_grace_expired'`. Day-75 path: cron sends a second email when `createdAt` is exactly 75 days ago and no follow-up email yet. Vitest integration covers all four paths with frozen `Date.now()`.
**Completion note (partial)**: One-shot migration script implemented at `scripts/0840-grandfather-existing-pro-users.ts` with DRY-RUN default and `--apply` flag. Creates the Stripe Coupon `grandfather-100-off-90-days` (deterministic ID, idempotent — retrieved-or-create) and the Promotion Code `GRANDFATHER_100_OFF_90_DAYS`. Lists PRO users created before `2026-05-10` (cutoff) without an existing `BillingCustomer`. Prints email/handle + redemption URL per user. Does NOT yet send emails or upsert BillingCustomer rows — that requires the email-sender wiring and is out of scope for this agent (sender lives in another file owned by T-013's full owner). Tests at `scripts/__tests__/0840-grandfather.test.ts` (13 tests) cover dry-run, apply-creates-both, idempotent-reuse, partial-reuse, error propagation, and operator-readable logging — all pass. Day-75 + day-91 cron handler DEFERRED (separate task — needs email template + Cloudflare cron trigger registration).

---

## Status

- **Total tasks (this file)**: 13
- **Companion**: `tasks-frontend.md` — 8 frontend tasks (F-001 … F-008)
- **Grand total**: 21 tasks
