# Implementation Plan: Hotfix: studio/search 502 — replace CF Worker self-fetch with direct call

## Overview

Surgical refactor of two Next.js route handlers in `vskill-platform`. Extract the data-search core of `skills/search/route.ts` (lines 206–304: edge+Postgres merge, blocklist enrichment, dedup, publisher join, paginate) into a new pure function `runSkillsSearch` at `src/lib/studio/run-skills-search.ts`. Both `studio/search` and `skills/search` routes call it directly. The studio route loses its `fetch()`/`AbortController`/timeout block entirely. Same Worker, same V8 isolate — no worker-to-self subrequest, which is the root cause of the production 502.

Single domain (Cloudflare Worker route + Vitest). Low complexity. ~15 tasks, single-day work.

## Architecture

### Components

- **`src/lib/studio/run-skills-search.ts` (NEW)** — pure async function `runSkillsSearch({ q, limit, offset, category?, respVersion? })` returning `{ results, total, offset, pagination, telemetry? }`. No `req`/`env`/Workers access. Imports the same `lib/search`, `lib/publisher`, `lib/search-index`, and `dedup` modules the skills/search route uses today.
- **`src/lib/studio/__tests__/run-skills-search.test.ts` (NEW)** — Vitest unit suite. Mocks `lib/search` + `lib/publisher`. Covers merge fallback, dedup, blocklist filter, publisher-timeout-degrade.
- **`src/app/api/v1/skills/search/route.ts` (MODIFIED)** — replaces lines 206–304 with `await runSkillsSearch({ q, limit, offset, category, respVersion })`. Reads telemetry from `out.telemetry` to populate `Server-Timing`. Workers Cache + KV `respVersion` lookup stay at the route layer.
- **`src/app/api/v1/studio/search/route.ts` (MODIFIED)** — drops `originFromRequest`, `UPSTREAM_TIMEOUT_MS`, `upstreamCtrl`, `upstreamTimedOut`, `req.signal` wiring, `fetch(...)` call, all upstream-status branches. Calls `runSkillsSearch` inside a `try/catch`; thrown exception → sanitized `502 search_unavailable`. Validates envelope shape after the call (defense-in-depth). Adds one `console.info("studio_search_direct:", { q_len, limit, offset, source })` log on the happy path for post-deploy observability.
- **`src/app/api/v1/studio/search/__tests__/route.test.ts` (MODIFIED)** — `vi.stubGlobal("fetch", ...)` → `vi.mock("@/lib/studio/run-skills-search")`. Assertions migrate from `mockFetch.mock.calls[0][0]` URL inspection to `runSkillsSearch.mock.calls[0][0]` payload inspection. Timeout test rewrites as "throws → sanitized 502".
- **`src/app/api/v1/studio/search/__tests__/route-perf.test.ts` (MODIFIED)** — same fetch-mock → function-mock migration. Perf assertion (route overhead in ms) remains valid.

### Data Flow

```
Client (vskill studio palette OR verified-skill.com/studio)
  │
  ▼
Studio route /api/v1/studio/search
  ├── parse params (q, limit, offset)
  ├── rate-limit check (LRU TokenBucket per IP)
  ├── LRU cache lookup (by [q, limit, offset] tuple)
  │     ├── HIT  → 200 + ETag-based 304 if If-None-Match
  │     └── MISS → continue
  ├── try {
  │     out = await runSkillsSearch({q, limit, offset})   ← DIRECT CALL (was: fetch(originFromRequest+/skills/search))
  │     validate envelope shape
  │     compute ETag, write LRU
  │     return 200 + headers
  │   } catch {
  │     return sanitized 502 search_unavailable
  │   }
  ▼
runSkillsSearch (lib/studio/run-skills-search.ts)
  ├── parallel edge + postgres search
  ├── merge + blocklist enrichment + dedup
  ├── publisher join (50ms soft-timeout)
  └── paginate slice → {results, total, offset, pagination, telemetry}

Skills route /api/v1/skills/search ALSO calls runSkillsSearch (DRY)
  ├── parse params + KV respVersion
  ├── Workers Cache read (CF native)
  ├── runSkillsSearch(...)
  └── Workers Cache write + headers (X-Search-Source, Server-Timing, etc.)
```

