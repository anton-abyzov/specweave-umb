---
id: US-001
feature: FS-505
title: "Delete Endpoint KV Cleanup (P0)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As an** admin deleting a malicious or test skill."
project: vskill-platform
---

# US-001: Delete Endpoint KV Cleanup (P0)

**Feature**: [FS-505](./FEATURE.md)

**As an** admin deleting a malicious or test skill
**I want** the hard-delete endpoint to remove the skill from the KV search index
**So that** deleted skills stop appearing in search results immediately

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill exists in both Postgres and KV search index, when an admin calls `DELETE /api/v1/admin/skills/{owner}/{repo}/{skill}/delete`, then `updateSearchShard(kv, skillEntry, "remove")` is called before the DB transaction deletes the skill record
- [x] **AC-US1-02**: Given the skill's data is needed for `updateSearchShard` (name, author, category, etc.), when the delete endpoint fetches the skill record, then it selects all fields required by `SearchIndexEntry` using `SEARCH_ENTRY_SELECT` before deleting
- [x] **AC-US1-03**: Given the KV shard removal succeeds, when the delete endpoint completes, then `invalidateSearchIndex(searchKv)` is called to force a meta refresh
- [x] **AC-US1-04**: Given the KV operation fails (network error, KV unavailable), when the delete endpoint runs, then the DB deletion still proceeds and the KV failure is logged but does not block the response

---

## Implementation

**Increment**: [0505-fix-stale-search-404](../../../../../increments/0505-fix-stale-search-404/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Write failing tests for delete endpoint KV cleanup (TDD Red)
- [x] **T-002**: Implement KV cleanup in delete endpoint (TDD Green + Refactor)
