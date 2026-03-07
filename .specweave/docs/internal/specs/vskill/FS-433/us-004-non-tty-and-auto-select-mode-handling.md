---
id: US-004
feature: FS-433
title: "Non-TTY and Auto-Select Mode Handling"
status: completed
priority: P1
created: 2026-03-05
tldr: "**As a** plugin consumer using CI or scripted installs."
project: vskill
---

# US-004: Non-TTY and Auto-Select Mode Handling

**Feature**: [FS-433](./FEATURE.md)

**As a** plugin consumer using CI or scripted installs
**I want** unregistered plugins to be listed but skipped in non-interactive modes
**So that** automated pipelines are not broken by unscanned plugins

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given non-TTY mode with unregistered plugins detected, when the plugin list is printed, then unregistered plugins are listed with an `(unregistered)` label and a note to use `--force` to include them
- [x] **AC-US4-02**: Given `--yes` or `--all` flag with unregistered plugins detected, when auto-selection runs, then only registered plugins are auto-selected and unregistered plugins are skipped with a message mentioning `--force`
- [x] **AC-US4-03**: Given `--yes --force` together with unregistered plugins, when auto-selection runs, then all plugins (registered and unregistered) are installed

---

## Implementation

**Increment**: [0433-marketplace-unregistered-plugin-discovery](../../../../../increments/0433-marketplace-unregistered-plugin-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Non-TTY listing with (unregistered) label
- [x] **T-009**: Auto-select (--yes/--all) skips unregistered; --yes --force includes them
