---
id: FS-483
title: "Merge social-posts into social-media-posting"
type: feature
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
lastUpdated: 2026-03-11
tldr: "Two overlapping social media skills exist in the marketing plugin: `social-media-posting` (11 platforms, automated posting, dedup, engagement, scheduling) and `social-posts` (6+1 platforms, strategic thinking, product context, video generation, per-platform copy files)."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-140'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-140'
    syncedAt: '2026-03-11T06:14:10.078Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 215
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/215'
    syncedAt: '2026-03-11T06:14:19.220Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Merge social-posts into social-media-posting

## TL;DR

**What**: Two overlapping social media skills exist in the marketing plugin: `social-media-posting` (11 platforms, automated posting, dedup, engagement, scheduling) and `social-posts` (6+1 platforms, strategic thinking, product context, video generation, per-platform copy files).
**Status**: completed | **Priority**: P1
**User Stories**: 4

![Merge social-posts into social-media-posting illustration](assets/feature-fs-483.jpg)

## Overview

Two overlapping social media skills exist in the marketing plugin: `social-media-posting` (11 platforms, automated posting, dedup, engagement, scheduling) and `social-posts` (6+1 platforms, strategic thinking, product context, video generation, per-platform copy files). This duplication causes confusion about which skill to invoke, splits capabilities across two SKILL.md files, and means neither skill alone delivers the full social media workflow. Merging them into one definitive orchestrator eliminates the overlap and creates a single, complete skill.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0483-merge-social-skills](../../../../../increments/0483-merge-social-skills/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Merge SKILL.md Content](./us-001-merge-skill-md-content.md)
- [US-002: Add Virality and Proof Screenshot Guidance](./us-002-add-virality-and-proof-screenshot-guidance.md)
- [US-003: Merge Eval Suites](./us-003-merge-eval-suites.md)
- [US-004: Delete social-posts and Verify](./us-004-delete-social-posts-and-verify.md)
