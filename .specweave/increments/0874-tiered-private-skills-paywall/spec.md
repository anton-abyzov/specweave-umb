---
status: completed
---
# 0874 — Tiered private skills: paid unlocks private + clear UI distinction

> Requirements gathered via AskUserQuestion (scope = "Full incl. paywall gating"; model = "Paid unlocks private") + plan approval (ExitPlanMode 2026-06-10), in lieu of the SpecWeave deep-interview. Source of truth: `reports/spec-reference.md` and the approved plan `~/.claude/plans/sleepy-sprouting-teapot.md`.

## Problem

The recorded lifecycle video showed no visible difference between private and public skills and no payment step. Free tier silently granted 50 private skills (`tenant-caps.ts` `FREE_TIER_CAPS.privateSkillLimit: 50`), Skill Studio's publish flow had no private/public chooser (always sent `privacy:'public'`), and a family of private-badge components was orphaned/never mounted. Increment 0848 (repo-visibility UI) had ~4/7 tasks landed with stale `tasks.md`. This increment makes Free public-only, gates private behind a paid Stripe plan, surfaces a clear private/public distinction, wires the paywall to real Stripe checkout, and reconciles 0848's open ACs.

## User stories

### US-001 — Free tier is public-only; private requires a paid plan

**AC-US1-01** FREE `privateSkillLimit` = 0 (was 50); first private attempt by a FREE tenant returns 402 `TENANT_LIMIT_REACHED` with an `upgradeUrl`.
- [x] **AC-US1-01** — `freePrivateSkillLimit()` defaults to 0; 402 + upgradeUrl returned on first private attempt.

**AC-US1-02** Enforced at all three private entry points: tenant private-skill POST, private submission intake, private-repo connect.
- [x] **AC-US1-02** — enforced in `tenants/[tenantId]/skills/route.ts`, `submissions/route.ts`, and the private-repo connect path.

**AC-US1-03** After a Stripe upgrade to PRO/TEAM the gated actions succeed (via `getTenantCaps`/`effectiveTier`).
- [x] **AC-US1-03** — PRO/TEAM resolve to `UNLIMITED_PRIVATE_SKILLS`; gated actions allowed post-upgrade.

**AC-US1-04** The FREE→0 pivot sits behind a reversible config/env flag.
- [x] **AC-US1-04** — reversible via `VSKILL_FREE_PRIVATE_SKILL_LIMIT` env (prod set to 50 to keep Free private during rollout).

### US-002 — Privacy chooser in Skill Studio publish

**AC-US2-01** `PublishDrawer` renders a PUBLIC/PRIVATE/decide-later chooser (port of platform `PrivacyTernaryField`).
- [x] **AC-US2-01** — `PrivacyChooser` rendered in `PublishDrawer.tsx`.

**AC-US2-02** `privacy` + `tenantId` are threaded to `api.submitToQueue` (not the hardcoded `public`).
- [x] **AC-US2-02** — threaded from `PublishStatusRow.tsx` / `EditorPanel.tsx` into `submitToQueue`.

**AC-US2-03** FREE → Private is locked with an "Upgrade to publish privately" CTA opening the paywall.
- [x] **AC-US2-03** — locked Private option + paywall CTA when `useTier().isFree`.

**AC-US2-04** PRO/TEAM → selecting Private sends `privacy:'private'`.
- [x] **AC-US2-04** — PRO/TEAM selection sends `privacy:'private'` (covered by `PublishDrawerPrivacy.test.tsx`).

### US-003 — Private visually distinct

**AC-US3-01** Studio detail header shows a Private/Public indicator (mount `PrivateBadge`).
- [x] **AC-US3-01** — `PrivateBadge` mounted on `DetailHeader.tsx` (`DetailHeader.privateBadge.test.tsx`).

**AC-US3-02** (0848 T-003) Sidebar sub-group "🔒 Private (N) / 🌐 Public (N)", collapsible with localStorage persistence.
- [x] **AC-US3-02** — `SectionPrivacySubgroup.tsx` mounted in `Sidebar.tsx` with localStorage-scoped collapse.

**AC-US3-03** (0848 T-006) `/publishers/[name]` shows a "+ N private skills not listed publicly" footer for the owner.
- [x] **AC-US3-03** — `PublisherPrivateFooter.tsx` rendered for the owner (`PublisherPrivateFooter.test.tsx`).

**AC-US3-04** (0848 T-007) `MarketplaceDrawer` shows a "Your private plugins" section.
- [x] **AC-US3-04** — section rendered (`MarketplaceDrawer.privatePlugins.test.tsx`).

**AC-US3-05** A private-published skill is absent from the public registry `/api/v1/skills`.
- [x] **AC-US3-05** — default-deny privacy fail-safe (SEC-4) keeps private skills out of the public registry.

### US-004 — Paywall → real Stripe checkout

**AC-US4-01** `useTier.ts` `PRICING_URL` honors a `VITE_PRICING_URL` override (default = prod).
- [x] **AC-US4-01** — `VITE_PRICING_URL` override added in `useTier.ts` (`pricingUrl.test.ts`).

**AC-US4-02** Paywall → real Stripe test checkout (4242) → webhook flips tier → billing UI shows the paid plan.
- [x] **AC-US4-02** — Pro checkout (4242) → webhook tier flip verified; PAY-1 out-of-order webhook self-heal/backfill added.

### US-005 — 0848 reconciled

**AC-US5-01** 0848 `tasks.md` marks landed T-001/T-002/T-004/T-005; T-003/T-006/T-007 done here; `plan.md` authored.
- [x] **AC-US5-01** — 0848 `tasks.md` reconciled and `plan.md` authored (verified present in 0848 increment dir).

## Out of scope

- Hosted private-publish on production (the platform private-publish/scan gaps remain separate, larger work).
- Team/seat checkout demo (needs a real org); the demo uses the Pro USER path.
