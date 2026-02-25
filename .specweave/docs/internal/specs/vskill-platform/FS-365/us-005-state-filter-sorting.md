---
id: US-005
feature: FS-365
title: State Filter Sorting
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1339
    url: https://github.com/anton-abyzov/specweave/issues/1339
---
# US-005: State Filter Sorting

**Feature**: [FS-365](./FEATURE.md)

**As a** user,
**I want** to filter by rejected/published and sort by when it happened
**So that** I can find relevant items quickly.

---

## Acceptance Criteria

- [x] **AC-US5-01**: "Active" filter defaults to processingOrder sort
- [x] **AC-US5-02**: "Rejected" filter defaults to updatedAt desc
- [x] **AC-US5-03**: "Published" filter defaults to updatedAt desc
- [x] **AC-US5-04**: "All" filter defaults to processingOrder sort
- [x] **AC-US5-05**: User can toggle sort direction on any column in any filter view

---

## Implementation

**Increment**: [0365-queue-position-ux](../../../../../increments/0365-queue-position-ux/spec.md)

## Tasks

_Completed_
