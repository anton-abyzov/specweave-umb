---
id: US-001
feature: FS-369
title: State Guard
status: complete
priority: P0
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1336
    url: https://github.com/anton-abyzov/specweave/issues/1336
---
# US-001: State Guard

**Feature**: [FS-369](./FEATURE.md)

**As a** platform operator,
**I want** success terminal states (PUBLISHED, VENDOR_APPROVED) to be locked against pipeline regression
**So that** duplicate processing cannot overwrite published skills with rejection.

---

## Acceptance Criteria

- [x] **AC-US1-01**: `updateState()` blocks transitions FROM PUBLISHED/VENDOR_APPROVED unless `force: true`
- [x] **AC-US1-02**: Blocked transitions log a warning (non-breaking, no throw)
- [x] **AC-US1-03**: Admin reprocess endpoints (REJECTED→RECEIVED) still work without `force`

---

## Implementation

**Increment**: [0369-fix-duplicate-processing-false-rejections](../../../../../increments/0369-fix-duplicate-processing-false-rejections/spec.md)

## Tasks

_Completed_
