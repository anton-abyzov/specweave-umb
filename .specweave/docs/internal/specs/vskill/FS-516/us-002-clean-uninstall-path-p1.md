---
id: US-002
feature: FS-516
title: "Clean uninstall path (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer uninstalling vskill plugins."
project: vskill
---

# US-002: Clean uninstall path (P1)

**Feature**: [FS-516](./FEATURE.md)

**As a** developer uninstalling vskill plugins
**I want** uninstall to remove skill directories from agent folders
**So that** plugins are cleanly removed without native system calls

---

## Acceptance Criteria

- [x] **AC-US2-01**: Uninstall removes skill directories from all detected agents' local and global skill dirs
- [x] **AC-US2-02**: No native uninstall CLI call is made during removal

---

## Implementation

**Increment**: [0516-remove-native-plugin-install](../../../../../increments/0516-remove-native-plugin-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: GREEN — Remove all native install code from add.ts and add.test.ts
