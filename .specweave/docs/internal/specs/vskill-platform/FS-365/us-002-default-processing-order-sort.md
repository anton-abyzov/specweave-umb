---
id: US-002
feature: FS-365
title: Default Processing Order Sort
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1334
    url: https://github.com/anton-abyzov/specweave/issues/1334
---
# US-002: Default Processing Order Sort

**Feature**: [FS-365](./FEATURE.md)

**As a** user,
**I want** the queue to default-sort by processing order
**So that** I see what's being processed next at the top.

---

## Acceptance Criteria

- [x] **AC-US2-01**: Default sort is `processingOrder asc` (priority DESC, createdAt ASC)
- [x] **AC-US2-02**: User can sort by any column (skillName, state, score, createdAt, updatedAt)
- [x] **AC-US2-03**: When filtering to "rejected" or "published", default sort changes to `updatedAt desc`

---

## Implementation

**Increment**: [0365-queue-position-ux](../../../../../increments/0365-queue-position-ux/spec.md)

## Tasks

_Completed_
