---
id: FS-507
title: "vskill update: unified skill update across all source types"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "`vskill update` currently hardcodes all updates through the verified-skill.com registry API (`getSkill()`)."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-185'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-185'
    syncedAt: '2026-03-12T03:27:44.522Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1016
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1016'
    syncedAt: '2026-03-12T03:27:52.427Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# vskill update: unified skill update across all source types

## TL;DR

**What**: `vskill update` currently hardcodes all updates through the verified-skill.com registry API (`getSkill()`).
**Status**: completed | **Priority**: P1
**User Stories**: 5

![vskill update: unified skill update across all source types illustration](assets/feature-fs-507.jpg)

## Overview

`vskill update` currently hardcodes all updates through the verified-skill.com registry API (`getSkill()`). Skills installed from GitHub repos, marketplace plugins, or local paths fail silently because the registry has no record of them. This feature makes `update` parse the lockfile `source` field to determine the correct fetch strategy per source type, so every installed skill can be updated from its actual origin.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0507-vskill-update-all-sources](../../../../../increments/0507-vskill-update-all-sources/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Source-Aware Update Routing (P1)](./us-001-source-aware-update-routing-p1.md)
- [US-002: SHA-Based Change Detection (P1)](./us-002-sha-based-change-detection-p1.md)
- [US-003: Security Scanning on All Sources (P1)](./us-003-security-scanning-on-all-sources-p1.md)
- [US-004: Graceful Failure Handling (P2)](./us-004-graceful-failure-handling-p2.md)
- [US-005: Plugin Directory Full Update (P2)](./us-005-plugin-directory-full-update-p2.md)
