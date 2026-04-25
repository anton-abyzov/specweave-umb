---
increment: 0719-cron-offload-stats-to-vm
title: "Cron Offload — Stats Compute to Hetzner VM — Tasks"
test_mode: TDD
---

# Tasks

STRICT TDD: each pair is RED → GREEN. Refactor folded inline.

## Phase 1 — CF write-only endpoints (deploy without traffic)

### T-001: RED — shared validators tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 (validation contract) | **Status**: [ ] pending
**Test Plan**:
- Given a valid QueueStats payload, `isQueueStatsPayload(body)` returns true
- Given a body missing `generatedAt`, returns false
- Given a body with `total: "string"`, returns false
- Given empty `{}`, returns false
- Test file: `src/app/api/v1/internal/_shared/__tests__/validators.test.ts`

### T-002: GREEN — implement validators
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
- File: `src/app/api/v1/internal/_shared/validators.ts`
- Export `isQueueStatsPayload`, `isPlatformStatsPayload`, `isListWarmupPayload`, `isSkillsCachePayload`, `isPublishersCachePayload` — each a type guard.

### T-003: RED — `/api/v1/internal/stats/queue` endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**Test Plan**:
- Given POST without X-Internal-Key → 401
- Given POST with wrong X-Internal-Key → 401
- Given POST with correct key + invalid body → 400
- Given POST with correct key + valid body → 200 + KV.put called with `submissions:stats-cache`
- Test file: `src/app/api/v1/internal/stats/queue/__tests__/route.test.ts`

### T-004: GREEN — implement queue stats endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
- File: `src/app/api/v1/internal/stats/queue/route.ts`
- Use shared validators.

### T-005: RED + GREEN — `/api/v1/internal/stats/platform`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
- Same shape as T-003/T-004 but for `platform:stats` KV key.

### T-006: RED + GREEN — `/api/v1/internal/stats/queue-list-warmup`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [ ] pending
- Accepts batched `[{key, value}, ...]` payload; writes each to KV.

### T-007: RED + GREEN — `/api/v1/internal/cache/skills`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
- KV key: `skills:cache`.

### T-008: RED + GREEN — `/api/v1/internal/cache/publishers`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
- KV key: `publishers:cache`.

### T-009: DEPLOY — Phase 1 (endpoints live, no traffic yet)
**User Story**: US-001 | **Satisfies ACs**: deployment | **Status**: [ ] pending
- `npm run build && npm run build:worker && npm run deploy`
- Smoke each endpoint via curl with valid + invalid payloads.

## Phase 2 — VM-side compute

### T-010: RED — `runStatsCompute` test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
**Test Plan**:
- Given a mocked Prisma client returning known counts → produces expected QueueStats payload
- Given a mocked fetch returning 200 → POST is invoked once per stat type with correct headers
- Given a mocked fetch returning 500 → error is logged, other stats still attempt
- Test file: `crawl-worker/__tests__/stats-compute.test.js`

### T-011: GREEN — implement compute functions for each payload
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
- File: `crawl-worker/sources/stats-compute.js`
- 5 compute functions; copy SQL from `src/lib/cron/*-refresh.ts` (Option B per plan).

### T-012: GREEN — implement POST helper with retry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
- 1 retry on 5xx, then log and continue. No infinite loop.

### T-013: GREEN — wire scheduler entry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending
- File: `crawl-worker/scheduler.js`
- Add `*/10 * * * *` entry that invokes `runStatsCompute(env)`.

### T-014: VERIFY — VM-local smoke (one-off run)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [ ] pending
- ssh into one VM, run `node sources/stats-compute.js --once`.
- Confirm 5 KV keys updated within 5s of each other.
- Curl `/api/v1/submissions/stats` from anywhere — confirm fresh data.

### T-015: DEPLOY — enable systemd timer on canary VM
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending
- Pick ONE of the 3 Hetzner VMs as canary.
- Enable systemd timer.
- Wait for 1 tick.

## Phase 3 — Cutover

### T-016: VERIFY — VM cron writes are landing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [ ] pending
- Watch one full hour. Confirm `submissions:stats-cache` `generatedAt` updates every 10 min within ±1 min.
- Confirm CF cron's old stats writes are also still happening (last-write-wins; no harm).

### T-017: REMOVE — block-1 stats chain from CF cron
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
- Edit `scripts/build-worker-entry.ts`:
  - Remove imports for `refreshPlatformStats`, `refreshQueueStats`, `warmQueueListCache`, `refreshSkillsCache`, `refreshPublishersCache`.
  - Remove the entire first `ctx.waitUntil(runWithWorkerEnv(env, async () => { ... }))` block (or trim to just DB prewarm if anything else needs it).
- Run `npm run build:worker` — confirm bundle size shrinks slightly and worker-with-queues.js no longer references the removed imports.

### T-018: DEPLOY — Phase 3 cutover
**User Story**: US-002 | **Satisfies ACs**: deployment | **Status**: [ ] pending
- `npm run deploy`
- Tail for 30 min: zero `[cron] queue stats refresh completed` logs (correct — they're not running on CF anymore). Confirm `[cron] enrichment completed` and recovery logs continue.

### T-019: VERIFY — 24h clean ticks + stats freshness
**User Story**: US-002, US-001 | **Satisfies ACs**: AC-US2-05, AC-US1-07 | **Status**: [ ] pending
- Set up monitoring (manual `wrangler tail` capture or a CF scheduled health check).
- 24h window: zero `Exceeded CPU Limit` for the `*/10` schedule.
- Stats `generatedAt` < 11 min for 99% of polls.

## Phase 4 — CPU band-aid removal

### T-020: REMOVE — `limits.cpu_ms: 60000` from wrangler.jsonc
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
- Edit `wrangler.jsonc` to remove the limits block (or replace with a comment pointing to 0719 closure).
- `npm run deploy`
- Watch 24h: still no `Exceeded CPU Limit`.

### T-021: CLOSE — full validation + sw:done
**User Story**: All | **Satisfies ACs**: closure | **Status**: [ ] pending
- All ACs marked complete.
- All tests green: `npx vitest run` + `npx playwright test tests/e2e/queue*.spec.ts`.
- 0713 hotfix increment can be referenced in closure summary.
- Run `/sw:done 0719`.

## Test pattern reference

Reuse 0713's pattern from `tests/integration/versions-compare-github.test.ts:1-48`:

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
const mockKvPut = vi.fn();
vi.mock("@opennextjs/cloudflare", () => ({
  getCloudflareContext: vi.fn().mockResolvedValue({
    env: {
      INTERNAL_BROADCAST_KEY: "test-key",
      SUBMISSIONS_KV: { put: mockKvPut },
    },
  }),
}));
```

VM-side tests use plain Vitest with `vi.mock` for Prisma + `globalThis.fetch`.
