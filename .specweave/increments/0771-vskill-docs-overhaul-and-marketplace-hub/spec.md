---
increment: 0771-vskill-docs-overhaul-and-marketplace-hub
title: >-
  vskill docs MDX migration, /marketplace hub, frontend polish, build-time count
  generator
type: feature
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
project: vskill-platform
projects:
  - vskill-platform
  - vskill
---

# Feature: vskill docs MDX migration, /marketplace hub, frontend polish, build-time count generator

## Context

Yesterday's audit shipped uncontroversial fixes to verified-skill.com (`npx vskill@latest` everywhere, count-string cleanup, SpecWeave version refresh). The **architectural** wins remained on the table: docs-as-content (MDX), a real marketplace surface, polish that earns the trust signal we sell, and a build-time generator that closes the count-drift class permanently.

This increment bundles six tracks into a single coherent ship so verified-skill.com gets a cohesive "v1" face — not a half-MDX site with stale counts and an orphan plugin page.

**Anchoring research (this session)**:
- Doc-structure brainstorm concluded: do **not** migrate to Docusaurus — a hybrid (Next.js + MDX for reference pages) preserves the trust-signal identity while removing inline-JSX bloat.
- `/docs/plugins` and `/insights` are missing from the sitemap (SEO-dead). A new `/marketplace` becomes the curated face; `/skills` (5K entries) stays as the universal catalog.
- `CodeBlock` ships zero syntax highlighting today — for a developer-tools brand, this is the biggest single visual miss.
- `vskill@0.5.138` drifted +9 patches from yesterday's `0.5.129` — proof that count strings will keep going stale until a build-time generator replaces manual sed.

**Confirmed numbers (as of this spec)**: vskill v0.5.138, 53 agents, 8 plugins, 14 skills, 52 scan patterns, SpecWeave v1.0.581.

**Repos touched**:
- `repositories/anton-abyzov/vskill-platform/` — Tracks A/B/C/D/E + the count-consumer half of F
- `repositories/anton-abyzov/vskill/` — README badge sync portion of F

---

## User Stories

### US-001: MDX migration for heavy reference pages
**Project**: vskill-platform

**As a** docs maintainer
**I want** the two heaviest reference pages converted from inline JSX to MDX
**So that** content updates don't require touching React components and the docs surface gets a real search index.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `src/app/docs/security-guidelines/page.tsx` (723 LOC) is replaced by `src/app/docs/security-guidelines/page.mdx`; rendered output is visually equivalent to the JSX version (Playwright pixel-diff < 5% tolerance).
- [x] **AC-US1-02**: `src/app/docs/cli-reference/page.tsx` (372 LOC) is replaced by `src/app/docs/cli-reference/page.mdx`; rendered output is visually equivalent (Playwright pixel-diff < 5% tolerance).
- [x] **AC-US1-03**: `mdx-components.tsx` at the app root wires `CodeBlock`, `Callout`, `FlagTable`, `SectionHeading`, `Prose`, `InlineCode`, and `TabGroup` so MDX files use the existing component vocabulary without rewrites.
- [x] **AC-US1-04**: Pagefind index is generated post-build and served as a static asset; a `⌘K` palette in `DocsLayout.tsx` returns at least one hit each for the queries `scan`, `tier`, and `install`.

---

### US-002: `/marketplace` top-level hub
**Project**: vskill-platform

**As a** developer evaluating verified-skill.com
**I want** a single curated showcase that surfaces all 8 plugins, recent insights, and learn videos
**So that** I can discover what's available without bouncing between an orphan `/docs/plugins` page and a sitemap-invisible `/insights`.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/app/marketplace/page.tsx` renders all 8 plugins as rich `DocCard`-based entries showing tier badge, supported-agent icons (reusing `AGENT_ICONS`), tagline, last-updated, and a copy-button install command sourced from typed `PluginEntry[]` in `src/lib/marketplace/plugins.ts`.
- [x] **AC-US2-02**: A "What's New" feed (sourced from `src/lib/marketplace/feed.ts`) interleaves entries of `kind: 'article' | 'video' | 'release'` with kind-tagged badges, in reverse-chronological order.
- [x] **AC-US2-03**: Top nav (`src/app/layout.tsx`) and `MobileNav.tsx` show "Marketplace" in place of "Insights"; `/insights` URL still resolves and is reachable from the marketplace feed and the footer Resources column.
- [x] **AC-US2-04**: `next.config.ts` adds a permanent (301) redirect from `/docs/plugins` to `/marketplace`; `src/app/sitemap.ts` includes `/marketplace` (priority 0.85), `/insights` (0.6), `/learn` (0.6), and `/docs` (0.7).

---

### US-003: Sidebar and TOC navigation UX
**Project**: vskill-platform

**As a** docs reader
**I want** the sidebar and table of contents to clearly show where I am
**So that** I can scan a long page and orient myself without re-reading headings.

