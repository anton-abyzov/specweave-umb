---
increment: 0783-vskill-platform-ui-pass
title: 'vskill-platform UI/UX cross-page pass: hero, marketplace, trust, studio'
type: feature
priority: P1
status: ready_for_review
created: 2026-04-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill-platform UI/UX cross-page pass

## Overview

A cross-page UX pass on `verified-skill.com` (vskill-platform). Four pages have visible defects spotted in user review:

1. **Home hero** — full-bleed dotted-grid SVG bleeds through the headline making text hard to read; stats line shows mathematically impossible "115,712 verified of 112.8k scanned"; agent count drifts (UI shows 39, generated counts say 53).
2. **Marketplace** — "All Plugins · 8 plugins · 14 skills" header confuses visitors into thinking the platform only has 14 skills; "Featured Collection" tier is fake (just `PLUGINS[0]`); featured card heading "frontend — Figma → React + design intelligence" overflows on narrow widths because it's rendered as a single h1.
3. **Trust Center** — Certified banner is filled saturated yellow with light text → fails WCAG AA contrast (~2.5:1).
4. **Studio** — top-of-page "NEW · Find verified skills" banner is mode-confused (Studio is for authoring + benchmarking, not searching the registry; nav already exposes Skills).

All four are presentation-layer fixes. No new APIs, no new data, no auth changes. Must pass at viewports 375 / 768 / 1280 / 1920 and in both `data-theme=light` and `data-theme=dark`.

## User Stories

### US-001: Home hero is readable and the stats are honest (P1)
**Project**: vskill-platform

**As a** first-time visitor to verified-skill.com
**I want** the hero text to be clearly readable and the stats to make logical sense
**So that** I trust the platform enough to read further

**Acceptance Criteria**:
- [x] **AC-US1-01**: The dotted background SVG behind the hero headline must not visually overlap the headline glyphs — either the radial mask cuts the dots fully behind the heading area, or the dots are removed in favour of a subtle accent that does not reduce headline contrast below WCAG AA (4.5:1).
- [x] **AC-US1-02**: The stats line must satisfy `verifiedCount <= scannedCount` (verified is a subset of scanned). If the underlying values don't satisfy this, the labels must be relabeled to reflect what the numbers actually mean (e.g. "verified of N submissions" → "verified · N pending review") OR the scanned count must be sourced from a column that includes verified rows.
- [x] **AC-US1-03**: The agent-platform count rendered in the hero subhead must equal `COUNTS.agentPlatforms` from `src/lib/generated-counts.ts` — single source of truth. No more `FEATURED_AGENTS.length + MORE_AGENTS.length` drift.

---

### US-002: Marketplace clarifies what plugins are and renders cleanly (P1)
**Project**: vskill-platform

**As a** developer browsing the marketplace
**I want** to understand that "plugins" are curated bundles distinct from the 115k-skill index, and to see plugin cards that don't overflow
**So that** I can find the right install command without confusion or visual breakage

**Acceptance Criteria**:
- [x] **AC-US2-01**: The "All Plugins" header on `/marketplace` must read **"Plugin bundles"** with the count line **"{N} published · {M} skills inside"** and a one-line subhead **"Curated multi-skill installs published by vskill."**.
- [x] **AC-US2-02**: The "Featured Collection" section must be removed entirely. No DOM element on `/marketplace` may contain the literal string "Featured Collection". The `FeaturedSpotlight` component is deleted (or no longer rendered) and `const featured = PLUGINS[0]` is removed from `MarketplacePage`.
- [x] **AC-US2-03**: Plugin card heading must render `name` and `tagline` as separate elements (eyebrow + heading), not a single concatenated `name — tagline` h1/h2. The grid card already does this (h3 + p) but if a card-detail/spotlight view is retained for any plugin, it must use the same pattern.
- [x] **AC-US2-04**: At viewport widths 375, 768, 1280, 1920 px, no horizontal overflow exists on `/marketplace` (`document.documentElement.scrollWidth <= clientWidth`).

---

### US-003: Trust Center banners pass WCAG AA contrast (P1)
**Project**: vskill-platform

