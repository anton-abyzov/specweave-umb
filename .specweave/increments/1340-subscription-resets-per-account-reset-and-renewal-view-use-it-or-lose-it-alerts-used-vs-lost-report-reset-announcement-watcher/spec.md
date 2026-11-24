# Subscription resets: per-account reset and renewal view, use-it-or-lose-it alerts, used-vs-lost report, reset-announcement watcher

## Problem

Anton pays for several subscriptions across several machines and loses quota every week because nothing says "this account resets in 9 hours and 60% of it is unused". The app already reads each account's windows and reset times, keeps 14 days of quota history and detects resets inside the forecast maths, but:

- No single view lists every subscription with its window, reset time, renewal date, banked resets and the machine that holds it. The data is spread over the Usage page, the host limits popover and the picker strip.
- `expiringQuota()` (`packages/shared/src/expiringQuota.ts`) finds quota about to be lost, but only model routing reads it. Nothing alerts the user.
- Reset detection (`resetBetween` in `packages/shared/src/usageLimitForecast.ts`) is private and records nothing, so there is no figure for what was lost at each reset.
- No field holds a subscription renewal date.
- Providers reset limits early without notice (Codex staff post it on X). The app learns of it only at the next usage read and never says so. `StatusMonitor` polls incident feeds only.

## Scope

In, SpecWithCode desktop app (`repositories/anton-abyzov/specwithcode`), web and server:

- A reset ledger: closed quota periods per account and window, kept for a year, with an RPC.
- Usage > Subscriptions: one row per account and machine.
- Use-it-or-lose-it alerts: app banner and desktop notification.
- A used-versus-lost report per account, week over week.
- A reset-announcement watcher with two sources: the account's own early reset (certain) and public announcements (context).

Out:

- Building airesets.dev. This spec only fixes the feed the app would read from it (see Approach).
- How usage is read per provider, the usage popover on the model chip, the Models settings section, every `providerLimit*` setting and `modelLanes.ts` routing. Increment 1339 owns these (split agreed with its thread on November 14, 2026).
- Moving a thread to another account automatically. The alert offers the action; the person starts it.
- iOS and Android.
- Reading X with stored credentials on the server. X is read only through the signed-in Chrome tools, by an optional routine.

## Acceptance Criteria

