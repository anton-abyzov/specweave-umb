# Plan — 0727: 0708 Follow-up Security & DoS Hardening

## 1. Architecture overview

This increment is **pure hardening of 0708's existing architecture** —
no new product features, no new system components, no scaling-trigger
changes. The base architecture diagrams and component contracts in
`.specweave/increments/0708-skill-update-push-pipeline/architecture.md`
**remain authoritative**; consult them for the SSE flow, the unified
scanner queue, the `UpdateHub` DO, the outbox writer/reconciler split,
and the cron belt. This document only specifies the *deltas* against
that baseline.

The change surface is small and bounded:

| Story | Component touched | Nature of change |
|---|---|---|
| US-001 | `app/api/v1/skills/stream/route.ts` | Add input validation (filter-id cap) at the route boundary |
| US-002 | `lib/internal-auth.ts`, `lib/webhook-auth.ts`, `app/api/v1/webhooks/github/route.ts` | Replace string `===` digest compare with `crypto.subtle`-backed timing-safe equality. Lift to one shared helper. |
| US-003 | `app/api/v1/webhooks/github/route.ts`, **new** `lib/skill-update/webhook-dedup-do.ts` | Introduce a minimal Durable Object whose `state.storage` provides atomic "put-if-absent" for `X-GitHub-Delivery`. Replaces the current GET-then-PUT against `RATE_LIMIT_KV`. |
| US-004 | 6 small files across `lib/skill-update/`, `lib/submission/publish.ts`, `scripts/build-worker-entry.ts` | Quality fixes — observability, narrowed types, narrowed catches |
| US-005 | `repositories/anton-abyzov/vskill/playwright.config.ts`, **new** `e2e/skill-update-pipeline-live.spec.ts` | Add a `@live`-tagged Playwright project that runs against a locally-spawned `npx wrangler dev` instead of `page.route` stubs |

**Non-goals** (explicit):
- No change to scaling triggers (DO sharding threshold, queue concurrency, rate-limit caps) — see 0708 §"Backpressure & Scaling".
- No change to event-payload shape, SSE wire format, or `UpdateEvent` schema.
- No change to the cron handler's task list (re-enable already shipped in 0708).
- No re-design of the outbox writer/reconciler split — only narrow observability tweaks under US-004.

## 2. §US-001 — SSE filter-id cap design

### Where the validation lives

The cap belongs **in the route handler itself**, before any Cloudflare
context resolution or DO upgrade fetch. Specifically: between the
existing empty-filter guard at `route.ts:35-39` and the
`getCloudflareContext` call at `route.ts:43`. Three reasons:

1. **No middleware**: Next.js 15 App Router middleware would intercept
   *all* `/api/v1/*` traffic. The cap is endpoint-specific; lifting it
   to middleware would be a wider blast-radius for zero gain.
2. **No Zod schema**: The current handler uses bare `URLSearchParams`
   parsing. Introducing Zod here would expand surface area beyond what
   one cap requires; a single inline check is the minimal change.
3. **Pre-DO**: The whole point is to reject before allocating a DO
   stub or opening a WebSocket — moving the check downstream of those
   would defeat the DoS protection.

### Cap value: 500 IDs

The authoritative plan documents 500 as the architect's existing
scaling boundary; subscriptions wider than that already have a documented
alternate path (`POST /api/v1/skills/stream/subscribe`, conceptually
present in 0708 §"Backpressure & Scaling"). Keeping the cap aligned with
that threshold means we don't have to relitigate the architectural
number later.

### Validation algorithm

```
ids       = skillsParam.split(",")          // O(n) in csv length
nonEmpty  = ids.filter(s => s.trim() !== "")
if nonEmpty.length > 500: return 400 with body
```

The split itself is O(csv-length); since Cloudflare already caps URL
length to ~16 KB, the worst-case input is bounded. We do not need to
replace the split with manual character scanning.

### 400 response shape

