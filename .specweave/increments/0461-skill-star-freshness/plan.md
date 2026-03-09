# Architecture Plan: Skill Star Count Freshness & Search Index Sync

## Overview

Five coordinated changes to ensure GitHub star counts and other metrics are accurate from the moment a skill is published and stay fresh between full index rebuilds. All changes are in vskill-platform (Cloudflare Workers + Next.js + Prisma + KV).

---

## C1: Fetch GitHub Stars at Publish Time (US-001)

### Problem

`publishSkill()` creates the Skill DB row with `githubStars: 0` because it never calls the GitHub API. The search shard message then propagates that zero into the KV search index.

### Design

Add a pre-upsert GitHub fetch inside `publishSkill()` in `src/lib/submission-store.ts`.

**Approach**: Reuse enrichment.ts's local `fetchGitHubMetrics()` pattern (not the popularity-fetcher one which uses `process.env.GITHUB_TOKEN`). The function is file-private in enrichment.ts, so extract a shared helper into a new module `src/lib/github-metrics.ts` that both `publishSkill()` and `runEnrichmentBatch()` can import.

```
src/lib/github-metrics.ts
  export async function fetchGitHubStars(
    repoUrl: string,
    token?: string,
    timeoutMs?: number  // default 5000
  ): Promise<{ stars: number; forks: number } | null>
```

**Integration point in publishSkill()**:

```
// Before the db.skill.upsert(), after line ~1018 (const slug = ...)
const workerEnv = getWorkerEnv();
const cfCtx = workerEnv ? null : await getCloudflareContext({ async: true }).catch(() => null);
const ghToken = workerEnv?.GITHUB_TOKEN ?? cfCtx?.env?.GITHUB_TOKEN;
const ghMetrics = await fetchGitHubStars(sub.repoUrl, ghToken, 5000).catch(() => null);
const starCount = ghMetrics?.stars ?? 0;

// Then pass githubStars: starCount in both create and update blocks of the upsert
// And pass githubStars: starCount in the queue message entry
```

**Failure handling**: `.catch(() => null)` -- any failure yields `null`, which maps to `githubStars: 0`. The publish is never blocked.

### Shared Helper Extraction

Currently three near-identical `fetchGitHub*` functions exist:
1. `enrichment.ts` line 374 -- `fetchGitHubMetrics()` with rate-limit status codes
2. `admin/enrich/route.ts` line 129 -- `fetchGitHub()` simplified
3. `popularity-fetcher.ts` line 97 -- `fetchGitHubMetrics()` with `process.env` (NOT usable in Workers)

The new `src/lib/github-metrics.ts` will replace #1 and #2. It keeps the enrichment.ts signature (returning `httpStatus` + `retryAfterMs` for rate-limit handling) and accepts an explicit `token` parameter (no `process.env`). Files #1 and #2 will import from it. File #3 stays as-is (it serves a different context with TTL caching for non-Worker callers).

### Files Changed

| File | Change |
|------|--------|
| `src/lib/github-metrics.ts` | NEW -- shared `fetchGitHubStars()` + full `fetchGitHubMetricsDetailed()` |
| `src/lib/submission-store.ts` | Call `fetchGitHubStars()` before upsert, pass result to both DB and queue msg |
| `src/lib/cron/enrichment.ts` | Import `fetchGitHubMetricsDetailed` from shared module, delete local copy |
| `src/app/api/v1/admin/enrich/route.ts` | Import from shared module, delete local `fetchGitHub()` |

---

## C2: Enrichment Cron Dispatches Incremental Search Shard Updates (US-002)

### Problem

`runEnrichmentBatch()` updates `githubStars` and `npmDownloadsWeekly` in the DB but never calls `updateSearchShard()`. The KV search index only refreshes on the full rebuild cycle (every 10 minutes at best).

### Design

After the per-skill DB transaction in the enrichment loop, compare old and new values for `githubStars` and `npmDownloadsWeekly`. If either changed, call `updateSearchShard()` inline.

