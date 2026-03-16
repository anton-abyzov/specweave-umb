# Implementation Plan: Track Tier 2 LLM Model in Scan Results

## Overview

Plumb the `model` field that `tier2-scan.js` already returns through `finalize-scan` into the Prisma `ScanResult` table, backfill historical rows with a duration-based heuristic, and expose a new admin stats endpoint for cost analysis.

Three vertical slices, each independently deployable:

1. **Schema + pipeline** -- Add `llmModel` column, thread value from payload to DB.
2. **Backfill** -- Single SQL migration for ~769K rows using duration thresholds.
3. **Stats endpoint** -- `GET /api/v1/admin/scan-model-stats` with date range and granularity.

## Architecture

### Data Flow (current vs. proposed)

```
                         CURRENT
  ┌─────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ VM Scanner   │─────►│ finalize-scan    │─────►│ submission-store  │
  │ tier2-scan.js│      │ route.ts         │      │ persistScanResult │
  │              │      │                  │      │ ToDb()            │
  │ returns:     │      │ Tier2Payload has │      │                  │
  │  ...model    │      │ NO model field   │      │ No llmModel col  │
  └─────────────┘      │ => model DROPPED │      └──────────────────┘
                        └──────────────────┘

                         PROPOSED
  ┌─────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ VM Scanner   │─────►│ finalize-scan    │─────►│ submission-store  │
  │ tier2-scan.js│      │ route.ts         │      │ persistScanResult │
  │              │      │                  │      │ ToDb()            │
  │ returns:     │      │ Tier2Payload +   │      │                  │
  │  ...model ──────────►  model?: string  │      │ writes llmModel  │
  └─────────────┘      │ passes to store  │      │ to ScanResult    │
                        └──────────────────┘      └──────────────────┘
```

### Data Model Change

```
ScanResult (existing table, ~769K rows)
───────────────────────────────────────────────────
Column          Type          Change
───────────────────────────────────────────────────
id              UUID PK       (no change)
submissionId    UUID FK?      (no change)
tier            Int           (no change)
verdict         ScanVerdict   (no change)
score           Int?          (no change)
durationMs      Int           (no change)
llmModel        String?       NEW — nullable
...other cols                 (no change)
───────────────────────────────────────────────────

New Index:
  @@index([tier, llmModel, createdAt])
  Purpose: Stats queries GROUP BY llmModel filtered on tier=2 and date range
```

**Why nullable**: Tier 1 and Tier 3 results have no LLM involvement (null is semantically "no LLM used"). Pre-backfill Tier 2 rows start null, then get backfilled with `(inferred)` suffix values.

### Components Modified

| Component | File | Change |
|-----------|------|--------|
| Prisma schema | `prisma/schema.prisma` | Add `llmModel String?` + composite index |
| Tier2Payload interface | `finalize-scan/route.ts` | Add `model?: string` |
| FinalizeScanBody interface | `finalize-scan/route.ts` | No change (tier2 is nested) |
| Route destructuring | `finalize-scan/route.ts` | Extract `tier2.model`, pass as `llmModel` |
| StoredScanResult | `submission-store.ts` | Add `llmModel?: string` |
| persistScanResultToDb | `submission-store.ts` | Write `llmModel` to `db.scanResult.create()` |
| ScanResultData | `types.ts` | Add `llmModel?: string \| null` |
| buildScanResultFromDbRows | `submission-store.ts` | Read `llmModel` from DB row |
| **NEW** Stats route | `admin/scan-model-stats/route.ts` | Query + aggregate |

### API Contract: Stats Endpoint

