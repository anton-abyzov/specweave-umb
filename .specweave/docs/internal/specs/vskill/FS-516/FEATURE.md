---
id: FS-516
title: "Remove native Claude Code plugin install from vskill"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "The `vskill install` command has two install paths: a native Claude Code plugin system (`claude plugin marketplace add` + `claude plugin install`) and a file-system extraction path."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-192'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-192'
    syncedAt: '2026-03-12T21:03:08.027Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1180
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1180'
    syncedAt: '2026-03-12T21:03:15.123Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Remove native Claude Code plugin install from vskill

## TL;DR

**What**: The `vskill install` command has two install paths: a native Claude Code plugin system (`claude plugin marketplace add` + `claude plugin install`) and a file-system extraction path.
**Status**: completed | **Priority**: P1
**User Stories**: 3

![Remove native Claude Code plugin install from vskill illustration](assets/feature-fs-516.jpg)

## Overview

The `vskill install` command has two install paths: a native Claude Code plugin system (`claude plugin marketplace add` + `claude plugin install`) and a file-system extraction path. The native path is fragile, breaks due to stale caches, and adds complexity. All skills should be managed via file-system copy only.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0516-remove-native-plugin-install](../../../../../increments/0516-remove-native-plugin-install/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: File-system-only install (P1)](./us-001-file-system-only-install-p1.md)
- [US-002: Clean uninstall path (P1)](./us-002-clean-uninstall-path-p1.md)
- [US-003: Test coverage (P1)](./us-003-test-coverage-p1.md)
