# Usage by machine per subscription: charts, drill-down and an outside-SpecWithCode estimate

## Problem

Anton runs one subscription on several machines (the same Codex account on linux-mini and the M4, Claude accounts that move between machines). SpecWithCode's Usage page shows tokens per provider and a limit percent per account, but nothing connects the two: usage buckets carry `(day, provider, model, source folder)` and no account, and the merged view drops which machine a bucket came from. So he cannot answer "who used this subscription this week: the M4, linux-mini, the M5, or something that is not SpecWithCode at all?".

Evidence on linux-mini (November 20, 2026): `usage-limit-history.json` holds four Claude accounts read by one provider instance within 14 days, so a folder cannot stand for an account; 98% of this week's Claude tokens and 97% of Codex tokens come from sessions a SpecWithCode thread owns, the rest from `claude` in a terminal and `codex exec`; the M4's Claude account reads 100% of its weekly limit while linux-mini recorded only part of that.

His words: "which machines are using which subscription mostly ... or maybe it was used externally ... somebody was using Claude with my subscription, but outside of SpecWeave. Brainstorm and build beautiful charts. Increase the way we report it with the grouping logic."

## Scope

In (app repository `anton-abyzov/specwithcode`):

- A per-machine report, read over the existing machine connections: recorded usage per account, day, model, project and origin (a SpecWithCode thread, or a session on that machine no thread owns).
- An account timeline per provider instance, so a session is charged to the account that was signed in when it ran.
- Shared pure logic that merges machines per subscription and estimates use outside every reporting machine.
- Web and desktop: a Machines tab on the Usage page with a bar per subscription split by machine, a per-day trend with the reset marker, drill-down by model, project and day, a table view, light and dark.
- iOS and Android app: a By machine section on the Usage screen from the same shared logic.
- Unit tests, a headless fixture, an adversarial review, a report with real-data screenshots.

Out: a release; changing the machine palette; reading any vendor's usage with a token the app does not already read; server-side fleet aggregation (each client merges the machines it reaches); usage of providers that keep no local record and run no SpecWithCode turn.

## Acceptance Criteria

- [ ] AC-01: Each machine answers `usage.machineReport` for a day range with cells `(day, account, model, origin, project)` holding tokens, API-equivalent cost, requests and sessions, plus an hourly series per account for the last 14 days. Providers with local transcripts (Claude, Codex, Grok) come from the transcript scan; providers without (Copilot and other ACP agents) come from the turns SpecWithCode recorded.
- [ ] AC-02: A session is charged to the account signed in on its provider instance when it ran: recorded account spans first, then the limit history's nearest reading within 12 hours (any distance when the driver only ever read one account); a driver with no readings uses the instance's current account; anything else is account not known, never a guess between several accounts; the report says which rule named each account.
- [ ] AC-03: A session whose native id a SpecWithCode thread owns counts as "in SpecWithCode" with that thread's project; any other session on the machine counts as "outside the app on this machine" (measured, not estimated).
- [ ] AC-04: The client merges machines by account key, never counts a transcript folder twice when two environments read the same one, and keeps a machine's last report so an offline machine shows as "last reported <when>" instead of vanishing. A machine too old to answer falls back to its usage summary when it has one account for that provider, marked as without the in-app split.
- [ ] AC-05: Use outside every reporting machine is estimated per subscription as the provider's reported consumption (weekly-limit percent points gained in the period, across resets) minus what the machines recorded, converted with a rate calibrated from the same account's history. It is always labelled an estimate with a confidence (high, medium, low), the time its source was last read, and the reasons that lower it. With too little history, an offline machine that holds the account, or no percent reading, it says why no estimate exists instead of showing zero.
- [ ] AC-06: Usage > Machines shows one segmented bar per subscription, split by machine in the machine's own colour, with the in-app and outside-the-app parts of a machine told apart, and a hatched "Outside your machines (estimate)" part; subscriptions sort by use.
- [ ] AC-07: A per-day stacked trend for the selected subscription over the chosen period (last 7 days, the reset window, last 14 or 30 days, a custom range), with a marker at each limit reset inside the range.
- [ ] AC-08: Selecting a machine or a bar part opens a drill-down by model, project and day for that subscription and machine.
- [ ] AC-09: Identity is never colour alone: every part has a legend entry and a tooltip on hover and keyboard focus, parts wide enough carry the machine's short name, a table view lists every number, and the charts pass text contrast in light and dark.
- [ ] AC-10: The mobile Usage screen shows the same per-subscription split by machine with the estimate line, from the same shared logic.
- [ ] AC-11: Unit tests cover the account timeline, the report core, the merge and the estimator; a headless fixture checks the charts at desktop and phone widths in light and dark; the report holds screenshots of the real charts over this machine's data and any other machine reached.
- [ ] AC-12: An adversarial review by the project's reviewer order (Gemini 4 Neon, then GPT-6.2 Sol) is recorded, and every finding fixed or answered.

