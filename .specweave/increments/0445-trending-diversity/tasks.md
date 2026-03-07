---
increment: 0445-trending-diversity
title: "Trending Skills Diversity: Cap Per-Repo + Show 10"
generated_by: sw:test-aware-planner
by_user_story:
  US-001:
    tasks: [T-001, T-002]
    acs: [AC-US1-01, AC-US1-02, AC-US1-03]
  US-002:
    tasks: [T-003, T-004]
    acs: [AC-US2-01, AC-US2-02, AC-US2-03]
total_tasks: 4
completed_tasks: 4
---

# Tasks: Trending Skills Diversity: Cap Per-Repo + Show 10

## User Story: US-001 - Per-repo cap in trending results

**Project**: vskill-platform
**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 2 total, 2 completed

---

### T-001: Implement diversifyTrending pure function

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a list of 5 skills where 4 are from the same repo
- **When** `diversifyTrending(skills, 3, 10)` is called
- **Then** only 3 from that repo appear in the result

- **Given** skills with empty `repoUrl`
- **When** diversity filtering runs
- **Then** the `author` field is used as the grouping key

**Implementation**:
1. In `src/lib/stats-compute.ts`, add exported `diversifyTrending(skills, maxPerRepo, limit)` function
2. Use Map to track per-repo count, skip entries exceeding maxPerRepo, stop at limit

---

### T-002: Write unit tests for diversifyTrending

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- Test capping at maxPerRepo
- Test limit enforcement
- Test order preservation
- Test author fallback for empty repoUrl
- Test empty input
- Test momentum pre-sort interaction

**Implementation**:
1. In `src/lib/__tests__/stats-compute.test.ts`, add `describe("diversifyTrending")` block with 6 test cases

---

## User Story: US-002 - Increase trending list to 10 items

**Project**: vskill-platform
**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 2 total, 2 completed

---

### T-003: Integrate diversifyTrending in both stats paths

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** `computeFullStats()` runs
- **When** trending skills are processed
- **Then** `diversifyTrending(raw, 3, 10)` is called after momentum sort

- **Given** `computeMinimalStats()` runs
- **When** trending skills are processed
- **Then** `diversifyTrending(raw, 3, 10)` is called consistently

**Implementation**:
1. In `computeFullStats()`, call `diversifyTrending(trendingSkillsRaw, 3, 10)` after momentum sort
2. In `computeMinimalStats()`, call `diversifyTrending(raw, 3, 10)` after momentum sort

---

### T-004: Verify TrendingSkills.tsx renders dynamic list

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** `TrendingSkills.tsx` component
- **When** it receives `stats.trendingSkills` array
- **Then** it maps over the entire array with no hardcoded limit

**Implementation**:
1. Verify `TrendingSkills.tsx` uses `trendingSkills.map()` with no `.slice()` or hardcoded cap
2. Confirmed: component renders all entries from `stats.trendingSkills`
