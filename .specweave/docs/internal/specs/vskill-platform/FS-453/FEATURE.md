---
id: FS-453
title: 'Unify skill page badges: remove redundant TierBadge'
type: feature
status: completed
priority: P1
created: 2026-03-07T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  The skill detail page renders TierBadge ('VERIFIED') and TrustBadge ('T3
  VERIFIED') side-by-side.
complexity: low
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-52
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-52'
    syncedAt: '2026-03-10T07:33:15.500Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 117
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/117
    syncedAt: '2026-03-10T07:33:16.281Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Unify skill page badges: remove redundant TierBadge

## TL;DR

**What**: The skill detail page renders TierBadge ("VERIFIED") and TrustBadge ("T3 VERIFIED") side-by-side.
**Status**: completed | **Priority**: P1
**User Stories**: 1

![Unify skill page badges: remove redundant TierBadge illustration](assets/feature-fs-453.jpg)

## Overview

The skill detail page renders TierBadge ("VERIFIED") and TrustBadge ("T3 VERIFIED") side-by-side. When `certTier=VERIFIED` maps to `trustTier=T3`, both say the same thing — redundant. TrustBadge is the richer composite signal (T0-T4). Remove TierBadge from the skill detail page, keep only TrustBadge.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0453-unify-skill-page-badges](../../../../../increments/0453-unify-skill-page-badges/spec.md) | ✅ completed | 2026-03-07T00:00:00.000Z |

## User Stories

- [US-001: Remove redundant TierBadge from skill detail page (P1)](./us-001-remove-redundant-tierbadge-from-skill-detail-page-p1.md)
