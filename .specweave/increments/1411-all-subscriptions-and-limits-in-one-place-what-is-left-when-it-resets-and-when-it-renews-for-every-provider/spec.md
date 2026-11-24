# All subscriptions and limits in one place: what is left, when it resets and when it renews, for every provider

Version 4, November 18, 2026. Three review rounds returned "fix first" (`reports/reviews/review-muse-wonder-full-1.0-1.md`, `-2.md`, `-3.md`; answers in `reports/review-responses.md`). Version 3 narrowed the plan: the three reader switches moved to increment 1415, and the Copilot reader is not changed here. Round 3 closed most of round 2 and left four pins and seven smaller points; version 4 applies them and has not been reviewed again.

## Problem

Anton, November 18, 2026: "we must have the full board. There should be an easy way to look up all your subscriptions and limits on it. That's very important ... how to understand the current limits that we have, or when it's going to be renewed (for example, GitHub Copilot from use). Maybe for Cursor, we also need to know when it's going to be expiring, when it's a weekly update, and how much is left for weekly or for hourly if this is still kind of supported by a provider."

Research, per provider, with sources: `reports/limits-research.md` in this increment. App paths are in `repositories/anton-abyzov/specwithcode` at `origin/main` `c46e2efe5`.

A board exists. Increment 1340 shipped Usage > Limits > Subscriptions: a row per account that has a reading, with its logo, plan, email, machine, each window with what is left and a countdown, a renewal date and what the last reset left unused (`apps/web/src/components/usage/subscriptions/subscriptionRows.ts`). What is wrong today:

1. **An account with no reading has no row.** The board reads `collectLimitAccounts`, which keeps only providers that publish `usageLimits` and skips a reading that has a notice instead of windows (`packages/shared/src/usageLimits.ts:78-88`, `:266`, `:705-713`). A list of the accounts it leaves out already exists, with a reason for each (`collectUnreportedLimitAccounts`, `packages/shared/src/usageLimits.ts:446-507`), but it covers only Claude and Codex (`:438`) and only the pooled Limits view draws it (`apps/web/src/components/usage/UsageLimitsPooled.tsx:556`). Antigravity, Gemini CLI, Devin, Pi, most ACP agents and Cursor with its reader off are on no page.
2. **Copilot, his own example, cannot keep a renewal day.** The day is saved under the account key, which needs an email or a credential fingerprint (`packages/shared/src/usageLimits.ts:139-149`). Copilot publishes neither; it publishes a login and a `subscriptionKey` (`apps/server/src/provider/copilotUsageLimits.ts:151-157`, `apps/server/src/provider/Drivers/AcpRegistryDriver.ts:591-604`). Its row has no key, so the editor cannot save (`subscriptionRows.ts:168-170`).
3. **No renewal date is read.** The contract has `renewsAt` (`packages/contracts/src/providerUsageLimits.ts:113`) and no reader writes it. Two readers hold a date that is the renewal date in the vendor's own words and publish it only as a window reset: OpenCode Go's monthly reset (`apps/server/src/provider/openCodeUsageLimits.ts:98-104`; "resets when a new paid period starts") and Cursor's `billingCycleEnd` on plans with a monthly period ("usage resets monthly with your billing cycle").
4. **A date the vendor reports would erase the day he set.** The row prefers a reported date and then hides the editor (`subscriptionRows.ts:188-193`, `apps/web/src/components/usage/subscriptions/SubscriptionRow.tsx:66-69`).
5. **Amounts are thrown away.** Copilot's reader gets an entitlement and what remains (`copilotUsageLimits.ts:67-70`) and uses them only to work out a percent (`:113-125`), because a window in the contract carries a percent and no amounts (`packages/contracts/src/providerUsageLimits.ts:20-32`).
6. **A missing window reads as a gap, not as a fact.** Copilot has only a monthly allowance and Cursor one weekly pool. The row shows nothing where it could say so.

## Scope

In: rows for accounts without a reading; a header line; a short note where a provider has no shorter window; the renewal day for Copilot and the person's day winning over a reported date; a reported renewal date from OpenCode Go and from Cursor's monthly plans; Copilot's amounts beside the percent; a recorded trial of GitHub's documented quota call.

Out, with where it went:

