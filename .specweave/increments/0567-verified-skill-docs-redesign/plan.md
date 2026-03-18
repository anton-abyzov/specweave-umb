# Architecture Plan: Verified Skill Docs Redesign + Video Learning Section

**Increment**: 0567-verified-skill-docs-redesign
**Architect**: sw:architect
**Date**: 2026-03-18
**Repos**: vskill-platform (primary), specweave/docs-site (secondary)

---

## 1. CSS Architecture: Light-Mode Variable Fix

### Problem

`globals.css` defines `--card-bg: #111111` in `:root` (light mode). This dark value is correct for intentionally-dark surfaces (trending skills section, homepage cards, video hero) but wrong for general-purpose light-mode card backgrounds. The variable name is misleading: it does not mean "a card on a light page" -- it means "a card that is always dark."

### Decision: Introduce Scoped Surface Tokens

Split the single `--card-bg` into two semantic layers:

```
:root (light mode)
  --surface-card: #FFFFFF          /* NEW: card on a light page */
  --surface-card-text: #111111     /* NEW: text on light card */
  --surface-dark: #111111          /* RENAME of --card-bg */
  --surface-dark-text: #E6EDF3     /* RENAME of --card-text */
  --surface-dark-muted: #8B949E    /* RENAME of --card-text-muted */

[data-theme="dark"]
  --surface-card: #161B22          /* card on dark page */
  --surface-card-text: #E6EDF3
  --surface-dark: #161B22          /* same as surface-card in dark mode */
  --surface-dark-text: #E6EDF3
  --surface-dark-muted: #8B949E
```

### Migration Path

1. Add the new `--surface-*` tokens alongside existing `--card-*` tokens
2. New code uses `--surface-card` for doc cards, learn cards; `--surface-dark` for homepage/trending
3. Legacy `--card-bg`, `--card-text`, `--card-text-muted` remain as aliases: `--card-bg: var(--surface-dark)`
4. No existing component breaks. Migration is additive only

### Additional Light-Mode Fixes

These variables need light-mode values that are currently too dark or too faint:

| Variable | Current `:root` | Problem | Fix |
|---|---|---|---|
| `--bg-code` | `#111111` | Dark terminal bg on white page | Keep as-is (code blocks are intentionally dark) |
| `--text-faint` | `#999999` | WCAG AA fail on `#FFFFFF` bg (3.0:1) | Change to `#767676` (4.54:1, AA pass) |
| `--text-faint-terminal` | `#6B7380` | Only used inside dark terminals | Keep as-is |

### Component Impact

| Component | Uses `--card-bg` | Action |
|---|---|---|
| `TrendingSkills.tsx` | Yes (dark rows) | Keep `--surface-dark` |
| `homepage/VideoHero.tsx` | No (hardcoded `#0a0a0a`) | No change |
| `DocCard.tsx` | No (uses `--border`) | Will use `--surface-card` for new hover states |
| `home/PipelineFlow.tsx` | No | No change |
| **NEW** `VideoCard.tsx` | Will use `--surface-card` | New component |
| **NEW** `/learn` page | Will use `--surface-card` | New route |

---

## 2. Typography System: Geist Sans for Prose, Geist Mono for Code

### Current State

The entire site uses `var(--font-geist-mono)` for everything -- headings, body text, nav, metrics. This is the monospace font. The `geist` package (v1.7.0) already ships both `GeistSans` and `GeistMono`, and both are loaded in `layout.tsx`.

### Decision: CSS Class Scoping Strategy

Add two utility classes to `globals.css`:

```css
.prose {
  font-family: var(--font-geist-sans);
  line-height: 1.7;
  letter-spacing: 0;
}

.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
  font-family: var(--font-geist-sans);
  letter-spacing: -0.02em;
  line-height: 1.25;
}

.prose code, .prose pre, .prose kbd {
  font-family: var(--font-geist-mono);
}
```

### Where to Apply

| Page/Section | Current | Target | How |
|---|---|---|---|
| Docs prose body (`DocsLayout` `<main>`) | Mono | `.prose` wrapper around `{children}` | Wrap in `DocsLayout.tsx` |
| `/learn` page descriptions | N/A (new) | `.prose` | Apply to description blocks |
| Doc page `<h1>` + subheadline | Mono inline style | `.prose` | Remove inline `fontFamily` overrides |
| Nav sidebar labels | Mono | Stay Mono | No change (nav is UI, not prose) |
| Code blocks | Mono | Stay Mono | Handled by `.prose code` override |
| Metrics, badges, labels | Mono | Stay Mono | These are data/UI, not prose |
| Homepage | Mono | Stay Mono | Brand identity is mono-first |

