---
id: FS-462
title: Rescan Published Skills for Trust Elevation
type: feature
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  41% of published skills (34,342 out of 84,779) remain at trustTier T2
  ('maybe') because they were fast-approved via Tier 1 regex scan only, without
  Tier 2 LLM analysis.
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-74
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-74'
    syncedAt: '2026-03-10T08:18:18.733Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 139
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/139
    syncedAt: '2026-03-10T08:18:19.583Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Rescan Published Skills for Trust Elevation

## TL;DR

**What**: 41% of published skills (34,342 out of 84,779) remain at trustTier T2 ("maybe") because they were fast-approved via Tier 1 regex scan only, without Tier 2 LLM analysis.
**Status**: completed | **Priority**: P1
**User Stories**: 2

![Rescan Published Skills for Trust Elevation illustration](assets/feature-fs-462.jpg)

## Overview

41% of published skills (34,342 out of 84,779) remain at trustTier T2 ("maybe") because they were fast-approved via Tier 1 regex scan only, without Tier 2 LLM analysis. These skills need full re-scanning to elevate to T3 ("verified"), improving overall trust quality across the registry.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0462-rescan-published-trust-elevation](../../../../../increments/0462-rescan-published-trust-elevation/spec.md) | ✅ completed | 2026-03-09 |

## User Stories

- [US-001: Rescan Published Skills Endpoint (P1)](./us-001-rescan-published-skills-endpoint-p1.md)
- [US-002: Batched Pagination and Observability (P1)](./us-002-batched-pagination-and-observability-p1.md)
