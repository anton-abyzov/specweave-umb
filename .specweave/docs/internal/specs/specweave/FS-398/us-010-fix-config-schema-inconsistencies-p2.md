---
id: US-010
feature: FS-398
title: "Fix Config Schema Inconsistencies (P2)"
status: completed
priority: P0
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** user configuring sync."
project: specweave
---

# US-010: Fix Config Schema Inconsistencies (P2)

**Feature**: [FS-398](./FEATURE.md)

**As a** user configuring sync
**I want** config properties to be consistent between types and runtime code
**So that** configuration works as documented

---

## Acceptance Criteria

- [x] **AC-US10-01**: `config.ts` PartialSyncConfig interface includes `profiles` field to match actual config.json shape
- [x] **AC-US10-02**: StatusMapper.canUpdateExternal() defaults align with SyncCoordinator behavior (currently StatusMapper returns `false`, Coordinator falls back to `permissions.canUpsert`)
- [x] **AC-US10-03**: validateSyncConfigConsistency() validates profile-based configs, not just legacy format

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
