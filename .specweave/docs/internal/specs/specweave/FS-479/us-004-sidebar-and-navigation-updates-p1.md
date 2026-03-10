---
id: US-004
feature: FS-479
title: "Sidebar and Navigation Updates (P1)"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** docs site visitor."
project: specweave
---

# US-004: Sidebar and Navigation Updates (P1)

**Feature**: [FS-479](./FEATURE.md)

**As a** docs site visitor
**I want** the new pages to appear in the sidebar navigation
**So that** I can find them through browsing, not just search

---

## Acceptance Criteria

- [ ] **AC-US4-01**: `sidebars.ts` updated to include `skills/installation` in the Skills sidebar, positioned early (before the standards sections)
- [ ] **AC-US4-02**: `sidebars.ts` updated to include `skills/skill-studio` in the Skills sidebar
- [ ] **AC-US4-03**: `sidebars.ts` updated to include `skills/vskill-cli` in the Skills sidebar (under Ecosystem or Reference category)
- [ ] **AC-US4-04**: `docusaurus.config.ts` updated if any navbar items need adjustment for new pages
- [ ] **AC-US4-05**: All sidebar links resolve correctly (no 404s from sidebar navigation)

---

## Implementation

**Increment**: [0479-docs-skills-studio-install](../../../../../increments/0479-docs-skills-studio-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-005**: Update sidebars.ts and verify navigation links
