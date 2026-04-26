# Implementation Plan: P0 hotfix — Studio search 502 (Cloudflare CDN loopback)

## Overview

A surgical transport swap inside `vskill-platform/src/app/api/v1/studio/search/route.ts`. When the Cloudflare context exposes `env.WORKER_SELF_REFERENCE` (a service binding to the same worker), dispatch the upstream fetch via that binding instead of `globalThis.fetch`. When it doesn't (dev, vitest, jest), keep using `globalThis.fetch`. Mirror the exact pattern that `src/lib/skill-update/publish-client.ts:60-65` ships in production today (per commit `665a63c`).

## Design

### Affected files (production code)

| # | File | Lines | Change |
|---|---|---|---|
| 1 | `vskill-platform/src/app/api/v1/studio/search/route.ts` | ~14, 133-153, top of GET | Add CF context lookup + service-binding-first fetch dispatch |

### Affected files (tests)

| # | File | Change |
|---|---|---|
| 2 | `vskill-platform/src/app/api/v1/studio/search/__tests__/route.test.ts` (or co-located test file) | Add 2 tests: (a) uses binding when present, (b) falls back to globalThis.fetch when absent |

(Existing tests for cache, ETag, rate-limit, timeout, malformed envelope, etc. remain green — we only swap the dispatch mechanism.)

### Code shape (target)

```typescript
type ServiceBinding = { fetch: (req: Request | string, init?: RequestInit) => Promise<Response> };

async function getSelfBinding(): Promise<ServiceBinding | null> {
  try {
    const { getCloudflareContext } = await import("@opennextjs/cloudflare");
    const ctx = await getCloudflareContext({ async: true });
    const env = (ctx?.env ?? {}) as { WORKER_SELF_REFERENCE?: ServiceBinding };
    return env.WORKER_SELF_REFERENCE ?? null;
  } catch {
    return null;
  }
}

// inside GET, after building `url`:
const binding = await getSelfBinding();
upstreamRes = binding
  ? await binding.fetch(url.toString(), { signal: upstreamCtrl.signal })
  : await fetch(url.toString(), { signal: upstreamCtrl.signal });
```

The `try/catch` in `getSelfBinding()` is deliberate — `getCloudflareContext` throws in non-CF runtimes (vitest, next dev without wrangler, jest), and we swallow that to let the fallback path serve dev/test traffic.

### Why service-binding (not direct function call)

A tempting alternative is to skip the HTTP hop entirely and call `searchSkills(...)` from `@/lib/search` directly. We reject that for THIS hotfix because:
- Larger surface change (route param mapping, response envelope construction, Server-Timing emission).
- Higher regression risk on a P0 with all eyes on the customer impact.
- The existing tests pin HTTP-level behavior (status codes, headers, ETag); rewriting to in-process invalidates a chunk of them.
- Performance gain is real but small (~30-100ms) and a follow-up can do it cleanly in green-field code.

Service-binding is the smallest possible change that matches the proven 0708 pattern. We can revisit in-process direct call as a follow-up optimization once the bleeding stops.

## Rationale

**Why this is a P0 hotfix, not a regular bug**: every search query in the deployed Studio find palette has been failing since 0716 closure-hardening landed (commit `0897eed`, Apr 25). User-visible impact is total — the find palette is the primary discovery surface. We have a reproducible probe and a known-good pattern from 0708.

**Why we don't fix the broader ranking issues here**: scope creep on a P0 is dangerous. Search rank tuning, LIST endpoint filter wiring, KV-index auto-rebuild, and `isVendor` drift are real bugs but each carries its own risk surface. Merging them with the loopback fix would inflate test runs, lengthen deploy verification, and increase rollback complexity. They're tracked as separate follow-up increments.

**Why we don't bump the timeout** (the previously-suspected red herring): direct probes show upstream `/api/v1/skills/search` returns 200 in 0.5-0.9s — the proxy fails in <0.2s — so the 5s timeout is not the cause. Bumping it would mask future regressions that warrant urgent attention.

**Why preserve every other proxy semantic byte-identical**: the route's per-isolate LRU, ETag, RFC-7232 If-None-Match, fail-open IP detection, etc. are all carefully argued in inline comments. Touching them in the same change as the transport swap would muddy the closure rationale and slow review.

## Architecture

### Components touched
- **Cloudflare Worker** (`verified-skill-com` per `wrangler.jsonc:2`). Uses OpenNext adapter — Next.js App Router routes run as worker handlers.
- **`WORKER_SELF_REFERENCE` service binding** (`wrangler.jsonc:81-86`). Already deployed; no wrangler config change needed.

