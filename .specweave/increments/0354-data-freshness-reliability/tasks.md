# Tasks — 0354 Data Freshness & Reliability

### T-001: Migration — add metricsRefreshedAt column
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given migration runs → When schema inspected → Then Skill has metricsRefreshedAt DateTime?
- `prisma/schema.prisma` — add `metricsRefreshedAt DateTime?` to Skill model
- Create Prisma migration

### T-002: Remove >0 guard in enrichment batch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given skill with 100 stars → When GitHub returns 50 → Then DB updates to 50
- `src/lib/cron/enrichment.ts:38-43` — always set value when fetch succeeded (non-null)

### T-003: Remove >0 guard in live metrics
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given live enrichment → When GitHub returns 0 stars → Then enriched.githubStars = 0
- `src/lib/popularity-fetcher.ts:207-220` — set value when non-null, skip on null

### T-004: Wrap enrichment in per-skill transaction
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given skill update fails → When transaction rolls back → Then old scores preserved
- `src/lib/cron/enrichment.ts:47-68` — per-skill `$transaction` with inline trending calc

### T-005: Set metricsRefreshedAt in enrichment
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test**: Given enrichment updates skill → When complete → Then metricsRefreshedAt = now
- `src/lib/cron/enrichment.ts` — add `metricsRefreshedAt: new Date()` to updates

### T-006: Display freshness on skill detail page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given metricsRefreshedAt set → When detail page renders → Then "Metrics updated X ago"
- Add field to `types.ts`, `data.ts` mapping, render in `skills/[name]/page.tsx`

### T-007: Add rate-limit detection with backoff
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given GitHub returns 429 → When processing → Then waits with backoff
- `src/lib/cron/enrichment.ts` — check 429, read Retry-After, backoff (30s start, 120s max)

### T-008: Invalidate stats cache after enrichment
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test**: Given enrichment completes → When stats checked → Then KV refreshed
- Pass KV to enrichment, call `kv.delete("platform:stats")` after batch

### T-009: Increase batch size with env config
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [x] completed
**Test**: Given ENRICHMENT_BATCH_SIZE=50 → When batch runs → Then processes 50 skills
- `src/lib/cron/enrichment.ts:10` — default 50, configurable via env param
