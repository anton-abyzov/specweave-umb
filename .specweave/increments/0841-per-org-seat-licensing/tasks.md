# Tasks — 0841 Per-Org Seat Licensing

**Test Mode**: TDD (RED → GREEN → REFACTOR per task)

---

### T-001: Schema migration — rename caps to overrides
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**Test Plan**: Given existing Tenant rows with `privateSkillLimit=50` and `memberLimit=25` → When migration runs → Then both columns are renamed to `*Override`, made nullable, and rows matching old defaults have NULL override values; no data loss for trial-granted rows (e.g., privateSkillLimit=200 stays as 200).
**Files**: `prisma/schema.prisma`, `prisma/migrations/<ts>_rename_caps_to_overrides/migration.sql`
**Verify**: `npx prisma migrate dev` applies cleanly; `SELECT count(*) FROM "Tenant" WHERE "privateSkillLimitOverride" IS NOT NULL` matches pre-migration count of non-default rows.

---

### T-002: Verify 0840 schema dependencies (Subscription.seats, scope, tenantId)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US6-01 | **Status**: [ ] pending
**Test Plan**: Given 0840 is merged → When 0841 inspects `prisma/schema.prisma` → Then `Subscription.seats: Int?`, `Subscription.tenantId: String?`, `BillingCustomer.scope: BillingScope` exist; if any missing, add in T-001 migration with backfill defaults (`scope=USER`, `seats=NULL`).
**Files**: `prisma/schema.prisma` (read), migration amendment if needed.

---

### T-003: Rewrite `getTenantCaps()` helper (tier-derived)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05 | **Status**: [ ] pending
**Test Plan**: Given (tier=FREE, sub=null) → expect `{ privateSkillLimit: 0, memberLimit: 5, tier: 'FREE' }`. Given (tier=TEAM, sub.seats=10) → expect `{ privateSkillLimit: MAX_SAFE_INTEGER, memberLimit: 10, tier: 'TEAM' }`. Given (tier=ENTERPRISE, override.privateSkillLimit=200) → expect override applied. Given (tier=ENTERPRISE, override=null) → expect TEAM defaults.
**Files**: `src/lib/tenant-caps.ts` (rewrite), `src/lib/tenant-caps.test.ts` (table-driven).
**Refactor**: Keep `checkTenantCap()` and `emitCapReachedAudit()` exports unchanged so 0826 callers compile.

---

### T-004: Migrate existing call sites to `getTenantCaps()`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given grep `tenant\.(privateSkillLimit|memberLimit)\b` across `src/` → Then zero matches outside `src/lib/tenant-caps.ts`. All call sites resolved through the helper, passing the active subscription.
**Files**: any route or service that previously read raw columns (skill create, member invite — use grep to enumerate).

---

### T-005: Add seat-cap enforcement in member-invite route
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given a TEAM tenant with `seats=2` and 2 existing members → When admin POSTs a 3rd invite → Then response is 402 with `{ error: "SEAT_LIMIT_REACHED", current: 2, limit: 2, upgradeUrl }` and `tenant.seats.cap_reached` audit emitted with `outcome=DENIED`. Concurrent invites at the cap: only one succeeds (transaction with row lock).
**Files**: `src/app/api/v1/tenants/[tenantId]/members/invite/route.ts`, route test.

---

### T-006: Add 80% warn header on member invite
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given seats=10 and 7 members → When 8th invite succeeds → Then response carries `X-Tenant-Seat-Warn: 0.8` header.
**Files**: `src/app/api/v1/tenants/[tenantId]/members/invite/route.ts`.

---

### T-007: Build `/api/v1/billing/seats/sync` route (manual reconciler)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [ ] pending
**Test Plan**: Given an admin POSTs sync with actualCount=5 and Subscription.seats=3 → When Stripe.subscriptionItems.update succeeds → Then DB updated, `tenant.seats.synced` audit emitted, `200 { changed: true, seats: 5 }`. Idempotent re-run returns `{ changed: false }`. Non-OWNER/ADMIN gets 403. No active TEAM sub gets 400. Stripe 4xx surfaces as 502.
**Files**: `src/app/api/v1/billing/seats/sync/route.ts`, `src/app/api/v1/billing/seats/sync/route.test.ts` (mock Stripe SDK via `vi.hoisted`).

---

