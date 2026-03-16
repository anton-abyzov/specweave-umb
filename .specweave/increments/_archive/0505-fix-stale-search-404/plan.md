# Implementation Plan: Fix Stale Search Results Returning 404

## Overview

Three-layer fix for stale KV search index entries caused by the admin hard-delete endpoint missing KV cleanup. The block endpoint already implements the correct pattern -- this increment applies the same pattern to delete, adds edge-only existence validation in the search route, and sets TTL on all KV shard writes as defense-in-depth.

No new architectural decisions. No schema changes. No new dependencies. All changes follow proven patterns already in production.

## Architecture

### Affected Components

```
┌──────────────────────────────────────────────────────────────────┐
│ Admin Delete Endpoint (US-001)                                   │
│ src/app/api/v1/admin/skills/[owner]/[repo]/[skill]/delete/       │
│                                                                  │
│  1. Fetch skill with SEARCH_ENTRY_SELECT (before delete)         │
│  2. updateSearchShard(kv, entry, "remove")  ← NEW               │
│  3. invalidateSearchIndex(kv)               ← NEW               │
│  4. DB $transaction delete (existing)                            │
│                                                                  │
│  KV failure → log + continue (best-effort, matches block)        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Search Route (US-002)                                            │
│ src/app/api/v1/skills/search/route.ts                            │
│                                                                  │
│  After merge, when searchSource === "edge":                      │
│    SELECT name FROM "Skill" WHERE name IN (...)                  │
│    Filter out names not found in Postgres                        │
│    DB failure → return unfiltered (graceful degradation)          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Search Index Library (US-003)                                    │
│ src/lib/search-index.ts                                          │
│                                                                  │
│  buildSearchIndex():                                             │
│    kv.put(shardKey, data, { expirationTtl: 604800 })  ← NEW     │
│    kv.put(META_KEY, meta, { expirationTtl: 604800 })  ← NEW     │
│                                                                  │
│  updateSearchShard():                                            │
│    kv.put(kvKey, data, { expirationTtl: 604800 })     ← NEW     │
│    kv.put(authorKvKey, data, { expirationTtl: 604800 })← NEW    │
│    kv.put(META_KEY, meta, { expirationTtl: 604800 })  ← NEW     │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow: Delete with KV Cleanup

```
Admin DELETE request
       │
       ▼
  Authenticate (admin or internal key)
       │
       ▼
  db.skill.findFirst({ select: SEARCH_ENTRY_SELECT })
       │               ↑ expanded from {id, name, displayName, author}
       ▼
  resolveEnv() → SEARCH_CACHE_KV
       │
       ▼
  buildSearchEntry(skill) → SearchIndexEntry
       │
       ▼
  updateSearchShard(kv, entry, "remove")    ← best-effort
       │
       ▼
  invalidateSearchIndex(kv)                 ← best-effort
       │
       ▼
  db.$transaction (delete cascading records) ← existing, unchanged
       │
       ▼
  Response { deleted, kvCleanup: true/false }
```

### Data Flow: Edge-Only Search Validation

```
GET /api/v1/skills/search?q=...
       │
       ▼
  searchSkillsEdge() → edgeResults
  searchSkills()     → pgResults (may be empty)
       │
       ▼
  Merge results, determine searchSource
       │
       ▼
  searchSource === "edge"?
       │          │
      YES         NO → skip validation (Postgres results are fresh)
       │
       ▼
  Extract names from merged results
       │
       ▼
  SELECT name FROM "Skill" WHERE name IN (...names)
       │
       ▼
  Filter: keep only results whose name exists in DB
       │  (DB failure → return all unfiltered + log warning)
       ▼
  Continue to enrichment, sort, dedup, paginate
