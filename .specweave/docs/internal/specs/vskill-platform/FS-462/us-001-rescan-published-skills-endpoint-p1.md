---
id: US-001
feature: FS-462
title: "Rescan Published Skills Endpoint (P1)"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** platform admin."
project: vskill-platform
external:
  github:
    issue: 42
    url: https://github.com/anton-abyzov/vskill-platform/issues/42
---

# US-001: Rescan Published Skills Endpoint (P1)

**Feature**: [FS-462](./FEATURE.md)

**As a** platform admin
**I want** an API endpoint that re-queues published skills with low trust tiers for full scanning
**So that** skills stuck at T1/T2 get elevated to their proper trust tier after LLM analysis

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a POST to `/api/v1/admin/rescan-published` with valid auth, when called with `{ "dryRun": true }`, then it returns counts of eligible T1/T2 published skills without creating any records
- [x] **AC-US1-02**: Given a live (non-dry-run) call, when executed, then it creates new Submission records in RECEIVED state for up to 500 eligible published skills and enqueues them to SUBMISSION_QUEUE
- [x] **AC-US1-03**: Given published skills that already have a pending Submission (state not in a terminal state), when the endpoint runs, then those skills are skipped to avoid duplicate pipeline runs
- [x] **AC-US1-04**: Given published skills with trustTier T0 (blocked) or that are on the active blocklist, when the endpoint runs, then those skills are skipped
- [x] **AC-US1-05**: Given the optional body parameter `{ "skipExistingT2": true }`, when the endpoint runs, then skills that already have a Tier 2 ScanResult are excluded from re-scanning

---

## Implementation

**Increment**: [0462-rescan-published-trust-elevation](../../../../../increments/0462-rescan-published-trust-elevation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement POST /api/v1/admin/rescan-published route with tests
