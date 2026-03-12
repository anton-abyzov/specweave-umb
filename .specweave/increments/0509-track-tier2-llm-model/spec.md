---
increment: 0509-track-tier2-llm-model
title: Track Tier 2 LLM Model in Scan Results
status: completed
priority: P1
type: feature
created: 2026-03-12T00:00:00.000Z
---

# Track Tier 2 LLM Model in Scan Results

## Problem Statement

The vskill-platform Tier 2 security scanner uses a 3-tier LLM fallback chain: Cloudflare Llama 4 Scout, Cloudflare Llama 3.3 70B, and OpenAI gpt-4o-mini. The VM scanner (`tier2-scan.js`) already returns a `model` field identifying which LLM handled each scan, but this field is dropped at the `Tier2Payload` interface in `finalize-scan/route.ts` and never persisted to the database. As a result, there is no way to determine which scans incurred OpenAI API costs versus running free on Cloudflare Workers AI.

## Goals

- Persist the LLM model identifier for every Tier 2 scan result in the database
- Backfill approximately 769K existing scan result rows with heuristic model attribution based on scan duration
- Provide an admin API endpoint to query model usage distribution and estimate OpenAI costs over time

## User Stories

### US-001: Persist LLM Model in Scan Results
**Project**: vskill-platform
**As a** platform operator
**I want** the LLM model name to be stored with each Tier 2 scan result
**So that** I can track which model processed each scan and identify OpenAI-incurring scans

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the Prisma schema `ScanResult` model, when the migration runs, then a nullable `llmModel String?` column exists in the `ScanResult` table
- [x] **AC-US1-02**: Given the `Tier2Payload` interface in `finalize-scan/route.ts`, when a Tier 2 scan payload is received, then the `model` field is accepted as an optional string property
- [x] **AC-US1-03**: Given the `StoredScanResult` interface in `submission-store.ts`, when a Tier 2 result is constructed, then the `llmModel` optional string property is available for storage
- [x] **AC-US1-04**: Given `persistScanResultToDb` in `submission-store.ts`, when a scan result with a non-null `llmModel` is persisted, then the `llmModel` value is written to the database `ScanResult` row
- [x] **AC-US1-05**: Given `finalize-scan/route.ts` destructures the request body and calls `storeScanResult`, when a Tier 2 payload includes `model`, then the value is passed through to `storeScanResult` as `llmModel`

### US-002: Heuristic Backfill of Historical Scan Data
**Project**: vskill-platform
**As a** platform operator
**I want** existing Tier 2 scan results to have inferred `llmModel` values based on scan duration
**So that** historical cost analysis is possible without rescanning all submissions

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given existing Tier 2 scan results with `durationMs > 30000`, when the backfill migration runs, then `llmModel` is set to `"gpt-4o-mini (inferred)"`
- [x] **AC-US2-02**: Given existing Tier 2 scan results with `durationMs` between 20000 and 30000 inclusive, when the backfill migration runs, then `llmModel` is set to `"unknown (ambiguous)"`
- [x] **AC-US2-03**: Given existing Tier 2 scan results with `durationMs < 20000`, when the backfill migration runs, then `llmModel` is set to `"cloudflare (inferred)"`
- [x] **AC-US2-04**: Given the backfill targets only `tier = 2` rows, when the migration runs, then Tier 1 and Tier 3 scan results are not modified

### US-003: Admin Stats Endpoint for LLM Model Usage
**Project**: vskill-platform
**As a** platform administrator
**I want** a stats endpoint showing LLM model distribution over time
**So that** I can monitor OpenAI cost exposure and track fallback frequency

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the endpoint `GET /api/v1/admin/scan-model-stats`, when an unauthenticated request is made, then a 401 response is returned
- [x] **AC-US3-02**: Given the endpoint `GET /api/v1/admin/scan-model-stats`, when an admin-authenticated request is made with `from` and `to` ISO date query params, then a JSON response is returned containing model distribution counts grouped by `llmModel` value
- [x] **AC-US3-03**: Given the `granularity` query param is set to `day`, when the stats endpoint is called with a date range, then results are grouped by calendar day
- [x] **AC-US3-04**: Given the `granularity` query param is set to `month`, when the stats endpoint is called with a date range, then results are grouped by calendar month
- [x] **AC-US3-05**: Given the response includes an `estimatedCost` field for each model group, when the model is `gpt-4o-mini` or `gpt-4o-mini (inferred)`, then cost is calculated using gpt-4o-mini per-token pricing

## Out of Scope