**Acceptance Criteria**:
- [x] **AC-US3-01**: The active sidebar link in `DocsLayout.tsx` shows a 2px `--code-green` left bar plus `--bg-hover` background; a Playwright snapshot of the active vs inactive states proves the marker is visually distinct.
- [x] **AC-US3-02**: TOC scroll-spy uses `IntersectionObserver` (no scroll event listeners) to mark the heading nearest the viewport top; a 2px green left bar animates between TOC items via `transform: translateY()`.
- [x] **AC-US3-03**: TOC items carry a `level: 1 | 2 | 3` field (h2/h3/h4) and indent by `level × 0.75rem`, so nested headings visually group under their parent.

---

### US-004: Shiki SSR syntax highlighting + hero typography
**Project**: vskill-platform

**As a** developer skimming code samples
**I want** real syntax-highlighted code blocks and a homepage hero that signals "product, not internal tool"
**So that** verified-skill.com reads as a polished developer brand on first impression.

**Acceptance Criteria**:
- [x] **AC-US4-01**: `CodeBlock.tsx` renders Shiki SSR-highlighted output using `github-dark` and `github-light` themes selected via CSS variable; the existing copy button and line-number behaviour are preserved; line-hover shows a subtle `rgba(255,255,255,0.03)` background; line numbers sit at opacity 0.4.
- [x] **AC-US4-02**: The Shiki bundle uses `shiki/bundle/web` with only the two themes registered; Lighthouse Performance score on `/` does not regress more than 5 points vs the pre-change baseline.
- [x] **AC-US4-03**: The homepage hero `h1` uses a display font (Departure Mono or JetBrains Mono Display) loaded via `next/font/google` with `display: 'swap'` and only the h1 weight preloaded; size jumps from `2.25rem` to `3.25rem` with `text-wrap: balance`; a dotted/grid SVG background with radial fade sits behind the hero.

---

### US-005: Tier-aware visual system
**Project**: vskill-platform

**As a** visitor learning the Scanned → Verified → Certified ladder
**I want** the visual weight of each tier to match its meaning
**So that** the brand promise is reinforced everywhere the ladder appears, not just in copy.

**Acceptance Criteria**:
- [x] **AC-US5-01**: The three-tier cards on `src/app/docs/getting-started/page.tsx` (lines 158-176) use `--tier-verified-bg` / `--tier-certified-bg` tints with ascending visual weight: Scanned = flat outline, Verified = filled tint with green inner glow, Certified = gold border-gradient with subtle parallax on hover.
- [x] **AC-US5-02**: `TrustBadge.tsx` and `src/app/trust/page.tsx` echo the same tier visual language so the ladder reads consistently across docs, marketing, and badge embeds.
- [x] **AC-US5-03**: `TabGroup.tsx` replaces per-button `border-bottom` with a single `position: absolute` underline that translates between tabs via `transform`; `DocCard.tsx` gains a layered shadow (`0 1px 0 inset rgba(255,255,255,0.05), 0 4px 16px -8px rgba(0,0,0,0.5)`) and a `featured` prop with a `background-clip: padding-box` gradient border.
- [x] **AC-US5-04**: `Callout.tsx` Unicode glyphs (ℹ ⚠ ✕) are replaced with inline SVG matching the docs SVG icon family; light theme tokens move to `--border: #E0E0E0` and `--bg-subtle: #F5F5F5`, and card-style components gain `box-shadow: inset 0 1px 0 rgba(255,255,255,0.6)` so they no longer disappear into the background.

---

### US-006: Build-time count generator across vskill and vskill-platform
**Project**: vskill-platform

**As a** release engineer
**I want** plugin/skill/agent/version counts regenerated at build and publish time, with a guard that fails publish on stale numbers
**So that** README badges and OG metadata can never drift again — eliminating the failure mode that produced this very increment.

**Acceptance Criteria**:
- [x] **AC-US6-01**: `vskill-platform/scripts/sync-agents-json.cjs` (already wired to `prebuild`) is extended to also write `src/lib/generated-counts.ts` exporting a typed `COUNTS` object with `agentPlatforms`, `plugins`, `skills`, `scanPatterns`, `vskillVersion`, and `specWeaveVersion` fields sourced from the filesystem and `npm view`.
- [x] **AC-US6-02**: Hardcoded count strings in `src/app/layout.tsx` (3 OG/Twitter strings), `src/app/components/homepage/FeatureAgentEcosystem.tsx`, `src/app/docs/page.tsx`, `src/app/docs/cli-reference/page.tsx`, and `src/app/docs/getting-started/page.tsx` are replaced with imports from `generated-counts.ts`.
- [x] **AC-US6-03**: `vskill/scripts/sync-readme-badges.cjs` is added (~30 LOC) that globs `plugins/*/`, `**/SKILL.md`, reads `agents.json` and `src/scanner/patterns.ts`, then sed-replaces shields.io badge URLs in `README.md`. **Project**: vskill
- [x] **AC-US6-04**: `vskill/package.json` `prepublishOnly` chain becomes `npm run build && npm run build:eval-ui && node scripts/sync-readme-badges.cjs && git diff --exit-code README.md` so a publish fails if anyone forgot to commit regenerated badges. **Project**: vskill

