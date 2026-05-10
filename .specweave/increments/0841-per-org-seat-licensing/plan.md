# Plan — 0841 Per-Org Seat Licensing

## Architecture

```
                 invite member
                       │
                       ▼
   ┌─────────────────────────────────┐
   │ /api/v1/tenants/:id/members/    │
   │  invite     (POST)              │
   │  → getTenantCaps(tenant, sub)   │
   │  → count(OrgMember)             │
   │  → 402 if at cap                │
   └────────────┬────────────────────┘
                │
                │ on success
                ▼
   ┌─────────────────────────────────┐    ┌────────────────────┐
   │ Subscription.seats             │◄───┤ /billing/seats/sync│
   │ (write-back on next sync)      │    │  (manual reconcile) │
   └────────────┬────────────────────┘    └─────────┬──────────┘
                │                                   │
                │      ┌─────────────────────────┐  │
                │      │ Cron */15 * * * *       │──┘
                │      │ scan TEAM subs, fix     │
                │      │ drift via Stripe API    │
                │      └─────────────────────────┘
                ▼
        ┌────────────────────┐
        │ Stripe             │
        │ subscriptionItems  │
        │   .update(qty)     │
        └────────────────────┘
```

Tier-derivation is centralized in `src/lib/tenant-caps.ts`. All cap reads go through `getTenantCaps(tenant, subscription)` — no direct reads of the (now renamed) override columns outside the helper.

## Files to Touch

### New files
- `src/app/api/v1/billing/seats/sync/route.ts` — POST handler for manual reconciliation (US-002)
- `src/app/api/v1/billing/seats/sync/route.test.ts` — Vitest integration with mocked Stripe SDK
- `src/lib/cron/seat-drift-reconcile.ts` — cron handler (US-003); registered in worker entry alongside `cohort-dispatch`
- `src/lib/cron/seat-drift-reconcile.test.ts` — Vitest unit + integration
- `src/components/account/SeatsWidget.tsx` — React widget for org page (US-005)
- `src/components/account/SeatsWidget.test.tsx` — RTL snapshot + state matrix
- `tests/e2e/0841-seat-licensing.spec.ts` — Playwright E2E (US-001 + US-005 happy/sad paths)

### Modified files
- `prisma/schema.prisma`:
  - Rename `Tenant.privateSkillLimit` → `Tenant.privateSkillLimitOverride` (Int?, nullable)
  - Rename `Tenant.memberLimit` → `Tenant.memberLimitOverride` (Int?, nullable)
  - Migration data step: copy current values into the renamed columns; null out where they equal defaults (50/25)
  - Verify `Subscription.seats: Int?`, `Subscription.tenantId: String?` exist (added in 0840); if not, add them in this migration
- `src/lib/tenant-caps.ts` — rewrite around `getTenantCaps()`; keep `checkTenantCap()` and `emitCapReachedAudit()` signatures stable (callers in 0826 still use them)
- `src/app/api/v1/tenants/[tenantId]/members/invite/route.ts` — add seat-cap branch (US-001)
- `src/app/api/v1/billing/webhooks/stripe/route.ts` — extend `customer.subscription.*` handlers to pick up TENANT-scope subscriptions and emit `tenant.tier.changed` (US-006)
- `src/app/account/orgs/[tenantId]/page.tsx` — render `SeatsWidget`, gate Invite button (US-005)
- Worker entry / cron registration (`wrangler.toml` + cron handler dispatch in `src/worker.ts` or wherever cohort-dispatch is wired) — register the new `*/15 * * * *` schedule

## ADRs

### ADR-NEW-1: Seat counting timing — at-create vs nightly recount

