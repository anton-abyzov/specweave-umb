---
id: US-001
feature: FS-421
title: Update Umbrella Documentation (P2)
status: completed
priority: P2
created: 2026-03-03
tldr: "**As a** SpecWeave umbrella user."
project: specweave-umb
external:
  github:
    issue: 1486
    url: https://github.com/anton-abyzov/specweave/issues/1486
---

# US-001: Update Umbrella Documentation (P2)

**Feature**: [FS-421](./FEATURE.md)

**As a** SpecWeave umbrella user
**I want** the umbrella README to document distributed sync and consolidation
**So that** I can understand how multi-repo sync routing works

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the umbrella README, when a user reads it, then it describes distributed vs centralized sync modes
- [x] **AC-US1-02**: Given the umbrella project config, when umbrella.projectName is set, then living docs route to a distinct umbrella folder

---

## Implementation

**Increment**: [0421-umbrella-docs-update](../../../../../increments/0421-umbrella-docs-update/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Document distributed vs centralized sync modes in README
- [x] **T-002**: Document umbrella.projectName configuration
