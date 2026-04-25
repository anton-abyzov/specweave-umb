---
increment: 0719-cron-offload-stats-to-vm
title: "Cron Offload — Stats Compute to Hetzner VM"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Cron Offload — Stats Compute to Hetzner VM

## Overview

Move heavy stats compute (platform-stats, queue-stats, queue-list-warmup, skills-cache, publishers-cache) from the verified-skill.com Cloudflare Worker cron handler onto the existing Hetzner ARM64 VMs that already run crawl-worker. CF retains a thin write-only internal endpoint per stat type that takes a pre-computed payload and writes it to KV. This permanently fixes the "Exceeded CPU Limit" starvation that the 0713 hotfix patched with a 60s budget bump.

## Context

During 0713 incident response we found that the CF cron handler was hitting per-event CPU limit on every tick because it ran 12+ tasks sequentially within the shared budget. Two of them (skill-update scan, outbox reconcile) were broken in-flight 0708 work consuming CPU on Prisma error stack-traces; we disabled those. But even after the disable + a CPU budget bump from 30s → 60s, the cumulative chain (DB prewarm + 5 stats refresh tasks + enrichment + 4 recovery tasks + 2 reconcile tasks running in parallel ctx.waitUntil blocks) still risked the budget on cold-start ticks.

The right architectural answer (per the user discussion on 2026-04-25) is to lift the heavy compute off CF entirely. CF is the wrong place to run multi-second aggregate queries against a 100k+ row Postgres table when we already operate dedicated VMs (3 ARM64 Hetzner instances) that have:

- Plenty of CPU headroom (currently sitting near-idle between crawl runs)
- Stable IPs (better for any future GitHub-rate-limit work, e.g., 0708 skill-update scanner)
- Persistent Prisma+Neon connection pooling (no cold start tax per tick)
- Existing scheduler infrastructure (systemd timer + Node.js)

CF retains everything that legitimately needs CF bindings (queue consumers, recovery cron that emits `SUBMISSION_QUEUE.send`, KV mutations from request context).

## User Stories

### US-001: VM computes platform + queue stats and writes them via internal CF endpoint (P1)
**Project**: vskill-platform

**As a** platform operator running the verified-skill.com cron pipeline
**I want** the heavy stats refresh to run on the Hetzner crawl-worker VMs
**So that** the CF Worker cron can never starve under CPU limits and so stats freshness is no longer hostage to whatever else CF cron is also doing

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A new `crawl-worker/sources/stats-compute.js` module exists that, when invoked by the existing crawl-worker scheduler, computes the same `QueueStats` payload that `_refreshQueueStatsImpl` produces today (total/active/published/rejected/blocked/onHold + avgScore + generatedAt + degraded flag).
- [ ] **AC-US1-02**: The same module also computes the `PlatformStats` payload that `refreshPlatformStats` produces (totalSkills, verifiedCount, certifiedCount, totalStars, etc. — full schema from `src/lib/cron/stats-refresh.ts`).
- [ ] **AC-US1-03**: After computing each payload, the module POSTs it to the corresponding internal CF endpoint with `X-Internal-Key: <INTERNAL_BROADCAST_KEY>` header.
- [ ] **AC-US1-04**: New CF endpoint `POST /api/v1/internal/stats/queue` validates `X-Internal-Key`, validates payload shape (rejects bodies missing required fields with 400), writes JSON to `SUBMISSIONS_KV` key `submissions:stats-cache`, returns `{ok: true, generatedAt}`.
- [ ] **AC-US1-05**: New CF endpoint `POST /api/v1/internal/stats/platform` does the same for `platform:stats` key.
- [ ] **AC-US1-06**: VM cron runs every 10 minutes via the existing systemd-timer-based scheduler. Schedule entry committed to `crawl-worker/scheduler.js` (or wherever current cadence is registered).
- [ ] **AC-US1-07**: After the VM cron is enabled and one tick has fired, `GET /api/v1/submissions/stats` returns fresh data (`degraded:false`, `generatedAt` < 11 min old) continuously for 24 hours.
- [ ] **AC-US1-08**: Existing 13 unit tests for `_refreshQueueStatsImpl` (from 0713) remain green — the function is no longer wired to cron but is still importable for ad-hoc use and future re-wiring.

