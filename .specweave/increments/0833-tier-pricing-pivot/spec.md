---
increment: 0833-tier-pricing-pivot
title: >-
  Pivot pricing model: free covers most users; paid gates private repos;
  enterprise is support
type: change-request
priority: P0
status: completed
created: 2026-05-08T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
projects:
  - vskill
parent: 0831-skill-studio-enterprise-tier
---

# Pivot pricing model: free covers most users; paid gates private repos; enterprise is support

## Overview

0831 shipped a tier model where the **primary free-tier gate was a 50-skill cap**. After review, that's the wrong differentiator — most users will never hit 50 skills, and the cap reads as artificial. The user-facing positioning should be:

- **Free** — unlimited public skills, connect to public repos. Most users live here, indefinitely. No artificial caps.
- **Pro (paid)** — adds **private repository connections** (the actual feature differentiator) + priority support.
- **Enterprise** — adds SSO, audit log, dedicated support contact, custom contract.

This increment removes the skill cap from free tier and rewires the paywall to fire on **private-repo connect attempts** (the real Pro-only feature), not on the 51st skill create.

## Problem statement

1. **Free tier is too restrictive.** A 50-skill cap punishes the most engaged users — exactly the people most likely to convert later. The cap also requires server-authoritative counting on every create, adding latency.
2. **Paywall trigger fires at the wrong moment.** Hitting "51st skill" feels arbitrary; hitting "connect private repo" is a clear feature ask. The current trigger creates a poor first-paid-impression.
3. **Pricing page leads with the wrong number.** The current /pricing page emphasizes "50 skills free" — that's the cap, not the feature. Pro users buy private repos, not "the 51st skill slot".
4. **Cap creates upgrade friction at the wrong moment.** A user creating their 51st skill is *in flow* — interrupting them with a paywall is jarring. A user clicking "Connect private repo" is *intent-to-pay*.

## Goals (v1)

