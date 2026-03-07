---
id: US-002
feature: FS-433
title: "Display Unregistered Plugins in Picker UI"
status: completed
priority: P1
created: 2026-03-05
tldr: "**As a** plugin consumer."
project: vskill
---

# US-002: Display Unregistered Plugins in Picker UI

**Feature**: [FS-433](./FEATURE.md)

**As a** plugin consumer
**I want** unregistered plugins to appear in the checkbox picker with a visual indicator
**So that** I can distinguish them from verified marketplace plugins

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given 12 registered and 1 unregistered plugin, when the interactive picker is shown, then unregistered plugins appear at the bottom of the list with a yellow `(new -- not in marketplace.json)` label
- [x] **AC-US2-02**: Given unregistered plugins exist, when the picker header is displayed, then it shows `Marketplace: <name> -- 12 registered, 1 unregistered` with the unregistered count in yellow
- [x] **AC-US2-03**: Given unregistered plugins are present in the picker, when displayed, then they are unchecked by default

---

## Implementation

**Increment**: [0433-marketplace-unregistered-plugin-discovery](../../../../../increments/0433-marketplace-unregistered-plugin-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Integrate discovery call and build combined picker items
- [x] **T-004**: Partition selected indices into registered vs unregistered