### T-008: Build seat-drift reconciliation cron handler
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..AC-US3-06 | **Status**: [ ] pending
**Test Plan**: Given 60 active TEAM subs with 30 of them showing drift → When cron tick runs → Then first 50 are processed, 25 corrected (Stripe success), 5 flagged (Stripe error simulated), audit events emitted accordingly. Given `BILLING_ENABLED=false` → cron exits without DB reads.
**Files**: `src/lib/cron/seat-drift-reconcile.ts`, test, plus wrangler.toml cron registration.

---

### T-009: Extend Stripe webhook handler for TENANT-scope subscriptions
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-04, AC-US6-05 | **Status**: [ ] pending
**Test Plan**: Given `customer.subscription.created` event for a TENANT-scope BillingCustomer → Then Subscription row is upserted with `tenantId`, `seats`, `status`. Given subsequent `.updated` flips status to CANCELED with currentPeriodEnd in past → Then next `getTenantCaps(tenant, sub)` returns FREE caps and `tenant.tier.changed` audit fires once.
**Files**: `src/app/api/v1/billing/webhooks/stripe/route.ts`, fixture-driven webhook test.

---

### T-010: Build `SeatsWidget` React component
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [ ] pending
**Test Plan**: Given (current=5, limit=10) → renders "5/10 seats used" with progress bar. Given (current=10, limit=10) → Invite button disabled with tooltip. Given (current=8, limit=10) → yellow warning banner shown. Component snapshot covers all three states.
**Files**: `src/components/account/SeatsWidget.tsx`, `src/components/account/SeatsWidget.test.tsx`.

---

### T-011: Wire SeatsWidget into `/account/orgs/:tenantId` page
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [ ] pending
**Test Plan**: Given a FREE tenant with 1 member viewed by OWNER → page renders `SeatsWidget` with "Upgrade to Team" CTA linking `/account/billing?upgrade=team&tenantId=...`. "Sync seats" button visible to OWNER, hidden for MEMBER. Click triggers POST to `/api/v1/billing/seats/sync` and shows toast.
**Files**: `src/app/account/orgs/[tenantId]/page.tsx`.

---

### T-012: E2E happy + sad path for seat enforcement and upgrade
**User Story**: US-001, US-005, US-006 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US5-02, AC-US5-04, AC-US6-02 | **Status**: [ ] pending
**Test Plan**: Given org admin with TEAM seats=2 and 2 members → When admin attempts 3rd invite via UI → Then 402 toast shows + Invite button disables. Admin clicks "Upgrade seats" → mock Stripe success webhook → retries invite → succeeds. Test runs end-to-end against Playwright with the test-mode webhook fixture from 0840.
**Files**: `tests/e2e/0841-seat-licensing.spec.ts`.

---

### T-013: Audit event types and audit-log filter UI
**User Story**: US-001, US-002, US-003, US-006 | **Satisfies ACs**: AC-US1-04, AC-US2-04, AC-US3-03, AC-US3-04, AC-US6-04 | **Status**: [ ] pending
**Test Plan**: Given the new event types `tenant.seats.cap_reached`, `tenant.seats.synced`, `tenant.seats.drift.corrected`, `tenant.seats.drift.flagged`, `tenant.tier.changed` → When audit-log viewer is opened for a tenant → Then they appear in the type filter dropdown and render with friendly labels.
**Files**: `src/lib/audit-log.ts` (extend type union), `src/app/account/orgs/[tenantId]/audit-log/page.tsx` (label map).

---

### T-014: Documentation — pricing page seat-counting note + admin runbook
**User Story**: US-004, US-002, US-003 | **Satisfies ACs**: documentation-only (rubric) | **Status**: [ ] pending
**Test Plan**: Given a v1 launch reader → When they hit `/pricing` → Then a footnote clarifies "All org members count as one seat — including viewers." Given an admin debugging a seat-count drift → When they open `.specweave/docs/internal/runbooks/0841-seat-drift.md` → Then they see the cron schedule, audit events to grep for, and manual `seats/sync` curl example.
**Files**: `src/app/pricing/page.tsx` (or MDX), `.specweave/docs/internal/runbooks/0841-seat-drift.md`.

---

### T-015: Run /sw:code-reviewer + /simplify + /sw:grill closure gates
**User Story**: ALL | **Satisfies ACs**: closure quality contract | **Status**: [ ] pending
**Test Plan**: Given all prior tasks complete + tests green → When closure pipeline runs → Then `code-review-report.json` has zero critical/high/medium findings, `/simplify` reports no duplication of cap logic, `/sw:grill` writes `grill-report.json` with no blocking findings, `judge-llm-report.json` produced (or waived).
**Files**: closure artifacts under `.specweave/increments/0841-per-org-seat-licensing/reports/`.
