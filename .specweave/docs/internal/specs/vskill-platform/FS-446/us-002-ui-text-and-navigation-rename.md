---
id: US-002
feature: FS-446
title: "UI Text and Navigation Rename"
status: not_started
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** site visitor."
project: vskill-platform
---

# US-002: UI Text and Navigation Rename

**Feature**: [FS-446](./FEATURE.md)

**As a** site visitor
**I want** all visible text reading "Authors" replaced with "Publishers"
**So that** the terminology is consistent throughout the interface

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given the desktop navigation bar in `layout.tsx`, when the page loads, then the nav link reads "Publishers" and points to `/publishers`
- [ ] **AC-US2-02**: Given the mobile navigation in `MobileNav.tsx`, when the menu opens, then the link reads "Publishers" and points to `/publishers`
- [ ] **AC-US2-03**: Given the publishers listing page, when rendered, then the page title, headings, and search placeholder use "Publishers" instead of "Authors"
- [ ] **AC-US2-04**: Given the publisher detail page, when rendered, then all headings and labels use "Publisher" instead of "Author"

---

## Implementation

**Increment**: [0446-rename-authors-to-publishers](../../../../../increments/0446-rename-authors-to-publishers/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Update navigation and page text from Authors to Publishers
