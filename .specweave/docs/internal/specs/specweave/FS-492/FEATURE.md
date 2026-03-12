---
id: FS-492
title: "Redesign specweave init project resolution"
type: feature
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "The `specweave init` command has several path-resolution issues that cause confusion and maintenance burden:."
complexity: medium
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 238
    url: 'https://github.com/anton-abyzov/specweave/milestone/238'
externalLinks:
  jira:
    epicKey: 'SWE2E-163'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-163'
    syncedAt: '2026-03-12T00:12:36.657Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 710
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/710'
    syncedAt: '2026-03-12T00:12:42.097Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Redesign specweave init project resolution

## TL;DR

**What**: The `specweave init` command has several path-resolution issues that cause confusion and maintenance burden:.
**Status**: completed | **Priority**: P1
**User Stories**: 3

![Redesign specweave init project resolution illustration](assets/feature-fs-492.jpg)

## Overview

The `specweave init` command has several path-resolution issues that cause confusion and maintenance burden:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0492-init-project-resolution-redesign](../../../../../increments/0492-init-project-resolution-redesign/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: No-args init uses CWD explicitly (P1)](./us-001-no-args-init-uses-cwd-explicitly-p1.md)
- [US-002: Extract umbrella config helper (P2)](./us-002-extract-umbrella-config-helper-p2.md)
- [US-003: Improved guard-clause error messages and relaxed post-scaffold guard (P2) — DESCOPED](./us-003-improved-guard-clause-error-messages-and-relaxed-post-scaffold-guard-p2-descoped.md)
