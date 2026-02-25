---
id: US-001
feature: FS-364
title: Admin views rejected skills
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1327
    url: https://github.com/anton-abyzov/specweave/issues/1327
---
# US-001: Admin views rejected skills

**Feature**: [FS-364](./FEATURE.md)

**As an** admin,
**I want** to see rejected skills categorized as "Security Issues" vs "Processing Errors"
**So that** I can focus on real threats.

---

## Acceptance Criteria

- [x] **AC-US1-01**: Rejected tab only visible when user is admin
- [x] **AC-US1-02**: Default category filter is "Security Issues"
- [x] **AC-US1-03**: Paginated with 20 items per page
- [x] **AC-US1-04**: Search by skill name with debounce

---

## Implementation

**Increment**: [0364-admin-rejected-skills-bulk-actions](../../../../../increments/0364-admin-rejected-skills-bulk-actions/spec.md)

## Tasks

_Completed_