- [ ] AC-01: The server turns quota history into closed periods per account and window (`startedAt`, `endedAt`, `usedPercentAtReset`, `lostPercent`, `cause` of `scheduled`, `early` or `redeemed`), keeps 12 months on disk, survives a restart and serves them through `usageLimits.resets`. An account first seen at its limit, a rolling window ageing out, a restamped read from another machine and a whole window with no read produce no period.
- [ ] AC-02: Usage > Limits > Subscriptions lists every account on every connected machine: provider logo, plan, email, machine name, each window with what is left and a countdown to its reset, the renewal date, banked resets with the next expiry, and "lost at last reset". Offline machines show their last reading with its age. Unknown values read "Not reported", never 0.
- [ ] AC-03: A renewal date comes from the provider when it reports one (`renewsAt`); otherwise the person sets the renewal day once per account in the Subscriptions row, and it is stored per subscription on that machine's server.
- [ ] AC-04: When a weekly or monthly window is in its last two days, at least an hour from its reset, and the pace so far will leave at least 40% of it unused (a 5-hour window never warns; Anton, November 14, 2026: warn only when there is time to act and the projection is bad), the app shows one banner above the thread list naming the account, machine, what is left and the time to reset, and raises one desktop notification per account and window per period. The banner offers "Start a thread on it" and lists threads waiting on a limit that this account could run. Dismissing it holds until the next period. One switch under "Use quota before it resets" turns alerts off.
- [ ] AC-05: The same alert fires for a banked reset expiring within 24 hours and for a subscription renewing within 24 hours with unused quota.
- [ ] AC-06: Usage > Limits > Subscriptions shows a report:, per account and week, percent used and percent lost at each reset as stacked bars with a data table, a total "lost this week" and "lost last 4 weeks", and a token estimate only where it can be measured (one account of that provider active on the machine in the period and at least 5% used). Estimates are labelled as estimates. The report can be copied as Markdown.
- [ ] AC-07: When an account's window resets before its announced reset time, the app notifies once ("Codex reset early on m4: weekly back to 100%") and marks the period `early`. This needs no network source.
- [ ] AC-08: A server watcher reads the configured announcement feed at most every 30 minutes with a conditional request, keeps each event once by its source link, and shows events in a "Reset announcements" list with date, provider, kind (full reset, banked grant, limit change) and the source link. It notifies only for a full reset, banked grant or limit change on a provider the person has an account for, and never for an event older than 48 hours on first read.
- [x] AC-09: An optional routine, off by default, reads the listed staff and official accounts through the signed-in Chrome tools every 2 hours and records confirmed posts through `studio_reset_announcement_record`. It uses the everyday model, posts nothing, and stays quiet when nothing new is found.
- [ ] AC-11: The banner's main action is "Use it for new threads until it resets". It makes that account's model the default for new worker threads (never the project coordinator, never an open thread) in the projects the person picks, until the window resets. It ends by itself at the reset time, at an early reset, when the account has under 5% left or stops being usable, or when the person ends it; the saved default is never rewritten, so nothing has to be restored. While it runs, the model chip and the banner say "Codex Pro until 6:40 AM" with "End now". Threads waiting on another limit are offered a one-click move to it.
- [ ] AC-12: A reset the feed marks as promised or expected with a named source (for example a staff post saying "reset by end of day") raises the same banner for accounts of that provider with quota left: "Codex reset expected today: 62% left on m1 will be replaced. Use it for new threads until it resets." It shows the source link and says "expected", never "announced". A forecast number alone raises it only when the feed reports the forecast as better than its base rate; otherwise the forecast is shown in the Subscriptions view only.
- [ ] AC-13: Subscriptions is a dashboard (mockup `reports/dashboard-mockup.png`). One filter row scopes everything below it: range 1W, 4W (default), 12W, 1Y, and group by provider, account or machine. A KPI row leads with the efficiency score (ring, percent, change against the previous range), then left unused with the token estimate, what resets in 24 hours, and banked resets. "Efficiency by week" shows one column per week with a hover readout per provider; clicking a week filters the resets table to it. "By provider" lists each subscription's used percent against its target. The resets table is paginated (10 per page), sorted newest first, and a row opens in place to show use through the week against an even pace, the token estimate, the busiest day and how exact the figure is. Renewal day, last read and machine details live in the opened row, not in the table. Charts animate once on load and on range change, and not at all under reduced motion.
- [ ] AC-14: The efficiency score is, per closed period, used percent divided by the subscription's target (capped at 100), averaged over the range and weighted by plan price when the person entered one, else equally. The target is 100% unless the person sets "I plan to use" per subscription (for example 30% for Muse), so a subscription kept as a spare does not lower the score. Periods whose figure is an upper bound count but are marked. With fewer than two closed periods the score reads "Not enough history yet".
- [x] AC-10: Each slice is merged through a pull request with green required checks and an independent review by Meta Muse Wonderful, released through the app's release request, and shown with headless screenshots of the released build.

## Approach

### What exists and is reused unchanged

- Windows, reset times, banked resets: `ServerProviderUsageLimits` (`packages/contracts/src/providerUsageLimits.ts`), `resetCredits.nextExpiresAt`.
- History: `usageLimits.history`, `apps/server/src/usage/UsageLimitHistory.ts` (14 days).
- Accounts with machine names: `collectLimitAccounts` (`packages/shared/src/usageLimits.ts`).
- The threshold rule: `expiringQuota()`. No second rule is added.
- Feed polling pattern: `apps/server/src/statusPage/StatusMonitor.ts`.

### Split with 1339

1339 owns usage reads, the chip popover, settings and routing. This increment adds optional `planLabel` and `renewsAt` to `ServerProviderUsageLimits`; 1339 fills `planLabel` for Copilot and may add the identical field first. The alert switch is one row under "Use quota before it resets" in `apps/web/src/components/settings/ModelLanesSettings.tsx`; 1339 carries it into Settings > Models > "When a limit hits". 1339 will start feeding ACP limit replies into history, so first samples at 100% are expected (AC-01).

### Slice 1: ledger, Subscriptions view, report (AC-01, 02, 03, 06)

- `packages/shared/src/usageResetLedger.ts`: lift `resetBetween` out of `usageLimitForecast.ts` unchanged and re-export it there; `closePeriods(series, previous)` returns new closed periods. `cause` is `early` when the reset lands more than 10 minutes before the last known `resetsAt`, `redeemed` when the app's own redeem ran in that gap, else `scheduled`.
- `apps/server/src/usage/UsageResetLedger.ts`: runs after each history write, appends to `<stateDir>/usage-reset-ledger.json` (12 months, 5,000 periods), RPC `usageLimits.resets`.
- `packages/contracts/src/usageResetLedger.ts`: schemas. `providerUsageLimits.ts`: `planLabel?`, `renewsAt?`.
- Renewal day typed by the person: `subscriptionRenewals` in server settings, keyed by `subscriptionKey`.
- Web: `apps/web/src/components/usage/subscriptions/` (`SubscriptionsView.tsx`, `SubscriptionRow.tsx`, `ResetReport.tsx`, `subscriptionRows.ts`), a "Subscriptions" tab on the Usage page.
- Token estimate: tokens the machine spent on that provider in the period (`UsageService` hourly buckets) divided by percent used, times percent lost. `UsageBucket` has no account field, so the estimate is withheld when two accounts of one provider were active.

