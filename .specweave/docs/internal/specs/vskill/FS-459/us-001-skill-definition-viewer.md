---
id: US-001
feature: FS-459
title: "Skill Definition Viewer"
status: completed
priority: P1
created: "2026-03-09T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 36
    url: "https://github.com/anton-abyzov/vskill/issues/36"
---

# US-001: Skill Definition Viewer

**Feature**: [FS-459](./FEATURE.md)

**As a** skill developer
**I want** to see the SKILL.md content prominently on the skill detail page with parsed frontmatter metadata
**So that** I can reference the skill definition while editing eval cases and reviewing benchmark results

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill with SKILL.md containing YAML frontmatter, when the SkillDetailPage loads, then the frontmatter fields (description, allowed-tools, model, context) are displayed as structured metadata cards above the body content
- [x] **AC-US1-02**: Given a skill with SKILL.md, when the page loads, then the markdown body (after frontmatter) is displayed in a styled monospace block below the metadata cards
- [x] **AC-US1-03**: Given the `allowed-tools` frontmatter field contains tool names, when rendered, then each tool name appears as an individual pill/chip tag
- [x] **AC-US1-04**: Given a SKILL.md with no YAML frontmatter (raw markdown only), when the page loads, then only the body content block is shown with no metadata cards and no errors
- [x] **AC-US1-05**: Given the skill definition viewer section, when the user interacts with it, then it is collapsible and defaults to expanded on page load

---

## Implementation

**Increment**: [0459-skill-eval-enhancements](../../../../../increments/0459-skill-eval-enhancements/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
