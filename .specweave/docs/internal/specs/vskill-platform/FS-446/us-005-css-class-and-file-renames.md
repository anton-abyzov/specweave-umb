---
id: US-005
feature: FS-446
title: "CSS Class and File Renames"
status: not_started
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** developer maintaining the codebase."
project: vskill-platform
---

# US-005: CSS Class and File Renames

**Feature**: [FS-446](./FEATURE.md)

**As a** developer maintaining the codebase
**I want** CSS classes and component file names using "author" renamed to "publisher"
**So that** styling selectors match the new terminology

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given `src/app/globals.css`, when inspected, then all `.author-*` CSS classes are renamed to `.publisher-*` (e.g., `.author-card` becomes `.publisher-card`)
- [ ] **AC-US5-02**: Given component files referencing `.author-*` class names in JSX, when inspected, then they reference the new `.publisher-*` class names
- [ ] **AC-US5-03**: Given `src/app/components/AuthorLink.tsx`, when inspected, then the file is renamed to `PublisherLink.tsx`
- [ ] **AC-US5-04**: Given `src/app/authors/AuthorsSearch.tsx` and `src/app/authors/[name]/AuthorSkillsList.tsx`, when the pages are moved to `src/app/publishers/`, then these component files are renamed to `PublishersSearch.tsx` and `PublisherSkillsList.tsx` respectively

---

## Implementation

**Increment**: [0446-rename-authors-to-publishers](../../../../../increments/0446-rename-authors-to-publishers/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Rename AuthorLink component to PublisherLink with skillName prop
- [x] **T-005**: Rename CSS classes from .author-* to .publisher-* and update all JSX references
