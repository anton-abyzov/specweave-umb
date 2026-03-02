# Implementation Plan: Crawl Pipeline Throughput Optimization

## Overview

Six targeted changes to the vskill-platform submission pipeline that remove throughput bottlenecks. All changes are config-value edits or small refactors to existing files -- no new database tables, no schema migrations, no new API endpoints. The work splits into two phases: P1 (latency + concurrency + rate-limit headroom) and P2 (feature flag + dedup improvements).

## Architecture

### Current Data Flow

```
Crawlers (VMs) ─► POST /submissions/bulk ─► createSubmission() ─► DB (RECEIVED)
                                           └─► SUBMISSION_QUEUE.send()
                                                    │
                                    ┌───────────────┘
                                    ▼
                            CF Queue consumer
                          (max_concurrency=3,
                           BATCH_CONCURRENCY=1)
                                    │
                                    ▼
                           processSubmission()

VMs also poll:  GET /internal/pending-submissions
                (WHERE updatedAt < 5 min ago)
                        │
                        ▼
              submission-scanner.js
              (claims + processes end-to-end)
```

### Target Data Flow

```
Crawlers (VMs) ─► POST /submissions/bulk ─► createSubmission() ─► DB (RECEIVED)
                                           └─► (SKIP_QUEUE_ENQUEUE=true → skip)

VMs poll:  GET /internal/pending-submissions
           (WHERE updatedAt < 30 seconds ago)    ◄── 10x faster pickup
                        │
                        ▼
              submission-scanner.js
              (13 VMs × 20 workers = 260 slots)

CF Queue consumer (fallback, SKIP_QUEUE_ENQUEUE=false):
  max_concurrency=10, BATCH_CONCURRENCY=3
  TokenRotator distributes across 3-5 PATs
```

### Components Modified

| Component | File | Change |
|-----------|------|--------|
| pending-submissions endpoint | `src/app/api/v1/internal/pending-submissions/route.ts` | 5min → 30s (configurable via `PENDING_AGE_SECONDS`) |
| CF Queue consumer | `src/lib/queue/consumer.ts` | `BATCH_CONCURRENCY` 1→3, multi-token rotation |
| Queue config | `wrangler.jsonc` | `max_concurrency` 3→10 |
| Bulk endpoint | `src/app/api/v1/submissions/bulk/route.ts` | `SKIP_QUEUE_ENQUEUE` flag |
| Single endpoint | `src/app/api/v1/submissions/route.ts` | `SKIP_QUEUE_ENQUEUE` flag |
| Enqueue endpoint | `src/app/api/v1/internal/enqueue-submissions/route.ts` | `SKIP_QUEUE_ENQUEUE` flag |
| Dedup logic | `src/lib/submission-dedup.ts` | Per-state staleness, rejected re-scan |
| New utility | `src/lib/token-rotator.ts` | Round-robin token rotation class |
| Type declarations | `src/lib/env.d.ts` | `SKIP_QUEUE_ENQUEUE`, `PENDING_AGE_SECONDS` |

### New Component: TokenRotator

```
src/lib/token-rotator.ts
```

A stateless round-robin utility. No external dependencies.

```typescript
export class TokenRotator {
  private tokens: string[];
  private index: number = 0;

  constructor(tokensCsv: string) {
    this.tokens = tokensCsv.split(",").map(t => t.trim()).filter(Boolean);
    if (this.tokens.length === 0) throw new Error("No valid tokens");
  }

  next(): string {
    const token = this.tokens[this.index % this.tokens.length];
    this.index++;
    return token;
  }

  get count(): number {
    return this.tokens.length;
  }
}
```

Design decisions:
- **Stateless rotation** (no rate-limit tracking): keeps the class trivial. Rate limits are per-token-per-hour; with 3-5 tokens and round-robin, each token gets roughly equal load. Adding rate-limit awareness would require shared state (KV or DO), which is overkill given the token count.
- **Single class for both consumer and VMs**: the crawl-worker already has its own `TokenRotator` in JS. This TypeScript version is for the CF Worker consumer only. No code sharing needed -- the two runtimes (Node.js ESM vs CF Worker) have different constraints.

### Dedup Refactor: Per-State Staleness

Current `isStale(updatedAt: Date)` uses a single `DEDUP_STALE_HOURS` (72h default).

Refactored to `isStale(updatedAt: Date, state: string)` with per-state env vars:

| State | Env Var | Default | Rationale |
|-------|---------|---------|-----------|
| PUBLISHED | `DEDUP_STALE_PUBLISHED_HOURS` | 24 | Published skills should be re-scanned daily for security updates |
| REJECTED / TIER1_FAILED / DEQUEUED | `DEDUP_STALE_REJECTED_HOURS` | 48 | Transient failures (rate limits, flaky scans) deserve retry |
| BLOCKED | (never stale) | -- | Admin-blocked is permanent |
| All other | `DEDUP_STALE_DEFAULT_HOURS` | 72 | Fallback for unclassified states |

Backward compatibility: if `DEDUP_STALE_HOURS` is set but per-state vars are not, it is used as the default for all states.

### SKIP_QUEUE_ENQUEUE Feature Flag

| Env Var | Type | Default | Location |
|---------|------|---------|----------|
| `SKIP_QUEUE_ENQUEUE` | string (truthy/falsy) | `"true"` | Cloudflare secret |

