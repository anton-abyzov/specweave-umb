# Tasks: Queue Per-Item Latency Optimization

---
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
  US-003: [T-003]
  US-004: [T-004]
  US-005: [T-005]
  US-006: [T-006]
---

## User Story: US-001 - Fire-and-Forget Metrics and Scan Log

### T-001: Remove await from metrics/log in consumer.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Implementation**:
1. In `consumer.ts`, remove `await` from `recordProcessed`, `recordFailed`, `recordTimeout`, `writeScanLog`
2. Add `.catch(() => {})` to each
3. Move `message.ack()` before telemetry calls

---

## User Story: US-002 - Merge setContentHash into storeScanResult

### T-002: Add contentHash param to storeScanResult, remove standalone call
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Implementation**:
1. Add optional `contentHash?: string` to `storeScanResult` second param
2. In the `sub:{id}` read-modify-write inside `storeScanResult`, also set `contentHashAtScan` if provided
3. In `process-submission.ts`, pass `contentHash` to the Tier 1 `storeScanResult` call
4. Remove the standalone `await setContentHash(id, contentHash)` call

---

## User Story: US-003 - Cache detectBranch in KV

### T-003: Add KV cache to detectBranch with 1hr TTL
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed

**Implementation**:
1. Import `getWorkerEnv`/`getCloudflareContext` in `scanner.ts`
2. At top of `detectBranch`, try `kv.get("branch:{owner}/{repo}")`
3. On hit, return cached value
4. On miss or error, call GitHub API as before
5. After successful API response, `kv.put` with 3600s TTL (fire-and-forget)

---

## User Story: US-004 - Parallelize getMetricsWindow

### T-004: Replace sequential loop with Promise.all
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed

**Implementation**:
1. Build array of bucket promises
2. Use `Promise.all([...bucketPromises, getTotals(kv)])`
3. Extract buckets and totals from results

---

## User Story: US-005 - Batch updateState for Publish Flow

### T-005: Add updateStateMulti and use in publish sequences
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed

**Implementation**:
1. Add `updateStateMulti(id, transitions: {state, message}[])` to `submission-store.ts`
2. Single KV read of `sub:{id}` and `hist:{id}`
3. Apply all transitions to submission object, append all to history
4. Single KV write for each
5. Fire DB persistence per-transition (best-effort)
6. In `process-submission.ts`, replace sequential `updateState` pairs with `updateStateMulti`

---

## User Story: US-006 - Parallelize Enrichment Batch

### T-006: Process enrichment in parallel chunks of 10
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed

**Implementation**:
1. Chunk skills array into groups of 10
2. Process each chunk with `Promise.allSettled`
3. Aggregate updated/errors counts from chunk results
4. Trending score recomputation unchanged (runs after loop)
