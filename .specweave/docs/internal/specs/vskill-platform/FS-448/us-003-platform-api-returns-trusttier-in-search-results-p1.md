---
id: US-003
feature: FS-448
title: Platform API returns trustTier in search results (P1)
status: completed
priority: P1
created: 2026-03-07
tldr: "**As the** vskill CLI."
project: vskill-platform
related_projects:
  - vskill
external:
  github:
    issue: 58
    url: "https://github.com/anton-abyzov/vskill-platform/issues/58"
---

# US-003: Platform API returns trustTier in search results (P1)

**Feature**: [FS-448](./FEATURE.md)

**As the** vskill CLI
**I want** the `/api/v1/skills/search` endpoint to return `trustTier` for each skill
**So that** badges can be rendered client-side without additional API calls

---

## Acceptance Criteria

- [x] **AC-US3-01**: Postgres search results include trustTier from the Skill table
- [x] **AC-US3-02**: Edge KV search index entries include trustTier (sharded index)
- [x] **AC-US3-03**: Blocked skills enriched via BlocklistEntry set trustTier to "T0"
- [x] **AC-US3-04**: CLI client maps `trustTier` from raw API response to `SkillSearchResult.trustTier`

---

## Implementation

**Increment**: [0448-trust-badges-find](../../../../../increments/0448-trust-badges-find/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
