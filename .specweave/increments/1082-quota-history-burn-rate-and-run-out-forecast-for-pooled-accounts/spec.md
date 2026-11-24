# Quota history, burn rate and run-out forecast for pooled accounts

## Problem

Theo (T3 Code) recommends putting many Claude and Codex subscriptions behind a CLIProxy hub and shows its "Quota Management" page: pooled remaining quota per provider ("555% of 600%"), a recorded and projected chart, "Pool empty", "First empty", "Next reset" and "Burn, last 3h" (x.com/theo/status/2114670780403560717).

SpecWithCode already covers most of that setup: several accounts per provider with separate logins (`ClaudeHome.ts`, `CodexHomeLayout.ts`), CLIProxyAPI hubs as a quota source (`usage/cliproxyApi.ts`), a pooled "By account" view that counts each account once across machines (`shared/usageLimits.ts`, `UsageLimitsPooled.tsx`), and automatic switching at the limit (`ProviderFallbackWorker.ts`). It keeps no quota history at all: only the latest snapshot per instance (`providerStatusCache.ts`) and hub reads in memory (`UsageLimitSources.ts`). So it cannot say how fast quota is going, when an account or the whole pool runs out, or draw quota over time. The "By account" caption also says accounts are "added up" while the pool is an average.

## Scope

In: server-side quota history for native instances and hub accounts, kept on disk with pruning; a read RPC; shared burn-rate and run-out maths; burn, first empty, pool empty, next reset, total left and a recorded plus projected chart on each pooled window card; the caption fix.

Out: routing turns through a CLIProxy hub or sharing logins between machines (subscription terms forbid pooling one login; SpecWithCode deliberately keeps hubs read-only); fallback ranking by remaining quota (separate change, `providerFallback.ts` is at its size cap); plan weighting; native iOS app.

## Acceptance Criteria

- [ ] AC-01: The server records a sample per account and window whenever a native instance or a hub reports new usage, keeps 14 days on disk, survives a restart, and serves it through `usageLimits.history` (orchestration read scope).
- [ ] AC-02: Shared maths gives each pooled window: total left out of total capacity, burn per hour over the last 3 hours, when the first account runs out (and which), when the whole pool runs out, the next reset that restores quota, and recorded plus projected pool series, with resets refilling accounts and spend moving to accounts that still have quota.
- [ ] AC-03: Usage → Limits → By account shows these figures and a recorded/projected chart per pooled window, says "Collecting history" until there is enough to measure, keeps working against servers without the RPC, and the caption no longer claims accounts are added up.

## Approach

- `packages/contracts/src/usageLimitHistory.ts`: sample, series, input and result schemas plus its own RPC group (rpc.ts groups are split for type depth), scope in `clientRpcPermissions.ts`, instrumentation category.
- `apps/server/src/usage/usageLimitHistoryStore.ts` (pure append, dedupe, prune, cap) and `UsageLimitHistory.ts` (subscribes to `ProviderRegistry.streamChanges` and `UsageLimitSources.streamChanges`, keys accounts with `limitAccountKey`, writes `<stateDir>/usage-limit-history.json` atomically at most once a minute and on shutdown). A JSON file, not a SQLite migration: the database is large and migrations have held up updates before.
- `packages/shared/src/usageLimitForecast.ts`: history index, burn per member, step simulation of the pool (demand stays at the current pooled burn; an empty account's share moves to the others; resets repeat every window length).
- `apps/web/src/components/usage/UsageLimitsPoolForecast.tsx` + `usageLimitHistoryState.ts`: fetch history from each connected environment, merge, render stats and an SVG chart inside `PoolWindowCard`.
- Sample time is the read's own `checkedAt`, so replayed or cached snapshots never invent points.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Build history and forecast, not request routing through a hub → visibility only; routing pooled subscription logins conflicts with provider terms.
- D-02 Units → percent of one account, so 6 accounts = 600%, matching Theo's page and the existing equal-width bar.
- D-03 Storage → JSON file in the state directory, 14 days, 3000 samples per series.

### Open
- none

## Tasks

### T-01 History contract, recorder and RPC
- AC: AC-01 | Files: packages/contracts/src/usageLimitHistory.ts, packages/contracts/src/rpc.ts, packages/contracts/src/clientRpcPermissions.ts, packages/contracts/src/index.ts, apps/server/src/usage/usageLimitHistoryStore.ts, apps/server/src/usage/UsageLimitHistory.ts, apps/server/src/usage/usageLimitHistoryStore.test.ts, apps/server/src/usage/UsageLimitHistory.test.ts, apps/server/src/observability/RpcInstrumentation.ts, apps/server/src/server.ts | Test: cd repositories/anton-abyzov/specweave-studio && pnpm exec vp test run apps/server/src/usage/usageLimitHistoryStore.test.ts apps/server/src/usage/UsageLimitHistory.test.ts

### T-02 Forecast maths
- AC: AC-02 | Files: packages/shared/src/usageLimitForecast.ts, packages/shared/src/usageLimitForecast.test.ts, packages/shared/package.json | Test: cd repositories/anton-abyzov/specweave-studio && pnpm exec vp test run packages/shared/src/usageLimitForecast.test.ts

### T-03 Pooled view forecast and chart
- AC: AC-03 | Files: apps/web/src/components/usage/UsageLimitsPoolForecast.tsx, apps/web/src/components/usage/usageLimitHistoryState.ts, apps/web/src/components/usage/UsageLimitsPooled.tsx, apps/web/src/components/usage/UsageLimits.tsx, apps/web/src/components/usage/UsageLimitsPoolForecast.test.tsx | Test: cd repositories/anton-abyzov/specweave-studio && pnpm exec vp test run apps/web/src/components/usage/UsageLimitsPoolForecast.test.tsx
