---
id: US-003
feature: FS-219
title: Migration Rollback
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1196
    url: https://github.com/anton-abyzov/specweave/issues/1196
---
# US-003: Migration Rollback

**Feature**: [FS-219](./FEATURE.md)

developer who ran the migration
**I want to** roll back to the original single-repo structure if something goes wrong
**So that** I don't lose my project state

---

## Acceptance Criteria

- [x] **AC-US3-01**: `specweave migrate-to-umbrella --rollback` restores the original single-repo structure from the backup
- [x] **AC-US3-02**: Rollback verifies the backup exists and is valid before proceeding
- [x] **AC-US3-03**: A migration log is maintained at `.specweave/logs/migration.log` recording all operations with timestamps

---

## Implementation

**Increment**: [0219-multi-repo-migrate](../../../../../increments/0219-multi-repo-migrate/spec.md)