```
GET /api/v1/admin/scan-model-stats?from=2026-01-01&to=2026-03-12&granularity=day

Headers:
  Authorization: Bearer <admin-jwt>

Response 200:
{
  "from": "2026-01-01",
  "to": "2026-03-12",
  "granularity": "day",
  "totalScans": 42301,
  "buckets": [
    {
      "period": "2026-03-11",
      "models": [
        {
          "model": "@cf/meta/llama-4-scout-17b-16e-instruct",
          "count": 312,
          "estimatedCost": 0
        },
        {
          "model": "gpt-4o-mini",
          "count": 18,
          "estimatedCost": 0.054
        },
        {
          "model": "gpt-4o-mini (inferred)",
          "count": 1200,
          "estimatedCost": 3.60
        },
        {
          "model": "cloudflare (inferred)",
          "count": 8500,
          "estimatedCost": 0
        },
        {
          "model": null,
          "count": 45,
          "estimatedCost": 0
        }
      ]
    }
  ],
  "summary": {
    "byModel": {
      "gpt-4o-mini": { "count": 18, "estimatedCost": 0.054 },
      "gpt-4o-mini (inferred)": { "count": 1200, "estimatedCost": 3.60 }
    },
    "totalEstimatedCost": 3.654
  }
}

Response 400 (missing params):
{ "error": "Missing required query params: from, to" }

Response 401 (no auth):
{ "error": "Authentication required" }
```

**Cost estimation logic**: Only models containing `gpt-4o-mini` incur cost. Estimated at $0.003 per scan (rough average of ~600 input + 300 output tokens at gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output). This is a constant per-scan estimate since we do not track token counts (out of scope per spec).

## Technology Stack

No new dependencies. Uses existing:
- **Prisma** -- schema migration + raw SQL backfill
- **Next.js App Router** -- admin route handler
- **`@/lib/auth`** -- `requireAdmin` + `isAuthError` (existing pattern)
- **`@/lib/api-helpers`** -- `jsonResponse`, `errorResponse` (existing pattern)
- **Neon Postgres** -- raw SQL for backfill + grouping queries

## Architecture Decisions

### AD-1: Single migration with schema + backfill

**Decision**: Combine the `llmModel` column addition, composite index creation, and backfill SQL into one Prisma migration.

**Rationale**: The backfill is a one-time operation that should run exactly once. Prisma migration history tracks this. A separate script would require manual invocation and tracking.

**Trade-off**: Migration will take longer (~30-60s for 769K row UPDATE), but this is acceptable for a one-time operation. Neon Postgres handles UPDATE statements efficiently -- no row-level locking concerns since we're only touching rows where `llmModel IS NULL AND tier = 2`.

### AD-2: Raw SQL UPDATE for backfill (not Prisma ORM)

**Decision**: Use raw SQL in the migration file rather than a seed script or Prisma `updateMany`.

**Rationale**: Three UPDATE statements with WHERE clauses process all 769K rows in-place without loading them into application memory. Prisma `updateMany` would work but raw SQL in migration is more explicit and runs at migration time, not application startup.

```sql
-- Backfill: >30s = OpenAI
UPDATE "ScanResult"
SET "llmModel" = 'gpt-4o-mini (inferred)'
WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" > 30000;

-- Backfill: 20-30s = ambiguous
UPDATE "ScanResult"
SET "llmModel" = 'unknown (ambiguous)'
WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" >= 20000 AND "durationMs" <= 30000;

-- Backfill: <20s = Cloudflare
UPDATE "ScanResult"
SET "llmModel" = 'cloudflare (inferred)'
WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" < 20000;
```

### AD-3: Composite index `(tier, llmModel, createdAt)`

**Decision**: Create a composite index covering the stats query pattern.

**Rationale**: The stats endpoint filters on `tier = 2`, groups by `llmModel`, and filters by `createdAt` range. The composite index covers all three operations, enabling index-only scans for the grouping query. Without it, the query would require a full table scan of 769K+ rows.

### AD-4: Constant per-scan cost estimate

**Decision**: Use a fixed $0.003/scan estimate for gpt-4o-mini rather than tracking actual token counts.

