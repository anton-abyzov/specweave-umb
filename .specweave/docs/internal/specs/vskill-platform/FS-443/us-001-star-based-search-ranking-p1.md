---
id: US-001
feature: FS-443
title: Star-based search ranking (P1)
status: completed
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** developer searching for skills on verified-skill.com."
project: vskill-platform
external:
  github:
    issue: 29
    url: "https://github.com/anton-abyzov/vskill-platform/issues/29"
---

# US-001: Star-based search ranking (P1)

**Feature**: [FS-443](./FEATURE.md)

**As a** developer searching for skills on verified-skill.com
**I want** search results sorted by GitHub star count (highest first)
**So that** the most popular and well-established skills appear at the top

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a search query matching multiple skills, when results are returned from the edge KV path, then results are sorted by githubStars descending within each certification tier
- [x] **AC-US1-02**: Given a search query matching multiple skills, when results are returned from the Postgres tsvector path, then results are sorted by githubStars descending within each certification tier
- [x] **AC-US1-03**: Given a search query matching multiple skills, when results are returned from the Postgres ILIKE fallback path, then results are sorted by githubStars descending within each certification tier
- [x] **AC-US1-04**: Given skills with equal star counts, when sorted, then the blended relevance rank (tsvector path) or computeSearchRank (edge path) is used as tiebreaker

---

## Implementation

**Increment**: [0443-search-rank-by-stars](../../../../../increments/0443-search-rank-by-stars/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Fix edge KV sort to use githubStars DESC
- [x] **T-002**: Fix Postgres tsvector sort to use githubStars DESC
- [x] **T-003**: Fix ILIKE fallback sort to use githubStars DESC (was trustScore first)
- [x] **T-004**: Verify tiebreaker behavior when stars are equal
