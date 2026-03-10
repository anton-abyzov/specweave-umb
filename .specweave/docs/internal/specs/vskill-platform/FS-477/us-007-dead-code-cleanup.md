---
id: US-007
feature: FS-477
title: "Dead Code Cleanup"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** developer."
project: vskill-platform
---

# US-007: Dead Code Cleanup

**Feature**: [FS-477](./FEATURE.md)

**As a** developer
**I want** removed homepage sections and their component files deleted
**So that** the codebase stays lean and there is no dead code to maintain

---

## Acceptance Criteria

- [x] **AC-US7-01**: Given the cleanup is complete, when checking the file system, then `HomepageDemoHero.tsx` and `MarketDashboard.tsx` (and related files) are deleted
- [x] **AC-US7-02**: Given the cleanup, when checking `HomeSkeleton.tsx`, then unused skeleton components (`HeroStatsSkeleton`, `DashboardSkeleton`) are removed if no longer imported anywhere
- [x] **AC-US7-03**: Given the cleanup, when running `npx tsc --noEmit`, then there are zero type errors (no dangling imports)
- [x] **AC-US7-04**: Given the cleanup, when running the full test suite, then all tests pass with no regressions

---

## Implementation

**Increment**: [0477-homepage-studio-nav-redesign](../../../../../increments/0477-homepage-studio-nav-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
