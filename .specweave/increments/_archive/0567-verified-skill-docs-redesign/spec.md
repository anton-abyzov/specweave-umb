---
increment: 0567-verified-skill-docs-redesign
title: Verified Skill Docs Redesign + Video Learning Section
type: feature
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Verified Skill Docs Redesign + Video Learning Section

## Problem Statement

The verified-skill.com docs have readability issues in light mode (low-contrast card backgrounds, code blocks, and faint text), use system fonts instead of the product typeface, and lack a video learning section. The information architecture does not follow Diataxis principles, making it hard for users to find tutorials vs. reference material. The SpecWeave docs-site (Docusaurus) sidebar has grown to 9+ categories without a clear hierarchy. Users need short-form video content to learn vskill and SpecWeave workflows, but no video infrastructure exists.

## Goals

- Achieve WCAG AA contrast compliance across all light-mode doc surfaces
- Establish Geist Sans as the prose typeface for consistent brand identity
- Launch /learn as a video hub with tabbed navigation, thumbnail grid, and email capture for upcoming content
- Restructure both vskill-platform and specweave docs-site navigation using Diataxis principles inspired by Claude Code's docs hierarchy
- Enable contextual video integration so doc pages surface related videos and vice versa
- Preserve all existing URLs during IA restructure (zero broken links)

## User Stories

### US-001: Light-Mode Readability Fix (P0)
**Project**: vskill-platform
**As a** docs reader in light mode
**I want** sufficient contrast on cards, code blocks, and secondary text
**So that** I can read documentation comfortably without straining

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given light mode is active, when a doc page renders, then `--card-bg` produces a contrast ratio of at least 4.5:1 for body text against the card background
- [x] **AC-US1-02**: Given light mode is active, when a code block renders, then `--bg-code` has a contrast ratio of at least 4.5:1 between code text and its background
- [x] **AC-US1-03**: Given light mode is active, when secondary text renders using `--text-faint`, then the contrast ratio against its parent background is at least 4.5:1
- [x] **AC-US1-04**: Given the globals.css file, when the light-mode color variables are updated, then dark mode variables remain unchanged

---

### US-002: Prose Typography Update (P1)
**Project**: vskill-platform
**As a** docs reader
**I want** doc prose rendered in Geist Sans at a comfortable reading size
**So that** long-form content is easy to read and visually consistent with the product brand

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a doc page, when prose content renders, then the font-family resolves to "Geist Sans" with appropriate fallbacks
- [x] **AC-US2-02**: Given a doc page, when prose paragraphs render, then font-size is 0.9375rem (15px at default root)
- [x] **AC-US2-03**: Given a doc page, when code blocks render, then they retain the existing monospace font (not Geist Sans)

---

### US-003: /learn Video Hub Page (P1)
**Project**: vskill-platform
**As a** new user exploring vskill or SpecWeave
**I want** a /learn page with categorized short video tutorials
**So that** I can quickly learn key workflows through visual content

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the /learn route, when the page loads, then three filter tabs render: "vskill", "SpecWeave", "Workflows"
- [x] **AC-US3-02**: Given a tab is selected, when the grid renders, then only VideoCard components matching that category are displayed
- [x] **AC-US3-03**: Given a VideoCard, when it renders, then it displays a static WebP thumbnail, video title, duration badge, and difficulty indicator
- [x] **AC-US3-04**: Given the /learn page initial load, when no video has been clicked, then the JavaScript bundle does not include the VideoPlayer component (loaded via next/dynamic on click)
- [x] **AC-US3-05**: Given the /learn page, when the initial HTML and CSS load completes, then the transferred payload is under 200KB (excluding images)

---

### US-004: "Coming Soon" Cards with Email Capture (P1)
**Project**: vskill-platform
**As a** user interested in an unreleased video
**I want** to enter my email on a "Coming Soon" card to get notified when it launches
**So that** I do not have to repeatedly check back for new content

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a video entry in the data array with `status: "coming-soon"`, when the VideoCard renders, then it displays a "Coming Soon" overlay instead of a play button
- [x] **AC-US4-02**: Given a "Coming Soon" card, when the user clicks "Get Notified", then an email input and submit button appear inline on the card
- [x] **AC-US4-03**: Given a valid email submission, when the form is submitted, then a row is inserted into the `video_notifications` table with the email and the video slug
- [x] **AC-US4-04**: Given a valid email submission, when the record is created, then a double opt-in confirmation email is sent via SendGrid
- [x] **AC-US4-05**: Given an invalid or empty email, when the form is submitted, then a client-side validation error is shown and no API call is made

---

