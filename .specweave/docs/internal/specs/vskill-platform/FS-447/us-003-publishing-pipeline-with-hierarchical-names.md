---
id: US-003
feature: FS-447
title: Publishing Pipeline with Hierarchical Names
status: complete
priority: P0
created: 2026-03-07
project: vskill-platform
---
# US-003: Publishing Pipeline with Hierarchical Names

**Feature**: [FS-447](./FEATURE.md)

skill publisher
**I want** the publishing pipeline to generate hierarchical `owner/repo/skill-slug` names
**So that** newly submitted skills get correct URLs from the start

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a submission from `github.com/acme/tools` with SKILL.md at `plugins/linter/skills/eslint-helper/SKILL.md`, when `publishSkill` runs, then `Skill.name` is set to `acme/tools/eslint-helper` and `skillSlug` is `eslint-helper` (parent folder name of SKILL.md)
- [x] **AC-US3-02**: Given a submission with SKILL.md at the repository root (`SKILL.md`), when `publishSkill` runs, then `skillSlug` is derived from the repo name (e.g., repo `acme/my-skill` produces `skillSlug = "my-skill"`)
- [x] **AC-US3-03**: Given the new naming scheme, when `resolveSlug` is called, then it no longer needs hash-based collision disambiguation (owner/repo/slug is inherently unique), and the old `makeSlug` flat-slug function is deprecated
- [x] **AC-US3-04**: Given the `slug.ts` module, when updated, then a new `buildHierarchicalName(repoUrl, skillPath)` function computes `ownerSlug`, `repoSlug`, and `skillSlug` from the repo URL and SKILL.md path
- [x] **AC-US3-05**: Given email notifications (submitted, auto-approved, rejected), when sent, then skill names in subject lines and body text use the hierarchical format, and badge URLs point to the new 3-segment path

---

## Implementation

**Increment**: [0447-hierarchical-skill-urls](../../../../../increments/0447-hierarchical-skill-urls/spec.md)

