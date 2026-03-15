---
id: US-005
feature: FS-504
title: --yes Flag Auto-Pick (P2)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** script author or power user."
project: vskill
external_tools:
  jira:
    key: SWE2E-264
  ado:
    id: 211
---

# US-005: --yes Flag Auto-Pick (P2)

**Feature**: [FS-504](./FEATURE.md)

**As a** script author or power user
**I want** `--yes` to auto-select the first ranked non-blocked result
**So that** I can script installs without interactive prompts

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the `--yes` flag and multiple search results, then the CLI automatically selects the first non-blocked result after ranking (including exact-match priority) and proceeds with installation
- [x] **AC-US5-02**: Given the `--yes` flag and all results are blocked, then the CLI exits with code 1 and an error message

---

## Implementation

**Increment**: [0504-install-skill-discovery](../../../../../increments/0504-install-skill-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: `--yes` flag auto-selects first ranked non-blocked result
