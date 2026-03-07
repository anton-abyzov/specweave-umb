---
increment: 0443-search-rank-by-stars
title: "Fix search ranking to sort by star count"
by_user_story:
  US-001: [T-001, T-002, T-003, T-004]
  US-002: [T-005, T-006]
total_tasks: 6
completed_tasks: 6
---

# Tasks: Fix search ranking to sort by star count

## User Story: US-001 - Star-based search ranking

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 4 total, 4 completed

---

### T-001: Fix edge KV sort to use githubStars DESC

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** a search query matching multiple skills with different star counts in the edge KV path
- **When** `searchSkillsEdge` returns results
- **Then** results are sorted by githubStars descending within each certification tier

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - "sorts results by githubStars descending" — verifies higher-starred skill ranks above lower-starred within same cert tier
   - "ranks higher-starred skill first even with weaker name match" — verifies stars override name relevance
   - **Coverage Target**: 90%

**Implementation**:
1. In `searchSkillsEdge` (line ~253 of `src/lib/search.ts`), sort `filtered` array:
   - Primary: CERTIFIED-first (certTier descending)
   - Secondary: `githubStars` descending
   - Tiebreaker: `computeSearchRank` descending

---

### T-002: Fix Postgres tsvector sort to use githubStars DESC

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a search query matching multiple skills via the Postgres tsvector path
- **When** `searchSkills` returns results
- **Then** results respect `githubStars DESC` ordering within each certification tier

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - Mock-based test verifying row ordering is preserved from Prisma result in expected star-descending order
   - **Coverage Target**: 90%

**Implementation**:
1. In `searchSkills` tsvector path (line ~343 of `src/lib/search.ts`), ORDER BY clause:
   - `CERTIFIED-first → "githubStars" DESC → rank DESC → "trustScore" DESC`

---

### T-003: Fix ILIKE fallback sort to use githubStars DESC (was trustScore first)

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a search query with no tsvector matches, triggering the ILIKE fallback path
- **When** `searchSkills` returns ILIKE results
- **Then** results are sorted by githubStars descending (not trustScore), within each certification tier

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - ILIKE path test: two skills returned from mock, higher-starred one appears first
   - **Coverage Target**: 90%

**Implementation**:
1. In ILIKE fallback block (line ~368 of `src/lib/search.ts`), change ORDER BY from:
   - `CERTIFIED-first → "trustScore" DESC → "npmDownloadsWeekly" DESC`
   - to: `CERTIFIED-first → "githubStars" DESC → "trustScore" DESC → "npmDownloadsWeekly" DESC`

---

### T-004: Verify tiebreaker behavior when stars are equal

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** two skills with identical githubStars values
- **When** sorted by the edge KV path
- **Then** the skill with higher `computeSearchRank` appears first

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - Equal-star tiebreaker test: two skills with same stars, different computeSearchRank — higher-rank skill sorts first
   - **Coverage Target**: 90%

**Implementation**:
1. No additional code change — tiebreaker logic already present in all 3 paths
2. Verify test assertions confirm tiebreaker ordering explicitly

---

## User Story: US-002 - CERTIFIED-first ordering preserved

**Linked ACs**: AC-US2-01, AC-US2-02
**Tasks**: 2 total, 2 completed

---

### T-005: Verify CERTIFIED skill ranks above non-certified regardless of stars

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed

**Test Plan**:
- **Given** a CERTIFIED skill with fewer stars than a non-certified skill
- **When** search results are returned from any of the 3 search paths
- **Then** the CERTIFIED skill appears first in results

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - "CERTIFIED vendor skill appears first in edge search results" — CERTIFIED with low stars vs non-certified with high stars; CERTIFIED wins
   - **Coverage Target**: 90%

**Implementation**:
1. All 3 sort clauses use cert tier as outermost (highest priority) sort key
2. In edge KV: CERTIFIED check before star comparison
3. In SQL paths: cert tier column as first ORDER BY expression

---

### T-006: Run full test suite to confirm all ACs pass

**User Story**: US-002
**Satisfies ACs**: AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** all 3 sort clauses updated in `src/lib/search.ts`
- **When** `npx vitest run src/lib/search.test.ts` executes in `repositories/anton-abyzov/vskill-platform/`
- **Then** all tests pass with no regressions

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - Full suite run — all existing and updated tests pass
   - **Coverage Target**: 90%

**Implementation**:
1. Run `npx vitest run src/lib/search.test.ts` in `repositories/anton-abyzov/vskill-platform/`
2. Confirm 0 failures
3. Mark all ACs in spec.md as satisfied