### Why Not a Component

A `<Prose>` wrapper component adds a React boundary for what is purely a CSS concern. A CSS class is simpler, can be applied via `className` on any element, and avoids import overhead.

---

## 3. /learn Route: Page Structure and Data Model

### App Router Structure

```
src/app/learn/
  layout.tsx          # Shared layout with sidebar categories + search
  page.tsx            # /learn landing -- featured videos, category browse
  [slug]/
    page.tsx          # Individual video page -- player + sidebar nav
```

### Data Model: Video Metadata

Static JSON file, not a database table. Reasons: (a) video count is small (~10-20 101 videos), (b) no user-generated content, (c) zero additional infrastructure, (d) deploys with the app.

```typescript
// src/lib/learn/videos.ts

export interface Video {
  slug: string;                    // URL segment: "getting-started-101"
  title: string;                   // "Getting Started with vskill"
  description: string;             // 1-2 sentence summary
  duration: number;                // seconds
  category: VideoCategory;
  tags: string[];                  // ["cli", "installation", "quickstart"]
  thumbnail: string;               // "/learn/thumbnails/getting-started-101.webp"
  sources: {
    mp4: string;                   // "/video/learn/getting-started-101.mp4"
    webm?: string;                 // optional WebM
  };
  remotionComposition?: string;    // "GettingStarted101" -- links to Remotion comp for re-render
  publishedAt: string;             // ISO date
  relatedDocs?: string[];          // ["/docs/getting-started", "/docs/cli-reference"]
  relatedVideos?: string[];        // ["cli-commands-101"]
}

export type VideoCategory =
  | "getting-started"
  | "cli-deep-dive"
  | "security"
  | "plugins"
  | "specweave-integration"
  | "advanced";

// src/lib/learn/video-data.ts -- the actual data
export const VIDEOS: Video[] = [
  // ... static entries
];

// Lookup helpers
export function getVideo(slug: string): Video | undefined;
export function getVideosByCategory(cat: VideoCategory): Video[];
export function getFeaturedVideos(): Video[];
```

### Filtering State Management

URL search params via `useSearchParams()`. No external state library.

```
/learn?category=security&q=scan
/learn?category=getting-started
```

This is the simplest approach that supports:
- Browser back/forward for filter changes
- Shareable filtered URLs
- SSR-compatible (search params available server-side)
- No state library dependency

Implementation: `LearnPage` reads `searchParams` from the page props (Next.js 15 App Router passes these to server components). The category pills and search input update the URL via `router.push` with shallow navigation.

---

## 4. VideoCard Component

### Props Interface

```typescript
// src/app/components/learn/VideoCard.tsx

interface VideoCardProps {
  slug: string;
  title: string;
  description: string;
  duration: number;
  category: VideoCategory;
  thumbnail: string;
  className?: string;
}
```

### Layout

```
+---------------------------------------+
|  [thumbnail.webp]                     |   aspect-ratio: 16/9
|            play icon  (overlay)       |   object-fit: cover
|                          02:34  badge |
+---------------------------------------+
|  Getting Started                       |   category pill (small, muted)
|  Getting Started with vskill          |   title (Geist Sans, 600 weight)
|  Install and run your first scan...   |   description (.prose, text-muted)
+---------------------------------------+
```

### Responsive Grid

```css
.learn-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .learn-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  .learn-grid { grid-template-columns: 1fr; }
}
```

### Thumbnail Generation Strategy

Use Remotion stills (`npx remotion still <composition> --frame=0 --output=...`). Each 101 video has a corresponding Remotion `<Still>` composition that renders the title card frame. The thumbnail is generated at build time (or manually during dev) and committed as a `.webp` file.

Why `.webp` over `.png`:
- 25-35% smaller file size at equivalent quality
- Native browser support is universal (97%+ as of 2025)
- Smaller thumbnails = faster grid load on `/learn`

Thumbnail storage: `public/learn/thumbnails/{slug}.webp` -- served by Cloudflare's CDN automatically since these are in `/public`.

---

## 5. Video Hosting: Self-Hosted in /public/video/learn/

### Decision: Keep Videos in /public/video/learn/

NOT Cloudflare R2. Reasons:

| Factor | /public/video/ | Cloudflare R2 |
|---|---|---|
| Infrastructure | Zero (already deployed) | New R2 bucket + binding + Worker route |
| CDN | Cloudflare automatic (Wrangler assets) | Cloudflare automatic (R2 custom domain) |
| Deployment | `git push` (existing) | Separate upload pipeline |
| Cost | Free (within Cloudflare Pages/Workers limits) | R2 storage + egress (pennies, but nonzero) |
| DX | Edit, deploy, done | Edit, upload to R2, deploy |
| Git bloat | Yes, ~2-5 MB per video | No git bloat |
| Existing pattern | `/public/video/` already has 7 videos (~16 MB) | No R2 binding exists |

