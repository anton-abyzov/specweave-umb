---
id: FS-387
title: >-
  Fix blocklist global poisoning, duplicate blocked submissions, and crawler
  dedup bypass
type: feature
status: completed
priority: P1
created: "2026-02-27T00:00:00.000Z"
lastUpdated: "2026-03-10T00:00:00.000Z"
tldr: >-
  Three related bugs in the vskill-platform submission pipeline compromise
  security and data integrity:.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-58
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-58'
    syncedAt: '2026-03-10T07:54:31.472Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 123
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/123
    syncedAt: '2026-03-10T07:54:32.336Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Fix blocklist global poisoning, duplicate blocked submissions, and crawler dedup bypass

## TL;DR

**What**: Three related bugs in the vskill-platform submission pipeline compromise security and data integrity:.
**Status**: completed | **Priority**: P1
**User Stories**: 4

## Overview

Three related bugs in the vskill-platform submission pipeline compromise security and data integrity:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0387-blocklist-dedup-poisoning-fixes](../../../../../increments/0387-blocklist-dedup-poisoning-fixes/spec.md) | ✅ completed | 2026-02-27T00:00:00.000Z |

## User Stories

- [US-001: Scope blocklist matching to sourceUrl](./us-001-scope-blocklist-matching-to-sourceurl.md)
- [US-002: Prevent duplicate submissions for blocked skills](./us-002-prevent-duplicate-submissions-for-blocked-skills.md)
- [US-003: Fix crawler discovery dedup race condition](./us-003-fix-crawler-discovery-dedup-race-condition.md)
- [US-004: Auto-block on critical scan violations](./us-004-auto-block-on-critical-scan-violations.md)
