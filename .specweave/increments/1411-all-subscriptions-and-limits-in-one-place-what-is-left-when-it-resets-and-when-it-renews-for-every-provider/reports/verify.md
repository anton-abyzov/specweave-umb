# Verify — 1411-all-subscriptions-and-limits-in-one-place-what-is-left-when-it-resets-and-when-it-renews-for-every-provider

PASS · 2026-11-19T11:04:34.527Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (18s)

```
test_absent_and_idempotent (__main__.SafetyTests.test_absent_and_idempotent) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests.test_dirty_and_untracked_preserved) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests.test_existing_empty_and_atomic_race_preserved) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests.test_final_readback_detects_descendant_and_staging) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests.test_incomplete_runtime_and_release_never_pass) ... ok
test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts (__main__.SafetyTests.test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests.test_missing_or_diverged_upstream_is_preserved) ... ok
test_new_and_legacy_clones_fetch_and_track_future_feature (__main__.SafetyTests.test_new_and_legacy_clones_fetch_and_track_future_feature) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests.test_offline_bundle_and_bad_digest) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests.test_remote_drift_preserves_old_checkout) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests.test_scoped_transport_preserves_identity_and_rejects_redirects) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests.test_unpushed_commit_preserved) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests.test_unsafe_paths_urls_and_symlinks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 17.700s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.737s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.173s

OK
recorded
```

## Acceptance criteria

