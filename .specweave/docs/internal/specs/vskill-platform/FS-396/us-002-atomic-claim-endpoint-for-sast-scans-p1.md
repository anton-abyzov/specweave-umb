---
id: US-002
feature: FS-396
title: "Atomic Claim Endpoint for SAST Scans (P1)"
status: completed
priority: P1
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** crawl-worker sast-scanner source."
project: vskill-platform
---

# US-002: Atomic Claim Endpoint for SAST Scans (P1)

**Feature**: [FS-396](./FEATURE.md)

**As a** crawl-worker sast-scanner source
**I want** an atomic claim endpoint that transitions PENDING -> RUNNING with claimedAt/claimedBy
**So that** multiple VMs cannot process the same scan simultaneously

---

## Acceptance Criteria

- [x] **AC-US2-01**: `POST /api/v1/internal/claim-sast-scan` accepts `{ scanId, claimedBy }` and atomically updates status PENDING->RUNNING with claimedAt=now and claimedBy set
- [x] **AC-US2-02**: The claim uses a Prisma `updateMany` with `where: { id, status: PENDING }` (or status=RUNNING with claimedAt >15min) to ensure atomicity -- returns `{ ok: false }` if already claimed
- [x] **AC-US2-03**: The endpoint requires `X-Internal-Key` header authentication
- [x] **AC-US2-04**: Response shape: `{ ok: true, scan: { id, skillName, provider, status } }` on success, `{ ok: false, reason: "already_claimed" }` on conflict

---

## Implementation

**Increment**: [0396-pull-based-sast-scanner](../../../../../increments/0396-pull-based-sast-scanner/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
