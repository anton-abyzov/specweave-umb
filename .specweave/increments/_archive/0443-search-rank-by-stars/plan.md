# Implementation Plan: Fix search ranking to sort by star count

## Overview

This increment addresses search ranking on verified-skill.com where results should sort by GitHub star count descending with CERTIFIED-first preservation across all 3 search paths. The change is scoped to a single file (`src/lib/search.ts`) with sort clause modifications in 3 locations.

**Key finding**: The production code already implements the desired sort behavior. Commits `1f3632f` (popularity-first ranking) and `b4dcc86` (certTier boost) collectively established the correct ORDER BY clauses across all 3 search paths. The existing test suite already validates this behavior.

## Architecture

### Component: Search Service (`src/lib/search.ts`)

Single-file change. No new components, APIs, or data model changes.

**Three search paths (all already correct)**:

1. **Edge KV** (`searchSkillsEdge`, line 253): In-memory sort
   ```
   CERTIFIED-first → githubStars DESC → computeSearchRank tiebreaker
   ```

2. **Postgres tsvector** (`searchSkills`, line 343): SQL ORDER BY
   ```
   CERTIFIED-first → "githubStars" DESC → rank DESC → "trustScore" DESC
   ```

3. **ILIKE fallback** (inside `searchSkills`, line 368): SQL ORDER BY
   ```
   CERTIFIED-first → "githubStars" DESC → "trustScore" DESC → "npmDownloadsWeekly" DESC
   ```

### Data Flow

```
User query
    |
    v
searchSkillsEdge (KV shards) ──── sub-50ms path
    |                                   |
    | (empty results?)                  | sort: cert-first, stars DESC
    v                                   |
searchSkills (Postgres tsvector) ───── fallback
    |                                   |
    | (empty results?)                  | sort: cert-first, stars DESC
    v                                   |
ILIKE fallback ────────────────────── last resort
                                        |
                                        | sort: cert-first, stars DESC
```

### Existing Sort Formulas (unchanged)

- `computeSearchRank`: relevance(50%) + popularity(30%) + certBonus(20%) -- used only as tiebreaker within equal star counts
- `computePopularityScore`: trust(40%) + stars(45%) + downloads(15%) -- feeds into computeSearchRank
- `computeCertBonus`: CERTIFIED=100, VERIFIED=20, else 0

## Technology Stack

- **Runtime**: Next.js 15 on Cloudflare Workers
- **Database**: Postgres via Prisma (Neon)
- **Cache**: Cloudflare KV (sharded search index)
- **Tests**: Vitest

## Implementation Phases

### Phase 1: Verification (primary work)

The sort clauses are already correct in production code. The work is to verify and add any missing test assertions that explicitly validate the AC requirements:

1. **AC-US1-01** (edge KV): Covered by existing test "sorts results by githubStars descending" and "ranks higher-starred skill first even with weaker name match"
2. **AC-US1-02** (tsvector): DB sort is handled by SQL ORDER BY -- mock-based tests verify row ordering is preserved
3. **AC-US1-03** (ILIKE): DB sort is handled by SQL ORDER BY -- needs explicit test verifying ILIKE results respect star ordering
4. **AC-US1-04** (tiebreaker): Covered by existing tests with equal-star scenarios
5. **AC-US2-01** (CERTIFIED-first): Covered by "CERTIFIED vendor skill appears first in edge search results" test
6. **AC-US2-02** (existing tests pass): Run full test suite

### Phase 2: Test Gap Coverage

Add targeted tests for any gaps:

- ILIKE fallback: verify sort order includes `githubStars DESC` (not just that results are returned)
- Cross-path consistency: verify same skill set produces same ordering across edge and Postgres paths

## Testing Strategy

- **Unit tests**: Vitest (`src/lib/search.test.ts`) -- existing 680-line suite covers core behavior
- **Coverage target**: 90% (per increment config)
- **TDD mode**: Verify red-green cycle for any new assertions
- **No E2E needed**: Backend-only sort change, no UI impact

## Technical Challenges

### Challenge 1: Spec describes already-fixed state

**Situation**: The problem statement references the blended formula with stars at ~13.5% effective weight, but code already sorts by `githubStars DESC` as primary factor.

**Resolution**: Verify existing implementation satisfies all ACs. Add any missing test assertions. Mark ACs as satisfied based on code review + test evidence.

**Risk**: None. The fix is already deployed and working.
