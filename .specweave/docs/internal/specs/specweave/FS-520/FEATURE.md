---
id: FS-520
title: PR-Based Increment Closure
type: feature
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
lastUpdated: 2026-03-13
tldr: SpecWeave currently pushes all commits directly to the working branch
  (typically `main`).
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-196
    epicUrl: https://antonabyzov.atlassian.net/browse/SWE2E-196
    syncedAt: 2026-03-13T04:47:19.870Z
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 1246
    featureUrl: https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1246
    syncedAt: 2026-03-13T04:47:23.819Z
    organization: EasyChamp
    project: SpecWeaveSync
external_tools:
  github:
    type: milestone
    id: 241
    url: https://github.com/anton-abyzov/specweave/milestone/241
---

# PR-Based Increment Closure

## TL;DR

**What**: SpecWeave currently pushes all commits directly to the working branch (typically `main`).
**Status**: completed | **Priority**: P1
**User Stories**: 4

![PR-Based Increment Closure illustration](assets/feature-fs-520.jpg)

## Overview

SpecWeave currently pushes all commits directly to the working branch (typically `main`). Teams that follow PR-based workflows have no way to integrate SpecWeave's automated closure flow with their code review process. This forces users to either abandon SpecWeave's `sw:done` flow or skip code review entirely, creating a gap between spec-driven development and standard engineering practices.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0520-pr-based-increment-closure](../../../../../increments/0520-pr-based-increment-closure/spec.md) | ✅ completed | 2026-03-13T00:00:00.000Z |

## User Stories

- [US-001: PR-Based Push Strategy Configuration (P1)](./us-001-pr-based-push-strategy-configuration-p1.md)
- [US-002: Feature Branch Creation in sw:do and sw:auto (P1)](./us-002-feature-branch-creation-in-sw-do-and-sw-auto-p1.md)
- [US-003: PR Creation and Metadata Storage via sw:pr (P1)](./us-003-pr-creation-and-metadata-storage-via-sw-pr-p1.md)
- [US-004: Enterprise Environment Promotion Configuration (P2)](./us-004-enterprise-environment-promotion-configuration-p2.md)
