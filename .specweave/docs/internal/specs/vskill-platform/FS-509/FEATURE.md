---
id: FS-509
title: Track Tier 2 LLM Model in Scan Results
type: feature
status: planned
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12T00:00:00.000Z
tldr: >-
  The vskill-platform Tier 2 security scanner uses a 3-tier LLM fallback chain:
  Cloudflare Llama 4 Scout, Cloudflare Llama 3.3 70B, and OpenAI gpt-4o-mini.
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-187
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-187'
    syncedAt: '2026-03-12T04:19:56.049Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 1063
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1063
    syncedAt: '2026-03-12T04:20:01.982Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-12'
---

# Track Tier 2 LLM Model in Scan Results

## TL;DR

**What**: The vskill-platform Tier 2 security scanner uses a 3-tier LLM fallback chain: Cloudflare Llama 4 Scout, Cloudflare Llama 3.3 70B, and OpenAI gpt-4o-mini.
**Status**: planned | **Priority**: P1
**User Stories**: 3

## Overview

The vskill-platform Tier 2 security scanner uses a 3-tier LLM fallback chain: Cloudflare Llama 4 Scout, Cloudflare Llama 3.3 70B, and OpenAI gpt-4o-mini. The VM scanner (`tier2-scan.js`) already returns a `model` field identifying which LLM handled each scan, but this field is dropped at the `Tier2Payload` interface in `finali

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0509-track-tier2-llm-model](../../../../../increments/0509-track-tier2-llm-model/spec.md) | ⏳ planned | 2026-03-12 |

## User Stories

- [US-001: Persist LLM Model in Scan Results](./us-001-persist-llm-model-in-scan-results.md)
- [US-002: Heuristic Backfill of Historical Scan Data](./us-002-heuristic-backfill-of-historical-scan-data.md)
- [US-003: Admin Stats Endpoint for LLM Model Usage](./us-003-admin-stats-endpoint-for-llm-model-usage.md)