```json
{
  "code": "subscription_filter_too_large",
  "maxIds": 500,
  "providedIds": <count>
}
```

`Content-Type: application/json`. The existing 400 paths in this file
return `text/plain` (line 36-38); we keep that for the empty-filter case
to avoid touching unrelated ACs, but emit JSON for the cap case so
clients can branch on `code` rather than parsing text.

### Boundary at exactly 500

Implementation accepts `count <= 500`, rejects `count > 500`. The AC
matrix (US1-01 vs US1-02) explicitly fixes the off-by-one direction:
500 → accepted, 501 → rejected.

## 3. §US-002 — Timing-safe HMAC compare

### CF Workers crypto context

We are running on Workers, not Node. The `node:crypto` module is
available via `nodejs_compat` (already enabled in `wrangler.jsonc:5`),
but using it for digest compare introduces an unnecessary import-graph
footprint and tests have to polyfill in jsdom. The cleaner answer is
the **Web Crypto subtle API** which is already used throughout the
codebase (`webhook-auth.ts:18-29`, `webhooks/github/route.ts:50-62`).

Web Crypto has no built-in `timingSafeEqual` — it is a Node-only API.
The correct primitive on Workers is the **constant-time XOR-fold** that
the project already implements at `webhook-auth.ts:54-61` and
`webhooks/github/route.ts:65-70`. Both are correct algorithms and both
already operate on equal-length strings (early-rejecting unequal length
is acceptable since HMAC-SHA256 hex output is always 64 chars and
length is public).

### Decision: lift, don't rewrite

There is no reason to introduce `node:crypto.timingSafeEqual` when two
in-tree implementations are already correct. The actual gap is that
`internal-auth.ts:14, 22` does **not** use either — it does a raw `===`.

The plan is therefore:

1. Create one shared module `src/lib/crypto/timing-safe-equal.ts`
   exporting `timingSafeEqualString(a: string, b: string): boolean`
   with the existing XOR-fold algorithm.
2. Replace `internal-auth.ts:14` and `:22` with calls to the shared
   helper.
3. Delete the duplicated local definitions in `webhook-auth.ts:54-61`
   and `webhooks/github/route.ts:65-70`; both call the shared helper.
4. Audit grep for any other `=== ` against HMAC/HMAC-shaped values:
   - `grep -rn "key === \\|signature === \\|digest === \\|hmac === "` in `src/`
   - Specifically inspect: `src/app/api/v1/webhooks/**`, `src/lib/**auth**`, `src/lib/**hmac**`, `src/lib/**signature**`
   - Any hit not protected by timing-safe path → fix in same change.

### API surface

```ts
export function timingSafeEqualString(a: string, b: string): boolean;
```

Preconditions documented in JSDoc:
- Both inputs are strings of `length === 64` (SHA-256 hex) for the
  primary use case, but the function works for any equal-length string.
- Unequal length → false (intentional early return; HMAC output length
  is constant and public).

### Why not `crypto.subtle.timingSafeEqual`?

There is no such primitive in Web Crypto. The next-best —
`crypto.subtle.verify` — requires re-importing the key and re-running
the HMAC verify on raw bytes, which is a heavier API change than
warranted. We keep the XOR fold.

### Test seam (AC-US2-03)

The test asserts:

1. **Structural** — grep `src/lib/internal-auth.ts` for `=== `, and the
   match against `key ===` is gone (replaced by helper call).
2. **Behavioral** — the helper rejects unequal-length input *before*
   the XOR loop runs (early-return path covered by a unit test).
3. **Spy** — Vitest spies on `timingSafeEqualString` and asserts that
   `internal-auth.ts` and `webhook-auth.ts` invoke it on every compare.

### Audit list (the explicit "any other digest compare" question)