### Decisions (ADRs in spirit)

**D-001: Place `runSkillsSearch` in `src/lib/studio/`**
Existing modules in `src/lib/studio/` (`lru.ts`, `etag.ts`, `rate-limit.ts`) are imported by both `/api/v1/skills/*` and `/api/v1/studio/*` routes. The new module fits the same convention. Alternative: co-located in `src/app/api/v1/skills/search/runSkillsSearch.ts` — rejected because it makes the cross-route import path awkward and ties the lib to an app-router subtree.

**D-002: Pure function, no `req` access**
The route layer owns request parsing, rate-limit, cache, headers, and observability. The lib owns data orchestration. Keeps testing simple (no NextRequest mocks needed for the lib).

**D-003: Skill route also adopts `runSkillsSearch` (US-002)**
Avoids two implementations of the same merge/dedupe/enrichment logic that could drift. Skills/search tests stay green because the public envelope is invariant.

**D-004: Defense-in-depth envelope check stays in studio route**
The lib could throw a typed exception, but the existing studio route ALREADY guards against malformed envelopes (lines 203–211). Keeping that guard preserves the contract surface and provides an extra safety net even though `runSkillsSearch` has stronger return-type guarantees.

**D-005: Migrate tests from global fetch stub to vi.mock**
`vi.stubGlobal("fetch", mockFetch)` is a leaky pattern — any code under test that legitimately calls fetch (e.g. KV access) breaks. `vi.mock("@/lib/studio/run-skills-search")` is explicit, isolated, and survives future refactors.

## Test Plan

| Layer | Tests |
|---|---|
| Unit (lib) | `src/lib/studio/__tests__/run-skills-search.test.ts` — merge fallback, dedup, blocklist, publisher-timeout-degrade |
| Unit (route) | `src/app/api/v1/studio/search/__tests__/route.test.ts` — migrated mocks; rate-limit + cache + ETag + 502 sanitization invariant |
| Unit (perf) | `src/app/api/v1/studio/search/__tests__/route-perf.test.ts` — migrated mocks; throughput unchanged |
| Unit (skills) | All existing `src/app/api/v1/skills/search/__tests__/*.test.ts` — pass unchanged (envelope invariant) |
| Build | `npm run build` (Next.js) + `npm run build:worker` (OpenNext + wrangler) |
| Manual smoke | post-deploy curl `https://verified-skill.com/api/v1/studio/search?q=greet&limit=20` → 200 |
| Manual smoke | post-deploy: open vskill studio, ⌘⇧K, type "greet" — expect real results, no degraded banner |

## Rollout Plan

1. Local: TDD red-green-refactor through tasks T-001..T-013.
2. Local: `npm run build && npm run build:worker` → both clean.
3. Push to GitHub: `git push origin main`.
4. **Deploy** (user-triggered, NOT automated): `cd repositories/anton-abyzov/vskill-platform && npm run deploy`. The deploy is a destructive shared-system action; needs explicit user confirmation.
5. Post-deploy curl smoke (AC-US1-06).
6. Post-deploy CF Logs check: confirm `studio_search_direct:` log line appears.
7. Manual UI smoke: vskill studio palette shows real results.

## Rollback Plan

If post-deploy smoke fails:
1. `git revert <commit>` and redeploy. Ten-minute window.
2. Local studio already has graceful degradation (0741) — users keep filtered trending until rollback completes.
3. Worker bundle is monotonic; revert ships a smaller version of the same bundle.

## Open Questions

None — diagnosis is complete, fix is mechanical, contract is locked.

## References

- Production 502 verified: `curl https://verified-skill.com/api/v1/studio/search?q=greet&limit=20` → 502
- Underlying healthy: `curl https://verified-skill.com/api/v1/skills/search?q=greet&limit=20` → 200
- Contract: `.specweave/docs/contracts/studio-search-api-v1.md`
- Sibling fix (similar 502-masking, different route): increment 0746 (status: active)
- Local UX shipped: increment 0741 (vskill find-palette redesign with graceful 502 degradation)
- Explore agent reports captured in `/Users/antonabyzov/.claude/plans/staged-dreaming-badger.md`
