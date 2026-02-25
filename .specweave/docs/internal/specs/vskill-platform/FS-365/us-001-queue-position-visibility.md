---
id: US-001
feature: FS-365
title: Queue Position Visibility
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1333
    url: https://github.com/anton-abyzov/specweave/issues/1333
---
# US-001: Queue Position Visibility

**Feature**: [FS-365](./FEATURE.md)

**As a** skill submitter,
**I want** to see my position in the queue (#N)
**So that** I know how many items are ahead of me.

---

## Acceptance Criteria

- [x] **AC-US1-01**: Active submissions show `#N` position badge (1-indexed, processing order)
- [x] **AC-US1-02**: Non-active submissions (published/rejected/dequeued) show `--` instead of position
- [x] **AC-US1-03**: Position is the first column in the queue table

---

## Implementation

**Increment**: [0365-queue-position-ux](../../../../../increments/0365-queue-position-ux/spec.md)

## Tasks

_Completed_
