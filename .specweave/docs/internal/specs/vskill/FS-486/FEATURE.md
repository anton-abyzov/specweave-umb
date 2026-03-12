---
id: FS-486
title: "AI Edit with Eval Change Suggestions"
type: feature
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
lastUpdated: 2026-03-11
tldr: "The Skill Studio's AI Edit feature currently only modifies SKILL.md content."
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 21
    url: 'https://github.com/anton-abyzov/vskill/milestone/21'
externalLinks:
  jira:
    epicKey: 'SWE2E-141'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-141'
    syncedAt: '2026-03-11T07:05:23.545Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 281
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/281'
    syncedAt: '2026-03-11T07:05:32.685Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# AI Edit with Eval Change Suggestions

## TL;DR

**What**: The Skill Studio's AI Edit feature currently only modifies SKILL.md content.
**Status**: completed | **Priority**: P1
**User Stories**: 4

## Overview

The Skill Studio's AI Edit feature currently only modifies SKILL.md content. When a user changes skill instructions, the associated test cases (evals) often become stale -- assertions may no longer match the updated behavior, new capabilities lack coverage, and removed features still have eval cases testing them. Users must manually audit and update evals after every AI Edit, which is tedious and error-prone.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0486-smart-ai-edit](../../../../../increments/0486-smart-ai-edit/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: LLM Returns Eval Change Suggestions](./us-001-llm-returns-eval-change-suggestions.md)
- [US-002: Combined Review Panel](./us-002-combined-review-panel.md)
- [US-003: Selective Apply of Eval Changes](./us-003-selective-apply-of-eval-changes.md)
- [US-004: Workspace State for Eval Changes](./us-004-workspace-state-for-eval-changes.md)
