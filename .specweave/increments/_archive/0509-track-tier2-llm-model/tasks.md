---
increment: 0509-track-tier2-llm-model
by_user_story:
  US-001:
    tasks: [T-001, T-002]
    acs: [AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05]
  US-002:
    tasks: [T-003]
    acs: [AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04]
  US-003:
    tasks: [T-004, T-005, T-006]
    acs: [AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05]
---

# Tasks: Track Tier 2 LLM Model in Scan Results

## Task Notation

- `[ ]` not started | `[x]` completed
- `[P]` parallelizable with sibling tasks
- Model hints: haiku (simple), sonnet (default), opus (complex/architectural)

---

## User Story: US-001 - Persist LLM Model in Scan Results

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 2 completed

---

### T-001: Prisma Schema Migration — Add llmModel Column and Composite Index

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** the `ScanResult` Prisma model does not have an `llmModel` column
- **When** the migration is applied to a test database
- **Then** the `ScanResult` table has a nullable `llmModel TEXT` column and the composite index `(tier, llmModel, createdAt)` exists

**Test Cases**:
1. **Unit** (schema snapshot): `prisma/schema.prisma`
   - Verify `llmModel String?` field present in `ScanResult` model
   - Verify `@@index([tier, llmModel, createdAt])` declaration present
   - **Coverage Target**: 100% schema declaration coverage (structural, not runtime)

2. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/finalize-scan/__tests__/route.test.ts`
   - `persistsLlmModelWhenProvided()`: Tier 2 payload with `model` field → DB row has non-null `llmModel`
   - `storesNullLlmModelWhenAbsent()`: Tier 2 payload without `model` field → DB row has null `llmModel`
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` — add `llmModel String?` to `ScanResult` model after `durationMs`
2. Add `@@index([tier, llmModel, createdAt])` to `ScanResult` model indexes
3. Run `npx prisma migrate dev --name add_llm_model_to_scan_result` from the vskill-platform directory
4. Verify the generated migration SQL contains `ALTER TABLE "ScanResult" ADD COLUMN "llmModel" TEXT;` and `CREATE INDEX` statement

**Dependencies**: None

---

### T-002: Thread llmModel Through Pipeline — Interfaces and Persistence

**User Story**: US-001
**Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** a Tier 2 finalize-scan payload containing `model: "@cf/meta/llama-4-scout-17b-16e-instruct"`
- **When** `POST /api/v1/internal/finalize-scan` is called
- **Then** the resulting `ScanResult` row in the database has `llmModel = "@cf/meta/llama-4-scout-17b-16e-instruct"`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
   - `persistScanResultToDb_writesLlmModel()`: Call `persistScanResultToDb` with `llmModel: "gpt-4o-mini"` → Prisma create called with `llmModel: "gpt-4o-mini"`
   - `persistScanResultToDb_omitsLlmModelWhenNull()`: Call with `llmModel: undefined` → Prisma create called with `llmModel: undefined`
   - **Coverage Target**: 95%

2. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/finalize-scan/__tests__/route.test.ts`
   - `route_extractsModelFromTier2Payload()`: POST with `tier2.model` present → `storeScanResult` receives `llmModel`
   - `route_handlesAbsentModelField()`: POST without `tier2.model` → `llmModel` is undefined, no error
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/finalize-scan/route.ts`:
   - Add `model?: string` to `Tier2Payload` interface
   - Destructure `model` from `tier2` in the handler body
   - Pass `llmModel: model` to both `storeScanResult` calls in the T2-present code path
2. Edit `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`:
   - Add `llmModel?: string` to `StoredScanResult` interface
   - Add `llmModel?: string | null` to `ScanResultData` interface (or confirm location in `types.ts`)
   - Add `llmModel` to the `db.scanResult.create({ data: { ... } })` call in `persistScanResultToDb`
   - Add `llmModel: row.llmModel` to `buildScanResultFromDbRows` (or equivalent mapper)
3. If `ScanResultData` lives in `src/lib/types.ts`, edit that file instead for the interface addition
4. Run `npx vitest run` — all existing tests must still pass

**Dependencies**: T-001 (migration must exist before Prisma client regenerates)

---

## User Story: US-002 - Heuristic Backfill of Historical Scan Data

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 1 total, 1 completed

---

