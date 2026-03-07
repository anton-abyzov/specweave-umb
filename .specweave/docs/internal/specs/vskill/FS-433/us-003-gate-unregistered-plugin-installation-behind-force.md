---
id: US-003
feature: FS-433
title: "Gate Unregistered Plugin Installation Behind --force"
status: completed
priority: P1
created: 2026-03-05
tldr: "**As a** plugin consumer."
project: vskill
---

# US-003: Gate Unregistered Plugin Installation Behind --force

**Feature**: [FS-433](./FEATURE.md)

**As a** plugin consumer
**I want** unregistered plugin selection without `--force` to be blocked with a warning
**So that** I do not accidentally install plugins that have not been platform-scanned

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a user selects an unregistered plugin in the picker without `--force`, when confirming the selection, then a warning is printed explaining the plugin is not in marketplace.json, only registered plugins proceed to install, and the user is offered repo re-submission
- [x] **AC-US3-02**: Given a user selects an unregistered plugin with `--force`, when confirming, then the plugin is installed via the existing extraction pipeline, the re-submission prompt is suppressed, and the lockfile entry uses `tier: "UNSCANNED"`
- [x] **AC-US3-03**: Given `--plugin <name>` targets an unregistered plugin without `--force`, when the command runs, then it prints a warning and does not install (explicit naming does not bypass the gate)
- [x] **AC-US3-04**: Given `--force` is used for an unregistered plugin, when the extraction pipeline runs, then the local Tier-1 scan still executes (only the marketplace registration requirement is bypassed)

---

## Implementation

**Increment**: [0433-marketplace-unregistered-plugin-discovery](../../../../../increments/0433-marketplace-unregistered-plugin-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Add --force gate and offerResubmission() helper
- [x] **T-006**: Add overrideSource parameter to installRepoPlugin()
- [x] **T-007**: Handle --plugin <name> targeting unregistered plugins
