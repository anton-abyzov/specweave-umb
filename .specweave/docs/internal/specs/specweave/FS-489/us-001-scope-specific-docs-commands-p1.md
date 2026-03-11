---
id: US-001
feature: FS-489
title: "Scope-specific docs commands (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** developer using the SpecWeave dashboard."
project: specweave
external:
  github:
    issue: 1534
    url: https://github.com/anton-abyzov/specweave/issues/1534
---

# US-001: Scope-specific docs commands (P1)

**Feature**: [FS-489](./FEATURE.md)

**As a** developer using the SpecWeave dashboard
**I want** separate start/stop commands for Internal Docs and Public Docs
**So that** I can independently manage each documentation server

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given command-runner.ts ALLOWED_COMMANDS, when the dashboard loads, then commands `docs-internal-start`, `docs-internal-stop`, `docs-public-start`, `docs-public-stop` are all registered
- [x] **AC-US1-02**: Given `docs-internal-start` is executed, when the command runs, then it spawns `specweave docs preview` (internal scope, port 3015)
- [x] **AC-US1-03**: Given `docs-public-start` is executed, when the command runs, then it spawns `specweave docs public preview` (public scope, port 3016)
- [x] **AC-US1-04**: Given `docs-internal-stop` or `docs-public-stop` is executed, when the command runs, then it kills the Docusaurus process on the corresponding port (3015 or 3016)
- [x] **AC-US1-05**: Given the old `docs-preview-start` and `docs-preview-stop` commands, when the code is updated, then they are removed from ALLOWED_COMMANDS

---

## Implementation

**Increment**: [0489-dashboard-docs-services](../../../../../increments/0489-dashboard-docs-services/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add scope-specific commands to command-runner.ts
- [x] **T-005**: Build and manual smoke test
