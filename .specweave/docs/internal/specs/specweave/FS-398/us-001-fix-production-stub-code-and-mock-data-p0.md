---
id: US-001
feature: FS-398
title: "Fix Production Stub Code and Mock Data (P0)"
status: completed
priority: P0
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** developer using SpecWeave sync."
project: specweave
---

# US-001: Fix Production Stub Code and Mock Data (P0)

**Feature**: [FS-398](./FEATURE.md)

**As a** developer using SpecWeave sync
**I want** all sync code paths to execute real logic
**So that** external tool sync actually works end-to-end

---

## Acceptance Criteria

- [x] **AC-US1-01**: `sync-coordinator.ts` loadCompletionData() parses real task titles from tasks.md instead of using "Add mock data for demo" stub (line 838)
- [x] **AC-US1-02**: `external-item-sync-service.ts` commentOnlySync() posts comments to actual external APIs instead of just logging "TODO: Integrate with external tool APIs" (line 283-284)
- [x] **AC-US1-03**: `external-item-sync-service.ts` fullSync() implements real update logic instead of "TODO: Implement full sync logic" stub (line 346-350)

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
