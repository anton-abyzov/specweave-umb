# Implementation Plan: Development Loom Documentation Site Rework — Phase 1

## Overview

Introduce a CSS design token system, custom MDX components, Cmd+K search, admonition restyling, and "Development Loom" homepage messaging for the SpecWeave docs site (Docusaurus 3.9.2).

## Architecture

### Components
- **tokens.css**: Foundation design token file (colors, typography, spacing, shadows)
- **custom.css**: Global styles consuming tokens (refactored from 927→~280 lines)
- **Callouts**: Note/Tip/Warning/Info MDX components
- **Steps**: Numbered step sequence with connector line
- **CardGroup**: Responsive grid of clickable cards
- **Accordion**: Native details/summary with animation
- **MDXComponents.tsx**: Global component registration

### Technology Stack
- **Framework**: Docusaurus 3.9.2 + React 19
- **CSS**: Custom properties (design tokens) + CSS Modules
- **Typography**: Inter (Google Fonts CDN) + JetBrains Mono (code)
- **Search**: @easyops-cn/docusaurus-search-local
- **Build**: npm scripts (build, serve)

## Implementation Phases

### Group A: Design Token System (T-001 to T-003)
1. Create `src/css/tokens.css` — refined indigo-purple palette, semantic colors, dark mode
2. Refactor `custom.css` — remove 600+ lines homepage CSS, tokenize everything
3. Add Inter font via Google Fonts in docusaurus.config.ts

### Group B: Custom MDX Components (T-004 to T-007)
4. Build Callouts (Note/Tip/Warning/Info)
5. Build Steps + CardGroup
6. Build Accordion
7. Register all in MDXComponents.tsx

### Group C: Admonition Restyling (T-008)
8. CSS-only override for .theme-admonition variants

### Group D: Search (T-009)
9. Install and configure @easyops-cn/docusaurus-search-local

### Group E: Homepage (T-010 to T-012)
10. Strip docs/intro.md
11. Rework homepage with Loom metaphor + design tokens
12. Delete unused HomepageFeatures component

### Group F: Verification (T-013)
13. Build and visual QA

## Dependency Graph

```
T-001 (tokens) ─┬─> T-002 (CSS) ──> T-008 (admonitions)
                 ├─> T-003 (font)
                 ├─> T-005 (Callouts)──┐
                 ├─> T-006 (Steps+Cards)├──> T-004 (MDXComponents)
                 └─> T-007 (Accordion)─┘

T-009 (Search) ── independent
T-010 (intro.md) ── after T-002
T-011 (Homepage) ── after T-001
T-012 (Delete HomepageFeatures) ── independent
T-013 (Verification) ── after all
```

## NPM Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `@easyops-cn/docusaurus-search-local` | `^0.52.2` | Local search with Cmd+K |

## Files Created (10)
1. `src/css/tokens.css`
2. `src/theme/MDXComponents.tsx`
3. `src/components/Callouts/index.tsx` + `Callouts.module.css`
4. `src/components/Steps/index.tsx` + `Steps.module.css`
5. `src/components/CardGroup/index.tsx` + `CardGroup.module.css`
6. `src/components/Accordion/index.tsx` + `Accordion.module.css`

## Files Modified (4)
1. `src/css/custom.css` — tokenize, remove homepage CSS, add admonition + search styles
2. `docusaurus.config.ts` — Inter font, search theme, tagline update
3. `package.json` — add search dependency
4. `src/pages/index.tsx` — Loom messaging + design tokens

## Files Deleted (2)
1. `src/components/HomepageFeatures/index.tsx`
2. `src/components/HomepageFeatures/styles.module.css`