- A switch for each reader that holds a vendor's token (Anton's answer D-01): increment 1415. Until it ships, Grok and OpenCode Go are read as today, without a switch, and Cursor keeps its existing one.
- A reported expiry for Cursor's weekly plans, which are its current ones. `billingCycleEnd` is in Cursor's answer for every plan (`apps/server/src/provider/cursorUsageLimits.ts:26-27`), but Cursor's page ties usage to the billing cycle only for monthly plans, and nothing read says that on a weekly plan this date is when the subscription renews. The day stays hand-set there (D-08). This leaves part of Anton's request unanswered for today's Cursor plans.
- Changing how Copilot is read. The present reader stays. Whether GitHub's documented call can replace it is recorded here (AC-08) and planned after the result.
- Links between Settings > Providers and the board, and the hold text on a row: 1397 AC-15.
- New usage links, and passing an ACP agent's id to the row. A row links where today's resolver already can.
- The ring panel, the pooled Limits view, the phone's usage screen and the reset report: they keep today's account list.
- Scraping a vendor's dashboard. Any new token read. Quota alerts are not changed; they will fire near a renewal date a reader reports (`packages/shared/src/quotaAlerts.ts:239-262`), which is intended.

## Acceptance Criteria

### Rows

- [ ] AC-01: Under the rows that have a reading, the Subscriptions board draws a row for every account `collectUnreportedLimitAccounts` returns when asked for all drivers. The function gains that option, used by the board alone. Only under it does each account also carry `environmentId`, `instanceId` and `displayName` (the provider snapshot's own, `packages/contracts/src/server.ts:303`), and only under it does an account key that a reading row already has suppress the row whatever the reading's reason. Without the option the result is field for field what it is today: the existing expectation (`packages/shared/src/usageLimits.test.ts:1029-1039`) is not edited, and `collectLimitAccounts` is not changed. Which instance gets which row is the table "Rows without a reading" below. Such a row is keyed by machine and instance (`${environmentId}:${instanceId}`, the key the function already uses, `usageLimits.ts:491`): one row per instance per machine, never merged, kept and marked offline when its machine is. It links to the vendor's usage page where `providerUsageLink` resolves from the driver and that display name as its label (`packages/shared/src/providerUsageLinks.ts:41-58`). Tests pin a Cursor instance whose reader is off on one machine while another machine has its reading (no second row), and a Copilot instance without a reading beside a Copilot reading row (a second row, since Copilot has no account key).
- [ ] AC-02: Each reading row shows its windows, shortest first, each with percent left and the reset as a countdown and a local date and time. Under them it shows a note only by a rule in the table "Window notes" below; a reading no rule covers shows only what was read. Model-scoped windows and Cursor's "Overall" (`packages/shared/src/usageLimits.ts:33-39`) never count as account windows. The order and the note are computed in `subscriptionRows.ts`, which today keeps no window kind and the order received (`subscriptionRows.ts:25-39`); the row only draws them.
- [ ] AC-03: A line at the top of `SubscriptionsView.tsx`, above the existing dashboard, reads "<n> subscriptions · <k> at a limit · next reset in <t>", and then " · <m> without a reading" when there are such rows. <n> counts reading rows only: the app cannot tell whether an instance with no reading is a plan or billed per use. A row is at a limit when its reading has `ordinaryUsageAllowed` false or `spendControlReached` true (`packages/contracts/src/providerUsageLimits.ts:80-82`), or when it has a spent account window and `ordinaryUsageAllowed` is not true; Copilot sets it true when spent premium requests do not stop it (`apps/server/src/provider/copilotUsageLimits.ts:195-199`), and then its row is not at a limit. A spent account window is fully used, live (its reset is not in the past, the test `packages/shared/src/usageWindows.ts:49-56` already makes), not model-scoped and not Cursor's "Overall". The row carries the result as a field, computed in `subscriptionRows.ts`. The next reset is the soonest reset of a spent account window among rows at a limit; a row at a limit with none gives the soonest reset of its live account windows; with no row at a limit it is the soonest such reset of all rows; a reset at or before now never shows, and with no reset time known the last part is left out. The order of rows stays 1340's; rows without a reading come last.

### Renewal

- [ ] AC-04: A row has a renewal key: the account key as today (email, else credential fingerprint), else `<driver>:subscription:<subscriptionKey>` when the reading has one. The account key itself is unchanged for the ledger, prices and history, and days already saved keep their key. The day is read and saved under the renewal key everywhere it is used (`SubscriptionsView.tsx:155`, `SubscriptionsDashboard.tsx:286`). A test sets a day on a Copilot row and finds it after a sign-out, a sign-in and a new reading for the same login and plan. A row with no renewal key has no editor: a no-reading row shows "A renewal day can be set once this account reports usage", and a reading row without one shows "No renewal day: this account reports nothing to save it under."
- [ ] AC-05: The day the person set wins and stays editable: "Renews <date> (set by you)". A date a reader reports shows only when no day is set and the date is in the future, as "Renews <date> (reported by <vendor>)", with the existing "Set day" control (`SubscriptionRow.tsx:119`) still offered. A reported date that has passed is ignored.
- [ ] AC-06: Two readers publish `renewsAt`. OpenCode Go: its monthly reset. Cursor: `billingCycleEnd`, only when plan information was read, its `includedUsagePeriod` is a text ending in `MONTHLY` (the value the reader's own test uses, `apps/server/src/provider/cursorUsageLimits.test.ts:71`), and the date is valid and in the future. In every other case Cursor publishes none: no plan information (the reader then assumes monthly by default, `apps/server/src/provider/cursorUsageLimits.ts:82-100`), a weekly period, a number, an unknown text, a reading with no windows (`cursorUsageLimits.ts:127-129`). Tests list each case.

### Amounts

- [ ] AC-07: A window may carry `used`, `limit` and `unit`. In the contract each is optional, a plain number or text with no check on its value and none across the three: windows travel in an array that drops a whole element its schema rejects (`packages/contracts/src/baseSchemas.ts:128-137`), and a bad amount must never cost the percent. The reader that publishes them emits all three or none. The row shows amounts only when all three are there, the numbers finite and zero or more and the unit 1 to 24 characters after trimming; anything else is shown as no amounts. The percent stays what bars, alerts and history use. Amounts belong to the read that produced them: an update for a window that carries none clears them (unlike `resetsAt`, which is carried forward, `apps/server/src/provider/providerUsageLimits.ts:110-128`), and equality compares them (`:320-330`). A test decodes a reading with the fields through the schema as it is at `c46e2efe5` and gets the same windows. In this increment only Copilot publishes them, from the snapshot it already chose (`copilotUsageLimits.ts:159-165`): limit is `entitlement`, used is `entitlement` less `remaining` and not below zero, unit is that snapshot's label in lower case ("premium requests"); none when the quota is unlimited, has no entitlement, or its `remaining` is absent or not finite (the percent can come from `percent_remaining` alone, `:113-125`). The row shows "885 of 1,500 premium requests" beside the percent.

### Copilot's documented call

- [ ] AC-08: `reports/copilot-quota-trial.md` records one trial, run by Anton or the build's owner on a machine where the Copilot CLI is signed in: GitHub's Copilot SDK client as published, calling its documented `account.getQuota`, in a scratch folder, with `COPILOT_GITHUB_TOKEN`, `GH_TOKEN` and `GITHUB_TOKEN` removed from the environment. The record holds the CLI version and the `COPILOT_HOME` the client used. The call returns no login, so yes means its entitlement and reset date equal what that signed-in CLI shows for its own login at the same time, read by the person running the trial. No agent signs in and no token file is opened. The reader is not changed by either result.

### Shipping

- [ ] AC-09: Each window note carries the vendor page and the date it was read, in `subscriptionWindowRules.json`. A plain Node script reports notes older than 90 days and is tested with a fixed date. A weekly scheduled workflow with `issues: write` runs it and, when something is old, comments on the open issue titled "Usage window notes need a re-read" or opens it when there is none. It never runs on a pull request.
- [ ] AC-10: Shipped in a released build after an independent Extra High review and green Checks, with headless screenshots from the fixture in `apps/web/tests/subscription-resets/`, extended to hold a Claude, a Codex and a Copilot row with amounts and a set renewal day, a row with no reading and a signed-out row. Its verifier is updated for them: today it expects three rows and a reported renewal date with no edit action (`apps/web/tests/subscription-resets/verify.mjs:180-203`). The fixture builds its rows by hand (`apps/web/tests/subscription-resets/main.tsx:53-101`), so the screenshots show how rows are drawn; AC-01 and AC-03 rest on T-01's tests.

### Rows without a reading (AC-01)

| The instance | Its row says |
|---|---|
| Enabled, installed, signed in or sign-in not proven (ACP agents report `unknown`, `apps/server/src/provider/Drivers/AcpRegistryDriver.ts:489-508`), no reading | The reader's notice when it has one, else "Usage not reported by <name>", where <name> is the instance's display name, else the driver's label |
| Claude or Codex, billed by an API key (`reason` `apiBilling`, `usageLimits.ts:485-488`). The rule is written for those two; for other drivers under the board option an `unsupported` reading without a message is "no reading", so an OpenCode instance on an external server (`apps/server/src/provider/openCodeUsageLimits.ts:40`) is not called API-billed | "Billed by API key. No plan limits." |
| Claude or Codex, signed out (`reason` `signedOut`) | The provider's message, else "Signed out" |
| Any other driver, signed out | No row |
| Usage tracked elsewhere (`externalUsage`, `usageLimits.ts:475`) | No row, as today |
| Has an account key (email or fingerprint) that a reading row on this or another machine has | No second row, whatever the reason. The `unsupported` exception at `usageLimits.ts:478-481` stays for the default only |
| Has no account key (Copilot, most ACP agents) | Its own row, even when another instance of the same account has a reading: nothing ties the two |
| Not enabled or not installed | No row |

1397 AC-15 asks that a held or signed-out account says so on its row. This table gives a signed-out Claude or Codex account its row, with the provider's message. A held account is different: 1397 publishes the hold as `account.hold`, which this function does not read (`usageLimits.ts:500-502`), and a held account whose reading keeps its windows stays a reading row. Reading `account.hold` for the wording, in `SubscriptionRow.tsx` and in `NoReadingRow.tsx`, is 1397 T-07's; its file list gains `NoReadingRow.tsx` when 1411 lands first.

### Window notes (AC-02)

A note fires on what the reading holds, never on a plan name alone.

| Provider | When the reading has | The row says | Source, read November 18, 2026 |
|---|---|---|---|
| GitHub Copilot | any window | "Monthly allowance. Resets on the first of the month at 00:00 UTC, whatever your billing day." | "your allowance resets to the full monthly amount at 00:00:00 UTC on the first day of each calendar month." `https://docs.github.com/en/copilot/concepts/billing/billing-for-individuals` |
| Cursor | a weekly window | "One weekly pool. No hourly limit." | "every paid plan includes one weekly pool of usage for Cursor models" `https://cursor.com/help/models-and-usage/usage-limits` |
| Cursor | a renewal date (AC-06) | "Usage resets monthly with your billing cycle." | "usage resets monthly with your billing cycle." same page |
| Grok | a weekly window | "One weekly pool across Grok products." | "you get one shared weekly usage pool" `https://docs.x.ai/grok/faq` |
| Codex | the plan label is one of the three Pro labels the app produces (`apps/server/src/provider/CodexProvider.ts:120-154`), a weekly window, no window of kind `session` and none shorter than seven days | "No 5-hour window reported for this plan." | The reading itself. OpenAI's pricing page was read only as a summary, so no vendor sentence is quoted. |
| Claude, OpenCode Go, everything else | | only what was read | Claude reports its session window only while one applies (`apps/server/src/provider/claudeUsageLimits.ts:393-395`), so its absence proves nothing |

## Approach

1. `collectUnreportedLimitAccounts` takes `{ drivers: "all" }` and, only then, returns the instance id, machine id and display name with each account. The board draws those in a new `NoReadingRow.tsx`. New tests go in a new file: `usageLimits.test.ts` is already 1,558 lines.
2. The notes live in `packages/shared/src/subscriptionWindowRules.ts`, with their sources and dates in a JSON file beside it that the age script reads without an install, the way `scripts/download-stats` runs today.
3. `subscriptionRows.ts` gives each row its renewal key, its at-limit field and its spent-window reset; the renewal precedence changes there and in `SubscriptionRow.tsx`.
4. The contract's window gains the three fields; the server's merge clears them on an update without them; Copilot's reader fills them.

Risks: vendors change their windows, so the notes are dated and checked on a schedule. Cursor's renewal date shows only for a plan whose period the reader can name as monthly; for the rest the day stays hand-set. Copilot's key holds the plan as GitHub names it, in whichever of two fields it fills (`copilotUsageLimits.ts:151-155`), so a plan change, or GitHub naming the same plan differently, gives a new key and the day is set again; AC-04's test covers the same login and plan, not that.

Rejected: changing `collectLimitAccounts` for everyone (nine files read it); a second collection built from scratch when the unreported list exists; keeping a reader's last identity while it is off (a stale account on the board); a plan-name rule for Claude Ultra (the app's label does not say "verified" and the reading cannot prove a missing window); reading a renewal date out of a CLI's login token; scraping a vendor's dashboard through the person's Chrome; a test that goes red on a calendar date.

## Decisions

### Asked
- D-01 Readers that hold the vendor's token (Cursor, Grok, OpenCode Go) → Anton, November 18, 2026: "Keep, each behind its own switch". Built in increment 1415, not here.

### Defaulted (change any before sw-do)
- D-02 The day the person set wins over a date a reader reports.
- D-03 A note about a window that does not exist fires only on what the reading holds, with a dated source.
- D-04 No new scraping and no new token reads.
- D-05 Copilot's reader stays as it is. The earlier plan to put it behind a fourth switch if the documented call fails is dropped: Anton's answer named three readers.
- D-06 1340's row order stays.
- D-07 Amounts are not carried from one read to the next.
- D-08 Cursor reports a renewal date only for monthly plans. Publishing `billingCycleEnd` for weekly plans too, as "Billing cycle ends <date>", is one clause in AC-06 if Anton wants it.
- D-09 The header counts only rows with a reading as subscriptions.

### Open
- H1 Does GitHub's SDK client answer `account.getQuota` from the Copilot CLI's own sign-in? AC-08 records it. Nothing in the repository shows it (`apps/server/src/provider/acp/testing/copilot-acp.fixture.mjs:1`).
- H2 Claude's reader uses an Agent SDK call the vendor names experimental (`apps/server/src/provider/ClaudeProvider.ts:531`). Left as is.

## Review

Adversarial review by Muse Wonder Full 1.0 at Extra High before building. Rounds 1, 2 and 3, November 18, 2026: "fix first" each time; every finding was checked against the code and answered in `reports/review-responses.md`. Round 3 found 8 of 12 round 2 findings closed and raised 4 must-fix and 7 should-fix, each a pin or a cut; they are applied in this version, which has not been reviewed again. No fourth spec round is planned: the build's own review reads the code.

Build order with 1397: both edit `SubscriptionRow.tsx`. 1411 owns the rows and the table above; 1397 T-07 owns the hold text. Whichever lands second keeps the other's tests green.

## Tasks

File tags: [exists] at `c46e2efe5`, [new] created here.

### T-01 Rows for accounts without a reading, and the header line
- AC: AC-01, AC-03 | Files: packages/shared/src/usageLimits.ts [exists], packages/shared/src/usageLimits.unreported.test.ts [new], apps/web/src/components/usage/subscriptions/subscriptionRows.ts [exists], apps/web/src/components/usage/subscriptions/subscriptionRows.test.ts [exists], apps/web/src/components/usage/subscriptions/NoReadingRow.tsx [new], apps/web/src/components/usage/subscriptions/NoReadingRow.test.tsx [new], apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx [exists], apps/web/src/components/usage/subscriptions/SubscriptionsView.test.tsx [exists] | Test: cd repositories/anton-abyzov/specwithcode && vp test run packages/shared/src/usageLimits.unreported.test.ts && cd apps/web && vp test run src/components/usage/subscriptions/subscriptionRows.test.ts src/components/usage/subscriptions/NoReadingRow.test.tsx src/components/usage/subscriptions/SubscriptionsView.test.tsx

### T-02 Window notes with dated sources, and the age check
- AC: AC-02, AC-09 | Files: packages/shared/src/subscriptionWindowRules.ts [new], packages/shared/src/subscriptionWindowRules.json [new], packages/shared/src/subscriptionWindowRules.test.ts [new], packages/shared/package.json [exists], apps/web/src/components/usage/subscriptions/subscriptionRows.ts [exists], apps/web/src/components/usage/subscriptions/subscriptionRows.test.ts [exists], apps/web/src/components/usage/subscriptions/SubscriptionRow.tsx [exists], apps/web/src/components/usage/subscriptions/SubscriptionRow.test.tsx [new], scripts/check-usage-rules-age.mjs [new], scripts/check-usage-rules-age.test.mjs [new], .github/workflows/usage-rules-age.yml [new] | Test: cd repositories/anton-abyzov/specwithcode && vp test run packages/shared/src/subscriptionWindowRules.test.ts && node --test scripts/check-usage-rules-age.test.mjs && cd apps/web && vp test run src/components/usage/subscriptions/subscriptionRows.test.ts src/components/usage/subscriptions/SubscriptionRow.test.tsx

### T-03 Renewal: a key Copilot has, the person's day first, and the two readers that report a date
- AC: AC-04, AC-05, AC-06 | Files: apps/web/src/components/usage/subscriptions/subscriptionRows.ts [exists], apps/web/src/components/usage/subscriptions/subscriptionRows.test.ts [exists], apps/web/src/components/usage/subscriptions/SubscriptionRow.tsx [exists], apps/web/src/components/usage/subscriptions/SubscriptionRow.test.tsx [new], apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx [exists], apps/web/src/components/usage/subscriptions/SubscriptionsDashboard.tsx [exists], apps/server/src/provider/cursorUsageLimits.ts [exists], apps/server/src/provider/cursorUsageLimits.test.ts [exists], apps/server/src/provider/openCodeUsageLimits.ts [exists], apps/server/src/provider/OpenCodeProvider.test.ts [exists] | Test: cd repositories/anton-abyzov/specwithcode && vp test run apps/server/src/provider/cursorUsageLimits.test.ts apps/server/src/provider/OpenCodeProvider.test.ts && cd apps/web && vp test run src/components/usage/subscriptions/subscriptionRows.test.ts src/components/usage/subscriptions/SubscriptionRow.test.tsx

### T-04 Amounts on a window, filled by Copilot's reader
- AC: AC-07 | Files: packages/contracts/src/providerUsageLimits.ts [exists], packages/contracts/src/providerUsageLimits.test.ts [exists], apps/server/src/provider/providerUsageLimits.ts [exists], apps/server/src/provider/providerUsageLimits.test.ts [exists], apps/server/src/provider/copilotUsageLimits.ts [exists], apps/server/src/provider/copilotUsageLimits.test.ts [exists], apps/web/src/components/usage/subscriptions/subscriptionRows.ts [exists], apps/web/src/components/usage/subscriptions/subscriptionRows.test.ts [exists], apps/web/src/components/usage/subscriptions/SubscriptionRow.tsx [exists] | Test: cd repositories/anton-abyzov/specwithcode && vp test run packages/contracts/src/providerUsageLimits.test.ts apps/server/src/provider/providerUsageLimits.test.ts apps/server/src/provider/copilotUsageLimits.test.ts && cd apps/web && vp test run src/components/usage/subscriptions/subscriptionRows.test.ts

### T-05 Record the trial of GitHub's documented quota call
- AC: AC-08 | Files: .specweave/increments/1411-all-subscriptions-and-limits-in-one-place-what-is-left-when-it-resets-and-when-it-renews-for-every-provider/reports/copilot-quota-trial.md | Test: test -s .specweave/increments/1411-all-subscriptions-and-limits-in-one-place-what-is-left-when-it-resets-and-when-it-renews-for-every-provider/reports/copilot-quota-trial.md

### T-06 Release, screenshots, review and close 1411
- AC: AC-10 | Files: apps/web/tests/subscription-resets/main.tsx [exists], apps/web/tests/subscription-resets/verify.mjs [exists], .specweave/increments/1411-all-subscriptions-and-limits-in-one-place-what-is-left-when-it-resets-and-when-it-renews-for-every-provider/reports/acceptance.md | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/subscription-resets/vite.config.ts && node apps/web/tests/subscription-resets/verify.mjs "$PWD/../../../.specweave/increments/1411-all-subscriptions-and-limits-in-one-place-what-is-left-when-it-resets-and-when-it-renews-for-every-provider/reports/screenshots"
