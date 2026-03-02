---
id: US-002
feature: FS-230
title: "Submission Queue (P1)"
status: completed
priority: P1
created: "2026-02-16T00:00:00.000Z"
tldr: "**As a** marketplace operator
**I want** discovered skills queued for automated security verification
**So that** only vetted skills reach verified status."
project: specweave
---

# US-002: Submission Queue (P1)

**Feature**: [FS-230](./FEATURE.md)

**As a** marketplace operator
**I want** discovered skills queued for automated security verification
**So that** only vetted skills reach verified status

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a discovered repo, when added to queue, then entry persists in `.specweave/state/skill-submissions.json`
- [x] **AC-US2-02**: Given a new submission, when autoScanOnDiscover is true, then Tier 1 regex scan runs automatically
- [x] **AC-US2-03**: Given a Tier 1 passed skill, when Tier 2 triggered, then consent gate checks before LLM analysis
- [x] **AC-US2-04**: Given corrupted queue JSON, when loaded, then auto-recovers from backup file
- [x] **AC-US2-05**: Given an operator action, when approve/reject called, then submission status updates with reason

---

## Implementation

**Increment**: [0230-marketplace-scanner-dashboard](../../../../../increments/0230-marketplace-scanner-dashboard/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
