---
id: FS-512
title: "Skill Studio Multi-File Editor"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "The Skill Studio editor currently shows only SKILL.md content."
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-189'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-189'
    syncedAt: '2026-03-12T06:02:05.568Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1088
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1088'
    syncedAt: '2026-03-12T06:02:07.968Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Skill Studio Multi-File Editor

## TL;DR

**What**: The Skill Studio editor currently shows only SKILL.md content.
**Status**: completed | **Priority**: P1
**User Stories**: 1

![Skill Studio Multi-File Editor illustration](assets/feature-fs-512.jpg)

## Overview

The Skill Studio editor currently shows only SKILL.md content. Skills are multi-file directories containing SKILL.md, evals/evals.json, evals/history/*.json, draft.json, and other files. Users have no way to browse or view these supporting files from within the editor, forcing them to use external tools to inspect skill directory contents.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0512-skill-studio-multifile-editor](../../../../../increments/0512-skill-studio-multifile-editor/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Multi-File Browsing and Viewing in Skill Studio Editor](./us-001-multi-file-browsing-and-viewing-in-skill-studio-editor.md)
