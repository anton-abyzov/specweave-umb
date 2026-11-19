---
title: "1411 acceptance: all subscriptions and limits in one place"
increment: 1411
date: November 19, 2026
---

# 1411 acceptance

Shipped in SpecWithCode 1.0.379 (`request-release.sh --released 87572d101` → v1.0.379).

| AC | Evidence |
|---|---|
| AC-01 Rows without a reading | `packages/shared/src/usageLimits.unreported.test.ts` (Cursor reader off with a reading elsewhere: no row; Copilot without a reading beside a Copilot reading row: its own row; the table's cases; default result unchanged), `NoReadingRow.test.tsx`; PR 670 CI |
| AC-02 Windows and notes | `subscriptionRows.test.ts` (shortest first, notes, scoped and Overall excluded, an expired session still counts), `subscriptionWindowRules.test.ts`, `SubscriptionRow.test.tsx` (countdown and local date and time) |
| AC-03 Header line | `subscriptionRows.test.ts` "subscriptionsSummary" (at-limit formula, Copilot still runs, spent reset only, past resets hidden), `SubscriptionsView.test.tsx` |
| AC-04 Renewal key | `subscriptionRows.test.ts` "keys Copilot's day by its subscription and finds it after a sign-out, a sign-in and a new reading" |
| AC-05 Set day wins | `subscriptionRows.test.ts`, `SubscriptionRow.test.tsx` (set by you, reported by the vendor with Set day, keyless row keeps a reported date) |
| AC-06 Reported renewal | `cursorUsageLimits.test.ts` (MONTHLY only, every other case none), `OpenCodeProvider.test.ts` |
| AC-07 Amounts | `providerUsageLimits.test.ts` (contracts: old schema decodes the same windows), server merge clears and compares, `copilotUsageLimits.test.ts`, row validation and "885 of 1,500 premium requests" |
| AC-08 Copilot quota call | `reports/copilot-quota-trial.md`: no (reset date is the call time) |
| AC-09 Dated notes and age check | `subscriptionWindowRules.json`, `scripts/check-usage-rules-age.mjs` and its test (fixed date), `.github/workflows/usage-rules-age.yml` (weekly, `issues: write`, no pull request trigger) |
| AC-10 Shipped, reviewed, screenshots | Release 1.0.379; GPT-6.1 Sol at Extra High: round 1 fix first, round 2 ship at `3eff10e0b` (PR 670), round 3 ship at `d8ee4d5b6` (PR 691, fixture only); PR CI green; headless fixture verifier passed with the screenshots below |

## Screenshots

Headless Chromium, fixture `apps/web/tests/subscription-resets/` at the merge of PR 691, clock fixed at November 15, 2026 01:00 UTC, New York time zone. The fixture builds rows by hand, so these show how rows are drawn; AC-01 and AC-03 rest on the tests above.

- `screenshots/subscription-rows-light.png`: a Claude, two Codex and a Copilot row with amounts and a day set by you, then a row with no reading (Devin) and a signed-out Codex row.
- `screenshots/subscription-row-copilot-light.png`: Copilot's amounts, its monthly note and the day set under its subscription.
- `screenshots/subscriptions-light-1280.png`, `subscriptions-dark-1280.png`, `subscriptions-light-390.png`, `subscriptions-dark-390.png`: the whole page with the header line.
- `screenshots/subscriptions-empty.png`: before any reading.

## Proof limits

- The screenshots come from a fixture, not a live account. Live readings of each provider were not exercised here.
- Cursor's weekly plans report no renewal date (D-08); the day stays hand-set there.
- The Copilot entitlement was not compared with the CLI (see the trial record); the reset date alone made the result no.