- Frontend dashboard UI for viewing model stats (admin API only in this increment)
- Modifying the VM scanner (`tier2-scan.js`) -- it already returns the `model` field
- Tracking token usage per scan (only model identity, not input/output token counts)
- Retroactive OpenAI billing reconciliation
- Alerting on OpenAI cost thresholds

## Technical Notes

### Dependencies
- Prisma ORM (existing) -- schema migration required
- `@/lib/auth` -- `requireAdmin` for admin endpoint auth
- `@/lib/api-helpers` -- `jsonResponse`, `errorResponse` for consistent API responses

### Constraints
- The `llmModel` column must be nullable (`String?`) since Tier 1 and Tier 3 scan results do not use LLMs, and pre-backfill rows will have null values
- The backfill must handle ~769K rows efficiently; raw SQL update with WHERE clause is preferred over row-by-row Prisma operations
- The composite index `(tier, llmModel, createdAt)` must be created in the same migration as the column addition to avoid a second migration

### Architecture Decisions
- **Nullable field over default value**: Using `String?` instead of a default empty string preserves the semantic distinction between "no LLM used" (Tier 1/3) and "LLM used but model unknown" (pre-backfill Tier 2)
- **Heuristic thresholds**: 30s+ = OpenAI (network round-trip to external API is slow), 20-30s = ambiguous (could be slow CF or fast OpenAI), <20s = Cloudflare (local inference is fast). These thresholds are based on observed production latency distributions
- **Inferred suffix**: Backfilled values use `"(inferred)"` suffix to distinguish heuristic attribution from actual model reporting
- **Prisma migration for backfill**: The backfill SQL runs as part of the Prisma migration rather than a standalone script, ensuring it runs exactly once and is tracked in migration history

### Key Files to Modify
- `prisma/schema.prisma` -- Add `llmModel` column and composite index to `ScanResult`
- `src/app/api/v1/internal/finalize-scan/route.ts` -- Add `model` to `Tier2Payload` interface, pass through to `storeScanResult`
- `src/lib/submission-store.ts` -- Add `llmModel` to `StoredScanResult` interface and `persistScanResultToDb`
- `src/lib/types.ts` -- Add `llmModel` to `ScanResultData` interface
- NEW: `src/app/api/v1/admin/scan-model-stats/route.ts` -- Stats endpoint
- NEW: Prisma migration with schema change + backfill SQL

## Non-Functional Requirements

- **Performance**: The composite index `@@index([tier, "llmModel", createdAt])` ensures stats queries over the 769K+ row `ScanResult` table complete in under 500ms for typical date ranges (30-90 days)
- **Security**: The stats endpoint requires admin JWT authentication via `requireAdmin`, consistent with all other `/api/v1/admin/` routes
- **Compatibility**: The nullable `llmModel` field is backwards-compatible; existing scan result reads that do not reference the field continue to work unchanged
- **Data Integrity**: The backfill migration is idempotent -- re-running it does not overwrite `llmModel` values that were already set by the live pipeline

## Edge Cases

- **Tier 2 payload without model field**: When `tier2-scan.js` returns a result without a `model` field (e.g., older scanner version), `llmModel` is stored as null -- no error
- **Tier 1 or Tier 3 scan results**: These do not use LLMs; `llmModel` remains null. The backfill SQL uses `WHERE tier = 2` to avoid touching them
- **Scan duration exactly 20000ms or 30000ms**: The 20000-30000 range is inclusive on both ends, classifying boundary values as `"unknown (ambiguous)"`
- **Stats query with no matching rows**: Returns an empty `buckets` array with `totalScans: 0` -- no 404
- **Missing `from`/`to` params**: Endpoint returns 400 with descriptive error message specifying required params

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Backfill migration times out on 769K rows | 0.3 | 6 | 1.8 | Use raw SQL UPDATE with WHERE clause (single statement, no row-by-row); test on staging first |
| Duration heuristic misclassifies model for edge-case scans | 0.5 | 3 | 1.5 | Suffix with "(inferred)" to distinguish from actual model reports; ambiguous range for 20-30s |
| Composite index creation locks table during migration | 0.2 | 5 | 1.0 | Use CONCURRENTLY if supported by Neon Postgres; run during low-traffic window |

## Success Metrics

- 100% of new Tier 2 scan results have non-null `llmModel` values within 24 hours of deployment
- Backfill covers all existing Tier 2 rows (verify with `SELECT COUNT(*) FROM "ScanResult" WHERE tier = 2 AND "llmModel" IS NULL`)
- Stats endpoint returns correct model distribution that matches manual spot-checks of recent scan logs
