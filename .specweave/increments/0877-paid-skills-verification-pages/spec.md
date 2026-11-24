---
increment: 0877-paid-skills-verification-pages
title: "Private Skills & Verification Marketing Pages"
type: feature
priority: P1
status: planned
created: 2026-07-02
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Private Skills & Verification Marketing Pages

> **⚠️ CORRECTED SCOPE (2026-07-01, from Anton via GTM session)**: There is **NO paid-skills marketplace**. Nobody sells skills through the platform — no revenue share, no platform fees, no per-seat licensing of skill packs to third parties. The paid model is exclusively: **teams pay to STORE their private skills in vskill infrastructure, where we SECURE them (isolated org tenants, default-deny from the public registry, audit log) and SCAN them (52 patterns → blocklist → LLM intent, on every version)**. Any earlier "Path B: selling skills / paid packs / founding-partner 0% fee" framing is dead — it must not appear anywhere on the site.

## Overview

Add two GTM-critical pages to vskill-platform (verified-skill.com):

1. **`/private-skills`** — "How Private Skills Work" (originally planned as `/paid-skills`; that route becomes a permanent redirect). Full corrected copy lives at [`assets/private-skills-page-draft.md`](assets/private-skills-page-draft.md) — the copy source of truth. Hero: "Your team's skills. Stored, secured, scanned."
2. **`/verification`** — the methodology trust page explaining what "verified" actually means, with one full sample verification report. **This is the load-bearing trust asset every cold-outreach email links to.**

Plus: replace the `mailto:anton.abyzov@gmail.com` Enterprise pricing CTA with a proper contact path, link `/private-skills` from the pricing hero and the Docs section, capture the five missing Studio screenshots, and deploy via the platform wrangler chain.

**Business context**: The GTM motion (founding-design-partner outreach: white-glove migration + flat founder pricing for year one) needs a public page explaining the private-skill hosting product, and a verification methodology page that makes the "verified/scanned" claim credible. Everything described is SHIPPED functionality (0874 tiers/paywall, 0826 private skills).

## User Stories

### US-001: /private-skills page — "How Private Skills Work" (P1)
**Project**: vskill-platform

**As a** engineering lead whose team shares CLAUDE.md files and skills over Slack/gists/git
**I want** a single page explaining how private skill hosting works, with real product screenshots
**So that** I can judge whether verified-skill.com beats our unscanned, unversioned skill sharing without booking a call first

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `GET /private-skills` renders a server component at `src/app/private-skills/page.tsx` with the corrected hero: H1 "Your team's skills. Stored, secured, scanned.", the private-hosting sub-line, and a CTA row (design-partner CTA + "See pricing" → `/pricing`).
- [ ] **AC-US1-02**: **No-marketplace guard (testable, blocking)**: the page contains NO selling/marketplace language — none of: "sell", "revenue share", "platform fee", "payout", "paid packs", "per-seat licensed" (as seller claims). The paid framing is exclusively storage + security + scanning.
- [ ] **AC-US1-03**: Problem strip renders per draft ("Your engineers already share CLAUDE.md files, Cursor rules, and skills — over Slack, gists, and git repos. Nobody scans them…"), including the Snyk prompt-injection stat as worded in the approved copy.
- [ ] **AC-US1-04**: 4-step how-it-works renders with a real screenshot per step: (1) Create & test in Skill Studio; (2) Publish privately — 🔒 Private in publish drawer, every version passes the 3-tier scan (52 patterns → malware blocklist → LLM intent); (3) We store and secure it — isolated org tenant, default-deny from public registry, member roster, exportable audit log (1-year retention); (4) One-command install — `vskill install org/skill`, auto-updates on newly scanned versions, across the supported agents. No AI-generated or mocked UI shots.
- [ ] **AC-US1-05**: "Why not just a git repo?" comparison table renders the 5 corrected rows (security scan per version, storage, versioning, visibility, reach) comparing "Git-repo skill sharing" vs "verified-skill.com private hosting".
- [ ] **AC-US1-06**: "What the scan covers" trust strip renders (52 static security patterns · known-malware blocklist · LLM intent analysis · re-scanned on every new version) and links to `/verification`.
- [ ] **AC-US1-07**: Pricing recap shows the 4 tiers with the corrected one-liners (Free — unlimited public skills · Pro $20/mo — private skill storage from private GitHub repos · Team $30/seat/mo min 3 — org-wide shared tenant, member roster, audit log · Enterprise — SSO, dedicated support, custom contract) and links `/pricing`.
- [ ] **AC-US1-08**: FAQ renders the 6 corrected questions as native `<details>`/`<summary>` accordions (storage location, who can see skills, scan failure, self-host, supported agents, SSO/SOC 2). SOC 2 answer uses honest wording ("reduces risk", "evidence collection in progress") — never "guarantees safe".
- [ ] **AC-US1-09**: Final design-partner CTA block: white-glove migration of existing skill repo, flat founder pricing for year one, direct line to the founder — pointing at the shared contact path (see US-004). No marketplace promises, no revenue/fee claims.
- [ ] **AC-US1-10**: Page exports `metadata` matching site convention (title, description, canonical `https://verified-skill.com/private-skills`, openGraph 1200×630 image, twitter card) plus JSON-LD, following `/pricing` and `/desktop` patterns.
- [ ] **AC-US1-11**: Styling matches existing site system: inline styles with CSS custom properties (`var(--border)`, `var(--surface-card)`, `var(--text)`, `var(--text-muted)`), JetBrains Mono display H1 (~3rem), 960px max-width containers, brand orange `#F25F1C` accents/badges, section padding `3rem 2rem`. Light and dark themes. No Tailwind, no CSS modules.
- [ ] **AC-US1-12**: `/paid-skills` permanently redirects (308) to `/private-skills` (next.config redirect), so any already-circulated outreach links keep working.

