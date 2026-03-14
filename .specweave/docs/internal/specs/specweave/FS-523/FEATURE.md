---
id: FS-523
title: 'Living Docs Sync Cleanup: Bug Fixes and DRY Extraction'
type: feature
status: planned
priority: P1
created: 2026-03-14T00:00:00.000Z
lastUpdated: 2026-03-14T00:00:00.000Z
tldr: >-
  `living-docs-sync.ts` contains three bugs and three DRY violations identified
  during code review.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-198
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-198'
    syncedAt: '2026-03-14T21:40:36.918Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 1277
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1277
    syncedAt: '2026-03-14T21:40:49.199Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-14'
---

# Living Docs Sync Cleanup: Bug Fixes and DRY Extraction

## TL;DR

**What**: `living-docs-sync.ts` contains three bugs and three DRY violations identified during code review.
**Status**: planned | **Priority**: P1
**User Stories**: 6

## Overview

`living-docs-sync.ts` contains three bugs and three DRY violations identified during code review. Bug 1 causes cross-reference links to include filtered-out (invalid/placeholder) projects in FEATURE.md files. Bug 2 leaves ~100 lines of dead code. Bug 3 cites the wrong ADR. The DRY violations add maintenance burden through duplicated SKIP_EXTERNAL_SYNC parsing, duplicated image generation blocks, and inconsistent gray-matter imports.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0523-living-docs-sync-cleanup](../../../../../increments/0523-living-docs-sync-cleanup/spec.md) | ⏳ planned | 2026-03-14 |

## User Stories

- [US-001: Fix Cross-Reference Generation Using Unfiltered Groups](./us-001-fix-cross-reference-generation-using-unfiltered-groups.md)
- [US-002: Remove Dead detectMultiProjectMode Method](./us-002-remove-dead-detectmultiprojectmode-method.md)
- [US-003: Correct ADR Citation in ProjectResolutionService](./us-003-correct-adr-citation-in-projectresolutionservice.md)
- [US-004: Extract Duplicated SKIP_EXTERNAL_SYNC Parsing](./us-004-extract-duplicated-skip-external-sync-parsing.md)
- [US-005: Extract Duplicated Image Generation Block](./us-005-extract-duplicated-image-generation-block.md)
- [US-006: Consolidate Dynamic gray-matter Import to Static](./us-006-consolidate-dynamic-gray-matter-import-to-static.md)
