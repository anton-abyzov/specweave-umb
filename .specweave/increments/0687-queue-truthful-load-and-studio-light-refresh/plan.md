# Plan — 0687 Queue Dashboard Truthful Load, Backend Stabilization, and Studio Light Refresh

## 1. Goals

Ship a queue page that is truthful on first load, fast during filter/search changes, visually aligned with the Studio light theme, and operationally easier to debug.

## 2. Working Assumptions

1. The current default `active` landing state is a poor product choice when the active queue is genuinely empty.
2. The queue should prefer a truthful, labeled fallback dataset over a blank default state.
3. The current performance issues are not only UI problems; they stem from query shape, cache drift, and production schema/runtime mismatch.
4. Secret values should be audited for usage, but never echoed into specs, logs, or code comments.

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
- Reduce payload cost and remove avoidable query work on first-page interactions.
- Make list cache and stats cache coherent:
  - shared freshness window
  - shared invalidation/update rules
  - clear fallback order
- Add lightweight instrumentation for cache hit/miss, query duration, and degraded fallback use.

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

### Track E — UI refresh using the frontend design skill

- Reuse the Studio light-theme direction from the current vSkill Studio:
  - warm paper background
  - ink-forward typography
  - restrained accent color
  - clearer card/table hierarchy
- Refresh:
  - hero/status section
  - filter controls
  - list container/table rows
  - empty/loading/error/degraded states
- Keep the design consistent with the broader site while moving the queue away from a flat utilitarian look.

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
  - Studio-aligned visual regressions for light theme
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
