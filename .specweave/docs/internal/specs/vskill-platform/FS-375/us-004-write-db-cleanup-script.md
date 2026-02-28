---
id: US-004
feature: FS-375
title: Write DB cleanup script
status: complete
priority: P1
created: 2026-02-28
project: vskill-platform
---
# US-004: Write DB cleanup script

**Feature**: [FS-375](./FEATURE.md)

platform operator
**I want** a one-time DB cleanup script that removes all seeded fake skills from production
**So that** the production database only contains real pipeline-verified skills

---

## Acceptance Criteria

- [x] **AC-US4-01**: A `scripts/cleanup-seed-skills.ts` script is created that identifies and deletes skills matching the old seed data IDs/names
- [x] **AC-US4-02**: The script deletes associated `SkillVersion`, `AgentCompat`, and `MetricsSnapshot` records in the correct order (foreign key dependencies)
- [x] **AC-US4-03**: The script runs in dry-run mode by default (requires `--execute` flag to actually delete)
- [x] **AC-US4-04**: The script outputs a count of records that would be / were deleted
- [x] **AC-US4-05**: The script handles the case where some seed skills may have been replaced by real pipeline entries (skip those)

---

## Implementation

**Increment**: [0375-remove-fake-seed-data](../../../../../increments/0375-remove-fake-seed-data/spec.md)

