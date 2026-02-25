---
id: US-004
feature: FS-367
title: User-Facing Staleness Warning
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1315
    url: https://github.com/anton-abyzov/specweave/issues/1315
---
# US-004: User-Facing Staleness Warning

**Feature**: [FS-367](./FEATURE.md)

skill submitter watching my submission
**I want** to see a staleness warning if my submission appears stuck
**So that** I know the platform is aware and working on recovery

---

## Acceptance Criteria

- [x] **AC-US4-01**: Client-side staleness threshold of 3 minutes based on `updatedAt` field
- [x] **AC-US4-03**: Recovery system trigger threshold remains 5 minutes (separate from UX threshold)
- [x] **AC-US4-04**: Staleness warning disappears once the submission progresses or is recovered

---

## Implementation

**Increment**: [0367-stuck-submission-detection](../../../../../increments/0367-stuck-submission-detection/spec.md)

