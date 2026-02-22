---
id: US-008
feature: FS-319
title: npm Pagination Fix
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1272
    url: https://github.com/anton-abyzov/specweave/issues/1272
---
# US-008: npm Pagination Fix

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** npm search to paginate beyond 100 results
**So that** all matching npm packages are discovered, not just the first 100

---

## Acceptance Criteria

- [x] **AC-US8-01**: npm search uses `from` offset parameter to paginate all results
- [x] **AC-US8-02**: Continues fetching until `objects` array is empty or total is reached
- [x] **AC-US8-03**: Dedup within and across keyword searches

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