---

### US-002: /verification methodology page (P1)
**Project**: vskill-platform

**As a** security-conscious buyer who received a cold email claiming "verified skills"
**I want** a methodology page that shows exactly what verification does, including a real report
**So that** I can trust (or audit) the claim before letting the registry near my org's agents

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `GET /verification` renders a server component at `src/app/verification/page.tsx` explaining the pipeline stages **accurately, matching the shipped implementation**: (1) Tier 1 static security scan — 52 regex patterns across 9 threat categories (command-injection, data-exfiltration, privilege-escalation, credential-theft, prompt-injection, filesystem-access, network-access, code-execution, DCI-abuse) with PASS/CONCERNS/FAIL verdicts; (2) Tier 2 LLM intent analysis — intent vs declared purpose, scope alignment, concerns, 0–100 score; (3) blocklist gate against known-malicious content hashes; (4) runtime execution — the skill artifact is exercised in a real agent runtime with invariant checks; (5) per-version certification — every published semver version gets its own scan results.
- [ ] **AC-US2-02**: A dedicated "Prompt-injection probes" section explains injection probing concretely (prompt-injection pattern family in Tier 1 + probe fixtures in the runtime harness that attempt to make the skill exfiltrate/execute, with BLOCKED as a first-class verdict).
- [ ] **AC-US2-03**: A "Per-version behavior transcript" section lists what a transcript records — fields grounded in the real data model: verdict, tier, score, patterns checked, finding counts by severity, scanner version, LLM model, content hash (SHA-256, tamper-evident), commit SHA, duration; runtime units → fixtures → invariant checks structure.
- [ ] **AC-US2-04**: A "Re-verification" section states the real triggers: every new published version is fully re-scanned; regression verification runs on a twice-daily schedule (CI lane with deterministic stub provider + real-model lane); all-SKIP runs fail loudly (a run must produce at least one PASS — never silent green); `RESCAN_REQUIRED` forces re-verification of already-published skills.
- [ ] **AC-US2-05**: One **full sample verification report** is rendered on the page (styled, readable — not a raw JSON dump, though a collapsible raw JSON view is acceptable as a secondary element). Structure and field names mirror the real report format (`verdict`, `units[]`, `fixtures[]`, `checks[]` with `invariant.*` ids, `surface`, `durationMs`, plus Tier 1/Tier 2 scan summary: patterns checked, findings by severity, score, content hash, commit SHA). Values are realistic and clearly labeled as a sample report.
- [ ] **AC-US2-06**: All copy uses honest risk language: "reduces risk", "verified against N patterns", "no verification makes a skill guaranteed safe". The words "guarantees safe" (or equivalents) never appear as a claim. Numbers on the page (52 patterns, 9 categories, supported-agent count, twice-daily) match implementation facts — re-verified against source at implementation time (draft says 53 agents, vskill README badge says 54 known: confirm the number before hardcoding).
- [ ] **AC-US2-07**: Page exports `metadata` (title, description, canonical `https://verified-skill.com/verification`, OG image, twitter card) + JSON-LD, same conventions as US-001.
- [ ] **AC-US2-08**: `/verification` is reachable from: the `/private-skills` scan-coverage strip (AC-US1-06), the Docs hub Security section, and the footer. Styling matches site system (same constraints as AC-US1-11).

