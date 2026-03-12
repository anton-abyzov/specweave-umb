---
id: FS-506
title: 'Skill Studio: Add Delete Skill Functionality'
type: feature
status: planned
priority: P3
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12T00:00:00.000Z
tldr: The Skill Studio eval-ui currently has no way to delete skills.
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-184
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-184'
    syncedAt: '2026-03-12T02:59:59.512Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 1002
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1002
    syncedAt: '2026-03-12T03:00:01.500Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-12'
---

# Skill Studio: Add Delete Skill Functionality

## TL;DR

**What**: The Skill Studio eval-ui currently has no way to delete skills.
**Status**: planned | **Priority**: P3
**User Stories**: 1

## Overview

The Skill Studio eval-ui currently has no way to delete skills. Users can create and edit skills but cannot remove them, leaving orphaned skill directories on disk. This increment adds a DELETE API endpoint on the eval server, a client-side API method, and a delete button with confirmation dialog in the DetailHeader component. Only skills with `origin: "source"` are deletable; installed (read-only) skills are protected.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0506-skill-studio-delete](../../../../../increments/0506-skill-studio-delete/spec.md) | ⏳ planned | 2026-03-12 |

## User Stories

- [US-001: Delete a Source Skill (P3)](./us-001-delete-a-source-skill-p3.md)
