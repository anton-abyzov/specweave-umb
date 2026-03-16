# Implementation Plan: npm Weekly Download Stats Integration

## Overview

Additive feature that threads a single new field (`npmDownloadsWeekly`) through five existing layers of the vskill-platform: Prisma schema, enrichment pipeline, data layer, skill detail UI, and edge search index. No new services, no new APIs, no new cron jobs. Every change extends an existing code path.

## Architecture

### Change Propagation Map

```
                    ┌──────────────────────┐
                    │  Prisma Schema       │
                    │  + npmDownloadsWeekly │
                    │  (Skill, Snapshot)    │
                    └─────────┬────────────┘
                              │ migration
                              ▼
  ┌───────────────────────────────────────────────────┐
  │            Enrichment Pipeline (cron)              │
  │                                                    │
  │  fetchNpmDownloadsBulk("last-month")  ← existing  │
  │  fetchNpmDownloadsBulk("last-week")   ← NEW       │
  │                                                    │
  │  DB transaction: update Skill + MetricsSnapshot    │
  └───────────────────────┬───────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
  ┌─────────────────────┐  ┌──────────────────────┐
  │  Data Layer          │  │  Search Index         │
  │  data.ts → SkillData │  │  SearchIndexEntry     │
  │  + npmDownloadsWeekly│  │  + npmDownloadsWeekly │
  └─────────┬───────────┘  │  INDEX_VERSION 3 → 4  │
            │               │  Sort: trust, stars,  │
            ▼               │        weekly_dl      │
  ┌─────────────────────┐  └──────────┬───────────┘
  │  Skill Detail Page   │             │
  │  StatCard "Weekly"   │             ▼
  │  StatCard "Monthly"  │  ┌──────────────────────┐
  │  (relabel "NPM")     │  │  Edge Search (KV)     │
  └─────────────────────┘  │  3-field sort          │
                            │  Postgres fallback     │
                            └──────────────────────┘
```

### Components Modified

| Component | File | Change |
|-----------|------|--------|
| Prisma Schema | `prisma/schema.prisma` | Add `npmDownloadsWeekly Int @default(0)` to `Skill` and `MetricsSnapshot` |
| Types | `src/lib/types.ts` | Add `npmDownloadsWeekly: number` to `SkillData` |
| Popularity Fetcher | `src/lib/popularity-fetcher.ts` | Add `period` parameter to `fetchNpmDownloadsBulk` |
| Enrichment Cron | `src/lib/cron/enrichment.ts` | Second bulk fetch for `last-week`, write to `npmDownloadsWeekly` |
| Data Layer | `src/lib/data.ts` | Map `npmDownloadsWeekly` in skill-to-SkillData transform |
| Skill Detail Page | `src/app/skills/[name]/page.tsx` | Add "Weekly" StatCard, relabel "NPM" to "Monthly" |
| Search Index Types | `src/lib/search-index.ts` | Add `npmDownloadsWeekly` to `SearchIndexEntry`, bump `INDEX_VERSION` to 4 |
| Search Index Build | `src/lib/search-index.ts` | Select new field, populate shard entries, 3-field sort |
| Edge Search | `src/lib/search.ts` | 3-field sort in `searchSkillsEdge`, add field to `SearchResult` |
| Queue Types | `src/lib/queue/types.ts` | Add `npmDownloadsWeekly` to `SearchShardQueueMessage.entry` |
| Publish Path | `src/lib/submission-store.ts` | Include `npmDownloadsWeekly: 0` in queue message |

### Components NOT Modified

| Component | File | Reason |
|-----------|------|--------|
| Trending Formula | `src/lib/trending-formula.ts` | Per spec FR-003: uses monthly `npmDownloads` only |
| Delta Trending | `src/lib/cron/trending-score.ts` | Uses monthly `npmDownloads` in `MetricValues`; weekly is display/rank only |
| Trust Score | `src/lib/trust/trust-score.ts` | No npm signal in trust computation |
| Process Submission | `src/lib/queue/process-submission.ts` | npm package extraction already works; weekly fetch is in enrichment |

### Data Model Changes

```
Skill table (existing → modified)
┌──────────────────────┬──────────┬───────────┬─────────────┐
│ Column               │ Type     │ Default   │ Status      │
├──────────────────────┼──────────┼───────────┼─────────────┤
│ npmDownloads         │ Int      │ 0         │ UNCHANGED   │
│ npmPackage           │ String?  │ null      │ UNCHANGED   │
│ npmPackageVerified   │ Boolean  │ false     │ UNCHANGED   │
│ npmDownloadsWeekly   │ Int      │ 0         │ NEW         │
└──────────────────────┴──────────┴───────────┴─────────────┘

MetricsSnapshot table (existing → modified)
┌──────────────────────┬──────────┬───────────┬─────────────┐
│ Column               │ Type     │ Default   │ Status      │
├──────────────────────┼──────────┼───────────┼─────────────┤
│ npmDownloads         │ Int      │ 0         │ UNCHANGED   │
│ npmDownloadsWeekly   │ Int      │ 0         │ NEW         │
└──────────────────────┴──────────┴───────────┴─────────────┘
```

## Architecture Decisions

### ADR-0244: Additive Weekly Downloads Field (not replacing monthly)

**Context**: The existing `npmDownloads` field stores monthly download counts. The user requested weekly download metrics.

