---
id: FS-489
title: "Fix dashboard docs preview services"
type: feature
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
lastUpdated: 2026-03-11
tldr: "The dashboard Services page has several bugs and missing functionality around documentation preview services:."
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 236
    url: 'https://github.com/anton-abyzov/specweave/milestone/236'
externalLinks:
  jira:
    epicKey: 'SWE2E-144'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-144'
    syncedAt: '2026-03-11T07:50:04.666Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 335
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/335'
    syncedAt: '2026-03-11T07:50:12.178Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix dashboard docs preview services

## TL;DR

**What**: The dashboard Services page has several bugs and missing functionality around documentation preview services:.
**Status**: completed | **Priority**: P1
**User Stories**: 4

![Fix dashboard docs preview services illustration](assets/feature-fs-489.jpg)

## Overview

The dashboard Services page has several bugs and missing functionality around documentation preview services:
1. The single "Docs Preview" service entry should be split into "Internal Docs" and "Public Docs" matching the existing `SCOPE_PORTS` definition (internal:3015, public:3016).
2. Port detection checks `config.documentation.previewPort ?? 3000`, which is wrong -- internal docs use port 3015, public docs use port 3016.
3. `command-runner.ts` only has generic `docs-preview-start`/`docs-preview-stop` commands, lacking scope-specific variants.
4. `useCommand.ts` hardcodes a 60-second client-side timeout, but docs commands (which install npm packages and start Docusaurus) routinely exceed 60 seconds.
5. `ServicesPage.tsx` hardcodes `svc.name === 'Docs Preview'` for rendering start/stop/open controls, making it impossible to add new controllable services without code changes.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0489-dashboard-docs-services](../../../../../increments/0489-dashboard-docs-services/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Scope-specific docs commands (P1)](./us-001-scope-specific-docs-commands-p1.md)
- [US-002: Correct service listing with proper ports (P1)](./us-002-correct-service-listing-with-proper-ports-p1.md)
- [US-003: Configurable command timeout (P1)](./us-003-configurable-command-timeout-p1.md)
- [US-004: Data-driven service controls in ServicesPage (P1)](./us-004-data-driven-service-controls-in-servicespage-p1.md)
