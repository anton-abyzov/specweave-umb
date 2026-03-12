---
id: FS-452
title: Rejected skill detail view
type: feature
status: ready_for_review
priority: P1
created: 2026-03-07T00:00:00.000Z
lastUpdated: 2026-03-12T00:00:00.000Z
tldr: >-
  When a user navigates to a skill that was submitted but rejected during
  verification, the page currently shows a bare-bones amber `RejectedSkillView`
  component.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-169
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-169'
    syncedAt: '2026-03-12T00:15:36.789Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 797
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/797
    syncedAt: '2026-03-12T00:15:43.124Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-12'
---

# Rejected skill detail view

## TL;DR

**What**: When a user navigates to a skill that was submitted but rejected during verification, the page currently shows a bare-bones amber `RejectedSkillView` component.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 4

## Overview

When a user navigates to a skill that was submitted but rejected during verification, the page currently shows a bare-bones amber `RejectedSkillView` component. This view lacks critical context that would help the skill author understand what happened and what to do next: there is no rejection stage breakdown, no resubmission guidance, no scan failure details, and no way to see related submissions. This increment enriches the rejected skill detail page to be on par with the `BlockedSkillView` in terms of information density while giving authors a clear path forward.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0452-rejected-skill-detail-view](../../../../../increments/0452-rejected-skill-detail-view/spec.md) | ⏳ ready_for_review | 2026-03-07T00:00:00.000Z |

## User Stories

- [US-001: Rejection reason and stage visibility (P1)](./us-001-rejection-reason-and-stage-visibility-p1.md)
- [US-002: Repository and source context (P1)](./us-002-repository-and-source-context-p1.md)
- [US-003: Resubmission guidance (P2)](./us-003-resubmission-guidance-p2.md)
- [US-004: Rejection stage indicator (P2)](./us-004-rejection-stage-indicator-p2.md)
