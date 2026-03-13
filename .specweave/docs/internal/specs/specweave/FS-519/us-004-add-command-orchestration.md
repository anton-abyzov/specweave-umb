---
id: US-004
feature: FS-519
title: "Add Command Orchestration"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-004: Add Command Orchestration

**Feature**: [FS-519](./FEATURE.md)

**As a** developer
**I want** a single `specweave get <source>` command that orchestrates parsing, cloning, registration, and initialization
**So that** adding a repo is a one-step operation

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given the command `specweave get org/repo`, when executed in an umbrella workspace, then the repo is cloned to `repositories/org/repo/`, registered in config, and `specweave init` is run on it
- [x] **AC-US4-02**: Given `--no-init` is passed, when the command runs, then `specweave init` is not executed on the cloned repo
- [x] **AC-US4-03**: Given a local path `./my-service` that exists and has a `.git` directory, when `specweave get ./my-service` runs in an umbrella workspace, then the repo is registered in config without cloning (using `detectRepository()` to extract owner/repo)
- [x] **AC-US4-04**: Given `--yes` is passed, when the command runs, then no confirmation prompts are shown
- [x] **AC-US4-05**: Given the directory exists but is NOT registered in config, when `specweave get org/repo` runs, then the command skips clone but completes registration and init

---

## Implementation

**Increment**: [0519-specweave-add-command](../../../../../increments/0519-specweave-add-command/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
