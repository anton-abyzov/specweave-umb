---
id: FS-501
title: Single Repo Clone via --repo Flag
type: feature
status: planned
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12T00:00:00.000Z
tldr: 'The `/sw-github:clone` command only supports org-level bulk cloning.'
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 239
    url: 'https://github.com/anton-abyzov/specweave/milestone/239'
externalLinks:
  jira:
    epicKey: SWE2E-179
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-179'
    syncedAt: '2026-03-12T01:52:27.441Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 926
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/926
    syncedAt: '2026-03-12T01:52:37.350Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-12'
---

# Single Repo Clone via --repo Flag

## TL;DR

**What**: The `/sw-github:clone` command only supports org-level bulk cloning.
**Status**: planned | **Priority**: P1
**User Stories**: 5

## Overview

The `/sw-github:clone` command only supports org-level bulk cloning. Users who want to add a single repository to their umbrella workspace must either clone manually and configure childRepos by hand, or run a full org fetch just to clone one repo. This is wasteful and error-prone.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0501-single-repo-clone](../../../../../increments/0501-single-repo-clone/spec.md) | ⏳ planned | 2026-03-12 |

## User Stories

- [US-001: Parse Repository Identifier from Multiple Formats (P1)](./us-001-parse-repository-identifier-from-multiple-formats-p1.md)
- [US-002: Validate Repository Exists on GitHub (P1)](./us-002-validate-repository-exists-on-github-p1.md)
- [US-003: Clone Single Repo into Umbrella Structure (P1)](./us-003-clone-single-repo-into-umbrella-structure-p1.md)
- [US-004: Flag Precedence and Dry-Run Support (P2)](./us-004-flag-precedence-and-dry-run-support-p2.md)
- [US-005: Update Clone Skill Definition (P1)](./us-005-update-clone-skill-definition-p1.md)
