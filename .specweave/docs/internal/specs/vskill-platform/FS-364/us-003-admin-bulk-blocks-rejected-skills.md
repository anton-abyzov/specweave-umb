---
id: US-003
feature: FS-364
title: Admin bulk blocks rejected skills
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1329
    url: https://github.com/anton-abyzov/specweave/issues/1329
---
# US-003: Admin bulk blocks rejected skills

**Feature**: [FS-364](./FEATURE.md)

**As an** admin,
**I want** to select multiple rejected skills and block them with threat metadata
**So that** confirmed threats are added to the blocklist.

---

## Acceptance Criteria

- [x] **AC-US3-01**: Block dialog with threatType, severity, reason fields
- [x] **AC-US3-02**: Creates BlocklistEntry for each selected skill

---

## Implementation

**Increment**: [0364-admin-rejected-skills-bulk-actions](../../../../../increments/0364-admin-rejected-skills-bulk-actions/spec.md)

## Tasks

_Completed_
