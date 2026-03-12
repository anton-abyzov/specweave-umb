---
id: FS-515
title: "vskill marketplace sync command"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "When new plugin directories are added to `plugins/` in the vskill repo, `.claude-plugin/marketplace.json` drifts out of sync."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-191'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-191'
    syncedAt: '2026-03-12T17:10:04.129Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1155
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1155'
    syncedAt: '2026-03-12T17:10:14.046Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# vskill marketplace sync command

## TL;DR

**What**: When new plugin directories are added to `plugins/` in the vskill repo, `.claude-plugin/marketplace.json` drifts out of sync.
**Status**: completed | **Priority**: P1
**User Stories**: 4

![vskill marketplace sync command illustration](assets/feature-fs-515.jpg)

## Overview

When new plugin directories are added to `plugins/` in the vskill repo, `.claude-plugin/marketplace.json` drifts out of sync. The `/plugin Discover` tab in Claude Code only renders plugins listed in `marketplace.json`, making new plugins invisible until the registry is manually edited. Observed: `google-workspace`, `marketing`, `productivity` were in `plugins/` but missing from `marketplace.json` -- appearing as "new -- not in marketplace.json" during `npx vskill i`.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0515-vskill-marketplace-sync](../../../../../increments/0515-vskill-marketplace-sync/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Auto-add new plugins to marketplace.json (P1)](./us-001-auto-add-new-plugins-to-marketplace-json-p1.md)
- [US-002: Update drifted plugin metadata (P1)](./us-002-update-drifted-plugin-metadata-p1.md)
- [US-003: Dry-run preview mode (P1)](./us-003-dry-run-preview-mode-p1.md)
- [US-004: Informative summary output and alias (P1)](./us-004-informative-summary-output-and-alias-p1.md)
