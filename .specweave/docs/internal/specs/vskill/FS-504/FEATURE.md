---
id: FS-504
title: Install Command Skill Discovery & Disambiguation
type: feature
status: planned
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12T00:00:00.000Z
tldr: >-
  When a user types `vskill install skill-creator` (flat name, no slashes), the
  CLI attempts a direct `getSkill()` API lookup.
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-182
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-182'
    syncedAt: '2026-03-12T02:36:36.097Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 977
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/977
    syncedAt: '2026-03-12T02:36:45.598Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-12'
---

# Install Command Skill Discovery & Disambiguation

## TL;DR

**What**: When a user types `vskill install skill-creator` (flat name, no slashes), the CLI attempts a direct `getSkill()` API lookup.
**Status**: planned | **Priority**: P1
**User Stories**: 5

## Overview

When a user types `vskill install skill-creator` (flat name, no slashes), the CLI attempts a direct `getSkill()` API lookup. If the skill is not found by exact name, the user gets a generic error suggesting `vskill find`. This forces a two-step workflow: search first with `vskill find`, then copy the exact `owner/repo/skill` path and install. The install command should be smart enough to search and disambiguate in one step.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0504-install-skill-discovery](../../../../../increments/0504-install-skill-discovery/spec.md) | ⏳ planned | 2026-03-12 |

## User Stories

- [US-001: Search Registry on Flat Name Install (P1)](./us-001-search-registry-on-flat-name-install-p1.md)
- [US-002: Interactive Disambiguation for Multiple Matches (P1)](./us-002-interactive-disambiguation-for-multiple-matches-p1.md)
- [US-003: Non-TTY Disambiguation (P1)](./us-003-non-tty-disambiguation-p1.md)
- [US-004: Result Ranking with Exact Match Priority (P1)](./us-004-result-ranking-with-exact-match-priority-p1.md)
- [US-005: --yes Flag Auto-Pick (P2)](./us-005-yes-flag-auto-pick-p2.md)
