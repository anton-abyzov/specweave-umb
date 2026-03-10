---
id: US-001
feature: FS-465
title: Unified Workspace Shell (P0)
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 41
    url: https://github.com/anton-abyzov/vskill/issues/41
---

# US-001: Unified Workspace Shell (P0)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** a single workspace page with a left rail navigation
**So that** I can switch between editing, testing, running, and viewing history without page navigations

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a skill exists, when navigating to /skills/:plugin/:skill, then a SkillWorkspace route renders replacing the 4 separate pages (SkillDetailPage, BenchmarkPage, ComparisonPage, HistoryPage)
- [ ] **AC-US1-02**: Given the workspace is open, when viewing the left rail, then 5 icon buttons (Editor, Tests, Run, History, Deps) are visible in a 48px-wide rail and clicking each switches the active panel
- [ ] **AC-US1-03**: Given the workspace is open, when viewing the WorkspaceHeader, then it shows breadcrumb (plugin > skill), pass rate summary badge, total assertion count, and active model info
- [ ] **AC-US1-04**: Given a panel is active, when the URL is shared or refreshed, then the query param ?panel=tests|editor|run|history|deps deep-links to that specific panel
- [ ] **AC-US1-05**: Given the workspace is open, when pressing Ctrl+1 through Ctrl+5, then the corresponding panel activates (1=Editor, 2=Tests, 3=Run, 4=History, 5=Deps)

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
