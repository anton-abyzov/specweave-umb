# Implementation Plan: Crawler Pipeline Reliability and Guardrails

## Overview

Five targeted fixes to the crawl-worker discovery pipeline plus a health monitoring layer. All changes are in the crawl-worker directory (`repositories/anton-abyzov/vskill-platform/crawl-worker/`), using Node.js ESM with plain JavaScript. No new dependencies, no database changes, no platform API changes.

The design introduces a shared `lib/crawl-state.js` utility for file-based state persistence, reused by github-sharded and skills-sh for checkpoint/resume. The InlineSubmitter fix is a self-contained change to the batching strategy. The SAST scanner fix is a 10-line pre-flight check. Metrics collection is layered into the existing scheduler state.

## Architecture

### Component Diagram

```
                     ┌─────────────────────────────────────────┐
                     │           crawl-worker (Docker)          │
                     │                                          │
                     │  server.js                               │
                     │    GET /health                           │
                     │    GET /status                           │
                     │    GET /metrics  ◄── NEW                 │
                     │    POST /crawl                           │
                     │                                          │
                     │  scheduler.js                            │
                     │    runSourceLoop()                       │
                     │    ├── metrics accumulation  ◄── NEW     │
                     │    ├── consecutive failure alerts  ◄──   │
                     │    └── dedup ratio logging  ◄── NEW      │
                     │                                          │
                     │  lib/                                    │
                     │    crawl-state.js  ◄── NEW               │
                     │    inline-submitter.js  ◄── FIX          │
                     │                                          │
                     │  sources/                                │
                     │    github-sharded.js  ◄── CHECKPOINT     │
                     │    skills-sh.js  ◄── RESUME              │
                     │    sast-scanner.js  ◄── HEALTH CHECK     │
                     │                                          │
                     │  /tmp/crawl-state/  (Docker volume)      │
                     │    github-sharded.json                   │
                     │    skills-sh.json                        │
                     └─────────────────────────────────────────┘
```

### Components

- **lib/crawl-state.js** (NEW): Shared state persistence utility with `loadState(sourceName)`, `saveState(sourceName, data)`, `clearState(sourceName)`. Handles staleness checks, directory creation, and JSON serialization. Configurable via `CRAWL_STATE_DIR` env var (default `/tmp/crawl-state/`).

- **lib/inline-submitter.js** (FIX): Change `_flush()` from destructive splice-first to copy-first-splice-on-success. Add retry tracking per batch with `maxRetryCount` (default 2). Add `totalLost` counter.

- **sources/github-sharded.js** (MODIFY): Load checkpoint on start, save after each completed shard, clear on full completion. Skip already-processed shards. Restore seenRepos from checkpoint.

- **sources/skills-sh.js** (MODIFY): Load last page from state on start, save after each page, clear when reaching the end.

- **sources/sast-scanner.js** (MODIFY): Add `checkScannerHealth()` as first step before `fetchPending()`. Return early if scanner-worker is unreachable.

- **scheduler.js** (MODIFY): Add `sourceMetrics` Map alongside existing `sourceStates`. Accumulate per-run results (totalDiscovered, totalSubmitted, etc). Add alert logging on consecutive failures exceeding threshold. Add dedup ratio logging.

- **server.js** (MODIFY): Add `GET /metrics` endpoint that returns `getSourceMetrics()` from scheduler.

### Data Flow

#### Checkpoint/Resume (github-sharded)

```
crawl() start
  │
  ├── loadState("github-sharded")
  │     └── exists & fresh? → restore lastShardIndex + seenRepos
  │     └── stale/missing? → start from index 0, empty seenRepos
  │
  ├── for (shard of shardPlan.slice(startIndex))
  │     ├── process shard
  │     ├── saveState("github-sharded", { lastShardIndex, seenRepos })
  │     └── continue
  │
  └── all shards done?
        └── clearState("github-sharded")
```

#### Page Resume (skills-sh)

```
crawl() start
  │
  ├── loadState("skills-sh")
  │     └── exists & fresh? → set startPage = state.lastPage + 1
  │     └── stale/missing? → startPage = 1
  │
  ├── for (page = startPage; ...)
  │     ├── fetch page
  │     ├── saveState("skills-sh", { lastPage: page })
  │     └── if (hasMore === false) → clearState("skills-sh")
  │
  └── timeout? → state file persists for next cycle
```

#### Safe Batching (InlineSubmitter)

```
_flush()
  │
  ├── batch = buffer.slice(0, batchSize)      ← COPY, don't remove
  ├── try submitBatch(batch)
  │     ├── success → buffer.splice(0, batch.length) + clear retries
  │     └── failure → increment retryCount for batch
  │           ├── retryCount <= maxRetries → leave in buffer
  │           └── retryCount > maxRetries → splice + log as lost
  └── return
```

### State File Schema

**github-sharded.json**:
```
lastShardIndex   number   Index of last completed shard (0-based)
seenRepos        string[] Array of "owner/repo:path" dedup keys
updatedAt        string   ISO 8601 timestamp
shardMode        string   "size-only" | "size-date" | "full"
totalShards      number   Total shard count for this mode
```

**skills-sh.json**:
```
lastPage         number   Last successfully crawled page number
updatedAt        string   ISO 8601 timestamp
```

### API Contracts

**GET /metrics** (NEW, no auth required):
```json
{
  "uptime": 86400,
  "sources": {
    "github-sharded": {
      "totalRuns": 15,
      "totalDiscovered": 4500,
      "totalSubmitted": 3200,
      "totalErrors": 2,
      "consecutiveErrors": 0,
      "lastDurationMs": 7200000,
      "averageDurationMs": 6800000,
      "lastDedupRatio": 0.72,
      "lastRunAt": "2026-03-02T12:00:00Z",
      "status": "cooldown"
    }
  },
  "alerts": []
}
```

