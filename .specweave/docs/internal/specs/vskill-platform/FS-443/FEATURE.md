---
id: FS-443
title: Fix search ranking to sort by star count
type: feature
status: completed
priority: P1
created: 2026-03-07T00:00:00.000Z
lastUpdated: 2026-03-07
tldr: Search results on verified-skill.com do not reflect user expectations.
complexity: medium
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 9
    url: https://github.com/anton-abyzov/vskill-platform/milestone/9
---

# Fix search ranking to sort by star count

## TL;DR

**What**: Search results on verified-skill.com do not reflect user expectations.
**Status**: completed | **Priority**: P1
**User Stories**: 2

![Fix search ranking to sort by star count illustration](assets/feature-fs-443.jpg)

## Overview

Search results on verified-skill.com do not reflect user expectations. The Anthropic frontend-design skill has 79.4k GitHub stars yet appears near the bottom of search results. The root cause is the blended ranking formula: Relevance(50%) + Popularity(30%) + CertBonus(20%), where stars are only 45% of the Popularity component -- giving stars an effective weight of ~13.5%. Users expect the most popular skills (by stars) to appear first. Additionally, the ILIKE fallback path sorts by trustScore first instead of stars, creating inconsistent ranking across search paths.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0443-search-rank-by-stars](../../../../../increments/0443-search-rank-by-stars/spec.md) | ✅ completed | 2026-03-07T00:00:00.000Z |

## User Stories

- [US-001: Star-based search ranking (P1)](./us-001-star-based-search-ranking-p1.md)
- [US-002: CERTIFIED-first ordering preserved (P1)](./us-002-certified-first-ordering-preserved-p1.md)
