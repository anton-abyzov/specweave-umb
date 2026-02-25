---
id: US-002
feature: FS-364
title: Admin bulk reprocesses rejected skills
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1328
    url: https://github.com/anton-abyzov/specweave/issues/1328
---
# US-002: Admin bulk reprocesses rejected skills

**Feature**: [FS-364](./FEATURE.md)

**As an** admin,
**I want** to select multiple rejected skills and reprocess them
**So that** platform errors get a fresh scan.

---

## Acceptance Criteria

- [x] **AC-US2-01**: Checkbox selection per row + select-all
- [x] **AC-US2-02**: Bulk action bar appears when items selected
- [x] **AC-US2-03**: Reprocess resets state to RECEIVED and re-enqueues

---

## Implementation

**Increment**: [0364-admin-rejected-skills-bulk-actions](../../../../../increments/0364-admin-rejected-skills-bulk-actions/spec.md)

## Tasks

_Completed_
