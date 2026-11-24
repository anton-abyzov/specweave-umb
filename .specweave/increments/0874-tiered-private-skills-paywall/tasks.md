---
increment: 0874-tiered-private-skills-paywall
totalTasks: 14
completedTasks: 14
---

# 0874 Tasks

> All work committed + pushed + released to prod: vskill `c16ee31`, vskill-platform `3016762` (security/billing), `7c0386e` (prod release keeping Free private via VSKILL_FREE_PRIVATE_SKILL_LIMIT=50). Test status verified at closure: tier-gate + tenant-isolation (19), billing/security backend (104), and the increment's own eval-ui chooser/badge suites (32) all green.

### T-001: Flip FREE private limit 50→0 with reversible env escape
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Landed**: `vskill-platform/src/lib/tenant-caps.ts` — `freePrivateSkillLimit()` reads `VSKILL_FREE_PRIVATE_SKILL_LIMIT` (default 0); FREE caps resolve `privateSkillLimit` accordingly.
**Test**: Given a FREE tenant with no override → When caps are resolved → Then privateSkillLimit is 0; with the env set → Then it honors the override.

### T-002: Enforce 402 + upgradeUrl at the three private entry points
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Landed**: `tenants/[tenantId]/skills/route.ts`, `submissions/route.ts`, private-repo connect path return 402 `TENANT_LIMIT_REACHED` + `upgradeUrl` for FREE.
**Test**: Given a FREE tenant → When the first private skill/submission/connect is attempted → Then 402 with upgradeUrl (route.private-paywall.test.ts).

### T-003: PRO/TEAM unlock via effectiveTier
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Landed**: `getTenantCaps`/`effectiveTier` resolve PRO/TEAM to `UNLIMITED_PRIVATE_SKILLS`.
**Test**: Given a PRO tenant → When a private action is attempted → Then it is allowed.

### T-004: Privacy chooser in PublishDrawer
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/components/PublishDrawer.tsx` renders `PrivacyChooser`; `privacy`+`tenantId` threaded from `PublishStatusRow.tsx`/`EditorPanel.tsx` into `submitToQueue`.
**Test**: Given the publish flow → When a privacy option is selected → Then submitToQueue receives the chosen privacy + tenantId (PublishDrawerPrivacy.test.tsx).

### T-005: FREE Private locked + paywall CTA; PRO sends private
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Landed**: locked Private option + "Upgrade to publish privately" CTA opening `PaywallModal` when `useTier().isFree`; PRO/TEAM selection sends `privacy:'private'`.
**Test**: Given FREE → locked Private + paywall; Given PRO → selecting Private sends privacy:'private' (PublishDrawerPrivacy.test.tsx).

### T-006: PrivateBadge on Studio DetailHeader
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/components/DetailHeader.tsx` mounts `PrivateBadge` with a Private/Public indicator.
**Test**: Given a private-source skill → When the detail header renders → Then the Private badge shows (DetailHeader.privateBadge.test.tsx).

### T-007: Sidebar sub-grouping by repo visibility (0848 T-003)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/components/SectionPrivacySubgroup.tsx` mounted in `Sidebar.tsx`; collapsible 🔒/🌐 sub-headers with localStorage-scoped state.
**Test**: Given a mixed section → render two sub-headers; single class → none; collapse persists (SectionPrivacySubgroup.test.tsx).

### T-008: Publisher private-skills footer (0848 T-006)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Landed**: `vskill-platform/src/app/publishers/[name]/PublisherPrivateFooter.tsx` rendered for the owner on `/publishers/[name]`.
**Test**: Given the owner viewing their profile with private skills → footer renders; anonymous → no footer (PublisherPrivateFooter.test.tsx).

### T-009: MarketplaceDrawer "Your private plugins" section (0848 T-007)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/components/MarketplaceDrawer.tsx` renders a "Your private plugins" section above the marketplace list.
**Test**: Given private-repo plugins → top private section renders (MarketplaceDrawer.privatePlugins.test.tsx).

### T-010: Default-deny privacy fail-safe keeps private out of public registry (SEC-4)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Landed**: SEC-4 default-deny privacy fail-safe in the publish pipeline; private-published skills absent from `/api/v1/skills`.
**Test**: Given a private-published skill → When the public registry is queried → Then it is absent (publish-degraded-data / privacy fail-safe tests).

### T-011: VITE_PRICING_URL override in useTier
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/hooks/useTier.ts` honors `VITE_PRICING_URL` (default production).
**Test**: Given the env override → PRICING_URL uses it; otherwise default prod (pricingUrl.test.ts).

### T-012: Real Stripe checkout → webhook tier flip + PAY-1 self-heal
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Landed**: Pro checkout (test 4242) → webhook flips tier → billing UI shows Pro; PAY-1 out-of-order webhook self-heal/backfill in `webhook-handlers.ts`.
**Test**: Given a checkout.session.completed (incl. out-of-order) → tier flips/backfills correctly (webhook-handlers.test.ts, checkout/session route.test.ts).

### T-013: Security + billing hardening (SEC-1..3, PAY-2, PAY-3)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Landed**: SEC-1 tenant-isolation guards on skill version/eval routes; SEC-2 org SSR auth+membership gate (`lib/org-access.ts`); SEC-3 e2e-harness production-host kill-switch; PAY-2 members-invite findUnique→findFirst 500 fix; PAY-3 promo-code resolution.
**Test**: tenant-isolation route tests, org-access tests, e2e-harness guard tests, members/invite tests, coupons tests — all green.

### T-014: Reconcile 0848 (mark landed tasks, author plan.md, finish T-003/T-006/T-007)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Landed**: 0848 `tasks.md` marks T-001/T-002/T-004/T-005 landed and T-003/T-006/T-007 done under 0874; 0848 `plan.md` authored. Verified present in the 0848 increment dir.
**Test**: Given the 0848 increment dir → tasks.md reflects accurate status and plan.md exists.
