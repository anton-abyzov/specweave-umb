# Plan — 0687 Queue Dashboard Truthful Load, Fast Filters, and Design Rollback

## 1. Goals

Ship a queue page that is truthful on first load, fast during filter/search changes, restored to the previous simpler queue-first design, and operationally easier to debug.

## 2. Working Assumptions

1. The current default `active` landing state is a poor product choice when the active queue is genuinely empty.
2. The queue should prefer a truthful, labeled fallback dataset over a blank default state.
3. The current performance issues are not only UI problems; they stem from query shape, cache drift, and production schema/runtime mismatch.
4. Secret values should be audited for usage, but never echoed into specs, logs, or code comments.
5. The queue request path must not compute expensive stats synchronously during SSR or during filter switching; stale-but-truthful cached stats are preferable to a 15 s blocking recompute that returns zeros.
6. The latest Studio-style queue hero/card redesign should be rolled back to the previous compact queue page structure while preserving the useful loading/error behavior.

## 3. Implementation Tracks

### Track A — Truthful server boot path

- Review `src/app/queue/page.tsx`, `src/app/queue/data.ts`, and `QueuePageClient` boot behavior.
- Replace nullable initial boot data with an explicit server-side result contract:
  - `mode: "ok" | "degraded" | "error"`
  - `defaultFilter`
  - `stats`
  - `submissions`
  - `total`
- Choose a truthful default behavior:
  - If active queue has rows, land on `active`.
  - If active queue has zero rows but other states have data, land on the best operator-friendly fallback such as `published` or `recent`.
- Ensure the first render and client hydration use the same source-of-truth payload.

### Track B — Query and cache stabilization

- Review the list API, search API, stats API, queue list warm-up, and cache TTL/invalidation strategy.
- Profile first-page queries for `active`, `published`, `rejected`, `blocked`, and `onHold`.
- Remove or bound synchronous on-demand stats computation from `/queue` and `/api/v1/submissions/stats` read paths; read paths should return KV, memory, DB fallback, or a clearly degraded response quickly.
- Reduce payload cost and remove avoidable query work on first-page interactions.
- Make list cache and stats cache coherent:
  - shared freshness window
  - shared invalidation/update rules
  - clear fallback order
- Add lightweight instrumentation for cache hit/miss, query duration, and degraded fallback use.
- Add a warm/read-through path so switching among `active`, `published`, `rejected`, and `blocked` uses exact or per-filter latest cache immediately, then refreshes in the background where needed.

### Track C — Database truthfulness and duplicate control

- Audit the live-serving assumptions around `Submission` uniqueness.
- Confirm whether the existing unique-constraint migration is present in repo but absent in production.
- Implement one of the following, preferring the strongest safe option:
  1. Apply/prepare the proper uniqueness migration and duplicate cleanup path.
  2. If migration must be phased, add deterministic queue-serving dedup plus an explicit runbook for prod rollout.
- Make sure filter counts and rendered rows operate on the same deduplicated truth model.

### Track D — Credentials and runtime audit

- Inspect `.env`, env-loading code, and Cloudflare bindings used by queue-serving code.
- Produce a safe inventory of:
  - DB connection inputs
  - KV/cache namespaces
  - auth/internal tokens
  - email/admin secrets if they participate in queue flows
- Verify queue-serving code does not log secret material and does not unnecessarily fan out across conflicting credential sources.

### Track E — UI rollback to prior queue-first design

- Remove the Studio-style hero/asides/card shell added to the queue page.
- Restore the previous compact structure:
  - `SectionDivider title="Submission Queue"`
  - stat cards directly under the title
  - rejection reason filters where applicable
  - status bar
  - search input
  - batch submit panel
  - banner/empty/loading/table/pagination
  - execution log
- Keep functional improvements that do not contribute to the heavy redesign:
  - truthful boot messaging where useful
  - stale/degraded retry banner
  - deterministic empty/loading states
- Remove queue-specific warm beige token usage if it is no longer needed after rollback.

## 4. Verification Strategy

- Unit/integration:
  - queue boot data contract
  - filter/list/stats coherence
  - dedup behavior in served results
  - cache TTL/invalidation behavior
  - env/binding audit utilities
- E2E:
  - initial load renders meaningful content
  - filters work across major states
  - empty/degraded states are intentional and readable
  - Playwright category-switch performance checks stay within target thresholds
  - visual regression confirms the compact pre-redesign queue structure is restored
- Required project gates after implementation:
  - `npx vitest run`
  - `npx playwright test`
  - `npx vitest run --coverage`

## 5. Rollout Notes

1. Preserve unrelated local changes in `repositories/anton-abyzov/vskill-platform`.
2. Separate safe app-code changes from any prod DB migration/runbook work.
3. If the live database still lacks the uniqueness constraint, treat rollout as two-stage:
   - app-side truthful rendering + dedup-safe serving
   - database enforcement/deploy/runbook
4. When all tasks are complete, run the closure flow immediately per repo instructions.

## 6. Baseline From 2026-04-24 Local Testing

- `CI=1 E2E_BASE_URL=http://localhost:3310 npx playwright test tests/e2e/queue-truthful-load.spec.ts tests/e2e/queue-cold-load.spec.ts --project=chromium --reporter=line`
  - Result: 4 passed, 1 failed.
  - Failure: `queue-cold-load.spec.ts` expects 50 rows within 1.5 s, but the first load renders an empty active view.
- Local server log shows repeated `GET /queue` durations around 15.3-19.7 s when the stats read path falls through to `computeQueueStats()` and its raw SQL times out after 15 s.
- Direct local timings:
  - cold `published` list: about 4.1 s
  - warm `published` list: about 20 ms
  - warm `blocked` list: about 20 ms
  - `active` list: about 225-440 ms
  - stats endpoint: about 15.2-15.3 s and returns all-zero stats