10/10 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Under the rows that have a reading, the Subscriptions board draws a row for every account `collectUnreportedLimitAccounts` returns when asked for all drivers. The function gains that option, used by the board alone. Only under it does each account also carry `environmentId`, `instanceId` and `displayName` (the provider snapshot's own, `packages/contracts/src/server.ts:303`), and only under it does an account key that a reading row already has suppress the row whatever the reading's reason. Without the option the result is field for field what it is today: the existing expectation (`packages/shared/src/usageLimits.test.ts:1029-1039`) is not edited, and `collectLimitAccounts` is not changed. Which instance gets which row is the table "Rows without a reading" below. Such a row is keyed by machine and instance (`${environmentId}:${instanceId}`, the key the function already uses, `usageLimits.ts:491`): one row per instance per machine, never merged, kept and marked offline when its machine is. It links to the vendor's usage page where `providerUsageLink` resolves from the driver and that display name as its label (`packages/shared/src/providerUsageLinks.ts:41-58`). Tests pin a Cursor instance whose reader is off on one machine while another machine has its reading (no second row), and a Copilot instance without a reading beside a Copilot reading row (a second row, since Copilot has no account key). |
| AC-02 | x (tasks) | met | Each reading row shows its windows, shortest first, each with percent left and the reset as a countdown and a local date and time. Under them it shows a note only by a rule in the table "Window notes" below; a reading no rule covers shows only what was read. Model-scoped windows and Cursor's "Overall" (`packages/shared/src/usageLimits.ts:33-39`) never count as account windows. The order and the note are computed in `subscriptionRows.ts`, which today keeps no window kind and the order received (`subscriptionRows.ts:25-39`); the row only draws them. |
| AC-03 | x (tasks) | met | A line at the top of `SubscriptionsView.tsx`, above the existing dashboard, reads "<n> subscriptions · <k> at a limit · next reset in <t>", and then " · <m> without a reading" when there are such rows. <n> counts reading rows only: the app cannot tell whether an instance with no reading is a plan or billed per use. A row is at a limit when its reading has `ordinaryUsageAllowed` false or `spendControlReached` true (`packages/contracts/src/providerUsageLimits.ts:80-82`), or when it has a spent account window and `ordinaryUsageAllowed` is not true; Copilot sets it true when spent premium requests do not stop it (`apps/server/src/provider/copilotUsageLimits.ts:195-199`), and then its row is not at a limit. A spent account window is fully used, live (its reset is not in the past, the test `packages/shared/src/usageWindows.ts:49-56` already makes), not model-scoped and not Cursor's "Overall". The row carries the result as a field, computed in `subscriptionRows.ts`. The next reset is the soonest reset of a spent account window among rows at a limit; a row at a limit with none gives the soonest reset of its live account windows; with no row at a limit it is the soonest such reset of all rows; a reset at or before now never shows, and with no reset time known the last part is left out. The order of rows stays 1340's; rows without a reading come last. |
| AC-04 | x (tasks) | met | A row has a renewal key: the account key as today (email, else credential fingerprint), else `<driver>:subscription:<subscriptionKey>` when the reading has one. The account key itself is unchanged for the ledger, prices and history, and days already saved keep their key. The day is read and saved under the renewal key everywhere it is used (`SubscriptionsView.tsx:155`, `SubscriptionsDashboard.tsx:286`). A test sets a day on a Copilot row and finds it after a sign-out, a sign-in and a new reading for the same login and plan. A row with no renewal key has no editor: a no-reading row shows "A renewal day can be set once this account reports usage", and a reading row without one shows "No renewal day: this account reports nothing to save it under." |
| AC-05 | x (tasks) | met | The day the person set wins and stays editable: "Renews <date> (set by you)". A date a reader reports shows only when no day is set and the date is in the future, as "Renews <date> (reported by <vendor>)", with the existing "Set day" control (`SubscriptionRow.tsx:119`) still offered. A reported date that has passed is ignored. |
| AC-06 | x (tasks) | met | Two readers publish `renewsAt`. OpenCode Go: its monthly reset. Cursor: `billingCycleEnd`, only when plan information was read, its `includedUsagePeriod` is a text ending in `MONTHLY` (the value the reader's own test uses, `apps/server/src/provider/cursorUsageLimits.test.ts:71`), and the date is valid and in the future. In every other case Cursor publishes none: no plan information (the reader then assumes monthly by default, `apps/server/src/provider/cursorUsageLimits.ts:82-100`), a weekly period, a number, an unknown text, a reading with no windows (`cursorUsageLimits.ts:127-129`). Tests list each case. |
| AC-07 | x (tasks) | met | A window may carry `used`, `limit` and `unit`. In the contract each is optional, a plain number or text with no check on its value and none across the three: windows travel in an array that drops a whole element its schema rejects (`packages/contracts/src/baseSchemas.ts:128-137`), and a bad amount must never cost the percent. The reader that publishes them emits all three or none. The row shows amounts only when all three are there, the numbers finite and zero or more and the unit 1 to 24 characters after trimming; anything else is shown as no amounts. The percent stays what bars, alerts and history use. Amounts belong to the read that produced them: an update for a window that carries none clears them (unlike `resetsAt`, which is carried forward, `apps/server/src/provider/providerUsageLimits.ts:110-128`), and equality compares them (`:320-330`). A test decodes a reading with the fields through the schema as it is at `c46e2efe5` and gets the same windows. In this increment only Copilot publishes them, from the snapshot it already chose (`copilotUsageLimits.ts:159-165`): limit is `entitlement`, used is `entitlement` less `remaining` and not below zero, unit is that snapshot's label in lower case ("premium requests"); none when the quota is unlimited, has no entitlement, or its `remaining` is absent or not finite (the percent can come from `percent_remaining` alone, `:113-125`). The row shows "885 of 1,500 premium requests" beside the percent. |
| AC-08 | x (tasks) | met | `reports/copilot-quota-trial.md` records one trial, run by Anton or the build's owner on a machine where the Copilot CLI is signed in: GitHub's Copilot SDK client as published, calling its documented `account.getQuota`, in a scratch folder, with `COPILOT_GITHUB_TOKEN`, `GH_TOKEN` and `GITHUB_TOKEN` removed from the environment. The record holds the CLI version and the `COPILOT_HOME` the client used. The call returns no login, so yes means its entitlement and reset date equal what that signed-in CLI shows for its own login at the same time, read by the person running the trial. No agent signs in and no token file is opened. The reader is not changed by either result. |
| AC-09 | x (tasks) | met | Each window note carries the vendor page and the date it was read, in `subscriptionWindowRules.json`. A plain Node script reports notes older than 90 days and is tested with a fixed date. A weekly scheduled workflow with `issues: write` runs it and, when something is old, comments on the open issue titled "Usage window notes need a re-read" or opens it when there is none. It never runs on a pull request. |
| AC-10 | x (tasks) | met | Shipped in a released build after an independent Extra High review and green Checks, with headless screenshots from the fixture in `apps/web/tests/subscription-resets/`, extended to hold a Claude, a Codex and a Copilot row with amounts and a set renewal day, a row with no reading and a signed-out row. Its verifier is updated for them: today it expects three rows and a reported renewal date with no edit action (`apps/web/tests/subscription-resets/verify.mjs:180-203`). The fixture builds its rows by hand (`apps/web/tests/subscription-resets/main.tsx:53-101`), so the screenshots show how rows are drawn; AC-01 and AC-03 rest on T-01's tests. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | specwithcode PR 670 at 3eff10e0b: 27 checks green (PR Gate … |  |
| T-02 | done | claude@antons-macbook-m4max | specwithcode PR 670 at 3eff10e0b: 27 checks green (PR Gate … |  |
| T-03 | done | claude@antons-macbook-m4max | specwithcode PR 670 at 3eff10e0b: 27 checks green (PR Gate … |  |
| T-04 | done | claude@antons-macbook-m4max | specwithcode PR 670 at 3eff10e0b: 27 checks green (PR Gate … |  |
| T-05 | done | claude@antons-macbook-m4max | test -s .specweave/increments/1411-all-subscriptions-and-li… |  |
| T-06 | done | claude@antons-macbook-m4max | Released in 1.0.379 (87572d101); GPT-6.1 Sol ship rounds 2 … |  |

6/6 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