### US-005: Render Initial Video Library (P1)
**Project**: vskill-platform
**As a** user on the /learn page
**I want** to watch the first set of tutorial videos rendered from Remotion scenes
**So that** I can learn vskill and SpecWeave workflows visually

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the video data array in `src/lib/learn/video-data.ts`, when the /learn page renders, then at least 3 video entries are present with `status: "published"`
- [x] **AC-US5-02**: Given a published VideoCard, when the user clicks the play overlay, then the VideoPlayer component loads via next/dynamic and begins playback
- [x] **AC-US5-03**: Given a video file fails to load, when the player encounters an error, then the card displays the static thumbnail with "Video unavailable -- coming soon" text
- [x] **AC-US5-04**: Given the video source files, when served from /public/video/learn/, then each video file is under 15MB
- [x] **AC-US5-05**: Given the total /public/video/learn/ directory, when measured, then the combined size is under 200MB

---

### US-006: vskill-platform Docs Navigation Restructure (P1)
**Project**: vskill-platform
**As a** docs reader on verified-skill.com
**I want** the sidebar navigation organized by Diataxis categories with Claude Code-inspired hierarchy
**So that** I can find tutorials, how-to guides, explanations, and reference material intuitively

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the docs sidebar, when it renders, then top-level groups follow the hierarchy: Overview, Quickstart, Core Concepts, Skills, Workflows, Integrations, Reference, FAQ
- [x] **AC-US6-02**: Given any existing doc page URL, when visited after the restructure, then it returns HTTP 200 (no redirects needed, URLs preserved)
- [x] **AC-US6-03**: Given a doc page, when the sidebar renders, then the current page is highlighted and its parent group is expanded
- [x] **AC-US6-04**: Given any doc page, when it renders, then a "Related resources" section appears at the bottom with links to related pages

---

### US-007: SpecWeave Docs-Site Navigation Simplification (P1)
**Project**: specweave
**As a** SpecWeave user browsing the docs-site
**I want** the top menu and sidebar simplified from 9+ categories to a clean Claude Code-inspired hierarchy
**So that** I can navigate between overview, concepts, workflows, and reference without cognitive overload

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the Docusaurus sidebar config, when the docs-site renders, then the primary sidebar groups are: Overview, Quickstart, Core Concepts, Skills, Workflows, Integrations, Reference, FAQ
- [x] **AC-US7-02**: Given the current separate sidebars (Academy, Skills, Enterprise, Reference), when consolidated, then Academy appears as a top-nav item "Learn" and Skills, Enterprise, Reference are folded into the primary sidebar hierarchy
- [x] **AC-US7-03**: Given any existing docs-site page URL, when visited after the restructure, then it returns HTTP 200 (URLs preserved, zero redirects)
- [x] **AC-US7-04**: Given the top navigation menu, when rendered, then items are: Docs, Learn, Enterprise, Blog (maximum 5 items)

---

### US-008: Contextual Video Sidebar Widget (P2)
**Project**: vskill-platform
**As a** docs reader on a concept page
**I want** to see related video tutorials in a sidebar widget
**So that** I can switch to visual learning when reading is insufficient

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given a doc page with entries in the video-data relatedDocs array matching its slug, when the page renders, then a "Related Videos" sidebar widget displays those video thumbnails
- [x] **AC-US8-02**: Given a related video thumbnail in the sidebar, when the user clicks it, then they navigate to /learn with that video auto-playing
- [x] **AC-US8-03**: Given a doc page with no matching related videos, when the sidebar renders, then the "Related Videos" widget is not rendered (no empty state)
- [x] **AC-US8-04**: Given a video that fails to load its thumbnail, when the sidebar widget renders, then it shows a text-only fallback link with the video title

---

### US-009: Cross-Repo Video Embedding in Docusaurus (P2)
**Project**: specweave
**As a** SpecWeave docs-site reader
**I want** embedded video players on relevant Docusaurus doc pages referencing verified-skill.com videos
**So that** I can watch tutorials without leaving the docs context

**Acceptance Criteria**:
- [x] **AC-US9-01**: Given a Docusaurus MDX page, when a `<VideoEmbed slug="video-slug" />` component is used, then it renders a video player sourcing from `https://verified-skill.com/video/learn/{slug}.mp4`
- [x] **AC-US9-02**: Given the VideoEmbed component, when the video has not been clicked, then it displays a static WebP thumbnail with a play overlay (no autoplay)
- [x] **AC-US9-03**: Given the VideoEmbed video source is cross-origin, when the `<video>` tag loads, then no CORS errors occur (direct video tag, not fetch)
- [x] **AC-US9-04**: Given a VideoEmbed where the source video is unavailable, when the component renders, then it shows the text "Video unavailable -- coming soon" with the thumbnail as background

---

### US-010: Video-Doc-Spec Depth Layers (P2)
**Project**: vskill-platform
**As a** user who just watched a tutorial video
**I want** clear navigation from the video to its related doc page and from that doc page to its spec brief
**So that** I can progressively deepen my understanding from visual overview to detailed specification