| File | Line | Today | Action |
|---|---|---|---|
| `src/lib/internal-auth.ts` | 14, 22 | `key === env.INTERNAL_BROADCAST_KEY` | Replace with `timingSafeEqualString(key, env.INTERNAL_BROADCAST_KEY)` |
| `src/lib/webhook-auth.ts` | 54-61 | local `timingSafeEqual` | Delete local def, import shared helper |
| `src/app/api/v1/webhooks/github/route.ts` | 65-70 | local `timingSafeEqual` | Delete local def, import shared helper |
| `src/lib/submission/**` | — | (audit) | Confirm no string `===` on signed values |
| `src/app/api/v1/internal/**` | — | (audit) | Confirm no string `===` on signed values |

If the audit finds further sites, they are added to the same PR;
discovery is part of the implementation work.

## 4. §US-003 — Atomic webhook anti-replay via Durable Object state

### Decision: new minimal `WebhookDeliveryDedupDO`

Per the interview answer (a). Reuse is preferred, but neither
`UpdateHub` (semantically: subscriber fan-out) nor `OutboxReconcilerDO`
(semantically: timer-driven reconciler) is a fit — overloading them
with delivery-id dedup would muddle their single-responsibility
contracts and the storage cost is trivial (one DO, one named instance,
~32 byte writes). A new DO with a single responsibility is cleaner.

### Why DO over D1 unique-constraint INSERT

The interview decision selected (a) over (b). Documenting the rationale
briefly so a future reader can re-evaluate:

- **Latency**: D1 INSERT-with-conflict is one network hop to the D1
  primary region (~30-100 ms cold from worker). DO storage is local to
  the DO's home region, typically <5 ms steady-state. The webhook
  fast-path NFR (NFR-NR-03) requires P50 unchanged or better; DO wins
  on the typical case.
- **Existing pattern**: 0708 already uses DOs for the hub and 0712
  uses one for the reconciler. A third tiny DO is consistent with
  existing operational practice (deploys, observability tooling,
  hibernation contract).
- **TTL**: D1 has no native TTL — we'd need a periodic cleanup query.
  DO `state.storage` has `setAlarm` and KV-style storage that is cheap
  to overwrite; we use **alarm-driven GC every 60s** to bound storage.
- **Failure modes**: D1 unique-constraint violation surfaces as a
  Prisma `P2002` error which we'd have to discriminate from other
  errors. DO `blockConcurrencyWhile` + `get`/`put` returns a clean
  boolean.

### Class shape

```ts
// src/lib/skill-update/webhook-dedup-do.ts

const TTL_MS          = 5 * 60 * 1000;  // 5 minutes (matches existing 300s)
const GC_INTERVAL_MS  = 60_000;         // run cleanup every 60s

export class WebhookDeliveryDedupDO {
  constructor(private state: DurableObjectState, private env: unknown) {}

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/dedup-and-record") {
      const { deliveryId } = await request.json<{ deliveryId: string }>();
      const result = await this.dedupAndRecord(deliveryId);
      return Response.json(result);
    }
    return new Response("not found", { status: 404 });
  }

  /**
   * Atomic put-if-absent + record.
   * Returns { firstSeen: true } if this is the first time we have seen
   * deliveryId in the TTL window. Returns { firstSeen: false } if it is
   * a replay.
   */
  private async dedupAndRecord(deliveryId: string): Promise<{ firstSeen: boolean }> {
    const key = `delivery:${deliveryId}`;
    const expiresAt = Date.now() + TTL_MS;

    return this.state.blockConcurrencyWhile(async () => {
      const existing = await this.state.storage.get<number>(key);
      if (existing !== undefined && existing > Date.now()) {
        return { firstSeen: false };
      }
      await this.state.storage.put(key, expiresAt);

      // Lazy-arm GC alarm if not already armed.
      const alarm = await this.state.storage.getAlarm();
      if (alarm === null) {
        await this.state.storage.setAlarm(Date.now() + GC_INTERVAL_MS);
      }
      return { firstSeen: true };
    });
  }

  /** Purge entries whose `expiresAt` is in the past, then re-arm. */
  async alarm(): Promise<void> {
    const now = Date.now();
    try {
      const all = await this.state.storage.list<number>({ prefix: "delivery:" });
      const dead: string[] = [];
      for (const [key, expiresAt] of all) {
        if (expiresAt <= now) dead.push(key);
      }
      if (dead.length > 0) {
        await this.state.storage.delete(dead);
      }
    } finally {
      const remaining = await this.state.storage.list({ prefix: "delivery:", limit: 1 });
      if (remaining.size > 0) {
        await this.state.storage.setAlarm(Date.now() + GC_INTERVAL_MS);
      }
    }
  }
}
```

