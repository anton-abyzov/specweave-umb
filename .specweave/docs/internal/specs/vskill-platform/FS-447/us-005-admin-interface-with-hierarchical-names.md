---
id: US-005
feature: FS-447
title: Admin Interface with Hierarchical Names
status: complete
priority: P1
created: 2026-03-07
project: vskill-platform
---
# US-005: Admin Interface with Hierarchical Names

**Feature**: [FS-447](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the admin skill block endpoint (`/api/v1/admin/skills/[name]/block`), when the route receives a hierarchical name with slashes, then Next.js catch-all routing (`[...name]`) correctly parses `owner/repo/skillSlug` and the block operation succeeds
- [x] **AC-US5-02**: Given the admin skill delete endpoint (`/api/v1/admin/skills/[name]/delete`), when called with a hierarchical name, then the skill is deleted and its KV entries (both hierarchical key and legacy alias) are cleaned up
- [x] **AC-US5-03**: Given the admin submissions list, when displaying pending or processed submissions, then skill names are shown in `owner/repo/skillSlug` format with links to the new URL structure
- [x] **AC-US5-04**: Given the repo-block endpoint, when a repo is blocked, then all skills from that repo (identified by `ownerSlug` + `repoSlug`) are blocked and their KV entries updated

---

## Implementation

**Increment**: [0447-hierarchical-skill-urls](../../../../../increments/0447-hierarchical-skill-urls/spec.md)

