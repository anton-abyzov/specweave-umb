# Implementation Plan: Fix queue observability alerts follow-ups (0807 judge-llm)

## Architecture

```
                 alerts-evaluator/route.ts                     alerts-digest/route.ts
                 ┌────────────────────────┐                    (unchanged from 0807)
   */10 cron ──▶ │ for alert in alerts:   │
                 │   if info:             │   J-001: gate
                 │     if !shouldFire():  │   ── ALERTS_KV
                 │       suppressed++     │      .get(dedup:llm-fallback-spike:<date>)
                 │       continue         │
                 │     recordFired()      │   ALERTS_KV.put dedup (TTL=86400)
                 │     info++             │   + ring buffer + digest counter
                 │   ...                  │
                 └────────────────────────┘

                 alerts-evaluator/route.ts (J-005)
                 ┌────────────────────────────────────┐
                 │ readDrainLast1h(kv):               │
                 │   hours = envInt(                  │
                 │     "ALERT_DRAIN_WINDOW_HOURS", 1) │
                 │   for i in 0..hours:               │
                 │     ts = (now - i*1h).slice(0,13)  │
                 │     read kv qm:<ts>                │
                 │   return sum                       │
                 └────────────────────────────────────┘

                 _test-seed/route.ts                  e2e admin-alerts.spec.ts
                 ┌────────────────────────┐           ┌─────────────────────────┐
   POST(admin    │ if !ALLOW_ALERT_SEED   │           │ before nav:             │
   cookie + flag)│   → 403                │           │   request.post(         │
              ──▶│ if !requireAdmin       │           │     "_test-seed", body) │
                 │   → 401/403            │ ──flag──▶ │ navigate /admin/queue   │
                 │ recordFired(synthetic) │           │ click ack-btn-<id>      │
                 │   → returns id         │           │ reload                  │
                 └────────────────────────┘           │ assert under            │
                                                      │   alerts-acknowledged-  │
                                                      │   section               │
                                                      └─────────────────────────┘

                 RecentAlertsPanel.test.tsx
                 ┌────────────────────────────────────┐
                 │ vi.mock("global.fetch") + RTL:     │
                 │   render(<RecentAlertsPanel/>)     │
                 │   wait for state                   │
                 │   assert testid + ack flow         │
                 └────────────────────────────────────┘
```

## Modules

### Modified — `src/app/api/v1/internal/alerts-evaluator/route.ts`
- **Lines 39–53 (J-005)**: replace dead `for (let i = 0; i < 1; i++)` with `for (let i = 0; i < envInt("ALERT_DRAIN_WINDOW_HOURS", 1); i++)` and a one-line comment naming the env var.
- **Lines 222–229 (J-001)**: gate info branch through `shouldFire(alertsKV, alert.kind, alert.key)` before `recordFired()`. Suppressed runs increment the existing `suppressed` counter.

### Modified — `src/app/api/v1/internal/alerts-evaluator/__tests__/route.test.ts`
- Append **TC-046** (J-001 dedup): seed fallback counters above 20 → POST twice → assert `info===1` then `info===0` + suppressed≥1, dedup key present after first call, digest counter stays at "1".
- Append **TC-047** (J-005 window): `process.env.ALERT_DRAIN_WINDOW_HOURS = "3"` → seed three `qm:<ts>` buckets → POST → drain detector reads all three (assert via mock kv `get` call count or via the resulting `drainLast1h` value in the response snapshot).

### New — `src/app/api/v1/admin/alerts/_test-seed/route.ts`
Shape:
```ts
export async function POST(request: NextRequest): Promise<Response> {
  const { env } = await getCloudflareContext({ async: true });
  if ((env as { ALLOW_ALERT_SEED?: string }).ALLOW_ALERT_SEED !== "1") {
    return Response.json({ error: "disabled" }, { status: 403 });
  }
  const auth = await requireAdmin(request);
  if (isAuthError(auth)) return auth;

  const alertsKV = (env as { ALERTS_KV?: AlertsKV }).ALERTS_KV ?? null;
  if (!alertsKV) return Response.json({ error: "ALERTS_KV not bound" }, { status: 503 });

  const body = await request.json().catch(() => ({})) as Partial<{
    kind: AlertKind; severity: Severity; key: string;
    title: string; payload: Record<string, unknown>;
  }>;
  if (!body.kind || !(body.kind in KIND_SEVERITY)) {
    return Response.json({ error: "invalid kind" }, { status: 400 });
  }
  const severity = body.severity ?? KIND_SEVERITY[body.kind];
  const alert: Alert = {
    id: crypto.randomUUID(),
    kind: body.kind,
    severity,
    key: body.key ?? "e2e-seed",
    title: body.title ?? `[E2E SEED] ${body.kind}`,
    payload: body.payload ?? {},
    timestamp: new Date().toISOString(),
  };
  await recordFired(alertsKV, alert);
  return Response.json({ seeded: true, id: alert.id });
}
```

