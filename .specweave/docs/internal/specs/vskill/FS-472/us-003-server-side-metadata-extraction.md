---
id: US-003
feature: FS-472
title: "Server-Side Metadata Extraction"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** the activation test API route."
project: vskill
external:
  github:
    issue: 69
    url: "https://github.com/anton-abyzov/vskill/issues/69"
---

# US-003: Server-Side Metadata Extraction

**Feature**: [FS-472](./FEATURE.md)

**As a** the activation test API route
**I want** to extract skill name and tags from SKILL.md frontmatter
**So that** the classification phase has the metadata it needs without accessing the full description

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given a SKILL.md with frontmatter containing `name` and `metadata.tags`, when the activation-test endpoint is called, then name and tags are extracted and passed to `testActivation` as `SkillMeta`
- [ ] **AC-US3-02**: Given a SKILL.md with missing or empty tags, when metadata is extracted, then `tags` is an empty array and classification falls back to `should_activate`

---

## Implementation

**Increment**: [0472-activation-auto-classify](../../../../../increments/0472-activation-auto-classify/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-004**: Extract SkillMeta from SKILL.md frontmatter in api-routes.ts
