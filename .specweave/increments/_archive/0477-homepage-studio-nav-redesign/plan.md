# Architecture Plan — 0477 Homepage Simplification, Studio Landing Page, and Navigation Restructure

## Overview

This increment restructures the vskill-platform frontend around a search-first homepage, a dedicated `/studio` landing page, streamlined navigation, and dead-code cleanup. The work targets `repositories/anton-abyzov/vskill-platform/` (Next.js 15, Cloudflare Workers, inline CSS, Geist Mono font).

## Current State Analysis

### File Inventory (what exists today)

| File | Lines | Role | Fate |
|------|-------|------|------|
| `src/app/page.tsx` | 299 | Homepage: video hero + role cards + search + trending + studio section + category nav + market dashboard + verification explainer + agent badges | **REWRITE** to ~100 lines |
| `src/app/layout.tsx` | 170 | Root layout with nav (Skills, Publishers, Trust, Docs, Queue, Submit, GitHub) and footer | **EDIT** nav links + add footer Studio link |
| `src/app/components/homepage/HomepageDemoHero.tsx` | 165 | Client component: video + play/pause + CLI copy overlay | **DELETE** after VideoPlayer extraction |
| `src/app/components/homepage/SkillStudioSection.tsx` | 228 | Client component: studio video + feature badges + CLI copy | **DELETE** after /studio page created |
| `src/app/components/MobileNav.tsx` | 54 | Mobile hamburger menu (Skills, Publishers, Trust, Docs, Queue, Submit, GitHub) | **EDIT** link list |
| `src/app/components/home/HeroSearchInput.tsx` | 71 | Client: dispatches `openSearch` custom event | **REUSE** as-is |
| `src/app/components/home/CategoryNav.tsx` | 41 | Server component: category pills from KV stats | **REUSE** as-is |
| `src/app/components/home/TrendingSkills.tsx` | 87 | Server component: trending table from KV stats | **REUSE** as-is |
| `src/app/components/home/MarketDashboard.tsx` | 119 | Server component: 4 metric cards + category chart from KV | **DELETE** |
| `src/app/components/home/HeroStats.tsx` | 37 | Server: HeroHeading + InlineStats from KV | **PARTIALLY REUSE** (HeroHeading for new hero, InlineStats removed) |
| `src/app/components/home/HomeSkeleton.tsx` | 155 | Skeleton loaders for all homepage sections | **EDIT** remove unused skeletons |
| `src/app/components/SearchPalette.tsx` | 550 | Cmd+K palette | **UNCHANGED** |

### Duplication Audit

`HomepageDemoHero.tsx` and `SkillStudioSection.tsx` share identical patterns:
- `useRef<HTMLVideoElement>` + `useState(true)` for play state
- `togglePlay` callback (play/pause toggle)
- Play/Pause overlay button with same SVG icons
- `<video autoPlay muted loop playsInline>` with `<source>` tags

The only differences: video sources, aria-label, accent color on button border, and whether children are rendered inside. Copy-to-clipboard logic also duplicated but with different commands.

## Architecture Decisions

### AD-1: VideoPlayer as a client component in `src/app/components/shared/`

**Decision**: Extract a single `VideoPlayer.tsx` client component that accepts props for all varying parts.

**Props interface**:
```typescript
interface VideoPlayerProps {
  mp4: string;              // e.g. "/video/homepage-demo.mp4"
  webm: string;             // e.g. "/video/homepage-demo.webm"
  ariaLabel: string;
  accentColor?: string;     // border color for play/pause button; defaults to "rgba(255,255,255,0.2)"
  className?: string;
  eager?: boolean;          // skip IntersectionObserver, load immediately
}
```

**Lazy loading**: Uses `IntersectionObserver` by default. When the video container enters the viewport (root margin `200px`), set the video sources. Disconnects observer on unmount via cleanup return in `useEffect`. When `eager={true}`, sources are present from initial render.

**Scope**: Play/pause overlay button only. Copy-to-clipboard overlays are NOT part of VideoPlayer -- they are context-specific (different commands, different positioning) and belong to the parent component.

**Alternative considered**: Render prop for overlays. Rejected -- the play/pause button is the only universal overlay. Copy buttons differ per usage.

### AD-2: `/studio` as a server component page with client VideoPlayer child

**Decision**: Create `src/app/studio/page.tsx` as a server component.

The page is entirely static content (heading, tagline, CLI command, feature cards, getting-started steps). The only client part is the `<VideoPlayer>` import. No KV/DB calls needed -- no `force-dynamic`.