### Components NOT touched
- Upstream `/api/v1/skills/search` route — works correctly; just unreachable via CDN.
- `/lib/search.ts` (KV + Postgres logic) — unchanged.
- `/lib/studio/{lru,rate-limit,etag}.ts` — unchanged.
- Studio frontend (`vskill/src/eval-ui/...`) — picks up the fix automatically once the proxy returns 200.

## Technology Stack

- TypeScript / Next.js 15 App Router (existing).
- `@opennextjs/cloudflare` `getCloudflareContext` (existing dependency).
- Vitest for new tests (existing).

## Implementation Phases

### Phase 1: RED — pin tests to the binding-first pattern (failing)
- T-001: Locate or create the studio-search route test file. If absent, create a minimal one mirroring `src/lib/skill-update/__tests__/publish-client.test.ts`.
- T-002: Add a test asserting the proxy uses the WORKER_SELF_REFERENCE binding's `fetch` when `getCloudflareContext` returns a binding.
- T-003: Add a test asserting the proxy falls back to `globalThis.fetch` when `getCloudflareContext` returns no binding.
- Verify both new tests FAIL against the unmodified source (RED gate).

### Phase 2: GREEN — apply the binding-first dispatch
- T-004: Add `getSelfBinding()` helper inside the route file (not exported — local to this module).
- T-005: Wrap the upstream `fetch(url.toString(), ...)` call at line 153 in a `binding ? binding.fetch(...) : fetch(...)` ternary.
- Verify both new tests PASS (GREEN gate).

### Phase 3: REFACTOR — verify no other proxy in the codebase has the same defect
- T-006: `grep -rn "fetch.*api/v1/skills/search" src/` and broader search for unmediated public-domain self-fetches in route handlers — confirm no other route has the same defect.

### Phase 4: VERIFY — local + production smoke
- T-007: `npm run lint && npm run typecheck` (or equivalent) — no new errors.
- T-008: Full `npx vitest run src/app/api/v1/studio/search/` — full route test file passes; targeted run of any other route that imports from this file remains green.
- T-009: `npm run deploy` — push to Cloudflare via OpenNext.
- T-010: Live probe production: `curl -sS -w "%{http_code}\n" https://verified-skill.com/api/v1/studio/search?q=react` returns 200; `curl ... ?q=skill-builder&limit=50` returns 200 with `total >= 31` and `results[]` containing `anton-abyzov/vskill/skill-builder`. Capture the responses in a log under the increment's `reports/` folder.

## Testing Strategy

- **Unit (Vitest)**: 2 new tests on the binding decision, mocking `getCloudflareContext` per existing pattern. Existing tests for cache/ETag/rate-limit/timeout/malformed remain unchanged and continue to pass.
- **Integration**: not added — service-binding behavior is faithfully covered by the publish-client.test.ts pattern.
- **Production smoke**: live curl probes (T-010) before closure.
- **Coverage target**: 90% (config). The 2 new tests increase route coverage; no decrease expected anywhere.

## Technical Challenges

### Challenge 1: testing `getCloudflareContext` without a real CF context
**Solution**: vitest mock at top of test file (`vi.mock("@opennextjs/cloudflare", () => ({ getCloudflareContext: vi.fn() }))`), then override per test to return either `{env:{WORKER_SELF_REFERENCE:{fetch}}}` or `{env:{}}`.
**Risk**: drift between mock shape and real OpenNext API. **Mitigation**: copy the exact mock shape from `src/lib/skill-update/__tests__/publish-client.test.ts` which already runs in CI.

### Challenge 2: confirming the bug is actually fixed in production after deploy
**Solution**: T-010 live probe with curl from the closure pipeline. If still 502, the increment stays open and we investigate further (e.g., service binding might need a wrangler redeploy of both the source and target service before becoming routable).
**Risk**: deploy succeeds but binding isn't active until both producer and consumer of the binding are simultaneously up. **Mitigation**: `verified-skill-com` is BOTH the producer and consumer of WORKER_SELF_REFERENCE here (it points back to itself), so a single deploy of the same worker is sufficient — no orchestration risk.

### Challenge 3: cache poisoning during the failed-state period
**Concern**: the per-isolate LRU might have cached a 502-equivalent prior response. **Reality check**: re-reading `route.ts:185-195`, only 200 OK responses with valid envelope shape get cached (lines 199-211 + 213-214); 502 responses skip the cache. So no cache poisoning to flush. New isolates after deploy will start cold and serve fresh 200s from the start.
