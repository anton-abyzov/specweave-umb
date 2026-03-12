---
id: US-002
feature: FS-428
title: "Interactive plugin selection"
status: completed
priority: P2
created: "2026-03-05T00:00:00.000Z"
tldr: "**As a** plugin user."
project: vskill
---

# US-002: Interactive plugin selection

**Feature**: [FS-428](./FEATURE.md)

**As a** plugin user
**I want** to see what will be installed and confirm before proceeding
**So that** I'm never surprised by what gets installed

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a single-plugin marketplace in TTY mode without `--yes`, when the user runs `vskill install`, then plugin name, version, and description are displayed and the user is prompted for confirmation before proceeding
- [x] **AC-US2-02**: Given the `--yes` flag is passed, when `vskill install` runs in any environment (TTY or CI), then confirmation is bypassed and install proceeds automatically
- [x] **AC-US2-03**: Given a call to `installPluginDir()`, when scanning begins, then a pre-install overview line showing the plugin name and source path/URL is printed before the "Collecting plugin files" message

---

## Implementation

**Increment**: [0428-plugin-install-reliability](../../../../../increments/0428-plugin-install-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Update tests for all changed modules
