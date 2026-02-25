---
id: US-002
feature: FS-370
title: Meaningful Trending Momentum
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
---
# US-002: Meaningful Trending Momentum

**Feature**: [FS-370](./FEATURE.md)

platform visitor
**I want** trending momentum arrows to show meaningful deltas across all popularity ranges
**So that** I can see which skills are gaining traction vs. stable

---

## Acceptance Criteria

- [x] **AC-US2-01**: Trending formula uses logarithmic scaling (LN) instead of linear multipliers to prevent cap saturation
- [x] **AC-US2-02**: Skills with 95k+ stars no longer show identical 7d/30d scores (both pinned at 100)
- [x] **AC-US2-03**: MomentumArrow threshold adjusted to show meaningful deltas at log scale
- [x] **AC-US2-04**: Trending formula extracted to shared module (DRY — single source of truth)
- [x] **AC-US2-05**: Both enrichment.ts and admin/enrich/route.ts use the shared formula

---

## Implementation

**Increment**: [0370-fix-trending-categories](../../../../../increments/0370-fix-trending-categories/spec.md)

