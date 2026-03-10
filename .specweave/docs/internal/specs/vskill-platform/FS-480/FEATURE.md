---
id: FS-480
title: "Remove Admin Evals Editor"
type: feature
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
lastUpdated: 2026-03-10
tldr: "Remove the redundant web-based evals.json editor from the admin panel."
complexity: low
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 20
    url: 'https://github.com/anton-abyzov/vskill-platform/milestone/20'
externalLinks:
  jira:
    epicKey: 'SWE2E-127'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-127'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 191
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/191'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Remove Admin Evals Editor

## TL;DR

**What**: Remove the redundant web-based evals.json editor from the admin panel.
**Status**: completed | **Priority**: P1
**User Stories**: 1

![Remove Admin Evals Editor illustration](assets/feature-fs-480.jpg)

## Overview

Remove the redundant web-based evals.json editor from the admin panel. Eval authoring belongs locally via `vskill studio` / `vskill eval` in the CLI. Authors manage `evals.json` in their repos; the platform discovers it via rescan and runs server-side benchmarks. The admin editor is dead weight -- it duplicates CLI functionality and introduces an unnecessary GitHub write-back surface.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0480-remove-admin-evals-editor](../../../../../increments/0480-remove-admin-evals-editor/spec.md) | ✅ completed | 2026-03-10T00:00:00.000Z |

## User Stories

- [US-001: Remove admin evals editor page and API routes (P1)](./us-001-remove-admin-evals-editor-page-and-api-routes-p1.md)