### T-003: Add Backfill SQL to Migration — Duration-Based llmModel Attribution

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** existing `ScanResult` rows with `tier = 2` and various `durationMs` values (`35000`, `25000`, `10000`) and `llmModel IS NULL`
- **When** the backfill SQL executes
- **Then** rows with `durationMs > 30000` get `"gpt-4o-mini (inferred)"`, rows with `20000 <= durationMs <= 30000` get `"unknown (ambiguous)"`, rows with `durationMs < 20000` get `"cloudflare (inferred)"`, and Tier 1/3 rows remain untouched

**Test Cases**:
1. **Unit** (SQL logic validation): `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/backfill-heuristic.test.ts`
   - `backfillLabel_above30s()`: `durationMs = 35000` → label `"gpt-4o-mini (inferred)"`
   - `backfillLabel_at30s()`: `durationMs = 30000` → label `"unknown (ambiguous)"` (boundary inclusive)
   - `backfillLabel_at20s()`: `durationMs = 20000` → label `"unknown (ambiguous)"` (boundary inclusive)
   - `backfillLabel_below20s()`: `durationMs = 19999` → label `"cloudflare (inferred)"`
   - `backfillLabel_tier1Untouched()`: `tier = 1`, `durationMs = 40000` → no label assigned
   - **Coverage Target**: 95%

2. **Integration** (migration file content): Read the generated migration `.sql` file and assert:
   - Contains `UPDATE "ScanResult" SET "llmModel" = 'gpt-4o-mini (inferred)' WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" > 30000`
   - Contains `WHERE ... "durationMs" >= 20000 AND "durationMs" <= 30000` for the ambiguous range
   - Contains idempotency guard `"llmModel" IS NULL` in all three UPDATE statements
   - **Coverage Target**: 100% of AC threshold combinations

**Implementation**:
1. Open the migration `.sql` file generated by T-001 (in `prisma/migrations/<timestamp>_add_llm_model_to_scan_result/migration.sql`)
2. Append the three raw SQL UPDATE statements after the `CREATE INDEX` statement:
   ```sql
   -- Backfill: >30s = OpenAI (inferred)
   UPDATE "ScanResult"
   SET "llmModel" = 'gpt-4o-mini (inferred)'
   WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" > 30000;

   -- Backfill: 20-30s inclusive = ambiguous
   UPDATE "ScanResult"
   SET "llmModel" = 'unknown (ambiguous)'
   WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" >= 20000 AND "durationMs" <= 30000;

   -- Backfill: <20s = Cloudflare (inferred)
   UPDATE "ScanResult"
   SET "llmModel" = 'cloudflare (inferred)'
   WHERE tier = 2 AND "llmModel" IS NULL AND "durationMs" < 20000;
   ```
3. Write the unit test helper function `inferLlmModel(durationMs: number, tier: number): string | null` that mirrors the SQL logic (used for unit testing boundary values without hitting a DB)
4. Run `npx vitest run` to validate the heuristic logic unit tests pass

**Dependencies**: T-001 (migration file must exist to append SQL)

---

## User Story: US-003 - Admin Stats Endpoint for LLM Model Usage

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 3 total, 3 completed

---

