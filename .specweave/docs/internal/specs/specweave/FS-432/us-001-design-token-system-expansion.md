---
id: US-001
feature: FS-432
title: Design Token System Expansion
status: complete
priority: P2
created: 2026-03-05
project: specweave
external:
  github:
    issue: 1495
    url: "https://github.com/anton-abyzov/specweave/issues/1495"
---
# US-001: Design Token System Expansion

**Feature**: [FS-432](./FEATURE.md)

developer working on the SpecWeave website
**I want** an expanded design token system with 350+ CSS custom properties covering colors, typography, spacing, shadows, motion, and glass morphism
**So that** all components share a consistent, maintainable visual language

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the tokens.css file, when inspected, then it contains organized token sections for: colors (primary 50-900, semantic, neutral, surface, text, border), typography (font families, fluid sizes, weights, line heights, letter spacing), spacing (4px grid 0-96px+), border radius, shadows (xs through glow plus elevation and glass morphism shadows), transitions (fast/base/slow/spring), and motion (duration, easing curves, stagger delays)
- [x] **AC-US1-02**: Given a dark mode toggle, when the user switches themes, then all surface, text, border, and shadow tokens update via [data-theme='dark'] overrides without flash of unstyled content
- [x] **AC-US1-03**: Given the token file, when the Infima mapping section is reviewed, then all --ifm-* variables correctly reference --sw-* tokens so Docusaurus default components inherit the design system
- [x] **AC-US1-04**: Given the token file, when counted, then there are at least 350 unique CSS custom properties defined across light and dark modes combined

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

