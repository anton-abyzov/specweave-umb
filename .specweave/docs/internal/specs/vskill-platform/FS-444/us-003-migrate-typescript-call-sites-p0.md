---
id: US-003
feature: FS-444
title: "Migrate TypeScript Call Sites (P0)"
status: completed
priority: P0
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** platform developer."
project: vskill-platform
external:
  github:
    issue: 33
    url: "https://github.com/anton-abyzov/vskill-platform/issues/33"
---

# US-003: Migrate TypeScript Call Sites (P0)

**Feature**: [FS-444](./FEATURE.md)

**As a** platform developer
**I want** all 8 TypeScript call sites to use `shouldRejectSkillPath()` instead of `isAgentConfigPath()`
**So that** framework plugin paths are filtered at every ingestion point in the platform

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `src/lib/scanner.ts` (2 call sites), when the scanner encounters a framework plugin path, then it is rejected
- [x] **AC-US3-02**: Given `src/app/api/v1/submissions/route.ts` (2 call sites), when a submission has a framework plugin path, then it is rejected with a reason
- [x] **AC-US3-03**: Given `src/app/api/v1/submissions/bulk/route.ts` (1 call site), when a bulk submission contains framework plugin paths, then those entries are rejected
- [x] **AC-US3-04**: Given `src/lib/crawler/github-discovery.ts` (2 call sites), when discovery finds a framework plugin SKILL.md, then it is skipped
- [x] **AC-US3-05**: Given `src/lib/crawler/vendor-org-discovery.ts` (1 call site), when vendor org scan finds a framework plugin path, then it is skipped

---

## Implementation

**Increment**: [0444-filter-framework-plugin-skills](../../../../../increments/0444-filter-framework-plugin-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Migrate scanner.ts call sites (2 sites)
- [x] **T-006**: Migrate submissions/route.ts call sites (2 sites)
- [x] **T-007**: Migrate submissions/bulk/route.ts call site (1 site)
- [x] **T-008**: Migrate github-discovery.ts call sites (2 sites)
- [x] **T-009**: Migrate vendor-org-discovery.ts call site (1 site)
