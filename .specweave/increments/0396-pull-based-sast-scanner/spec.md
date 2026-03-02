---
increment: 0396-pull-based-sast-scanner
title: Pull-based SAST scanning
type: feature
priority: P1
status: completed
created: 2026-03-02T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Pull-based SAST Scanner

## Problem Statement

External SAST scans (semgrep, njsscan, trufflehog) are currently dispatched via push: the platform's `dispatchExternalScans()` does an HTTP POST to Hetzner scanner workers, round-robining across `SCANNER_WORKERS` env var. This creates tight coupling between the platform and worker availability. If workers are down during dispatch, scans are lost. There is also a dead GitHub Actions fallback path that is never used.

The crawl-worker already has a proven pull-based pattern (`submission-scanner.js`): fetch pending items from platform API, claim atomically, process, finalize. This increment adds a `sast-scanner` source that follows the same pattern for external SAST scans, replacing the push dispatch with a lightweight "enqueue to DB" operation.

## Architecture Decisions

1. **Pull-based source**: New `crawl-worker/sources/sast-scanner.js` follows the `submission-scanner.js` pattern (fetchPending -> claim -> dispatch to localhost scanner-worker -> finalize via webhook)
2. **Platform API**: Two new internal endpoints: `GET /api/v1/internal/pending-sast-scans` and `POST /api/v1/internal/claim-sast-scan`
3. **Lightweight enqueue**: Existing call sites (process-submission, finalize-scan, admin/scan-external) write PENDING status to DB+KV but skip HTTP dispatch when `SAST_PULL_MODE` is active
4. **Feature flag**: `SAST_PULL_MODE` env var on platform. When true, `dispatchExternalScans()` only enqueues (writes PENDING) without pushing to workers. Pull source picks up PENDING rows.
5. **Reaper**: pending-sast-scans endpoint returns RUNNING scans stuck >15 min (claimedAt older than threshold) as re-claimable, alongside genuinely PENDING rows
6. **Schema changes**: Add `claimedAt` (DateTime?) and `claimedBy` (String?) columns to `ExternalScanResult` Prisma model
7. **Claim granularity**: One provider per claim (one ExternalScanResult row) for failure isolation
8. **VM assignment**: `sast-scanner` added to `ASSIGNED_SOURCES` on VM-2 initially
9. **Auth**: Crawl-worker uses existing `WORKER_SECRET` for localhost:9500 scanner-worker dispatch
10. **Phased**: This increment adds pull path. Push path stays as fallback. Follow-up increment removes push + GitHub Actions dead code.

## User Stories

### US-001: Platform API for Pending SAST Scans (P1)
**Project**: vskill-platform

