---
id: US-002
feature: FS-278
title: Fix AC progress comment posting
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1213
    url: "https://github.com/anton-abyzov/specweave/issues/1213"
---
# US-002: Fix AC progress comment posting

**Feature**: [FS-278](./FEATURE.md)

SpecWeave user who completes acceptance criteria
**I want** AC progress comments to be posted to the correct GitHub issues
**So that** GitHub issues reflect real-time progress on acceptance criteria

---

## Acceptance Criteria

- [x] **AC-US2-01**: `parseIssueLinks()` in `github-ac-comment-poster.ts` reads issue numbers from **metadata.json** (`github.issues[]` and `externalLinks.github.issues`) instead of spec.md frontmatter
- [x] **AC-US2-02**: When an AC is completed in spec.md, a progress comment is posted to the corresponding GitHub issue
- [x] **AC-US2-03**: The metadata.json path is derived from the spec.md path (sibling file in the same increment folder)

---

## Implementation

**Increment**: [0278-fix-github-sync-links-and-comments](../../../../../increments/0278-fix-github-sync-links-and-comments/spec.md)

