---
id: FS-505
title: "Fix Stale Search Results Returning 404"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "When users run `npx vskill find <query>`, results include skills that have been hard-deleted from Postgres but still exist in Cloudflare KV search index shards."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-183'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-183'
    syncedAt: '2026-03-12T02:43:20.351Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 983
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/983'
    syncedAt: '2026-03-12T02:43:26.132Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix Stale Search Results Returning 404

## TL;DR

**What**: When users run `npx vskill find <query>`, results include skills that have been hard-deleted from Postgres but still exist in Cloudflare KV search index shards.
**Status**: completed | **Priority**: P1
**User Stories**: 3

![Fix Stale Search Results Returning 404 illustration](assets/feature-fs-505.jpg)

## Overview

When users run `npx vskill find <query>`, results include skills that have been hard-deleted from Postgres but still exist in Cloudflare KV search index shards. Clicking these results on verified-skill.com returns 404. The admin hard-delete endpoint (`/api/v1/admin/skills/.../delete`) removes records from Postgres but never calls `updateSearchShard(..., "remove")`, leaving stale entries in KV indefinitely. KV entries have no TTL, so stale data persists until a manual full index rebuild is triggered.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0505-fix-stale-search-404](../../../../../increments/0505-fix-stale-search-404/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Delete Endpoint KV Cleanup (P0)](./us-001-delete-endpoint-kv-cleanup-p0.md)
- [US-002: Search Result Existence Validation (P1)](./us-002-search-result-existence-validation-p1.md)
- [US-003: KV Shard TTL Defense-in-Depth (P1)](./us-003-kv-shard-ttl-defense-in-depth-p1.md)
