---
increment: 0783-vskill-platform-ui-pass
title: "vskill-platform UI/UX cross-page pass — Architecture & Plan"
created: 2026-04-27
---

# Architecture & Implementation Plan

## Stack Confirmation

- **Framework**: Next.js 15 App Router, React 19, Server Components by default
- **Runtime**: Cloudflare Workers via `@opennextjs/cloudflare`
- **Data**: Postgres (Neon) via Prisma 6; KV cache for stats (30-min TTL)
- **Styling**: Vanilla CSS + design tokens (CSS custom properties in `src/app/globals.css`). No Tailwind, no shadcn.
- **Testing**: Vitest (unit), Playwright (E2E) — `test:e2e` script.

## Files Touched

| File | Reason |
|---|---|
| `src/app/components/home/HeroStats.tsx` | Tame dot grid; switch agent count to `COUNTS.agentPlatforms`; fix scanned/verified math labels |
| `src/lib/cron/stats-refresh.ts` (read-only inspect) | Confirm what `submissionTotal` represents and whether it includes verified rows |
| `src/app/marketplace/page.tsx` | Rename header to "Plugin bundles", remove `FeaturedSpotlight` rendering, remove `featured` const |
| `src/app/trust/page.tsx` | Restyle Certified + Verified + Scanned banners for WCAG AA |
| `src/app/studio/page.tsx` | Remove "Find verified skills" callout |
| `src/app/globals.css` | Adjust `.tier-banner` (or equivalent) for AA contrast in both themes |
| `tests/e2e/0783-ui-pass.spec.ts` (new) | Playwright tests covering all ACs |

## Design Decisions

### DD-001: Hero dot grid → keep but mask harder
Rationale: the dot grid is brand identity (it appears across the product as the "atmosphere"). Removing it would be a bigger visual change than the user asked for. Instead we strengthen the radial mask so dots fully fade in the central rectangle behind the headline + subhead.

**Implementation**: change the radial-gradient stops in HeroStats.tsx from `0%→60%→100%` (opaque→0.4→0) to a tighter mask, e.g. `0%→35%→100%` (opaque→0→0). Drop SVG `opacity` from 0.55 to 0.35. Net effect: dots only show in the periphery; headline area is clean.

Alternative considered: replace SVG with a single bottom-right blurred accent. **Rejected** — would require coordinating the same change on `/marketplace`, `/trust`, `/studio` heroes.

### DD-002: Stats math fix → pick labels that match the DB
The current `getHomeStats()` returns:
- `verifiedCount`: rows in `Skill` with `certTier IN (VERIFIED, CERTIFIED)` AND `NOT isDeprecated`
- `submissionTotal`: rows in `Submission` table

`verifiedCount` is from `Skill`, `submissionTotal` is from `Submission` — they're **disjoint** populations (a verified skill is not a "submission"; submissions are pending uploads waiting for verification). So `verified > submitted` is consistent with the data — but the UI label "of N scanned" implies `verified ⊆ scanned`, which is wrong.

**Decision**: Change the UI label, not the query. Render two independent facts side-by-side instead of one with a misleading "of":
```
115,712 verified · 112.8k pending review · AI intent analysis · 3 trust tiers
```
Keeps both numbers honest. Same number of glyphs, same line.

Alternative: compute a true `scannedCount` = verified + scanned + rejected. **Rejected** — out of scope (touches stats-compute.ts data model and KV cache).

### DD-003: Agent count → use generated-counts
Replace `const TOTAL_AGENTS = FEATURED_AGENTS.length + MORE_AGENTS.length` with `COUNTS.agentPlatforms` from `src/lib/generated-counts.ts`. Single source of truth.

### DD-004: Marketplace — rename + remove featured
- Header text changes are pure copy edits in `marketplace/page.tsx`.
- Remove `<FeaturedSpotlight>` rendering. Delete the function definition and the `featured` const (per CLAUDE.md "Avoid backwards-compatibility hacks").
- The "All Plugins" `<section>` becomes the only plugin section. Header shows "Plugin bundles · {N} published · {M} skills inside" with a `<p>` subhead.

