---
id: US-VSK-001
feature: FS-435
title: "Flat install-sorted search results (P1)"
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As a** CLI user searching for skills."
project: vskill
related_projects: [vskill-platform]
external:
  github:
    issue: 14
    url: "https://github.com/anton-abyzov/vskill/issues/14"
---

# US-VSK-001: Flat install-sorted search results (P1)

**Feature**: [FS-435](./FEATURE.md)

**As a** CLI user searching for skills
**I want** results displayed as a flat list sorted by install count in a clean `repo@skill-name` format
**So that** I can quickly identify and install the most popular skills

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0435-find-command-redesign](../../../../../increments/0435-find-command-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Add formatInstalls utility and update SkillSearchResult type
- [x] **T-005**: Change default limit from 50 to 15
- [x] **T-006**: Rewrite findCommand TTY output to flat install-sorted list
- [x] **T-007**: Implement non-TTY tab-separated output and JSON vskillInstalls
