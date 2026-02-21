---
id: US-003
feature: FS-292
title: Backward-Compatible Lookup
status: complete
priority: P2
created: 2026-02-21
project: vskill-platform
---
# US-003: Backward-Compatible Lookup

**Feature**: [FS-292](./FEATURE.md)

user who bookmarked a skill page under the old slug URL
**I want** old slugs to still resolve to the correct skill
**So that** existing links and references do not break

---

## Acceptance Criteria

- [x] **AC-US3-01**: `getPublishedSkill()` falls back to trying the old org-prefixed slug format when the clean slug is not found
- [x] **AC-US3-02**: Frontend skill detail pages (`/skills/[name]`) work with both old and new slug formats

---

## Implementation

**Increment**: [0292-skill-naming-strip-prefix](../../../../../increments/0292-skill-naming-strip-prefix/spec.md)

