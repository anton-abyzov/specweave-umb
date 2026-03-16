# Implementation Plan: Pull-based SAST Scanner

## Overview

Replace the push-based external SAST dispatch (`dispatchExternalScans()` POSTing to `SCANNER_WORKERS` IPs) with a pull-based crawl-worker source. The new `sast-scanner.js` source follows the proven `submission-scanner.js` pattern: poll platform API for pending work, claim atomically, dispatch to co-located scanner-worker on `localhost:9500`, and let the existing webhook callback handle result ingestion. A feature flag (`SAST_PULL_MODE`) gates the transition -- when enabled, the platform enqueues work to DB+KV without pushing HTTP to workers.

## Architecture

### System Flow (Pull Model)

```
ENQUEUE (Platform side):
  process-submission.ts / finalize-scan / admin/scan-external
    └─► dispatchExternalScans() [modified]
         └─► if SAST_PULL_MODE:
              ├── Write PENDING to EXTERNAL_SCANS_KV (backward compat)
              └── Upsert ExternalScanResult DB row (status=PENDING)
              └── RETURN (no HTTP push)

PULL (VM side):
  crawl-worker scheduler loop
    └─► sast-scanner.js crawl()
         ├── GET /api/v1/internal/pending-sast-scans
         │    └── Returns PENDING rows + stuck RUNNING rows (claimedAt >15min)
         │    └── Joins Skill table to include repoUrl
         ├── For each scan:
         │    ├── POST /api/v1/internal/claim-sast-scan {scanId, claimedBy}
         │    │    └── Atomic PENDING→RUNNING via updateMany WHERE
         │    ├── POST http://localhost:9500/scan {skillName, repoOwner, repoName, provider, callbackUrl}
         │    │    └── Scanner worker returns 202, runs scan async
         │    └── Skip if claim fails (already claimed by another VM)
         └── Return {checked, dispatched, skipped, errors}

RESULT CALLBACK (unchanged):
  scanner-worker
    └─► POST /api/v1/webhooks/scan-results
         ├── Upsert ExternalScanResult (status=PASS/FAIL)
         └── Update EXTERNAL_SCANS_KV
```

### Components

