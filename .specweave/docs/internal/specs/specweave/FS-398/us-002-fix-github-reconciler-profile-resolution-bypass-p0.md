---
id: US-002
feature: FS-398
title: "Fix GitHub Reconciler Profile Resolution Bypass (P0)"
status: completed
priority: P0
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** user with profile-based sync configuration."
project: specweave
---

# US-002: Fix GitHub Reconciler Profile Resolution Bypass (P0)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with profile-based sync configuration
**I want** the GitHub reconciler to respect profile configs
**So that** reconciliation works for users who configured sync via profiles

---

## Acceptance Criteria

- [x] **AC-US2-01**: `github-reconciler.ts` line 94 uses `isProviderEnabled(config, 'github')` instead of `config.sync?.github?.enabled ?? false` which bypasses profile-based detection
- [x] **AC-US2-02**: All three reconcilers (GitHub, JIRA, ADO) use consistent provider detection via `isProviderEnabled()`

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
