---
id: FS-495
title: "Comparison Progress Observability"
type: feature
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
lastUpdated: 2026-03-11
tldr: "The compare endpoint wraps 3 sequential LLM calls (skill generation, baseline generation, rubric scoring) in a single `withHeartbeat()` that emits the same generic 'comparing...' message for 3-4 minutes."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-157'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-157'
    syncedAt: '2026-03-11T22:59:30.763Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 563
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/563'
    syncedAt: '2026-03-11T22:59:38.994Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Comparison Progress Observability

## TL;DR

**What**: The compare endpoint wraps 3 sequential LLM calls (skill generation, baseline generation, rubric scoring) in a single `withHeartbeat()` that emits the same generic "comparing..." message for 3-4 minutes.
**Status**: completed | **Priority**: P1
**User Stories**: 5

## Overview

The compare endpoint wraps 3 sequential LLM calls (skill generation, baseline generation, rubric scoring) in a single `withHeartbeat()` that emits the same generic "comparing..." message for 3-4 minutes. Users see no phase differentiation and cannot tell which step is executing or how far along the comparison is.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0495-comparison-progress-observability](../../../../../increments/0495-comparison-progress-observability/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Dynamic Heartbeat SSE Helper](./us-001-dynamic-heartbeat-sse-helper.md)
- [US-002: Progress Callback in Comparator](./us-002-progress-callback-in-comparator.md)
- [US-003: Wire Dynamic Heartbeat in Compare Endpoint](./us-003-wire-dynamic-heartbeat-in-compare-endpoint.md)
- [US-004: ProgressLog Phase Support](./us-004-progresslog-phase-support.md)
- [US-005: ProgressLog on ComparisonPage](./us-005-progresslog-on-comparisonpage.md)
