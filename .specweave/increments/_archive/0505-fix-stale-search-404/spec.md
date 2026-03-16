---
increment: 0505-fix-stale-search-404
title: Fix Stale Search Results Returning 404
type: bugfix
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Stale Search Results Returning 404

## Problem Statement

When users run `npx vskill find <query>`, results include skills that have been hard-deleted from Postgres but still exist in Cloudflare KV search index shards. Clicking these results on verified-skill.com returns 404. The admin hard-delete endpoint (`/api/v1/admin/skills/.../delete`) removes records from Postgres but never calls `updateSearchShard(..., "remove")`, leaving stale entries in KV indefinitely. KV entries have no TTL, so stale data persists until a manual full index rebuild is triggered.

Example: `steipete/clawdis/skill-creator` (264K stars) appears in search results but 404s on the website.

The block endpoint (`/api/v1/admin/skills/.../block`) already does this correctly -- it calls `updateSearchShard(searchKv, skill, "remove")` after updating the DB. The delete endpoint simply lacks the same pattern.

## Goals

- Prevent future stale entries by cleaning KV search index on hard-delete
- Heal existing stale entries by validating edge-only search results against DB
- Add defense-in-depth TTL on KV shard writes so stale entries self-expire

## User Stories

### US-001: Delete Endpoint KV Cleanup (P0)
**Project**: vskill-platform

**As an** admin deleting a malicious or test skill
**I want** the hard-delete endpoint to remove the skill from the KV search index
**So that** deleted skills stop appearing in search results immediately

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill exists in both Postgres and KV search index, when an admin calls `DELETE /api/v1/admin/skills/{owner}/{repo}/{skill}/delete`, then `updateSearchShard(kv, skillEntry, "remove")` is called before the DB transaction deletes the skill record
- [x] **AC-US1-02**: Given the skill's data is needed for `updateSearchShard` (name, author, category, etc.), when the delete endpoint fetches the skill record, then it selects all fields required by `SearchIndexEntry` using `SEARCH_ENTRY_SELECT` before deleting
- [x] **AC-US1-03**: Given the KV shard removal succeeds, when the delete endpoint completes, then `invalidateSearchIndex(searchKv)` is called to force a meta refresh
- [x] **AC-US1-04**: Given the KV operation fails (network error, KV unavailable), when the delete endpoint runs, then the DB deletion still proceeds and the KV failure is logged but does not block the response

---

### US-002: Search Result Existence Validation (P1)
**Project**: vskill-platform

**As a** developer searching for skills via CLI or website
**I want** search results that only contain skills that actually exist
**So that** I never encounter a 404 when clicking a search result

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the search source is "edge" (KV-only, Postgres returned zero results), when the search route returns results, then each result's `name` is batch-validated against Postgres and non-existent skills are filtered out before the response
- [x] **AC-US2-02**: Given the search source is "edge+postgres" or "postgres", when the search route returns results, then no additional existence validation is performed (Postgres results are inherently fresh)
- [x] **AC-US2-03**: Given the DB validation query fails, when the search route processes edge-only results, then all edge results are returned unfiltered (graceful degradation) and a warning is logged

---

### US-003: KV Shard TTL Defense-in-Depth (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** KV search index entries to have a 7-day TTL
**So that** any stale entries that slip through (missed cleanup, race conditions) self-expire rather than persisting indefinitely

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `buildSearchIndex()` writes name shards and author shards to KV, when the shard data is written via `kv.put()`, then `expirationTtl: 604800` (7 days in seconds) is included in the put options
- [x] **AC-US3-02**: Given `updateSearchShard()` upserts a single entry into a shard, when the shard is written back to KV via `kv.put()`, then `expirationTtl: 604800` is included in the put options
- [x] **AC-US3-03**: Given the search index metadata key is written by `buildSearchIndex()`, when the meta is stored, then it also uses `expirationTtl: 604800`

## Out of Scope

- Retroactive cleanup of currently stale entries (the TTL + validation will heal them over time)
- Soft-delete functionality for the admin delete endpoint
- Full index rebuild scheduling or cron-based refresh
- Changes to the block endpoint (already correctly removes from KV)
- Changes to the CLI (`vskill find`) -- the fix is server-side only

## Technical Notes

### Dependencies
- `src/lib/search-index.ts` -- `updateSearchShard()`, `invalidateSearchIndex()`, `buildSearchIndex()`, `SEARCH_ENTRY_SELECT`, `buildSearchEntry()`
- `src/lib/env-resolve.ts` -- `resolveEnv()` for accessing `SEARCH_CACHE_KV`
- `src/app/api/v1/admin/skills/[owner]/[repo]/[skill]/block/route.ts` -- reference implementation for KV cleanup pattern

### Constraints
- KV shard removal must happen BEFORE the DB transaction to ensure the skill data (name, author, etc.) is still available for building the `SearchIndexEntry`
- The `QueueKV` type used by `updateSearchShard` does not natively support TTL in `.put()` options -- the implementation must use the Cloudflare KV API's `expirationTtl` parameter which the `QueueKV` interface may need to accommodate
- Existence validation in the search route must not add significant latency -- use a single `SELECT name FROM Skill WHERE name IN (...)` batch query, not per-result lookups

### Architecture Decisions
- Follow the same pattern as the block endpoint for KV cleanup (proven, already in production)
- TTL of 7 days balances freshness (stale entries expire within a week) against rebuild frequency (daily rebuilds refresh TTL, so entries never actually expire under normal operation)
- Existence validation only runs for edge-only results to avoid penalizing the common case where Postgres is available

## Non-Functional Requirements

- **Performance**: Existence validation batch query must complete in under 50ms for up to 200 skill names
- **Reliability**: KV failures in the delete endpoint must not block the DB deletion (best-effort pattern)
- **Observability**: Log KV cleanup success/failure in the delete endpoint for audit trail

## Edge Cases

- Skill name contains special characters (slashes, hyphens) -- `getNameShardKeys()` already handles this, delete cleanup must use the same function
- Skill was already removed from KV (e.g., by a prior block operation) -- `updateSearchShard("remove")` is idempotent (filters by name, no-op if absent)
- Concurrent delete and search requests -- TTL provides eventual consistency safety net
- KV is unreachable during delete -- DB deletion proceeds, stale entry expires via TTL within 7 days
- Full index rebuild runs between delete and TTL expiry -- `buildSearchIndex()` queries Postgres and skips deleted skills, effectively cleaning up stale entries

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| QueueKV interface doesn't support expirationTtl option | 0.4 | 3 | 1.2 | Check Cloudflare KV types; extend QueueKV interface if needed |
| Existence validation adds latency to edge-only searches | 0.3 | 4 | 1.2 | Single batch IN query; only runs when Postgres was unreachable (rare) |
| 7-day TTL causes index gaps if rebuild fails for 7+ days | 0.1 | 6 | 0.6 | Monitoring alert on rebuild-index failures; manual trigger as fallback |

## Success Metrics

- Zero 404s from search results for skills that have been hard-deleted
- Delete endpoint response includes confirmation of KV shard cleanup
- Edge-only search results contain only skills that exist in Postgres
