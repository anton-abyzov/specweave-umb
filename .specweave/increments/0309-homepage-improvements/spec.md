---
increment: 0309-homepage-improvements
title: "Homepage improvements: CLI examples, category chart fix, trending data consistency"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Homepage Improvements

## Overview

Three focused improvements to the vskill-platform homepage:
1. Replace the generic `$ npx vskill ...` placeholder with real `vskill install` and `vskill find` command examples
2. Fix the category distribution chart to use total skill counts (seed + DB) instead of only the 118 seed skills
3. Make trendingScore data self-documenting with a clear scale definition and ensure seed data values produce meaningful momentum deltas

## User Stories

### US-001: CLI Command Examples on Homepage (P1)
**Project**: vskill-platform

**As a** developer visiting the homepage
**I want** to see real vskill install and find command examples
**So that** I can immediately understand how to use the CLI without reading separate docs

**Acceptance Criteria**:
- [x] **AC-US1-01**: The hero section shows at least one concrete `vskill install` example (e.g., `$ npx vskill install anthropics/skills`)
- [x] **AC-US1-02**: The hero section shows at least one concrete `vskill find` example (e.g., `$ npx vskill find security`)
- [x] **AC-US1-03**: The examples use real skill names/repos that exist in the seed data
- [x] **AC-US1-04**: The `or bunx / pnpx / yarn dlx` hint is preserved

---

### US-002: Fix Category Chart Data Inconsistency (P1)
**Project**: vskill-platform

**As a** visitor viewing the "Skills by Category" chart
**I want** the chart to reflect the total number of skills in the registry
**So that** the chart counts match the total skills number shown in the hero

**Acceptance Criteria**:
- [x] **AC-US2-01**: `getSkillCategories()` returns counts from seed + Prisma DB (not seed-only when DB is available)
- [x] **AC-US2-02**: Category chart sum equals the total skills count shown in the hero section
- [x] **AC-US2-03**: When Prisma is unavailable, fallback behavior (seed + KV) still works correctly
- [x] **AC-US2-04**: Existing tests pass and new tests cover the DB-merged category counts

---

### US-003: Trending Score Data Consistency (P2)
**Project**: vskill-platform

**As a** developer maintaining the seed data
**I want** trendingScore values to have a documented scale and produce meaningful momentum indicators
**So that** the trending section displays useful differentiation between skills

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `SkillData` type or seed-data file documents the trendingScore scale (0-100, what the score represents)
- [x] **AC-US3-02**: Seed data trendingScore7d and trendingScore30d values produce visually distinguishable momentum arrows (i.e., non-trivial deltas for top trending skills)
- [x] **AC-US3-03**: A code comment or JSDoc on the trendingScore fields explains the scoring methodology
- [x] **AC-US3-04**: The MomentumArrow component renders correctly for the full range of possible delta values

## Functional Requirements

### FR-001: CLI Examples in Hero
Replace `$ npx vskill ...` with two concrete command examples that demonstrate install and find workflows. Use real repo URLs and search terms from existing seed data.

### FR-002: Category Chart Accuracy
The `getSkillCategories()` function already attempts to merge Prisma counts. The issue is that the chart title says "Skills by Category" but only shows seed counts when DB skills exist. Ensure the chart data source is consistent with the total skills count.

### FR-003: Trending Score Documentation
Add JSDoc comments to `trendingScore7d` and `trendingScore30d` in the `SkillData` interface explaining the 0-100 scale and that 7d represents recent momentum while 30d is the baseline. Review seed data to ensure top-8 trending skills have meaningful 7d vs 30d deltas.

## Success Criteria

- Homepage CLI examples match real vskill commands (install/find)
- Category chart total matches hero skill count (no off-by-N discrepancy)
- Trending scores are documented inline and produce visible momentum arrows

## Out of Scope

- Changing the trending score algorithm or fetcher
- Adding new categories
- Redesigning the hero section layout
- Changing the vskill CLI commands themselves

## Dependencies

- vskill CLI commands `install` (alias `add`) and `find` (alias `search`) already exist
- Prisma DB integration for `getSkillCategories()` already exists (just needs validation)
