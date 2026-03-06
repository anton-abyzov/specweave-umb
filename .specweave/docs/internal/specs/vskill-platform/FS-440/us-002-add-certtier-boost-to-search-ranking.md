---
id: US-002
feature: FS-440
title: "Add CertTier Boost to Search Ranking"
status: not_started
priority: P0
created: 2026-03-06
tldr: "**As a** user searching for a skill by name."
project: vskill-platform
external:
  github:
    issue: 19
    url: https://github.com/anton-abyzov/vskill-platform/issues/19
---

# US-002: Add CertTier Boost to Search Ranking

**Feature**: [FS-440](./FEATURE.md)

**As a** user searching for a skill by name
**I want** the official CERTIFIED vendor version to rank above community forks
**So that** I find the trusted original before third-party copies

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Edge search ranking formula becomes `relevance * 0.5 + popularity * 0.3 + certBonus * 0.2` where CERTIFIED certBonus=100 and VERIFIED certBonus=20, all others certBonus=0
- [ ] **AC-US2-02**: A CERTIFIED skill with 0 stars outranks a VERIFIED skill with 500 stars when both match the same query with equal relevance
- [ ] **AC-US2-03**: Postgres tsvector search path uses `CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC` as secondary sort after ts_rank_cd
- [ ] **AC-US2-04**: Postgres ILIKE fallback path uses the same certTier sort as secondary sort after trustScore
- [ ] **AC-US2-05**: Existing popularity formula (`computePopularityScore`) weights remain unchanged (40% trust, 45% stars, 15% downloads)

---

## Implementation

**Increment**: [0440-fix-anthropic-skills-search](../../../../../increments/0440-fix-anthropic-skills-search/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Add computeCertBonus() and update computeSearchRank() in src/lib/search.ts
- [x] **T-006**: Add certTier secondary sort to Postgres tsvector path in searchSkills()
- [x] **T-007**: Add certTier secondary sort to Postgres ILIKE fallback path in searchSkills()