### US-002: CF cron stops running the offloaded stats tasks (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** `scripts/build-worker-entry.ts` to no longer schedule `refreshPlatformStats`, `refreshQueueStats`, `warmQueueListCache`, `refreshSkillsCache`, `refreshPublishersCache` on the CF cron
**So that** the CF cron tick has CPU budget to spare for the recovery/reconcile/queue-consumer work that genuinely needs CF bindings

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `scripts/build-worker-entry.ts` no longer references `refreshPlatformStats`, `refreshQueueStats`, `warmQueueListCache`, `refreshSkillsCache`, or `refreshPublishersCache` in the `scheduled()` handler. Their imports are removed.
- [ ] **AC-US2-02**: The first `ctx.waitUntil` block (formerly the "stats refresh" chain) is either removed entirely or reduced to just the DB prewarm + recovery (whatever stays in CF).
- [ ] **AC-US2-03**: After deploy, `wrangler tail --format pretty` for one full 30-min window shows zero `[cron] platform stats refresh completed` and zero `[cron] queue stats refresh completed` lines (because they're not running on CF anymore).
- [ ] **AC-US2-04**: The same window shows `[cron] enrichment completed`, recovery logs, and `[cron] reconcile-active completed` — proving the remaining CF cron work runs to completion within budget.
- [ ] **AC-US2-05**: For 24 hours after deploy, no `Exceeded CPU Limit` log line appears for the `*/10` schedule.

### US-003: Restore CF Worker default CPU budget (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** to remove the `limits.cpu_ms: 60000` band-aid added in 0713
**So that** CF Worker config reflects the steady-state architecture and cost/performance accounting is honest

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Only AFTER 24 hours of clean cron ticks under the post-0719 architecture, `wrangler.jsonc` is modified to remove the `"limits": { "cpu_ms": 60000 }` entry.
- [ ] **AC-US3-02**: Deploy with the band-aid removed succeeds (no Exceeded CPU Limit returns) — proves the architectural fix holds.
- [ ] **AC-US3-03**: Comment explaining the 0713 history is retained adjacent to (or replaced by) a comment pointing to 0719 closure.

### US-004: Skills + publishers cache offload (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** `refreshSkillsCache` and `refreshPublishersCache` to also move to the VM
**So that** ALL stats/cache compute is consolidated in one place (the VM) and CF cron handles only what genuinely needs CF bindings

**Acceptance Criteria**:
- [ ] **AC-US4-01**: VM stats-compute module additionally produces the `skills-cache` payload (top-N skills by trust/stars/installs) and `publishers-cache` payload (top publishers ranked).
- [ ] **AC-US4-02**: New CF endpoints `POST /api/v1/internal/cache/skills` and `POST /api/v1/internal/cache/publishers` accept the payloads (same X-Internal-Key auth pattern) and write them to KV.
- [ ] **AC-US4-03**: After deploy, the existing skills-cache and publishers-cache KV reads (powering homepage, /publishers, etc.) continue to return current data with no contract changes.

### US-005: Queue list warmup offload (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** the `warmQueueListCache` payload (5 KV keys: `submissions:list:active::*`, `submissions:list:published::*`, etc.) to be precomputed on the VM
**So that** the /queue page's first-load latency stays instant (KV cache hit) without CF cron paying the compute cost

**Acceptance Criteria**:
- [ ] **AC-US5-01**: VM module computes the warm-up list payloads using the same dedup + sort logic that `warmQueueListCache` does today.
- [ ] **AC-US5-02**: New CF endpoint `POST /api/v1/internal/stats/queue-list-warmup` accepts a list of `{key, value}` pairs and writes each to KV (single endpoint, batched payload).
- [ ] **AC-US5-03**: After deploy, /queue first-page render time (TTFB) does not regress versus pre-0719 measurements.

## Functional Requirements

### FR-001: Internal write-only endpoint contract
Every new internal endpoint:
- Requires `X-Internal-Key` header matching `env.INTERNAL_BROADCAST_KEY`. 401 on mismatch.
- Validates payload shape (required fields, types). 400 on malformed body.
- Writes to KV. Returns `{ok: true, ...}` 200 on success, 500 on KV failure with `Retry-After`.
- Is NOT exposed in any public API documentation.
- Logs payload size + KV write outcome for observability.

### FR-002: VM scheduler reliability
The VM cron MUST be:
- Triggered by systemd timer (or equivalent) that survives VM reboot.
- Idempotent (safe to run twice in quick succession).
- Bounded (one run cannot block the next; if a run takes >10 min the next tick skips).

### FR-003: Failure observability
If the VM cron fails to publish stats for >30 min:
- The /queue page degraded-stats UI from 0713 surfaces the staleness.
- An ops alert fires (mechanism TBD — could be a CF endpoint that posts to Slack on stale-stats, or a VM-side health check).

## Success Criteria

- **CF cron health**: zero `Exceeded CPU Limit` for the `*/10` schedule across a 7-day window post-deploy.
- **Stats freshness**: `GET /api/v1/submissions/stats` `generatedAt` < 11 min for 99% of polls over 24 hours.
- **Cost**: zero incremental Hetzner cost (existing VMs absorb the workload). CF Workers metered usage decreases (one less heavy cron task per tick).

## Out of Scope

- Recovery cron, reconcile crons, queue consumers — they stay in CF (need bindings).
- 0708 skill-update scanner re-enable — handled in its own follow-up after schema migrates.
- Health-alert plumbing for VM cron silence (FR-003) — captured as a separate ticket if not already covered by an existing alarm.
- Schema changes — none.
- API contract changes for the public `/api/v1/submissions/stats` endpoint — none, just the source of the data.

## Dependencies

- Existing Hetzner VMs (3 ARM64 instances per `~/Projects/Obsidian/personal-docs/` reference)
- Existing crawl-worker repo with Prisma + Neon connection
- Existing `INTERNAL_BROADCAST_KEY` CF secret
- 0713 hotfix already in production (deploys `fbdc453`, `8241633`, `9ab7fed`)