**As a** security-conscious visitor reading the Trust Center
**I want** all three tier banners (Scanned / Verified / Certified) legible at WCAG AA
**So that** the page itself models the trust the product is selling

**Acceptance Criteria**:
- [x] **AC-US3-01**: The "Certified" banner on `/trust` must achieve text-vs-background contrast ≥ 4.5:1 in both `data-theme=light` and `data-theme=dark`. Implementation can be either dark text on yellow fill OR an outlined card with yellow accent only — design choice owned by frontend-design skill.
- [x] **AC-US3-02**: The "Scanned" and "Verified" banners on `/trust` likewise pass contrast ≥ 4.5:1 in both themes.

---

### US-004: Studio leads with authoring, not registry search (P1)
**Project**: vskill-platform

**As a** skill author opening Studio
**I want** the page to lead with what Studio is for (write + benchmark) without telling me to go search the registry
**So that** I'm not confused about which mode I'm in

**Acceptance Criteria**:
- [x] **AC-US4-01**: The "Find verified skills" callout/banner at the top of `/studio` is removed. No DOM element on `/studio` may contain the literal string "Find verified skills" (the existing top-nav search is unaffected).
- [x] **AC-US4-02**: After removal, `/studio` lands directly on the "Skill Studio" heading + tagline + npm install command.
- [x] **AC-US4-03**: Only one ⌘K search affordance is visible on `/studio` and `/studio/*` — the studio-scoped `FindNavButton`. The root-nav `SearchTriggerButton` is path-guarded and hidden on those routes (mirroring `RootSearchPalette`'s existing path-guard). On non-studio routes (`/`, `/marketplace`, `/trust`), the root `SearchTriggerButton` continues to render.

---

### US-005: Production deploy verified end-to-end (P1)
**Project**: vskill-platform

**As a** maintainer
**I want** all four pages to be deployed to Cloudflare and re-verified live
**So that** what's tested in CI matches what users see on `https://verified-skill.com`

**Acceptance Criteria**:
- [x] **AC-US5-01**: Build (`npm run build`) succeeds with zero TypeScript errors in vskill-platform.
- [x] **AC-US5-02**: Deploy completes via `npm run deploy` (or `scripts/push-deploy.sh`).
- [x] **AC-US5-03**: Playwright re-runs against `https://verified-skill.com` confirm AC-US1-01..US4-02 pass on production at viewports 375 / 768 / 1280 / 1920. Screenshots captured into `reports/screenshots/`.

## Functional Requirements

### FR-001: Single source of truth for counts
All public-facing counts on home + marketplace must come from `src/lib/generated-counts.ts` (`COUNTS.agentPlatforms`, `COUNTS.plugins`, `COUNTS.skills`) or live DB stats — never from manually-maintained arrays that can drift.

### FR-002: Stats labels must be mathematically honest
`verified <= scanned` must hold by definition. Either fix the data source, swap labels, or split into two non-implying lines. Decision deferred to plan.md based on what the underlying columns actually represent.

### FR-003: WCAG AA across redesigned surfaces
All redesigned banners/cards must hit ≥ 4.5:1 contrast for body text and ≥ 3:1 for large text in both themes.

## Success Criteria

- 6 Playwright tests (one per AC across the four pages + production smoke) all green.
- No horizontal scroll on any page at viewports 375/768/1280/1920.
- Lighthouse a11y score ≥ 95 on `/`, `/marketplace`, `/trust`, `/studio`.
- Production verification on `https://verified-skill.com` matches CI.

## Out of Scope

- Skills index page (`/skills`) — separate concerns.
- Submit / Publishers / Queue / Docs pages — not in user feedback.
- New copy or marketing changes beyond what's needed for the corrections above.
- Backend stats refactor — only the labels/sources used by the home hero.
- Plugin model changes (e.g. real `featured` flag) — we're removing the fake tier, not replacing it.

## Dependencies

- `src/lib/generated-counts.ts` (already auto-generated by `scripts/sync-agents-json.cjs`).
- Existing `getHomeStats()` from `src/lib/cron/stats-refresh.ts`.
- Existing Playwright setup (`npm run test:e2e`).
- Cloudflare Workers deploy pipeline (`@opennextjs/cloudflare`).
