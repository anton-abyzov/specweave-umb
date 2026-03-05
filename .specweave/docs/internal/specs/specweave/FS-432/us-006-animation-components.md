---
id: US-006
feature: FS-432
title: Animation Components
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-006: Animation Components

**Feature**: [FS-432](./FEATURE.md)

site visitor scrolling the landing page
**I want** smooth scroll-triggered animations and number counters
**So that** the page feels polished and professional without excessive loading weight

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given the AnimateOnScroll component wrapping a child element, when the element enters the viewport (IntersectionObserver threshold 0.1), then it transitions from opacity 0 / translateY(24px) to opacity 1 / translateY(0) over 600ms with an ease-out curve
- [x] **AC-US6-02**: Given the WordAnimation component, when rendered with a text string, then it reveals words one at a time with staggered delays (Anthropic-style word-by-word), completing the full reveal within 2 seconds
- [x] **AC-US6-03**: Given the CountUp component, when its container scrolls into view, then it animates a number from 0 to the target value over 2 seconds using an ease-out interpolation
- [x] **AC-US6-04**: Given any animation component, when the user has prefers-reduced-motion enabled, then all animations are disabled and content displays immediately at its final state
- [x] **AC-US6-05**: Given SSR (Docusaurus build), when the page is server-rendered, then all animated content is visible by default (opacity: 1, no transform) and animations are only applied after client-side hydration via useEffect

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

