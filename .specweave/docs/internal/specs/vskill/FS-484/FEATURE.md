---
id: FS-484
title: "Skill Studio AI Edit Feature"
type: feature
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
lastUpdated: 2026-03-11
tldr: "Skill authors currently rely on the 'Improve Skill' feature which applies opinionated best-practice improvements automatically."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-139'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-139'
    syncedAt: '2026-03-11T06:04:24.041Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 212
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/212'
    syncedAt: '2026-03-11T06:04:30.461Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Skill Studio AI Edit Feature

## TL;DR

**What**: Skill authors currently rely on the "Improve Skill" feature which applies opinionated best-practice improvements automatically.
**Status**: completed | **Priority**: P1
**User Stories**: 2

![Skill Studio AI Edit Feature illustration](assets/feature-fs-484.jpg)

## Overview

Skill authors currently rely on the "Improve Skill" feature which applies opinionated best-practice improvements automatically. There is no way to give the AI a specific, freeform instruction like "add error handling section" or "make the description more concise." Authors must either manually edit the SKILL.md or accept the AI's generic improvements wholesale. This slows down targeted iteration.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0484-skill-studio-ai-edit](../../../../../increments/0484-skill-studio-ai-edit/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Freeform AI Edit via Inline Prompt Bar](./us-001-freeform-ai-edit-via-inline-prompt-bar.md)
- [US-002: Diff Review and Apply/Discard for AI Edits](./us-002-diff-review-and-apply-discard-for-ai-edits.md)
