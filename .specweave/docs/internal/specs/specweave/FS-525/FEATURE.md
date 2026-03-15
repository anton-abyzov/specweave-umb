---
id: FS-525
title: "Fix Living Docs Sync Architecture"
type: feature
status: completed
priority: P1
created: 2026-03-14T00:00:00.000Z
lastUpdated: 2026-03-15
tldr: "The PostToolUse hook (`close-completed-issues.sh`) spawns `specweave sync-living-docs` via `& disown` -- a fire-and-forget pattern that creates."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-204'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-204'
    syncedAt: '2026-03-15T00:35:05.665Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1338
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1338'
    syncedAt: '2026-03-15T00:35:10.046Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix Living Docs Sync Architecture

## TL;DR

**What**: The PostToolUse hook (`close-completed-issues.sh`) spawns `specweave sync-living-docs` via `& disown` -- a fire-and-forget pattern that creates.
**Status**: completed | **Priority**: P1
**User Stories**: 2

![Fix Living Docs Sync Architecture illustration](assets/feature-fs-525.jpg)

## Overview

The PostToolUse hook (`close-completed-issues.sh`) spawns `specweave sync-living-docs` via `& disown` -- a fire-and-forget pattern that creates

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0525-fix-living-docs-sync-architecture](../../../../../increments/0525-fix-living-docs-sync-architecture/spec.md) | ✅ completed | 2026-03-14T00:00:00.000Z |

## User Stories

- [US-001: Fix specweave complete silent failures](./us-001-fix-specweave-complete-silent-failures.md)
- [US-003: Add living docs sync skip mechanism](./us-003-add-living-docs-sync-skip-mechanism.md)

## Related Projects

This feature spans multiple projects:

- [specweave-umb](../../specweave-umb/FS-525/)
