---
id: FS-439
title: Skill Eval Infrastructure
type: feature
status: ready_for_review
priority: P1
created: "2026-03-05T00:00:00.000Z"
lastUpdated: "2026-03-07T00:00:00.000Z"
tldr: >-
  Skills across vskill (42 plugin skills) and specweave (48 skills) lack a
  systematic evaluation framework.
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-29
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-29'
    syncedAt: "2026-03-07T03:10:16.234Z"
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 82
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/82
    syncedAt: '2026-03-07T03:10:27.532Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-07'
external_tools:
  github:
    type: milestone
    id: 226
    url: 'https://github.com/anton-abyzov/specweave/milestone/226'
---

# Skill Eval Infrastructure

## TL;DR

**What**: Skills across vskill (42 plugin skills) and specweave (48 skills) lack a systematic evaluation framework.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 1

## Overview

Skills across vskill (42 plugin skills) and specweave (48 skills) lack a systematic evaluation framework. The only existing evals.json is a manually-authored file for the social-media-posting skill. There is no CLI tooling to scaffold, run, or report on evals. The platform has stub eval API routes but no web editor for browsing or editing eval definitions. Without eval infrastructure, there is no way to measure whether skills actually work, detect regressions, or enforce quality standards at scale.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0439-skill-eval-infrastructure](../../../../../increments/0439-skill-eval-infrastructure/spec.md) | ⏳ ready_for_review | 2026-03-05 |

## User Stories

- [US-SW-001: Eval Content for SpecWeave Skills (P1)](./us-sw-001-eval-content-for-specweave-skills-p1.md)

## Related Projects

This feature spans multiple projects:

- [vskill](../../vskill/FS-439/)
- [vskill-platform](../../vskill-platform/FS-439/)
