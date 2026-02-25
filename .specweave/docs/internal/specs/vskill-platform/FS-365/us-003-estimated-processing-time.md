---
id: US-003
feature: FS-365
title: Estimated Processing Time
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1335
    url: https://github.com/anton-abyzov/specweave/issues/1335
---
# US-003: Estimated Processing Time

**Feature**: [FS-365](./FEATURE.md)

**As a** submitter,
**I want** to see how long until my submission is processed (~Xm)
**So that** I can set expectations.

---

## Acceptance Criteria

- [x] **AC-US3-01**: Active submissions show estimated wait time below position badge
- [x] **AC-US3-02**: Estimate based on recent throughput (avgProcessingTimeMs from last 6h metrics)
- [x] **AC-US3-03**: Format: `~Xs` (<1m), `~Xm` (1-60m), `~Xh` (>60m)

---

## Implementation

**Increment**: [0365-queue-position-ux](../../../../../increments/0365-queue-position-ux/spec.md)

## Tasks

_Completed_