## Technology Stack

- **Runtime**: Node.js 22+ (existing)
- **Language**: Plain JavaScript ESM (existing)
- **Test Runner**: node:test + assert/strict (existing)
- **State Persistence**: JSON files on disk (new, via `/tmp/crawl-state/`)
- **New Dependencies**: None

**Architecture Decisions**:

1. **File-based state over in-memory**: Docker containers restart on crashes. File-based state at `/tmp/crawl-state/` survives scheduler timeout (container stays up) but resets on container restart (intentional — stale state is worse than fresh start). The `/tmp` dir is container-local, no volume mount needed for this use case since we only need to survive timeouts within a running container.

2. **24-hour staleness threshold**: Checkpoint files older than 24h are ignored. This prevents resuming from stale state after a long downtime where the GitHub index has shifted. The 24h window is generous enough to cover multiple scheduler timeout-restart cycles.

3. **Copy-first batching over transactional outbox**: The InlineSubmitter fix uses a simple copy-before-splice pattern. A transactional outbox (write to disk, submit, delete from disk) would be more durable but adds complexity and I/O overhead for a problem that only manifests on timeout. The copy-first pattern handles 99% of failure cases with zero I/O overhead.

4. **In-memory metrics over persistent storage**: Metrics reset on restart. This is acceptable because we only need to detect degradation within a running process. External monitoring can scrape `/metrics` periodically. Persistent metrics would require either a file-based store or an external database, neither of which is justified at this scale.

5. **Health check before claim (not before dispatch)**: The SAST scanner checks health once at the start of the crawl function, not per-scan. If the scanner-worker goes down mid-run, individual dispatch failures are already handled. The pre-flight check prevents the common case: entire run claiming N scans that all fail.

## Implementation Phases

### Phase 1: Foundation (lib/crawl-state.js + InlineSubmitter fix)
These are prerequisites for Phases 2-3 and have no dependencies.
1. Create `lib/crawl-state.js` with loadState/saveState/clearState
2. Fix `lib/inline-submitter.js` splice-before-confirm bug
3. Tests for both

### Phase 2: Source Fixes (github-sharded, skills-sh, sast-scanner)
Each source fix is independent and can be done in any order.
4. Add checkpoint/resume to github-sharded.js
5. Add page resumption to skills-sh.js
6. Add pre-flight health check to sast-scanner.js
7. Tests for all three

### Phase 3: Monitoring (scheduler metrics + /metrics endpoint)
Depends on scheduler understanding from Phase 2 work.
8. Add metrics accumulation to scheduler.js
9. Add /metrics endpoint to server.js
10. Add docker-compose volume mount for crawl-state dir
11. Tests for metrics

## Testing Strategy

All tests use `node:test` + `assert/strict`, matching existing crawl-worker test patterns.

### Unit Tests
- **lib/crawl-state.js**: loadState/saveState/clearState with fresh, stale, missing, and corrupted files. Use a temp directory per test.
- **lib/inline-submitter.js**: Verify batch is not lost on failure, verify retry count, verify totalLost tracking, verify buffer integrity after mixed success/failure flushes.
- **sources/sast-scanner.js**: Mock fetch to simulate health check success/failure. Verify no claims are made when health check fails. Verify stats object includes healthCheckFailed field.

### Integration Tests
- **sources/github-sharded.js**: Mock HTTP server (existing pattern from TC-018/019/020). Test checkpoint save/load across two crawl() invocations. Test stale checkpoint ignored. Test clean slate after full completion.
- **sources/skills-sh.js**: Mock HTTP server. Test page resume from saved state. Test state cleared on last page.

### Metrics Tests
- **scheduler.js**: Test metrics accumulation after mock source runs. Test consecutive failure alert threshold. Test dedup ratio logging.
- **server.js**: Test GET /metrics returns expected JSON shape.

## Technical Challenges

### Challenge 1: seenRepos Set Serialization
The `seenRepos` Set in github-sharded can grow to 10,000+ entries. Serializing/deserializing to JSON on every shard completion adds I/O.
**Solution**: Save every N shards (e.g., every 5) instead of every shard. Also, convert Set to Array for JSON serialization and back on load. At 10K entries with ~50 chars each, the file is ~500KB — well within reasonable disk I/O.
**Risk**: If the process dies between saves, up to N shards of progress is lost. Acceptable since this is a discovery crawler and repos will be re-discovered.

### Challenge 2: Concurrent State File Access
Multiple scheduler loops run concurrently. Each source has its own state file, so there's no contention. However, if two instances of the same source somehow ran (bug), they could corrupt the file.
**Solution**: Each state file is keyed by source name. The scheduler guarantees one loop per source. No locking needed.

### Challenge 3: InlineSubmitter Retry Tracking
The current buffer is a flat array. Tracking per-batch retry counts requires either annotating items or maintaining a separate retry counter.
**Solution**: Track retries as a counter on the InlineSubmitter instance (`_currentBatchRetries`). Reset to 0 on success, increment on failure. When the same batch (identified by buffer head position) fails `maxRetryCount` times, splice it and log as lost. This avoids modifying the buffer item structure.

### Challenge 4: Docker Volume for State Files
The crawl-worker container uses `/tmp/crawl-state/` which is ephemeral. Container restarts wipe it.
**Solution**: Add a named Docker volume for `/tmp/crawl-state/` in docker-compose.yml. This persists across container restarts but not across `docker compose down --volumes`. This is the right behavior: explicit teardown clears state, normal restarts preserve it.