**As a** crawl-worker sast-scanner source
**I want** an API endpoint that returns PENDING and stuck RUNNING external scan rows
**So that** I can pull work items instead of relying on push dispatch

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /api/v1/internal/pending-sast-scans` returns ExternalScanResult rows with status=PENDING, ordered by dispatchedAt ASC, limited to 50 per request
- [x] **AC-US1-02**: The endpoint also returns RUNNING rows where claimedAt is older than 15 minutes (stuck/timed-out scans eligible for re-claim)
- [x] **AC-US1-03**: The endpoint requires `X-Internal-Key` header matching `INTERNAL_BROADCAST_KEY` env var (same auth as other internal endpoints)
- [x] **AC-US1-04**: Response shape: `{ scans: [{ id, skillName, provider, status, dispatchedAt, claimedAt, claimedBy }] }`

---

### US-002: Atomic Claim Endpoint for SAST Scans (P1)
**Project**: vskill-platform

**As a** crawl-worker sast-scanner source
**I want** an atomic claim endpoint that transitions PENDING -> RUNNING with claimedAt/claimedBy
**So that** multiple VMs cannot process the same scan simultaneously

**Acceptance Criteria**:
- [x] **AC-US2-01**: `POST /api/v1/internal/claim-sast-scan` accepts `{ scanId, claimedBy }` and atomically updates status PENDING->RUNNING with claimedAt=now and claimedBy set
- [x] **AC-US2-02**: The claim uses a Prisma `updateMany` with `where: { id, status: PENDING }` (or status=RUNNING with claimedAt >15min) to ensure atomicity -- returns `{ ok: false }` if already claimed
- [x] **AC-US2-03**: The endpoint requires `X-Internal-Key` header authentication
- [x] **AC-US2-04**: Response shape: `{ ok: true, scan: { id, skillName, provider, status } }` on success, `{ ok: false, reason: "already_claimed" }` on conflict

---

### US-003: Schema Migration for Claim Tracking (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** claimedAt and claimedBy columns on ExternalScanResult
**So that** the claim endpoint can track which worker owns each scan and detect stuck scans

**Acceptance Criteria**:
- [x] **AC-US3-01**: Prisma schema adds `claimedAt DateTime?` to ExternalScanResult model
- [x] **AC-US3-02**: Prisma schema adds `claimedBy String?` to ExternalScanResult model
- [x] **AC-US3-03**: Migration runs cleanly against the existing database (nullable columns, no data loss)
- [x] **AC-US3-04**: The `@@index([status])` index on ExternalScanResult is retained for efficient pending queries

---

### US-004: Crawl-Worker SAST Scanner Source (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** a `sast-scanner` crawl-worker source that pulls pending SAST scans and dispatches them to the local scanner-worker
**So that** external SAST scans run reliably without depending on push dispatch from Cloudflare Workers

**Acceptance Criteria**:
- [x] **AC-US4-01**: New file `crawl-worker/sources/sast-scanner.js` exports a default `crawl(config)` function following the crawl-worker source contract
- [x] **AC-US4-02**: The source fetches pending scans via `GET /api/v1/internal/pending-sast-scans`, claims each via `POST /api/v1/internal/claim-sast-scan`, then dispatches to `http://localhost:9500/scan` with the existing scanner-worker payload format (`{ skillName, repoOwner, repoName, provider, callbackUrl }`)
- [x] **AC-US4-03**: The source uses `X-Worker-Signature` header with `WORKER_SECRET` env var for scanner-worker auth (same as current push dispatch)
- [x] **AC-US4-04**: Failed claims (already claimed by another VM) are skipped gracefully with a log line
- [x] **AC-US4-05**: The source processes one scan at a time (sequential claim-dispatch, no concurrency within a single cycle) for simplicity
- [x] **AC-US4-06**: The crawl function returns `{ checked, dispatched, skipped, errors }` summary matching the crawl-worker source return convention

---

### US-005: Lightweight Enqueue (Feature-Flagged Push Bypass) (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** `dispatchExternalScans()` to only write PENDING status to DB+KV without HTTP dispatch when `SAST_PULL_MODE` is enabled
**So that** the platform enqueues work for the pull-based source instead of pushing to workers

**Acceptance Criteria**:
- [x] **AC-US5-01**: When `SAST_PULL_MODE` env var is truthy, `dispatchExternalScans()` writes PENDING status to KV and creates/upserts the ExternalScanResult DB row with status=PENDING, then returns without making HTTP calls to scanner workers
- [x] **AC-US5-02**: When `SAST_PULL_MODE` is falsy or absent, the existing push dispatch behavior is preserved unchanged (round-robin POST to SCANNER_WORKERS)
- [x] **AC-US5-03**: The DB upsert uses `@@unique([skillName, provider])` constraint -- if a row already exists with PENDING or RUNNING status, the enqueue is skipped (dedup, same as current KV dedup logic)
- [x] **AC-US5-04**: The GitHub Actions fallback code path is left in place (removal deferred to follow-up increment)
- [x] **AC-US5-05**: All three call sites (process-submission, finalize-scan, admin/scan-external) use the updated `dispatchExternalScans()` with no call-site changes needed

---

### US-006: Scheduler Integration and VM Deployment (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** the sast-scanner source registered in the scheduler with appropriate timeout/cooldown and deployed to VM-2
**So that** SAST scans are continuously pulled and processed

