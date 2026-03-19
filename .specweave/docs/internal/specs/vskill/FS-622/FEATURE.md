---
id: FS-622
title: "Dashboard Cost Display & Real-Time Updates Redesign"
type: feature
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
lastUpdated: 2026-03-19
tldr: "The vskill Studio dashboard cost display is nearly useless — only OpenRouter returns actual cost data."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-713'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-713'
    syncedAt: '2026-03-19T16:06:14.032Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1552
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1552'
    syncedAt: '2026-03-19T16:06:29.418Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Dashboard Cost Display & Real-Time Updates Redesign

## TL;DR

**What**: The vskill Studio dashboard cost display is nearly useless — only OpenRouter returns actual cost data.
**Status**: completed | **Priority**: P1
**User Stories**: 8

![Dashboard Cost Display & Real-Time Updates Redesign illustration](assets/feature-fs-622.jpg)

## Overview

The vskill Studio dashboard cost display is nearly useless — only OpenRouter returns actual cost data. Claude (CLI + API), Codex, Gemini, and Ollama all show "N/A". The StatsPanel shows

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0622-dashboard-cost-realtime-redesign](../../../../../increments/0622-dashboard-cost-realtime-redesign/spec.md) | ✅ completed | 2026-03-19T00:00:00.000Z |

## User Stories

- [US-001: Pricing Engine (P1)](./us-001-pricing-engine-p1.md)
- [US-002: Cost in LLM Responses (P1)](./us-002-cost-in-llm-responses-p1.md)
- [US-003: Cost in StatsPanel (P1)](./us-003-cost-in-statspanel-p1.md)
- [US-004: Cost in RunPanel & BenchmarkPage (P2)](./us-004-cost-in-runpanel-benchmarkpage-p2.md)
- [US-005: Cost in HistoryPanel (P2)](./us-005-cost-in-historypanel-p2.md)
- [US-006: Cost Formatting (P1)](./us-006-cost-formatting-p1.md)
- [US-007: Real-Time Panel Updates (P2)](./us-007-real-time-panel-updates-p2.md)
- [US-008: Client-Side Caching (P3)](./us-008-client-side-caching-p3.md)
