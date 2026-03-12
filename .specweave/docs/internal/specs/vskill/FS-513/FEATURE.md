---
id: FS-513
title: 'Skill Studio: eval history redesign + comparison fix'
type: feature
status: active
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12T00:00:00.000Z
tldr: >-
  The comparison mode ('Compare All') in Skill Studio's eval system is broken at
  the per-case level.
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-190
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-190'
    syncedAt: '2026-03-12T07:02:24.583Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 1124
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1124
    syncedAt: '2026-03-12T07:02:30.822Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-12'
---

# Skill Studio: eval history redesign + comparison fix

## TL;DR

**What**: The comparison mode ("Compare All") in Skill Studio's eval system is broken at the per-case level.
**Status**: active | **Priority**: P1
**User Stories**: 3

## Overview

The comparison mode ("Compare All") in Skill Studio's eval system is broken at the per-case level. The comparison endpoint (`/api/skills/:plugin/:skill/compare`) emits `outputs_ready` and `comparison_scored` SSE events, but the client's `handleSSEEvent` only handles `output_ready` (singular), `assertion_result`, and `case_complete` -- events that the comparison endpoint never sends. As a result, per-case cards render empty during comparison runs (no assertions, no pass rate).

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0513-skill-studio-eval-history-redesign](../../../../../increments/0513-skill-studio-eval-history-redesign/spec.md) | ⏳ active | 2026-03-12 |

## User Stories

- [US-001: Fix comparison mode per-case SSE rendering (P0 -- BUG)](./us-001-fix-comparison-mode-per-case-sse-rendering-p0-bug.md)
- [US-002: Split-lane timeline for per-case eval history (P1)](./us-002-split-lane-timeline-for-per-case-eval-history-p1.md)
- [US-003: Dual-line MiniTrend sparkline (P1)](./us-003-dual-line-minitrend-sparkline-p1.md)
