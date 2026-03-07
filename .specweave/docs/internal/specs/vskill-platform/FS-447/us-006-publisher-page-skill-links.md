---
id: US-006
feature: FS-447
title: Publisher Page Skill Links
status: complete
priority: P1
created: 2026-03-07
project: vskill-platform
---
# US-006: Publisher Page Skill Links

**Feature**: [FS-447](./FEATURE.md)

publisher page visitor
**I want** skill links on publisher profile pages to use the new hierarchical URL format
**So that** clicking a skill from a publisher page takes me to the correct `/skills/{owner}/{repo}/{skillSlug}` URL

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given the `PublisherSkillsList` component, when rendering skill cards, then each card's `href` uses `/skills/${ownerSlug}/${repoSlug}/${skillSlug}` instead of `/skills/${encodeURIComponent(skill.name)}`
- [x] **AC-US6-02**: Given the `TrendingSkills` component, when rendering skill links on the homepage, then links use the 3-segment hierarchical URL format
- [x] **AC-US6-03**: Given the `SearchPalette` component, when displaying search results, then result links navigate to `/skills/{owner}/{repo}/{skillSlug}`
- [x] **AC-US6-04**: Given the skill detail page badge markdown snippet, when displayed, then the badge link URL uses the hierarchical format (e.g., `https://verified-skill.com/skills/owner/repo/skill-slug`)

---

## Implementation

**Increment**: [0447-hierarchical-skill-urls](../../../../../increments/0447-hierarchical-skill-urls/spec.md)

