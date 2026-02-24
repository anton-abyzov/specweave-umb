# Tasks: Stuck Submission Detection

## Phase 1: Backend — Recovery & Cron

### T-001: Increase cron frequency to every 5 minutes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given cron runs → When minute >= 5 → Then only recovery + stats run (no discovery/enrichment)

**Files**: `wrangler.jsonc`, `scripts/build-worker-entry.ts`

- Change cron from `0 * * * *` to `*/5 * * * *`
- Gate discovery and enrichment to run only when `minute < 5` (hourly)
- Recovery, stats refresh, DB prewarm run every invocation

---

### T-002: Increase recovery retry budget from 1 to 3
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given stuck submission retried 2x → When recovery runs 3rd time → Then re-enqueues (not rejects)

**Files**: `src/lib/queue/recovery.ts`, `src/app/api/v1/admin/reenqueue/route.ts`

- Change KV value from boolean `"1"` to counter (`"1"`, `"2"`, `"3"`)
- Parse counter, compare against `MAX_RECOVERY_RETRIES = 3`
- Backward compat: existing `"1"` values treated as count=1
- Include retry count in recovery message
- Updated reenqueue route MAX_RECOVERY_RETRIES from 1 to 3 to match

## Phase 2: Backend — Consumer Observability

### T-003: Add inflight tracking and wire recordRetried
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04 | **Status**: [x] completed
**Test**: Given consumer starts processing → When inflight KV read → Then contains startedAt and attempt

**File**: `src/lib/queue/consumer.ts`

- Before processing: write `inflight:{submissionId}` KV with `{ startedAt, attempt }`, TTL 300s
- After processing (success/failure): delete inflight marker
- In catch block: call `recordRetried()` when `message.attempts > 1`

---

### T-004: Classify timeout vs other failures
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**Test**: Given withTimeout rejects → When consumer catches → Then metric recorded as timeout

**Files**: `src/lib/queue/consumer.ts`, `src/lib/queue/metrics-store.ts`, `src/lib/queue/types.ts`

- Add `recordTimeout(kv, durationMs)` to metrics-store (increments `failed` + new `timedOut` counter)
- Add optional `timedOut`/`totalTimedOut` to bucket/totals types
- Add `delete` to QueueKV interface for inflight cleanup
- In consumer catch: check `error.message.startsWith("Timeout after")` → call `recordTimeout` instead of `recordFailed`

## Phase 3: User UX — Staleness Warning

### T-005: Add staleness warning on submission status page
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given submission stuck > 3min → When page renders → Then amber warning banner shown with elapsed time

**File**: `src/app/submit/[id]/page.tsx`

- After Status line, add staleness check
- Active states only: RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED
- Threshold: 3 minutes (before 5-min recovery threshold)
- Use `useEffect` interval (30s) to tick elapsed time display
- Amber banner: "This submission appears to be taking longer than usual (Xm). The system will automatically retry processing."

## Phase 4: Admin Observability

### T-006: Surface attempt info in admin queue status API
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03 | **Status**: [x] completed
**Test**: Given stuck submission with inflight marker → When admin queries status → Then response includes attempt info

**File**: `src/app/api/v1/admin/queue/status/route.ts`

- For each stuck entry, look up `inflight:{id}` from QUEUE_METRICS_KV
- Add `processingStartedAt` and `attempt` to stuck list entries
- Add `totalTimedOut` to throughput section
- Add `timedOut` to recentHours entries

---

### T-007: Enhance admin Queue Monitor with timeout stats
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**Test**: Given timeout metrics exist → When admin views queue → Then timeout stat card and attempt info shown

**File**: `src/app/admin/queue/page.tsx`

- Add "Timeouts (24h)" stat card (5-column grid)
- Show attempt number on stuck submission rows
- Update StuckEntry type with processingStartedAt and attempt fields
