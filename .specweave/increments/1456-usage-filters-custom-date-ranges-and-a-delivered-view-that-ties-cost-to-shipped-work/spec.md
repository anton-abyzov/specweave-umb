# Usage filters, custom date ranges and a Delivered view that ties cost to shipped work

## Problem

Anton reads Usage to judge what the subscriptions buy. On November 24, 2026, Usage > Cost showed at least $38,169.40 API-equivalent over 30 days (Claude Code $34,672, Codex $3,342, Grok Build $155, OpenCode unpriced). Three things are missing:

- **Filters.** Cost and Tokens can be narrowed by clicking a provider row or searching a model, but there is no visible filter control. Limits and Machines have none at all. Nothing filters by project.
- **Date ranges.** The page offers only Past 24h, 7, 30 and 90 days (`usageShortcuts.ts` `WINDOW_OPTIONS`, saved as `windowDays: 1|7|30|90`). There is no way to read, for example, November 1 to November 15. Machines has its own custom range (`SharePeriod` custom, 92 days back from today), and Limits has its own 1W/4W/12W/1Y periods. So the page shows two or three ranges at once.
- **What the money delivered.** Nothing connects cost to work. The data exists: app turns carry the thread, threads resolve to increments (`ThreadIncrementProgress.ts`: manual link, claim file, branch, checkpoint, name), and ledgers record when tasks were done and when PRs merged.

Measured on M5 (November 24, 2026, 329 threads with turns in the last 30 days, weighted by token use):

| Source | Share |
|---|---|
| Claim files | 46.4% |
| Parent thread is bound | 5.6% |
| Number in the title | 2.6% |
| Increment branch | 2.4% |
| Coordinators | 5.8% |
| No increment | 36.9% |

`thread_increment_links` has no rows. The no-increment share is mostly real work outside increments, such as "GTA 6 livestream kit" and "OBS audio and wired network", not missed links. The view has to show that share honestly, not hide it.

## Scope

In:

- One toolbar on the Usage page with the range (presets plus Custom), Machines (the existing filter, moved), Providers, Model and Project.
- A per-tab filter matrix. A filter a tab cannot apply is shown as not applied, never silently ignored.
- Custom date ranges applied to Cost, Tokens, Machines and the new Delivered tab.
- A new Delivered tab and a per-machine `usage.deliveredReport` RPC. It lists increments with tasks done, merged or closed in the range, or with spend in it, and shows what each cost by provider and model. Coordinators, other threads and use outside the app appear as their own rows.
- "Copy report" (Markdown) on Delivered, honouring the range and filters. The Limits "Copy 4-week report" names the provider filter.

Out:

- Filters inside the Models > Limits by account popover. It stays a summary that links to the page.
- An account filter on Cost and Tokens: their records carry no account. Accounts stay in Limits and Machines.
- Splitting one thread's cost across several increments by time.
- Ranges longer than 92 days.
- Plan prices, savings or "real spend". API-equivalent stays an estimate, not a bill.
- Writing thread-to-increment links from this view.

## Acceptance Criteria

- [ ] AC-01: The toolbar shows Past 24h, 7 days, 30 days, 90 days and Custom. Custom opens From and Until date fields.
  - Until may not be after today, From may not be after Until, and the range may span at most 92 days. Each rule shows its own message, and Apply stays disabled while a rule fails.
  - Once applied, the button reads the range, such as "Nov 1 – Nov 15". The range survives closing and reopening the page.
  - Cost, Tokens, Machines and Delivered request exactly those days.
- [ ] AC-02: Limits keeps its reset-aligned periods (1W, 4W, 12W, 1Y) and says so beside them: "Limits counts whole reset weeks, not the page range."
  - When the range ends before today, the Cost forecast and the "now" billing chips are hidden, and a line says the range is in the past.
- [ ] AC-03: Providers is a multi-select menu listing every provider that has usage, limits or registry rows on the selected machines, including GitHub Copilot and ACP registry agents.
  - A selection narrows Cost, Tokens, Delivered, Machines (accounts of that provider) and Limits (subscriptions and accounts of that provider).
  - A selected provider with no measured cost in the range reads "No measured cost for <provider> in this range", never $0.
- [ ] AC-04: Model search applies to Cost, Tokens and Delivered. Machines applies to every tab. Project applies to Delivered only; every other tab names why it is not applied (Machines: subscription shares and outside estimates are per account, not per project).
  - Under the toolbar, each active filter the current tab cannot apply is named with the reason, for example "Project is not applied on Cost: its records carry no project."
  - Clear filters resets every filter but not the range.
- [ ] AC-05: Each machine answers `usage.deliveredReport {sinceDay, untilDay, timeZone}` (capability `usageDeliveredReport`, scope `diagnostics:read`, at most 92 days).
  - Costs use the Cost tab's basis: transcript records mapped from native session to thread, plus recorded turns of drivers without transcripts, with the same price table and overrides.
  - It returns per increment: cost, tokens, records and unpriced records; a per provider and model split; the threads behind it, each with its binding; tasks done in the range out of the total; and closed or merged evidence with dates.
  - Separately it returns coordinators, other app threads (largest first, at most 20 named), use outside the app on that machine, and the machine's measured total.
  - Test: those parts add up to the measured total.