### Slice 1b: dashboard (AC-13, 14)

- Default range 4 weeks: weekly windows give four points per subscription, enough for a trend and short enough to act on; the chart always draws 12 columns so the range sits in context. 1Y uses monthly columns.
- `efficiency.ts` (pure, in `apps/web/src/components/usage/subscriptions/`): score, per-group scores, per-week series from ledger periods. Settings: `subscriptionTargets` and `subscriptionPrices` beside `subscriptionRenewalDays`.
- Use through the week comes from `usageLimits.history` (14 days), so it is drawn only for periods that recent; older rows show the figures without the line.
- Carried from the slice 1 review (round 2, ship): the token estimate must also be withheld when a second account of the provider was read in the period without closing one, so `usageLimits.resets` returns the account keys of its open cursors; a ledger file written before `creditSpentAt` keeps its old `creditSpent` flag for one reset.
- Charts are plain SVG in the app's tokens; colour by provider is fixed per provider, never by rank. The slice-1 rows and report table become the dashboard's table and opened row.

### Slice 2: alerts (AC-04, 05, 07)

- `packages/shared/src/quotaAlerts.ts`: pure `quotaAlerts(accounts, renewals, now)` built on `expiringQuota()`; alert id is account, window and period end, so one period alerts once.
- Dismissals and the on/off switch are settings (`quotaAlertDismissals`: per alert key, the dismissed period end; `quotaAlertsEnabled`), not a server file and RPC as first planned: settings already sync and merge by key, and one value per key keeps the map bounded (decided November 14, 2026). The early-reset notice comes from the ledger. The banner links to the Subscriptions view; "Start a thread on it" is replaced by the boost (AC-11) in the next PR.
- Web: `QuotaAlertBanner.tsx` above the thread list (a new app-wide slot; none exists today), and `Notification` through the existing permission path in `apps/web/src/notificationConnection.ts`.
- Use it until reset (AC-11): a time-boxed override, not a settings change. the `quotaBoosts` setting on the main machine: a list of `{ accountKey, instanceId, model, projectIds, label, windowId, until, startedAt }`, one per account, replaced whole by a patch (decided November 14, 2026: a setting syncs and needs no new file or RPC, like the dismissals). The new-thread model resolution reads it before the project's `defaultModelSelection`; `coordinatorModelSelection` is never read through it. Expiry is checked when a thread starts, so no timer has to fire and a restart or sleep cannot leave it stuck; the ledger's early-reset and the 5% floor end it sooner. The model for the boost is the provider's default worker model from 1339's lanes, not a new choice. Agreed with 1339 (November 14, 2026): this increment exports pure `currentQuotaBoost(boosts, projectId, nowMs)` returning `{ instanceId, model } | null` from `packages/shared/src/quotaBoost.ts`; 1339 calls it in `projectWorkerModel` (`apps/server/src/project/ProjectDelegation.ts`, not edited here) only when the caller named no model. The boost stores `instanceId` only; the model is `tierModelFor(provider, "regular", settings.modelTiers)` resolved at thread start. It returns null for per-token, Vertex, paid-router or unknown-billing instances (`packages/shared/src/providerFallback.ts`) and when the instance does not list the model.
- Each machine alerts for its own accounts. A machine also shows other machines' alerts in the banner, but only the machine that holds the account raises the desktop notification, so one account never notifies twice.

### Slice 3: announcements (AC-08, 09)

