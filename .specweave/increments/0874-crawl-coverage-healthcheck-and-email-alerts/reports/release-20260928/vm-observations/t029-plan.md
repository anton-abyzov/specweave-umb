# T029: retain every registered VM's source observations

Planning only until T028's reviewed Worker rollout is safely observed. Root authorization/review and fresh ownership checks precede edits in a new isolated worktree from then-current main. Existing0874; no new increment, crawler restart, schedules, credentials, DB migration or synthetic heartbeat.

## Reproduced cause
Every authenticated VM heartbeat replaces the same SOURCE_OBS_KEY array. VM3's lastSeen advances at :17; another VM overwrites observations at :25, and a third writes its own sources at :46. Source histories/coverage baselines are also keyed only by source name, so simply combining arrays would mix unrelated submission-scanner counters. Current production evidence confirms fresh VM3 lastSeen and successful natural HTTP200 heartbeat, but the readback contains only another VM's sources. Tests must reproduce sequential/concurrent heartbeat overwrite and duplicate-source baseline interference first.

## Exact files (10)
- src/lib/alerts/source-observations.ts (new)
- src/lib/alerts/__tests__/source-observations.test.ts (new)
- src/lib/alerts/detectors.ts
- src/lib/alerts/__tests__/detectors.test.ts
- src/app/api/v1/internal/vm-heartbeat/route.ts
- src/app/api/v1/internal/vm-heartbeat/__tests__/route.test.ts
- src/app/api/v1/internal/alerts-evaluator/route.ts
- src/app/api/v1/internal/alerts-evaluator/__tests__/route.test.ts
- src/app/api/v1/admin/queue-health/route.ts
- src/app/api/v1/admin/queue-health/__tests__/route.test.ts

## Contract
1. Keep the existing aggregate write for compatibility; add a separate stable KV key per registered VM: SOURCE_OBS_KEY + ':vm:' + encoded IP. No read/modify/write of a shared array. Persist a version1 envelope with registered VM identity, server receive timestamp and safe observations. Same one-hour source TTL, unchanged ten-minute VM lastSeen TTL. Source identity comes from the server's validated registered IP, not an incoming per-source vmId.
2. Shared reader loads only keys named by HETZNER_VM_IPS, bounded/deduplicated configured identities. Validate schema, matching VM identity, source name/count, finite numeric metadata, booleans/closed sweep values, and bounded serialized size. New records contain no raw paths, repositories, headers, tokens or arbitrary payloads; free-form lastError is represented as a generic reported-error marker while existing legacy aggregate behavior stays unchanged.
3. Return separate observations per (VM, source), never counter sums or latest-arrival replacement. SourceObservation gains optional vmId. A stable identity helper keys dark-history, coverage baseline, ratio-history and per-source alert dedup using both fields. Keep the original source name for display and source-specific interpretation. Admin coverage rows expose vmId so duplicate names remain distinguishable.
4. Existing unscoped observations retain their exact historical key names and behavior. Use the old aggregate only when every configured per-VM key is genuinely absent (or configuration is absent), not when a read failed or a scoped record is malformed; once scoped records exist, never use aggregate data to fill a missing VM or assign a source to an unknown VM. Keep existing unscoped history/baselines untouched; new scoped histories start independently rather than inheriting a mixed legacy baseline.
5. Preserve server-clock receivedAt and stale observations until their existing TTL expires. Never fabricate a fresh observation for a missing/stale VM. Existing per-VM freshness/deadman checks continue to read lastSeen unchanged, so healthy VM observations cannot hide an absent VM. Existing detector thresholds, cooldowns and notification policy stay unchanged.

## Tests and release evidence
Interleaved/concurrent VM writes retain all VM arrays; duplicate source names maintain separate histories/baselines/alert keys; one VM failure cannot be erased by another's healthy arrival. Cover stale/missing VM, malformed/oversized records, rejected unregistered/forged vmId, expiry, mixed scoped/legacy transition and fallback, reader integration in evaluator/admin, and preserved false/incomplete coverage values. Run focused suites, full platform, Node22 Worker build, required CI and independent root review. Worker-only rollout. Read exact per-VM KV records after real scheduled heartbeats, including sweepId/progress plus unchanged failure counters; no manual production heartbeat or payload replay.
