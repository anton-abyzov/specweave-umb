# Subscription effectiveness index: one click from the usage ring, backfilled from limit history

## Problem

Anton asked where his index of how well he uses his subscriptions is: does he burn each one to zero before it resets, or leave quota on the table. The Subscriptions dashboard existed but sat three clicks deep under Usage > Limits, and it was empty: the reset ledger only records resets it watches live, it started after the last weekly resets, and it never read the 14 days of limit history the app already keeps. The history alone shows six weekly resets between November 4 and 14, 2026 (Claude 100, 69, 97, 99, 88%; Codex 98%).

## Scope

In: a startup backfill of the reset ledger from the limit history; a "Used before reset" summary at the top of the usage ring's panel (index ring, one row per provider with its logo on the left, a three-bar sparkline of the last two weeks and this week's projection, the next reset with projected leftover); an "Effectiveness" button that opens Usage on Limits > Subscriptions; provider logos to the left of provider names in the Subscriptions dashboard groups and resets table. Out: a session-window (5-hour) index, which stays out of the weekly score; a redesign of the existing Subscriptions dashboard charts.

## Acceptance Criteria

- [ ] AC-01: On startup the ledger adds the weekly and monthly resets the limit history saw and it lacks, with model scope from the window id, never duplicating a reset it already holds, and keeping a weekly and a monthly window with one id apart.
- [ ] AC-02: Opening the usage ring's panel shows "Used before reset" over the last four weeks, a row per provider with its logo left of its name, the last two weeks and this week's projection, the average, and the next reset with projected leftover.
- [ ] AC-03: "Effectiveness" in that panel opens Usage over the app on Limits > Subscriptions in one click.
- [ ] AC-04: Provider names in the Subscriptions dashboard group rows and resets table carry the provider logo on their left.
- [ ] AC-05: Shipped in a released build after an independent xhigh review and green Checks.

## Approach

Server: `backfillLedger(state, history)` in `usageResetLedgerStore.ts` runs `resetPeriods` per history series that is a ledger window, skips any period whose read-to-reset span overlaps one already recorded for the same account, kind and window, and dates an open cursor's start from the last backfilled reset. `UsageResetLedger.make` reads the history file once after decoding the ledger and bumps the version when it added periods, so the next flush saves them. The history file name moves to the plain store module so the ledger service does not import the history service (keeps the import graph flat, see the TS2589 note on `ws.ts`).

Web: `effectivenessIndex.ts` is pure over `accountWidePeriods` (model slices never count twice) and `subscriptionRows` (live windows), with `projectedUnusedPercent` for this week. `EffectivenessSummary.tsx` renders it with `ProviderInstanceIcon` and the existing primary chart colour; the panel mounts it above Limits by account. `openSubscriptionsSheet()` in `usageSheetStore.ts` sets the Limits view key and opens the sheet.

Rejected: a new full-page view (the Subscriptions dashboard already is the full view); an index from history at read time on the client (the server backfill fixes every surface at once).

## Decisions

### Asked
- D-01 Ring panel summary, full view, or both → both: summary in the ring panel plus "Effectiveness" to the full view (Anton, November 17, 2026).
- D-02 Provider names → always a provider logo on the left of the name (Anton, November 17, 2026).
### Defaulted (change any before sw-do)
- D-03 Session (5-hour) windows → kept out of the index; Claude stopped reporting them after November 11 and no other provider reports one.
- D-04 Index span → last four weeks, raw used percent (targets stay on the full dashboard).
### Open
- none

## Tasks

### T-01 Backfill the reset ledger from limit history
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageResetLedgerStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageResetLedger.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageLimitHistoryStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageLimitHistory.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/usageResetLedgerStore.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageResetLedger.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/usage/usageResetLedgerStore.test.ts apps/server/src/usage/UsageResetLedger.test.ts

### T-02 Used before reset in the usage ring panel, one click to the full view
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/effectivenessIndex.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/EffectivenessSummary.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/effectivenessIndex.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectUsageIndicator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectUsageIndicator.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/usageSheetStore.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageLimits.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/effectiveness-index | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/usage/subscriptions/effectivenessIndex.test.tsx src/components/studio/shell/ProjectUsageIndicator.test.tsx

### T-03 Provider logos left of names in the Subscriptions view
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsDashboard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/ResetsTable.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/usage/subscriptions

### T-04 Review, merge, release
- AC: AC-05 | Files: none | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released <merge sha>

### T-05 Verify and close 1375
- AC: AC-05 | Files: none | Test: specweave verify
