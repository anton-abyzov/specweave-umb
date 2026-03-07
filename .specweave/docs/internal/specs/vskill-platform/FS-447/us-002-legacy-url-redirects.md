---
id: US-002
feature: FS-447
title: Legacy URL Redirects
status: complete
priority: P0
created: 2026-03-07
project: vskill-platform
---
# US-002: Legacy URL Redirects

**Feature**: [FS-447](./FEATURE.md)

developer
**I want** old flat-slug URLs (`/skills/dailydotdev-daily`) to redirect to the new hierarchical URL
**So that** existing bookmarks, README badges, and external links continue to work

---

## Acceptance Criteria

- [x] **AC-US2-01**: ~~Given a skill with `legacySlug = "dailydotdev-daily"`, when a request hits `/skills/dailydotdev-daily`, then the server responds with a 301 redirect to `/skills/dailydotdev/daily/daily`~~ — DESCOPED: No backward compat needed per user decision; old routes removed entirely
- [x] **AC-US2-02**: Given the data migration, when it runs on existing skills, then every skill row has `legacySlug` populated with its current flat `name` value before the name is updated to hierarchical format
- [x] **AC-US2-03**: ~~Given the redirect route, when a slug matches no `legacySlug` and no hierarchical skill, then a 404 page is shown~~ — DESCOPED: Old routes removed entirely
- [x] **AC-US2-04**: ~~Given KV alias entries, when the migration runs, then `skill:alias:{legacySlug}` KV keys point to the new `owner/repo/skillSlug` value for fast redirect resolution without DB lookup~~ — DESCOPED: No KV aliases needed without legacy redirects

---

## Implementation

**Increment**: [0447-hierarchical-skill-urls](../../../../../increments/0447-hierarchical-skill-urls/spec.md)

