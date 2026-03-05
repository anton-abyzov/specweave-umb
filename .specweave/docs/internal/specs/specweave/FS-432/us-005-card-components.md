---
id: US-005
feature: FS-432
title: Card Components
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-005: Card Components

**Feature**: [FS-432](./FEATURE.md)

developer populating content grids on the landing page
**I want** a set of card components (FeatureCard, ContentCard, StatCard, IntegrationCard, PricingCard)
**So that** content is presented in visually rich, consistent card layouts

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the FeatureCard component, when rendered with icon, title, and description props, then it displays a 64px icon area, bold title, and body text in a bordered card with hover shadow elevation
- [x] **AC-US5-02**: Given the ContentCard component, when rendered with image, tag, title, description, and link props, then it displays a card suitable for academy course listings with reading time and difficulty metadata
- [x] **AC-US5-03**: Given the StatCard component, when rendered with value, label, and optional suffix props, then it displays the value in a large display font with the label beneath, suitable for a stats section
- [x] **AC-US5-04**: Given the IntegrationCard component, when rendered with logo SVG, name, and description props, then it shows the integration logo at 48px, the integration name, and a short description in a card layout
- [x] **AC-US5-05**: Given any card component, when viewed in dark mode, then backgrounds use elevated surface tokens and borders use dark-mode border tokens

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

