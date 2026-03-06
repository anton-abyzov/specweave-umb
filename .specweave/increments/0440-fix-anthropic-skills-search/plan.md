# Implementation Plan: Fix Anthropic Skills Missing from Search

## Overview

Three targeted bug fixes in vskill-platform to make vendor-published skills (e.g., Anthropic's `skill-creator`) discoverable and correctly ranked. No schema changes, no new APIs, no new dependencies. All changes are to existing functions in 4 files.

**Root causes**:
1. `listOrgRepos()` in both JS and TS vendor-org-discovery files filters out repos with `stargazers_count === 0`, silently dropping legitimate vendor repos that happen to have zero stars.
2. `computeSearchRank()` in the edge search path has no certification weight: `relevance * 0.6 + popularity * 0.4`. A community fork with 500 stars easily outranks a CERTIFIED vendor original with 0 stars.
3. The Postgres search path (`searchSkills`) sorts by `rank DESC, trustScore DESC` with no `certTier` secondary sort, so CERTIFIED skills have no advantage over VERIFIED forks when trust/relevance tie.
4. `VENDOR_ORGS` / `TRUSTED_ORGS` arrays in `crawl-worker/sources/vendor-org-discovery.js` and `crawl-worker/lib/vendor-detect.js` are missing microsoft, vercel, cloudflare compared to the authoritative `src/lib/trust/trusted-orgs.ts`.

## Architecture

### Component Map (unchanged boundaries)

```
Edge Search Path (KV)              Postgres Fallback Path
--------------------------         ---------------------------
searchSkillsEdge()                 searchSkills()
  |                                  |
  +-- computeSearchRank()            +-- tsvector query
  |     |                            |     ORDER BY rank, certTier, trustScore
  |     +-- computeRelevanceScore()  |
  |     +-- computePopularityScore() +-- ILIKE fallback
  |     +-- computeCertBonus() [NEW] |     ORDER BY certTier, trustScore, stars
  |                                  |
  sort + paginate                    sort + paginate

Crawler (crawl-worker)             Platform Crawler (src/lib)
--------------------------         ---------------------------
vendor-org-discovery.js            vendor-org-discovery.ts
  |                                  |
  +-- listOrgRepos()                 +-- listOrgRepos()
  |     skip fork=true               |     skip fork=true
  |     [REMOVE zero-star filter]    |     [REMOVE zero-star filter]
  |                                  |
  +-- VENDOR_ORGS [SYNC to 7]       +-- imports from trusted-orgs.ts (OK)

vendor-detect.js
  +-- TRUSTED_ORGS [SYNC to 7]
```

### Files to Modify

| File | Function/Constant | Change |
|------|-------------------|--------|
| `src/lib/search.ts` | `computeSearchRank()` | New weights: `relevance * 0.5 + popularity * 0.3 + certBonus * 0.2` |
| `src/lib/search.ts` | (new) `computeCertBonus()` | Returns 100 for CERTIFIED, 20 for VERIFIED, 0 otherwise |
| `src/lib/search.ts` | `searchSkills()` tsvector query | Add `CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC` as secondary ORDER BY |
| `src/lib/search.ts` | `searchSkills()` ILIKE fallback | Add same certTier sort as secondary ORDER BY |
| `crawl-worker/sources/vendor-org-discovery.js` | `VENDOR_ORGS` constant | Sync to 7 orgs, add source-of-truth comment |
| `crawl-worker/sources/vendor-org-discovery.js` | `listOrgRepos()` | Remove `if (item.stargazers_count === 0) continue;` |
| `crawl-worker/lib/vendor-detect.js` | `TRUSTED_ORGS` constant | Sync to 7 orgs, add source-of-truth comment |
| `src/lib/crawler/vendor-org-discovery.ts` | `listOrgRepos()` | Remove `if (item.stargazers_count === 0) continue;` |

### Data Flow (no model changes)

No Prisma schema changes. The `certTier` field already exists on the `Skill` model and is already stored in `SearchIndexEntry` in KV shards. The edge search path already has access to `entry.certTier`. The Postgres path already selects `"certTier"::text` in its raw query.

## Design Decisions

### D1: certBonus Scale (100 / 20 / 0) Rather Than a Multiplier

**Decision**: Use an additive bonus on a 0-100 scale, weighted at 20% of the final rank.

**Rationale**: A multiplier (e.g., 2x for CERTIFIED) would make certification dominate all other signals. An additive bonus at 20% weight means:
- CERTIFIED skill (certBonus=100): gets +20 points to final rank
- VERIFIED skill (certBonus=20): gets +4 points to final rank
- A CERTIFIED skill with 0 stars and equal relevance beats a VERIFIED skill with 500 stars: `relevance * 0.5 + 0 * 0.3 + 100 * 0.2 = relevance * 0.5 + 20` vs `relevance * 0.5 + popularity * 0.3 + 20 * 0.2 = relevance * 0.5 + popularity * 0.3 + 4`. For popularity to overcome the 16-point cert gap, a VERIFIED skill would need ~53 popularity score, which equates to ~10k stars. This fulfills AC-US2-02 (0-star CERTIFIED beats 500-star VERIFIED).

**Rejected alternative**: Binary CERTIFIED-first sort. This would make ANY CERTIFIED skill rank above ANY non-CERTIFIED skill regardless of relevance, which breaks search quality for unrelated queries.

### D2: Postgres certTier Sort as Secondary, Not Primary

**Decision**: Add `CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC` after `rank DESC` in tsvector path and after `trustScore DESC` in ILIKE path.

**Rationale**: The Postgres path is a fallback; making certTier a tiebreaker after the existing primary sort preserves the current Postgres ranking behavior for most queries while ensuring CERTIFIED skills win ties. This mirrors the edge path's blended approach without requiring a full formula rewrite of the SQL.

### D3: Remove Zero-Star Filter Only for Vendor Orgs (Not Globally)

**Decision**: The zero-star filter stays for non-vendor discovery sources. Only `vendor-org-discovery.js` and `vendor-org-discovery.ts` drop the filter, and they exclusively scan vendor org repos.

**Rationale**: Zero-star filtering is a useful quality signal for the general GitHub discovery pipeline. Vendor orgs are inherently trusted (auto-CERTIFIED), so star count is irrelevant for them. Since these two files only scan `VENDOR_ORGS`, removing the filter here means it only affects vendor repos. AC-US1-02 is automatically satisfied because other discovery sources are untouched.

### D4: Fork Filter Stays Unconditionally

**Decision**: `if (item.fork) continue;` remains even for vendor orgs.

**Rationale**: Forks under a vendor org (e.g., anthropics forking someone else's repo) are not original vendor skills. The fork filter correctly excludes these. AC-US1-04 is satisfied.

## Implementation Phases

### Phase 1: Vendor Org List Sync (US-003)

Sync `VENDOR_ORGS` in `crawl-worker/sources/vendor-org-discovery.js` and `TRUSTED_ORGS` in `crawl-worker/lib/vendor-detect.js` to match the 7 orgs in `src/lib/trust/trusted-orgs.ts`. Add a comment referencing the source of truth.

This is done first because it affects which orgs are scanned -- prerequisite for Phase 2 testing.

### Phase 2: Remove Zero-Star Filter (US-001)

Remove `if (item.stargazers_count === 0) continue;` from `listOrgRepos()` in both:
- `crawl-worker/sources/vendor-org-discovery.js` (line 127)
- `src/lib/crawler/vendor-org-discovery.ts` (line 104)

The fork filter remains.

### Phase 3: Add certTier Boost to Search (US-002)

1. Add `computeCertBonus(entry: SearchIndexEntry): number` to `src/lib/search.ts`
2. Update `computeSearchRank()` to use new weights: `relevance * 0.5 + popularity * 0.3 + certBonus * 0.2`
3. Update Postgres tsvector ORDER BY to include certTier secondary sort
4. Update Postgres ILIKE fallback ORDER BY to include certTier secondary sort

## Testing Strategy

### Unit Tests (Vitest)

**search.ts**:
- `computeCertBonus()`: returns 100 for "CERTIFIED", 20 for "VERIFIED", 0 for "UNVERIFIED" / unknown
- `computeSearchRank()`: CERTIFIED+0stars beats VERIFIED+500stars at equal relevance (AC-US2-02 numeric proof)
- `computeRelevanceScore()`: unchanged behavior regression test
- `computePopularityScore()`: unchanged weights regression test (AC-US2-05)

**vendor-org-discovery.js** (crawl-worker):
- Mock GitHub API responses including a 0-star non-fork repo; verify it appears in results
- Mock a fork with 100 stars; verify it is still excluded

**vendor-org-discovery.ts** (platform):
- Same pattern: 0-star vendor repo included, fork excluded

**vendor-detect.js**:
- `isVendorRepo()` returns true for all 7 vendor orgs

### Integration Tests

- Edge search: build KV index with one CERTIFIED 0-star skill and one VERIFIED 500-star skill with the same name; verify CERTIFIED ranks first
- Postgres tsvector path: same scenario via raw SQL (can be tested with Prisma test client)

### Post-Deploy Verification

- Manual re-crawl of vendor orgs
- Search "skill-creator" on verified-skill.com; confirm Anthropic's version is in top 3

## Technical Challenges

### Challenge 1: JS/TS Duplication

The zero-star filter exists in both `crawl-worker/sources/vendor-org-discovery.js` (plain JS for Docker workers) and `src/lib/crawler/vendor-org-discovery.ts` (TypeScript for Cloudflare Workers). Both must be patched identically.

**Mitigation**: The TS file already imports `VENDOR_ORGS` from `trusted-orgs.ts`, so it stays in sync automatically. The JS file cannot import TS, so it gets a manual sync + source-of-truth comment. This is an existing architectural constraint (noted in the VENDOR_ORGS comment on line 19 of vendor-org-discovery.js).

### Challenge 2: Edge vs Postgres Ranking Parity

The edge path uses `computeSearchRank()` (in-memory JS), while the Postgres path uses SQL `ORDER BY`. These cannot use identical formulas because the Postgres path relies on `ts_rank_cd()` rather than `computeRelevanceScore()`.

**Mitigation**: The Postgres path uses certTier as a secondary sort tiebreaker rather than trying to replicate the exact blended formula in SQL. This is sufficient because the Postgres path is a fallback for rare queries that miss the edge index; most traffic hits the edge path where the full formula applies.

### Challenge 3: Existing Search Index KV Data

After deploying the search.ts changes, the edge ranking formula changes immediately (it reads certTier from existing KV entries). No KV rebuild is needed. However, newly discovered 0-star vendor skills only appear after a re-crawl writes them to Postgres, and then a search index rebuild writes them to KV.

**Mitigation**: Post-deploy step includes triggering a vendor-org-discovery re-crawl and search index rebuild.

## Domain Skill Delegation

No domain skill delegation needed. This is a targeted bug fix across 4 files in a single project (vskill-platform). No new UI, no new APIs, no new infrastructure. Standard TypeScript/JavaScript edits with Vitest tests.