- `apps/server/src/resetAnnouncements/` modelled on `StatusMonitor`: `feeds.ts`, `ResetAnnouncementMonitor.ts`, store `<stateDir>/reset-announcements.json`.
- Default feed, live since September 2026: `GET https://airesets.dev/alert-feed.json` (`{ items: [{ id, provider, kind: "hard-reset" | "banked-reset" | "boost", evidence: "verified", headline, body, sourceUrl, publishedAt, path }] }`, 36 verified events, `ETag`, CORS open). Promised resets are in `https://airesets.dev/wire-fallback.json` (`kind: "reset-untyped"`, source link) and probabilities in `https://airesets.dev/forecast.json`, which today reports low confidence with no edge over the base rate, so AC-12 uses promises, not the forecast. The site's source is `anton-abyzov/ai-reset` (SpecWithCode project "AI Resets"); its hourly watch of X accounts already does what AC-09's routine would, so AC-09 stays a fallback. The feed stopped updating on October 17, 2026: the monitor shows the feed's last event date and says when it is older than 14 days. Earlier proposal, superseded: `GET https://airesets.dev/feed.json` returning `{ updatedAt, events: [{ id, provider: "codex" | "claude" | "grok" | "cursor" | "gemini" | "muse" | "copilot", kind: "full_reset" | "banked_grant" | "limit_change" | "boost" | "scheduled", at, audience, summary, sourceUrl, sourceKind: "primary" | "secondary" }] }` with `ETag`.
- Accounts for the routine: `@thsottiaux`, `@OpenAI`, `@OpenAIDevs`, `@AnthropicAI`, `@claudeai`, `@AIatMeta`, `@GoogleAI`, `@cursor_ai`. Community trackers used only to cross-check: `codex-resets.com` (the one Anton remembers), `codex-reset.com`, `reset-tracker.com/codex`. They disagree on dates, so a tracker alone never notifies.
- An announcement is context. The certain signal is AC-07, the account's own early reset; when both exist within 6 hours the notification links the post.

### Rejected

- Scraping X from the server: needs credentials and breaks often.
- A second threshold setting for alerts: `expiringQuota()` already encodes 24 hours and 40%.
- Showing lost tokens for every account: the app has no per-account token counts, and an invented number is worse than a percent.

### Risks

- Reset detection false positives would put wrong numbers in a report. The ledger uses the reviewed 1082 rule and adds fixtures for the three cases in AC-01.
- Banner noise. One banner at a time, worst first, dismissed per period.

- AC-09 as built (November 15, 2026): the routine is a personal-assistant template, "Reset announcement watch", offered under its Routines and off until saved; "Every 2 hours" is a choice in its form. It saves on the coordinator's provider at that provider's everyday (regular tier) model (PR 483, v1.0.319). It keeps the coordinator's model, and the form says why, when the everyday model bills per token, is missing, or reports no billing and was not the person's own choice in Settings; Save waits until the models load. `studio_reset_announcement_record` (agent threads only) refuses while "Read reset announcements" is off and takes only a link to a post on X or the provider's own site. The boost copy says "new worker threads": 1339's hook (PR 423) moves only agent-started worker threads with no named model, not routines or composer threads.
- Shipped (November 15, 2026): PR 430 (v1.0.312), PR 459 (v1.0.314), PR 468 and PR 477 (v1.0.316), each merged at a head Muse Wonderful reviewed "ship" with green Checks (records 13, 17, 19, 21 in reports/reviews/). Released-build screenshots: reports/released/ on the M4's installed 1.0.314 (slices 1 to 3); slice 4's routine template and record tool are shown by the headless fixture only (reports/slice-4/), because the M4 had not installed 1.0.316 at closure. Proof limit: no released-build screenshot of slice 4.
- The full configured verify passed at closure (reports/verify.md, PASS, 15/15 ACs); T-12's Test reruns the ACs with 1340's focused tests because `task done --run` stops at 20 minutes and the full run takes about 40.
- Verify at closure first ran the shared app checkout at an older main (013d05387); its two failures (fleet `test_helpers_and_gh_run_outside_darwin_background` 60 s subprocess timeout, server `liveDatabaseLocks.test.ts` SIGBUS expectation) pass alone on main 2bf46fea2 and are outside this increment's files.
- Follow-up, not built: the fallback feed (`wire-fallback.json`, `reset-untyped`) also carries posts saying a reset already happened ("Codex Day 10 reset reported done"); the list labels them "Reset expected". Mapping them needs the feed to type them.
- Closure exceptions (November 15, 2026, closure review record 22). AC-09's everyday model shipped in PR 483 (v1.0.319, reviews 23 to 26). AC-10's released-build screenshots taken on 1.0.319 (November 15, 2026): reports/released/subscriptions-v1.0.319-dark.png, reset-announcements-v1.0.319-dark.png and reset-watch-routine-v1.0.319-dark.png (the watch form, "Every 2 hours" picked, not saved; on Claude the coordinator's Opus 5.5 already is the everyday tier, so the form names it; no plan-limits line because that model's billing is not reported). Narrowed: AC-05's renewal warning fires only when one of that plan's windows also qualifies under the projection rule; a renewal alone raises nothing (accepted in review record 13). Open follow-up: the fallback feed labels every `reset-untyped` post "Reset expected", including posts saying a reset already happened (AC-08, AC-12), until the feed types them.
## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Lost quota is reported in percent of each window, with a token estimate only where measurable.
- D-02 Renewal date is typed once per account when the provider does not report it.
- D-03 Alerts are on by default; the X routine is off by default.
- D-04 The alert offers an action and never moves a thread by itself. The boost (AC-11) starts only when the person clicks it, covers new worker threads only, and leaves the coordinator alone (Anton, November 14, 2026).
- D-05 Ledger retention is 12 months.
### Open
- none