### The Git Bloat Tradeoff

Current `/public/video/` is 16 MB for 7 videos. Adding 10-15 101 videos at ~2-4 MB each (compressed, 1-2 min, 1080p) adds ~30-60 MB. Total: ~76 MB in git. This is within the acceptable range for a single-repo approach. Each video is committed once and rarely changes.

If the video library grows beyond ~50 videos or ~200 MB, migrate to R2 at that point. The `Video.sources.mp4` paths are just strings -- switching from `/video/learn/foo.mp4` to `https://r2.verified-skill.com/learn/foo.mp4` is a one-line data change per video.

### Directory Structure

```
public/video/
  learn/
    getting-started-101.mp4
    getting-started-101.webm     # optional, if Remotion renders WebM
    cli-commands-101.mp4
    ...
  homepage-demo.mp4              # existing
  ship-while-you-sleep.mp4       # existing
  ...

public/learn/
  thumbnails/
    getting-started-101.webp
    cli-commands-101.webp
    ...
```

---

## 6. IA Restructure: Diataxis Framework

### Current IA (7 pages, flat)

```
/docs                    -> Overview (hub page)
/docs/getting-started    -> Quick Start
/docs/cli-reference      -> CLI Reference
/docs/security-guidelines -> Security Guidelines
/docs/plugins            -> Plugin Marketplace
/docs/submitting         -> Submit a Skill
/docs/faq                -> FAQ
```

### Target IA (Diataxis Quadrants)

Diataxis organizes documentation into four types:
- **Tutorials** (learning-oriented): Get started step by step
- **How-to Guides** (task-oriented): Accomplish a specific goal
- **Reference** (information-oriented): Technical descriptions
- **Explanation** (understanding-oriented): Conceptual discussion

Proposed restructure:

```
/docs                          -> Overview hub (keep)
  Tutorials
    /docs/getting-started      -> Quick Start (keep URL)
  How-to Guides
    /docs/submitting           -> Submit a Skill (keep URL)
  Reference
    /docs/cli-reference        -> CLI Reference (keep URL)
    /docs/security-guidelines  -> Security Guidelines (keep URL)
    /docs/plugins              -> Plugin Marketplace (keep URL)
  Explanation
    /docs/faq                  -> FAQ (keep URL)
```

### URL Stability: No Redirects Needed

The existing 6 doc page URLs all survive the restructure. The change is purely navigational -- the sidebar groups pages under Diataxis headings, but the URLs remain identical. This is critical because:
- No SEO penalty from redirects
- No broken external links
- No Next.js redirect config changes needed
- Existing `docs-nav.ts` just adds group labels

### Navigation Config Change

```typescript
// src/app/docs/docs-nav.ts -- updated

export const DOCS_NAV: NavItem[] = [
  { label: "Overview", href: "/docs" },
  {
    label: "Tutorials",
    href: "/docs/getting-started",
    children: [
      { label: "Getting Started", href: "/docs/getting-started" },
    ],
  },
  {
    label: "How-to Guides",
    href: "/docs/submitting",
    children: [
      { label: "Submitting Skills", href: "/docs/submitting" },
    ],
  },
  {
    label: "Reference",
    href: "/docs/cli-reference",
    children: [
      { label: "CLI Reference", href: "/docs/cli-reference" },
      { label: "Security Guidelines", href: "/docs/security-guidelines" },
      { label: "Plugins", href: "/docs/plugins" },
    ],
  },
  {
    label: "Explanation",
    href: "/docs/faq",
    children: [
      { label: "FAQ", href: "/docs/faq" },
    ],
  },
];
```

The `NavItem` interface already supports `children?: NavItem[]`, and `DocsLayout.tsx` already renders nested items when the parent is active. No component changes needed.

---

## 7. Cross-Repo Video Integration (Docusaurus docs-site)

### Problem

The specweave docs-site (Docusaurus 3.9.2 at `repositories/anton-abyzov/specweave/docs-site/`) needs to embed videos that are hosted on vskill-platform's domain (`verified-skill.com`).

### Decision: Cross-Origin Video Embeds via Absolute URLs

Docusaurus MDX pages reference videos using full URLs:

```mdx
<!-- In a Docusaurus .mdx file -->
import VideoEmbed from '@site/src/components/ui/VideoEmbed';

<VideoEmbed
  src="https://verified-skill.com/video/learn/getting-started-101.mp4"
  thumbnail="https://verified-skill.com/learn/thumbnails/getting-started-101.webp"
  title="Getting Started with vskill"
  duration={154}
/>
```

### VideoEmbed Component for Docusaurus

```typescript
// docs-site/src/components/ui/VideoEmbed/index.tsx

interface VideoEmbedProps {
  src: string;            // full URL to mp4
  webm?: string;          // optional WebM URL
  thumbnail: string;      // full URL to thumbnail
  title: string;
  duration: number;       // seconds
}
```

This is a click-to-play component (not autoplay). It shows the thumbnail with a play button overlay. On click, it replaces the thumbnail with a `<video>` element. This avoids loading video bytes until the user explicitly requests playback.

### Why Not iframe Embed

An `<iframe>` pointing to `verified-skill.com/learn/[slug]` would work but:
- Loads the entire Next.js shell (header, nav, footer) inside the iframe
- No style control from the Docusaurus side
- Heavier initial load
- CSP/frame-ancestors headers needed

A direct `<video>` element with a cross-origin `src` is simpler, lighter, and renders natively.

### CORS Consideration

The videos are static files served from Cloudflare's CDN (Wrangler assets). Cloudflare serves static assets with permissive CORS by default. No custom headers needed.

---

## 8. Remotion Scene Strategy for 101 Videos

### Existing Reusable Scenes (vskill-platform)

| Scene | Reuse for 101s | Why |
|---|---|---|
| `scenes/InstallDemo.tsx` | Yes | CLI installation flow, directly maps to "Getting Started 101" |
| `scenes/CLIShowcase.tsx` | Yes | Command demos for "CLI Deep Dive 101" |
| `scenes/VerifyBlockDemo.tsx` | Yes | Security scan visualization for "Security 101" |
| `scenes/VerifiedSkills.tsx` | Partial | Trust tier badges, usable as b-roll |
| `scenes/FileTreeDemo.tsx` | Partial | File structure animation, useful for "Plugin Structure 101" |
| `scenes/Intro.tsx` | Yes | Branded intro slate, reuse as-is for all 101s |
| `scenes/Outro.tsx` | Yes | Branded outro slate, reuse as-is |
| `components/TerminalFrame.tsx` | Yes | Terminal chrome wrapper, used in most CLI scenes |
| `components/BigText.tsx` | Yes | Title card text rendering |

### New Scenes Needed

| New Scene | Purpose | Composition ID |
|---|---|---|
| `scenes/learn/TitleCard.tsx` | Generic 101 title card with topic name + number | `Learn101TitleCard` |
| `scenes/learn/PluginBrowse.tsx` | Plugin marketplace browsing animation | `Learn101Plugins` |
| `scenes/learn/SpecWeaveWorkflow.tsx` | Spec-driven development lifecycle | `Learn101SpecWeave` |
| `scenes/learn/SecurityScan.tsx` | Step-by-step scan walkthrough (slower than VerifyBlockDemo) | `Learn101Security` |

### Thumbnail Generation Pipeline

Each 101 video gets a `<Still>` composition registered in `Root.tsx`:

```typescript
// In Root.tsx, add for each 101 video:
<Still
  id="Learn101TitleCard-getting-started"
  component={TitleCard}
  defaultProps={{ title: "Getting Started", number: "01" }}
  width={1920}
  height={1080}
/>
```

Generate thumbnails:
```bash
npx remotion still Learn101TitleCard-getting-started \
  --output public/learn/thumbnails/getting-started-101.webp \
  --image-format=webp
```

This can be scripted as an npm script (`npm run generate-thumbnails`) that iterates over the video data and renders all stills.

---

## 9. Component Boundaries and New File Map

### New Files (vskill-platform)

```
src/app/learn/
  layout.tsx                           # Learn section layout (sidebar categories)
  page.tsx                             # /learn landing page

src/app/learn/[slug]/
  page.tsx                             # Individual video page

src/app/components/learn/
  VideoCard.tsx                        # Grid card for /learn listing
  VideoGrid.tsx                        # Responsive grid wrapper
  CategoryFilter.tsx                   # Category pill strip (reuses .category-pill class)
  LearnSidebar.tsx                     # Sidebar nav for /learn section

src/lib/learn/
  videos.ts                            # Video type definitions + helpers
  video-data.ts                        # Static video metadata array

src/remotion/scenes/learn/
  TitleCard.tsx                        # Generic 101 title card scene
  PluginBrowse.tsx                     # Plugin marketplace animation
  SpecWeaveWorkflow.tsx                # Spec-driven workflow animation
  SecurityScan.tsx                     # Security scan walkthrough
```