**Why inline (not queue)?** Enrichment already runs in the Worker cron context with direct KV access via `opts.kv`. Sending a queue message would add a round-trip through the queue consumer for no benefit. The spec's architecture decisions section confirms this: "Inline updateSearchShard calls in enrichment loop rather than queue messages."

**Change detection**: The skill query at line 66 already selects `githubStars` and `npmDownloadsWeekly`. After the DB update, compare with the pre-fetch values.

```
// After the tx.$transaction() completes (line ~286):
const starsChanged = (updates.githubStars !== undefined) && (updates.githubStars !== skill.githubStars);
const downloadsChanged = (updates.npmDownloadsWeekly !== undefined) && (updates.npmDownloadsWeekly !== skill.npmDownloadsWeekly);

if ((starsChanged || downloadsChanged) && opts.searchKv) {
  const fresh = await db.skill.findUnique({ where: { id: skill.id }, select: SEARCH_ENTRY_SELECT });
  if (fresh && !fresh.isDeprecated) {
    await updateSearchShard(opts.searchKv, buildSearchEntry(fresh), "upsert")
      .catch(err => console.warn(`[enrichment] shard update failed for ${skill.name}:`, err));
  }
}
```

**Best-effort**: Shard update is wrapped in `.catch()` -- failures are logged but do not block enrichment of the next skill (AC-US2-04).

### New Enrichment Options

Add a `searchKv` field to `EnrichmentOptions`. The existing `kv` field is SUBMISSIONS_KV (used for stats cache invalidation). The search index lives on SEARCH_CACHE_KV, a separate namespace.

```
export interface EnrichmentOptions {
  githubToken?: string;
  batchSize?: number;
  kv?: KVNamespace;           // SUBMISSIONS_KV (cache invalidation)
  searchKv?: QueueKV;         // SEARCH_CACHE_KV (search shard updates)
  snapshotRetentionDays?: number;
}
```

Cron orchestration (build-worker-entry.ts) passes `searchKv: env.SEARCH_CACHE_KV` alongside the existing `kv: env.SUBMISSIONS_KV`.

### Helper: buildSearchEntry()

A utility function to construct a `SearchIndexEntry` from a DB skill record. Used by enrichment shard dispatch and both admin endpoints. Place in `src/lib/search-index.ts` alongside `updateSearchShard()`.

```
export function buildSearchEntry(skill: SkillForSearchEntry): SearchIndexEntry
```

Where `SkillForSearchEntry` is a type matching the select clause used by `buildSearchIndex()` (lines 118-137 of search-index.ts). This also lets `buildSearchIndex()` itself call `buildSearchEntry()` to DRY up entry construction.

### Files Changed

| File | Change |
|------|--------|
| `src/lib/search-index.ts` | Add `buildSearchEntry()` helper + `SkillForSearchEntry` type + `SEARCH_ENTRY_SELECT` |
| `src/lib/cron/enrichment.ts` | Import `updateSearchShard`, `buildSearchEntry`; add shard dispatch after DB update; add `searchKv` option |
| `scripts/build-worker-entry.ts` | Pass `searchKv: env.SEARCH_CACHE_KV` to `runEnrichmentBatch()` |

---

## C3: Admin Refresh-Skills Endpoint (US-003)

### Problem

No targeted way to force-refresh metrics for specific skills without waiting for the cron cycle.

### Design

New route: `src/app/api/v1/admin/refresh-skills/route.ts`

```
POST /api/v1/admin/refresh-skills
Auth: X-Internal-Key or SUPER_ADMIN JWT
Body: { repoUrl?, author?, skillNames?, dryRun? }
```

**Request validation** (Zod):
- At least one of `repoUrl`, `author`, `skillNames` must be provided (AC-US3-05)
- `skillNames` is `string[]` when present
- `dryRun` defaults to `false`

**Flow**:

