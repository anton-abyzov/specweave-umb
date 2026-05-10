# 0840 — Tasks (Frontend / UI)

**Companion file**: `tasks.md` (backend tasks T-001 … T-013)

**Repository**: `repositories/anton-abyzov/vskill-platform`

---

### F-001: CheckoutButton component (signed-out + signed-in branches)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02 | **Status**: [ ] pending
**AC**: AC-US7-01, AC-US7-02
**Test Plan**: Given `src/components/billing/CheckoutButton.tsx` accepting `{ planCode, scope, tenantId? }` props → When clicked by a signed-out user → Then it routes to `/auth/login?return=/pricing&intent=<planCode>`. When clicked by a signed-in user (USER scope) → It POSTs to `/api/v1/billing/checkout/session` and `window.location.href = url`. Vitest component tests with `vi.mock('next/navigation')` cover both branches; loading + error states render correctly.

### F-002: SeatSelectorModal for Team checkout
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [ ] pending
**AC**: AC-US7-02
**Test Plan**: Given `src/components/billing/SeatSelectorModal.tsx` → When opened with `defaultSeats=3` → Then the input accepts integers 3–100, disables submit when seats < 3, shows live total ($30 × seats), and calls `onConfirm({ seats })` which fires the checkout POST. Vitest covers: min-seats validation, total calculation, keyboard-accessible (Esc closes, Enter submits when valid).

### F-003: Rewire /pricing CTAs (Pro + Team)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [ ] pending
**AC**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Test Plan**: Given `src/app/pricing/page.tsx` → When rendered → Then the Pro tier CTA reads "Subscribe →" and uses `<CheckoutButton planCode='PRO' scope='USER' />`. The Team tier renders an org-aware CTA: not-in-org users see "Create org" linking to `/account/orgs/new`; org admins see `<CheckoutButton planCode='TEAM' scope='TENANT' tenantId={...} />` which opens `<SeatSelectorModal />` first. Enterprise CTA stays `mailto:sales@verified-skill.com`. The waitlist form is preserved as a fallback section below. Vitest snapshot + Playwright spec assert each branch.

### F-004: ManageSubscriptionButton component
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [ ] pending
**AC**: AC-US6-04
**Test Plan**: Given `src/components/account/ManageSubscriptionButton.tsx` → When clicked → Then it POSTs to `/api/v1/billing/portal` and on success runs `window.location.href = res.url`. Disabled when `customerPortalAvailable=false`. Shows error toast on 4xx/5xx. Vitest component test mocks `fetch` and asserts redirect behavior.

### F-005: Rewrite BillingClient.tsx with live data
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05 | **Status**: [ ] pending
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05
**Test Plan**: Given `src/app/account/billing/BillingClient.tsx` → When the page loads → Then it calls `GET /api/v1/billing/subscription`, renders `<PlanCard subscription=... />` (live tier, renewal date, cancel-at-period-end indicator) and `<InvoiceTable invoices=... />` (real rows with hostedInvoiceUrl links). When `subscription === null` → Renders the "You're on the Free plan → See pricing" CTA card. When URL has `?status=success` → Shows a one-time success banner and refetches with cache-bust. The "Coming when subscriptions launch" tooltip is removed. Vitest component tests cover the 3 states (active, free, success-banner); Playwright covers the post-checkout refresh.

### F-006: Update PlanCard + InvoiceTable to accept live data
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02 | **Status**: [ ] pending
**AC**: AC-US6-02
**Test Plan**: Given `src/components/account/PlanCard.tsx` and `InvoiceTable.tsx` → When passed real `subscription` and `invoices` props → Then they render: tier name, monthly/yearly indicator, next renewal date formatted, cancel-at-period-end pill if true; invoice rows with number, amount (USD formatted), status pill, "View" link to `hostedInvoiceUrl`. Backwards-compat unused-props (`tier` Tier prop) removed cleanly. Vitest snapshot tests cover ACTIVE, TRIALING, CANCELED, PAST_DUE rendering.

### F-007: Playwright E2E — happy path + cancel + Team
**User Story**: US-002, US-003, US-006, US-007 | **Satisfies ACs**: AC-US2-01, AC-US3-01, AC-US6-02, AC-US7-01 | **Status**: [ ] pending
**AC**: AC-US2-01, AC-US3-01, AC-US6-02, AC-US7-01, AC-US7-02
**Test Plan**: Given local dev with `stripe listen --forward-to localhost:3000/api/v1/billing/webhooks/stripe` running → When `e2e/billing-checkout-happy-path.spec.ts` runs → Then it logs in a test user, visits `/pricing`, clicks Subscribe, completes Stripe Checkout with test card `4242 4242 4242 4242`, returns to `/account/billing?status=success`, sees the success banner, sees subscription marked ACTIVE within 5s (webhook polling). `billing-cancel-flow.spec.ts` cancels via portal and asserts `cancelAtPeriodEnd=true` in DB. `billing-team-seat-checkout.spec.ts` creates an org, opens Team CTA, confirms 3 seats, completes checkout, asserts `Tenant.tier='TEAM'`.

### F-008: Verify in browser + visual regression
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-02, AC-US7-04 | **Status**: [ ] pending
**AC**: AC-US6-02, AC-US7-04
**Test Plan**: Given `npm run dev` running on localhost:3000 → When I open `/pricing` and `/account/billing` in Chrome → Then both pages render without console errors, the Pro/Team CTAs are visually consistent with the existing pricing-card styling, the success banner has correct theme tokens (no hardcoded colors), and Lighthouse a11y score ≥ 90 on both pages. Document findings in this task's status note before marking [x].

---

## Status

- **Total tasks (this file)**: 8
- **Companion**: `tasks.md` — 13 backend tasks (T-001 … T-013)
- **Grand total**: 21 tasks