| Component | Location | Change Type |
|-----------|----------|-------------|
| `sast-scanner.js` | `crawl-worker/sources/` | **NEW** |
| `pending-sast-scans/route.ts` | `src/app/api/v1/internal/` | **NEW** |
| `claim-sast-scan/route.ts` | `src/app/api/v1/internal/` | **NEW** |
| `external-scan-dispatch.ts` | `src/lib/` | MODIFIED (feature flag) |
| `schema.prisma` | `prisma/` | MODIFIED (2 columns) |
| `scheduler.js` | `crawl-worker/` | MODIFIED (timeouts/cooldowns) |
| `server.js` | `crawl-worker/` | MODIFIED (VALID_SOURCES) |
| `.env.vm2` | `crawl-worker/` | MODIFIED (add sast-scanner) |
| `env.d.ts` | `src/lib/` | MODIFIED (add SAST_PULL_MODE) |
| scanner-worker/* | `scanner-worker/` | **UNCHANGED** |
| webhook route | `src/app/api/v1/webhooks/scan-results/` | **UNCHANGED** |

### Data Model

#### ExternalScanResult (Modified)

```
ExternalScanResult
──────────────────────────────────────────────────────────────
Column          Type                 Change    Notes
──────────────────────────────────────────────────────────────
id              String UUID PK       existing
skillName       String               existing  @@unique with provider
provider        ScanProvider enum    existing  SEMGREP/NJSSCAN/TRUFFLEHOG
status          ExternalScanStatus   existing  PENDING/RUNNING/PASS/FAIL/TIMED_OUT
verdict         String?              existing
score           Int?                 existing
criticalCount   Int                  existing
highCount       Int                  existing
mediumCount     Int                  existing
lowCount        Int                  existing
findings        Json                 existing
commitSha       String?              existing
githubRunId     String?              existing
githubRunUrl    String?              existing
dispatchedAt    DateTime             existing  When enqueued
completedAt     DateTime?            existing  When results received
claimedAt       DateTime?            NEW       When a VM claimed this scan
claimedBy       String?              NEW       VM identifier (e.g. "vm2:9600")
createdAt       DateTime             existing
updatedAt       DateTime             existing

Indexes: @@unique([skillName, provider]), @@index([skillName]),
         @@index([status]), @@index([provider])
```

The `claimedAt` column serves double duty: claim tracking AND reaper detection. Scans where `status=RUNNING AND claimedAt < NOW() - 15min` are returned by the pending endpoint as re-claimable.

#### Skill (Read-only join target)

The `pending-sast-scans` endpoint joins `ExternalScanResult` with `Skill` to get `repoUrl` for each scan. No changes to the Skill model.

### API Contracts

#### GET /api/v1/internal/pending-sast-scans

```
Auth: X-Internal-Key header (matches INTERNAL_BROADCAST_KEY)
Query params: ?limit=50 (max 200)

Response 200:
{
  "scans": [
    {
      "id": "uuid",
      "skillName": "eslint-config-airbnb",
      "provider": "SEMGREP",
      "status": "PENDING",
      "repoUrl": "https://github.com/airbnb/javascript",
      "dispatchedAt": "2026-03-02T00:00:00Z",
      "claimedAt": null,
      "claimedBy": null
    }
  ],
  "count": 1
}

SQL (simplified):
  SELECT esr.id, esr."skillName", esr.provider, esr.status,
         esr."dispatchedAt", esr."claimedAt", esr."claimedBy",
         s."repoUrl"
  FROM "ExternalScanResult" esr
  JOIN "Skill" s ON s.name = esr."skillName"
  WHERE esr.status = 'PENDING'
     OR (esr.status = 'RUNNING'
         AND esr."claimedAt" < NOW() - INTERVAL '15 minutes')
  ORDER BY esr."dispatchedAt" ASC
  LIMIT $limit
```

#### POST /api/v1/internal/claim-sast-scan

```
Auth: X-Internal-Key header
Body: { "scanId": "uuid", "claimedBy": "vm2:9600" }

Response 200 (success):
  { "ok": true, "scan": { "id": "uuid", "skillName": "...", "provider": "SEMGREP" } }

Response 200 (conflict):
  { "ok": false, "reason": "already_claimed" }

Implementation: Prisma updateMany with compound WHERE:
  WHERE id = ? AND (
    status = 'PENDING'
    OR (status = 'RUNNING' AND claimedAt < NOW() - 15min)
  )
  SET status = 'RUNNING', claimedAt = NOW(), claimedBy = ?

  If count === 0 → already claimed / not found
```

### Feature Flag: SAST_PULL_MODE

- **Where**: `CloudflareEnv` type in `env.d.ts`, read in `external-scan-dispatch.ts`
- **When truthy**: `dispatchExternalScans()` writes PENDING to KV + upserts DB row, then returns. No HTTP to workers.
- **When falsy/absent**: Existing push behavior preserved (round-robin POST to `SCANNER_WORKERS`).
- **Rollout**: Set `SAST_PULL_MODE=true` as CF secret. Add `sast-scanner` to VM-2 `ASSIGNED_SOURCES`. Monitor. Follow-up increment removes push path entirely.

## Technology Stack

- **Language/Framework**: TypeScript (Next.js API routes), JavaScript (crawl-worker source)
- **Database**: PostgreSQL via Prisma (existing)
- **KV**: Cloudflare Workers KV (existing, backward compat writes)
- **Runtime**: Node.js ESM on Hetzner VMs (crawl-worker), Cloudflare Workers (platform)

## Implementation Phases

### Phase 1: Schema + Platform API (Foundation)

1. **Prisma migration**: Add `claimedAt` and `claimedBy` nullable columns to `ExternalScanResult`
2. **GET /api/v1/internal/pending-sast-scans**: Raw SQL query with Skill join, X-Internal-Key auth
3. **POST /api/v1/internal/claim-sast-scan**: Atomic claim with updateMany WHERE clause
4. **Tests**: Unit tests for both endpoints (mock DB, verify auth, verify atomicity)

### Phase 2: Enqueue + Crawl Source (Core)

5. **Modify `dispatchExternalScans()`**: Add SAST_PULL_MODE check. When true, write KV + upsert DB row, skip HTTP push. The DB upsert uses the existing `@@unique([skillName, provider])` -- skipDuplicates for PENDING/RUNNING rows.
6. **New `sast-scanner.js`**: fetchPending -> claim -> dispatch to localhost:9500 -> return stats. Follows queue-processor.js/submission-scanner.js pattern.
7. **Tests**: Unit tests for modified dispatch (both flag states), crawl source logic (mock fetch)

### Phase 3: Integration + Deploy (Enhancement)

8. **Scheduler config**: Add `sast-scanner` to SOURCE_TIMEOUTS (30min) and SOURCE_COOLDOWNS (30s) in `scheduler.js`. Add to `VALID_SOURCES` in `server.js`.
9. **VM config**: Add `sast-scanner` to `.env.vm2` ASSIGNED_SOURCES
10. **env.d.ts**: Add `SAST_PULL_MODE?: string` to CloudflareEnv
11. **Deploy and verify**: Set CF secret, deploy platform, deploy VMs, verify end-to-end

## Testing Strategy

### Unit Tests (Vitest)
- `pending-sast-scans/route.test.ts`: Auth, SQL query shape, reaper logic (RUNNING + stale claimedAt), limit handling
- `claim-sast-scan/route.test.ts`: Auth, atomic claim success/conflict, updateMany WHERE verification
- `external-scan-dispatch.test.ts`: Extended to cover SAST_PULL_MODE=true path (DB upsert, no HTTP), SAST_PULL_MODE=false (existing behavior unchanged)
- `sast-scanner.test.js`: Node test runner, mock fetch for platform API + scanner-worker, verify claim/dispatch/skip flow

### Integration Tests
- Full pull cycle: enqueue via modified dispatch -> pending endpoint returns it -> claim -> dispatch to mock scanner-worker
- Reaper: set claimedAt to 20min ago, verify pending endpoint returns it as re-claimable

### Manual Verification
- Deploy to VM-2 with `SAST_PULL_MODE=true` on platform
- Trigger a manual scan via admin endpoint, verify sast-scanner picks it up
- Monitor `/status` endpoint on crawl-worker for sast-scanner source state

## Technical Challenges

### Challenge 1: Race Condition Between Enqueue and Pull
**Problem**: If `dispatchExternalScans()` writes PENDING and the pull source claims it before the KV write completes, KV could still show old state.
**Solution**: The KV write happens first (before DB upsert), and is used only for dedup. The pull source queries DB, not KV. KV is eventual-consistency safe for this use case.
**Risk**: Low. KV is only for backward compat reads; DB is source of truth for pull.

### Challenge 2: Scanner-Worker Accepts Scan But Callback Fails
**Problem**: Scanner-worker returns 202 (accepted), runs the scan, but the webhook callback to the platform fails. ExternalScanResult stays RUNNING forever.
**Solution**: The 15-minute reaper catches this. Next pull cycle re-claims the scan, dispatches again. Scanner-worker is idempotent (clones fresh, scans fresh). The webhook endpoint does upsert, so duplicate results are safe.
**Risk**: Low. This is the same failure mode as the push model, but now auto-recovers via reaper.

### Challenge 3: ExternalScanResult Has No repoUrl
**Problem**: The sast-scanner source needs `repoOwner` and `repoName` for the scanner-worker payload, but `ExternalScanResult` doesn't store them.
**Solution**: The `pending-sast-scans` endpoint JOINs with `Skill` table (on `skillName = Skill.name`) to include `repoUrl`. The crawl source parses `repoUrl` to extract owner/name. If the Skill doesn't exist (orphaned scan row), the scan is skipped.
**Risk**: Low. Every published skill has a Skill row. Orphaned ExternalScanResult rows are edge cases from manual admin triggers.

### Challenge 4: Backward Compatibility During Phased Rollout
**Problem**: During transition, some scans might be both pushed (if SAST_PULL_MODE isn't set yet) and pulled. The scanner-worker could process the same scan twice.
**Solution**: The scanner-worker and webhook are idempotent. The webhook does `upsert` on `@@unique([skillName, provider])`. Duplicate processing wastes compute but doesn't corrupt data. The feature flag ensures clean cutover: once SAST_PULL_MODE is set, push stops immediately.
**Risk**: Minimal. Brief overlap during rollout is harmless.

## Architecture Decision

**ADR-0244: Pull-Based SAST Scanning Over Push Dispatch**

**Context**: External SAST scans are dispatched via HTTP POST from Cloudflare Workers to hardcoded Hetzner VM IPs (`SCANNER_WORKERS` env var). This creates: (1) tight coupling to VM IPs as CF secrets, (2) silent scan loss when workers are unreachable, (3) manual IP management when scaling VMs.

**Decision**: Adopt a pull-based model where VMs self-schedule SAST work using the same proven pattern as `submission-scanner.js`. The platform becomes a work queue (DB-backed), VMs poll for pending scans, claim atomically, and dispatch to their co-located scanner-worker.

**Consequences**:
- VMs are self-contained: no inbound network access needed from the platform
- Scan loss eliminated: DB-backed queue with reaper for stuck scans
- Scaling is additive: new VMs just add `sast-scanner` to `ASSIGNED_SOURCES`
- `SCANNER_WORKERS` CF secret can be removed after phased rollout
- Minor increase in platform DB load from polling (mitigated by 30s cooldown and small result sets)

**Status**: Accepted
