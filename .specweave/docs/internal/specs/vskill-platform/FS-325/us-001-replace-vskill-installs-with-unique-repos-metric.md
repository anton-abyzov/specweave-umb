---
id: US-001
feature: FS-325
title: Replace vskill Installs with Unique Repos Metric
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1286
    url: https://github.com/anton-abyzov/specweave/issues/1286
---
# US-001: Replace vskill Installs with Unique Repos Metric

**Feature**: [FS-325](./FEATURE.md)

visitor viewing the homepage dashboard
**I want** the "vskill Installs" metric card to show "Unique Repos" instead
**So that** I see an honest, verifiable metric showing the breadth of the skill ecosystem

---

## Acceptance Criteria

- [x] **AC-US1-01**: The second metric card title changes from "vskill Installs" to "Unique Repos"
- [x] **AC-US1-02**: The value shows the count of distinct `repoUrl` values across all skills (deduped)
- [x] **AC-US1-03**: The subtitle changes from "platform installs" to "GitHub repositories"
- [x] **AC-US1-04**: The MiniBarChart shows top repos by skill count (most skills per repo) instead of top by installs
- [x] **AC-US1-05**: The hero inline stat changes from `{fmt(totalInstalls)} installs` to `{uniqueRepos} repos`
- [x] **AC-US1-06**: Trending row "inst" column changes to show the repo's total skill count or is removed
- [x] **AC-US1-07**: A helper function `getUniqueRepoCount(skills)` is added to the data layer with tests

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