## Approach

Data model, decided before the code:

1. What a machine records. Claude, Codex and Grok write every response to local transcripts with tokens, model, time and a session id; the existing scan already prices and de-duplicates them, and it also sees sessions run outside the app. Copilot and other ACP agents leave no transcript, but each SpecWithCode turn stores its tokens (`turnTokenUsage`) with the provider instance, the run's model and the start time. The report takes the transcript scan where one exists and recorded turns elsewhere, so nothing counts twice.
2. Account identity. A transcript folder belongs to a provider instance, and an instance changes accounts. A small store records, per instance, spans of the account key the limits reader saw (`<driver>:<email>`, the key the Limits tab already uses). Before the store existed, the 14-day limit history gives the nearest reading, but only within 12 hours unless the driver ever read a single account; real data showed an unbounded guess charging old sessions to whichever account was read first.
3. Origin. Native session ids the app owns come from `provider_threads` and `run_attempts`; the same join names the thread's project.
4. Fleet-wide. No new transport: the client asks each connected machine, as it does for the usage summary and the limit history, and merges by account key. Each cell names its transcript folder's fingerprint, so two environments on one machine never double count.
5. Outside estimate. For one account's weekly (else monthly) window, the history gives percent points consumed over time, summed across resets. Recorded cost per hour gives what the machines explain. Chunks of at least 4 points give ratios of recorded cost per point; where only the machines used the account the ratio is the true rate, and outside use only lowers it, so the rates are the weighted 80th and 50th percentiles of chunks with recorded use. They give a low and a high figure (consumed points minus recorded cost over each rate, never below zero) and the estimate is their midpoint, reported with a confidence from the number of chunks, their spread, history coverage and whether every machine that holds the account reported. Below the rounding margin (2 points or 5 percent) it reads "none detected". Points consumed are gains over the period's highest reading, so two feeds that round differently are not counted twice, and a fall to under half is a reset even when the reset time did not move (both seen in real history).
6. Grouping. Subscription first, then machine, then origin; drill-down by model, project, day.

Files, in order: `packages/contracts/src/usageMachineReport.ts` and the RPC in its own group `WsUsageMachineReportRpcGroup`, registered in `server.ts`; `apps/server/src/usage/usageAccountSpans.ts`, `usageMachineReportCore.ts`, `UsageMachineReport.ts`, a record visitor in `UsageService.ts`; `packages/shared/src/usageMachineShare.ts`, `usageMachineShareView.ts` (the view model web and mobile share) and `usageOutsideEstimate.ts`; `packages/client-runtime` command; `apps/web/src/components/usage/machines/*` and the Machines tab in `UsagePage.tsx`; `apps/mobile/src/features/usage/UsageByMachineSection.tsx`; fixture `apps/web/tests/usage-machine-share/`.

Charts follow the dataviz method: a tall segmented bar for "one whole split into parts", a stacked column chart for the split over time, one axis, 2 px surface gaps, a legend plus sparing direct labels, per-mark tooltips, a table view. The machine palette is the app's own (`[data-machine-color]`); as a set it fails the categorical colour-blind checks (amber and orange sit 1.6 apart), so colour only supports the names.

Rejected: adding account fields to `UsageBucket` (older clients would merge the extra buckets wrongly); a server that polls its peers (a second transport and stale copies); showing the estimate as a plain number; a new palette for machines in charts (a machine must look the same everywhere).

