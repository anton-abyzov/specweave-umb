---
id: US-003
feature: FS-396
title: "Schema Migration for Claim Tracking (P1)"
status: completed
priority: P1
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** platform developer."
project: vskill-platform
---

# US-003: Schema Migration for Claim Tracking (P1)

**Feature**: [FS-396](./FEATURE.md)

**As a** platform developer
**I want** claimedAt and claimedBy columns on ExternalScanResult
**So that** the claim endpoint can track which worker owns each scan and detect stuck scans

---

## Acceptance Criteria

- [x] **AC-US3-01**: Prisma schema adds `claimedAt DateTime?` to ExternalScanResult model
- [x] **AC-US3-02**: Prisma schema adds `claimedBy String?` to ExternalScanResult model
- [x] **AC-US3-03**: Migration runs cleanly against the existing database (nullable columns, no data loss)
- [x] **AC-US3-04**: The `@@index([status])` index on ExternalScanResult is retained for efficient pending queries

---

## Implementation

**Increment**: [0396-pull-based-sast-scanner](../../../../../increments/0396-pull-based-sast-scanner/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
