# Tasks: Private Skills & Verification Marketing Pages

**Repo**: `repositories/anton-abyzov/vskill-platform` (branch `main`) unless noted. TDD mode: `warn` — RED before GREEN per pair.

> **Corrected scope (2026-07-01)**: no marketplace. Page is `/private-skills` ("How Private Skills Work"); `/paid-skills` = 308 redirect. Copy source: `assets/private-skills-page-draft.md`.

## Phase 1: Assets

### T-001: Capture Studio screenshots (publish drawer, PaywallModal, sidebar, My Queue)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05 | **Status**: [ ] pending
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05

**Description**: Bring up Studio locally (`vskill studio` from `repositories/anton-abyzov/vskill`; platform stack per memory `vskill-platform-local-stack` if needed). Drive with Playwright CLI at 1440×900. Capture: publish drawer with PrivacyChooser visible; PaywallModal (Free-tier org at private-skill limit — seed or lower `VSKILL_FREE_PRIVATE_SKILL_LIMIT` locally); sidebar "🔒 Private (N) / 🌐 Public (N)" grouping (org audit-log view bonus); My Queue with real verification status chips. Review captures for secrets/personal data before use.

**Test Plan**:
- **TC-001**: Given Studio running locally with seeded data → When each target state is reached and captured → Then 4+ PNGs exist, each showing the named UI element, no tokens/secrets/personal emails visible
- **TC-002**: Given raw captures → When optimized → Then each file ≤ 300 KB at ~1440px width, saved to `public/images/private-skills/` (+ copies in increment `assets/screenshots/studio/`)

**Dependencies**: None

---

### T-002: Capture CLI verified-install output
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] pending
**AC**: AC-US3-04

**Description**: Run a real `vskill install <org/skill>` for a verified skill; capture the Verified ✓ output. Deliver as optimized screenshot OR preserved exact text for a styled terminal block (decide by visual fit with site style).

**Test Plan**:
- **TC-001**: Given a verified skill in the registry → When `vskill install` runs → Then output shows the verified indicator; capture stored with the exact command visible (no tokens)

**Dependencies**: None

## Phase 2: Pages (RED → GREEN per page)

### T-003: [RED] /private-skills page tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01..AC-US1-12 (test-first) | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10

**Description**: Write failing vitest suite `src/app/private-skills/__tests__/page.test.tsx` following the pricing-page pattern (`renderToString` of the async page, mock `getServerAuth` if imported).

**Test Plan**:
- **TC-001**: Given the page module → When rendered → Then HTML contains the H1 "Your team's skills. Stored, secured, scanned."
- **TC-002**: **No-marketplace guard**: Given rendered HTML (lowercased) → Then it does NOT contain: "revenue share", "platform fee", "payout", "paid pack", "sell your skills", "selling skills"
- **TC-003**: Given rendered HTML → Then problem strip present (Slack/gists/git wording + Snyk stat); 4-step section present with 4 `<img>` tags with non-empty alt
- **TC-004**: Given rendered HTML → Then comparison table has the 5 corrected rows; scan-coverage strip links `/verification`; pricing recap links `/pricing` and says "private skill storage" for Pro
- **TC-005**: Given rendered HTML → Then 6 `<details>` FAQ items; SOC 2 answer contains "reduce" wording and does NOT contain "guarantees safe"
- **TC-006**: Given the module → Then `metadata.alternates.canonical === 'https://verified-skill.com/private-skills'` and OG image present
- **TC-007**: Given rendered HTML → Then design-partner CTAs href the shared contact constant; CTA copy mentions white-glove migration + flat founder pricing, with no fee/revenue claims

**Dependencies**: None (screenshots not needed for RED)

---

### T-004: [GREEN] Implement /private-skills page + /paid-skills redirect
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10, AC-US1-11, AC-US1-12 | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10, AC-US1-11, AC-US1-12

**Description**: Build `src/app/private-skills/page.tsx` per plan.md section architecture, copy faithful to `assets/private-skills-page-draft.md` (corrected), screenshots from T-001/T-002 with descriptive alt text, `src/lib/contact.ts` constants (also created here), OG image in `public/og/`, JSON-LD. Add permanent redirect `/paid-skills` → `/private-skills` in `next.config.ts`. Visual check in dev server, light + dark.

**Test Plan**:
- **TC-001**: Given T-003 suite → When `npx vitest run src/app/private-skills` → Then all pass
- **TC-002**: Given `npm run dev` → When visiting /private-skills in light and dark themes → Then sections match site style (960px, JetBrains Mono H1, orange badges), images load
- **TC-003**: Given dev server → When requesting /paid-skills → Then 308 redirect to /private-skills

**Dependencies**: T-001, T-002, T-003

---

### T-005: [RED] /verification page tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..AC-US2-07 (test-first) | **Status**: [ ] pending
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07

**Description**: Failing vitest suite `src/app/verification/__tests__/page.test.tsx`.

**Test Plan**:
- **TC-001**: Given rendered HTML → Then all 5 pipeline stages named; "52" patterns and 9 category names present
- **TC-002**: Given rendered HTML → Then injection-probe section present (mentions prompt-injection patterns + probe fixtures + BLOCKED verdict)
- **TC-003**: Given rendered HTML → Then transcript-fields section lists contentHash/commit SHA/severity counts/score; re-verification section mentions twice-daily and per-version rescan
- **TC-004**: Given rendered HTML → Then sample report present (`data-testid="sample-report"`), labeled as sample, contains `invariant.` check ids and a PASS verdict, includes collapsible raw JSON
- **TC-005**: Given rendered HTML → Then honest-language holds: contains "reduce", does NOT match /guarantee[sd]?\s+(safe|security)/i
- **TC-006**: Given the module → Then canonical `https://verified-skill.com/verification`, OG + twitter present