---

### US-003: Studio & CLI screenshots (P1)
**Project**: vskill-platform

**As a** visitor skimming /private-skills
**I want** real product screenshots, not illustrations
**So that** I can see the product actually exists and works as described

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Publish drawer with PrivacyChooser (PUBLIC/PRIVATE choice visible) captured from the locally running Studio app.
- [ ] **AC-US3-02**: PaywallModal captured (the private-skill paywall from 0874 tiered paywall).
- [ ] **AC-US3-03**: Sidebar private/public grouping captured ("🔒 Private (N) / 🌐 Public (N)"); org audit-log view is a bonus capture for step 3 if reachable.
- [ ] **AC-US3-04**: CLI verified-install output captured from a real `vskill install` run showing the Verified ✓ output (rendered on-page either as an optimized screenshot or as a styled terminal block containing the real captured text — real output either way).
- [ ] **AC-US3-05**: My Queue verification statuses captured (queue list showing real status chips, e.g. scanning/published/rejected states).
- [ ] **AC-US3-06**: All raster assets are optimized (≤ 300 KB each, appropriate width ~1440px or 2x DPR crop), stored under `public/images/private-skills/` (and `public/images/verification/` where used there), referenced with descriptive alt text. The four existing live-site captures preserved at [`assets/screenshots/`](assets/screenshots/) (home, pricing, desktop, docs-studio) are available for reuse. No fabricated UI.

---

### US-004: Enterprise CTA contact path + pricing hero link (P1)
**Project**: vskill-platform

**As a** enterprise prospect on the pricing page
**I want** a professional contact path instead of a personal Gmail mailto
**So that** contacting sales feels trustworthy and the lead is captured rather than lost in an inbox

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `mailto:anton.abyzov@gmail.com` no longer appears anywhere in `src/app/pricing/page.tsx` (currently the `ENTERPRISE_MAILTO` const at ~line 65). The existing pricing unit test asserting the mailto is updated to assert the new path.
- [ ] **AC-US4-02**: The Enterprise card CTA ("Talk to sales") points to a proper contact path: the on-page enterprise contact form (anchor `#enterprise-contact` on the existing waitlist form section, with `tier=enterprise` preselected, posting to the existing `/api/v1/billing/waitlist` endpoint). The form section heading/copy is adjusted so it reads as "Talk to sales / Contact" rather than only "waitlist". `data-testid` updated accordingly (e.g. `enterprise-contact-cta`).
- [ ] **AC-US4-03**: The contact path is defined once as a shared constant (e.g. `src/lib/contact.ts` exporting `ENTERPRISE_CONTACT_PATH` and `DESIGN_PARTNER_CONTACT_PATH`) and consumed by both the pricing page and `/private-skills` CTAs, so a future calendar/booking link is a one-line swap. If a calendar URL is provided before implementation completes, use it for `DESIGN_PARTNER_CONTACT_PATH`; otherwise both point at the enterprise contact form.
- [ ] **AC-US4-04**: Pricing page hero links to `/private-skills` (visible link/badge, e.g. "New: how private skills work →"), styled with existing hero conventions.

---