Applied in three endpoints:
1. `POST /api/v1/submissions` -- both batch (`sendBatch`) and single (`send`) paths
2. `POST /api/v1/submissions/bulk` -- the `SUBMISSION_QUEUE.send()` call
3. `POST /api/v1/internal/enqueue-submissions` -- early return with success when flag is set

When the flag is truthy (default), submissions stay in RECEIVED state in the DB. VMs poll `pending-submissions` (now with 30s age filter) and pick them up. If VMs go down, an operator sets `SKIP_QUEUE_ENQUEUE=""` via `wrangler secret put` to re-enable the CF Queue path.

### Env Declarations (env.d.ts)

Two new optional bindings to add:

```typescript
SKIP_QUEUE_ENQUEUE?: string;
PENDING_AGE_SECONDS?: string;
```

`GITHUB_TOKENS` is already declared.

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15, Cloudflare Workers
- **Libraries**: No new dependencies
- **Tools**: `wrangler secret put` for deploying env var changes

**Architecture Decisions**:
- **No new DB tables or columns**: All configuration via env vars. Dedup staleness is computed at query time from existing `updatedAt` fields. This avoids migrations and keeps the change set minimal.
- **TokenRotator as a standalone file**: Rather than adding to an existing module, a new `src/lib/token-rotator.ts` keeps the utility isolated and testable. The crawl-worker's JS rotator stays separate -- different runtimes, no benefit to sharing.
- **Feature flag over code deletion**: `SKIP_QUEUE_ENQUEUE` keeps the CF Queue path intact. If VMs fail, the flag can be toggled without a redeploy (only `wrangler secret put` + wait for propagation).

## Implementation Phases

### Phase 1: Latency + Concurrency (P1 -- US-001, US-002, US-003)

1. **pending-submissions age filter** -- change `5 * 60 * 1000` to `parseInt(env.PENDING_AGE_SECONDS || "30") * 1000`. Since this endpoint runs in the Next.js request context (not the queue worker), `PENDING_AGE_SECONDS` is read from CF env via `getCloudflareContext`.
2. **wrangler.jsonc concurrency** -- `max_concurrency: 3 → 10`.
3. **BATCH_CONCURRENCY** -- `1 → 3` in `consumer.ts`.
4. **TokenRotator** -- new `src/lib/token-rotator.ts`. Consumer instantiates it from `env.GITHUB_TOKENS ?? env.GITHUB_TOKEN ?? ""` and calls `rotator.next()` per submission.

### Phase 2: Feature Flag + Dedup (P2 -- US-004, US-005, US-006)

5. **SKIP_QUEUE_ENQUEUE** -- guard `SUBMISSION_QUEUE.send()` / `sendBatch()` calls in all three endpoints behind `!env.SKIP_QUEUE_ENQUEUE` or `cfEnv.SKIP_QUEUE_ENQUEUE !== "true"`.
6. **Per-state staleness** -- refactor `isStale()` signature, add per-state env var reads.
7. **Rejected re-scan** -- modify `checkSubmissionDedup` and `checkSubmissionDedupBatch` to return `kind: "new"` for stale rejected submissions instead of `kind: "rejected"`.

## Testing Strategy

- **Unit tests** for `TokenRotator` (round-robin, single token, empty input).
- **Unit tests** for refactored `isStale(updatedAt, state)` with per-state thresholds.
- **Unit tests** for `checkSubmissionDedup` / `checkSubmissionDedupBatch` with rejected+stale path.
- **Integration-level** verification that bulk endpoint respects `SKIP_QUEUE_ENQUEUE`.
- **Manual verification** post-deploy: check VM pickup latency via scan logs, confirm CF Queue metrics show increased concurrency when enabled.

## Technical Challenges

### Challenge 1: PENDING_AGE_SECONDS in CF Worker context

The `pending-submissions` endpoint runs as a Next.js route handler on CF Workers. Environment variables are accessed via `getCloudflareContext()`, not `process.env`. The age seconds value must be read from `env.PENDING_AGE_SECONDS` (CF binding), not `process.env`.

**Solution**: Read from CF env with fallback: `const ageMs = parseInt(env.PENDING_AGE_SECONDS || "30", 10) * 1000`.

**Risk**: Low. The endpoint already reads `env.INTERNAL_BROADCAST_KEY` the same way.

### Challenge 2: Race between SKIP_QUEUE_ENQUEUE check and secret propagation

When an operator changes `SKIP_QUEUE_ENQUEUE` via `wrangler secret put`, the change may take up to 30 seconds to propagate to all CF Worker isolates. During this window, some requests may still enqueue to the CF Queue.

**Solution**: Acceptable. The CF Queue consumer is idempotent -- duplicate processing is handled by `processSubmission`'s dedup logic. No data corruption risk.

**Risk**: Minimal operational confusion during the propagation window.

### Challenge 3: Increased DB pressure from BATCH_CONCURRENCY=3

Each `processSubmission` makes 2-4 GitHub API calls and multiple DB writes. With `max_concurrency=10` and `BATCH_CONCURRENCY=3`, up to 30 submissions may hit the DB simultaneously via the CF Queue path.

**Solution**: The CF Queue path is the *fallback* (SKIP_QUEUE_ENQUEUE defaults to true). When enabled, the existing circuit breaker and DB connection pooling (Neon with Prisma Accelerate) handle the load. If the circuit trips, the consumer retries messages (max 3 retries with 60s delay).

**Risk**: Medium if VMs go down and all load shifts to CF Queue. Mitigation: monitor circuit breaker metrics and reduce `max_concurrency` if needed.
