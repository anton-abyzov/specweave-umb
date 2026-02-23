---
id: US-003
feature: FS-325
title: GitHub Stars Deduplication by Repo URL
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1289
    url: https://github.com/anton-abyzov/specweave/issues/1289
---
# US-003: GitHub Stars Deduplication by Repo URL

**Feature**: [FS-325](./FEATURE.md)

visitor viewing the GitHub Stars metric
**I want** stars to be counted once per unique repository, not once per skill
**So that** the total reflects actual GitHub star counts without inflation

---

## Acceptance Criteria

- [x] **AC-US3-01**: A helper function `getDeduplicatedStars(skills)` returns `{ totalStars, repoCount, topRepos }` by grouping skills by `repoUrl` and taking the max stars per repo
- [x] **AC-US3-02**: The homepage "GitHub Stars" metric card uses the deduplicated total
- [x] **AC-US3-03**: The MiniBarChart shows top repos (not skills) by star count, with the repo display name as `owner/repo`
- [x] **AC-US3-04**: The hero inline stat `{fmt(totalStars)} stars` uses the deduplicated value
- [x] **AC-US3-05**: The MetricCard subtitle shows "across N repos" (not "across N skills")
- [x] **AC-US3-06**: The deduplication uses the max `githubStars` value among all skills sharing a `repoUrl` (since the repo's star count should be the same for all skills in it)

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

