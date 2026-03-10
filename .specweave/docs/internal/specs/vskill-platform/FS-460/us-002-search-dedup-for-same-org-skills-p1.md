---
id: US-002
feature: FS-460
title: "Search dedup for same-org skills (P1)"
status: completed
priority: P0
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** user searching for skills."
project: vskill-platform
related_projects: [vskill]
external:
  github:
    issue: 47
    url: https://github.com/anton-abyzov/vskill-platform/issues/47
---

# US-002: Search dedup for same-org skills (P1)

**Feature**: [FS-460](./FEATURE.md)

**As a** user searching for skills
**I want** search results to show one canonical entry when the same skill exists in multiple repos from the same vendor org
**So that** I see clean, non-redundant results with the best version highlighted

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given skills with identical `ownerSlug` and `skillSlug` exist across multiple repos (e.g., `anthropics/skills/frontend-design` and `anthropics/claude-code/frontend-design`), when edge search returns results, then duplicates are collapsed into a single canonical entry (the one with highest `githubStars`)
- [x] **AC-US2-02**: Given a collapsed search result, when the API response is returned, then the canonical entry includes an `alternateRepos` array containing `{ ownerSlug, repoSlug, repoUrl }` for each collapsed duplicate
- [x] **AC-US2-03**: Given the Postgres fallback search path, when results are returned, then the same dedup logic applies (group by `ownerSlug`+`skillSlug`, keep highest stars, attach alternates)
- [x] **AC-US2-04**: Given the `SearchResult` type in `search.ts`, when `alternateRepos` is added, then the field is typed as `Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>` and is optional (undefined when no duplicates exist)
- [x] **AC-US2-05**: Given the dedup logic, when unit tests run, then at least 3 test cases cover: no duplicates (passthrough), two repos same skill (collapse), mixed vendors (only same-org collapses)

---

## Implementation

**Increment**: [0460-vendor-provider-discovery](../../../../../increments/0460-vendor-provider-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Add alternateRepos to SearchResult type in search.ts
- [x] **T-007**: Implement deduplicateBySkill() in search route.ts and add unit tests
