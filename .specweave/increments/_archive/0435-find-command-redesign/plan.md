# Architecture Plan: 0435-find-command-redesign

## Overview

Two-repo change that surfaces `vskillInstalls` through the search pipeline (vskill-platform) and redesigns the CLI `find` output (vskill). All changes are additive -- no breaking API changes, no schema migrations, no new dependencies.

---

## Component 1: Search Index Extension (vskill-platform)

### 1A. `SearchIndexEntry` -- add `vskillInstalls`

**File**: `src/lib/search-index.ts`

```
SearchIndexEntry (KV shard entry)
──────────────────────────────────────
name              string
displayName       string
command           string | null
pluginName        string | null
author            string
category          string
certTier          string
githubStars       number
trustScore        number
npmDownloadsWeekly number
repoUrl           string
isTainted         boolean | undefined
+ vskillInstalls  number              <-- NEW (default 0)
```

**Rationale**: `vskillInstalls` already exists in the `Skill` Prisma model (`@default(0)`, indexed DESC). `buildSearchIndex()` already reads full `Skill` rows via `findMany` -- just add `vskillInstalls: true` to the `select` and include it in the entry object.

**Shard size impact**: One additional number field per entry. At 5,000 skills, ~25 KB total across all shards. Negligible.

### 1B. `INDEX_VERSION` bump 4 -> 5

**File**: `src/lib/search-index.ts`

```typescript
export const INDEX_VERSION = 5;
```

**Effect**: Next admin rebuild call detects version mismatch in `SearchIndexMeta.version` and triggers a full shard rebuild. All shards will include `vskillInstalls` after rebuild completes.

### 1C. `SearchShardQueueMessage.entry` -- add `vskillInstalls`

**File**: `src/lib/queue/types.ts`

The `SearchShardQueueMessage.entry` type mirrors `SearchIndexEntry` fields for incremental shard updates. Add `vskillInstalls?: number` to maintain parity.

### 1D. `buildSearchIndex()` -- include `vskillInstalls` in entries

**File**: `src/lib/search-index.ts`, `buildSearchIndex()` function

Two changes:
1. Add `vskillInstalls: true` to the Prisma `select` clause
2. Include `vskillInstalls: skill.vskillInstalls ?? 0` in the entry construction (both name-shard and author-shard loops)

### 1E. `updateSearchShard()` -- propagate `vskillInstalls`

**File**: `src/lib/search-index.ts`, `updateSearchShard()` function

No code change needed. `updateSearchShard` accepts a full `SearchIndexEntry` and writes it to KV. Since the type now includes `vskillInstalls`, callers that build the entry will naturally include it.

Callers to audit: `processSubmission` in `submission-store.ts` constructs the `SearchShardQueueMessage.entry`. That code reads from the DB Skill row, which has `vskillInstalls`. Confirm the field is plumbed through.

---

## Component 2: Search API Response (vskill-platform)

### 2A. `SearchResult` -- add `vskillInstalls`

**File**: `src/lib/search.ts`

```
SearchResult (API response type)
──────────────────────────────────────
name              string
displayName       string
command           string | null
pluginName        string | null
author            string
repoUrl           string
category          string
certTier          string
githubStars       number
trustScore        number
npmDownloadsWeekly number | undefined
highlight         string
isTainted         boolean | undefined
isBlocked         boolean | undefined
threatType        string | undefined
severity          string | undefined
+ vskillInstalls  number              <-- NEW (default 0)
```

### 2B. `SkillSearchRow` -- add `vskillInstalls`

**File**: `src/lib/search.ts`

```
SkillSearchRow (raw DB row from $queryRaw)
──────────────────────────────────────
...existing fields...
+ vskillInstalls  number              <-- NEW
```

### 2C. `searchSkillsEdge()` -- map `entry.vskillInstalls`

**File**: `src/lib/search.ts`, `searchSkillsEdge()` function

In the `resultSlice.map()` block, add:
```typescript
vskillInstalls: entry.vskillInstalls ?? 0,
```

### 2D. `searchSkills()` -- add `"vskillInstalls"` to SQL queries

**File**: `src/lib/search.ts`, `searchSkills()` function

Two SQL queries need the new column:

1. **tsvector query** (line ~317): Add `"vskillInstalls"` to the SELECT list
2. **ILIKE fallback** (line ~348): Add `"vskillInstalls"` to the SELECT list

In the `resultRows.map()` block, add:
```typescript
vskillInstalls: row.vskillInstalls ?? 0,
```

### 2E. `searchBlocklistEntries()` -- blocked entries get `vskillInstalls: 0`