### DD-005: Marketplace card overflow
Per AC-US2-03: the existing grid `PluginCard` component already stacks `h3 (name)` above `p (tagline)` — that's already correct. The overflow problem is in `FeaturedSpotlight` where `{plugin.name} — {plugin.tagline}` is concatenated as a single h2. Since we're removing `FeaturedSpotlight` entirely (DD-004), the overflow disappears as a side effect. No additional work for AC-US2-03 once DD-004 ships.

### DD-006: Trust banners — outlined cards with accent
Replace solid filled banners with outlined cards (1px accent border + tinted background `color-mix(in srgb, accent 8%, transparent)`). Text color becomes `var(--text)` (passes AA in both themes). Accent color is preserved as the border + small icon tint.

For Certified specifically: yellow `#fbbf24` background with light text fails AA. Outlined card with yellow border + `var(--text)` body text passes AA in both themes (verified in light: ~16:1, dark: ~14:1).

### DD-007: Studio — delete the banner
The "NEW · Find verified skills" element is rendered at the top of `studio/page.tsx`. Delete the JSX. The page now starts with the "Skill Studio" h1.

## TDD Cycle Plan

### RED phase
Write `tests/e2e/0783-ui-pass.spec.ts` with these specs (all expected to fail):

```
test('AC-US1-01: hero headline contrast >= 4.5:1', ...)
test('AC-US1-02: scanned/verified math is honest', ...)
test('AC-US1-03: agent count matches generated-counts.ts', ...)
test('AC-US2-01: marketplace header reads "Plugin bundles"', ...)
test('AC-US2-02: no "Featured Collection" string on /marketplace', ...)
test('AC-US2-04: no horizontal overflow at 375/768/1280/1920', ...)
test('AC-US3-01: Certified banner contrast >= 4.5:1', ...)
test('AC-US3-02: Verified + Scanned banners contrast >= 4.5:1', ...)
test('AC-US4-01: no "Find verified skills" string on /studio', ...)
```

### GREEN phase
Implement DD-001..DD-007 in dependency order. Each test goes green as the corresponding code change lands.

### REFACTOR phase
Run `simplify` skill to look for duplication (e.g., banner styling pattern repeats 3× in trust page → extract a `<TierBanner>` if profitable; only if simpler than inline).

## Test Plan (Playwright)

For each AC:
- **AC-US1-01**: launch `/`, assert hero headline text is rendered above the SVG (z-index check) and that the SVG has reduced opacity in the centre (sample readability via computed style + visual snapshot).
- **AC-US1-02**: parse stats line text — assert it does NOT contain the misleading substring `"of {smaller-number} scanned"`. Either no "of" pattern, or `verified <= scanned`.
- **AC-US1-03**: read the rendered hero subhead, extract the agent count, assert it equals 53 (matches `COUNTS.agentPlatforms`).
- **AC-US2-01**: assert `/marketplace` contains "Plugin bundles" and "published" and "skills inside".
- **AC-US2-02**: `expect(page.locator('text=Featured Collection')).toHaveCount(0)`.
- **AC-US2-03**: assert `data-testid="featured-spotlight"` does not exist (since we delete the spotlight).
- **AC-US2-04**: at each viewport, `expect(scrollWidth).toBe(clientWidth)`.
- **AC-US3-01/02**: page.evaluate computed style on each banner; pass into a contrast helper; assert ≥ 4.5.
- **AC-US4-01**: `expect(page.locator('text=Find verified skills')).toHaveCount(0)` on `/studio`.

## Deploy Plan

1. `npm run build` (vskill-platform) — fail fast on type errors.
2. `npm run test:e2e` against local dev server — fail fast on broken specs.
3. `npm run deploy` (or `bash scripts/push-deploy.sh`) — push to Cloudflare Workers.
4. Re-run `npm run test:e2e` with `BASE_URL=https://verified-skill.com` for production smoke.
5. Capture screenshots at four viewports for each page → `reports/screenshots/`.

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Removing `FeaturedSpotlight` breaks an existing snapshot test | Medium | Run full vitest before deploy; update snapshots if found |
| Stats math fix changes a number visitors learned to recognize | Low | Values unchanged — only label changes |
| Trust banner restyle breaks visual hierarchy | Low | frontend-design skill validates side-by-side |
| Cloudflare deploy fails due to Worker bundle size | Low | Changes are presentation-only, no new deps |

## Open Questions

None — user gave full autonomy. Naming decision ("Plugin bundles") confirmed.
