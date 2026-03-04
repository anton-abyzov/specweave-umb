---
id: US-001
feature: FS-411
title: "CLI Health Check Command"
status: completed
priority: P1
created: 2026-03-03
tldr: "**As a** DevOps engineer."
project: specweave
---

# US-001: CLI Health Check Command

**Feature**: [FS-411](./FEATURE.md)

**As a** DevOps engineer
**I want** a CLI health check command
**So that** I can verify all SpecWeave services are running correctly after deployment

---

## Acceptance Criteria

- [x] **AC-US1-01**: specweave health command checks config validity, plugin availability, and sync connectivity
- [x] **AC-US1-02**: Returns exit code 0 on success and non-zero on failure with diagnostic details
- [x] **AC-US1-03**: JSON output mode for CI/CD pipeline integration

---

## Implementation

**Increment**: [0411J-cli-health-check](../../../../../increments/0411J-cli-health-check/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