```
1. Validate auth (hasInternalAuth || requireAdmin)
2. Parse + validate body
3. Build Prisma where clause from filters:
   - repoUrl  -> { repoUrl, isDeprecated: false }
   - author   -> { author: { equals: author, mode: "insensitive" }, isDeprecated: false }
   - skillNames -> { name: { in: skillNames }, isDeprecated: false }
   Multiple filters combine with AND
4. Query matching skills
5. If dryRun: return { skills: [...names], count }
6. For each skill:
   a. Fetch GitHub metrics (fetchGitHubStars from shared module)
   b. Update DB (githubStars, githubForks, lastCommitAt, metricsRefreshedAt)
   c. Build SearchIndexEntry via buildSearchEntry(), call updateSearchShard()
7. Return { refreshed: N, errors: N, skills: [...names] }
```

**Pattern reference**: Follows `admin/enrich/route.ts` auth and structure exactly.

### Files Changed

| File | Change |
|------|--------|
| `src/app/api/v1/admin/refresh-skills/route.ts` | NEW -- POST handler |

---

## C4: Admin Dedup-Skills Endpoint (US-004)

### Problem

Same skill appears twice under old flat slug and new hierarchical slug. No automated cleanup.

### Design

New route: `src/app/api/v1/admin/dedup-skills/route.ts`

```
POST /api/v1/admin/dedup-skills
Auth: X-Internal-Key or SUPER_ADMIN JWT
Body: { dryRun? }
```

**Duplicate detection**: Group non-deprecated skills by `(repoUrl, COALESCE(skillPath, ''))`. Groups with 2+ entries are duplicates.

```sql
SELECT "repoUrl", COALESCE("skillPath", '') as sp, COUNT(*) as cnt
FROM "Skill"
WHERE "isDeprecated" = false
GROUP BY "repoUrl", sp
HAVING COUNT(*) > 1
```

Using `COALESCE` so null skillPaths group together correctly (two skills with the same repoUrl and null skillPath are duplicates from repos with a single SKILL.md at root).

**Winner selection** (per AC-US4-02): Highest `trustScore`. Tiebreaker: most recent `certifiedAt` DESC.

**Flow**:

```
1. Auth check
2. Find duplicate groups via raw SQL or Prisma groupBy + follow-up queries
3. For each group:
   a. Load all non-deprecated skills with that (repoUrl, skillPath)
   b. Sort by trustScore DESC, certifiedAt DESC NULLS LAST
   c. Winner = first; losers = rest
4. If dryRun: return { duplicateGroups, groups: [{ winner, losers }] }
5. For each loser:
   a. Set isDeprecated = true in DB
   b. Call updateSearchShard(SEARCH_CACHE_KV, entry, "remove")
6. Return { duplicateGroups, deprecated: N }
```

### Files Changed

| File | Change |
|------|--------|
| `src/app/api/v1/admin/dedup-skills/route.ts` | NEW -- POST handler |

---

## C5: Fix SearchShardQueueMessage Type (US-005)

### Problem

`SearchShardQueueMessage.entry` is missing `ownerSlug`, `repoSlug`, `skillSlug`, and `trustTier` that `SearchIndexEntry` expects.

### Design

Add the four optional fields to `SearchShardQueueMessage.entry` in `src/lib/queue/types.ts`:

```typescript
entry: {
  // ... existing fields ...
  ownerSlug?: string;
  repoSlug?: string;
  skillSlug?: string;
  trustTier?: string;
};
```

The only current caller is in `publishSkill()` (line ~1186 of submission-store.ts), which already conditionally spreads these fields (lines 1204-1206). The runtime values are already correct; the type just needs to accept them.

**Alternative considered**: Make `SearchShardQueueMessage.entry` directly reference `SearchIndexEntry`. This is cleaner but creates a coupling between the queue types module (kept minimal for Worker-safe imports) and search-index.ts. Keep the current inline type but add the missing fields -- minimal change, maximum safety.

### Files Changed

| File | Change |
|------|--------|
| `src/lib/queue/types.ts` | Add `ownerSlug?`, `repoSlug?`, `skillSlug?`, `trustTier?` to entry type |

---

## Data Flow Diagram