**File**: `src/lib/search.ts`

Blocked entries are not real skills -- they have no install count. Add `vskillInstalls: 0` to the return mapping for type consistency.

### 2F. Search API route -- no changes needed

**File**: `src/app/api/v1/skills/search/route.ts`

The route handler passes through `SearchResult[]` from the search functions directly to `NextResponse.json()`. Since `SearchResult` now includes `vskillInstalls`, it will appear in the JSON response automatically. No route-level changes required.

---

## Component 3: CLI Client (vskill)

### 3A. `SkillSearchResult` -- add `vskillInstalls`

**File**: `src/api/client.ts`

```
SkillSearchResult
──────────────────────────────────────
...existing fields...
+ vskillInstalls  number | undefined   <-- NEW
```

In `searchSkills()` response mapping, add:
```typescript
vskillInstalls: s.vskillInstalls != null ? Number(s.vskillInstalls) : undefined,
```

### 3B. Default limit change 50 -> 15

**File**: `src/api/client.ts`, `searchSkills()` function

```typescript
const limit = options?.limit ?? 15;  // was 50
```

**File**: `src/index.ts`, commander definition

Update the `--limit` option description:
```typescript
.option("--limit <n>", "Max results to return (default 15)", parseInt)
```

---

## Component 4: CLI Display Redesign (vskill)

### 4A. `formatInstalls()` utility

**File**: `src/utils/output.ts`

New export:
```typescript
export function formatInstalls(count: number): string {
  if (count >= 1_000_000) {
    const val = (count / 1_000_000).toFixed(1);
    return val.endsWith(".0") ? val.slice(0, -2) + "M" : val + "M";
  }
  if (count >= 1_000) {
    const val = (count / 1_000).toFixed(1);
    return val.endsWith(".0") ? val.slice(0, -2) + "K" : val + "K";
  }
  return String(count);
}
```

### 4B. `findCommand()` rewrite -- flat install-sorted output

**File**: `src/commands/find.ts`

**Sort order change**:
```
Old: non-blocked by score DESC, blocked last
New: non-blocked by vskillInstalls DESC (score as tiebreaker), blocked last
```

**TTY output** (replaces grouped marketplace table):

For each result, render two lines:
```
owner/repo@skill-name  1.2K installs
  https://github.com/owner/repo    (clickable OSC 8 link)
```

For blocked results:
```
owner/repo@skill-name  BLOCKED  critical | credential-theft
  https://github.com/owner/repo
```

**Non-TTY output** (piped/scripted):
Tab-separated flat lines, no ANSI, no table helper:
```
name\trepo\tinstalls
```

**Footer**:
- Count line: `15 results found`
- When `hasMore`: `Use --limit N for more`
- Blocked count warning (unchanged)

### 4C. Code to remove

- `extractBaseRepo()` function -- no longer needed (no marketplace grouping)
- `buildRow()` function -- replaced by inline rendering
- `formatRepo()` function -- simplified to just extract `owner/repo` slug
- Marketplace grouping logic (group-by-repo, `Plugin Marketplace:` headers, `table()` calls)
- `table()` import can be removed from find.ts (still used elsewhere)

### 4D. Display name format: `owner/repo@skill-name`

Derive from `repoUrl`:
```typescript
function formatSkillId(repoUrl: string | undefined, name: string): string {
  if (!repoUrl) return name;
  try {
    const slug = new URL(repoUrl).pathname
      .replace(/^\//, "")
      .replace(/\.git$/, "")
      .replace(/\/tree\/.*$/, "")
      .replace(/\/$/, "");
    return `${slug}@${name}`;
  } catch {
    return name;
  }
}
```

---

## Data Flow

```
Postgres Skill table (has vskillInstalls)
         |
         v
buildSearchIndex() ──> KV shards (SearchIndexEntry + vskillInstalls)
         |                        |
         |                        v
         |              searchSkillsEdge() ──> SearchResult + vskillInstalls
         |                                              |
         v                                              v
searchSkills() ──> SkillSearchRow ──> SearchResult     API route.ts
         |                                              |
         v                                              v
   Postgres fallback                           JSON response
                                                        |
                                                        v
                                              CLI searchSkills()
                                                        |
                                                        v
                                              SkillSearchResult + vskillInstalls
                                                        |
                                                        v
                                              findCommand() renders flat output
```

---

## Decision Record

### DR-1: Add field to KV shards vs. fetch installs separately

**Chosen**: Add `vskillInstalls` directly to `SearchIndexEntry` stored in KV shards.

**Alternative**: Keep shards unchanged, make a separate API call or DB lookup for install counts.

