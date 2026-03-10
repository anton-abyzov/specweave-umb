---
id: FS-466
title: 'Skill Builder: MD Preview & Per-Case History'
type: feature
status: planned
priority: P1
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: 'The Skill Builder workspace (localhost:3162) has two usability gaps.'
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-76
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-76'
    syncedAt: '2026-03-10T08:18:25.567Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 141
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/141
    syncedAt: '2026-03-10T08:18:25.942Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Skill Builder: MD Preview & Per-Case History

## TL;DR

**What**: The Skill Builder workspace (localhost:3162) has two usability gaps.
**Status**: planned | **Priority**: P1
**User Stories**: 4

![Skill Builder: MD Preview & Per-Case History illustration](assets/feature-fs-466.jpg)

## Overview

The Skill Builder workspace (localhost:3162) has two usability gaps. First, the SKILL.md editor's "Preview" pane renders the markdown body as a raw `<pre>` block instead of formatted HTML, making it no better than reading the source. Skill authors cannot visually verify their documentation without leaving the editor. Second, the TestsPanel shows only the latest run result for each test case. Viewing a case's execution history requires switching to the HistoryPanel (Ctrl+4), breaking the editing flow. Both issues slow down the skill authoring iteration loop.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0466-skill-builder-preview-history](../../../../../increments/0466-skill-builder-preview-history/spec.md) | ⏳ planned | 2026-03-09 |

## User Stories

- [US-001: Custom Markdown Renderer Utility](./us-001-custom-markdown-renderer-utility.md)
- [US-002: Real Markdown Preview in EditorPanel](./us-002-real-markdown-preview-in-editorpanel.md)
- [US-003: Per-Case Execution History in TestsPanel](./us-003-per-case-execution-history-in-testspanel.md)
- [US-004: Shared History Display Utilities](./us-004-shared-history-display-utilities.md)
