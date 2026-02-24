---
id: US-003
feature: FS-355
title: Non-Zero Trending Scores
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-003: Non-Zero Trending Scores

**Feature**: [FS-355](./FEATURE.md)

visitor to the homepage
**I want** the trending section to show meaningful scores
**So that** I can discover active and popular skills

---

## Acceptance Criteria

- [x] **AC-US3-01**: Trending score formula includes recency boost: +5 for skills created within 7 days, +3 for active repos (lastCommitAt within 7 days)
- [x] **AC-US3-02**: 30-day trending formula includes proportional recency boost: +3 for skills created within 30 days, +2 for active repos

---

## Implementation

**Increment**: [0355-fix-homepage-zero-stats](../../../../../increments/0355-fix-homepage-zero-stats/spec.md)