---

## Cross-Cutting Non-Functional Requirements

### Performance
- Shiki bundle uses `shiki/bundle/web` with two themes only; tree-shaken to keep first-load JS within 5pt Lighthouse tolerance.
- MDX is server-rendered by Next 15 — no client-side hydration cost beyond current JSX pages.
- Pagefind runs as a static WASM index served as an asset; query latency target ≤ 100ms for the existing page count.
- Hero font loaded via `next/font` with `display: 'swap'` and h1-weight preload to control CLS (target CLS < 0.05 on `/`).
- TOC scroll-spy uses `IntersectionObserver` exclusively — no scroll event listeners.

### Security
- No new auth, secrets, or PII surface introduced.
- MDX content is in-tree only; no user-supplied MDX, so no MDX-XSS surface.
- Pagefind is fully static (no server-side search endpoint) — no injection vector.
- 301 redirect target `/docs/plugins → /marketplace` is hardcoded in `next.config.ts` — no open-redirect risk.
- Build-time generators run only on `prebuild` and `prepublishOnly`; never on user input.

### Accessibility
- Sidebar active state and TOC active item must meet WCAG AA contrast against their backgrounds in both light and dark themes.
- Animated tab indicator and TOC scroll-spy animations respect `prefers-reduced-motion: reduce` — fall back to instant state changes.
- Shiki output preserves semantic `<pre><code>` structure; copy button retains its existing `aria-label`.
- Hero h1 uses `text-wrap: balance` for readability without sacrificing semantic structure.

### SEO
- New `/marketplace` is added to the sitemap at priority 0.85; `/insights`, `/learn`, and `/docs` are added at appropriate priorities (currently all missing from the sitemap).
- 301 redirect `/docs/plugins → /marketplace` preserves any existing inbound links and search-engine equity.
- MDX-converted pages keep their existing URL slugs (`/docs/security-guidelines`, `/docs/cli-reference`) — no redirect needed for them.

### Compatibility
- Cloudflare Workers (`output: standalone`) compatibility preserved: no Node-only APIs introduced; Pagefind index is generated into `public/pagefind/` and served via the worker static-file fallback.
- Existing tests (`docs-nav.test.ts`, `link-checker.test.ts`, `docs-sidebar.test.tsx`) must continue passing; `link-checker` allow-list extended for new `/marketplace` URL.

---

## Out of Scope

The following are explicitly **not** part of this increment — they are V2 candidates documented here so reviewers don't expand scope:

- **DB-backed marketplace data** — V1 plugin data lives in `src/lib/marketplace/plugins.ts` as hardcoded typed entries. A Prisma/D1-backed marketplace is a separate increment.
- **Per-plugin detail pages** (`/marketplace/[slug]`) — V1 cards link out to existing plugin documentation; dedicated detail routes come later.
- **Multiple Featured Collections** — V1 ships a single spotlight card; rotating or themed collections are V2.
- **Full Insights merge into Marketplace as the primary nav** — `/insights/*` URLs stay live; insights articles are surfaced in the marketplace feed but the existing `/insights` route is **not** removed, rewritten, or made a sub-route of `/marketplace`.
- **Search beyond Pagefind static index** — no server-side search, no AI-powered semantic search; only the static Pagefind WASM index.
- **Theme switching** beyond the existing dark/light token system — no new theme picker UI.
- **MDX migration of marketing pages** — `src/app/docs/page.tsx`, `src/app/docs/getting-started/page.tsx`, `src/app/docs/submitting/page.tsx`, `src/app/docs/faq/page.tsx`, and `src/app/docs/plugins/page.tsx` (which collapses to a redirect) stay as React components.
- **Count generator beyond the documented six count fields** — no telemetry, no historical tracking, no dashboard.

---

## Glossary

- **MDX** — Markdown with embedded JSX/components, server-rendered by Next 15 via `@next/mdx`. Used here for content-heavy reference pages.
- **Pagefind** — Static, WASM-based search index generated post-build; no search server required. Mounted as a `⌘K` palette.
- **Shiki** — Syntax highlighting library that runs at build/SSR time using TextMate grammars and VS Code themes (`github-dark`, `github-light`).
- **Scroll-spy** — UI pattern where the active section in a TOC updates as the user scrolls; here implemented via `IntersectionObserver` for performance.
- **Tier ladder** — Brand language for verification levels: Scanned (automated), Verified (human-reviewed), Certified (signed). Each tier gets ascending visual weight.
- **`COUNTS` import** — Build-generated TypeScript constant exported from `src/lib/generated-counts.ts`; replaces hardcoded plugin/skill/agent counts across the codebase.
- **`prepublishOnly`** — npm lifecycle hook that runs before `npm publish`; used in vskill to guard against stale README badges via `git diff --exit-code`.
