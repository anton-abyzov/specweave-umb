# Tasks: Crawler Pipeline Reliability and Guardrails (0401)

**Base path**: `repositories/anton-abyzov/vskill-platform/crawl-worker/`

## US-001: GitHub-Sharded Timeout Recovery

### T-001: Checkpoint persistence for github-sharded source
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given github-sharded runs in full mode → When it completes 10 shards and times out → Then next run resumes from shard 10 with seenRepos restored

**Implementation Details**:
- `lib/crawl-state.js`: shared checkpoint module with `loadState`, `saveState`, `clearState` functions
- State stored at `/tmp/crawl-state/github-sharded.json` with `savedAt` timestamp
- Checkpoint saved every 10 shards and on rate-limit interruption
- seenRepos serialized to checkpoint (capped at 50k entries) for cross-shard dedup
- On startup, checkpoint loaded and validated: must match current shardMode, index < shardPlan.length
- Stale checkpoints (>24h via `savedAt`) are ignored and deleted
- Full completion clears checkpoint file

**Files modified**:
- `lib/crawl-state.js` (new shared module)
- `sources/github-sharded.js` (checkpoint integration)

---

## US-002: Skills.sh Page Resumption

### T-002: Page state persistence for skills-sh source
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given skills-sh crawls page 15 and times out → When next run starts → Then crawling resumes from page 16

**Implementation Details**:
- Uses shared `crawl-state.js` module (`loadState`, `saveState`, `clearState`)
- State saved after every page: `{ lastPage: N }`
- On startup, loads checkpoint; if `lastPage > configStartPage`, resumes from `lastPage + 1`
- When `hasMore === false` or empty skills array, state file cleared (fresh start next run)
- 24h staleness handled by `crawl-state.js` (shared with github-sharded)

**Files modified**:
- `sources/skills-sh.js` (checkpoint integration)

---

## US-003: InlineSubmitter Safe Batching

### T-003: Copy-before-remove pattern in InlineSubmitter._flush()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given a batch of 15 repos is ready → When submission fails twice → Then repos are dropped with totalLost incremented and error logged

**Implementation Details**:
- `_flush()` copies batch via `buffer.slice(0, batchSize)` BEFORE any removal
- On success: `_recordSuccess()` splices from buffer, increments `totalSubmitted`
- On first failure: retries once via `submitBatch()` (which itself has 3 internal retries with backoff)
- On second failure: splices batch from buffer, increments `totalLost`, logs error
- `maxRetryBatches` effectively = 2 (initial + 1 retry), then drop to prevent infinite loops

**Files modified**:
- `lib/inline-submitter.js`

---

## US-004: SAST Scanner Pre-flight Health Check

### T-004: Pre-flight health check before claiming scans
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given scanner-worker is down → When sast-scanner crawl runs → Then returns immediately with `{ healthCheckFailed: true, checked: 0 }` and no scans are claimed

**Implementation Details**:
- `checkScannerHealth()` function: GET `http://{SCANNER_WORKER_HOST}:9500/health` with 5s `AbortSignal.timeout`
- Called before `fetchPending()` in the main `crawl()` function
- On failure (network error, non-200, timeout): logs error with host details, returns early with `{ ...stats, healthCheckFailed: true }`
- No scans are fetched or claimed when health check fails

**Files modified**:
- `sources/sast-scanner.js`

---

## US-005: Health Monitoring and Metrics

### T-005: Per-source metrics accumulation in scheduler
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [x] completed
**Test**: Given source runs 10 times → When 5 consecutive failures occur → Then [ALERT] is logged and metrics reflect totalErrors

**Implementation Details**:
- `sourceMetrics` Map in scheduler.js, keyed by source name
- `getOrCreateMetrics()` initializes: totalRuns, totalErrors, totalTimeouts, totalDiscovered, totalSubmitted, totalCreated, totalLost, durations[], lastAlertAt
- `accumulateMetrics()` called after each successful run, updates all counters
- `checkConsecutiveFailures()` logs `[ALERT]` when consecutiveErrors >= threshold (default 5), rate-limited to once per 30 min per source
- Dedup ratio calculated in `getSourceMetrics()`: `(1 - totalCreated/totalSubmitted) * 100`
- Duration tracking: last 100 runs stored, averageDurationMs computed
- Metrics reset on process restart (in-memory only)

**Files modified**:
- `scheduler.js`

### T-006: GET /metrics endpoint on crawl-worker server
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test**: Given scheduler has run sources → When GET /metrics is called → Then returns JSON with uptime, per-source metrics, and scheduler state

**Implementation Details**:
- `GET /metrics` route in server.js returns JSON with:
  - `uptime`: seconds since process start
  - `metrics`: output of `getSourceMetrics()` from scheduler.js
  - `scheduler`: output of `getSchedulerState()` from scheduler.js
- No authentication required (monitoring endpoint)

**Files modified**:
- `server.js`
