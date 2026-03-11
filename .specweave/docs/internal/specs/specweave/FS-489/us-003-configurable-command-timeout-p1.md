---
id: US-003
feature: FS-489
title: "Configurable command timeout (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** developer starting a docs preview from the dashboard."
project: specweave
external:
  github:
    issue: 1536
    url: https://github.com/anton-abyzov/specweave/issues/1536
---

# US-003: Configurable command timeout (P1)

**Feature**: [FS-489](./FEATURE.md)

**As a** developer starting a docs preview from the dashboard
**I want** the client-side timeout to be long enough for docs commands
**So that** the command does not falsely report a timeout while npm install and Docusaurus startup are still running

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `useCommand` hook, when `execute` is called, then it accepts an optional `timeoutMs` parameter (defaults to 60000)
- [x] **AC-US3-02**: Given a docs start command is executed, when the timeout parameter is set to 300000 (300s), then the safety timeout fires at 300 seconds instead of 60
- [x] **AC-US3-03**: Given a non-docs command is executed, when no timeout override is provided, then the default 60-second timeout still applies
- [x] **AC-US3-04**: Given the timeout fires, when the command is still running, then the error message reflects the actual timeout duration (not hardcoded "60 seconds")

---

## Implementation

**Increment**: [0489-dashboard-docs-services](../../../../../increments/0489-dashboard-docs-services/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add optional timeoutMs to useCommand hook
- [x] **T-005**: Build and manual smoke test
