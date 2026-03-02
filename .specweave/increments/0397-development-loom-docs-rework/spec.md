---
increment: 0397-development-loom-docs-rework
title: "Development Loom Documentation Site Rework — Phase 1"
type: feature
priority: P1
status: in-progress
created: 2026-03-02
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Development Loom Documentation Site Rework — Phase 1

## Overview

Rework spec-weave.com (Docusaurus 3.9.2) with a professional design system, "Development Loom" positioning (light touch — homepage/README only), Cmd+K search, styled MDX components, and refined indigo-purple palette. Phase 1 of 3.

**Site**: `repositories/anton-abyzov/specweave/docs-site/`

## User Stories

### US-001: Design Token System (P1)
**Project**: specweave

**As a** docs site visitor
**I want** a consistent, professional visual design
**So that** the site feels polished and trustworthy

**Acceptance Criteria**:
- [x] **AC-US1-01**: CSS token file defines refined indigo-purple palette (primary ~#6b58b8), semantic colors, neutrals, typography (Inter + JetBrains Mono), spacing (4px grid), radius, shadows
- [x] **AC-US1-02**: Dark mode has intentional dark palette, not just inverted values
- [x] **AC-US1-03**: Infima variables (`--ifm-*`) are mapped from design tokens
- [x] **AC-US1-04**: custom.css uses only `var(--sw-*)` tokens — no hard-coded colors
- [x] **AC-US1-05**: Inter font loaded via Google Fonts CDN with preconnect

---

### US-002: Custom MDX Components (P1)
**Project**: specweave

**As a** docs author
**I want** reusable styled components (Callouts, Steps, Cards, Accordions)
**So that** I can create rich, structured documentation pages

**Acceptance Criteria**:
- [x] **AC-US2-01**: `<Note>`, `<Tip>`, `<Warning>`, `<Info>` callout components with icon, optional title, left border accent, tinted background
- [x] **AC-US2-02**: `<Steps>`/`<Step title="">` with CSS counter numbering and vertical connector
- [x] **AC-US2-03**: `<CardGroup cols={2|3|4}>`/`<Card title="" href="" icon="">` responsive grid
- [x] **AC-US2-04**: `<Accordion>`/`<AccordionGroup>` with native details/summary, chevron animation
- [x] **AC-US2-05**: All components globally registered via `src/theme/MDXComponents.tsx`

---

### US-003: Admonition Restyling (P1)
**Project**: specweave

**As a** docs reader
**I want** refined admonition blocks (:::tip, :::warning, etc.)
**So that** callouts are visually clear without being jarring

**Acceptance Criteria**:
- [x] **AC-US3-01**: Admonitions have 3px left border, tinted backgrounds (5-8% opacity), design token colors, rounded corners
- [x] **AC-US3-02**: CSS-only override — no component swizzle — 29+ existing usages auto-update

---

### US-004: Cmd+K Search (P1)
**Project**: specweave

**As a** docs visitor
**I want** instant keyboard-triggered search (Cmd+K)
**So that** I can quickly find any page or concept

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `@easyops-cn/docusaurus-search-local` installed and configured
- [ ] **AC-US4-02**: Cmd+K opens search modal, indexes docs/ and blog/
- [ ] **AC-US4-03**: Search modal styled to match design system

---

### US-005: Homepage Loom Messaging (P1)
**Project**: specweave

**As a** first-time visitor
**I want** clear "Development Loom" positioning on the homepage
**So that** I immediately understand what SpecWeave does

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Hero has "The Development Loom" subtitle with updated tagline
- [ ] **AC-US5-02**: Homepage uses design tokens, not hard-coded colors
- [ ] **AC-US5-03**: Unused HomepageFeatures component deleted
- [ ] **AC-US5-04**: `docs/intro.md` stripped to simple landing with redirect

---

### US-006: Build Verification (P1)
**Project**: specweave

**As a** developer
**I want** the site to build without errors
**So that** all changes can be deployed

**Acceptance Criteria**:
- [ ] **AC-US6-01**: `npm run build` completes with zero errors
- [ ] **AC-US6-02**: Dark mode, search, admonitions, Inter font all functional

## Functional Requirements

### FR-001: Design Token Architecture
CSS custom properties in `src/css/tokens.css` with light/dark mode via `[data-theme='dark']`, imported by custom.css.

### FR-002: MDX Component Registration
Global registration via `src/theme/MDXComponents.tsx` extending `@theme-original/MDXComponents`.

### FR-003: Search Integration
`@easyops-cn/docusaurus-search-local` as a Docusaurus theme, configured with `searchBarShortcut: true`.

## Success Criteria

- Site builds cleanly (`npm run build` = 0 errors)
- Cmd+K search returns results from docs and blog
- Professional, consistent visual appearance matching Claude Code docs quality
- All 29+ existing admonition usages render with new styling
- Homepage communicates "Development Loom" positioning

## Out of Scope

- Sidebar restructuring (Phase 2)
- Content deduplication — Academy vs Learn (Phase 2)
- Progressive user levels — beginner/intermediate/advanced (Phase 3)
- Learning paths and missing fundamentals (Phase 3)
- `llms.txt` for AI discoverability (Phase 3)

## Dependencies

- Docusaurus 3.9.2 (already installed)
- React 19 (already installed)
- `@easyops-cn/docusaurus-search-local` (new dependency)
