---
id: US-001
feature: FS-521
title: Integration Health Check at Setup Time (P1)
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer setting up external sync."
project: specweave
external_tools:
  jira:
    key: SWE2E-248
  ado:
    id: 194
---

# US-001: Integration Health Check at Setup Time (P1)

**Feature**: [FS-521](./FEATURE.md)

**As a** developer setting up external sync
**I want** SpecWeave to automatically run health checks after sync-setup completes
**So that** I catch misconfigurations (wrong credentials, missing permissions, invalid project keys) immediately, not during the first sync attempt

---

## Acceptance Criteria

- [x] **AC-US1-01**: When `specweave sync-setup` completes successfully, integration health checks run automatically for the configured provider(s) and results are displayed
- [x] **AC-US1-02**: Health check results include actionable fix suggestions for each failing check (e.g., "Grant Edit Issues permission in JIRA project settings")
- [x] **AC-US1-03**: A standalone `specweave sync-health` CLI command runs health checks on-demand and returns exit code 0 for healthy, 1 for failures

---

## Implementation

**Increment**: [0521-external-integration-smart-linking](../../../../../increments/0521-external-integration-smart-linking/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