#### Why `blockConcurrencyWhile` over `state.storage.transaction`

`storage.transaction` would also work and is technically closer to a
"true" atomic compare-and-swap. We pick `blockConcurrencyWhile` because:

1. The DO is a single-instance bottleneck by design (one named instance
   = `"global"`); concurrent webhook deliveries from different isolates
   all funnel through it. `blockConcurrencyWhile` makes the critical
   section explicit and matches the documented Cloudflare pattern for
   "exactly-once" gating.
2. It keeps the read+write inside the same JS turn, which is the
   guarantee we need (no other turn can interleave between the `get`
   and the `put`).
3. The `OutboxReconcilerDO` and `UpdateHub` patterns both use direct
   `state.storage` calls inside DO methods rather than transactions —
   we stay consistent with that house style.

`storage.transaction` is acceptable too; if the implementor finds
`blockConcurrencyWhile` blocks too long under load (it serializes all
calls), the swap to `transaction` is a one-line change. We document
this as a fallback, not the v1 choice.

### Wrangler binding

Add to `wrangler.jsonc`:

```jsonc
"durable_objects": {
  "bindings": [
    /* …existing… */
    { "name": "WEBHOOK_DEDUP_DO", "class_name": "WebhookDeliveryDedupDO" }
  ]
},
"migrations": [
  /* …existing v1, v2, v3 entries… */
  { "tag": "v4", "new_classes": ["WebhookDeliveryDedupDO"] }
]
```

### Webhook handler integration

`src/app/api/v1/webhooks/github/route.ts:99-110` becomes:

```ts
const deliveryId = request.headers.get("x-github-delivery");
if (deliveryId && env.WEBHOOK_DEDUP_DO) {
  const stub = env.WEBHOOK_DEDUP_DO.get(env.WEBHOOK_DEDUP_DO.idFromName("global"));
  const resp = await stub.fetch(new Request("https://do/dedup-and-record", {
    method: "POST",
    body: JSON.stringify({ deliveryId }),
  }));
  const { firstSeen } = await resp.json<{ firstSeen: boolean }>();
  if (!firstSeen) {
    return NextResponse.json({ ok: true, duplicate: true }, { status: 200 });
  }
}
// No second write — the DO already recorded the delivery.
```

Removes the prior `RATE_LIMIT_KV.get` + `RATE_LIMIT_KV.put` two-step.
The `RATE_LIMIT_KV` binding itself is still used by other rate-limit
paths; only the `gh-delivery:` prefix becomes unused (KV TTL drains it
within 5 min — no manual cleanup needed).

### Concurrency test (AC-US3-02)

```ts
it("100 concurrent calls with same delivery-id → exactly 1 firstSeen", async () => {
  const deliveryId = "test-uuid";
  const results = await Promise.all(
    Array.from({ length: 100 }, () => callDedup(deliveryId))
  );
  const firstSeenCount = results.filter(r => r.firstSeen).length;
  expect(firstSeenCount).toBe(1);
});
```

In test harness we instantiate the DO directly with a fake
`DurableObjectState` whose `storage` is a `Map`-backed shim and whose
`blockConcurrencyWhile` is a serial-promise queue. Vitest's
single-threaded JS turn semantics give us the same ordering guarantee
the real runtime provides. `vitest-pool-workers` is an alternative if
the implementor prefers a real Workers env.

