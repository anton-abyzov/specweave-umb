---
id: US-003
feature: FS-369
title: Bulk Restore
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1340
    url: https://github.com/anton-abyzov/specweave/issues/1340
---
# US-003: Bulk Restore

**Feature**: [FS-369](./FEATURE.md)

**As an** admin,
**I want** a bulk restore endpoint that moves falsely rejected submissions back to PUBLISHED
**So that** I can remediate the ~185 false rejections without re-scanning.

---

## Acceptance Criteria

- [x] **AC-US3-01**: `POST /api/v1/admin/submissions/restore-published` finds submissions with PUBLISHED in state history but current state REJECTED
- [x] **AC-US3-02**: Restores them to PUBLISHED using existing scan data (no re-scan)
- [x] **AC-US3-03**: Creates audit trail state events

---

## Implementation

**Increment**: [0369-fix-duplicate-processing-false-rejections](../../../../../increments/0369-fix-duplicate-processing-false-rejections/spec.md)

## Tasks

_Completed_
