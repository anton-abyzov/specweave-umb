---
id: US-001
feature: FS-417
title: "Update migrate-to-umbrella Help Text"
status: completed
priority: P2
created: 2026-03-03
tldr: "**As a** SpecWeave user."
project: specweave
---

# US-001: Update migrate-to-umbrella Help Text

**Feature**: [FS-417](./FEATURE.md)

**As a** SpecWeave user
**I want** the `migrate-to-umbrella --help` output to document the `--consolidate` flag and sync strategy modes
**So that** I can discover and use these features without consulting external docs

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given `specweave migrate-to-umbrella --help` is run, when the output is displayed, then it includes `--consolidate` with a description of consolidating orphaned increments
- [x] **AC-US1-02**: Given the CLI help is displayed, when a user reads it, then it mentions distributed vs centralized sync strategy modes

---

## Implementation

**Increment**: [0417J-update-cli-help-umbrella](../../../../../increments/0417J-update-cli-help-umbrella/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Verify --consolidate flag in help output
- [x] **T-002**: Add sync strategy mode documentation to help text
