---
id: US-012
feature: FS-398
title: "Fix ADO getAdoPat Sync vs Async Mismatch (P1)"
status: completed
priority: P0
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** developer."
project: specweave
---

# US-012: Fix ADO getAdoPat Sync vs Async Mismatch (P1)

**Feature**: [FS-398](./FEATURE.md)

**As a** developer
**I want** the ADO PAT provider to be called consistently
**So that** PAT retrieval doesn't fail silently

---

## Acceptance Criteria

- [x] **AC-US12-01**: `sync-coordinator.ts` ADO sync path at line 769 calls `getAdoPat()` consistently (currently missing `await` while line 247 uses `await`)

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