1. **Remove skill cap from free tier.** `/api/v1/billing/quota` returns `skillLimit: null` for free users.
2. **Rewire paywall trigger.** Fires only on `connect_private_repo` attempts, not on skill create.
3. **Reposition pricing page.** Lead with "Connect private repos" as the Pro differentiator. Skill count is no longer mentioned as a Free-tier limit.
4. **Update marketing copy** in PaywallModal, PricingCard, sidebar callouts to reflect the new positioning.
5. **Keep server-authoritative quota counting** as telemetry-only (we still want to know how engaged users are; we just don't gate on it).
6. **Update existing 0831 tests** — paywall e2e was triggered by 51st create; now it's triggered by private-repo connect.

## Out of scope (v1)

- Stripe / payment processing wiring (still deferred to a future increment)
- Soft "fair use" warnings at very high public-skill counts (e.g. 1000+) — no warning ships in v1; revisit if abuse emerges
- A/B testing different paywall copy
- Per-organization seat licensing (Enterprise tier feature, not v1 here)
- Billing portal / subscription management UI (paid users don't exist yet)

## Inherited givens

- 0831's tier infrastructure is shipped and working: `User.tier` Prisma field, `/api/v1/billing/quota` endpoint, `requireUserOrGithubBearer` middleware, `useTier()` React hook, `PaywallModal` component, `QuotaProvider` context, `keyring`-backed token storage.
- 0831's `quota_can_create_skill` Tauri IPC exists — it's NOT removed; just no longer called from the skill-create path. Keep for future telemetry.
- ADR-0831-04 (server-authoritative quota) — still valid; the value of `skillLimit` changes (null for free, was 50), but the architecture stays.

## Personas

### P-1: Hobbyist (the modal user)
Has 5-30 skills they share publicly. Will likely never pay. The product should welcome them — no cap, no nag.

### P-2: Indie / consultant (the convert path)
Has client work in private GitHub repos. Free tier doesn't help them; they need private-repo connections. Hits the paywall the first time they try to connect a private repo. Clear value exchange → likely converts.

### P-3: Enterprise admin (Support-tier upsell)
Has a team. Cares about SSO, audit log, dedicated support — not feature differences with Pro. Buys via sales conversation, not self-serve.

## User stories

---

### US-001: Remove skill cap from free tier (P0)
**Project**: vskill

**As a** free-tier user creating my Nth public skill
**I want** no artificial limit
**So that** Skill Studio doesn't punish engagement

**Acceptance Criteria**:
- [x] **AC-US1-01**: `/api/v1/billing/quota` returns `skillLimit: null` for `tier === "free"` (was `50`).
- [x] **AC-US1-02**: `useTier()` derived state interprets `skillLimit: null` as "unlimited" — no badge, no warning, no UI affordance suggesting a cap.
- [x] **AC-US1-03**: `quota_can_create_skill` Tauri IPC always returns `{allowed: true}` for free tier when `skillLimit === null` (does not consult `currentCount`). Limit-check logic is bypassed when limit is null.
- [x] **AC-US1-04**: Existing cached `quota.json` on a v1.0.14 user's disk gets updated on next 1h sync — server returns null, cache overwrites the old `50` value. No migration script needed; eventual consistency.
- [x] **AC-US1-05**: Server still increments `lastReportedSkillCount` via `/quota/report` POST (telemetry use case is preserved — we want to know engagement levels even though we don't gate on them).

---

### US-002: Rewire paywall trigger to private-repo connect (P0)
**Project**: vskill

**As a** free-tier user clicking "Connect private repo"
**I want** the paywall modal to fire there (not on skill create)
**So that** the upgrade prompt corresponds to a real feature ask

**Acceptance Criteria**:
- [x] **AC-US2-01**: The skill-create flow no longer calls `quota_can_create_skill`. The pre-create gate is removed; the create proceeds without any tier check.
- [x] **AC-US2-02**: A new pre-flight gate fires on the "Connect private repo" UI action: if `useTier().isFree`, show PaywallModal; otherwise proceed to GitHub App installation flow.
- [x] **AC-US2-03**: `PaywallModal` body copy is updated: title "Connect private repositories with Skill Studio Pro", body "Pro adds private repo connections, priority support, and unlimited skills. Free users keep all current features for public repos.", CTAs unchanged ("Upgrade to Pro" → /pricing, "Maybe later" → close).
- [x] **AC-US2-04**: `[Pro]` chip on private-repo connect button stays — it's the visible affordance that telegraphs which features are paid.
- [x] **AC-US2-05**: ConnectedRepoWidget for a public repo never shows a paywall, ever — public is fully free.
- [x] **AC-US2-06**: When tier transitions free → pro (via successful upgrade or manual tier flip), the paywall is dismissed automatically on next QuotaProvider tick.

---

### US-003: Reposition pricing page (P0)
**Project**: vskill-platform

**As a** visitor to verified-skill.com/pricing
**I want** to see clearly what each tier offers
**So that** I can identify which tier matches my needs

**Acceptance Criteria**:
- [x] **AC-US3-01**: Free card lead bullet: "Unlimited public skills". Sub-bullets: connect public repos · all CLI features · auto-update · all 53 agent platforms. CTA: "Download" → /desktop. **No mention of a 50-skill cap anywhere.**
- [x] **AC-US3-02**: Pro card lead bullet: "+ Private repository connections". Sub-bullets: priority support email · early access to new features · supports the project. Highlight strip: "MOST POPULAR — for indie devs + consultants". CTA: "Notify me" → waitlist form (Stripe wiring still out of scope).
- [x] **AC-US3-03**: Enterprise card lead bullet: "+ SSO + audit log + dedicated support". Sub-bullets: custom contract · invoice billing · seat-based licensing · private support Slack. CTA: "Contact sales" → mailto with subject pre-filled (no actual sales pipeline yet).
- [x] **AC-US3-04**: SEO meta description updated: "Skill Studio is free for public skills and public repos. Pro adds private repo connections."
- [x] **AC-US3-05**: schema.org SoftwareApplication JSON-LD `offers` updated: free tier is `price: "0"`, Pro stays `price: "0"` with note "Coming soon" until Stripe ships.

---

### US-004: Update existing 0831 tests + e2e specs (P1)
**Project**: vskill

**As a** maintainer
**I want** the test suite to match the new paywall trigger
**So that** CI continues to pass and regressions are caught

**Acceptance Criteria**:
- [x] **AC-US4-01**: `e2e/desktop/auth-and-paywall.spec.ts` test "paywall on 51st create" is deleted or rewritten — there's no longer a 51st-create paywall. Replace with "paywall on private-repo connect".
- [x] **AC-US4-02**: `e2e/desktop/auth-flow-regression.spec.ts` Test 3 "Paywall on 51st create" is rewritten to "Paywall on private-repo connect". Stub returns `{tier: "free"}` and a private repo; click Connect → paywall appears.
- [x] **AC-US4-03**: Vitest tests for `useTier()` hook updated to assert `skillLimit: null` produces `isUnlimited: true` derived state.
- [x] **AC-US4-04**: Cargo test for `quota_can_create_skill` updated to assert null-limit returns `allowed: true` regardless of count.
- [x] **AC-US4-05**: Vitest tests for `/api/v1/billing/quota` endpoint updated: free tier returns `skillLimit: null`.

---

### US-005: Update marketing copy across the codebase (P1)
**Project**: vskill

**As a** user reading any UI/copy reference to tiers
**I want** consistent positioning everywhere
**So that** I never see contradictory messaging

**Acceptance Criteria**:
- [x] **AC-US5-01**: Search the entire vskill repo for "50 skill" / "50-skill" / "skillLimit" / "free tier" / "Pro tier" copy strings; update where they reference the cap.
- [x] **AC-US5-02**: PaywallModal text — done in US-002.
- [x] **AC-US5-03**: ProChip tooltip text: was "Upgrade for unlimited skills + private repos" → "Upgrade for private repo connections".
- [x] **AC-US5-04**: README.md (vskill) tier mentions — update any copy that references the 50 cap.
- [x] **AC-US5-05**: vskill-platform marketing pages (/desktop, /skill-studio, /ai-studio) — scan for skill-cap mentions, update.

---

## Glossary

- **0831 tier infrastructure** — the User.tier Prisma column, /api/v1/billing/quota endpoint, useTier hook, PaywallModal, QuotaProvider, etc., shipped in increment 0831.
- **Private-repo connect** — the UI action where a logged-in user clicks "Connect" on a GitHub repository where `repo.isPrivate === true`. v1 free users see a `[Pro]` chip and click triggers PaywallModal; v1 Pro users get redirected to GitHub App installation flow.
- **Telemetry-only counting** — server still tracks `lastReportedSkillCount` for product analytics, but the value is never used to gate feature access.

## Open Questions

- **Q1**: Should we ship a one-time migration that bumps existing user's `lastReportedSkillCount` field type to nullable? **Resolved**: no — the field stays `Int?`; no schema change. Only the gate behavior changes.
- **Q2**: Do we surface "Pro: unlimited skills" anywhere? **Resolved**: yes, but as a soft "and" benefit, not the primary differentiator. Lead with private repos.
- **Q3**: Should the "Maybe later" CTA on the paywall snooze the modal for some duration? **Resolved**: not in v1 — clicking Connect again re-opens it; that's fine for v1.
