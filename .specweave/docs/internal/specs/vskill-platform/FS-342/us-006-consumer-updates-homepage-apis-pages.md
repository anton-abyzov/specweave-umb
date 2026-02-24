---
id: US-006
feature: FS-342
title: Consumer Updates (Homepage, APIs, Pages)
status: not-started
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-006: Consumer Updates (Homepage, APIs, Pages)

**Feature**: [FS-342](./FEATURE.md)

user browsing skills
**I want** pages to use efficient DB queries with proper pagination
**So that** the site stays fast even with thousands of skills

**ACs:**
- [x] AC-US6-01: Homepage uses `getPlatformStats()` + `getTrendingSkills(8)` — no full skill load
- [x] AC-US6-02: Skills browse page uses DB-level SKIP/TAKE pagination with total count
- [x] AC-US6-03: `/api/v1/skills` uses DB pagination + count query
- [x] AC-US6-04: `/api/v1/stats` returns KV-cached stats blob

---

## Acceptance Criteria

- [ ] **AC-US006-01**: Pending specification

---

## Implementation

**Increment**: [0342-db-first-skill-architecture](../../../../../increments/0342-db-first-skill-architecture/spec.md)

