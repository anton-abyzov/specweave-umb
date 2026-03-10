---
id: FS-455
title: Skill Eval UI
type: feature
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  Skill developers currently manage evals through JSON files and CLI commands
  only.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-65
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-65'
    syncedAt: '2026-03-10T08:17:51.861Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 130
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/130
    syncedAt: '2026-03-10T08:17:52.951Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Skill Eval UI

## TL;DR

**What**: Skill developers currently manage evals through JSON files and CLI commands only.
**Status**: completed | **Priority**: P1
**User Stories**: 8

![Skill Eval UI illustration](assets/feature-fs-455.jpg)

## Overview

Skill developers currently manage evals through JSON files and CLI commands only. There is no visual way to browse, edit, run, or compare eval results across benchmark runs. Diagnosing regressions, tuning skill descriptions for activation, and understanding the WITH-skill vs WITHOUT-skill delta all require manual JSON inspection. This slows the skill quality feedback loop.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md) | ✅ completed | 2026-03-08T00:00:00.000Z |

## User Stories

- [US-001: Eval Server Command (P1)](./us-001-eval-server-command-p1.md)
- [US-002: Skill Browser and Eval Case CRUD (P1)](./us-002-skill-browser-and-eval-case-crud-p1.md)
- [US-003: Assertion-Level Benchmark Runner (P1)](./us-003-assertion-level-benchmark-runner-p1.md)
- [US-004: WITH vs WITHOUT Skill Comparison (P1)](./us-004-with-vs-without-skill-comparison-p1.md)
- [US-005: Benchmark History and Regression Detection (P1)](./us-005-benchmark-history-and-regression-detection-p1.md)
- [US-006: Auto-Activation Description Testing (P2)](./us-006-auto-activation-description-testing-p2.md)
- [US-007: REST API Layer (P1)](./us-007-rest-api-layer-p1.md)
- [US-008: Playwright E2E Tests (P1)](./us-008-playwright-e2e-tests-p1.md)
