---
id: FS-440
title: Fix Anthropic Skills Missing from Search
type: feature
status: ready_for_review
priority: P0
created: 2026-03-06
lastUpdated: 2026-03-06
tldr: Anthropic's official skills (skill-creator, etc.) are completely absent
  from verified-skill.com search results.
complexity: medium
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 7
    url: https://github.com/anton-abyzov/vskill-platform/milestone/7
---

# Fix Anthropic Skills Missing from Search

## TL;DR

**What**: Anthropic's official skills (skill-creator, etc.) are completely absent from verified-skill.com search results.
**Status**: ready_for_review | **Priority**: P0
**User Stories**: 3

![Fix Anthropic Skills Missing from Search illustration](assets/feature-fs-440.jpg)

## Overview

Anthropic's official skills (skill-creator, etc.) are completely absent from verified-skill.com search results. Third-party forks appear instead. Two root causes:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0440-fix-anthropic-skills-search](../../../../../increments/0440-fix-anthropic-skills-search/spec.md) | ⏳ ready_for_review | 2026-03-06 |

## User Stories

- [US-001: Remove Zero-Star Filter for Vendor Orgs](./us-001-remove-zero-star-filter-for-vendor-orgs.md)
- [US-002: Add CertTier Boost to Search Ranking](./us-002-add-certtier-boost-to-search-ranking.md)
- [US-003: Sync VENDOR_ORGS Lists Across Codebase](./us-003-sync-vendor-orgs-lists-across-codebase.md)
