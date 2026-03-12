---
id: FS-511
title: "Fix ADO/JIRA Sync Bugs"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "Five bugs in the ADO and JIRA sync providers cause work items to remain stuck in wrong states, miss parent links, use wrong work item types, skip metadata fallbacks, and silently swallow transition failures."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-188'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-188'
    syncedAt: '2026-03-12T05:59:15.740Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1082
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1082'
    syncedAt: '2026-03-12T05:59:24.167Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix ADO/JIRA Sync Bugs

## TL;DR

**What**: Five bugs in the ADO and JIRA sync providers cause work items to remain stuck in wrong states, miss parent links, use wrong work item types, skip metadata fallbacks, and silently swallow transition failures.
**Status**: completed | **Priority**: P1
**User Stories**: 5

![Fix ADO/JIRA Sync Bugs illustration](assets/feature-fs-511.jpg)

## Overview

Five bugs in the ADO and JIRA sync providers cause work items to remain stuck in wrong states, miss parent links, use wrong work item types, skip metadata fallbacks, and silently swallow transition failures. All fixes target `src/sync/providers/ado.ts`, `src/sync/providers/jira.ts`, and `src/sync/sync-coordinator.ts` in the specweave repo.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0511-fix-ado-jira-sync](../../../../../increments/0511-fix-ado-jira-sync/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: ADO Process-Aware State Transitions (P1)](./us-001-ado-process-aware-state-transitions-p1.md)
- [US-002: ADO Parent Work Item Linking (P1)](./us-002-ado-parent-work-item-linking-p1.md)
- [US-003: ADO Process-Aware Work Item Types (P1)](./us-003-ado-process-aware-work-item-types-p1.md)
- [US-004: ADO Metadata Fallback for Closure (P2)](./us-004-ado-metadata-fallback-for-closure-p2.md)
- [US-005: JIRA Transition Warning on Skip (P2)](./us-005-jira-transition-warning-on-skip-p2.md)
