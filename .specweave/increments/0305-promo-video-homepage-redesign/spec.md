# Spec: Promotional Video & Homepage Redesign

## Overview

Create a world-class promotional video (~45s looping) and redesign the spec-weave.com (verified-skill.com) homepage with feature sections, nanobanana-generated images, and Apple keynote-level production quality.

---

### US-001: Promotional Video Production with Remotion
**Project**: vskill-platform

**As a** visitor landing on spec-weave.com
**I want** to see a polished, looping promotional video at the top of the homepage
**So that** I immediately understand SpecWeave's value proposition and workflow

**Acceptance Criteria**:
- [x] **AC-US1-01**: Video is ~45s long, loops seamlessly, autoplays muted with play/pause control
- [x] **AC-US1-02**: Video showcases increment creation workflow (terminal typing animation)
- [x] **AC-US1-03**: Video showcases team-lead multi-agent orchestration with nested expert agents
- [x] **AC-US1-04**: Video showcases verified skills with tier badges (Scanned/Verified/Certified)
- [x] **AC-US1-05**: Video showcases documentation generation and code writing
- [x] **AC-US1-06**: Big, readable typography (Geist Mono) with smooth transitions between scenes
- [x] **AC-US1-07**: Agent icons displayed for Claude Code, Codex, OpenClaw, Cursor, etc.
- [x] **AC-US1-08**: vskill CLI command visualization (install, scan, init)
- [ ] **AC-US1-09**: Energetic background music or ambient soundtrack (royalty-free)
- [x] **AC-US1-10**: Video built with Remotion (React-based) for maintainability and iteration
- [x] **AC-US1-11**: Video renders to MP4 (H.264) at 1920x1080, 30fps, and WebM fallback
- [x] **AC-US1-12**: Slick scene transitions (fade, slide, scale) with easing curves

---

### US-002: Homepage Hero Section with Video Player
**Project**: vskill-platform

**As a** visitor
**I want** the homepage hero to feature the video prominently with a dark cinematic backdrop
**So that** the first impression is premium and engaging

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Full-width hero section with video player, max-width 1080px centered
- [ ] **AC-US2-02**: Video autoplays muted, loops, with subtle play/pause overlay toggle
- [ ] **AC-US2-03**: Below video: tagline "Spec-Driven Development for AI Agents" in large Geist Mono
- [ ] **AC-US2-04**: Two CTA buttons: "Browse Skills >>" and "npx vskill init" (copy-to-clipboard)
- [ ] **AC-US2-05**: Hero section uses dark gradient background (--bg to transparent) with subtle grain texture
- [ ] **AC-US2-06**: Responsive: video scales down on mobile, stacks vertically on narrow screens

---

### US-003: Feature Sections Redesign
**Project**: vskill-platform

**As a** visitor scrolling below the video
**I want** clearly organized feature sections explaining SpecWeave's value
**So that** I understand the product capabilities before browsing skills

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Section 1 "Spec-First Development" — increment workflow visualization with animated terminal
- [ ] **AC-US3-02**: Section 2 "Multi-Agent Teams" — diagram showing team-lead spawning domain experts
- [ ] **AC-US3-03**: Section 3 "Security-Verified Skills" — three-tier verification visual with tier badges
- [ ] **AC-US3-04**: Section 4 "Works With 39 Agents" — agent grid with branded icons/colors
- [ ] **AC-US3-05**: Each section alternates layout (text-left/visual-right, then reversed)
- [ ] **AC-US3-06**: Sections use scroll-triggered fade-in animations (IntersectionObserver)
- [ ] **AC-US3-07**: Sections have nanobanana-generated illustration placeholders (256x256 or larger)
- [ ] **AC-US3-08**: Market dashboard (stars, installs, npm, quality score) preserved below features

---

### US-004: Nanobanana Image Generation Placeholders
**Project**: vskill-platform

**As a** developer maintaining the homepage
**I want** clearly marked image placeholder slots with dimensions and descriptions
**So that** nanobanana-generated images can be dropped in without code changes

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Each feature section has an `<img>` tag with `data-nanobanana-prompt` attribute describing the desired image
- [ ] **AC-US4-02**: Placeholder images use SVG gradient placeholders with dimensions overlay
- [ ] **AC-US4-03**: At minimum 4 placeholder slots: spec workflow, multi-agent, security shield, agent ecosystem
- [ ] **AC-US4-04**: Images are in `/public/images/homepage/` directory with descriptive filenames

---

### US-005: Existing Dashboard & Trending Integration
**Project**: vskill-platform

**As a** returning user
**I want** the market dashboard, trending skills, categories, and verification explanation preserved
**So that** I don't lose access to the data-driven content I rely on

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Market dashboard (MetricCard grid) appears after the feature sections
- [ ] **AC-US5-02**: Trending skills table preserved with current functionality
- [ ] **AC-US5-03**: Category navigator + search preserved
- [ ] **AC-US5-04**: "How verification works" and "Works with N agents" sections preserved (may be restyled)
- [ ] **AC-US5-05**: No regression in server-side data fetching (getSkills, getSkillCategories)

## Out of Scope

- Actual nanobanana image generation (placeholders only — images will be generated separately)
- Background music licensing (use silence or placeholder; note royalty-free source in code comments)
- Video hosting/CDN setup (self-hosted in /public for now)
- Mobile-native video player customization beyond basic responsive behavior

## Dependencies

- Remotion library for video production
- Existing vskill-platform codebase (Next.js 15, Cloudflare Workers)
- Agent branding constants from `src/lib/agent-branding.ts`
