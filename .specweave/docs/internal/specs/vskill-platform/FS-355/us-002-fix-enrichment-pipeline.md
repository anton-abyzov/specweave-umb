---
id: US-002
feature: FS-355
title: Fix Enrichment Pipeline
status: complete
priority: P0
created: 2026-02-24
project: vskill-platform
---
# US-002: Fix Enrichment Pipeline

**Feature**: [FS-355](./FEATURE.md)

platform operator
**I want** the enrichment cron to cycle through all skills
**So that** GitHub stars, npm downloads, and trending scores reflect real data

---

## Acceptance Criteria

- [x] **AC-US2-01**: Enrichment always advances `updatedAt` for processed skills, even when no metric updates are available — prevents starvation
- [x] **AC-US2-02**: Enrichment batch size increased from 20 to 50 (172 skills / 50 = ~3.5h full cycle)
- [x] **AC-US2-03**: Enrichment batch logs start info including skill count and token availability

---

## Implementation

**Increment**: [0355-fix-homepage-zero-stats](../../../../../increments/0355-fix-homepage-zero-stats/spec.md)

