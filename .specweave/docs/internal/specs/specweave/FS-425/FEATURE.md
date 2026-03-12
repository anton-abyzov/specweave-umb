---
id: FS-425
title: Umbrella Sync E2E Verification
type: feature
status: active
priority: P2
created: "2026-03-04T00:00:00.000Z"
lastUpdated: "2026-03-05T00:00:00.000Z"
tldr: Verify that umbrella sync routing correctly routes GitHub issues, JIRA
  tickets, and ADO work items to per-child-repo targets based on the **Project**
  field in each user story.
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: WTTC-36
    epicUrl: "https://antonabyzov.atlassian.net/browse/WTTC-36"
    syncedAt: "2026-03-05T19:46:05.129Z"
    projectKey: WTTC
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 28
    featureUrl: "https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/28"
    syncedAt: "2026-03-05T19:46:05.712Z"
    organization: EasyChamp
    project: SpecWeaveSync
updated: 2026-03-05
external_tools:
  github:
    type: milestone
    id: 217
    url: "https://github.com/anton-abyzov/specweave/milestone/217"
---

# Umbrella Sync E2E Verification

## TL;DR

**What**: Verify that umbrella sync routing correctly routes GitHub issues, JIRA tickets, and ADO work items to per-child-repo targets based on the **Project** field in each user story.
**Status**: active | **Priority**: P2
**User Stories**: 1

## Overview

Verify that umbrella sync routing correctly routes GitHub issues, JIRA tickets, and ADO work items to per-child-repo targets based on the **Project** field in each user story.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0425-umbrella-sync-e2e-test](../../../../../increments/0425-umbrella-sync-e2e-test/spec.md) | ⏳ active | 2026-03-04 |

## User Stories

- [US-SPE-001: Specweave Repo Sync Verification](./us-spe-001-specweave-repo-sync-verification.md)

## Related Projects

This feature spans multiple projects:

- [vskill](../../vskill/FS-425/)
- [vskill-platform](../../vskill-platform/FS-425/)
