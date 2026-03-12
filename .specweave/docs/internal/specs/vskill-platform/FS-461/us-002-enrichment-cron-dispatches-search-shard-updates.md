---
id: US-002
feature: FS-461
title: "Enrichment Cron Dispatches Search Shard Updates"
status: completed
priority: P1
created: "2026-03-09T00:00:00.000Z"
tldr: "**As a** skill searcher."
project: vskill-platform
---

# US-002: Enrichment Cron Dispatches Search Shard Updates

**Feature**: [FS-461](./FEATURE.md)

**As a** skill searcher
**I want** search results to reflect the latest star and download counts
**So that** the metrics I see are not stale between full index rebuilds

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the enrichment batch updates a skill's `githubStars` to a value different from its previous DB value, when the batch loop completes that skill, then an `updateSearchShard()` call is dispatched for that skill
- [x] **AC-US2-02**: Given the enrichment batch updates a skill's `npmDownloadsWeekly` to a different value, when the batch loop completes that skill, then an `updateSearchShard()` call is dispatched for that skill
- [x] **AC-US2-03**: Given a skill's metrics did not change during enrichment, when the batch loop completes that skill, then no search shard update is dispatched
- [x] **AC-US2-04**: Given the search shard dispatch fails, when the enrichment processes the next skill, then enrichment continues (shard dispatch is best-effort, logged but non-blocking)

---

## Implementation

**Increment**: [0461-skill-star-freshness](../../../../../increments/0461-skill-star-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