### T-004: Create Stats Route — Auth, Param Validation, and Query

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** the route `GET /api/v1/admin/scan-model-stats`
- **When** called without an Authorization header
- **Then** a 401 response is returned; and when called with valid admin JWT and `from`/`to` params, a 200 with `buckets` array and `totalScans` is returned

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/scan-model-stats/__tests__/route.test.ts`
   - `GET_returns401_whenUnauthenticated()`: No auth header → 401 `{ error: "Authentication required" }`
   - `GET_returns400_whenFromMissing()`: Auth present, `to` only → 400 `{ error: "Missing required query params: from, to" }`
   - `GET_returns400_whenToMissing()`: Auth present, `from` only → 400 with descriptive error
   - `GET_returns200_withValidParams()`: Auth + `from=2026-01-01&to=2026-03-12` → 200 with `{ from, to, granularity, totalScans, buckets, summary }`
   - `GET_returnsEmptyBuckets_whenNoData()`: Auth + valid date range with no matching rows → `{ totalScans: 0, buckets: [] }`
   - **Coverage Target**: 90%

**Implementation**:
1. Create directory `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/scan-model-stats/`
2. Create `route.ts` with `export async function GET(request: NextRequest)`:
   - Call `requireAdmin(request)` — return 401 on auth error (use `isAuthError` pattern from existing admin routes)
   - Parse `from`, `to`, `granularity` from `request.nextUrl.searchParams`
   - Return 400 if `from` or `to` missing
   - Default `granularity` to `"day"` if absent; validate it is `"day"` or `"month"`
   - Execute raw SQL or Prisma `groupBy` query filtering `tier = 2` and `createdAt` in range
   - Return 200 with structured response
3. Create `__tests__/route.test.ts` with mocked `requireAdmin`, `prisma`, and `isAuthError`
4. Run `npx vitest run src/app/api/v1/admin/scan-model-stats`

**Dependencies**: T-001, T-002 (llmModel column must exist in Prisma client types)

---

### T-005: Implement Granularity Grouping — Day and Month Bucketing

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** scan result rows spread across multiple days in March 2026
- **When** `GET /api/v1/admin/scan-model-stats?from=2026-03-01&to=2026-03-12&granularity=day` is called
- **Then** `buckets` contains one entry per calendar day with `period: "2026-03-01"` format; and when `granularity=month`, buckets use `period: "2026-03"` format

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/scan-model-stats/__tests__/route.test.ts`
   - `bucketsGroupedByDay_whenGranularityIsDay()`: Seeded rows on 3 different days → 3 buckets with `period: "YYYY-MM-DD"`
   - `bucketsGroupedByMonth_whenGranularityIsMonth()`: Rows spanning 2 months → 2 buckets with `period: "YYYY-MM"`
   - `defaultsToDay_whenGranularityAbsent()`: No `granularity` param → `"granularity": "day"` in response
   - `returns400_whenGranularityInvalid()`: `granularity=hour` → 400 `{ error: "granularity must be 'day' or 'month'" }`
   - **Coverage Target**: 90%

**Implementation**:
1. In `route.ts`, implement the grouping logic using raw SQL with `DATE_TRUNC`:
   - `granularity = "day"` → `DATE_TRUNC('day', "createdAt")` in GROUP BY
   - `granularity = "month"` → `DATE_TRUNC('month', "createdAt")` in GROUP BY
2. Format the period string: day → `YYYY-MM-DD`, month → `YYYY-MM` (use `toISOString().slice(0, N)`)
3. Structure each bucket as `{ period: string, models: Array<{ model: string | null, count: number, estimatedCost: number }> }`
4. Assemble the `buckets` array from the grouped query results
5. Run `npx vitest run src/app/api/v1/admin/scan-model-stats`

**Dependencies**: T-004

---

### T-006: Implement Cost Estimation and Summary Totals

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed
**Model hint**: haiku

**Test Plan**:
- **Given** scan results with `llmModel = "gpt-4o-mini"` (count: 10) and `llmModel = "gpt-4o-mini (inferred)"` (count: 100) and `llmModel = "@cf/meta/llama-4-scout-17b-16e-instruct"` (count: 50)
- **When** the stats endpoint computes `estimatedCost`
- **Then** OpenAI models get `count * OPENAI_COST_PER_SCAN` (0.003), Cloudflare models get `0`, and the `summary.totalEstimatedCost` equals the sum of all model costs

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/scan-model-stats/__tests__/route.test.ts`
   - `computesCost_forGptMiniModel()`: model `"gpt-4o-mini"`, count 10 → `estimatedCost: 0.03`
   - `computesCost_forGptMiniInferred()`: model `"gpt-4o-mini (inferred)"`, count 100 → `estimatedCost: 0.30`
   - `zeroCost_forCloudflareModel()`: model `"@cf/meta/llama-4-scout-17b-16e-instruct"`, count 50 → `estimatedCost: 0`
   - `zeroCost_forNullModel()`: model `null`, count 5 → `estimatedCost: 0`
   - `summaryTotals_aggregateCorrectly()`: mixed models → `summary.totalEstimatedCost` = sum of all non-zero costs, `summary.byModel` keyed by model name
   - **Coverage Target**: 95%

**Implementation**:
1. Define constant in `route.ts`: `const OPENAI_COST_PER_SCAN = 0.003;`
2. Implement `isOpenAiModel(model: string | null): boolean` — returns true when model contains `"gpt-4o-mini"`
3. In the response assembly, compute `estimatedCost = isOpenAiModel(model) ? count * OPENAI_COST_PER_SCAN : 0` for each model group
4. Build `summary.byModel` by aggregating across all buckets for models with non-zero costs
5. Compute `summary.totalEstimatedCost` as sum of all `estimatedCost` values
6. Run `npx vitest run src/app/api/v1/admin/scan-model-stats`
7. Run full test suite: `npx vitest run` — all tests must pass

**Dependencies**: T-005
