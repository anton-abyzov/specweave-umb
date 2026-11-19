# Review: anton-abyzov/specwithcode#670 at `56621f2ef`
Verdict: fix first

Reviewer: GPT-6.1 Sol on Copilot Enterprise (`acpRegistry_copilot`), Extra High, November 19, 2026. Read with `git show` and `git diff` only.

1. **Must-fix · medium · AC-03: An unknown spent-window reset falls back to an unrelated reset.** `apps/web/src/components/usage/subscriptions/subscriptionRows.ts:405-407`. Input: a weekly account window at 100%, without `resetsAt`, plus an unspent session window resetting in one hour. The row correctly counts as limited, but `spent` becomes `null`, so the header announces "next reset in 1h 0m". That reset does not clear the exhausted weekly allowance. AC-03 permits this fallback only when no spent account window exists, not when its timestamp is unknown.

2. **Should-fix · medium · AC-05: A missing renewal key hides a valid reported renewal.** `apps/web/src/components/usage/subscriptions/SubscriptionRow.tsx:80-83`. Input: a reading with a future `renewsAt`, but no email, credential fingerprint or subscription key. The early return hides it behind "No renewal day...". A key is necessary to save a day, not to display a reported date.

3. **Should-fix · medium · AC-02: Expiring a session window fabricates the Codex missing-window note.** `apps/web/src/components/usage/subscriptions/subscriptionRows.ts:328`. Input: `ChatGPT Pro 20x Subscription`, a future weekly window, and a reported five-hour session whose reset just passed. `windowsOf` removes that session before `noteOf` evaluates the reading, so the row claims "No 5-hour window reported for this plan".

## Responses (fixed in `3eff10e0b`)

1. A row at a limit with any spent account window takes only those windows' resets; an unknown one gives no reset rather than a shorter window's. Test: "names no reset for a row whose spent window has no reset time".
2. With no renewal key, a reported future date shows as "Renews <date> (reported by <vendor>)" with no editor; the no-key sentence shows only without one. Test: "still shows a reported date on a row with nothing to key a day by".
3. Notes read every account window the reading holds, live or not; bars and the limit still use live windows. Test: "does not say a Codex Pro plan lacks a 5-hour window when its session just reset".
