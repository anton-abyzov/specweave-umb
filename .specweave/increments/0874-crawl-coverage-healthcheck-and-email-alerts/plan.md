# Implementation Plan: Crawl coverage: health-check, email alerts, verification + GitHub breadth

**Repo**: `repositories/anton-abyzov/vskill-platform` · **Stack**: crawl-worker (zero-dep Node ESM, Docker on 3 Hetzner VMs, Vitest) + platform (Next.js 15 / Cloudflare Workers, Vitest). TDD red→green→refactor.

## Design

### Track A — silent-failure health check + email alerting (US-001)
The defect is *liveness ≠ correctness*: the regressed coverage number never leaves the VM and no detector compares a per-source total to a baseline.

- **Transport (load-bearing):** `crawl-worker/scheduler.js` `getHeartbeatSources()` adds `coverageTotal` per source (`= state.lastResult?.totalSkillsSh ?? state.lastResult?.upstreamTotal ?? null`). Widen `HeartbeatSource` (`src/app/api/v1/internal/vm-heartbeat/route.ts`) and `SourceObservation` (`src/lib/alerts/detectors.ts`) with `coverageTotal?: number|null`; persist into `SOURCE_OBS_KEY`. **Push, not pull** — CF Workers get a synthetic 403 fetching plain-HTTP VM IPs.
- **Detectors (pure):** `detectCoverageRegression` reads an upward-only HWM baseline from `ALERTS_KV` (`alerts:coverage:baseline:<source>`, mirroring `ORPHAN_BASELINE_KEY`); fires critical when `coverageTotal < absoluteFloor` OR `< baselineHWM*(1−dropPct)` (`dropPct=0.30`, `ALERT_COVERAGE_FLOOR_SKILLS_SH=20000`). `detectCoverageStale` (age > cooldown×1.5) and `detectCoverageRatioCollapse` (`submittedΔ/discoveredΔ<0.05` over 3 heartbeats). Register all three in `runAllDetectors`; add `DetectorThresholds`.
- **Email:** add `coverage-regression`|`coverage-stale`|`coverage-ratio-collapse` to `AlertKind` (`types.ts`), `KIND_SEVERITY` (regression=critical → `DIGEST_EXCLUDED_KINDS`), `QueueHealthAlertParams` union + `renderAlertBody` cases (`email.ts`), and `dispatchEmailForAlert` cases (`alerts-evaluator/route.ts`). Routes through existing `sendQueueHealthAlert`→SendGrid, deduped via `shouldFire/recordFired`. Runs in the existing `*/10` LIGHT cron.
- **Relabel:** `skillsShTotal`→`skillsShUpstreamReportedTotal`; add `skillsShAllTimeInstalls` + `skillsShDiscoveredThisRun`. Surface on `/coverage` and `GET /api/v1/admin/queue-health`.

### Track B — intake verification false-negatives (US-002)
The correct tri-state already exists at `crawl-worker/lib/repo-files.js:174`; bulk intake bypasses it.

- Authenticate: thread `cfEnv.GITHUB_TOKEN` through `cachedCheck → checkSkillMdExists → detectBranch` (`bulk/route.ts`, `src/lib/scanner.ts`).
- Tri-state `{exists, transient}`: `transient=true` on 403/429/5xx/timeout; `exists:false` only on a confirmed 404-on-all-branches. In `bulk/route.ts` Phase 2.5, transients re-enqueue via the existing 403 identity-defer path (counted `deferred`), never `status:"error"`.
- `headCache` memoizes only authoritative results (`exists:true` / confirmed 404) — never a transient false.
- Thread `{submitted,skipped,errors,deferred,aliased}` per source into `inline-submitter.js` + scheduler `lastResult`; expose `submit_rate`/`intake_notfound_rate`.

### Track C — GitHub breadth via size-bisection (US-003) — validated live
The 0861 bisection engine is structurally correct; it bisected the inert `created:` dimension. `size:` is a live continuous integer dimension (live: `size:0..200`=4,632, `size:42..42`=155, no single byte-value >~400 → no tiling holes for the SKILL.md corpus; bare `size:N` 422s so leaves must be `size:N..N`).

- `splitSizeRange(lo,hi)` → midpoint split, `null` when `lo===hi`; cap open-ended top (`[10001,null]`→`[10001,384000]`).
- `bisectWindow(win, countFn, {split})` — inject the split fn (default `splitDateWindow`, back-compatible); the iterative stack driver is reused verbatim.
- `expandPlanByBisection` keys off `shard.size` under `shardMode==="size-bisect"`; probe closure reused.
- `buildShardPlan` gains `"size-bisect"` mode + honors `config.sizeShards` (fix the dead param); `crawl()` gates expansion on the mode and wires `shardMode`/`adaptiveBisect` through `server.js` scheduler config.
- Persist the expanded leaf plan in the checkpoint (`crawl-state.js`) so the `shardMode`-keyed resume replays an identical plan across 120-min windows.
- Complementary: widen `github-graphql-check` (`LOOKBACK_MONTHS` 3→12, topic allow-list); keep `github-events` as-is; quarantine the unused dead `generateTimeShardedQueries` in `src/lib/crawler/github-discovery.ts`.

### Track A↔C bridge + security (US-004)
- Daily `filename:SKILL.md` ground-truth probe + `shardsZeroResultCount` detector + loud "date qualifier ineffective on code search" assertion (date-shard 0 while parent >0) — reuses Track A heartbeat plumbing.
- Secret hygiene: `.gitignore` `.env.vm*`/`.env.gcp-vm*`, `git rm --cached`, flag PATs for rotation. **Blocks the prod size-bisect flip (T-C06).**

## Rationale

- **Reuse over rebuild.** Email (SendGrid/`sendQueueHealthAlert`), the detector framework + `*/10` cron, the heartbeat push channel, and the bisection engine all exist and are battle-tested (0861). Adding fields + pure detectors + a split function is low-risk and fast; a new cron/email/discovery engine would be slower and riskier.
- **Push, not pull**, because the CF→VM plain-HTTP 403 is a documented dead end (`vm-heartbeat/route.ts`).
- **Upward-only HWM baseline** prevents the alarm self-healing: a regressed reading must never lower the baseline, or the drop becomes the new normal silently.
- **size: over language:** every `SKILL.md` is markdown, so `language:` is degenerate (`language:markdown`=the whole corpus). `size:` is the only working code-search dimension that subdivides; it bisects cleanly because it's continuous and the corpus has no single-value hot-spots over the cap. `path:` is held as a cold fallback.
- **Defer, don't drop.** A transient rate-limit is not evidence of absence; treating it as 404 is the root false-negative. The fix mirrors logic the worker already has (`repo-files.js`) — consistency, not novelty.
- **All-in-one** (Anton's call): the silent-failure visibility (A), the genuine funnel loss (B), and the breadth fix (C) share the coverage/alert plumbing and are best verified together — the new coverage detector (A/C bridge) is exactly what proves C worked.

## ADR
No new ADR required — this extends existing patterns (0861 dedup/alerts, heartbeat, bisection). If the size-bisect mode proves load-bearing, capture it as an ADR under `.specweave/docs/internal/architecture/adr/` during closure.

## Risks
- Size-bisect token budget under 2 tokens/VM → mitigated by checkpoint resume across windows (must persist the expanded plan).
- Committed PATs → rotation gates the prod flip; CI uses a fresh least-privilege token.
- Live-API CI test flakiness under GitHub secondary rate limits → gate on `GITHUB_TEST_TOKEN`, low request count, scheduled not per-PR-blocking.