### TTL behavior preserved (AC-US3-03)

Replay after 5 minutes is allowed by the `existing > Date.now()`
expiry check on read. A delivery-id used at t=0 and again at t=305s
will hit the second branch (entry exists but expired), write a fresh
expiry, and return `firstSeen: true`. Test:

```ts
it("after TTL expires, same delivery-id is treated as fresh", async () => {
  await callDedup("uuid"); // first: firstSeen=true
  vi.advanceTimersByTime(TTL_MS + 1000);
  const second = await callDedup("uuid");
  expect(second.firstSeen).toBe(true);
});
```

### Migration / rollout sequencing

Because the DO class is *new*, the wrangler migration
(`v4 new_classes: ["WebhookDeliveryDedupDO"]`) must be applied before
the route handler tries to look up the binding. We ship in two steps:

1. **Step 1**: Add the DO class + binding + migration. Deploy. Verify
   `WEBHOOK_DEDUP_DO` binding is reachable from a smoke test.
2. **Step 2**: Switch the webhook route to use the DO. Deploy.

In practice both steps can land in one PR if the implementor verifies
the binding via `wrangler dev` before committing.

## 5. §US-004 — Medium fixes (file:line table)

| AC | Finding | File | Line(s) | Design note |
|---|---|---|---|---|
| AC-US4-01 | F-CR6 | `src/lib/skill-update/scanner.ts` | hash compute site | Add a unit test that asserts `contentHash` for an unresolved skill matches the format `/^sha256:pending:[0-9a-f]{12}$/`. No production code change — this is purely a regression test. The format is already correct; the gap is test coverage. |
| AC-US4-02 | F-CR7 | `src/lib/skill-update/__tests__/queue-consumer.test.ts` | 2 sites | Replace `as any` with `vi.hoisted(() => ({ batch: {} as MessageBatch<ScanQueueMessage> }))` and a `Partial<MessageBatch<ScanQueueMessage>>` cast where partial is required. No production change. |
| AC-US4-03 | F-CR8 | `src/lib/skill-update/outbox-reconciler.ts` | 91-105 | In the catch path, change `console.error("[outbox-reconciler] success-update failed:", err)` to include `eventId: row.eventId`. Likewise the failure-update catch. AE metric write inside the loop should add `blobs[3] = row.eventId` as a correlation tag. Single-line edits. |
| AC-US4-04 | F-CR9 | `src/lib/submission/publish.ts` | (audit needed — broad catch around fingerprint computation; line numbers diverged from finding's `~125`) | Implementor greps for fingerprint-adjacent try/catch and narrows from `catch` to `catch (err) { if (err instanceof TypeError \|\| err instanceof RangeError) { /* expected — log warn and proceed */ } else throw err; }`. If the audit shows the catch was already removed (refactor since 0708), close as no-op with note. |
| AC-US4-05 | F-CR10 | `src/lib/skill-update/__tests__/outbox-writer.test.ts` | the `as never` site | Replace with `as unknown as Prisma.TransactionClient`. Must `import type { Prisma } from "@prisma/client"`. No production change. |
| AC-US4-06 | F-CR11 | `scripts/build-worker-entry.ts` | scheduled handler attachment site | Inside the scheduled handler attachment, add `console.log("[cron] scheduled handler attached")` once on cold start (i.e., at module top level if attachment is module-scoped, or on first invocation guarded by a module-level boolean). |

These are independent edits with no architectural risk. Each gets its
own task pair (red test / green change) but they ship in one PR.

## 6. §US-005 — Live wire E2E

### Test placement

Place new test in `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline-live.spec.ts`,
not in vskill-platform. Rationale: the existing
`skill-update-pipeline.spec.ts` lives in vskill (it tests Studio UI
behavior); the live variant should sit alongside its stubbed sibling
for ease of comparison. The "live" wires through to the running
worker, but the *test driver* is still Studio-side.

### Wrangler dev setup

Playwright's `webServer` config is *already* used in
`playwright.config.ts:11-21` to spawn `node dist/index.js eval serve …`
on port 3077. We add a **second `webServer`** entry for `wrangler dev`:

```ts
// playwright.config.ts (excerpt)
webServer: [
  // existing eval server
  {
    command: "node dist/index.js eval serve --root e2e/fixtures --port 3077",
    port: 3077,
    reuseExistingServer: !process.env.CI,
    timeout: 10_000,
    env: { VSKILL_WORKSPACE_DIR: "/tmp/vskill-e2e-workspace" },
  },
  // NEW: wrangler dev for vskill-platform — only for @live tests
  {
    command: "cd ../vskill-platform && npx wrangler dev --port 8788",
    port: 8788,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000, // wrangler dev cold-start is slower
    env: {
      DATABASE_URL: process.env.E2E_DATABASE_URL ?? "postgresql://localhost/vskill_e2e",
      GITHUB_WEBHOOK_SECRET: "test-secret-for-e2e",
      INTERNAL_BROADCAST_KEY: "test-broadcast-key",
    },
  },
],
```

### Database setup

The live test needs a real Postgres — we cannot use Prisma's in-memory
mock. Strategy:

1. Add an `npm run e2e:db-reset` script in vskill-platform that runs
   `prisma migrate reset --force` against `E2E_DATABASE_URL`.
2. The Playwright `globalSetup` for `@live` tests calls this script
   and seeds a single `Skill` row matching the test fixture's
   `sourceRepoUrl`.
3. After the suite, `globalTeardown` is a no-op (next run resets).

This keeps the live test hermetic across runs without burning a real
prod database.

### Test flow (AC-US5-02)

```ts
test("@live signed webhook → DB → SSE → UpdateBell badge", async ({ page }) => {
  // 1. Sign payload exactly like GitHub
  const payload = JSON.stringify({
    ref: "refs/heads/main",
    repository: { html_url: "https://github.com/test-org/test-skill" },
    head_commit: { id: "abc123" },
  });
  const signature = "sha256=" + (await hmacHex("test-secret-for-e2e", payload));

  // 2. Navigate Studio FIRST so SSE is connected before webhook fires
  await page.goto("/studio");
  await page.waitForSelector('[data-testid="update-bell"]');

  // 3. POST signed webhook to local wrangler dev
  const response = await fetch("http://localhost:8788/api/v1/webhooks/github", {
    method: "POST",
    headers: {
      "x-hub-signature-256": signature,
      "x-github-event": "push",
      "x-github-delivery": "test-delivery-" + Date.now(),
      "content-type": "application/json",
    },
    body: payload,
  });
  expect(response.status).toBe(200);

  // 4. Assert DB row landed (Prisma direct read)
  await expect.poll(async () => {
    const events = await prisma.updateEvent.findMany({
      where: { /* match by skillId from seeded fixture */ },
      orderBy: { createdAt: "desc" },
      take: 1,
    });
    return events.length;
  }, { timeout: 5_000 }).toBe(1);

  // 5. Assert badge increments within 2s
  await expect(page.locator('[data-testid="update-bell-badge"]'))
    .toHaveText("1", { timeout: 2_000 });
});
```

### EventSource in Playwright

The Studio app already opens its EventSource via the standard browser
API; we do not have to mock anything. The browser context's network
goes through Playwright's network stack; we point Studio at
`http://localhost:8788` for the API base via a fixture:

```ts
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    (window as any).__VSKILL_API_BASE__ = "http://localhost:8788";
  });
});
```

(Exact override mechanism follows whatever Studio uses today; the
implementor inspects `eval-ui/src/components/UpdateBell.tsx` for the
config hook.)

### `@live` tag config

Playwright supports per-project tags. Add a `live` project to
`playwright.config.ts`:

```ts
projects: [
  {
    name: "default",
    testIgnore: /-live\.spec\.ts$/,
  },
  {
    name: "live",
    testMatch: /-live\.spec\.ts$/,
    grep: /@live/,
  },
],
```

Then:

- `npx playwright test` → runs default project (existing tests, no
  wrangler dev needed because the second `webServer` entry is gated on
  `process.env.PLAYWRIGHT_RUN_LIVE === "1"` and that var is set by the
  live project's setup script).
- `npx playwright test --project=live` → runs only the live test with
  wrangler dev spawned.

### CI gating (AC-US5-03)

The live test does **not** run on the default CI lane. Add a separate
GitHub Actions workflow file (`.github/workflows/e2e-live-nightly.yml`)
that runs on schedule (`0 6 * * *`, daily at 6 AM UTC) and on
manual `workflow_dispatch`. The default PR workflow continues to run
only the stubbed `default` project. This keeps PRs fast and unblocks
contributors who don't have wrangler dev installed locally.

## 7. Backpressure & scaling

This increment **does not change** any scaling trigger:

- The new `WebhookDeliveryDedupDO` is a single named instance; it
  serializes through `blockConcurrencyWhile` but the section is
  microseconds (one `get` + one `put`). At 100 webhooks/sec (10x our
  current peak) the queue depth on the critical section is < 1 ms.
- The SSE filter cap reduces resource use on the `UpdateHub` DO, which
  is a *negative* load impact (helpful, not a new constraint).
- HMAC and quality fixes are at the implementation layer with no
  observable scaling effect.

For the actual scaling thresholds (SSE 10k concurrent, scanner queue
10k QPS, DO 1k connections per instance), refer to
`.specweave/increments/0708-skill-update-push-pipeline/architecture.md`
§"Backpressure & Scaling". Nothing in this increment moves those
numbers.

## 8. File manifest

### Modified files

| Path | Story | Nature |
|---|---|---|
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/route.ts` | US-001 | Add filter-id cap (~10 LOC) |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/__tests__/route.test.ts` | US-001 | New test file (or new tests in existing) |
| `repositories/anton-abyzov/vskill-platform/src/lib/internal-auth.ts` | US-002 | Replace `===` with shared helper (2 sites) |
| `repositories/anton-abyzov/vskill-platform/src/lib/webhook-auth.ts` | US-002 | Delete local `timingSafeEqual`, import shared |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` | US-002, US-003 | Delete local `timingSafeEqual`; switch dedup from KV to DO |
| `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` | US-003 | Add `WEBHOOK_DEDUP_DO` binding + `v4` migration |
| `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler.ts` | US-004 | Add `eventId` to error logs (lines 91-105) + AE metric tag |
| `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts` | US-004 | Narrow broad catch around fingerprint compute |
| `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/queue-consumer.test.ts` | US-004 | Drop `as any` casts |
| `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-writer.test.ts` | US-004 | Replace `as never` with `Prisma.TransactionClient` cast |
| `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` | US-004 | Add `contentHash` regression test |
| `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` | US-004 | Add cold-start log |
| `repositories/anton-abyzov/vskill/playwright.config.ts` | US-005 | Add `live` project + second `webServer` entry |

### New files

| Path | Story | Purpose |
|---|---|---|
| `repositories/anton-abyzov/vskill-platform/src/lib/crypto/timing-safe-equal.ts` | US-002 | Shared timing-safe string compare helper |
| `repositories/anton-abyzov/vskill-platform/src/lib/crypto/__tests__/timing-safe-equal.test.ts` | US-002 | Unit tests for helper |
| `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/webhook-dedup-do.ts` | US-003 | New DO class for atomic delivery-id dedup |
| `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/webhook-dedup-do.test.ts` | US-003 | DO unit tests including 100-concurrent-call test |
| `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline-live.spec.ts` | US-005 | Live wire E2E spec |
| `repositories/anton-abyzov/vskill-platform/__tests__/e2e/global-setup.ts` (or extend existing) | US-005 | DB reset + fixture seed for live tests |
| `.github/workflows/e2e-live-nightly.yml` | US-005 | Nightly + manual-dispatch CI |

No file is being deleted in this increment.

## 9. Test plan summary

### TDD pairing

Each AC gets a red/green pair:

- **AC-US1-01**: red — POST 501-id CSV expects 400. green — handler returns 400.
- **AC-US1-02**: red — POST 500-id CSV expects 200 (currently passes; locks as regression). green — no-op.
- **AC-US2-01..03**: red — assertion that `internal-auth.ts` calls `timingSafeEqualString`; green — refactor.
- **AC-US3-01**: red — concurrency test (100 calls, 1 first-seen). green — DO implementation.
- **AC-US3-02**: same red+green, asserts 99 dedup hits.
- **AC-US3-03**: red — TTL expiry test using fake timers. green — DO TTL logic.
- **AC-US4-\***: each one red+green; trivial.
- **AC-US5-\***: live spec is itself the test; it runs against wrangler dev.

### Structural assertions

- **HMAC**: Vitest spy on `timingSafeEqualString` + grep assertion that `=== ` is gone from auth modules.
- **Atomic anti-replay**: concurrency test using `Promise.all([100 calls])` with the DO instantiated under test.
- **SSE cap**: response body shape matches `{ code, maxIds, providedIds }`.

### Coverage target

Spec sets `coverage_target: 90`. New code (DO, helper, validators) must
hit 100% line coverage; quality fixes inherit the surrounding file's
existing coverage and shouldn't regress.

## 10. Migration & rollout

Order matters because the DO migration must precede its first call.

1. **Phase A (low risk, ship first)**:
   - US-001 SSE cap (additive 400 path; no semantic change for valid clients)
   - US-002 timing-safe HMAC (algorithmic equivalent — verified pairs still verify, invalid pairs still reject)
   - US-004 medium fixes (test/log/comment cleanups)

   These ship in one PR. No DO migration needed. No DB migration. Can
   roll back by reverting.

2. **Phase B (DO migration, ships next)**:
   - US-003 atomic webhook anti-replay
   - Wrangler migration `v4` deploys the DO class
   - Webhook route swaps from KV to DO

   Risk: rollback after deploy requires a wrangler migration to remove
   the DO class (or just leaves it dangling — DOs cost zero when
   unbound). The webhook route revert is straightforward.

3. **Phase C (test infra, no production impact)**:
   - US-005 live wire E2E + nightly workflow

   Independent of A/B; can land at any time after the DO is deployed.

Recommended single-PR strategy: A + B + C in one PR if the implementor
has wrangler dev configured; otherwise A in PR1, B in PR2, C in PR3.

## 11. Open questions / TBD

None. All five stories' design decisions are settled by the interview
answers + the authoritative plan + the existing 0708/0712 patterns.
The implementor proceeds directly to TDD red.

## References

- `.specweave/increments/0708-skill-update-push-pipeline/architecture.md` — base architecture (authoritative for all unchanged systems)
- `.specweave/increments/0708-skill-update-push-pipeline/reports/code-review-report.json` — F-CR2/3/4/6-11 source
- `.specweave/state/interview-0727-0708-followup-security-and-dos-hardening.json` — interview answers
- `~/.claude/plans/fluffy-foraging-popcorn.md` — approved authoritative plan
- `.specweave/docs/internal/architecture/adr/0727-01-do-state-for-webhook-delivery-dedup.md` (this increment writes it)
- `.specweave/docs/internal/architecture/adr/0727-02-live-wire-e2e-with-wrangler-dev.md` (this increment writes it)

## 12. ADR decisions

- **ADR-0727-01** — *will be written* (US-003 introduces a new DO; that is a long-lived architectural commitment worth recording).
- **ADR-0727-02** — *will be written* (the wrangler-dev + Playwright `@live` project pattern is novel for this repo; future increments will likely reuse it, so we standardize once).
