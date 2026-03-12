---
id: US-001
feature: FS-447
title: Hierarchical Skill URLs
status: complete
priority: P0
created: 2026-03-07
project: vskill-platform
external:
  github:
    issue: 1505
    url: "https://github.com/anton-abyzov/specweave/issues/1505"
---
# US-001: Hierarchical Skill URLs

**Feature**: [FS-447](./FEATURE.md)

user
**I want** skill URLs to follow the format `/skills/{owner}/{repo}/{skill-slug}`
**So that** I can identify the source repository directly from the URL

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill from `github.com/dailydotdev/daily` with SKILL.md in `plugins/news/skills/daily/SKILL.md`, when I visit `/skills/dailydotdev/daily/daily`, then the skill detail page renders correctly
- [x] **AC-US1-02**: Given Prisma schema, when the migration runs, then `Skill` model has new columns `ownerSlug`, `repoSlug`, `skillSlug`, and `legacySlug` (all non-null after migration), and the unique constraint is on `(ownerSlug, repoSlug, skillSlug)` instead of flat `name`
- [x] **AC-US1-03**: Given the `Skill.name` field, when a skill is created or updated, then `name` stores the format `owner/repo/skillSlug` (e.g., `dailydotdev/daily/daily`)
- [x] **AC-US1-04**: Given Next.js App Router, when the route `/skills/[owner]/[repo]/[skillSlug]` is requested, then the page resolves the skill by the three path segments and renders the detail page with correct badge URLs, metadata, and OG tags
- [x] **AC-US1-05**: Given KV cache entries, when a skill is published or updated, then the KV key uses the hierarchical format `skill:owner/repo/skillSlug` instead of `skill:flat-slug`

---

## Implementation

**Increment**: [0447-hierarchical-skill-urls](../../../../../increments/0447-hierarchical-skill-urls/spec.md)