**Decision**: Add `npmDownloadsWeekly` as a separate field alongside `npmDownloads`.

**Rationale**:
- The trending formula (`trending-formula.ts`) and delta-based trending computation (`trending-score.ts`) depend on monthly `npmDownloads`. Changing its semantics mid-stream invalidates all existing `MetricsSnapshot` rows and would cause incorrect trending deltas for 30+ days until the snapshot window rolls over.
- Monthly and weekly serve different purposes: monthly for trending momentum calculation, weekly for real-time display and search ranking signals.
- The npm bulk API endpoint accepts a period parameter, making dual fetching trivial.

**Alternatives rejected**:
- Replace `npmDownloads` semantics with weekly: breaks trending scores, requires snapshot backfill.
- Compute weekly from monthly via ratio: inaccurate, npm provides direct weekly endpoint.

### ADR-0245: Third Tiebreaker Sort (not composite score)

**Context**: Edge search sorts by `trustScore DESC, githubStars DESC`. Adding npm weekly downloads as a ranking signal.

**Decision**: Add `npmDownloadsWeekly` as a third tiebreaker field in the sort comparator, not a blended composite score.

**Rationale**:
- Tiebreaker is transparent and debuggable. Given two skills with equal trust and stars, the one with more weekly downloads ranks higher.
- A composite score (weighted blend of trust + stars + downloads) requires tuning weights, testing distribution, and explaining to users why rankings shifted.
- The tiebreaker approach is backward-compatible: existing rankings only change when two skills were previously tied on both trust and stars.

**Trade-off**: A composite score would provide finer granularity. But the tiebreaker approach has near-zero risk of unwanted ranking regressions.

### ADR-0246: Sequential npm API Calls (not parallel)

**Context**: Enrichment now makes two bulk npm API calls per cycle (`last-month` + `last-week`).

**Decision**: Run the two calls sequentially, not in parallel.

**Rationale**:
- npm's bulk API has undocumented rate limits. Parallel calls from the same IP double the burst rate.
- Each batch processes up to 128 packages in one HTTP request. Sequential execution adds ~1-2 seconds total (one extra HTTP call per batch), negligible within the hourly cron window.
- The enrichment loop already has rate-limit backoff infrastructure. Sequential calls let the backoff state apply correctly between both call types.

## Implementation Phases

### Phase 1: Schema + Types (US-001)
1. Add `npmDownloadsWeekly` to Prisma `Skill` and `MetricsSnapshot` models
2. Run `npx prisma migrate dev` to generate migration
3. Add `npmDownloadsWeekly` to `SkillData` type
4. Update data layer mapping in `data.ts`

### Phase 2: Enrichment Pipeline (US-002)
1. Add `period` parameter to `fetchNpmDownloadsBulk` in `popularity-fetcher.ts`
2. Add second bulk call in `enrichment.ts` for `last-week`
3. Write `npmDownloadsWeekly` in DB transaction alongside other metrics
4. Include weekly in `MetricsSnapshot` row

### Phase 3: UI Display (US-003)
1. Add "Weekly" StatCard to skill detail page
2. Relabel existing "NPM" StatCard to "Monthly"

### Phase 4: Search Index (US-004)
1. Add `npmDownloadsWeekly` to `SearchIndexEntry` and `SearchShardQueueMessage`
2. Update `buildSearchIndex` to select and populate the field
3. Update all sort comparators to 3-field order
4. Bump `INDEX_VERSION` to 4
5. Update `SearchResult` type and Postgres fallback ORDER BY
6. Include field in publish path queue message (`submission-store.ts`)

## Testing Strategy

### Unit Tests
- `popularity-fetcher.test.ts`: Test `fetchNpmDownloadsBulk` with `period: "last-week"` parameter
- `enrichment.test.ts`: Verify two sequential bulk calls, weekly value written to DB, null-preserves
- `search-index.test.ts`: Verify 3-field sort in shard build and upsert
- `search.test.ts`: Verify edge sort includes `npmDownloadsWeekly` as tiebreaker

### Integration Verification
- Prisma migration applies cleanly with no data loss
- `INDEX_VERSION` bump triggers full rebuild (verify meta version check)

### Regression Tests
- Trending formula produces identical scores before/after (no `npmDownloadsWeekly` in formula)
- Search results for skills with `npmDownloadsWeekly = 0` sort identically to current behavior

## Technical Challenges

### Challenge 1: KV Shard Size Growth
**Impact**: Each `SearchIndexEntry` grows by ~20 bytes (one integer field). For 10,000 skills, total growth is ~200KB across all shards.
**Mitigation**: Well within Cloudflare KV's 25MB per-key limit. No action needed.

### Challenge 2: npm API Rate Limits on Dual Fetch
**Impact**: Two bulk calls per enrichment cycle instead of one.
**Mitigation**: Sequential execution, shared rate-limit backoff state, 128-package batching. The npm bulk API handles 128 packages in one HTTP call, so the overhead is exactly one additional HTTP request per batch of 128 packages.

### Challenge 3: Zero-Value Sort Behavior
**Impact**: All skills start with `npmDownloadsWeekly = 0` until enriched. The third tiebreaker field is ineffective until populated.
**Mitigation**: Acceptable cold-start behavior. After one enrichment cycle (~50 skills/hour), the field populates progressively. Skills without npm packages remain at 0, which is correct behavior (they genuinely have zero npm downloads).
