---
id: FS-471
title: 'Submit page: distinguish new vs rescan submissions'
type: feature
status: planned
priority: P1
created: 2026-03-10T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  The submit page at `/submit` treats all discovered skills identically
  regardless of whether they already exist on the platform.
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-79
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-79'
    syncedAt: '2026-03-10T08:18:34.710Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 144
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/144
    syncedAt: '2026-03-10T08:18:35.161Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Submit page: distinguish new vs rescan submissions

## TL;DR

**What**: The submit page at `/submit` treats all discovered skills identically regardless of whether they already exist on the platform.
**Status**: planned | **Priority**: P1
**User Stories**: 1

![Submit page: distinguish new vs rescan submissions illustration](assets/feature-fs-471.jpg)

## Overview

The submit page at `/submit` treats all discovered skills identically regardless of whether they already exist on the platform. When a user resubmits a repo containing skills that are already verified (stale >24h), every skill shows as "N submitted" with no indication that some are rescans of existing skills. The discovery endpoint (`POST /api/v1/submissions/discover`) already returns enrichment status (`new`/`verified`/`pending`/`rejected`) per skill via `enrichDiscoveryWithStatus`, but the frontend `DiscoveredSkill` interface drops the `status` field and never uses it.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0471-submit-rescan-feedback](../../../../../increments/0471-submit-rescan-feedback/spec.md) | ⏳ planned | 2026-03-10 |

## User Stories

- [US-001: Rescan-aware submission feedback (P1)](./us-001-rescan-aware-submission-feedback-p1.md)