**Decision**: Count seats **at OrgMember.create time** (synchronous check inside the invite route's transaction) **and** run a **15-min cron** for drift reconciliation.

**Why**:
- At-create check gives instant 402 feedback; admins know immediately why an invite was rejected.
- Cron drift reconciliation handles silent paths: admin removes a member directly in DB, GitHub uninstall purges members, etc. Without the cron, Stripe quantity diverges and we under-bill (or over-bill).
- Nightly-only would let an admin invite past the cap during the day if Stripe usage hadn't been pushed yet.
- Real-time-only would couple every invite to a Stripe API call (latency + failure surface). Decoupling: invite hits local count; cron pushes to Stripe.

**Consequence**: Two write paths to `Subscription.seats` (manual sync + cron). Both go through the same helper to avoid race-y double-write. We rely on Stripe's idempotency keys for the API call.

### ADR-NEW-2: Viewer-free seats — NOT in v1

**Decision**: All `OrgRole` values count as one seat. No "free viewer" tier.

**Why**:
- Stripe modeling for variable-price-per-role is non-trivial (multiple subscription items, proration math).
- Vercel-style viewer-free is a 2027 feature; for v1 a flat $30/seat is the SKU we sell on the pricing page (locked in 0833).
- Reduces audit-event surface: tier change doesn't depend on role mix, only on member count.

**Consequence**: Documented on `/pricing` page when 0841 ships ("All members count as a seat, including viewers"). Re-evaluate if customer feedback flags it.

### ADR-NEW-3: Tier-derivation centralized in `getTenantCaps()`

**Decision**: `Tenant.privateSkillLimit` / `memberLimit` are **renamed to overrides** (nullable) and never read directly outside the helper. The helper takes `(tenant, subscription)` and returns the effective caps.

**Why**:
- Single source of truth — adding a new tier (e.g., starter) is a one-file change.
- Keeps schema migration backwards-compatible: existing trial grants live on as overrides.
- Test surface is small (4 tier branches × override-or-not).

**Consequence**: Code review must enforce no direct reads of the override columns. Add an ESLint rule or grep guard in `/sw:grill`.

## Database Migrations

```sql
-- Rename existing columns to overrides
ALTER TABLE "Tenant" RENAME COLUMN "privateSkillLimit" TO "privateSkillLimitOverride";
ALTER TABLE "Tenant" RENAME COLUMN "memberLimit" TO "memberLimitOverride";
ALTER TABLE "Tenant" ALTER COLUMN "privateSkillLimitOverride" DROP NOT NULL;
ALTER TABLE "Tenant" ALTER COLUMN "memberLimitOverride" DROP NOT NULL;

-- Null out values that match the previous defaults (so derived tier caps win)
UPDATE "Tenant" SET "privateSkillLimitOverride" = NULL WHERE "privateSkillLimitOverride" = 50;
UPDATE "Tenant" SET "memberLimitOverride" = NULL WHERE "memberLimitOverride" = 25;
```

Migration is reversible — old defaults are restorable via the inverse `UPDATE` if rollback is needed within 7 days.

## Test Strategy

- **Vitest unit**: `tenant-caps.test.ts` — table-driven over (tier, hasOverride, seats) → expected caps. Coverage target: 100% of `getTenantCaps()` branches.
- **Vitest integration**: `seats/sync/route.test.ts` with `vi.hoisted()` + `vi.mock("stripe")` — happy path, idempotent re-run, 400 on no TEAM sub, 502 on Stripe error.
- **Vitest integration**: `seat-drift-reconcile.test.ts` — drift detected and corrected, drift detected and Stripe-fails (flagged), batching, BILLING_ENABLED=false skip.
- **Playwright E2E** (`tests/e2e/0841-seat-licensing.spec.ts`): admin invites N members successfully, observes 402 + upgrade banner on (N+1)th, navigates to `/account/billing`, fakes a Stripe upgrade (intercepted via test-mode webhook fixture), retries invite successfully.
- **Coverage targets**: unit 95%, integration 90%, e2e 100% of AC scenarios that exercise UI flows.

## Out of Scope (explicit)

- SCIM / WorkOS-driven seat changes → 0842
- Per-role pricing (viewer-free) → revisit post v1
- Self-service seat slider in UI → admins reduce seats by removing members + clicking "Sync seats"
- Proration UX (admin sees proration preview) → defer; Stripe's default proration applies silently
- Stripe webhook retry storms / dead-letter queue → handled by 0840's `StripeWebhookEvent` idempotency, no new infra here
