---
id: FS-474
title: "AI commands not recording to history"
type: feature
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "Skill Studio's History tab does not consistently show entries for all AI-powered commands."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-162'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-162'
    syncedAt: '2026-03-12T00:09:09.965Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 692
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/692'
    syncedAt: '2026-03-12T00:09:15.886Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# AI commands not recording to history

## TL;DR

**What**: Skill Studio's History tab does not consistently show entries for all AI-powered commands.
**Status**: completed | **Priority**: P1
**User Stories**: 3

![AI commands not recording to history illustration](assets/feature-fs-474.jpg)

## Overview

Skill Studio's History tab does not consistently show entries for all AI-powered commands. While the backend `improve-routes.ts` does call `writeHistoryEntry` for both "improve" (auto) and "instruct" (smart edit) modes, and `model-compare-routes.ts` records model-compare entries, two AI commands never record to history:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0474-ai-command-history](../../../../../increments/0474-ai-command-history/spec.md) | ✅ completed | 2026-03-10T00:00:00.000Z |

## User Stories

- [US-001: AI Skill Generation Appears in History (P1)](./us-001-ai-skill-generation-appears-in-history-p1.md)
- [US-002: AI Eval Generation Appears in History (P1)](./us-002-ai-eval-generation-appears-in-history-p1.md)
- [US-003: All AI Types Display Correctly in History UI (P2)](./us-003-all-ai-types-display-correctly-in-history-ui-p2.md)
