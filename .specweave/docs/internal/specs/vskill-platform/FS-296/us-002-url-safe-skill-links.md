---
id: US-002
feature: FS-296
title: URL-Safe Skill Links
status: complete
priority: P2
created: 2026-02-21
project: vskill-platform
---
# US-002: URL-Safe Skill Links

**Feature**: [FS-296](./FEATURE.md)

user browsing skills on the homepage or using the search palette
**I want** skill links to work even when skill names contain special characters
**So that** clicking a trending skill or search result always navigates to the correct page

---

## Acceptance Criteria

- [x] **AC-US2-01**: Homepage trending skill links use `encodeURIComponent(skill.name)` in the href
- [x] **AC-US2-02**: SearchPalette skill result links use `encodeURIComponent(r.name)` in the href

---

## Implementation

**Increment**: [0296-strip-prefix-rollout-fixes](../../../../../increments/0296-strip-prefix-rollout-fixes/spec.md)

