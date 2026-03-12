---
id: FS-448
title: Trust badges in vskill find output
type: feature
status: planned
priority: P1
created: "2026-03-07T00:00:00.000Z"
lastUpdated: "2026-03-11T00:00:00.000Z"
tldr: >-
  Display colored trust tier badges (T4 certified, T3 verified, T2/T1 maybe)
  alongside star counts in `vskill find` CLI output.
complexity: medium
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 25
    url: 'https://github.com/anton-abyzov/vskill/milestone/25'
externalLinks:
  jira:
    epicKey: SWE2E-151
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-151'
    syncedAt: '2026-03-11T21:15:36.935Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 499
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/499
    syncedAt: '2026-03-11T21:15:41.942Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-11'
---

# Trust badges in vskill find output

## TL;DR

**What**: Display colored trust tier badges (T4 certified, T3 verified, T2/T1 maybe) alongside star counts in `vskill find` CLI output.
**Status**: planned | **Priority**: P1
**User Stories**: 2

## Overview

Display colored trust tier badges (T4 certified, T3 verified, T2/T1 maybe) alongside star counts in `vskill find` CLI output. The platform search API already returns `trustTier` in skill records; the CLI must parse it and render an appropriate colored badge in both TTY and non-TTY output modes.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0448-trust-badges-find](../../../../../increments/0448-trust-badges-find/spec.md) | ⏳ planned | 2026-03-07 |

## User Stories

- [US-001: See trust badges in find results (P1)](./us-001-see-trust-badges-in-find-results-p1.md)
- [US-002: Trust tier in non-TTY and JSON output (P1)](./us-002-trust-tier-in-non-tty-and-json-output-p1.md)

## Related Projects

This feature spans multiple projects:

- [vskill-platform](../../vskill-platform/FS-448/)
