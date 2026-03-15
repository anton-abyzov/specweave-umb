---
id: FS-526
title: "Test JIRA ADO Sync Hierarchy"
type: feature
status: ready_for_review
priority: P2
created: 2026-03-15
lastUpdated: 2026-03-15
tldr: "Minimal test increment to verify that user stories appear as child work items under their parent feature/epic in JIRA and ADO after the v1.0.453 sync fixes."
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-206'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-206'
    syncedAt: '2026-03-15T02:33:31.558Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1350
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1350'
    syncedAt: '2026-03-15T02:33:35.516Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Test JIRA ADO Sync Hierarchy

## TL;DR

**What**: Minimal test increment to verify that user stories appear as child work items under their parent feature/epic in JIRA and ADO after the v1.0.453 sync fixes.
**Status**: ready_for_review | **Priority**: P2
**User Stories**: 1

![Test JIRA ADO Sync Hierarchy illustration](assets/feature-fs-526.jpg)

## Overview

Minimal test increment to verify that user stories appear as child work items under their parent feature/epic in JIRA and ADO after the v1.0.453 sync fixes.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0526-test-jira-ado-sync](../../../../../increments/0526-test-jira-ado-sync/spec.md) | ⏳ ready_for_review | 2026-03-15 |

## User Stories

- [US-001: Verify sync hierarchy](./us-001-verify-sync-hierarchy.md)
