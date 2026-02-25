---
id: US-001
feature: FS-366
title: Orphan Skill Cleanup on Re-submission
status: not_started
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1330
    url: https://github.com/anton-abyzov/specweave/issues/1330
---
# US-001: Orphan Skill Cleanup on Re-submission

**Feature**: [FS-366](./FEATURE.md)

**As a** platform operator,
**I want** stale Skill records to be automatically deprecated when a skill is re-submitted
**So that** the search index and registry only surface the latest version.

---

## Acceptance Criteria

- [ ] **AC-US1-01**: When a submission is created for a repo+skillName that already has a published Skill record, the old Skill record gets `isDeprecated = true` within the same transaction
- [ ] **AC-US1-02**: Orphan cleanup uses one `findMany` + one `updateMany` Prisma query (no N+1)
- [ ] **AC-US1-03**: Cleanup runs inside the existing batch submission flow in `POST /api/v1/submissions` -- no separate cron job
- [ ] **AC-US1-04**: Skills that are NOT being re-submitted are never touched by the cleanup logic
- [ ] **AC-US1-05**: The cleanup is idempotent -- running it multiple times for the same submission produces the same result

---

## Implementation

**Increment**: [0366-orphan-cleanup-install-tracking](../../../../../increments/0366-orphan-cleanup-install-tracking/spec.md)

## Tasks

_Not started_
