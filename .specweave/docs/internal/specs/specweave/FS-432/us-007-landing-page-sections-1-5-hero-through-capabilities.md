---
id: US-007
feature: FS-432
title: Landing Page Sections 1-5 (Hero through Capabilities)
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-007: Landing Page Sections 1-5 (Hero through Capabilities)

**Feature**: [FS-432](./FEATURE.md)

first-time visitor arriving at verified-skill.com
**I want** a visually striking hero, trusted-by marquee, demo video, how-it-works timeline, and capabilities showcase
**So that** I immediately understand what SpecWeave does and why it matters

---

## Acceptance Criteria

- [x] **AC-US7-01**: Given the Hero section, when rendered, then it fills the full viewport height with a dark background, displays gradient text on the headline using WordAnimation, shows two CTAs (primary "Get Started" and secondary "Watch Demo"), and includes animated pill badges
- [x] **AC-US7-02**: Given the Trusted By section, when rendered, then it displays a horizontal logo marquee with CSS scroll animation (no JS) showing technology and community logos with seamless infinite loop
- [x] **AC-US7-03**: Given the Demo Video section, when rendered, then it shows the Remotion video inside a browser chrome frame with a glow shadow, using lazy loading with a poster frame and play-on-visible via IntersectionObserver
- [x] **AC-US7-04**: Given the How It Works section, when rendered, then it displays a horizontal timeline with 3 steps (64px numbered circles), each showing a command, title, description, and a CodeBlock example, connected by a progress line
- [x] **AC-US7-05**: Given the Capabilities section, when rendered, then it uses an alternating left-right layout showing 6 features with icons, titles, descriptions, and optional code snippets, each wrapped in AnimateOnScroll

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

