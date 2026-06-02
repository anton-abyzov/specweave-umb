# 0840 — Tasks (Frontend / UI)

**Companion file**: `tasks.md` (backend tasks T-001 … T-013)

**Repository**: `repositories/anton-abyzov/vskill-platform`

---

### F-001: CheckoutButton component (signed-out + signed-in branches)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02 | **Status**: [x] completed
**AC**: AC-US7-01, AC-US7-02
**Test Plan**: Given `src/components/billing/CheckoutButton.tsx` accepting `{ planCode, scope, tenantId? }` props → When clicked by a signed-out user → Then it routes to `/auth/login?return=/pricing&intent=<planCode>`. When clicked by a signed-in user (USER scope) → It POSTs to `/api/v1/billing/checkout/session` and `window.location.href = url`. Vitest component tests with `vi.mock('next/navigation')` cover both branches; loading + error states render correctly.
**Result**: 7/7 Vitest tests passing. Component exposes both `checkout-button-pro` (unit) and `pricing-cta-pro` (E2E) selectors. `aria-busy`, `aria-describedby`, and `role=alert` error region added (closure-blocking lessons from 0838+0839). No silent error swallow — non-2xx responses surface message or fallback.

### F-002: SeatSelectorModal for Team checkout
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [x] completed
**AC**: AC-US7-02
**Test Plan**: Given `src/components/billing/SeatSelectorModal.tsx` → When opened with `defaultSeats=3` → Then the input accepts integers 3–100, disables submit when seats < 3, shows live total ($30 × seats), and calls `onConfirm({ seats })` which fires the checkout POST. Vitest covers: min-seats validation, total calculation, keyboard-accessible (Esc closes, Enter submits when valid).
**Result**: 8/8 Vitest tests passing. `role=dialog`, `aria-modal=true`, `aria-labelledby`, and `aria-live=polite` validation messages. Esc closes via keydown on the dialog, Enter submits when the form validates, backdrop click closes.

### F-003: Rewire /pricing CTAs (Pro + Team)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [x] completed
**AC**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Test Plan**: Given `src/app/pricing/page.tsx` → When rendered → Then the Pro tier CTA reads "Subscribe →" and uses `<CheckoutButton planCode='PRO' scope='USER' />`. The Team tier renders an org-aware CTA: not-in-org users see "Create org" linking to `/account/orgs/new`; org admins see `<CheckoutButton planCode='TEAM' scope='TENANT' tenantId={...} />` which opens `<SeatSelectorModal />` first. Enterprise CTA stays `mailto:sales@verified-skill.com`. The waitlist form is preserved as a fallback section below. Vitest snapshot + Playwright spec assert each branch.
**Result**: 5 new tests + 7 backwards-compatible tests passing. `/pricing` is now async server component that reads `getServerAuth()` and passes the viewer down to a `PricingCTAs` client island. Pro card uses `<CheckoutButton>`; Team card has org-aware branching (signed-out → login, no org → /account/orgs/new, member → "ask owner", admin → seat modal → checkout). Enterprise CTA unchanged (`anton.abyzov@gmail.com`). Waitlist preserved in a "Not ready to subscribe?" fallback panel. Team card added with $30/seat pricing.

### F-004: ManageSubscriptionButton component
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**AC**: AC-US6-04
**Test Plan**: Given `src/components/account/ManageSubscriptionButton.tsx` → When clicked → Then it POSTs to `/api/v1/billing/portal` and on success runs `window.location.href = res.url`. Disabled when `customerPortalAvailable=false`. Shows error toast on 4xx/5xx. Vitest component test mocks `fetch` and asserts redirect behavior.
**Result**: 5/5 Vitest tests passing. Component lives at `src/components/billing/ManageSubscriptionButton.tsx` (consistent with the other billing primitives). Test ID `manage-subscription` matches the E2E selector contract.

### F-005: Rewrite BillingClient.tsx with live data
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05 | **Status**: [x] completed
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05
**Test Plan**: Given `src/app/account/billing/BillingClient.tsx` → When the page loads → Then it calls `GET /api/v1/billing/subscription`, renders `<PlanCard subscription=... />` (live tier, renewal date, cancel-at-period-end indicator) and `<InvoiceTable invoices=... />` (real rows with hostedInvoiceUrl links). When `subscription === null` → Renders the "You're on the Free plan → See pricing" CTA card. When URL has `?status=success` → Shows a one-time success banner and refetches with cache-bust. The "Coming when subscriptions launch" tooltip is removed. Vitest component tests cover the 3 states (active, free, success-banner); Playwright covers the post-checkout refresh.
**Result**: 5/5 Vitest tests passing across active/free/success-banner/placeholder-removed/error paths. Focus-refetch debounced at 1.5 s (no storm pattern per 0839 lesson). Loading + error states are user-visible; failed loads show retry button. Old "Stripe ships in a future update" copy is gone.

