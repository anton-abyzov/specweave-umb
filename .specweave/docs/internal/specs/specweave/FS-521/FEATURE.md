---
id: FS-521
title: "External Integration Health Check & Smart Linking"
type: feature
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
lastUpdated: 2026-03-15
tldr: "Enhance SpecWeave's external integration pipeline by wiring health checks into the sync-setup flow, integrating external ticket keys into branch naming, adding a standalone `sync-health` CLI command, and auto-triggering PR-to-ticket linking during PR-based closure."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-246'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-246'
    syncedAt: '2026-03-15T17:37:58.230Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1371
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1371'
    syncedAt: '2026-03-15T17:38:04.143Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# External Integration Health Check & Smart Linking

## TL;DR

**What**: Enhance SpecWeave's external integration pipeline by wiring health checks into the sync-setup flow, integrating external ticket keys into branch naming, adding a standalone `sync-health` CLI command, and auto-triggering PR-to-ticket linking during PR-based closure.
**Status**: completed | **Priority**: P1
**User Stories**: 4

![External Integration Health Check & Smart Linking illustration](assets/feature-fs-521.jpg)

## Overview

Enhance SpecWeave's external integration pipeline by wiring health checks into the sync-setup flow, integrating external ticket keys into branch naming, adding a standalone `sync-health` CLI command, and auto-triggering PR-to-ticket linking during PR-based closure. Most building blocks already exist (`integration-health-check.ts`, `resolveExternalBranchPrefix()`, `pr-linker.ts`, `link-pr` command) — this increment connects them into a cohesive, production-ready workflow.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0521-external-integration-smart-linking](../../../../../increments/0521-external-integration-smart-linking/spec.md) | ✅ completed | 2026-03-13T00:00:00.000Z |

## User Stories

- [US-001: Integration Health Check at Setup Time (P1)](./us-001-integration-health-check-at-setup-time-p1.md)
- [US-002: Branch Naming with External Ticket Keys (P1)](./us-002-branch-naming-with-external-ticket-keys-p1.md)
- [US-003: Automatic PR-to-Ticket Linking on PR Creation (P1)](./us-003-automatic-pr-to-ticket-linking-on-pr-creation-p1.md)
- [US-004: Standalone Sync Health Command (P2)](./us-004-standalone-sync-health-command-p2.md)
