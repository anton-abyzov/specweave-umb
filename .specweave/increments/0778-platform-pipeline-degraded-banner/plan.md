# Implementation Plan: Studio Bell — Surface Platform Pipeline Degraded State

## Design

Three small, additive changes inside `repositories/anton-abyzov/vskill/`. No upstream platform changes.

### Part A — Server proxy `GET /api/platform/health` (US-001)

`src/eval-server/api-routes.ts` gains a new route. Implementation:

1. Reuse the existing `Router` interface; register adjacent to `/api/skills/updates` so logs/metrics group cleanly.
2. Handler issues `Promise.all` against two upstream URLs with `fetch(url, { signal: AbortSignal.timeout(1500) })`:
   - `https://verified-skill.com/api/v1/submissions/stats`
   - `https://verified-skill.com/api/v1/queue/health`
3. Computes the response shape:
   ```ts
   interface PlatformHealth {
     degraded: boolean;
     reason: string | null;        // "stats reports degraded; heartbeat stale 2h 4m"
     statsAgeMs: number;            // queueHealth.statsAge.ageMs ?? 0
     oldestActiveAgeMs: number;     // queueHealth.oldestActive.ageMs ?? 0
   }
   ```
4. Degraded gate (any of):
   - `stats.degraded === true`
   - `queueHealth.statsAge.ageMs > 30 * 60 * 1000`
   - `queueHealth.oldestActive.ageMs > 24 * 60 * 60 * 1000`
5. `reason` composed by appending whichever signals fired (e.g. `"platform reports degraded; heartbeat stale 2h 4m; oldest active submission 31d"`). Null when not degraded.
6. Try/catch wraps both fetches. On any error → return `{ degraded: false, reason: "platform-unreachable", statsAgeMs: 0, oldestActiveAgeMs: 0 }`. The studio MUST NOT amber-flash on user wifi blips.
7. In-memory cache with 60 s TTL keyed by `"v1"` (single-key cache; the response is global). Pattern: existing `agentPresenceCache` at `api-routes.ts:154`.

### Part B — Client hook `usePlatformHealth` (US-001)

New file `src/eval-ui/src/hooks/usePlatformHealth.ts` mirroring the `useGitHubStatus` pattern from 0772:

```ts
import { useSWR } from "./useSWR";

export interface PlatformHealth { /* same shape */ }

export function usePlatformHealth(): {
  data: PlatformHealth | undefined;
  loading: boolean;
} {
  const { data, loading } = useSWR<PlatformHealth>(
    "platform-health",
    () => fetch("/api/platform/health").then(r => r.json()),
    { ttl: 60_000 },
  );
  return { data, loading };
}
```

### Part C — UpdateBell amber state (US-002, US-003)

`src/eval-ui/src/components/UpdateBell.tsx` reads `usePlatformHealth()`. The component is currently keyed off `useSkillUpdates`; adding a sibling read costs one extra fetch / minute.

Render branches:

1. Bell `<button>`: when `degraded`, the embedded `<svg fill={iconColor}>` switches to `var(--color-own)`, and the button gains `title=` + `aria-label=` from US-002. When healthy, current rendering is preserved.
2. Dropdown surface: a new `<div role="status" aria-live="polite">` with the amber banner renders above the existing list when `degraded`. Uses the same border/padding tokens already in use elsewhere (e.g. `MarketplaceDrawer` warning surfaces).
3. Banner copy: `Platform crawler degraded` (bold) + `data?.reason ?? "—"` (dim). Composed with utility helpers — never includes raw upstream JSON.

The `degraded` classification in the UI is `data?.degraded === true` — both `loading` and `failure` paths fall through to the healthy-state render (defensive).

## Rationale

- **Why a server proxy and not browser → verified-skill.com directly?** Project memory `project_studio_cors_free_architecture` enshrines browser-to-localhost-only. Going around it would force CORS + auth surfaces we don't need.
- **Why 60 s cache?** The platform's degraded state changes on the timescale of operator action — minutes, not seconds. 60 s balances freshness with upstream protection.
- **Why fall back to `degraded: false` on any error?** False-positive amber on a user's flaky wifi would erode the signal's value. The platform's real degraded periods are long enough that we'll catch them on the NEXT successful fetch.
- **Why two thresholds (30 min stats, 24 h oldest active)?** Platform's stats refresh cadence is ~1 min; 30 min stale = real outage. Oldest-active 24 h is the minimum age that strongly indicates a stuck submission (normal processing is < 1 min per `avgProcessingTimeMs: 12012` from the live probe).
- **Why not change `/api/skills/updates`?** That endpoint has its own contract; adding a new orthogonal endpoint keeps the change additive and reversible.

## ADRs

No new ADRs. Respects:
- Studio CORS-free architecture (proxy lives on eval-server).
- Existing useSWR cadence pattern from 0772 (60 s TTL).
- Existing `var(--color-own)` warn token convention.
