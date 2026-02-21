---
id: US-005
feature: FS-286
title: "Skill Descriptions in Wizard (P2)"
status: completed
priority: P1
created: "2026-02-21T00:00:00.000Z"
tldr: "**As a** CLI user choosing skills from a multi-skill repo
**I want** to see a brief description of each skill
**So that** I can make informed decisions about which skills to install."
project: vskill
---

# US-005: Skill Descriptions in Wizard (P2)

**Feature**: [FS-286](./FEATURE.md)

**As a** CLI user choosing skills from a multi-skill repo
**I want** to see a brief description of each skill
**So that** I can make informed decisions about which skills to install

---

## Acceptance Criteria

- [x] **AC-US5-01**: `DiscoveredSkill` interface includes optional `description` field
- [x] **AC-US5-02**: Discovery fetches the first non-empty, non-heading line from each SKILL.md as description (truncated to 80 chars)
- [x] **AC-US5-03**: Wizard checkbox list shows skill name with description as hint text (using existing `description` field on `CheckboxItem`)
- [x] **AC-US5-04**: Missing descriptions (fetch failure or empty content) gracefully fall back to no hint

---

## Implementation

**Increment**: [0286-vskill-install-ux](../../../../../increments/0286-vskill-install-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
