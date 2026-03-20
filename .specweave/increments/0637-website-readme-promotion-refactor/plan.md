# Implementation Plan: Website & README Promotion Refactor

## Overview

Content-focused refactor of spec-weave.com homepage (Docusaurus), GitHub README, and hierarchy mapping docs. No new APIs, no database changes — purely TSX components, markdown, and content.

## Architecture

### Components (Docusaurus site)

Homepage at `docs-site/src/pages/index.tsx` imports section components from `docs-site/src/components/sections/`.

**Existing (keep/modify)**:
- `HeroSection.tsx` — modify messaging and add badge bar
- `TrustedBySection.tsx` — keep as-is
- `DemoVideoSection.tsx` — keep as-is (Remotion video)
- `HowItWorksSection.tsx` — keep as-is
- `IntegrationsSection.tsx` — keep as-is
- `CTASection.tsx` — keep as-is

**New**:
- `WhySpecFirstSection.tsx` — comparison table + explainer
- `ShowcaseSection.tsx` — production apps + stats
- `TopSkillsSection.tsx` — skill grid with CTA

**Remove from homepage** (files stay, just not imported):
- `StatsSection.tsx`
- `AcademyPromoSection.tsx`
- `VerifiedSkillsSection.tsx`
- `SkillStudioSection.tsx`

### Docs (Docusaurus markdown)
- `docs/guides/hierarchy-mapping.md` — add mermaid diagrams
- `docs/reference/metadata-reference.md` — new page
- `sidebars.ts` — add metadata-reference entry

### README
- `README.md` — full rewrite, same file

## Technology Stack

- **Framework**: Docusaurus v3 (React 19)
- **Styling**: Existing CSS modules pattern in docs-site
- **Diagrams**: Mermaid (native Docusaurus support)
- **Content**: MDX/Markdown

## Implementation Phases

### Phase 1: New Homepage Components (parallel)
Create WhySpecFirstSection, ShowcaseSection, TopSkillsSection

### Phase 2: Homepage Assembly
Modify HeroSection messaging, update index.tsx imports/order

### Phase 3: README Rewrite
Complete README.md rewrite

### Phase 4: Docs Enhancement
Add mermaid diagrams, create metadata reference, update sidebar

### Phase 5: Verification
Build site, verify all sections render, check for broken links

## Testing Strategy

- Docusaurus build (`npm run build`) as integration test
- Visual verification via dev server
- Markdown linting for docs
- No unit tests needed for static content components (TSX renders static HTML)