### US-005: Navigation & docs discoverability (P2)
**Project**: vskill-platform

**As a** docs reader or nav user
**I want** /private-skills and /verification discoverable from the site chrome
**So that** the pages get organic traffic, not just outreach clicks

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Docs hub (`src/app/docs/page.tsx`) gets a DocCard linking to `/private-skills` ("Private Skills") in an appropriate section, following the existing `DocCard` pattern.
- [ ] **AC-US5-02**: Docs hub Security section gets a DocCard linking to `/verification` ("Verification methodology").
- [ ] **AC-US5-03**: Footer (in `src/app/layout.tsx`) gains links to `/private-skills` and `/verification`, matching existing `footerLink` style. The existing string-grep nav test pattern (`layout.nav.test.tsx`) is extended to cover them.

---

### US-006: Deploy to production (P1)
**Project**: vskill-platform

**As a** founder running outreach
**I want** the pages live on verified-skill.com
**So that** cold emails can link to /verification and /private-skills today

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Full test suite green before deploy: `npx vitest run` and the relevant Playwright specs pass in `repositories/anton-abyzov/vskill-platform`.
- [ ] **AC-US6-02**: Deploy follows the platform wrangler chain: clean stale caches (`rm -rf .next .open-next .turbo node_modules/.cache`) → `npm run build:worker` → `npx wrangler deploy` (worker `verified-skill-com`). The postdeploy `queue-health` 401 is a known-benign local artifact and does not fail the increment.
- [ ] **AC-US6-03**: Live verification: `https://verified-skill.com/private-skills` and `https://verified-skill.com/verification` return HTTP 200 with expected content (curl checks for H1 strings); `https://verified-skill.com/paid-skills` redirects to `/private-skills`; pricing page live-checked for the new Enterprise CTA and absence of the personal Gmail mailto.

## Functional Requirements

### FR-001: Copy fidelity
`assets/private-skills-page-draft.md` (CORRECTED 2026-07-01) is the approved copy source for /private-skills. Deviations allowed only for: HTML structure, minor grammar, and resolving placeholders (calendar link → shared contact constant). Claims must stay honest to shipped reality — the paid model is storage + security + scanning only.

### FR-002: Fact fidelity for /verification
Every technical claim on /verification must trace to the implementation (see plan.md Fact Sources table). If a number can drift (52 patterns, 53-vs-54 agents), verify against source at implementation time before hardcoding.

### FR-003: Server-rendered, JS-light
Both pages are async server components; interactive elements limited to native HTML (`<details>`, anchors). No new client components unless unavoidable.

## Success Criteria

- Both pages live and linked; outreach emails can link `/verification` and `/private-skills` immediately.
- Zero marketplace/selling claims anywhere on the site from this increment; zero personal-Gmail mailtos on the pricing page.
- All unit + E2E tests green; existing tests updated, none deleted to pass.
- Screenshots are real product captures.

## Out of Scope

- **Any paid-skills marketplace content** — the feature does not exist; nothing on the site may state or imply skill selling, revenue share, platform fees, or payouts.
- The 60–90s explainer video (storyboard in the draft — separate increment).
- Press page mailto replacement (`/press` also uses the personal Gmail — flag as follow-up, don't block).
- New backend contact endpoint (reuse `/api/v1/billing/waitlist`).
- A public per-skill transcript browser (sample report is static content).

## Dependencies

- 0874 tiered-private-skills-paywall (PaywallModal, tiers — shipped, needed for screenshots).
- 0853/0857/0858 (runtime verify, stub harness, regression scheduling — facts source for /verification).
- Local Studio app run (`vskill studio` from `repositories/anton-abyzov/vskill`) + local platform stack for screenshot capture (see memory: vskill-platform-local-stack).
- Sample report source: `repositories/anton-abyzov/vskill/test/verify/reports/verify-result.json`.

## Closure triage (November 24, 2026)

Class d, stale. Nothing happened since July 2, 2026: no `/private-skills`, `/paid-skills` or `/verification` route on vskill-platform main and no PR for it (checked with `git ls-tree` and `gh pr list`). Proposed: abandon or re-plan; owner's call.