```
                        publishSkill()
                             |
                    +--------+--------+
                    |                 |
             fetchGitHubStars()   db.skill.upsert()
             (5s timeout,         (githubStars = fetched)
              best-effort)              |
                                  queue.send({
                                    type: "rebuild_search_shard",
                                    entry: { githubStars, ownerSlug, ... }
                                  })
                                        |
                                  queue consumer
                                        |
                                  updateSearchShard(KV)


              runEnrichmentBatch() [hourly cron]
                        |
          for each skill in batch:
                        |
          +-------------+-------------+
          |                           |
    fetchGitHubMetrics()        db.skill.update()
    fetchNpmDownloadsBulk()           |
                              if stars or downloads changed:
                                      |
                              updateSearchShard(SEARCH_CACHE_KV)
                              (inline, best-effort)


           POST /admin/refresh-skills
                        |
              filter skills from DB
                        |
              for each skill:
                        |
          +-------------+-------------+
          |                           |
    fetchGitHubMetrics()        db.skill.update()
                                      |
                              updateSearchShard(SEARCH_CACHE_KV)


           POST /admin/dedup-skills
                        |
              find duplicate groups
                        |
              for each loser:
                        |
          +-------------+-------------+
          |                           |
    db.skill.update()         updateSearchShard(KV,
    (isDeprecated: true)       entry, "remove")
```

---

## Cross-Cutting Concerns

### Error Isolation

Every new external call (GitHub fetch at publish, shard update in enrichment, shard update in admin) is wrapped in `.catch()` with logging. No feature degrades the reliability of its host operation.

### Token Resolution

All GitHub API calls in Worker context use explicit token parameter, never `process.env.GITHUB_TOKEN`. Token source:
- `publishSkill()`: `getWorkerEnv()?.GITHUB_TOKEN` or `getCloudflareContext().env.GITHUB_TOKEN`
- `enrichment.ts`: Already receives `githubToken` via options
- Admin endpoints: `getCloudflareContext().env.GITHUB_TOKEN`

### KV Namespace Mapping

| Operation | KV Namespace | Variable |
|-----------|-------------|----------|
| Search shard upsert/remove | SEARCH_CACHE_KV | `env.SEARCH_CACHE_KV` |
| Submission state | SUBMISSIONS_KV | `env.SUBMISSIONS_KV` |
| Stats cache invalidation | SUBMISSIONS_KV | `env.SUBMISSIONS_KV` |

Enrichment currently only receives SUBMISSIONS_KV. The plan adds `searchKv` option to also receive SEARCH_CACHE_KV.

### Shared Code Extraction Summary

| New Module | Replaces | Consumers |
|-----------|----------|-----------|
| `src/lib/github-metrics.ts` | enrichment.ts local `fetchGitHubMetrics`, admin/enrich `fetchGitHub` | publishSkill, enrichment, admin/refresh-skills, admin/enrich |
| `buildSearchEntry()` in search-index.ts | inline entry construction in buildSearchIndex | enrichment shard dispatch, admin/refresh-skills, admin/dedup-skills, buildSearchIndex |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GitHub API rate limit during publish burst | Low | Low | 5s timeout + fallback to 0 stars; rate-limit backoff in enrichment |
| Shard update adds latency to enrichment loop | Medium | Low | Each shard update is ~2 KV reads + 2 KV writes (~10ms). 50-skill batch adds ~500ms max |
| Dedup incorrectly deprecates the wrong entry | Low | High | Winner logic is deterministic (trustScore DESC, certifiedAt DESC). dryRun mode for verification |
| SearchShardQueueMessage type change breaks consumers | Very Low | Low | Fields are optional, backward-compatible |

---

## Implementation Order

1. **C5** -- Fix `SearchShardQueueMessage` type (pure type change, no runtime effect)
2. **C1** -- Extract `github-metrics.ts`, integrate into `publishSkill()`
3. **C2** -- Add `buildSearchEntry()`, integrate shard dispatch into enrichment
4. **C3** -- Admin refresh-skills endpoint
5. **C4** -- Admin dedup-skills endpoint

C5 first unblocks clean types for all subsequent work. C1 and C2 are the core value. C3 and C4 are independent admin tooling that build on the shared helpers from C1/C2.
