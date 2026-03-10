---
id: FS-472
title: Auto-classify activation test expectations
type: feature
status: planned
priority: P1
created: 2026-03-10T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  In the Skill Studio Activation Panel, test prompts without a `!` prefix
  default to `expected: 'should_activate'`.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-81
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-81'
    syncedAt: '2026-03-10T08:23:01.742Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 146
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/146
    syncedAt: '2026-03-10T08:23:02.339Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Auto-classify activation test expectations

## TL;DR

**What**: In the Skill Studio Activation Panel, test prompts without a `!` prefix default to `expected: "should_activate"`.
**Status**: planned | **Priority**: P1
**User Stories**: 5

![Auto-classify activation test expectations illustration](assets/feature-fs-472.jpg)

## Overview

In the Skill Studio Activation Panel, test prompts without a `!` prefix default to `expected: "should_activate"`. When users type irrelevant prompts (e.g., "I built my test" for a Slack messaging skill), the system incorrectly expects activation, producing false FN results and corrupting precision/recall metrics. This makes the activation panel unreliable for iterating on skill descriptions.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0472-activation-auto-classify](../../../../../increments/0472-activation-auto-classify/spec.md) | ⏳ planned | 2026-03-10 |

## User Stories

- [US-001: Two-Phase Activation Evaluation](./us-001-two-phase-activation-evaluation.md)
- [US-002: Classification Prompt and Cross-Model Compatibility](./us-002-classification-prompt-and-cross-model-compatibility.md)
- [US-003: Server-Side Metadata Extraction](./us-003-server-side-metadata-extraction.md)
- [US-004: Client Prefix Handling and UI Updates](./us-004-client-prefix-handling-and-ui-updates.md)
- [US-005: Unit Tests for Classification Logic](./us-005-unit-tests-for-classification-logic.md)
