---
id: US-002
feature: FS-445
title: "Increase trending list to 10 items (P1)"
status: completed
priority: P1
created: 2026-03-07
tldr: "**As a** homepage visitor."
project: vskill-platform
---

# US-002: Increase trending list to 10 items (P1)

**Feature**: [FS-445](./FEATURE.md)

**As a** homepage visitor
**I want** the trending section to show 10 skills instead of 8
**So that** I see a broader range of trending tools

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the `diversifyTrending()` function, when called with `limit=10`, then the result contains at most 10 entries
- [x] **AC-US2-02**: Given both `computeFullStats()` and `computeMinimalStats()`, when they compute trending skills, then both call `diversifyTrending(raw, 3, 10)` consistently
- [x] **AC-US2-03**: Given the `TrendingSkills.tsx` component, when it renders trending data, then it displays all entries returned by the stats (no hardcoded UI limit)

---

## Implementation

**Increment**: [0445-trending-diversity](../../../../../increments/0445-trending-diversity/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Integrate diversifyTrending in both stats paths
- [x] **T-004**: Verify TrendingSkills.tsx renders dynamic list
