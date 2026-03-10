---
id: US-001
feature: FS-396
title: "Platform API for Pending SAST Scans (P1)"
status: completed
priority: P1
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** crawl-worker sast-scanner source."
project: vskill-platform
---

# US-001: Platform API for Pending SAST Scans (P1)

**Feature**: [FS-396](./FEATURE.md)

**As a** crawl-worker sast-scanner source
**I want** an API endpoint that returns PENDING and stuck RUNNING external scan rows
**So that** I can pull work items instead of relying on push dispatch

---

## Acceptance Criteria

- [x] **AC-US1-01**: `GET /api/v1/internal/pending-sast-scans` returns ExternalScanResult rows with status=PENDING, ordered by dispatchedAt ASC, limited to 50 per request
- [x] **AC-US1-02**: The endpoint also returns RUNNING rows where claimedAt is older than 15 minutes (stuck/timed-out scans eligible for re-claim)
- [x] **AC-US1-03**: The endpoint requires `X-Internal-Key` header matching `INTERNAL_BROADCAST_KEY` env var (same auth as other internal endpoints)
- [x] **AC-US1-04**: Response shape: `{ scans: [{ id, skillName, provider, status, dispatchedAt, claimedAt, claimedBy }] }`

---

## Implementation

**Increment**: [0396-pull-based-sast-scanner](../../../../../increments/0396-pull-based-sast-scanner/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
