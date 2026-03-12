---
id: FS-502
title: "Centralized config state for Skill Studio eval-ui"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "The Skill Studio eval-ui has 12 independent `api.getConfig()` calls across 10 components."
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 27
    url: 'https://github.com/anton-abyzov/vskill/milestone/27'
externalLinks:
  jira:
    epicKey: 'SWE2E-180'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-180'
    syncedAt: '2026-03-12T01:53:47.933Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 932
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/932'
    syncedAt: '2026-03-12T01:53:55.656Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Centralized config state for Skill Studio eval-ui

## TL;DR

**What**: The Skill Studio eval-ui has 12 independent `api.getConfig()` calls across 10 components.
**Status**: completed | **Priority**: P1
**User Stories**: 4

![Centralized config state for Skill Studio eval-ui illustration](assets/feature-fs-502.jpg)

## Overview

The Skill Studio eval-ui has 12 independent `api.getConfig()` calls across 10 components. Each component fetches config on mount, creating isolated snapshots of server state. When the user changes the model via ModelSelector (the only mutation point), other components retain stale config until they are remounted. This causes the "Generate with {model}" button in CreateSkillInline to show a different model than what the user just selected in the sidebar.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0502-config-context-sync](../../../../../increments/0502-config-context-sync/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Instant Model Propagation on Selection](./us-001-instant-model-propagation-on-selection.md)
- [US-002: Centralized Config Provider](./us-002-centralized-config-provider.md)
- [US-003: Component Migration to Shared Context](./us-003-component-migration-to-shared-context.md)
- [US-004: ConfigContext File Structure](./us-004-configcontext-file-structure.md)