**Dependencies**: None

---

### T-006: [GREEN] Implement /verification page with sample report
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07

**Description**: Build `src/app/verification/page.tsx` + `src/app/verification/sample-report.ts`. **Before hardcoding numbers**: re-count patterns in `crawl-worker/lib/scanner-patterns.js` and resolve the agent-count discrepancy (draft: 53; README badge: 54). Sample report mirrors `vskill/test/verify/reports/verify-result.json` shape + Tier 1/2 summary from `ScanResult` fields; realistic values; "Sample report" label. Include "what verification does NOT prove" section.

**Test Plan**:
- **TC-001**: Given T-005 suite → When `npx vitest run src/app/verification` → Then all pass
- **TC-002**: Given dev server → When visiting /verification → Then sample report reads as a styled artifact (not JSON dump); raw JSON in `<details>` matches the rendered values

**Dependencies**: T-005

## Phase 3: Pricing, contact path, chrome links

### T-007: [RED] Pricing CTA + links tests
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01..AC-US4-04, AC-US5-01..AC-US5-03 (test-first) | **Status**: [ ] pending
**AC**: AC-US4-01, AC-US4-02, AC-US4-04, AC-US5-01, AC-US5-02, AC-US5-03

**Description**: Update `src/app/pricing/__tests__/page.test.tsx` (currently asserts the mailto — flip the assertion) and extend `src/app/__tests__/layout.nav.test.tsx` string-grep for footer links; add docs-hub link assertions.

**Test Plan**:
- **TC-001**: Given pricing page HTML → Then it does NOT contain "mailto:anton.abyzov@gmail.com"; Enterprise CTA (`data-testid="enterprise-contact-cta"`) hrefs `#enterprise-contact` path; form section has `id="enterprise-contact"` with enterprise tier preselected
- **TC-002**: Given pricing page HTML → Then hero contains a link to `/private-skills`
- **TC-003**: Given layout.tsx source → Then footer contains `href="/private-skills"` and `href="/verification"`
- **TC-004**: Given docs page HTML/source → Then DocCards link `/private-skills` and `/verification`

**Dependencies**: None

---

### T-008: [GREEN] Pricing CTA rework, hero link, docs + footer links
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [ ] pending
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US5-01, AC-US5-02, AC-US5-03

**Description**: Remove `ENTERPRISE_MAILTO`; wire `src/lib/contact.ts` into pricing Enterprise CTA; anchor + retitle waitlist form section (`id="enterprise-contact"`, tier=enterprise preselect, "Talk to sales" framing); pricing hero link to /private-skills; DocCards in docs hub; footer links in layout.tsx.

**Test Plan**:
- **TC-001**: Given T-007 suites → When `npx vitest run` → Then all pass, no other suites broken
- **TC-002**: Given dev server → When clicking Enterprise "Talk to sales" → Then page scrolls to the contact form with Enterprise preselected; submitting a test email returns success

**Dependencies**: T-007

## Phase 4: Refactor, E2E

### T-009: [REFACTOR] Shared marketing-section styles + duplication pass
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-11, AC-US2-08 | **Status**: [ ] pending
**AC**: AC-US1-11, AC-US2-08

**Description**: If /private-skills and /verification duplicate section/badge/table style objects, extract a small shared module (e.g. `src/lib/marketing-styles.ts`) — only if it reduces net code; keep tests green.

**Test Plan**:
- **TC-001**: Given refactor → When `npx vitest run` → Then all green; rendered HTML unchanged for key testids

**Dependencies**: T-004, T-006, T-008

---

### T-010: E2E smoke spec for new pages + pricing CTA
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US6-01 | **Status**: [ ] pending
**AC**: AC-US6-01

**Description**: `e2e/0877-marketing-pages.spec.ts` (Playwright): /private-skills and /verification return 200 with H1s; /paid-skills redirects; FAQ `<details>` toggles; scan-strip link navigates to /verification; pricing Enterprise CTA anchors to the contact form; no personal-Gmail mailto in pricing DOM; no marketplace language on /private-skills.

**Test Plan**:
- **TC-001**: Given `npx playwright test e2e/0877-marketing-pages.spec.ts` → Then all scenarios pass against local dev server

**Dependencies**: T-004, T-006, T-008

## Phase 5: Deploy

### T-011: Full test run, deploy via wrangler chain, live verification
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [ ] pending
**AC**: AC-US6-01, AC-US6-02, AC-US6-03

**Description**: In vskill-platform: `npx vitest run` + `npx playwright test` (green) → `rm -rf .next .open-next .turbo node_modules/.cache` → `npm run build:worker` → `npx wrangler deploy`. Postdeploy queue-health 401 is benign. Then curl live URLs.

**Test Plan**:
- **TC-001**: Given deploy completes with a `Current Version ID` → When `curl -s https://verified-skill.com/private-skills | grep "Stored, secured, scanned"` and `curl -s https://verified-skill.com/verification | grep -i "verified"` → Then both 200 with expected content
- **TC-002**: Given `curl -sI https://verified-skill.com/paid-skills` → Then 308 (or 301) with Location `/private-skills`
- **TC-003**: Given live pricing page → When grepped → Then no `mailto:anton.abyzov@gmail.com`; Enterprise CTA present; hero links /private-skills
- **TC-004**: Given vskill-platform repo → When `git status` → Then work committed and pushed to `main` (platform repo), umbrella increment files committed separately

**Dependencies**: T-009, T-010