**Acceptance Criteria**:
- [x] **AC-US6-01**: `scheduler.js` SOURCE_TIMEOUTS includes `"sast-scanner": 30 * 60 * 1000` (30 min timeout -- scans are quick, each cycle dispatches to scanner-worker which handles the actual work)
- [x] **AC-US6-02**: `scheduler.js` SOURCE_COOLDOWNS includes `"sast-scanner": 30 * 1000` (30s cooldown -- check for new work frequently but not aggressively)
- [x] **AC-US6-03**: `.env.vm2` has `sast-scanner` appended to ASSIGNED_SOURCES
- [x] **AC-US6-04**: The callbackUrl constructed by sast-scanner.js uses `config.platformUrl` (defaults to `https://verified-skill.com`) so webhook results route back to the platform

## Functional Requirements

### FR-001: Pending Scan Query
The `pending-sast-scans` endpoint queries: `WHERE status = 'PENDING' OR (status = 'RUNNING' AND claimedAt < NOW() - INTERVAL '15 minutes')`, ordered by `dispatchedAt ASC`, limited to 50 rows. This ensures stuck scans are automatically retried.

### FR-002: Atomic Claim with Optimistic Locking
The claim endpoint uses Prisma `updateMany` with a compound WHERE clause (`id = ? AND (status = 'PENDING' OR (status = 'RUNNING' AND claimedAt < ?))`). If `count === 0`, the scan was already claimed. This avoids explicit database locks.

### FR-003: Scanner-Worker Payload Compatibility
The sast-scanner source constructs the exact same payload as the current push dispatch: `{ skillName, repoOwner, repoName, provider, callbackUrl }`. The scanner-worker (server.js:9500) and webhook callback path remain unchanged.

### FR-004: DB+KV Dual Write on Enqueue
In pull mode, `dispatchExternalScans()` writes both KV (for dedup checks by existing code) and DB (for the pull source to query). The KV write preserves backward compatibility with code that reads `external-scan:{skillName}:{provider}` keys.

## Success Criteria

- External SAST scans complete end-to-end via pull path on VM-2 with `SAST_PULL_MODE=true`
- No scan loss: every PENDING row is eventually claimed and dispatched
- Stuck scans (worker crash) automatically retry after 15-minute reaper window
- Zero changes to scanner-worker server.js or webhook callback endpoint
- Platform response time unaffected (no more outbound HTTP from Cloudflare Workers to Hetzner)

## Out of Scope

- Removing push dispatch code or GitHub Actions fallback (follow-up increment)
- Changes to scanner-worker/server.js (already handles the scan payload correctly)
- Changes to the webhook callback endpoint (`/api/v1/webhooks/scan-results`)
- Multi-VM sast-scanner deployment (VM-2 only for initial rollout)
- Result aggregation or dashboard changes
- KV-only mode without DB (DB is the source of truth for pull)

## Dependencies

- Existing `ExternalScanResult` Prisma model and `ExternalScanStatus` enum
- Existing `scanner-worker/server.js` on port 9500
- Existing `crawl-worker/scheduler.js` source loading mechanism
- Existing `INTERNAL_BROADCAST_KEY` / `X-Internal-Key` auth pattern on internal endpoints
- Existing KV store operations in `external-scan-store.ts`

## Technical Notes

- The `submission-scanner.js` source is the closest architectural analog. The sast-scanner source follows the same fetchPending -> claim -> process pattern, but dispatches to localhost scanner-worker instead of doing the scan itself.
- The `repoOwner` and `repoName` are not currently stored on ExternalScanResult. The sast-scanner source needs them for the scanner-worker payload. Two options: (a) store them on ExternalScanResult at enqueue time, or (b) look up the Skill record to get repoUrl and parse it. Option (b) avoids a schema change and uses existing data. The pending-sast-scans endpoint should join with the Skill table to include repoUrl in the response.
- The `callbackUrl` is always `{platformUrl}/api/v1/webhooks/scan-results` -- the sast-scanner source constructs this from `config.platformUrl`.
