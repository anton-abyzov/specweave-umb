---
id: FS-503
title: "Fix vendor auto-certification gap in publish pipeline"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "Fix vendor auto-certification gap where vendor org skills were published as VERIFIED instead of CERTIFIED due to missing isVendor flag propagation in the publish pipeline."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-181'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-181'
    syncedAt: '2026-03-12T02:31:40.225Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 973
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/973'
    syncedAt: '2026-03-12T02:31:46.851Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix vendor auto-certification gap in publish pipeline

## TL;DR

**What**: Fix vendor auto-certification gap where vendor org skills were published as VERIFIED instead of CERTIFIED due to missing isVendor flag propagation in the publish pipeline.
**Status**: completed | **Priority**: P1
**User Stories**: 3

![Fix vendor auto-certification gap in publish pipeline illustration](assets/feature-fs-503.jpg)

## Overview

Skills from certified vendor organizations (anthropics, openai, google, microsoft, vercel, cloudflare, google-gemini) displayed as "unreviewed" instead of "certified" in `vskill find` results. Three gaps in the trust pipeline were fixed: (1) `markVendor()` now sets `isVendor=true` on the submission record before `publishSkill()` runs, (2) `publishSkill()` has a defense-in-depth fallback via `isVendorOrg(owner)`, and (3) existing 626 vendor skills were backfilled to CERTIFIED/T4 via the admin backfill endpoint.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0503-vendor-auto-certification-fix](../../../../../increments/0503-vendor-auto-certification-fix/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Mark submission as vendor before publishing (P1)](./us-001-mark-submission-as-vendor-before-publishing-p1.md)
- [US-002: Add vendor org fallback in publishSkill (P1)](./us-002-add-vendor-org-fallback-in-publishskill-p1.md)
- [US-003: Backfill existing vendor skills (P2)](./us-003-backfill-existing-vendor-skills-p2.md)