### New — `src/app/api/v1/admin/alerts/_test-seed/__tests__/route.test.ts`
- TC-048: `ALLOW_ALERT_SEED` unset → 403.
- TC-049: flag set, no admin → forwards `requireAdmin`'s 401/403.
- TC-050: flag set + admin cookie → 200 + ring buffer contains seeded alert.

### New — `src/app/admin/queue/__tests__/RecentAlertsPanel.test.tsx`
Mocks `globalThis.fetch`. Five cases:
- TC-051 empty: GET returns `{alerts:[]}` → `[data-testid="alerts-empty"]` visible.
- TC-052 loading: never-resolving fetch → `Loading…` text visible immediately.
- TC-053 error: GET returns 500 → `[data-testid="alerts-error"]` shows `HTTP 500`.
- TC-054 grouping: GET returns 1 critical + 1 warning + 1 info → all three sections render in `SEVERITY_ORDER`; counts pill shows `(3 active, 0 acknowledged)`.
- TC-055 ack: GET returns 1 alert → click `ack-btn-<id>` → POST `/api/v1/admin/alerts/<id>/ack` called → second GET returns same alert with `acknowledged:true` → row appears under `[data-testid="alerts-acknowledged-section"]`.

### Modified — `tests/e2e/admin-alerts.spec.ts:84-106`
Replace the `test.skip(!hasAlert, ...)` block with a pre-test seed call to `_test-seed`. If the seed call returns 403 (no flag in local dev), skip the test once with a clear reason. In CI (`ALLOW_ALERT_SEED=1`), run the full ack flow.

### Modified — `.specweave/increments/0807-queue-observability-alerts/spec.md:71`
Wording-only change for AC-US3-05: "09:00 / 13:00 / 17:00 / 21:00 UTC" → "00:00 / 06:00 / 12:00 / 18:00 UTC", with an inline note `(see 0808 for code/spec alignment)`.

## Reused utilities

- `shouldFire` / `recordFired` — `src/lib/alerts/dedup.ts`
- `KIND_SEVERITY`, `SEVERITY_TTL_S`, `dedupKey`, `Alert`, `AlertKind`, `Severity` — `src/lib/alerts/types.ts`
- `requireAdmin`, `isAuthError` — `src/lib/auth.ts`
- `envInt` — already in `alerts-evaluator/route.ts:144`
- `getCloudflareContext` — `@opennextjs/cloudflare`

## ADR (inline)

**Decision**: J-001 fix gates info-severity through `shouldFire()` rather than introducing a per-info-kind counter table.
**Rationale**: existing severity-tier dedup primitive already gives us per-(kind,key) deduplication. A separate counter table would duplicate state and add a new schema. The 1-day TTL on `SEVERITY_TTL_S.info` is exactly the cadence the digest needs.
**Alternatives**: (1) move info to a separate code path (rejected — no behavior win, more divergence). (2) lengthen `*/10` cron to `*/60` for info detectors only (rejected — couples cadence to severity which is wrong abstraction).

**Decision**: J-002 seeding via flag-gated admin endpoint, not wrangler kv:put from inside Playwright.
**Rationale**: keeps the test self-contained and auth-checked. Avoids leaking the prod KV namespace ID into test code or CI secrets. Easy to extend later (e.g. multi-alert seed scenarios).
**Alternatives**: (1) direct wrangler shell-out (rejected — brittle, requires wrangler auth in CI). (2) bypass auth for `_test-seed` (rejected — anonymous seed in prod is not acceptable even with the flag).

## Test strategy

| File | Type | Coverage |
|------|------|----------|
| `alerts-evaluator/__tests__/route.test.ts` | vitest unit | TC-046 (J-001 dedup), TC-047 (J-005 window) |
| `_test-seed/__tests__/route.test.ts` | vitest unit | TC-048..TC-050 (flag, auth, happy path) |
| `RecentAlertsPanel.test.tsx` | vitest + jsdom + RTL | TC-051..TC-055 (empty/loading/error/grouping/ack) |
| `tests/e2e/admin-alerts.spec.ts` | Playwright | TC-044/045 ack flow runs end-to-end with seed |

TDD discipline: T-001 / T-003 / T-005 / T-009 are RED; T-002 / T-004 / T-006 / T-007 are GREEN. T-008 is wording-only.

## Deploy + smoke

1. `rm -rf .open-next && npm run build && npm run build:worker && npm run deploy`.
2. Set `ALLOW_ALERT_SEED` prod secret to "0" (default-OFF). Flip to "1" only for the e2e CI window.
3. **J-001 smoke**: write `ai:fallback:claude:<today>` and `ai:fallback:ollama:<today>` to KV with values that sum > 20. Wait two `*/10` ticks. Read `alerts:digest:count:llm-fallback-spike` — must be `"1"`. Read `alerts:dedup:llm-fallback-spike:<today>` — must be set.
4. **J-003 spot-check**: trigger `/api/v1/internal/alerts-digest` (cron will hit it on the heavy cohort) — confirm `window.start` matches `T(00|06|12|18):00Z`.
5. **Submission-processing guarantee** (US-006): POST a fresh submission to `/api/v1/submissions`, poll `state` every 5s, record elapsed → must be ≤ 300s.
