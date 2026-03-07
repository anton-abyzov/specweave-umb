---
increment: 0440-fix-anthropic-skills-search
title: Fix Anthropic Skills Missing from Search
type: bug
priority: P0
status: completed
created: 2026-03-06T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Anthropic Skills Missing from Search

## Problem Statement

Anthropic's official skills (skill-creator, etc.) are completely absent from verified-skill.com search results. Third-party forks appear instead. Two root causes:

1. The vendor-org-discovery crawler filters out zero-star repos even from trusted vendor orgs, silently dropping repos like `anthropics/skill-creator` that have 0 GitHub stars.
2. The CERTIFIED certification tier gives zero ranking boost in search. Community forks with more GitHub stars outrank vendor originals because the ranking formula is purely `relevance * 0.6 + popularity * 0.4` with no certification weight.

Additionally, `VENDOR_ORGS` hardcoded lists in crawl-worker JS files have drifted from the authoritative `trusted-orgs.ts` (missing microsoft, vercel, cloudflare).

## Goals

- Vendor skills with 0 stars are discovered and indexed
- CERTIFIED vendor skills outrank VERIFIED community forks in search results
- All VENDOR_ORGS lists across the codebase are synchronized

## User Stories

### US-001: Remove Zero-Star Filter for Vendor Orgs
**Project**: vskill-platform
**As a** user searching for official vendor skills
**I want** vendor repos with zero GitHub stars to be discoverable
**So that** all vendor-published skills appear in search results regardless of star count

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a vendor org repo with 0 GitHub stars and a valid SKILL.md, when vendor-org-discovery runs, then the repo is included in discovery results (not filtered out)
- [ ] **AC-US1-02**: Given a non-vendor org repo with 0 GitHub stars, when any discovery source runs, then existing zero-star filtering behavior is unchanged
- [ ] **AC-US1-03**: Both `crawl-worker/sources/vendor-org-discovery.js` and `src/lib/crawler/vendor-org-discovery.ts` skip the zero-star filter for vendor org repos
- [ ] **AC-US1-04**: Fork repos are still filtered out regardless of vendor status

---

### US-002: Add CertTier Boost to Search Ranking
**Project**: vskill-platform
**As a** user searching for a skill by name
**I want** the official CERTIFIED vendor version to rank above community forks
**So that** I find the trusted original before third-party copies

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Edge search ranking formula becomes `relevance * 0.5 + popularity * 0.3 + certBonus * 0.2` where CERTIFIED certBonus=100 and VERIFIED certBonus=20, all others certBonus=0
- [ ] **AC-US2-02**: A CERTIFIED skill with 0 stars outranks a VERIFIED skill with 500 stars when both match the same query with equal relevance
- [ ] **AC-US2-03**: Postgres tsvector search path uses `CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC` as secondary sort after ts_rank_cd
- [ ] **AC-US2-04**: Postgres ILIKE fallback path uses the same certTier sort as secondary sort after trustScore
- [ ] **AC-US2-05**: Existing popularity formula (`computePopularityScore`) weights remain unchanged (40% trust, 45% stars, 15% downloads)

---

### US-003: Sync VENDOR_ORGS Lists Across Codebase
**Project**: vskill-platform
**As a** platform maintainer
**I want** all VENDOR_ORGS hardcoded lists to match the authoritative `trusted-orgs.ts`
**So that** vendor detection is consistent across crawler and platform

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `crawl-worker/sources/vendor-org-discovery.js` VENDOR_ORGS list contains all 7 orgs: anthropics, openai, google-gemini, google, microsoft, vercel, cloudflare
- [ ] **AC-US3-02**: `crawl-worker/lib/vendor-detect.js` TRUSTED_ORGS list contains all 7 orgs matching `trusted-orgs.ts`
- [ ] **AC-US3-03**: A code comment in each JS file references `src/lib/trust/trusted-orgs.ts` as the source of truth
- [ ] **AC-US3-04**: Post-deploy: manual re-crawl of vendor orgs is triggered to pick up previously filtered repos

## Out of Scope

- Changing the `computePopularityScore` internal weights or adding vskillInstalls to it
- UI changes to search results display
- Automated sync mechanism between TS and JS vendor org lists
- Adding new vendor orgs beyond the current 7

## Technical Notes

### Files to Modify

| File | Change |
|------|--------|
| `crawl-worker/sources/vendor-org-discovery.js` | Remove zero-star filter (line 127), sync VENDOR_ORGS to 7 orgs |
| `src/lib/crawler/vendor-org-discovery.ts` | Remove zero-star filter (line 104) |
| `crawl-worker/lib/vendor-detect.js` | Sync TRUSTED_ORGS to 7 orgs |
| `src/lib/search.ts` | Add `computeCertBonus()`, update `computeSearchRank()` weights, add certTier ORDER BY to both Postgres paths |

### Ranking Formula Change

**Before**: `relevance * 0.6 + popularity * 0.4`
**After**: `relevance * 0.5 + popularity * 0.3 + certBonus * 0.2`

| certTier | certBonus |
|----------|-----------|
| CERTIFIED | 100 |
| VERIFIED | 20 |
| UNVERIFIED | 0 |

### Post-Deploy Steps

1. Deploy updated crawl-worker to VMs
2. Trigger manual vendor-org-discovery re-crawl
3. Verify Anthropic skills appear in search results

## Success Metrics

- Anthropic official skills (e.g., skill-creator) appear in top 3 results when searched by name
- Zero third-party forks outrank their CERTIFIED vendor originals in search
