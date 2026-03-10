---
id: FS-458
title: Eval Run History & A/B Benchmarking
type: feature
status: planned
priority: P1
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  The vskill eval system has basic benchmark history and A/B comparison, but the
  stored data lacks granularity (no per-case token breakdowns, no input/output
  token split, no baseline-only assertion results).
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-61
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-61'
    syncedAt: '2026-03-10T08:08:39.120Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 126
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/126
    syncedAt: '2026-03-10T08:08:40.089Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Eval Run History & A/B Benchmarking

## TL;DR

**What**: The vskill eval system has basic benchmark history and A/B comparison, but the stored data lacks granularity (no per-case token breakdowns, no input/output token split, no baseline-only assertion results).
**Status**: planned | **Priority**: P1
**User Stories**: 8

![Eval Run History & A/B Benchmarking illustration](assets/feature-fs-458.jpg)

## Overview

The vskill eval system has basic benchmark history and A/B comparison, but the stored data lacks granularity (no per-case token breakdowns, no input/output token split, no baseline-only assertion results). Users cannot filter history, compare arbitrary past runs, visuali

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md) | ⏳ planned | 2026-03-09 |

## User Stories

- [US-001: Enriched History Data Model (P1)](./us-001-enriched-history-data-model-p1.md)
- [US-002: Baseline-Only Run Mode (P1)](./us-002-baseline-only-run-mode-p1.md)
- [US-003: History Filtering (P1)](./us-003-history-filtering-p1.md)
- [US-004: Cross-Session Run Comparison (P1)](./us-004-cross-session-run-comparison-p1.md)
- [US-005: Trend Visualization (P2)](./us-005-trend-visualization-p2.md)
- [US-006: Rerun Capabilities (P2)](./us-006-rerun-capabilities-p2.md)
- [US-007: Frontend API Client Extensions (P2)](./us-007-frontend-api-client-extensions-p2.md)
- [US-008: Per-Test-Case History (P1)](./us-008-per-test-case-history-p1.md)
