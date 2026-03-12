---
id: US-003
feature: FS-446
title: "Skill Display with publisher/skill-name Format"
status: not_started
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** user browsing skills."
project: vskill-platform
---

# US-003: Skill Display with publisher/skill-name Format

**Feature**: [FS-446](./FEATURE.md)

**As a** user browsing skills
**I want** skills displayed as `publisher/skill-name` with the publisher part being a clickable link
**So that** I can quickly identify who published a skill and navigate to their profile

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given a skill card or listing entry, when rendered, then the skill is displayed as `publisher/skill-name` (e.g., `specweave/architect`)
- [ ] **AC-US3-02**: Given the `publisher/skill-name` display, when the user clicks the publisher portion, then they are navigated to `/publishers/[publisher-name]`
- [ ] **AC-US3-03**: Given the skill detail page at `/skills/[name]`, when rendered, then the publisher attribution shows the `publisher/skill-name` format with a clickable publisher link
- [ ] **AC-US3-04**: Given the `AuthorLink` component, when renamed to `PublisherLink`, then all imports across the codebase are updated and the component renders the new format

---

## Implementation

**Increment**: [0446-rename-authors-to-publishers](../../../../../increments/0446-rename-authors-to-publishers/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Update skill listing page to display publisher/skill-name format
- [x] **T-010**: Update skill detail page and run final compile and test verification
