---
id: FS-494
title: "Search Performance Optimization"
type: feature
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
lastUpdated: 2026-03-11
tldr: "Search on verified-skill.com is perceived as slow."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-155'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-155'
    syncedAt: '2026-03-11T22:38:40.549Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 549
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/549'
    syncedAt: '2026-03-11T22:38:51.639Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Search Performance Optimization

## TL;DR

**What**: Search on verified-skill.com is perceived as slow.
**Status**: completed | **Priority**: P1
**User Stories**: 6

## Overview

Search on verified-skill.com is perceived as slow. The current hybrid search (KV edge + Postgres) runs both sources sequentially, always queries Postgres even when edge has sufficient results, adds 3 DB queries for blocklist enrichment unconditionally, and uses conservative cache TTLs. The frontend offers no instant results on palette open, requiring users to wait for the full API roundtrip before seeing anything.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0494-search-performance-optimization](../../../../../increments/0494-search-performance-optimization/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Edge-First Search with Conditional Postgres Fallback](./us-001-edge-first-search-with-conditional-postgres-fallback.md)
- [US-002: Conditional Blocklist Enrichment](./us-002-conditional-blocklist-enrichment.md)
- [US-003: Improved CDN and Client Cache Headers](./us-003-improved-cdn-and-client-cache-headers.md)
- [US-004: Server-Timing Latency Headers](./us-004-server-timing-latency-headers.md)
- [US-005: Preload Trending Skills on Palette Open](./us-005-preload-trending-skills-on-palette-open.md)
- [US-006: Client-Side Filter of Preloaded Trending Data](./us-006-client-side-filter-of-preloaded-trending-data.md)
