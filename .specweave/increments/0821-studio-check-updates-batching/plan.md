# Plan: Studio Check-Updates Batching

## Context

`vskill/src/eval-ui/src/api.ts` exposes two functions that POST to `/api/v1/skills/check-updates` from the Skill Studio frontend:

1. `api.checkSkillUpdates(skillIds)` — line 920 — used by the SSE-fallback reconciler in `useSkillUpdates`.
2. `api.resolveInstalledSkillIds(skills)` — line 987 — used by `StudioContext` to resolve UUID/slug for the SSE subscription filter.

Both build a single request body `{skills: [{name, currentVersion}, ...]}` containing every input. The platform handler at `vskill-platform/src/app/api/v1/skills/check-updates/route.ts:139` rejects any request with `>100` skills via HTTP 400 `{"error":"Maximum 100 skills per request"}`. Studios with >100 installed skills (real for power users — observed at 230) hit the cap on every reconcile cycle.

## Decision

Chunk client-side. The platform cap is intentional protection (rate-limit + KV cache key bloat); raising it punishes the wrong layer and doesn't fix legacy clients. A small file-internal helper plus two call-site rewrites is sufficient.

## Architecture

- **No new files.** All changes land in `src/eval-ui/src/api.ts` and its colocated test `src/eval-ui/src/api.test.ts`.
- **Module-private helper** `chunkArray<T>(arr, size)` declared near the top of `api.ts`, alongside a `CHECK_UPDATES_BATCH_SIZE = 100` constant whose comment names the platform file/line it mirrors (`vskill-platform/src/app/api/v1/skills/check-updates/route.ts:139`).
- **Per-chunk fetches** run via `Promise.all`. Each chunk's success/failure is isolated using `Promise.allSettled`-style handling inside the function (catch + return empty for that chunk), so one failure can't reject the whole batch.
- **Result merge order** preserves input order by concatenating chunk results in chunk order.

## Why not platform-side?

The platform `MAX_BATCH_SIZE` exists to:
- bound KV cache key length (`buildCacheKey(parsed)` hashes the input list),
- bound DB `IN (...)` query size,
- bound rate-limit-bucket consumption per request (currently 600/hr/IP).

Raising it would shift the same problem to those subsystems. Client-side batching is the textbook fix.

## Why not abort + retry on 400?

A 400 from the cap is deterministic — retrying doesn't help. Detecting it client-side and chunking on retry would work but doubles latency on every reconcile. Pre-chunking is strictly cheaper and simpler.

## Why not CLI (`src/api/client.ts`) too?

Out of scope per spec. The CLI path runs at `vskill outdated` cadence (interactive, infrequent) against ≤100 skills today. If/when a user has >100 skills installed AND runs `vskill outdated`, we'll batch that path separately — it has different timeout/abort wiring (per-call AbortController + 15s timeout) that needs its own thought.

## Risks

- **Browser HTTP/2 multiplexing assumption** — Cloudflare serves HTTP/2 to modern browsers, so 3 concurrent requests share one socket. On HTTP/1.1 the per-host concurrency limit (~6) still leaves headroom for typical scales.
- **Per-chunk graceful degradation may mask transient errors** — same risk exists today for the single-call path. Logging is already gated by `SKILL_UPDATE_DEBUG=false`. No new logging added.
- **Cache cardinality on the platform** — `buildCacheKey` is content-hashed, so chunked requests produce distinct cache entries. First reload populates 3 entries instead of 1; subsequent reloads hit cache. Acceptable.

## Test Strategy

Vitest, fetch-mocked. Five new tests covering:
1. `checkSkillUpdates` 100-element single fetch (boundary).
2. `checkSkillUpdates` 230-element three fetches (chunking).
3. `checkSkillUpdates` first-chunk-rejects partial degradation.
4. `resolveInstalledSkillIds` 230-element three fetches with order preservation.
5. `chunkArray` helper edge cases (empty, exact, < size, N×size, 230).

Existing tests in `api.test.ts` for the single-call path stay green (no behavioral change for ≤100 inputs).

## Manual Verification Steps

1. Confirm reproduction first: open Studio devtools network tab, filter for `check-updates`, observe HTTP 400 response with `{"error":"Maximum 100 skills per request"}`.
2. Apply fix, run `npx vitest run src/eval-ui/src/api.test.ts`, then full `npx vitest run`.
3. Rebuild the Studio bundle (the eval-server serves a pre-built bundle per memory `project_vskill_studio_runtime.md`): follow whatever build step is wired in vskill (`npm run build` or equivalent).
4. Restart `vskill studio`, reload browser, confirm:
   - 2-3 `check-updates` requests in network tab, all 200.
   - Console no longer shows the 400 error.
   - Detail panel for an installed skill shows tracking state correctly.

## Rollback

Revert the api.ts diff. Single-file change, no schema/proxy/protocol coupling.
