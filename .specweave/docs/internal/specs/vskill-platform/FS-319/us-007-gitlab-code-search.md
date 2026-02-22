---
id: US-007
feature: FS-319
title: GitLab Code Search
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1271
    url: https://github.com/anton-abyzov/specweave/issues/1271
---
# US-007: GitLab Code Search

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** to discover skills on GitLab.com
**So that** non-GitHub repos are included in the registry

---

## Acceptance Criteria

- [x] **AC-US7-01**: Queries GitLab API `GET /api/v4/search?scope=projects&search=SKILL.md` (projects scope works without Premium)
- [x] **AC-US7-02**: For matched projects, checks file tree for SKILL.md presence
- [x] **AC-US7-03**: Handles pagination, rate limits, and auth via GITLAB_TOKEN
- [x] **AC-US7-04**: Submits discovered GitLab repos to platform

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