**SEO metadata**: Exported via Next.js `metadata` object (title, description, OG, Twitter). No JSON-LD needed for `/studio` (JSON-LD SearchAction is homepage-only per US-006).

### AD-3: Navigation data as inline constants

**Decision**: Define nav link arrays as typed constants in `layout.tsx` (desktop) and `MobileNav.tsx` (mobile). No dynamic nav configuration.

**Desktop nav order** (after separator): Skills, Studio, Publishers, Trust, Docs

**Footer**: Add Studio link between Skills and Publishers. Retain Queue and Submit.

**Mobile nav order**: Skills, Studio, Publishers, Trust, Docs, GitHub

**Rationale**: 5-6 static links. Constants are simplest. Project uses inline styles throughout.

### AD-4: Homepage hero search with conditional auto-focus

**Decision**: Create a new `HeroSearch.tsx` client component for the homepage that:
1. On mount, checks `window.matchMedia('(hover: hover)').matches`
2. If true (non-touch device), focuses the input
3. On input change, dispatches `openSearch` custom event (same as existing `HeroSearchInput.tsx`)
4. Uses larger placeholder: "Search 90,000+ verified skills..."

**Why not modify `HeroSearchInput.tsx`**: That component is also imported by `CategoryNav.tsx` (via `SearchTriggerInput`). Auto-focus logic is homepage-specific and should not leak to other contexts.

### AD-5: Compact agent strip replaces full badge grid

**Decision**: Replace the verbose ~100-line agent badge section with a compact inline strip: "Works with 39 agents" + first 6 agent icon pills + "+33 more".

**Data source**: Existing `FEATURED_AGENTS` and `MORE_AGENTS` arrays. Move them from `page.tsx` to `src/lib/agent-branding.ts` to co-locate all agent data.

### AD-6: JSON-LD SearchAction on homepage

**Decision**: Add `<script type="application/ld+json">` in `page.tsx` only (not layout.tsx).

**Schema**:
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "vskill",
  "url": "https://verified-skill.com",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://verified-skill.com/skills?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

### AD-7: Dead code cleanup strategy

Delete files only AFTER all new components are wired and tests pass (Phase 4).

**Files to delete**:
- `src/app/components/homepage/HomepageDemoHero.tsx`
- `src/app/components/homepage/SkillStudioSection.tsx`
- `src/app/components/home/MarketDashboard.tsx`

**Skeleton exports to remove** from `HomeSkeleton.tsx`: `HeroStatsSkeleton`, `DashboardSkeleton`, `InlineStatsSkeleton`.

**Verification gate**: `npx tsc --noEmit` + full test suite.

## Component Architecture

```
layout.tsx (server)
├── nav: [Skills, Studio, Publishers, Trust, Docs] + GitHub icon
├── footer: [Skills, Studio, Publishers, Trust, Docs, Queue, Submit, GitHub, npm]
├── SearchPalette (client, unchanged)
└── MobileNav (client, updated links)

page.tsx (server, force-dynamic)
├── Hero section (inline)
│   ├── HeroHeading (server, reused from HeroStats.tsx)
│   ├── Stat callout ("90k+ verified")
│   └── HeroSearch (client, new -- auto-focus + openSearch dispatch)
├── CategoryNav (server, reused)
├── TrendingSkillsSection (server, reused)
├── AgentStrip (inline, ~15 lines)
│   ├── 6 agent icon pills from FEATURED_AGENTS
│   └── "+N more" text
└── JSON-LD <script> (SearchAction)

studio/page.tsx (server, static)
├── Hero (heading, tagline, CopyButton for "npx vskill studio")
├── VideoPlayer (client, shared, lazy-loaded)
├── Feature cards (4 static: BDD Tests/green, A/B Compare/blue, Any Model/purple, 100% Local/cyan)
└── Getting-started (3 numbered steps, each with CopyButton)

components/shared/
├── VideoPlayer.tsx (client) -- extracted from HomepageDemoHero + SkillStudioSection
└── CopyButton.tsx (client) -- copy-to-clipboard with "copied" feedback
```

## Data Flow

```
KV (home-stats) ──getHomeStats()──► page.tsx (server render)
                                    ├──► HeroHeading (verified count)
                                    ├──► CategoryNav (category pills)
                                    └──► TrendingSkillsSection (trending table)

User types in HeroSearch ──openSearch CustomEvent──► SearchPalette (takes over)

FEATURED_AGENTS / MORE_AGENTS (from @/lib/agent-branding)
  └──► AgentStrip (first 6 icons + total count)
```

