---
id: US-001
feature: FS-393
title: "Reduce Pending Submission Age Filter (P1)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-001: Reduce Pending Submission Age Filter (P1)

**Feature**: [FS-393](./FEATURE.md)

**As a** platform operator
**I want** the pending-submissions endpoint to return items after 30 seconds instead of 5 minutes
**So that** VMs can pick up and process new submissions much faster, reducing end-to-end latency

---

## Acceptance Criteria

- [x] **AC-US1-01**: `pending-submissions/route.ts` uses a 30-second age filter (`updatedAt < 30 seconds ago`) instead of the current 5-minute filter
- [x] **AC-US1-02**: The age filter value is configurable via an environment variable `PENDING_AGE_SECONDS` (default: 30) for operational flexibility
- [x] **AC-US1-03**: Existing tests for the pending-submissions endpoint pass with the updated filter value

---

## Implementation

**Increment**: [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
