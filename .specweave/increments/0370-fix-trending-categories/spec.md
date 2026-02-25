---
increment: 0370-fix-trending-categories
title: "Fix Homepage Categories & Trending Momentum"
type: bug
priority: P1
status: in-progress
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix Homepage Categories & Trending Momentum

## Overview

Two bugs on the vskill-platform homepage: (1) "Skills by Category" section renders empty due to fragile stats computation fallback, (2) trending momentum arrows show 0.0 for most skills because the linear scoring formula caps at 100, making deltas meaningless. Additionally, the trending formula is duplicated in two files (DRY violation).

## User Stories

### US-001: Categories Section Resilience (P1)
**Project**: vskill-platform

**As a** platform visitor
**I want** the "Skills by Category" section to always display category distribution
**So that** I can browse skills by category from the homepage

**Acceptance Criteria**:
- [x] **AC-US1-01**: `computeFullStats()` uses `Promise.allSettled` so individual query failures don't kill all results
- [x] **AC-US1-02**: `computeMinimalStats()` attempts category groupBy with try/catch instead of hard-coding `categories: []`
- [x] **AC-US1-03**: `computeMinimalStats()` attempts topStarRepos recovery with try/catch instead of hard-coding `topStarRepos: []`

---

### US-002: Meaningful Trending Momentum (P1)
**Project**: vskill-platform

**As a** platform visitor
**I want** trending momentum arrows to show meaningful deltas across all popularity ranges
**So that** I can see which skills are gaining traction vs. stable

**Acceptance Criteria**:
- [x] **AC-US2-01**: Trending formula uses logarithmic scaling (LN) instead of linear multipliers to prevent cap saturation
- [x] **AC-US2-02**: Skills with 95k+ stars no longer show identical 7d/30d scores (both pinned at 100)
- [x] **AC-US2-03**: MomentumArrow threshold adjusted to show meaningful deltas at log scale
- [x] **AC-US2-04**: Trending formula extracted to shared module (DRY — single source of truth)
- [x] **AC-US2-05**: Both enrichment.ts and admin/enrich/route.ts use the shared formula

## Out of Scope

- Historical snapshot table for true velocity-based trending (future increment)
- Category auto-assignment improvements
- Filtering deprecated skills from category counts
