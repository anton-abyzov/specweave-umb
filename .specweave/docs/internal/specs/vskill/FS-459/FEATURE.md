---
id: FS-459
title: Skill Eval UI Enhancements
type: feature
status: planned
priority: P1
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  The vskill Skill Eval UI provides benchmarking and A/B comparison
  capabilities, but skill developers lack visibility into the skill definition
  itself, have no AI-assisted iteration workflow, cannot compare different
  models on the same test case, and have no awareness of MCP server dependencies
  required by their skills.
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 14
    url: 'https://github.com/anton-abyzov/vskill/milestone/14'
externalLinks:
  jira:
    epicKey: SWE2E-108
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-108'
    syncedAt: '2026-03-10T09:45:32.934Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 173
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/173
    syncedAt: '2026-03-10T09:45:33.416Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Skill Eval UI Enhancements

## TL;DR

**What**: The vskill Skill Eval UI provides benchmarking and A/B comparison capabilities, but skill developers lack visibility into the skill definition itself, have no AI-assisted iteration workflow, cannot compare different models on the same test case, and have no awareness of MCP server dependencies required by their skills.
**Status**: planned | **Priority**: P1
**User Stories**: 4

![Skill Eval UI Enhancements illustration](assets/feature-fs-459.jpg)

## Overview

The vskill Skill Eval UI provides benchmarking and A/B comparison capabilities, but skill developers lack visibility into the skill definition itself, have no AI-assisted iteration workflow, cannot compare different models on the same test case, and have no awareness of MCP server dependencies required by their skills. These gaps slow down the skill development and iteration cycle.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0459-skill-eval-enhancements](../../../../../increments/0459-skill-eval-enhancements/spec.md) | ⏳ planned | 2026-03-09 |

## User Stories

- [US-001: Skill Definition Viewer](./us-001-skill-definition-viewer.md)
- [US-002: AI-Powered Skill Improvement](./us-002-ai-powered-skill-improvement.md)
- [US-003: Per-Test-Case Model A/B Comparison](./us-003-per-test-case-model-a-b-comparison.md)
- [US-004: Skill Dependency Visibility (MCP + Skill-to-Skill)](./us-004-skill-dependency-visibility-mcp-skill-to-skill.md)
