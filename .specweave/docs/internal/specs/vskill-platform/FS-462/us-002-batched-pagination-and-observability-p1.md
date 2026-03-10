---
id: US-002
feature: FS-462
title: "Batched Pagination and Observability (P1)"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** platform admin."
project: vskill-platform
external:
  github:
    issue: 43
    url: https://github.com/anton-abyzov/vskill-platform/issues/43
---

# US-002: Batched Pagination and Observability (P1)

**Feature**: [FS-462](./FEATURE.md)

**As a** platform admin
**I want** the rescan endpoint to process in batches with clear progress reporting
**So that** I can safely re-scan 34k+ skills without overwhelming the queue or losing visibility

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given more than 500 eligible skills, when the endpoint completes a batch, then the response includes `"hasMore": true` and the caller repeats until `hasMore` is false
- [x] **AC-US2-02**: Given each created Submission, when the state is set to RECEIVED, then a SubmissionStateEvent audit record is created with trigger "rescan-published: trust elevation" and actor "system"
- [x] **AC-US2-03**: Given a request without valid X-Internal-Key header or SUPER_ADMIN Bearer token, when the endpoint is called, then it returns 401/403

---

## Implementation

**Increment**: [0462-rescan-published-trust-elevation](../../../../../increments/0462-rescan-published-trust-elevation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement POST /api/v1/admin/rescan-published route with tests
- [x] **T-002**: Deploy to production and run dry-run verification
