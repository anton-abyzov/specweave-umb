---
id: US-005
feature: FS-507
title: "Plugin Directory Full Update (P2)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill user."
project: vskill
---

# US-005: Plugin Directory Full Update (P2)

**Feature**: [FS-507](./FEATURE.md)

**As a** vskill user
**I want** plugin-dir sources to update all skills within the plugin, not just a single SKILL.md
**So that** multi-skill plugins from GitHub are fully synchronized

---

## Acceptance Criteria

- [x] **AC-US5-01**: When `entry.pluginDir === true`, the update re-discovers all `skills/*/SKILL.md` paths under the plugin using the GitHub Trees API
- [x] **AC-US5-02**: Each discovered skill file is fetched, scanned, and written to the agent's skill directory
- [x] **AC-US5-03**: The lockfile entry SHA is computed from the combined content of all skill files in the plugin
- [x] **AC-US5-04**: Agent file entries that no longer exist upstream (skill removed from plugin) are not deleted -- only additions and updates are applied

---

## Implementation

**Increment**: [0507-vskill-update-all-sources](../../../../../increments/0507-vskill-update-all-sources/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
