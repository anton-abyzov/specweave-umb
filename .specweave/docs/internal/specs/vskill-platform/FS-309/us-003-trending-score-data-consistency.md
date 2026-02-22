---
id: US-003
feature: FS-309
title: Trending Score Data Consistency
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1260
    url: https://github.com/anton-abyzov/specweave/issues/1260
---
# US-003: Trending Score Data Consistency

**Feature**: [FS-309](./FEATURE.md)

developer maintaining the seed data
**I want** trendingScore values to have a documented scale and produce meaningful momentum indicators
**So that** the trending section displays useful differentiation between skills

---

## Acceptance Criteria

- [x] **AC-US3-01**: The `SkillData` type or seed-data file documents the trendingScore scale (0-100, what the score represents)
- [x] **AC-US3-02**: Seed data trendingScore7d and trendingScore30d values produce visually distinguishable momentum arrows (i.e., non-trivial deltas for top trending skills)
- [x] **AC-US3-03**: A code comment or JSDoc on the trendingScore fields explains the scoring methodology
- [x] **AC-US3-04**: The MomentumArrow component renders correctly for the full range of possible delta values

---

## Implementation

**Increment**: [0309-homepage-improvements](../../../../../increments/0309-homepage-improvements/spec.md)