## Phase Dependency Graph

```
Phase 1: VideoPlayer + /studio ─────┐
                                     ├──► Phase 3: Homepage rewrite ──► Phase 4: Cleanup + SEO
Phase 2: Nav restructure ───────────┘
```

Phases 1 and 2 are independent and can be implemented in parallel or any order. Phase 3 depends on both (homepage imports shared components and nav must link to `/studio`). Phase 4 depends on 3 (dead code deleted only after homepage no longer references old components).

## Phase Breakdown

### Phase 1: VideoPlayer + /studio page (US-001, US-002)

**New files**:
- `src/app/components/shared/VideoPlayer.tsx` (~70 lines)
- `src/app/components/shared/CopyButton.tsx` (~30 lines)
- `src/app/studio/page.tsx` (~120 lines)
- `src/app/components/shared/__tests__/VideoPlayer.test.tsx`
- `src/app/components/shared/__tests__/CopyButton.test.tsx`
- `src/app/studio/__tests__/page.test.tsx`

**No existing files modified.** Purely additive.

### Phase 2: Nav restructure (US-003, US-004)

**Modified files**:
- `src/app/layout.tsx` -- desktop nav links reordered, footer adds Studio
- `src/app/components/MobileNav.tsx` -- link list updated

**Test files**:
- `src/app/__tests__/layout.test.tsx`
- `src/app/components/__tests__/MobileNav.test.tsx`

### Phase 3: Homepage rewrite (US-005)

**New files**:
- `src/app/components/home/HeroSearch.tsx` (~50 lines)
- `src/app/components/home/__tests__/HeroSearch.test.tsx`

**Modified files**:
- `src/app/page.tsx` -- complete rewrite from ~300 to ~100 lines

### Phase 4: Cleanup + SEO (US-006, US-007)

**Deleted files**:
- `src/app/components/homepage/HomepageDemoHero.tsx`
- `src/app/components/homepage/SkillStudioSection.tsx`
- `src/app/components/home/MarketDashboard.tsx`

**Modified files**:
- `src/app/components/home/HomeSkeleton.tsx` -- remove unused skeleton exports
- `src/app/page.tsx` -- add JSON-LD SearchAction script tag

**Verification**: `npx tsc --noEmit` + full test suite

## Testing Strategy

**Environment**: Vitest + jsdom (per `vitest.config.ts`: `environmentMatchGlobs: [["src/app/**/__tests__/*.test.tsx", "jsdom"]]`).

**Mocking pattern**: `vi.hoisted()` + `vi.mock()` for ESM compatibility.

| Component | Test Focus |
|-----------|-----------|
| `VideoPlayer` | Renders `<video>` with correct mp4/webm sources; play/pause button toggles state; IntersectionObserver triggers load; `eager` prop skips observer; cleanup disconnects observer; `accentColor` applies to button border |
| `CopyButton` | Renders command text; click calls `navigator.clipboard.writeText` with correct value; shows "copied" feedback |
| `/studio` page | Renders heading + tagline; CopyButton for `npx vskill studio`; VideoPlayer with studio video sources; 4 feature cards with correct labels/colors; 3 getting-started steps; correct metadata export |
| `layout.tsx` nav | Desktop nav contains Skills/Studio/Publishers/Trust/Docs in order; does NOT contain Queue/Submit; Studio links to `/studio`; footer has Studio |
| `MobileNav` | Links in correct order; no Queue/Submit; Studio present |
| `HeroSearch` | Auto-focuses on non-touch (hover:hover matches); does NOT auto-focus on touch; dispatches `openSearch` on input; placeholder matches spec |
| `page.tsx` homepage | Renders HeroHeading + HeroSearch + CategoryNav + TrendingSkills + agent strip; does NOT render old sections; JSON-LD present and valid |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking search flow | HeroSearch uses same `openSearch` CustomEvent -- SearchPalette unchanged |
| SEO regression | JSON-LD SearchAction added; page metadata preserved in layout.tsx; `/studio` gets own metadata |
| Video not loading with IntersectionObserver | `eager` prop escape hatch; 200px rootMargin for early trigger |
| Nav links break existing flows | Queue/Submit moved to footer only (still accessible); all routes remain |
| Dead code cleanup misses reference | `tsc --noEmit` gate + full test suite catches dangling imports |