**Rationale**: Token tracking is explicitly out of scope (spec). The per-scan cost is a rough but useful approximation: typical Tier 2 prompts are ~600 input tokens ($0.15/1M = $0.00009) + ~300 output tokens ($0.60/1M = $0.00018) = ~$0.00027 per scan. Rounding up to $0.003 accounts for longer prompts and provides a conservative upper bound. This constant lives in the stats route as a named constant (`OPENAI_COST_PER_SCAN`), easily updated if pricing changes.

### AD-5: `llmModel` not `model` as column/field name

**Decision**: Use `llmModel` throughout the TypeScript/Prisma layer, even though the crawl worker returns `model`.

**Rationale**: `model` is too generic and collides with Prisma's `model` keyword in schema definitions. `llmModel` is self-documenting and follows the existing naming pattern of tier2-specific fields (`tier2Score`, `tier2Verdict`, `intentAnalysis`).

## Implementation Phases

### Phase 1: Schema + Pipeline (US-001)

1. Add `llmModel String?` to `ScanResult` in `prisma/schema.prisma`
2. Add `@@index([tier, llmModel, createdAt])` composite index
3. Generate Prisma migration (creates column + index)
4. Add `model?: string` to `Tier2Payload` interface in `finalize-scan/route.ts`
5. Add `llmModel?: string` to `StoredScanResult` interface in `submission-store.ts`
6. Add `llmModel?: string | null` to `ScanResultData` interface in `types.ts`
7. Thread value: `finalize-scan` extracts `tier2.model` and passes it as `llmModel` in both `storeScanResult` calls (T2 present path)
8. `persistScanResultToDb` writes `llmModel` to DB
9. `buildScanResultFromDbRows` reads `llmModel` from DB rows

### Phase 2: Backfill (US-002)

1. Add raw SQL backfill statements to the same migration file created in Phase 1
2. Three UPDATE statements using duration thresholds (>30s, 20-30s, <20s)
3. WHERE clause includes `llmModel IS NULL` for idempotency
4. WHERE clause includes `tier = 2` to avoid touching Tier 1/3 rows

### Phase 3: Stats Endpoint (US-003)

1. Create `src/app/api/v1/admin/scan-model-stats/route.ts`
2. Use `requireAdmin` for auth (follows existing admin route pattern)
3. Parse `from`, `to`, `granularity` from query params
4. Use Prisma `groupBy` or raw SQL for aggregation
5. Calculate `estimatedCost` per model group using `OPENAI_COST_PER_SCAN` constant
6. Return bucketed response with summary totals

## Testing Strategy

- **Unit tests**: Stats endpoint query param validation, cost calculation logic
- **Integration tests**: Prisma writes with `llmModel`, stats query against seeded data
- **Migration test**: Verify backfill SQL on test database with sample data
- BDD test plans specified per-task in tasks.md

## Technical Challenges

### Challenge 1: Backfill migration on 769K rows

**Solution**: Raw SQL UPDATE with WHERE clause processes rows in-place (no application memory). The `tier` column already has an index (`@@index([tier])`), so the WHERE filter is efficient. Adding `AND "llmModel" IS NULL` makes the migration idempotent.

**Risk**: Migration could time out if Neon Postgres has strict statement timeout. Mitigation: Neon's default statement timeout is 60s for migration connections, which is sufficient for three indexed UPDATE statements.

### Challenge 2: Index creation on large table

**Solution**: Postgres creates B-tree indexes without exclusive lock on the table for most operations. The composite index on `(tier, llmModel, createdAt)` is created in the same migration. If blocking becomes an issue, the index can be created with `CREATE INDEX CONCURRENTLY` in a separate migration step.

**Risk**: Low. Standard `CREATE INDEX` on 769K rows takes seconds, not minutes.

### Challenge 3: Stats query performance on growing table

**Solution**: The composite index `(tier, llmModel, createdAt)` covers the exact query pattern: `WHERE tier = 2 AND createdAt BETWEEN $from AND $to GROUP BY llmModel`. This enables an index-only scan with no table heap access for the grouping columns.

**Risk**: None for current scale. At 10M+ rows the query would still perform well with the covering index.
