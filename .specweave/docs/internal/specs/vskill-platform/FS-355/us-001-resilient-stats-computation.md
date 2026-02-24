---
id: US-001
feature: FS-355
title: Resilient Stats Computation
status: complete
priority: P0
created: 2026-02-24
project: vskill-platform
---
# US-001: Resilient Stats Computation

**Feature**: [FS-355](./FEATURE.md)

visitor to the homepage
**I want** to always see real platform statistics
**So that** the platform appears credible with accurate data

---

## Acceptance Criteria

- [x] **AC-US1-01**: `computeMinimalStats()` runs individual queries with per-query try/catch instead of returning hardcoded zeros — each metric degrades independently
- [x] **AC-US1-02**: `computeFullStats()` uses a 25s timeout (up from 10s) for the 12-query Promise.all batch
- [x] **AC-US1-03**: Structured error logging in `computePlatformStats` catch block includes error message and short stack trace
- [x] **AC-US1-04**: `scanPassRate` correctly computes as ~100% when there are skills but no blocklist entries (not 0%)

---

## Implementation

**Increment**: [0355-fix-homepage-zero-stats](../../../../../increments/0355-fix-homepage-zero-stats/spec.md)