```

## Technology Stack

- **Runtime**: Cloudflare Workers (via OpenNext)
- **Database**: Postgres (Neon) via Prisma
- **KV Store**: Cloudflare KV (`SEARCH_CACHE_KV`)
- **Framework**: Next.js 15 API routes

No new dependencies. All imports already used by the block endpoint.

## Implementation Phases

### Phase 1: Delete Endpoint KV Cleanup (US-001, P0)

Modify the delete endpoint to mirror the block endpoint's KV cleanup pattern.

**Changes to `delete/route.ts`**:
1. Add imports: `updateSearchShard`, `invalidateSearchIndex`, `buildSearchEntry`, `SEARCH_ENTRY_SELECT` from `@/lib/search-index`, `resolveEnv` from `@/lib/env-resolve`
2. Expand the existing `db.skill.findFirst` select to use `SEARCH_ENTRY_SELECT` (currently only selects `id, name, displayName, author`)
3. Before the `$transaction`, call `updateSearchShard(kv, entry, "remove")` wrapped in try/catch
4. After shard removal, call `invalidateSearchIndex(kv)` (also best-effort)
5. Track `kvCleanup: true/false` in the response for observability

**Key constraint**: KV removal MUST happen before the DB transaction. Once the skill is deleted from Postgres, the data needed to build `SearchIndexEntry` (name, author, category, etc.) is gone. The block endpoint does this correctly and we follow the same order.

**Error handling**: KV failures are logged but do not block the DB deletion. This matches the block endpoint's `try { ... } catch { /* best-effort */ }` pattern.

### Phase 2: Search Result Existence Validation (US-002, P1)

Add a validation step in the search route for edge-only results.

**Changes to `search/route.ts`**:
1. After merge and before enrichment, check if `searchSource === "edge"`
2. If edge-only: extract all `name` values from `results`, run `SELECT name FROM "Skill" WHERE name IN (...)`
3. Build a `Set<string>` of existing names, filter results to keep only matches
4. If the DB query fails, log a warning and return all results unfiltered (graceful degradation)
5. For `"edge+postgres"` or `"postgres"` sources, skip validation entirely

**Performance**: Single batch `IN` query against the `name` column (primary key or unique index). For up to 200 names, this completes well under 50ms.

### Phase 3: KV Shard TTL (US-003, P1)

Add `expirationTtl: 604800` (7 days) to all `kv.put()` calls in search-index.ts.

**Changes to `search-index.ts`**:
1. Define constant: `const SHARD_TTL_SECONDS = 604800;` (7 days)
2. `buildSearchIndex()`: Add `{ expirationTtl: SHARD_TTL_SECONDS }` to the `kv.put()` calls for name shards, author shards, and the meta key (3 call sites)
3. `updateSearchShard()`: Add `{ expirationTtl: SHARD_TTL_SECONDS }` to the `kv.put()` calls for name shards, author shard, and meta key (3 call sites)

**QueueKV compatibility**: Already confirmed -- `QueueKV.put()` signature is `put(key: string, value: string, options?: { expirationTtl?: number })`. No interface changes needed.

**TTL rationale**: 7 days balances staleness window against rebuild frequency. Daily full index rebuilds refresh the TTL, so entries never actually expire under normal operation. If rebuilds fail for 7+ days, stale entries self-expire rather than persisting indefinitely.

## Testing Strategy

### Unit Tests

**Delete endpoint** (`delete/route.test.ts`):
- Test that `updateSearchShard` is called with `"remove"` action and correct entry shape
- Test that `invalidateSearchIndex` is called after shard removal
- Test that DB deletion proceeds even when KV operations throw
- Test that `SEARCH_ENTRY_SELECT` fields are fetched (not just id/name)
- Test response includes `kvCleanup` status

**Search route** (`search/route.test.ts`):
- Test edge-only results are filtered against DB existence check
- Test `"edge+postgres"` results skip validation
- Test graceful degradation when DB validation query fails
- Test empty edge results skip validation

**Search index** (`search-index.test.ts`):
- Test `buildSearchIndex` passes `expirationTtl: 604800` to all `kv.put()` calls
- Test `updateSearchShard` passes `expirationTtl: 604800` to all `kv.put()` calls

### Integration Tests

- Delete a skill via admin endpoint, verify it no longer appears in edge search results
- Search with edge-only source, verify non-existent skills are filtered out

## Technical Challenges

### Challenge 1: Select Expansion in Delete Endpoint
**Problem**: The delete endpoint currently selects only `{ id, name, displayName, author }`. Building a `SearchIndexEntry` requires all fields in `SEARCH_ENTRY_SELECT` (name, displayName, command, pluginName, author, category, certTier, githubStars, trustScore, trustTier, npmDownloadsWeekly, vskillInstalls, repoUrl, isTainted, ownerSlug, repoSlug, skillSlug).
**Solution**: Replace the select with `SEARCH_ENTRY_SELECT` plus `id` (still needed for the transaction). This is a safe expansion -- no behavior change for existing fields, just more data fetched.

### Challenge 2: TTL on Shared Meta Key
**Problem**: Both `buildSearchIndex` and `updateSearchShard` write to `META_KEY`. If `updateSearchShard` runs shortly after a full rebuild, it resets the TTL on meta to 7 days from that point -- which is correct behavior (keeps meta alive as long as index is actively used).
**Solution**: No issue. TTL refresh on write is the desired behavior. The meta key only expires if no writes happen for 7 days, which would indicate the index is truly stale.

### Challenge 3: Edge-Only Validation Latency
**Problem**: Adding a DB query to edge-only search results could add latency.
**Solution**: Edge-only means Postgres was unreachable or returned zero results. If Postgres was unreachable, the validation query will also fail and graceful degradation returns unfiltered results (no added latency). If Postgres returned zero but is reachable, the validation query is a fast `IN` lookup (sub-50ms for 200 names). Net impact: negligible in the common case, zero in the failure case.

## Risks

| Risk | Mitigation |
|------|------------|
| Expanded select in delete endpoint fetches more data | Negligible -- single row fetch, same DB round trip |
| TTL causes index gaps if rebuilds fail 7+ days | Existing monitoring on rebuild-index; this is defense-in-depth, not primary cleanup |
| Concurrent delete + search race | TTL provides eventual consistency; delete removes from KV before DB, so the window where KV has entry but DB doesn't is minimized |

## No New ADRs Required

All changes follow established patterns:
- KV cleanup on admin mutations (ADR: N/A -- pattern established by block endpoint, no formal ADR exists)
- Best-effort KV operations with DB as source of truth (consistent across all admin endpoints)
- TTL on KV writes (Cloudflare KV native feature, `QueueKV` interface already supports it)
- Batch existence validation (standard Prisma `findMany` with `IN` filter)

## Domain Skill Delegation

No domain skill delegation needed. This is a backend-only bug fix in existing Next.js API routes and a shared library file. All changes are TypeScript, following patterns already in the codebase. No frontend, infrastructure, or schema changes.
