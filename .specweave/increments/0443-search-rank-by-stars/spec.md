---
increment: 0443-search-rank-by-stars
title: Fix search ranking to sort by star count
type: bug
priority: P1
status: completed
created: 2026-03-07T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix search ranking to sort by star count

## Problem Statement

Search results on verified-skill.com do not reflect user expectations. The Anthropic frontend-design skill has 79.4k GitHub stars yet appears near the bottom of search results. The root cause is the blended ranking formula: Relevance(50%) + Popularity(30%) + CertBonus(20%), where stars are only 45% of the Popularity component -- giving stars an effective weight of ~13.5%. Users expect the most popular skills (by stars) to appear first. Additionally, the ILIKE fallback path sorts by trustScore first instead of stars, creating inconsistent ranking across search paths.

## Goals

- Sort all search results by GitHub star count descending as the primary factor
- Preserve CERTIFIED-first ordering so vendor-certified skills always rank above community skills
- Ensure consistent sort behavior across all 3 search paths (edge KV, tsvector, ILIKE fallback)

## User Stories

### US-001: Star-based search ranking (P1)
**Project**: vskill-platform
**As a** developer searching for skills on verified-skill.com
**I want** search results sorted by GitHub star count (highest first)
**So that** the most popular and well-established skills appear at the top

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a search query matching multiple skills, when results are returned from the edge KV path, then results are sorted by githubStars descending within each certification tier
- [x] **AC-US1-02**: Given a search query matching multiple skills, when results are returned from the Postgres tsvector path, then results are sorted by githubStars descending within each certification tier
- [x] **AC-US1-03**: Given a search query matching multiple skills, when results are returned from the Postgres ILIKE fallback path, then results are sorted by githubStars descending within each certification tier
- [x] **AC-US1-04**: Given skills with equal star counts, when sorted, then the blended relevance rank (tsvector path) or computeSearchRank (edge path) is used as tiebreaker

---

### US-002: CERTIFIED-first ordering preserved (P1)
**Project**: vskill-platform
**As a** developer searching for skills
**I want** CERTIFIED vendor skills to always appear before non-certified skills
**So that** I see trusted, officially certified skills first regardless of star count

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a CERTIFIED skill with fewer stars than a non-certified skill, when search results are returned, then the CERTIFIED skill appears first
- [x] **AC-US2-02**: Given the sort order change, when existing tests run, then CERTIFIED-first ordering is verified across all 3 search paths

## Out of Scope

- Changing the computeSearchRank or computePopularityScore formulas (they remain as tiebreakers)
- UI/frontend changes (sort order is purely backend)
- Search index structure or KV shard format changes
- Modifying the blocklist search ranking

## Technical Notes

### File Scope
- Single file: `src/lib/search.ts`
- Test file: `src/lib/search.test.ts`

### Search Paths to Fix
1. **Edge KV** (`searchSkillsEdge`): Sort `filtered` array by CERTIFIED-first, then githubStars DESC, then computeSearchRank as tiebreaker
2. **Postgres tsvector** (`searchSkills`): ORDER BY clause must use `"githubStars" DESC` after cert tier sort
3. **Postgres ILIKE fallback** (inside `searchSkills`): ORDER BY clause must use `"githubStars" DESC` after cert tier sort -- currently uses `"trustScore" DESC` first

### Constraints
- Must not break existing search functionality
- Must not impact search latency

## Success Metrics

- Anthropic frontend-design skill (79.4k stars) appears in top results for relevant queries
- All 3 search paths produce consistent ordering by stars
- Existing search test suite passes with updated assertions