## Review
- Reviewer: meta (muse-wonder-1.0)
- Depth: deep
- Required: yes

## Tasks

### T-01 Reset ledger maths and contracts
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/usageResetLedger.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/usageResetLedger.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/usageLimitForecast.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/usageResetLedger.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/providerUsageLimits.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/usageResetLedger.test.ts packages/shared/src/usageLimitForecast.test.ts

### T-02 Server ledger store and usageLimits.resets
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageResetLedger.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageResetLedger.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageResetLedgerStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageResetLedgerStore.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/server.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/usage/UsageResetLedger.test.ts apps/server/src/usage/usageResetLedgerStore.test.ts

### T-03 Subscriptions view
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionRow.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/subscriptionRows.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/subscriptionRows.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageLimits.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/usageResetLedgerState.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/packages/contracts/src/usageResetLedger.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageResetLedgerStore.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage

### T-04 Used-versus-lost report
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/ResetReport.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/resetReportModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/resetReportModel.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage/subscriptions

### T-04b Subscriptions dashboard and efficiency score
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/efficiency.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/efficiency.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsDashboard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/EfficiencyChart.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/ResetsTable.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/subscription-resets/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/subscription-resets/verify.mjs | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode/apps/web && node node_modules/vite-plus/bin/vp test run --project unit src/components/usage/subscriptions

### T-05 Ship slice 1
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/docs/user/usage-subscriptions.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released 0f3da544d830657e235b7827a285bf1aa3f89c84

### T-06 Alert rule, server state and early-reset notice
- AC: AC-04, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/quotaAlerts.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/quotaAlerts.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/quotaAlerts.test.ts

### T-07 Banner, desktop notification and the settings row
- AC: AC-04, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/QuotaAlertBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/QuotaAlertBanner.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/quotaAlertNotifications.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelLanesSettings.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/usage/alerts

### T-07b Use it for new threads until it resets
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/quotaBoost.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/quotaBoost.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/serverSettings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/QuotaAlertBanner.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/quotaBoost.test.ts packages/shared/src/quotaAlerts.test.ts

### T-08 Ship slice 2
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/docs/user/usage-subscriptions.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released 89d2a9518cbd983f46b2688285dc8b0fe33a589e

### T-09 Announcement monitor, store and list
- AC: AC-08, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/resetAnnouncements/ResetAnnouncementMonitor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/resetAnnouncements/feeds.ts, repositories/anton-abyzov/specwithcode/apps/server/src/resetAnnouncements/ResetAnnouncementMonitor.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/resetAnnouncements.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/ResetAnnouncements.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/resetAnnouncements

### T-10 Record tool and the optional Chrome routine
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/resetAnnouncements/recordTool.ts, repositories/anton-abyzov/specwithcode/apps/server/src/resetAnnouncements/recordTool.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/resetAnnouncements/ResetAnnouncementMonitor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/resetAnnouncements/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/resetAnnouncements/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/resetAnnouncements/handlers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/routineTemplates.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/routineTemplates.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/RoutineQuickForm.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useRoutineModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectRoutines.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/QuotaAlertBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/QuotaAlertBanner.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/subscription-resets/verify.mjs, repositories/anton-abyzov/specwithcode/docs/user/usage-subscriptions.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/resetAnnouncements/recordTool.test.ts apps/server/src/mcp/toolkits/resetAnnouncements packages/shared/src/routineTemplates.test.ts

### T-11 Ship slice 3
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/docs/user/usage-subscriptions.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released 3a8cb9d4188c4d739506a3e76f9284058496914a

### T-12 Verify and close 1340
- AC: AC-10 | Files: .specweave/increments/1340-subscription-resets-per-account-reset-and-renewal-view-use-it-or-lose-it-alerts-used-vs-lost-report-reset-announcement-watcher/reports/verify.md | Test: specweave verify 1340 --cmd "cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1340-subscription-resets/repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/resetAnnouncements apps/server/src/mcp/toolkits/resetAnnouncements packages/shared/src/quotaAlerts.test.ts packages/shared/src/quotaBoost.test.ts packages/shared/src/routineTemplates.test.ts"
