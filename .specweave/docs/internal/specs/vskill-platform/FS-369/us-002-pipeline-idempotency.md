---
id: US-002
feature: FS-369
title: Pipeline Idempotency
status: complete
priority: P0
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1338
    url: https://github.com/anton-abyzov/specweave/issues/1338
---
# US-002: Pipeline Idempotency

**Feature**: [FS-369](./FEATURE.md)

**As a** platform operator,
**I want** `processSubmission()` to skip already-published submissions
**So that** duplicate queue messages don't trigger redundant scans.

---

## Acceptance Criteria

- [x] **AC-US2-01**: `processSubmission()` checks current state at start; returns early if PUBLISHED/VENDOR_APPROVED
- [x] **AC-US2-02**: Early exit logs a message for observability

---

## Implementation

**Increment**: [0369-fix-duplicate-processing-false-rejections](../../../../../increments/0369-fix-duplicate-processing-false-rejections/spec.md)

## Tasks

_Completed_