### New Files (specweave docs-site)

```
src/components/ui/VideoEmbed/
  index.tsx                            # Cross-origin video embed component
  styles.module.css                    # Scoped styles
```

### Modified Files (vskill-platform)

```
src/app/globals.css                    # Add --surface-* tokens, .prose class, .learn-grid
src/app/docs/docs-nav.ts              # Diataxis grouping
src/app/components/DocsLayout.tsx      # Wrap children in .prose
src/remotion/Root.tsx                  # Register new 101 compositions + stills
```

---

## 10. Data Flow Diagram

```
                    vskill-platform (Next.js 15)
                    ============================

[video-data.ts]  -->  /learn (page.tsx)
  Static array           |
  of Video objects        |--- VideoGrid ---> VideoCard (x N)
                          |      uses searchParams for filtering
                          |
                          \--- /learn/[slug] (page.tsx)
                                 |
                                 |--- VideoPlayer (existing shared component)
                                 |     src="/video/learn/{slug}.mp4"
                                 |
                                 \--- Related docs links
                                       href="/docs/getting-started"


[Remotion]  -->  Still compositions  -->  public/learn/thumbnails/*.webp
                 (build-time)              (served by Cloudflare CDN)


                    specweave docs-site (Docusaurus 3.9.2)
                    =======================================

MDX page  -->  <VideoEmbed
                 src="https://verified-skill.com/video/learn/{slug}.mp4"
                 thumbnail="https://verified-skill.com/learn/thumbnails/{slug}.webp"
               />
```

---

## 11. WCAG AA Compliance Checklist

| Requirement | Implementation |
|---|---|
| Color contrast (text) | `--text-faint` fix to 4.54:1. All new text on `--surface-card` will be `--text` (15.3:1 on white) |
| Color contrast (UI) | Category pills, borders: minimum 3:1 against background |
| Focus indicators | All interactive elements (VideoCard, CategoryFilter) get `:focus-visible` outline |
| Video captions | `<track kind="captions">` on all `<video>` elements (already in VideoPlayer.tsx) |
| Reduced motion | Respect `prefers-reduced-motion` for any animations (already in globals.css for cursor) |
| Keyboard navigation | VideoCard grid is tabbable via `<a>` wrapping. Category pills are buttons with focus states |

---

## 12. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Git repo grows too large from video files | Low (estimated ~76 MB) | Medium | Monitor after 10 videos. R2 migration path is documented and trivial (path swap in video-data.ts) |
| Remotion thumbnail generation slows CI | Low | Low | Generate thumbnails manually/locally, commit artifacts. Not in CI pipeline |
| Diataxis grouping confuses users with only 6 pages | Medium | Low | Groups are collapsible in sidebar. If feedback is negative, flatten back -- zero URL changes either way |
| Cross-origin video fails on some browsers/corporate proxies | Low | Medium | Cloudflare default CORS is permissive. Add explicit `Access-Control-Allow-Origin: *` header in Wrangler if needed |
| `.prose` class conflicts with existing inline styles | Medium | Low | Inline styles have higher specificity than class styles. Remove inline `fontFamily` overrides in doc pages to let `.prose` take effect |

---

## 13. Implementation Order

Recommended task sequence (dependencies shown):

1. **CSS tokens** -- Add `--surface-*` variables and `.prose` class to `globals.css`
2. **Typography** -- Update `DocsLayout.tsx` to wrap content in `.prose`, remove inline font overrides from doc pages
3. **WCAG fix** -- Update `--text-faint` to `#767676`
4. **IA restructure** -- Update `docs-nav.ts` with Diataxis groups
5. **Video data model** -- Create `src/lib/learn/videos.ts` + `video-data.ts`
6. **VideoCard component** -- Create `src/app/components/learn/VideoCard.tsx` + grid
7. **/learn route** -- Create `src/app/learn/` pages (layout, listing, detail)
8. **Remotion scenes** -- Create new 101 scenes in `src/remotion/scenes/learn/`
9. **Thumbnail generation** -- Render stills, commit to `public/learn/thumbnails/`
10. **Video production** -- Render 101 videos, commit to `public/video/learn/`
11. **Docusaurus VideoEmbed** -- Create cross-origin embed component in docs-site
12. **Integration testing** -- Verify /learn pages, video playback, cross-repo embeds, WCAG

Tasks 1-4 are independent of 5-7. Tasks 8-10 can proceed in parallel once the data model (5) is defined.
