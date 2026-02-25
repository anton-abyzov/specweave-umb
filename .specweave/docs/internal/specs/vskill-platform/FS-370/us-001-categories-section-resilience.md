---
id: US-001
feature: FS-370
title: Categories Section Resilience
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
external:
  github:
    issue: 1356
    url: https://github.com/anton-abyzov/specweave/issues/1356
---
# US-001: Categories Section Resilience

**Feature**: [FS-370](./FEATURE.md)

platform visitor
**I want** the "Skills by Category" section to always display category distribution
**So that** I can browse skills by category from the homepage

---

## Acceptance Criteria

- [x] **AC-US1-01**: `computeFullStats()` uses `Promise.allSettled` so individual query failures don't kill all results
- [x] **AC-US1-02**: `computeMinimalStats()` attempts category groupBy with try/catch instead of hard-coding `categories: []`
- [x] **AC-US1-03**: `computeMinimalStats()` attempts topStarRepos recovery with try/catch instead of hard-coding `topStarRepos: []`

---

## Implementation

**Increment**: [0370-fix-trending-categories](../../../../../increments/0370-fix-trending-categories/spec.md)

