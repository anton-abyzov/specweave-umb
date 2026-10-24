# Usage and cost dashboard

## Problem

Anton asked whether SpecWithCode has the T3 Code style "Usage" money view (reference: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-d8645084-a1e5-41b9-bbf3-0120400b03b6.png`).

Finding (specwithcode-dev `origin/main` 252be2eb4): most of it already exists. `/usage` (`apps/web/src/components/usage/UsagePage.tsx`, reached from the account menu, the command palette and the coordinator usage chip) has Cost/Tokens/Limits, Past 24h/7/30/90 days, an environment filter, a dollar total, per-provider rows, a hover-readout daily stacked area chart, token/cache totals, cost by type, cost by speed, and a model/day breakdown with a model detail dialog and price overrides. Server data comes from local transcripts (`apps/server/src/usage/`), priced by provider-reported cost, custom overrides or the LiteLLM table.

What is wrong today:

- The money is easy to misread. The only basis label is a small "API estimate"; nothing says it is not a bill, which providers bill per token versus run on a plan, or how much plan allowance is left. Anton's Claude CLI currently bills Console API credits, so a reader cannot tell estimate from spend.
- Unknown shows as zero. Provider rows, chart readouts and day cells print `$0.00` for usage whose records have no rates; only the model table says "Unpriced".
- Providers SpecWithCode cannot read (GitHub Copilot, Gemini CLI and other ACP agents) silently disappear from the totals.
- No provider or model filter, and the chart cannot drill into a day.

## Scope

In: the Usage page Cost and Tokens views (web), additive fields in `packages/shared/src/usageMerge.ts`, a pure billing/allowance model, chart click-to-pin, provider/model filters, unit tests, headless fixture screenshots, merge, release through the current release owner, installed screenshots. Desktop first (1440px), still usable at 1024px and 390px. Follow-up scope: an explicit next-seven-day forecast from complete measured daily history, improved responsive composition, readable stacked cost categories and ranked model rows, and exact sampled chart lines with keyboard/touch selection.

Out: new billing integrations or credentials (no Anthropic balance API exists; Admin keys are unavailable for individual orgs), changes to provider accounts, Limits tab redesign, server transcript readers, Copilot/Gemini token history, the picker usage (#549/0983 own it), iOS.

## Acceptance Criteria

- [ ] AC-01: A cost basis strip under the total separates three things with explicit labels: "API-equivalent estimate" (dollar figure, "not a bill", priced coverage), "Billed spend" (shown as "Not reported" with the providers whose current sign-in bills per token named; never a fabricated dollar figure), and "Plan allowance" (per subscription provider, the tightest fresh window's remaining percent, or "Not reported"/"Stale" when the read is missing or older than 15 minutes). No savings figure is presented as money saved.
- [ ] AC-02: Each provider row carries its current billing mode from the connected environments' provider sign-ins: Plan, Per token, Mixed or Unknown.
- [ ] AC-03: Unknown is never zero: a provider, day, hour or chart readout whose records are all unpriced reads "Unpriced"; a partly unpriced figure is marked as a lower bound; the total says what share is excluded in visible text.
- [ ] AC-04: Connected providers whose usage SpecWithCode cannot read are listed as "Not in these totals" instead of disappearing.
- [ ] AC-05: Clicking a provider row filters the chart, totals, cost by type and breakdown to that provider set; a search field filters the model breakdown; active filters show as removable chips with a Clear action.
- [ ] AC-06: Clicking (or Enter on) a chart column pins that day or hour: the totals, cost by type and model breakdown show that period only, the chart marks the pinned column, and the pin clears with its chip or Escape.
- [ ] AC-07: Headless fixture screenshots at 1440px (dark and light) and 390px show the cost basis, filters, pinned day and unpriced states; unit tests cover the billing model, unpriced provider totals and filtering.
- [ ] AC-08: Merged to main, released by the current release owner, and the installed app's `/usage` page shows the new view (installed screenshot, distinct from fixture proof).
- [ ] AC-09: A distinct forecast view shows daily burn rate and next-seven-day token/API-equivalent projections from up to seven completed calendar days, with at least five covered days and three active days. Exclude the current partial day. Show the observation dates, oldest source read, assumptions and empirical low/high scenario range, never a promised confidence interval. Incomplete, stale, hourly-only, pinned or insufficient history stays unavailable. Unpriced history suppresses monetary forecasts while measured-token forecasts may remain available. Never forecast actual charges or infer subscription time-to-limit without quota history.
- [ ] AC-10: Improve the desktop and narrow-screen hierarchy around measured history, forecast, billing meaning and breakdown. Keep the stacked Input/Cache read/Cache write/Output/Other bar and ranked models with inline metric share bars, Cost/Share/Tokens values, legible responsive labels and keyboard focus. Unpriced and partial coverage remain explicit; no hidden mobile values or overflowing document.
- [ ] AC-11: Multi-provider daily/hourly lines connect exact sampled values without smoothing or invented peaks. A shared date cursor reads each provider and total, coordinated with date/provider filters. Pointer/touch click and keyboard selection pin the same sample, and Escape clears the selection without leaving the page.

## Approach

1. `packages/shared/src/usageMerge.ts`: add `records`/`unpricedRecords` to `byProvider` period entries and `unpricedRecords` to `ProviderTotals`; export `isCostUnknown`/`isCostPartial` helpers. Additive, existing callers unchanged.
2. `apps/web/src/components/usage/usageBilling.ts` (new, pure): map usage provider kinds to driver kinds, classify each environment's provider instances with the existing `billingOf` (`packages/shared/src/taskRouting.ts`), collapse to Plan / Per token / Mixed / Unknown, compute the tightest fresh window (`remainingPercent`, 15 minute freshness like `USAGE_FRESH_MS`), and list untracked connected providers.
3. `apps/web/src/components/usage/UsageCostBasis.tsx` (new): the three-card strip and the "Not in these totals" line.
4. `UsageProviderChart.tsx`: `selectedIndex` + `onSelectPeriod` props, click/Enter/Escape, pinned column marker, "Unpriced" in the readout.
5. `UsagePage.tsx`: provider set + pinned period + model query state, a second filtered merge via `mergeAnsweredUsage(keepBucket)` (chart uses provider filter only; summary sections use both), filter chips, unpriced-aware cells, billing chips on provider rows. Sessions are summed from the selected providers; a pinned period shows responses instead because sessions are not split by period.
6. Headless fixture under `apps/web/tests/usage-dashboard/`, screenshots to `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/`.

Rejected: a new server billing endpoint (no provider exposes charges without credentials the user has not given); computing "savings vs subscription" (needs plan prices SpecWithCode does not know and would fabricate money); a third-party chart library (the existing SVG chart already does hover and stacking).

Risk: billing mode is the current sign-in, not historical; the copy says "now".

## Decisions

### Asked
- none (user authorized plan, implementation and deployment)
### Defaulted (change any before sw-do)
- D-01 Billed spend shows "Not reported" plus the per-token providers instead of any dollar figure, because no connected source reports charges.
- D-02 Cache savings stays in Totals but is relabeled "Cache savings at API rates" so it is not read as money saved.
- D-03 Filters live in page state (not persisted); window and metric keep their saved preferences.
### Open
- none

## Tasks

### T-01 Unpriced-aware merge fields
- AC: AC-03 | Files: packages/shared/src/usageMerge.ts, packages/shared/src/usageMerge.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard && npx vitest run packages/shared/src/usageMerge.test.ts

### T-02 Billing mode and allowance model
- AC: AC-01, AC-02, AC-04 | Files: apps/web/src/components/usage/usageBilling.ts, apps/web/src/components/usage/usageBilling.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && npx vitest run src/components/usage/usageBilling.test.ts

### T-03 Cost basis strip, filters, pinned period and unpriced cells
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/web/src/components/usage/UsageCostBasis.tsx, apps/web/src/components/usage/UsagePage.tsx, apps/web/src/components/usage/UsageProviderChart.tsx, apps/web/src/components/usage/usageFilters.ts, apps/web/src/components/usage/usageFilters.test.ts, apps/web/src/components/usage/UsagePage.test.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && npx vitest run src/components/usage

### T-04 Headless fixture screenshots
- AC: AC-07 | Files: apps/web/tests/usage-dashboard, /Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023 | Test: headless Playwright fixture at 1440px dark/light and 390px

### T-05 Merge, release and installed check
- AC: AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023 | Test: exact-head CI green, release published by the release owner, installed version readback and headless screenshot of the installed /usage

### T-07 Correct pooled provider branding after CI guard failure
- AC: AC-01, AC-02, AC-07 | Files: apps/web/src/components/usage/UsageCostBasis.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/copilotIcon.test.tsx src/components/usage

### T-08 Measured-history forecast and responsive dashboard hierarchy
- AC: AC-09, AC-10 | Files: apps/web/src/components/usage/usageForecast.ts, apps/web/src/components/usage/usageForecast.test.ts, apps/web/src/components/usage/UsageOutlook.tsx, apps/web/src/components/usage/UsageFilterBar.tsx, apps/web/src/components/usage/UsagePage.tsx, apps/web/src/components/usage/UsagePage.test.tsx, apps/web/src/components/usage/UsagePage.refresh.test.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage

### T-09 Exact sampled chart interaction and accessible share visualization
- AC: AC-10, AC-11 | Files: apps/web/src/components/usage/UsageProviderChart.tsx, apps/web/src/components/usage/UsageProviderChart.test.ts, apps/web/src/components/usage/UsageShareBar.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage

### T-10 Forecast and visual interaction acceptance
- AC: AC-07, AC-09, AC-10, AC-11 | Files: apps/web/tests/usage-dashboard, /Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023 | Test: headless production-component fixture in dark/light at 1440px, 1024px and 390px, including forecast available/stale/insufficient/unpriced and pointer/keyboard chart pinning

### T-11 Responsive ranked model breakdown component
- AC: AC-03, AC-05, AC-10 | Files: apps/web/src/components/usage/UsageModelTable.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage src/components/copilotIcon.test.tsx

### T-12 Keep model drill-down scoped and partial costs explicit
- AC: AC-03, AC-06, AC-10 | Files: apps/web/src/components/usage/UsageModelDialog.tsx, apps/web/src/components/usage/UsageModelDialog.test.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/usage-cost-dashboard/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage

### T-06 Verify and close 1007
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1007-usage-and-cost-dashboard | Test: specweave verify and fresh-context review
