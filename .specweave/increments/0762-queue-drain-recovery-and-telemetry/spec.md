---
status: completed
---
# 0762 — Queue drain recovery and per-stage telemetry

## Problem

Production observation 2026-04-26 14:35Z on verified-skill.com:

- `/api/v1/submissions/stats` returns `generatedAt: 2026-04-26T07:11:07Z` (7.5h stale), `degraded: true`, `avgScore: 0`. 4 polls 30s apart return identical body — cron is frozen.
- `/api/v1/submissions?state=active` returns `total: 1`, `cache: "latest"`, with `queuePositions` reporting position **141** for the only visible item — the API contradicts itself.
- Last `state=PUBLISHED` `updatedAt` is **2026-02-27** (~2 months stale); last `REJECTED` is 2026-03-31. Pipeline has been effectively dead for weeks.
- The single visible active item entered `TIER1_SCANNING` 1.5h ago with message "Claimed by VM scanner" and never advanced.

The queue counter on the queue page oscillates between 1, 5, 3 — not because items are draining, but because the rehydrate+drift-correction path in the active list endpoint shows whatever survives the KV→DB consistency check while real items pile up undisplayed.

## Root causes

1. **Hetzner VM `stats-compute` source not registered in `crawl-worker/scheduler.js`** — `SOURCE_TIMEOUTS`/`SOURCE_COOLDOWNS` lack the `stats-compute` entry that `crawl-worker/sources/stats-compute.js`'s own header documented as required (lines 24-25). Falls through to 1h cooldown (vs intended 10min) and is the first to die under exponential backoff.
2. **CF Worker `refreshQueueStats` cron exits silently on partial failure** — `_refreshQueueStatsImpl` runs sequentially behind the platform-stats / DB-prewarm phases. Any upstream failure or CPU-budget overrun in those phases starves the queue stats refresh, and there is no fallback path that writes a fresh-timestamped degraded snapshot.
3. **Items get permanently stuck in `TIER1_SCANNING`** when the VM scanner crashes between claim and finalize. `recoverStuckSubmissions` only touches items with stored scan results — claimed-but-never-scanned items have no escape hatch.
4. **List cache poisoning** — `src/app/api/v1/submissions/route.ts:475` writes `submissions: []` with `total: N>0` to the 24h `submissions:latest:active` cache when drift correction empties the visible list. Once written, the queue page serves a near-empty list for up to 24h.
5. **`flushDbUpdates` swallows DB write failures** — fire-and-forget at line 442 with a bare `.catch(() => {})` masks Prisma errors, so drift corrections that should persist silently don't.

## User stories and acceptance criteria

### US-001 — Stats freshness self-heals when VMs are dead
- [x] **AC-US1-01**: KV `submissions:stats-cache` `generatedAt` is at most 15 minutes old whenever the CF Worker cron is firing, regardless of Hetzner VM health.
- [x] **AC-US1-02**: When the full computation exceeds budget, a degraded snapshot with fresh `generatedAt` and `degraded: true` is still written so the API returns a recent timestamp.
- [x] **AC-US1-03**: `crawl-worker/scheduler.js` has explicit `SOURCE_TIMEOUTS["stats-compute"] = 5*60*1000` and `SOURCE_COOLDOWNS["stats-compute"] = 10*60*1000` so VM stats refresh runs every 10 min when assigned.

### US-002 — Items don't stay stuck in TIER1_SCANNING
- [x] **AC-US2-01**: Items in `TIER1_SCANNING` whose `updatedAt` is older than 30 minutes are atomically reset to `RECEIVED` (CAS ensures only matching items are updated) on each cron tick.
- [x] **AC-US2-02**: Each release increments KV `recovery:scanning-released:{id}` (90-day TTL); after 3 releases the item is rejected with reason `scanner_timeout_max_retries` instead of resetting again.
- [x] **AC-US2-03**: A reset emits a stateEvent with `from: "TIER1_SCANNING"`, `to: "RECEIVED"`, `trigger: "scanner_timeout"`, and updates `sub:<id>` KV to keep readers consistent.

### US-003 — Per-stage processing time is observable
- [x] **AC-US3-01**: `GET /api/v1/submissions/[id]` returns a `stageTimings` object with: `receivedAt`, `tier1ScanningAt`, `autoApprovedAt`, `publishedAt`, `rejectedAt` (each ISO timestamp or null) and `msInReceived`, `msInScanning`, `msInAutoApproved`, `totalMs` (each non-negative integer or null).
- [x] **AC-US3-02**: Out-of-order timestamps in `stateHistory` (e.g. PUBLISHED before AUTO_APPROVED — observed in `sub_32a4c001`) clamp computed durations to 0 instead of producing negative values.
- [x] **AC-US3-03**: New `GET /api/v1/queue/health` returns `statsAge`, `oldestActive` (id, state, ageMs), `drainRate.last1h`, `drainRate.last6h`, `vmHeartbeat.lastPostAt`. Cached 30 seconds in KV `queue-health:cache`.

### US-004 — List cache cannot poison itself with empty arrays
- [x] **AC-US4-01**: `src/app/api/v1/submissions/route.ts` only writes the KV list cache when `submissions.length > 0`; an empty `submissions` array is never persisted, regardless of the `total` field.
- [x] **AC-US4-02**: `flushDbUpdates` failures are logged via `console.error("[queue/flushDbUpdates] failed:", ...)` per rejected `Promise.allSettled` entry, surfacing silent drift-correction breakage.

### US-005 — Drain rate is verifiable end-to-end
- [x] **AC-US5-01**: A verification script (`scripts/drain-verify.mjs`) submits N items, polls `/api/v1/submissions?state=active` every 30s for up to 30 min, and reports per-id stage transitions with timestamps and durations.
- [x] **AC-US5-02**: The script writes a structured log to `reports/drain-verification-<timestamp>.txt` listing every poll's `total` plus a per-id timing matrix.
- [x] **AC-US5-03**: After deploy, the active count must show movement (any non-zero change) within 30 minutes; if not, the report explicitly flags `NO_DRAIN_OBSERVED` for follow-up.

## Out of scope

- Hetzner VM SSH access / VM env reconfiguration (no SSH keys in this environment).
- Bulk admin drain endpoint for the ~150 items already stuck — recovery cron will work them through gradually at 3 retries × 30 min cycles.
- Replacing the stale `published` listing data (last entry 2026-02-27); whether that's a list-cache stale issue or a real publish drought is a separate diagnosis.
