---
id: FS-392
title: "npm Weekly Download Stats Integration"
type: feature
status: completed
priority: P1
created: "2026-03-01T00:00:00.000Z"
lastUpdated: 2026-03-10
tldr: "Add `npmDownloadsWeekly` as a separate field alongside the existing monthly `npmDownloads`."
complexity: high
stakeholder_relevant: true
---

# npm Weekly Download Stats Integration

## TL;DR

**What**: Add `npmDownloadsWeekly` as a separate field alongside the existing monthly `npmDownloads`.
**Status**: completed | **Priority**: P1
**User Stories**: 4

## Overview

Add `npmDownloadsWeekly` as a separate field alongside the existing monthly `npmDownloads`. Weekly downloads are used for display on skill detail pages and as a third tiebreaker in edge search sorting. The existing monthly field and trending formula remain unchanged.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0392-npm-weekly-downloads](../../../../../increments/0392-npm-weekly-downloads/spec.md) | ✅ completed | 2026-03-01T00:00:00.000Z |

## User Stories

- [US-001: Weekly Downloads Database Field (P1)](./us-001-weekly-downloads-database-field-p1.md)
- [US-002: Weekly Downloads Enrichment (P1)](./us-002-weekly-downloads-enrichment-p1.md)
- [US-003: Weekly Downloads in Skill Detail Page (P1)](./us-003-weekly-downloads-in-skill-detail-page-p1.md)
- [US-004: Weekly Downloads in Edge Search Ranking (P2)](./us-004-weekly-downloads-in-edge-search-ranking-p2.md)
