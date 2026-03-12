---
id: US-002
feature: FS-452
title: "Repository and source context (P1)"
status: completed
priority: P1
created: 2026-03-07T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill-platform
---

# US-002: Repository and source context (P1)

**Feature**: [FS-452](./FEATURE.md)

**As a** skill author
**I want** the rejected skill page to show the repository link and skill name prominently
**So that** I can quickly navigate to my source code and understand which submission this refers to

---

## Acceptance Criteria

- [x] **AC-US2-01**: The skill name is displayed as a heading in `owner/repo/skill` format, matching the URL structure
- [x] **AC-US2-02**: The repository URL is rendered as a clickable link opening in a new tab
- [x] **AC-US2-03**: Metadata generates proper `<title>` and OpenGraph tags for rejected skills (already implemented in `generateMetadata`)

---

## Implementation

**Increment**: [0452-rejected-skill-detail-view](../../../../../increments/0452-rejected-skill-detail-view/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
