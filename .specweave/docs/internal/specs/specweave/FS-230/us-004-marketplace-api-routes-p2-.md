---
id: US-004
feature: FS-230
title: "Marketplace API Routes (P2)"
status: completed
priority: P1
created: "2026-02-16T00:00:00.000Z"
tldr: "**As a** dashboard client
**I want** REST endpoints for marketplace data and scanner control
**So that** the frontend can fetch, filter, and manage the pipeline."
project: specweave
---

# US-004: Marketplace API Routes (P2)

**Feature**: [FS-230](./FEATURE.md)

**As a** dashboard client
**I want** REST endpoints for marketplace data and scanner control
**So that** the frontend can fetch, filter, and manage the pipeline

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given GET /api/marketplace/scanner/status, when called, then returns worker health and scan statistics
- [x] **AC-US4-02**: Given GET /api/marketplace/queue with status filter, when called, then returns paginated results (20/page default)
- [x] **AC-US4-03**: Given POST /api/marketplace/queue/:id/approve, when called, then updates submission to verified
- [x] **AC-US4-04**: Given GET /api/marketplace/insights, when called, then returns aggregated discovery timeline and pass/fail rates
- [x] **AC-US4-05**: Given POST /api/marketplace/scanner/start, when called, then launches scanner worker via job manager

---

## Implementation

**Increment**: [0230-marketplace-scanner-dashboard](../../../../../increments/0230-marketplace-scanner-dashboard/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
