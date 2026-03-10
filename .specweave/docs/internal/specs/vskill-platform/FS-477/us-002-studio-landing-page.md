---
id: US-002
feature: FS-477
title: "Studio Landing Page"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill author."
project: vskill-platform
---

# US-002: Studio Landing Page

**Feature**: [FS-477](./FEATURE.md)

**As a** skill author
**I want** a dedicated `/studio` page explaining Skill Studio features
**So that** I can learn about BDD testing, benchmarking, and local development before installing

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given a visitor navigating to `/studio`, when the page loads, then they see a hero section with "Skill Studio" heading, the tagline "Test skills with BDD assertions, run benchmarks against any LLM, and track quality over time", and a CLI command (`npx vskill studio`) with a copy-to-clipboard button
- [ ] **AC-US2-02**: Given the `/studio` page, when scrolling past the hero, then a video demo section renders using the shared VideoPlayer component with `/video/skill-studio.mp4` and `/video/skill-studio.webm` sources (lazy-loaded)
- [ ] **AC-US2-03**: Given the `/studio` page, when scrolling to the features section, then 4 feature cards are displayed: "BDD Tests" (green), "A/B Compare" (blue), "Any Model" (purple), "100% Local" (cyan) -- each with a title, description, and accent color
- [ ] **AC-US2-04**: Given the `/studio` page, when scrolling to the getting-started section, then 3 numbered steps are shown: (1) install vskill, (2) init a test suite, (3) run studio -- each with a CLI command
- [ ] **AC-US2-05**: Given the `/studio` page, when inspecting the HTML head, then it contains page-specific `<title>`, `<meta name="description">`, Open Graph (`og:title`, `og:description`, `og:url`), and Twitter Card (`twitter:title`, `twitter:description`) metadata

---

## Implementation

**Increment**: [0477-homepage-studio-nav-redesign](../../../../../increments/0477-homepage-studio-nav-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
