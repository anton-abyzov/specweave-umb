---
id: FS-467
title: "Parallel Per-Case Benchmark Execution"
type: feature
status: ready_for_review
priority: P1
created: 2026-03-10
lastUpdated: 2026-03-11
tldr: "The eval-ui Skill Builder benchmark system executes all test cases sequentially through a single SSE stream."
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 18
    url: 'https://github.com/anton-abyzov/vskill/milestone/18'
externalLinks:
  jira:
    epicKey: 'SWE2E-115'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-115'
    syncedAt: '2026-03-10T09:49:40.948Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 180
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/180'
    syncedAt: '2026-03-10T09:49:41.601Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Parallel Per-Case Benchmark Execution

## TL;DR

**What**: The eval-ui Skill Builder benchmark system executes all test cases sequentially through a single SSE stream.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 6

![Parallel Per-Case Benchmark Execution illustration](assets/feature-fs-467.jpg)

## Overview

The eval-ui Skill Builder benchmark system executes all test cases sequentially through a single SSE stream. A global `isRunning: boolean` flag blocks the entire UI whenever any case is running, preventing users from running, viewing, or cancelling individual cases independently. Single-case runs cannot be cancelled on their own and are not saved to history. There is no concurrency control or parallel execution capability on the server.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md) | ⏳ ready_for_review | 2026-03-10 |

## User Stories

- [US-001: Run a Single Test Case Independently (P0)](./us-001-run-a-single-test-case-independently-p0.md)
- [US-002: Cancel a Running Case Independently (P0)](./us-002-cancel-a-running-case-independently-p0.md)
- [US-003: Parallel Bulk Execution with Concurrency Control (P1)](./us-003-parallel-bulk-execution-with-concurrency-control-p1.md)
- [US-004: Per-Case History Saving (P1)](./us-004-per-case-history-saving-p1.md)
- [US-005: Cancel All Running Cases (P1)](./us-005-cancel-all-running-cases-p1.md)
- [US-006: Independent UI State Per Case (P0)](./us-006-independent-ui-state-per-case-p0.md)
