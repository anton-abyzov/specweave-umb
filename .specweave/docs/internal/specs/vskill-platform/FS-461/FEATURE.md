---
id: FS-461
title: Skill Star Count Freshness & Search Index Sync
type: feature
status: active
priority: P1
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  Skills published on verified-skill.com sometimes show 0 stars in search
  results even when their GitHub repos have thousands of stars.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-73
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-73'
    syncedAt: '2026-03-10T08:18:15.450Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 138
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/138
    syncedAt: '2026-03-10T08:18:15.788Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Skill Star Count Freshness & Search Index Sync

## TL;DR

**What**: Skills published on verified-skill.com sometimes show 0 stars in search results even when their GitHub repos have thousands of stars.
**Status**: active | **Priority**: P1
**User Stories**: 5

![Skill Star Count Freshness & Search Index Sync illustration](assets/feature-fs-461.jpg)

## Overview

Skills published on verified-skill.com sometimes show 0 stars in search results even when their GitHub repos have thousands of stars. Root causes:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0461-skill-star-freshness](../../../../../increments/0461-skill-star-freshness/spec.md) | ⏳ active | 2026-03-09 |

## User Stories

- [US-001: Fetch GitHub Stars at Publish Time](./us-001-fetch-github-stars-at-publish-time.md)
- [US-002: Enrichment Cron Dispatches Search Shard Updates](./us-002-enrichment-cron-dispatches-search-shard-updates.md)
- [US-003: Admin Refresh-Skills Endpoint](./us-003-admin-refresh-skills-endpoint.md)
- [US-004: Admin Dedup-Skills Endpoint](./us-004-admin-dedup-skills-endpoint.md)
- [US-005: Fix SearchShardQueueMessage Type](./us-005-fix-searchshardqueuemessage-type.md)
