---
id: US-002
feature: FS-449
title: "CLI Display Fix (P1)"
status: completed
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** CLI user running `vskill find`."
project: vskill
related_projects: [vskill-platform]
---

# US-002: CLI Display Fix (P1)

**Feature**: [FS-449](./FEATURE.md)

**As a** CLI user running `vskill find`
**I want** search results to show the short skill name with a clear repo identifier
**So that** I can identify and install skills without seeing duplicated `owner/repo@owner/repo/skillSlug` text

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the `SkillSearchResult` interface in the CLI API client, when the type definition is inspected, then it includes `ownerSlug?: string`, `repoSlug?: string`, and `skillSlug?: string` fields.
- [x] **AC-US2-02**: Given `vskill find <query>` output, when results render in the terminal, then the label shows `ownerSlug/repoSlug@skillSlug` (or just `skillSlug` if slug fields are absent for backwards compatibility) instead of the current `owner/repo@owner/repo/skillSlug` duplication.
- [x] **AC-US2-03**: Given a skill with a hierarchical `name` field but missing slug fields in the API response, when `formatSkillId` renders the label, then it falls back gracefully to parsing `name` into segments rather than duplicating prefixes.

---

## Implementation

**Increment**: [0449-fix-skill-display-names](../../../../../increments/0449-fix-skill-display-names/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Add slug fields to CLI SkillSearchResult type
- [x] **T-008**: Fix CLI formatSkillId to use slug fields without duplication
- [x] **T-009**: Verify CLI graceful fallback for missing slug fields