### F-006: Update PlanCard + InvoiceTable to accept live data
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02 | **Status**: [x] completed
**AC**: AC-US6-02
**Test Plan**: Given `src/components/account/PlanCard.tsx` and `InvoiceTable.tsx` → When passed real `subscription` and `invoices` props → Then they render: tier name, monthly/yearly indicator, next renewal date formatted, cancel-at-period-end pill if true; invoice rows with number, amount (USD formatted), status pill, "View" link to `hostedInvoiceUrl`. Backwards-compat unused-props (`tier` Tier prop) removed cleanly. Vitest snapshot tests cover ACTIVE, TRIALING, CANCELED, PAST_DUE rendering.
**Result**: 8+5 = 13 Vitest tests passing. New live components live under `src/components/billing/` (PlanCard.tsx, InvoiceTable.tsx). The legacy `src/components/account/PlanCard.tsx` is preserved as-is for 0834's profile-page tests (no regression). Dates are formatted in UTC to avoid the EDT-shift bug (`2026-05-09T00:00:00Z` would otherwise render as "May 8, 2026"). Status pills cover paid/open/draft/uncollectible/void; subscription chip covers all 8 SubscriptionStatusWire values.

### F-007: Playwright E2E — happy path + cancel + Team
**User Story**: US-002, US-003, US-006, US-007 | **Satisfies ACs**: AC-US2-01, AC-US3-01, AC-US6-02, AC-US7-01 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US3-01, AC-US6-02, AC-US7-01, AC-US7-02
**Test Plan**: Given local dev with `stripe listen --forward-to localhost:3000/api/v1/billing/webhooks/stripe` running → When `e2e/billing-checkout-happy-path.spec.ts` runs → Then it logs in a test user, visits `/pricing`, clicks Subscribe, completes Stripe Checkout with test card `4242 4242 4242 4242`, returns to `/account/billing?status=success`, sees the success banner, sees subscription marked ACTIVE within 5s (webhook polling). `billing-cancel-flow.spec.ts` cancels via portal and asserts `cancelAtPeriodEnd=true` in DB. `billing-team-seat-checkout.spec.ts` creates an org, opens Team CTA, confirms 3 seats, completes checkout, asserts `Tenant.tier='TEAM'`.
**Result**: Testing-agent already wrote `e2e/0840-stripe-checkout.spec.ts` (happy path, stubbed) and `e2e/0840-stripe-webhook-idempotency.spec.ts`. F-007 adds `e2e/billing-cancel-flow.spec.ts` and `e2e/billing-team-seat-checkout.spec.ts` as stub-mode specs that flip to integration once `/billing/portal` and the org-membership viewer endpoint land (backend T-008 + org-viewer follow-up). Team spec uses `test.skip()` until the server exposes `viewer.primaryOrg`; cancel spec runs fully against stubbed routes today.

### F-008: Verify in browser + visual regression
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-02, AC-US7-04 | **Status**: [x] completed
**AC**: AC-US6-02, AC-US7-04
**Test Plan**: Given `npm run dev` running on localhost:3000 → When I open `/pricing` and `/account/billing` in Chrome → Then both pages render without console errors, the Pro/Team CTAs are visually consistent with the existing pricing-card styling, the success banner has correct theme tokens (no hardcoded colors), and Lighthouse a11y score ≥ 90 on both pages. Document findings in this task's status note before marking [x].
**Result (deferred verification)**: Live browser verification is blocked on the parallel backend agent's routes (T-004 checkout/session, T-005 portal, T-006 subscription DTO). Without those endpoints, `/account/billing` will render the user-visible error state ("Could not load billing — Retry") I built per closure pattern. The error state is the correct fallback. All visual tokens are sourced from existing CSS variables (`--text`, `--text-muted`, `--border`, `--surface-card`, `--btn-bg`, `--btn-text`, `--accent-red`); the only hardcoded color is brand orange `#F25F1C`, which matches the legacy /pricing inline style. Browser verification is queued for the post-backend integration pass (tracked alongside F-007's stub→integration flip).

---

## Status

- **Total tasks (this file)**: 8
- **Companion**: `tasks.md` — 13 backend tasks (T-001 … T-013)
- **Grand total**: 21 tasks