**Rationale**: The shard entries are already denormalized snapshots (include `githubStars`, `trustScore`, `npmDownloadsWeekly`). Adding one more integer is consistent with the pattern and avoids a second network hop. Shard size increase is negligible (~5 bytes per entry).

### DR-2: INDEX_VERSION bump vs. incremental backfill

**Chosen**: Bump `INDEX_VERSION` from 4 to 5, triggering full rebuild on next admin action.

**Alternative**: Write a migration script to backfill existing shards.

**Rationale**: Full rebuild is the established mechanism (used for every prior schema change). It is idempotent, triggered by a single admin API call, and guarantees consistency. Incremental backfill adds complexity for a one-time operation.

### DR-3: Sort by installs vs. blended score in CLI

**Chosen**: Sort by `vskillInstalls` DESC with relevance score as tiebreaker. The API still sorts by its blended rank (relevance 60% + popularity 40%) -- the CLI re-sorts the returned results.

**Alternative**: Change the API sort order to installs-first.

**Rationale**: The API serves both the web UI (which benefits from relevance-first ranking) and the CLI (which wants installs-first). Keeping the API sort unchanged avoids impacting the web UI. The CLI receives at most 15 results, so client-side re-sort is trivial.

### DR-4: Flat output vs. grouped marketplace tables

**Chosen**: Remove marketplace grouping entirely. Each result is a flat two-line entry.

**Rationale**: The grouped view was designed for browsing large result sets (50 results). With the new 15-result default and install-count sorting, users get focused results. Flat output is scannable in under 3 seconds (spec success metric). The `owner/repo@skill-name` format already conveys the marketplace relationship without explicit grouping.

---

## Test Strategy

### vskill-platform

1. **search.test.ts**: Update the "should NOT include excluded fields" assertion -- `vskillInstalls` is now an included field. Add assertion that `vskillInstalls` is present and is a number.

2. **search-index unit test**: Verify `buildSearchIndex()` includes `vskillInstalls` in shard entries.

3. **Edge search test**: Verify `searchSkillsEdge()` maps `vskillInstalls` from KV entries to `SearchResult`.

### vskill CLI

1. **find.test.ts**: Test `findCommand()` output format:
   - Results sorted by `vskillInstalls` DESC
   - `owner/repo@skill-name` format
   - Human-readable install counts (`1.2K`, `450`)
   - Blocked results show threat info instead of install count
   - `--json` includes `vskillInstalls` field
   - Default limit is 15
   - `Use --limit N for more` hint when `hasMore` is true

2. **output.test.ts**: Test `formatInstalls()`:
   - `0` -> `"0"`
   - `999` -> `"999"`
   - `1000` -> `"1K"`
   - `1200` -> `"1.2K"`
   - `1000000` -> `"1M"`
   - `3400000` -> `"3.4M"`

---

## Deployment Sequence

1. **Deploy vskill-platform first**: Types + API changes. The new `vskillInstalls` field defaults to `0`, so existing clients see no difference until they read it.
2. **Trigger admin index rebuild**: POST to admin rebuild endpoint. This rebuilds all KV shards with `vskillInstalls` included.
3. **Deploy vskill CLI**: New `find` command reads `vskillInstalls` from the API response. If the field is absent (old API response), it defaults to `undefined` / `0`.

Order matters: CLI must not deploy before the API returns `vskillInstalls`, or install counts will all show `0`.

---

## Files Changed Summary

### vskill-platform (5 files)

| File | Change |
|------|--------|
| `src/lib/search-index.ts` | Add `vskillInstalls` to `SearchIndexEntry`, bump `INDEX_VERSION` to 5, include field in `buildSearchIndex()` select + entry |
| `src/lib/search.ts` | Add `vskillInstalls` to `SearchResult`, `SkillSearchRow`; map in `searchSkillsEdge()`, add to SQL SELECTs in `searchSkills()`, add to `searchBlocklistEntries()` |
| `src/lib/queue/types.ts` | Add `vskillInstalls?: number` to `SearchShardQueueMessage.entry` |
| `src/lib/search.test.ts` | Update field presence assertions |
| `src/app/api/v1/skills/search/route.ts` | No changes needed |

### vskill CLI (4 files)

| File | Change |
|------|--------|
| `src/api/client.ts` | Add `vskillInstalls` to `SkillSearchResult`, map from API response, change default limit to 15 |
| `src/commands/find.ts` | Rewrite display: flat install-sorted output, remove marketplace grouping, add blocked threat display |
| `src/utils/output.ts` | Add `formatInstalls()` utility |
| `src/index.ts` | Update `--limit` option description to say "default 15" |
