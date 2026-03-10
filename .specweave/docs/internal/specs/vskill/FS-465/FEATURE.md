---
id: FS-465
title: 'Skill Builder Redesign: Unified Workspace'
type: feature
status: planned
priority: P1
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  The eval-ui currently has 4 disconnected pages (SkillDetailPage 1068 lines,
  BenchmarkPage 647, ComparisonPage 381, HistoryPage 789) that force skill
  developers to navigate between separate routes to edit, test, run benchmarks,
  and review history.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-46
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-46'
    syncedAt: '2026-03-10T07:25:09.766Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 111
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/111
    syncedAt: '2026-03-10T07:25:10.225Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Skill Builder Redesign: Unified Workspace

## TL;DR

**What**: The eval-ui currently has 4 disconnected pages (SkillDetailPage 1068 lines, BenchmarkPage 647, ComparisonPage 381, HistoryPage 789) that force skill developers to navigate between separate routes to edit, test, run benchmarks, and review history.
**Status**: planned | **Priority**: P1
**User Stories**: 8

![Skill Builder Redesign: Unified Workspace illustration](assets/feature-fs-465.jpg)

## Overview

The eval-ui currently has 4 disconnected pages (SkillDetailPage 1068 lines, BenchmarkPage 647, ComparisonPage 381, HistoryPage 789) that force skill developers to navigate between separate routes to edit, test, run benchmarks, and review history. This fragmented workflow breaks the tight edit-test-iterate loop that is critical for skill quality. State is not shared between pages, so running a benchmark requires navigating away from the test case list, losing context.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md) | ⏳ planned | 2026-03-09 |

## User Stories

- [US-001: Unified Workspace Shell (P0)](./us-001-unified-workspace-shell-p0.md)
- [US-002: SKILL.md Editor with Live Preview (P1)](./us-002-skill-md-editor-with-live-preview-p1.md)
- [US-003: Test Case Management Panel (P0)](./us-003-test-case-management-panel-p0.md)
- [US-004: Assertion Health and Quality Indicators (P1)](./us-004-assertion-health-and-quality-indicators-p1.md)
- [US-005: Benchmark Execution Panel (P1)](./us-005-benchmark-execution-panel-p1.md)
- [US-006: History and Regression Detection Panel (P1)](./us-006-history-and-regression-detection-panel-p1.md)
- [US-007: Edit-Test-Iterate Tight Loop (P0)](./us-007-edit-test-iterate-tight-loop-p0.md)
- [US-008: Centralized State Management (P0)](./us-008-centralized-state-management-p0.md)
