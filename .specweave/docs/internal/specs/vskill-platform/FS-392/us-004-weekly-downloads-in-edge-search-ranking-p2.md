---
id: US-004
feature: FS-392
title: "Weekly Downloads in Edge Search Ranking (P2)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** developer searching for skills."
project: vskill-platform
---

# US-004: Weekly Downloads in Edge Search Ranking (P2)

**Feature**: [FS-392](./FEATURE.md)

**As a** developer searching for skills
**I want** weekly download count used as a third tiebreaker in edge search results
**So that** actively-downloaded skills rank higher among otherwise equal results

---

## Acceptance Criteria

- [x] **AC-US4-01**: `SearchIndexEntry` interface includes `npmDownloadsWeekly: number`
- [x] **AC-US4-02**: `buildSearchIndex` selects `npmDownloadsWeekly` from Postgres and populates it into each shard entry
- [x] **AC-US4-03**: Shard sort order is `trustScore DESC, githubStars DESC, npmDownloadsWeekly DESC`
- [x] **AC-US4-04**: `updateSearchShard` upsert uses the same three-field sort order
- [x] **AC-US4-05**: `INDEX_VERSION` is bumped to 4 to trigger full index rebuild on deploy
- [x] **AC-US4-06**: Edge search results in `search.ts` sort by `trustScore DESC, githubStars DESC, npmDownloadsWeekly DESC` (KV path and Postgres fallback)
- [x] **AC-US4-07**: The `SearchResult` type in `search.ts` includes `npmDownloadsWeekly`

---

## Implementation

**Increment**: [0392-npm-weekly-downloads](../../../../../increments/0392-npm-weekly-downloads/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Add npmDownloadsWeekly to SearchIndexEntry and bump INDEX_VERSION
- [x] **T-009**: Update buildSearchIndex and updateSearchShard with 3-field sort
- [x] **T-010**: Update edge search sort and SearchResult type in search.ts
- [x] **T-011**: Update SearchShardQueueMessage and publish path