- [ ] AC-06: A thread counts toward exactly one increment, in this order:
  - manual link, claim, branch, checkpoint, name;
  - then the increment of its parent thread (subagents and delegated workers).
  - Coordinator threads are never assigned to an increment.
  - "Name" and "checkpoint" bindings are labelled "matched by title". An increment created before the range start is flagged "spend before <date> not shown".
- [ ] AC-07: The Delivered tab shows:
  - a strip with increments delivered (closed or merged in the range), tasks done, the attributed cost with its share of measured cost, and the median cost per delivered increment;
  - a table sorted by cost (Increment, Status Closed / Merged / In progress, Tasks done, Threads, Top model, Cost). A row expands to its provider and model split and its threads with their bindings;
  - the rows Coordinators, Other threads and Outside the app.
  - Increments from several machines merge by project title and increment id.
  - Machines that did not answer, or run a version without Delivered, are named, and the totals are marked incomplete.
- [ ] AC-08: "Copy report" on Delivered copies Markdown with the range, the active filters, the strip, the increments table and the four non-increment rows. The Limits "Copy 4-week report" header lists an active provider filter.
- [ ] AC-09: Unit tests cover range validation and preferences, the filter matrix, the Delivered core with reconciliation and binding order, and the client merge and report. Typecheck passes. Headless screenshots of the toolbar, Custom range, Delivered and a not-applied note are in `reports/`.

## Approach

1. Mockup: `reports/mockup-delivered.html`, screenshotted headless before code.
2. Shared and pure code (`packages/shared/src/usageRange.ts`, new):
   - `UsageRange` is preset days or custom since and until; it has validation and a label, and builds the `UsageSummaryInput` window.
   - Preferences gain an optional `range` (v1 stays decodable).
   - `apps/web/src/components/usage/usageScope.ts` (new) holds the filter state and the matrix `FILTER_SUPPORT[tab]`.
   - The provider key is the driver kind: Cost buckets map `UsageProviderKind` to the driver through `usageBilling.ts`, and registry agents use their driver.
3. Toolbar: `UsageToolbar.tsx` and `UsageCustomRange.tsx` (new). They are taken out of `UsagePage.tsx`, which is at 1,476 lines, so the page shrinks.
4. Tabs:
   - Cost and Tokens use the existing bucket filter, keyed by driver.
   - Machines takes the page range as `SharePeriod` custom (the clamp to "92 days back from today" becomes "span at most 92 days") and filters accounts by driver.
   - Limits filters subscriptions and accounts by driver and shows the reset-weeks note.
5. Contract `packages/contracts/src/usageDelivered.ts` (new): its own RpcGroup, following `usageMachineReport.ts`. The capability flag goes in `environment.ts`, and the keybinding `usage.delivered` goes in `keybindings.ts`.
6. Server:
   - `apps/server/src/usage/usageDeliveredCore.ts` (pure): grouping, binding precedence, coordinator split and reconciliation.
   - `UsageDeliveredReport.ts`: it reuses `visitRecords`, the owned-session query and `totalsForTurn` as in `UsageMachineReport.ts`, maps sessions to threads, and resolves threads per project through `ThreadIncrementProgressService.read` in chunks of 100.
   - Increment evidence: `metadata.json` closed states with `updated`; ledger notes "Merged …#N" and PR merges for merged; task `doneAt` for tasks done.
7. Client: `apps/web/src/state/usageDelivered.ts` and a client-runtime call in a new file (`server.ts` is at 1,499 lines). `usageDeliveredMerge.ts` merges machines by project title and increment id and applies the filters.
8. UI: `delivered/UsageDeliveredSection.tsx`, `DeliveredIncrementRow.tsx` and `deliveredReport.ts` (Markdown).
9. Headless fixture: extend `apps/web/tests/usage-dashboard/` with Delivered mocks. Screenshots go to `reports/`.

Rejected:

- An account filter on Cost and Tokens: buckets have no account, so it would mislead.
- Spreading coordinator cost over increments: it invents precision.
- `turnTokenUsage` alone as the cost basis: it misses native subagents and would not reconcile with Cost.
- Keying "delivered" on `status: completed` alone: 1447 still says `active` after its merge.

Risks:

- Binding is as of now: a thread whose claim moved to a later increment counts entirely there.
- Machines hold different umbrella checkouts, so increment status can differ. The merge takes the most advanced state: closed, then merged, then in progress.
- Resolving many threads reads many ledgers. Reads share the service's cache, and the RPC answers within the existing usage scan.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 "The full report" → the Usage page itself (the Models popover links to it), plus its copied Markdown reports. Filters go on the page and into "Copy report", not into the popover.
- D-02 Which filters → Provider (every tab, the most valuable cut: cost is 91% Claude), Model (Cost, Tokens, Delivered), Machine (every tab, existing), Project (Delivered only: its records carry a project; Machines shares are per account, so it says so instead). No account filter outside Limits and Machines.
- D-03 Range cap → custom spans at most 92 days on every range-driven tab, matching the machine report limit, so one range works everywhere. The 90-day preset stays.
- D-04 Limits range → stays reset-aligned (1W/4W/12W/1Y). Cutting reset windows at arbitrary dates would misstate "left unused". It says so on screen.
- D-05 "Delivered" states → Closed (metadata closed states), Merged (a ledger merge note or a merged PR in the range), In progress (tasks done in the range or spend, not closed or merged). Status alone is not enough.
- D-06 Attribution → one increment per thread, using the existing resolver order and then the parent thread. Coordinators and other threads get their own rows and are never spread.
- D-07 (review) Past 24h on Machines and Delivered → whole days (yesterday and today), labelled with the real days and a scope note; Cost keeps the rolling 24 hours.
- D-08 (review) Delivered needs diagnostics:read and filesystem:read, on the server and in the UI, because it shows increment titles, tasks and merges like the increment RPCs.
- D-09 (review) "Delivered" counts increments closed or merged inside the range (`deliveredInRange`); the row still shows the current state. Fully unpriced deliveries stay out of the median and highest; the median is "per priced delivery" and a lower bound when partly unpriced.
- D-10 (review) Overlap → machines with exactly the same transcript folder set count once and are named; a partial overlap keeps both, warns, and blanks the combined Tied and median figures. Known limit: two hosts reading one mounted folder have different fingerprints and count twice, as on Cost and Machines; a host-independent source identity is a follow-up.
- D-11 (review) Cursor account history is left out of Delivered and disclosed.
### Open
- none

## Tasks

### T-01 Mockup of the toolbar, Custom range and Delivered tab
- AC: AC-01, AC-07 | Files: [.specweave/increments/1456-usage-filters-custom-date-ranges-and-a-delivered-view-that-ties-cost-to-shipped-work/reports/mockup-delivered.html, .specweave/increments/1456-usage-filters-custom-date-ranges-and-a-delivered-view-that-ties-cost-to-shipped-work/reports/mockup-delivered.png] | Test: test -s .specweave/increments/1456-usage-filters-custom-date-ranges-and-a-delivered-view-that-ties-cost-to-shipped-work/reports/mockup-delivered.png

### T-02 Range model, preferences and filter matrix
- AC: AC-01, AC-02, AC-04 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/usageRange.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/usageRange.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/usageScope.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/usageScope.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/usagePagePreferences.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/usagePagePreferences.test.ts] | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/usageRange.test.ts apps/web/src/components/usage/usageScope.test.ts apps/web/src/components/usage/usagePagePreferences.test.ts

### T-03 Toolbar with Custom range, Providers, Model and Project; page uses it
- AC: AC-01, AC-02, AC-03, AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageRangeControl.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageScopeBar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageEnvironmentFilter.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageToolbar.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsagePage.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/usageShortcuts.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/keybindings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsagePage.test.tsx] | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/usage/UsagePage.test.tsx src/components/usage/UsageToolbar.test.tsx

### T-04 Machines follows the page range and provider; Limits filters by provider
- AC: AC-01, AC-02, AC-03, AC-08 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/machines/UsageMachinesSection.tsx, repositories/anton-abyzov/specwithcode/packages/shared/src/usageMachineShareView.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageLimits.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/resetReportModel.ts] | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/usageMachineShareView.test.ts apps/web/src/components/usage/subscriptions/resetReportModel.test.ts

### T-05 Delivered contract and server report
- AC: AC-05, AC-06 | Files: [repositories/anton-abyzov/specwithcode/packages/contracts/src/usageDelivered.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageDeliveredCore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageDeliveredCore.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageDeliveredReport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageMachineReport.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts] | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/usage/usageDeliveredCore.test.ts

### T-06 Delivered client state, merge and tab
- AC: AC-03, AC-04, AC-07, AC-08 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/state/usageDelivered.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/delivered/usageDeliveredMerge.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/delivered/usageDeliveredMerge.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/delivered/UsageDeliveredSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/delivered/deliveredReport.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/delivered/deliveredFixtures.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/delivered/DeliveredTable.tsx] | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/usage/delivered

### T-07 Headless screenshots and typecheck
- AC: AC-09 | Files: [repositories/anton-abyzov/specwithcode/apps/web/tests/usage-dashboard/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/usage-dashboard/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/usage-dashboard/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/usage-dashboard/deliveredFixture.ts, .specweave/increments/1456-usage-filters-custom-date-ranges-and-a-delivered-view-that-ties-cost-to-shipped-work/reports/] | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json
