---
id: US-006
feature: FS-523
title: "Consolidate Dynamic gray-matter Import to Static"
status: not_started
priority: P1
created: 2026-03-14
tldr: "**As a** SpecWeave maintainer."
project: specweave
---

# US-006: Consolidate Dynamic gray-matter Import to Static

**Feature**: [FS-523](./FEATURE.md)

**As a** SpecWeave maintainer
**I want** `gray-matter` imported statically at the top of `living-docs-sync.ts`
**So that** the import style is consistent and there is no duplicated dynamic import

---

## Acceptance Criteria

- [ ] **AC-US6-01**: Given `living-docs-sync.ts`, when checking imports, then `gray-matter` is imported via a static `import` statement at the top of the file
- [ ] **AC-US6-02**: Given the file contents, when searching for `await import('gray-matter')`, then zero occurrences exist

---

## Implementation

**Increment**: [0523-living-docs-sync-cleanup](../../../../../increments/0523-living-docs-sync-cleanup/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
