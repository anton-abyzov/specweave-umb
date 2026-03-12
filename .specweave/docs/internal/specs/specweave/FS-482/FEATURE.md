---
id: FS-482
title: "Radically Simplify specweave init"
type: feature
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
lastUpdated: 2026-03-11
tldr: "The current `specweave init` command is 1,242 lines with 41 helper modules totaling ~13,000 lines."
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 235
    url: 'https://github.com/anton-abyzov/specweave/milestone/235'
externalLinks:
  jira:
    epicKey: 'SWE2E-134'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-134'
    syncedAt: '2026-03-10T23:45:34.796Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 206
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/206'
    syncedAt: '2026-03-10T23:45:44.087Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Radically Simplify specweave init

## TL;DR

**What**: The current `specweave init` command is 1,242 lines with 41 helper modules totaling ~13,000 lines.
**Status**: completed | **Priority**: P1
**User Stories**: 5

## Overview

The current `specweave init` command is 1,242 lines with 41 helper modules totaling ~13,000 lines. It handles brownfield/greenfield classification, repository hosting setup (GitHub/ADO/Bitbucket), umbrella cloning, multi-project folder creation, issue tracker setup, and complex wi

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0482-simplify-init](../../../../../increments/0482-simplify-init/spec.md) | ✅ completed | 2026-03-10T00:00:00.000Z |

## User Stories

- [US-001: Simplified Init Command (P1)](./us-001-simplified-init-command-p1.md)
- [US-002: Guided Next Steps (P1)](./us-002-guided-next-steps-p1.md)
- [US-003: Simplified Config Schema (P1)](./us-003-simplified-config-schema-p1.md)
- [US-004: Clean Summary Banner (P2)](./us-004-clean-summary-banner-p2.md)
- [US-005: Barrel and Type Cleanup (P2)](./us-005-barrel-and-type-cleanup-p2.md)
