---
id: US-004
feature: FS-521
title: Standalone Sync Health Command (P2)
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** DevOps engineer."
project: specweave
external_tools:
  jira:
    key: SWE2E-254
  ado:
    id: 210
---

# US-004: Standalone Sync Health Command (P2)

**Feature**: [FS-521](./FEATURE.md)

**As a** DevOps engineer
**I want** a `specweave sync-health` command that validates all configured integrations
**So that** I can include it in CI pipelines and scheduled checks to detect credential expiration or permission changes

---

## Acceptance Criteria

- [x] **AC-US4-01**: `specweave sync-health` checks all enabled providers (GitHub, JIRA, ADO) and displays results in a structured format
- [x] **AC-US4-02**: The command supports `--json` flag for machine-readable output suitable for CI pipelines
- [x] **AC-US4-03**: Exit code is 0 when all checks pass, 1 when any check fails, 2 when no providers are configured

---

## Implementation

**Increment**: [0521-external-integration-smart-linking](../../../../../increments/0521-external-integration-smart-linking/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
