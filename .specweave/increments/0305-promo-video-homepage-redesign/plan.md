# Implementation Plan: Promotional Video & Homepage Redesign

## Overview

Two parallel workstreams: (1) Build a Remotion-based promotional video showcasing SpecWeave's workflow, and (2) redesign the homepage with a cinematic hero, feature sections, and image placeholders — all while preserving the existing dashboard/trending data.

## Architecture

### Components (New)

- `src/remotion/` — Remotion video project (separate from Next.js app, lives in vskill-platform repo)
  - `Root.tsx` — Remotion composition root
  - `scenes/` — Individual scene components (IncrementWorkflow, TeamLead, VerifiedSkills, DocGen, CLICommands)
  - `components/` — Shared video primitives (TerminalFrame, AgentIcon, TierBadge, BigText, TransitionWipe)
- `src/app/components/homepage/` — New homepage section components
  - `VideoHero.tsx` — Hero with video player, tagline, CTAs
  - `FeatureSection.tsx` — Reusable alternating-layout feature block
  - `FeatureSpecFirst.tsx` — Spec-first development feature content
  - `FeatureMultiAgent.tsx` — Multi-agent teams feature content
  - `FeatureSecurityVerified.tsx` — Three-tier security feature content
  - `FeatureAgentEcosystem.tsx` — Agent compatibility feature content
  - `ImagePlaceholder.tsx` — Nanobanana placeholder component
  - `ScrollFadeIn.tsx` — IntersectionObserver-based animation wrapper

### Data Model

No database changes. All content is static/component-based. Video is a static asset.

### Video Pipeline

```
src/remotion/ → npx remotion render → public/video/specweave-promo.mp4 + .webm
```

Video is pre-rendered and committed to public/. No server-side rendering needed.

## Technology Stack

- **Video**: Remotion 4.x (React-based programmatic video)
- **Frontend**: Next.js 15 (existing), React Server Components (existing page.tsx is RSC)
- **Animations**: CSS animations + IntersectionObserver (no heavy animation libraries)
- **Fonts**: Geist Sans/Mono (already in project)
- **Images**: SVG placeholders with nanobanana prompt metadata

**Architecture Decisions**:
- **Remotion over After Effects**: Programmatic, versionable, iterable — matches SpecWeave ethos
- **Self-hosted video over YouTube embed**: No tracking, no branding, instant load, loop control
- **CSS animations over Framer Motion**: Lighter bundle, RSC-compatible, sufficient for scroll reveals
- **Separate remotion/ directory**: Keeps video build pipeline isolated from Next.js build

## Implementation Phases

### Phase 1: Remotion Video Setup & Scene Components
- Install Remotion, scaffold project structure
- Build individual scene components with placeholder content
- Compose scenes into full video with transitions
- Render to MP4/WebM

### Phase 2: Homepage Redesign
- Create VideoHero component with HTML5 video player
- Build feature section components with alternating layouts
- Create image placeholder system
- Wire up scroll-triggered animations

### Phase 3: Integration & Polish
- Refactor existing page.tsx to include new sections while preserving dashboard
- Responsive testing and mobile optimization
- Accessibility audit (video controls, reduced motion, alt text)

## Testing Strategy

- Component tests for new homepage components (VideoHero, FeatureSection, ScrollFadeIn)
- Visual regression: ensure existing dashboard/trending sections unchanged
- Remotion: scene-level snapshot tests
- Lighthouse performance check (video lazy-load, image optimization)

## Technical Challenges

### Challenge 1: Remotion + Cloudflare Workers Compatibility
**Solution**: Remotion is a build-time tool only. Video is pre-rendered to MP4/WebM static files. No runtime dependency on Remotion.
**Risk**: Low — complete separation of concerns.

### Challenge 2: Video File Size
**Solution**: Target <5MB for 45s at 1080p. Use H.264 CRF 23-25 for MP4, VP9 CRF 30 for WebM. Lazy-load video below fold.
**Risk**: Medium — may need to adjust quality/length tradeoff.

### Challenge 3: Preserving Existing RSC Data Flow
**Solution**: New sections are purely presentational client components. Existing server component data fetching in page.tsx untouched. New client components receive no server data.
**Risk**: Low — additive changes only.
