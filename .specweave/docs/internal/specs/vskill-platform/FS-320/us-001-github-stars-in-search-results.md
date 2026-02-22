---
id: US-001
feature: FS-320
title: GitHub Stars in Search Results
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1293
    url: https://github.com/anton-abyzov/specweave/issues/1293
---
# US-001: GitHub Stars in Search Results

**Feature**: [FS-320](./FEATURE.md)

developer browsing skills via the Cmd+K palette
**I want** to see GitHub star counts for each skill result
**So that** I can quickly gauge a skill's popularity without opening its detail page

---

## Acceptance Criteria

- [x] **AC-US1-01**: Search API `/api/v1/skills/search` returns `githubStars` (number) alongside existing fields
- [x] **AC-US1-02**: SearchPalette displays a star icon with formatted count for each skill result where `githubStars > 0`
- [x] **AC-US1-03**: Star count is formatted as compact notation -- raw number below 1000, "X.Xk" for 1000+
- [x] **AC-US1-04**: Star display does not appear when `githubStars` is 0 or missing
- [x] **AC-US1-05**: Star icon and count positioned between repo URL and cert tier badge in result row

---

## Implementation

**Increment**: [0320-search-palette-github-stars](../../../../../increments/0320-search-palette-github-stars/spec.md)