**Acceptance Criteria**:
- [x] **AC-US10-01**: Given a VideoCard in /learn, when the video ends or the user clicks "Read More", then a link navigates to the related doc page
- [x] **AC-US10-02**: Given a doc page linked from a video, when it renders, then a "View Spec Brief" link is present if a spec brief exists for that topic
- [x] **AC-US10-03**: Given the depth layer navigation, when a user follows Video -> Doc -> Spec Brief, then each page includes a breadcrumb or back-link to the previous layer
- [x] **AC-US10-04**: Given the video-data.ts entries, when a video has `relatedDocSlug` and `specBriefSlug` fields populated, then both forward links render on the VideoCard component

## Out of Scope

- Adaptive bitrate streaming (HLS/DASH) -- not needed for 30-90s clips
- Video CMS or admin panel -- static TypeScript data array is sufficient
- Cloudflare R2 migration -- deferred until video library exceeds 200MB
- Full Remotion rendering pipeline automation -- manual render and commit for Phase 2
- Dark mode changes -- this increment only fixes light-mode readability
- SEO audit or sitemap restructure beyond sidebar/nav changes
- User accounts or video watch history
- Comments or community features on /learn
- Mobile app video playback
- Docusaurus version upgrade

## Non-Functional Requirements

- **Performance**: /learn page initial load (HTML + CSS + JS, excluding images) under 200KB; VideoPlayer lazy-loaded on interaction only
- **Accessibility**: All light-mode doc surfaces meet WCAG AA contrast (4.5:1 minimum); video player supports keyboard controls; thumbnail alt text required on all VideoCards
- **Security**: Email capture endpoint validates input server-side; SendGrid API key stored in environment variable, never committed; double opt-in prevents spam abuse
- **Compatibility**: Video playback supported in Chrome, Firefox, Safari, Edge (latest 2 versions); `<video>` tag with MP4 H.264 for universal support; WebP thumbnails with JPEG fallback for Safari < 14
- **Bundle Size**: No new runtime dependencies added to the main bundle for /learn; VideoPlayer loaded via next/dynamic

## Edge Cases

- Video file missing from /public/video/learn/: VideoCard shows thumbnail with "Video unavailable -- coming soon" text, card remains visible in grid
- Empty video-data.ts array for a tab category: Tab still renders, grid shows "No videos yet -- check back soon" message
- User submits same email twice for same video notification: Database upserts (no duplicate rows), UI shows "You're already subscribed" confirmation
- Browser does not support WebP thumbnails: `<picture>` element falls back to JPEG source
- /learn page accessed with JavaScript disabled: Static thumbnails and titles render via SSR; play buttons are non-functional but grid layout is intact
- Docusaurus VideoEmbed referencing a video slug that does not exist: Component renders fallback text, does not break the MDX page
- Sidebar nav restructure with deeply nested current page: All ancestor groups expand to reveal the active page

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Geist Sans font not loading (CDN failure) | 0.1 | 4 | 0.4 | CSS fallback stack: system-ui, -apple-system, sans-serif |
| Video files bloat the Git repo beyond practical limits | 0.3 | 7 | 2.1 | Monitor /public/video/learn/ size; migrate to R2 at 200MB threshold |
| IA restructure accidentally breaks deep-linked doc pages | 0.2 | 9 | 1.8 | URL preservation is a hard constraint; sidebar-only restructure with no file moves; automated link checker in CI |
| SendGrid double opt-in emails land in spam | 0.3 | 5 | 1.5 | Verify sender domain (SPF/DKIM); test with major providers before launch |
| Cross-origin video tag blocked by corporate firewalls | 0.2 | 4 | 0.8 | Fallback thumbnail with link to verified-skill.com/learn |

## Technical Notes

### Dependencies
- @sendgrid/mail (already in vskill-platform package.json)
- Prisma + Neon PostgreSQL (existing stack) for video_notifications table
- Geist Sans font (next/font or CDN)
- Remotion (existing) for rendering initial video set
- Docusaurus (existing specweave docs-site)

### Constraints
- Videos served from /public/video/learn/ until 200MB threshold, then migrate to Cloudflare R2
- Video data is a static TypeScript array (`src/lib/learn/video-data.ts`), not a database or CMS
- Both repos reference videos by absolute URL to verified-skill.com/video/learn/
- No feature flags -- each phase ships directly to production
- All existing doc page URLs must return HTTP 200 post-restructure

### Architecture Decisions
- Static WebP thumbnails generated from Remotion stills (not video poster frames)
- VideoPlayer loaded via next/dynamic to keep /learn initial bundle under 200KB
- Docusaurus VideoEmbed uses `<video src>` (direct tag, not fetch) to avoid CORS configuration
- Sidebar-only IA restructure (grouping pages under new categories) preserves all file paths and URLs
- Video content plan: 5 vskill videos + 5 SpecWeave videos, 30s-2min each

## Success Metrics

- WCAG AA compliance: 100% of light-mode doc surfaces pass 4.5:1 contrast ratio audit
- /learn page Lighthouse performance score >= 90
- /learn initial page load (HTML + CSS + JS) under 200KB
- Zero broken links after IA restructure (verified by automated link checker)
- Email capture: 50+ notification signups within first 30 days of launch
- Video engagement: average watch-through rate >= 60% across published videos
