---
increment: 0783-vskill-platform-ui-pass
title: "vskill-platform UI/UX cross-page pass — Tasks"
created: 2026-04-27
test_mode: TDD
---

# Tasks

Working directory for all paths below: `repositories/anton-abyzov/vskill-platform/`

---

### T-001: RED — Write failing Playwright tests for all ACs
**User Story**: US-001..US-005 | **Satisfies ACs**: AC-US1-01..AC-US4-01 | **Status**: [x] completed
**Test Plan**:
- Given the codebase pre-fix
- When `npx playwright test tests/e2e/0783-ui-pass.spec.ts` runs
- Then all 9 specs fail with the expected assertion messages, proving the tests actually exercise the broken state.

Write `tests/e2e/0783-ui-pass.spec.ts` with the 9 specs from plan.md. Use existing Playwright config; no new fixtures.

---

### T-002: GREEN — Hero dot-grid mask + agent count + stats math
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given `/` rendered
- When the hero is inspected
- Then dots are not visible behind the headline glyphs (radial mask tightens to 35% inner stop, SVG opacity → 0.35), the agent count equals `COUNTS.agentPlatforms` (53), and the stats line reads "{verified} verified · {scanned} pending review · AI intent analysis · 3 trust tiers" (no misleading "of N scanned").

Edit `src/app/components/home/HeroStats.tsx`:
- Import `COUNTS` from `@/lib/generated-counts`.
- Replace `TOTAL_AGENTS` definition with `COUNTS.agentPlatforms`.
- Tighten radial-gradient stops to `0%→35%→100%` with stops `(1, 0, 0)`.
- Drop SVG opacity 0.55 → 0.35.
- Restructure stats `<span>`: emit `verified · pending review · AI intent · 3 trust tiers` as four equal-weight items separated by middle-dots; drop the "of {scanned} scanned" inline construction.

---

### T-003: GREEN — Marketplace header rename + remove Featured Collection
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**:
- Given `/marketplace` rendered
- When the page is inspected
- Then the header text reads "Plugin bundles · {N} published · {M} skills inside" with a one-line subhead "Curated multi-skill installs published by vskill.", no "Featured Collection" string exists in the DOM, no `[data-testid="featured-spotlight"]` element exists, and at viewports 375/768/1280/1920 `scrollWidth === clientWidth`.

Edit `src/app/marketplace/page.tsx`:
- Remove `FeaturedSpotlight` function definition (lines ~265-347).
- Remove `const featured = PLUGINS[0]` (line 439).
- Remove the `<section>` that renders `<FeaturedSpotlight plugin={featured} />` (lines ~447-452).
- In the "All Plugins grid" section header, replace `"All Plugins"` with `"Plugin bundles"` and the count line with `"{PLUGINS.length} published · {COUNTS.skills} skills inside"`. Add a `<p>` subhead below the h2: `"Curated multi-skill installs published by vskill."`.

---

### T-004: GREEN — Trust banners restyled for WCAG AA
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given `/trust` rendered in `data-theme=light` and `data-theme=dark`
- When each tier banner (Scanned, Verified, Certified) is inspected
- Then the computed contrast ratio of body text vs banner background is ≥ 4.5:1.

Find the banner JSX in `src/app/trust/page.tsx`. Convert from filled-saturation banners to outlined accent cards:
- `border: 1px solid <accent>`
- `background: color-mix(in srgb, <accent> 8%, transparent)`
- `color: var(--text)`
Apply uniformly to all three tiers. Tier-specific accent colour (yellow/green/blue) stays on the border + icon, not the body text.

---

### T-005: GREEN — Remove Studio "Find verified skills" banner + dedupe ⌘K
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test Plan**:
- Given `/studio` rendered
- When the page is inspected
- Then no element contains the literal string "Find verified skills", the first visible heading is "Skill Studio", and only one ⌘K search trigger is visible (the studio-scoped FindNavButton). On non-studio routes (`/`, `/marketplace`, `/trust`), the root-nav SearchTriggerButton continues to render.

Edit `src/app/studio/page.tsx`. Delete the top "NEW · Find verified skills · Search skills ⌘K" callout JSX. Studio opens directly with the "Skill Studio" h1 + tagline + npm install command. Then path-guard the root-nav `SearchTriggerButton` so it hides on `/studio` and `/studio/*` (mirroring `RootSearchPalette`'s existing path-guard) — keeps the studio-scoped `FindNavButton` as the only ⌘K affordance there.

---

### T-006: GREEN — Run Playwright suite locally; iterate until all 9 ACs pass
**User Story**: US-001..US-004 | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test Plan**:
- Given T-002..T-005 implemented
- When `npm run test:e2e -- tests/e2e/0783-ui-pass.spec.ts` runs against local dev server
- Then all 9 specs pass.

Start `npm run dev` in background, run Playwright suite against `http://localhost:3000`, fix any remaining failures. Iterate until green.

---

### T-007: REFACTOR — simplify pass
**User Story**: US-001..US-004 | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test Plan**:
- Given GREEN tests pass
- When `simplify` skill runs over the four touched files
- Then no duplicated banner-card pattern remains (extract a small helper if it appears 3+ times); inline-style noise reduced where a CSS class is cleaner; tests still pass.

Invoke `Skill({ skill: "simplify" })` scoped to the four files. Apply suggested changes that don't alter behaviour. Re-run Playwright.

---

### T-008: Build + deploy to Cloudflare
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**:
- Given GREEN + REFACTOR done
- When `npm run build` then `npm run deploy` runs in `repositories/anton-abyzov/vskill-platform/`
- Then build emits zero TypeScript errors and Wrangler deploy reports success.

Run from inside the vskill-platform repo: `npm run build && npm run deploy`. If the repo has `scripts/push-deploy.sh`, prefer that.

---

### T-009: Production verification with Playwright + screenshots
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**:
- Given deploy succeeded
- When Playwright runs against `https://verified-skill.com` at viewports 375/768/1280/1920 for `/`, `/marketplace`, `/trust`, `/studio`
- Then all 9 ACs pass on production AND screenshots are saved to `.specweave/increments/0783-vskill-platform-ui-pass/reports/screenshots/{viewport}/{page}.png`.

Run `BASE_URL=https://verified-skill.com npm run test:e2e -- tests/e2e/0783-ui-pass.spec.ts`. Capture screenshots from a side script using `playwright` library directly into the reports folder.

---

### T-010: Close increment via /sw:done
**User Story**: meta | **Satisfies ACs**: meta | **Status**: [x] completed
**Test Plan**:
- Given T-001..T-009 complete and committed
- When `/sw:done 0783-vskill-platform-ui-pass` runs
- Then code-review, simplify, grill, judge-llm, PM gates all pass and the increment moves to `archive/`.

Invoke the closer agent. If a gate fails, fix and re-run.
