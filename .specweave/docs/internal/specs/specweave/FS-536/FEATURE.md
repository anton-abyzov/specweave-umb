---
id: FS-536
title: "Fix plugin Discover tab scope mismatch"
type: feature
status: completed
priority: P0
created: 2026-03-15T00:00:00.000Z
lastUpdated: 2026-03-15
tldr: "Claude Code's `/plugin` Discover tab only shows `sw` as installed (checkmark) while the Installed tab correctly shows all 8 SpecWeave plugins as enabled."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-265'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-265'
    syncedAt: '2026-03-15T21:53:41.525Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1372
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1372'
    syncedAt: '2026-03-15T21:53:51.348Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix plugin Discover tab scope mismatch

## TL;DR

**What**: Claude Code's `/plugin` Discover tab only shows `sw` as installed (checkmark) while the Installed tab correctly shows all 8 SpecWeave plugins as enabled.
**Status**: completed | **Priority**: P0
**User Stories**: 3

![Fix plugin Discover tab scope mismatch illustration](assets/feature-fs-536.jpg)

## Overview

Claude Code's `/plugin` Discover tab only shows `sw` as installed (checkmark) while the Installed tab correctly shows all 8 SpecWeave plugins as enabled. The root cause is a scope mismatch: `sw` installs at `user` scope (via `scopeOverrides`) while all other SpecWeave plugins default to `project` scope (via `specweaveScope: 'project'`). Claude Code's Discover tab only recogni

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0536-plugin-discover-scope-fix](../../../../../increments/0536-plugin-discover-scope-fix/spec.md) | ✅ completed | 2026-03-15T00:00:00.000Z |

## User Stories

- [US-001: Consistent Plugin Scope (P0)](./us-001-consistent-plugin-scope-p0.md)
- [US-002: Settings Enablement on Init (P0)](./us-002-settings-enablement-on-init-p0.md)
- [US-003: Settings Enablement Regardless of Install Method (P1)](./us-003-settings-enablement-regardless-of-install-method-p1.md)
