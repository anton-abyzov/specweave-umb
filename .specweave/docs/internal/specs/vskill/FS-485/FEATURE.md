---
id: FS-485
title: Skill Studio AI-Assisted Skill Creation
type: feature
status: planned
priority: P1
created: 2026-03-11T00:00:00.000Z
lastUpdated: 2026-03-11T00:00:00.000Z
tldr: Add an AI-assisted mode to the Create Skill page in Skill Studio (eval-ui).
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 24
    url: 'https://github.com/anton-abyzov/vskill/milestone/24'
externalLinks:
  jira:
    epicKey: SWE2E-153
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-153'
    syncedAt: '2026-03-11T21:16:26.030Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 504
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/504
    syncedAt: '2026-03-11T21:16:37.424Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-11'
---

# Skill Studio AI-Assisted Skill Creation

## TL;DR

**What**: Add an AI-assisted mode to the Create Skill page in Skill Studio (eval-ui).
**Status**: planned | **Priority**: P1
**User Stories**: 7

## Overview

Add an AI-assisted mode to the Create Skill page in Skill Studio (eval-ui). Users describe what a skill should do in natural language, select a provider/model, and the system generates a complete SKILL.md (name, description, system prompt body, frontmatter metadata) plus starter eval test cases -- all via a real-time SSE streaming UX. The generated content populates the manual form for review and editing before final creation.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md) | ⏳ planned | 2026-03-11 |

## User Stories

- [US-001: AI-Assisted Skill Generation (P1)](./us-001-ai-assisted-skill-generation-p1.md)
- [US-002: Provider and Model Selection for Generation (P1)](./us-002-provider-and-model-selection-for-generation-p1.md)
- [US-003: Generated Test Cases (P1)](./us-003-generated-test-cases-p1.md)
- [US-004: Error Handling and Cancellation (P1)](./us-004-error-handling-and-cancellation-p1.md)
- [US-005: Backend Skill Generation Endpoint (P1)](./us-005-backend-skill-generation-endpoint-p1.md)
- [US-006: Skill Creation with AI-Generated Evals (P2)](./us-006-skill-creation-with-ai-generated-evals-p2.md)
- [US-007: SKILL.md Preview in AI Mode (P2)](./us-007-skill-md-preview-in-ai-mode-p2.md)
