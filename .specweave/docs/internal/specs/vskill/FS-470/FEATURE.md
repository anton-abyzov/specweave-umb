---
id: FS-470
title: Skill Studio Full Redesign
type: feature
status: ready_for_review
priority: P1
created: 2026-03-10T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  The local Skill Studio UI (React eval UI served by `vskill eval serve`) uses a
  sidebar navigation with separate page routes for each concern (Home, Create,
  Benchmark, Comparison, History).
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-78
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-78'
    syncedAt: '2026-03-10T08:18:31.511Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 143
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/143
    syncedAt: '2026-03-10T08:18:31.922Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Skill Studio Full Redesign

## TL;DR

**What**: The local Skill Studio UI (React eval UI served by `vskill eval serve`) uses a sidebar navigation with separate page routes for each concern (Home, Create, Benchmark, Comparison, History).
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 8

![Skill Studio Full Redesign illustration](assets/feature-fs-470.jpg)

## Overview

The local Skill Studio UI (React eval UI served by `vskill eval serve`) uses a sidebar navigation with separate page routes for each concern (Home, Create, Benchmark, Comparison, History). Selecting a skill navigates to an entirely separate workspace page with an icon-based LeftRail panel switcher. This multi-page navigation model is slow, loses context, and makes it hard to compare or quickly browse between skills. The UI needs a unified master-detail layout where the skill list is always visible and selecting a skill shows its details inline without full-page navigation.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md) | ⏳ ready_for_review | 2026-03-10 |

## User Stories

- [US-001: Master-Detail Split-Pane Layout](./us-001-master-detail-split-pane-layout.md)
- [US-002: Scrollable Skill List with Search and Filter](./us-002-scrollable-skill-list-with-search-and-filter.md)
- [US-003: Inline Skill Detail with Tabbed Panels](./us-003-inline-skill-detail-with-tabbed-panels.md)
- [US-004: New Skill Creation Button and Flow](./us-004-new-skill-creation-button-and-flow.md)
- [US-005: `vskill studio` CLI Command](./us-005-vskill-studio-cli-command.md)
- [US-006: Responsive Layout](./us-006-responsive-layout.md)
- [US-007: Category Icon Generation via Nano Banana Pro](./us-007-category-icon-generation-via-nano-banana-pro.md)
- [US-008: Empty States and Error Handling](./us-008-empty-states-and-error-handling.md)