Risks: the weekly limit is not exactly proportional to API-equivalent cost, so the rate is noisy when the model mix shifts; constant outside use in every chunk hides inside the rate, so the estimate is a floor; percent readings are whole numbers.

## Decisions

### Asked
- none (the request names the views, the estimate rule, the periods and the reviewer order)
### Defaulted (change any before sw-do)
- D-01 The weight for shares is API-equivalent cost; tokens when a cell has no price; requests as a third measure → cost is the only weight comparable across models.
- D-02 "Outside SpecWithCode" has two parts shown apart: measured sessions on a machine that no thread owns, and the estimate of use on no reporting machine.
- D-03 The estimate uses the account-wide weekly window, else the monthly one; model-scoped and 5-hour windows are not used.
- D-04 The report RPC needs the same scope as the usage summary (`diagnostics:read`).
- D-05 A machine's last report is cached on the viewing device for 14 days.
- D-06 Mobile shows the split and the estimate as a third Usage tab, Machines, without the trend and drill-down.
- D-07 A subscription whose use has no price is shown in tokens, after the priced ones; a signed-in subscription with no use in the period is one line, not a card.
- D-08 A limit reset is found by placing each reading in a window by the reset time it carries (one still ahead ends its window, one that has passed began it): two readings in different windows have one reset between them, two in the same window have none. Readings without a reset time fall back on a clear fall in the percent, and a restart counted on one records the window it opened. Reached after review rounds 4 to 12 each broke a rule layered on the last; checked against the reset schedule itself by a randomized test.
- D-09 A reading that drops and is back within 30 minutes is a misread, not a reset, unless the reset times say the window turned over; when it fell to under half, the estimate says how it was read and its confidence is at most medium.
- D-10 In the drill-down, a project worked on from two machines is one row, matched by its title; two projects of one machine that share a title stay separate.
### Open
- none

## Tasks

### T-01 Contract and server report
- AC: AC-01, AC-02, AC-03 | Files: packages/contracts/src/usageMachineReport.ts, packages/contracts/src/usageLimitHistory.ts, apps/server/src/usage/usageAccountSpans.ts, apps/server/src/usage/usageMachineReportCore.ts, apps/server/src/usage/UsageMachineReport.ts, apps/server/src/usage/UsageService.ts, apps/server/src/usage/UsageLimitHistory.ts, apps/server/src/server.ts | Test: vp test run apps/server/src/usage/usageAccountSpans.test.ts apps/server/src/usage/usageMachineReportCore.test.ts

### T-02 Shared merge and outside estimate
- AC: AC-04, AC-05 | Files: packages/shared/src/usageMachineShare.ts, packages/shared/src/usageMachineShareView.ts, packages/shared/src/usageOutsideEstimate.ts | Test: vp test run packages/shared/src/usageMachineShare.test.ts packages/shared/src/usageOutsideEstimate.test.ts

### T-03 Web and desktop Machines tab
- AC: AC-06, AC-07, AC-08, AC-09 | Files: apps/web/src/components/usage/machines/, apps/web/src/components/usage/UsagePage.tsx, apps/web/src/components/usage/usageShortcuts.ts, packages/client-runtime/src/state/server.ts | Test: vp test run packages/shared/src/usageMachineShareView.test.ts apps/web/src/components/usage/UsagePage.test.tsx apps/web/src/components/usage/usageShortcuts.test.ts

### T-04 Mobile By machine section
- AC: AC-10 | Files: apps/mobile/src/features/usage/UsageByMachineSection.tsx, apps/mobile/src/features/usage/UsageRouteScreen.tsx | Test: vp test run apps/mobile/src/features/usage/usageByMachine.test.ts

### T-05 Headless fixture, real-data screenshots and report
- AC: AC-11 | Files: apps/web/tests/usage-machine-share/ | Test: node apps/web/tests/usage-machine-share/verify.mjs /absolute/report-dir

### T-06 Adversarial review, PR, merge
- AC: AC-12 | Files: none | Test: gh pr checks
