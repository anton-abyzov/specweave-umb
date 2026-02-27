---
id: US-001
feature: FS-386
title: View Source File Link
status: complete
priority: P1
created: 2026-02-27
project: vskill-platform
external:
  github:
    issue: 1416
    url: https://github.com/anton-abyzov/specweave/issues/1416
---
# US-001: View Source File Link

**Feature**: [FS-386](./FEATURE.md)

skill consumer browsing verified-skill.com
**I want** a direct link to the SKILL.md source file
**So that** I can quickly review the skill's source without navigating the repo manually

---

## Acceptance Criteria

- [x] **AC-US1-01**: Skill model has `skillPath` optional column in database
- [x] **AC-US1-02**: `publishSkill()` copies `skillPath` from Submission to Skill during publish
- [x] **AC-US1-03**: Skill detail page shows "Source" meta row with clickable deep-link to `{repoUrl}/blob/HEAD/{skillPath}`
- [x] **AC-US1-04**: When `skillPath` is null, "Source path unknown" placeholder is shown

---

## Implementation

**Increment**: [0386-skill-path-view-source](../../../../../increments/0386-skill-path-view-source/spec.md)

