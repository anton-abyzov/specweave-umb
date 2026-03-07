# Plan: Fix Skill Display Names After Hierarchical URL Migration

## Decision: Propagate slug fields through existing data types (no new abstractions)

The DB already has `ownerSlug`, `repoSlug`, `skillSlug` columns on the `Skill` table (from increment 0447). The fix is purely additive: thread these three fields through every intermediate type and adjust display logic to use `skillSlug` instead of `name`.

No new ADRs needed -- this is a data propagation bugfix within existing architecture.

## Data Flow (Current vs Fixed)

```
CURRENT (broken):
  DB.name = "dailydotdev/daily/news-digest"
  -> mapDbSkillToSkillData() -> SkillData.name = "dailydotdev/daily/news-digest"
  -> SearchPalette: label = "dailydotdev/dailydotdev/daily/news-digest"  (DUPLICATED)
  -> TrendingSkills: "dailydotdev/dailydotdev/daily/news-digest"          (DUPLICATED)
  -> CLI find: "dailydotdev/daily@dailydotdev/daily/news-digest"          (DUPLICATED)

FIXED:
  DB.ownerSlug = "dailydotdev", DB.repoSlug = "daily", DB.skillSlug = "news-digest"
  -> mapDbSkillToSkillData() -> SkillData.{ownerSlug, repoSlug, skillSlug}
  -> SearchPalette: label = "news-digest"  context = "dailydotdev/daily"
  -> TrendingSkills: "dailydotdev/" + "news-digest"
  -> CLI find: "dailydotdev/daily@news-digest"
```

## Changes by Layer

### Layer 1: Type Definitions (vskill-platform)

Add `ownerSlug`, `repoSlug`, `skillSlug` to four types:

| Type | File | Add |
|------|------|-----|
| `SkillData` | `src/lib/types.ts` | ownerSlug?, repoSlug?, skillSlug? |
| `SearchIndexEntry` | `src/lib/search-index.ts` | ownerSlug?, repoSlug?, skillSlug? |
| `SearchResult` | `src/lib/search.ts` | ownerSlug?, repoSlug?, skillSlug? |
| `TrendingSkillEntry` | `src/lib/stats-compute.ts` | ownerSlug?, repoSlug?, skillSlug? |

All three fields are optional (`string | undefined`) for backward compatibility with cached/stale data.

### Layer 2: Data Mappers (vskill-platform)

**`src/lib/data.ts` -- `mapDbSkillToSkillData()`**
- Read `s.ownerSlug`, `s.repoSlug`, `s.skillSlug` from the Prisma row and map into `SkillData`.

**`src/lib/search-index.ts` -- `buildSearchIndex()`**
- Add `ownerSlug`, `repoSlug`, `skillSlug` to the DB `select` clause.
- Include them in each `SearchIndexEntry` written to KV shards.
- Same for `updateSearchShard()` -- the `SearchIndexEntry` type update covers it automatically.

**`src/lib/search.ts` -- `searchSkillsEdge()` and `searchSkills()`**
- Edge path: copy slug fields from `SearchIndexEntry` into `SearchResult`.
- Postgres path: add `"ownerSlug"`, `"repoSlug"`, `"skillSlug"` to raw SQL SELECT. Update `SkillSearchRow` type.

**`src/lib/stats-compute.ts` -- trending skill queries**
- Add `ownerSlug`, `repoSlug`, `skillSlug` to the Prisma `select` in both `computeFullStats()` and `computeMinimalStats()` trending queries.

### Layer 3: Frontend Components (vskill-platform)

**`SearchPalette.tsx` (~line 344)**
- Current: `label: \`${r.author}/${r.name}\``
- Fixed: `label: r.skillSlug ?? r.name` as primary name, with `r.ownerSlug && r.repoSlug ? \`${r.ownerSlug}/${r.repoSlug}\` : r.author` as secondary context.

**`TrendingSkills.tsx` (~lines 48-49)**
- Current: `{skill.author}/` + `{skill.name}`
- Fixed: `{skill.ownerSlug ?? skill.author}/` faint prefix + `{skill.skillSlug ?? skill.name}` bold name.

**`skills/page.tsx` (~line 265)**
- Current: `<PublisherLink author={skill.author} skillName={skill.name} />`
- Fixed: `<PublisherLink author={skill.author} skillName={skill.skillSlug ?? skill.name} />`
- `PublisherLink.tsx` itself needs no changes -- it already renders `author / skillName` correctly.

### Layer 4: CLI (vskill)

**`src/api/client.ts` -- `SkillSearchResult` interface**
- Add optional fields: `ownerSlug?: string`, `repoSlug?: string`, `skillSlug?: string`.

**`src/commands/find.ts` -- `formatSkillId()`**
- Current: `extractBaseRepo(repoUrl)` + `@` + `skillName` -> duplicated because `skillName` is already `owner/repo/skillSlug`.
- Fixed: if `skillSlug` is present, return `ownerSlug/repoSlug@skillSlug`; else fall back to parsing `name` by splitting on `/` and using the last segment.

### Layer 5: Backfill + Index Rebuild

**Backfill NULL slugs**
- One-time script in `scripts/` subfolder that queries skills with NULL slugs and populates using `extractOwner()`, `extractRepoName()`, `deriveSkillSlug()` from `src/lib/slug.ts`.
- Run against production DB via `npx tsx scripts/backfill-slugs.ts`.

**Rebuild KV search index**
- After backfill + deploy, trigger full index rebuild so KV shards contain the slug fields.
- Existing `buildSearchIndex()` handles this via the cron endpoint.

## Risk Mitigation

1. **Backward compatibility**: All slug fields are optional on every type. Components fall back to `name` when slugs are absent. Partial deploys or old cached data still render correctly.

2. **KV shard size**: Adding 3 short string fields (~30 bytes) per entry increases shard size by ~3-5%. Negligible.

3. **Search relevance**: `computeRelevanceScore()` scores against `entry.name` (full hierarchical string). No change needed -- display is separate from ranking.

## Component Boundaries

```
vskill-platform (Next.js)
  src/lib/types.ts              -- SkillData type
  src/lib/search-index.ts       -- SearchIndexEntry type + buildSearchIndex()
  src/lib/search.ts             -- SearchResult type + search functions
  src/lib/stats-compute.ts      -- TrendingSkillEntry type + queries
  src/lib/data.ts               -- mapDbSkillToSkillData()
  src/app/components/SearchPalette.tsx       -- Fix label
  src/app/components/home/TrendingSkills.tsx -- Fix name display
  src/app/skills/page.tsx                    -- Fix PublisherLink prop

vskill (CLI)
  src/api/client.ts             -- SkillSearchResult type
  src/commands/find.ts           -- formatSkillId()
```

## Testing Strategy

- Unit tests for `formatSkillId()` with hierarchical names (CLI)
- Unit tests verifying `SearchIndexEntry` and `SearchResult` include slug fields
- Integration test: `mapDbSkillToSkillData()` maps slug fields from DB row
- Manual verification: SearchPalette, TrendingSkills, skills browse page display correct labels after deploy

## No Domain Skill Chaining Needed

This is a data propagation bugfix across existing layers. No new infrastructure, no new services, no architectural changes. Standard TypeScript + SQL changes in the existing codebase.
