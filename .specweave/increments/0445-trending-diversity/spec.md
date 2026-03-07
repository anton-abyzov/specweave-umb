---
increment: 0445-trending-diversity
title: "Trending Skills Diversity: Cap Per-Repo + Show 10"
type: feature
priority: P1
status: active
created: 2026-03-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Trending Skills Diversity: Cap Per-Repo + Show 10

## Problem Statement

The trending skills section on the homepage can be dominated by multiple skills from the same repository, reducing diversity and making the list less useful for discovery. Additionally, the list was limited to 8 items, which doesn't surface enough variety.

## Goals

- Cap the maximum number of skills from the same repo to 3 in trending results
- Increase the trending list size from 8 to 10 for broader visibility
- Ensure the diversity filter preserves momentum-based ordering

## User Stories

### US-001: Per-repo cap in trending results (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** the trending section to show at most 3 skills from the same repository
**So that** I discover a diverse set of trending tools rather than seeing one repo dominate

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a `diversifyTrending()` function in `stats-compute.ts`, when called with `maxPerRepo=3`, then no more than 3 skills from the same `repoUrl` appear in the result
- [x] **AC-US1-02**: Given skills with empty `repoUrl`, when diversity filtering runs, then the `author` field is used as the grouping key instead
- [x] **AC-US1-03**: Given the diversity filter, when skills are processed, then the original input order (momentum-sorted) is preserved for non-filtered entries

---

### US-002: Increase trending list to 10 items (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** the trending section to show 10 skills instead of 8
**So that** I see a broader range of trending tools

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the `diversifyTrending()` function, when called with `limit=10`, then the result contains at most 10 entries
- [x] **AC-US2-02**: Given both `computeFullStats()` and `computeMinimalStats()`, when they compute trending skills, then both call `diversifyTrending(raw, 3, 10)` consistently
- [x] **AC-US2-03**: Given the `TrendingSkills.tsx` component, when it renders trending data, then it displays all entries returned by the stats (no hardcoded UI limit)

## Out of Scope

- Changing the trending score formula (handled by `trending-formula.ts`)
- Modifying the cron job schedule or KV caching strategy
- Adding UI pagination or "show more" to the trending section

## Technical Notes

- `diversifyTrending()` is a pure function in `src/lib/stats-compute.ts` — easy to unit test
- Called in both `computeFullStats()` (Promise.allSettled path) and `computeMinimalStats()` (fallback path)
- DB query fetches top 50 by `trendingScore7d`, then re-sorts by momentum (7d - 30d delta) before diversity filtering
- `TrendingSkills.tsx` renders `stats.trendingSkills` array directly with no hardcoded cap
