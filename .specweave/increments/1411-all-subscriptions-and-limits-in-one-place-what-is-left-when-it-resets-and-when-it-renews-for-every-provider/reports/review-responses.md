---
title: "1411 spec review: findings and responses"
increment: 1411
reviewer: Muse Wonder Full 1.0, Extra High
author of responses: Claude Fable 5.2
date: November 18, 2026
---

# 1411 spec review: findings and responses

Round 1 verdict: REVISE. The reviewer's own record is `reports/reviews/review-muse-wonder-full-1.0-1.md` in this increment. Each finding was checked against `repositories/anton-abyzov/specwithcode` at `c46e2efe5` before it was answered. The spec was rewritten rather than patched; the rewritten text has not been reviewed.

| Finding | Checked | Response in the spec |
|---|---|---|
| M1 The board's source drops exactly the rows AC-01 adds; T-01 lacked the files; no agent id reaches the header; no new link was read from a vendor page | True: `packages/shared/src/usageLimits.ts:78-88`, `:266`, `:705-713`; `SubscriptionRow.tsx:148` | Problem 2 now says an account with no reading has no row. AC-01 names a board-only collection, pins the old one with a test, threads the agent id, and adds a link only with the vendor page that names it (H3). T-01 lists the files. |
| M2 The rule table had no key and no rows | True: `planLabel` is written nowhere; plan strings come from `ClaudeProvider.ts:204-246` and `CodexProvider.ts:120-154` | The table is in the spec, keyed by the labels the app produces, with observed-shape rules where the name is not enough, each with its source. Scoped windows and Cursor's "Overall" never count. |
| M3 No evidence that Copilot answers `account.getQuota`; no connection is held at status time; the fail branch was undefined | True: no call or SDK dependency in the repository; `AcpRegistryDriver.ts:707`; `copilot-acp.fixture.mjs:1` | AC-07 starts with a recorded spike of the SDK's server mode and writes both branches. A no makes Copilot a fourth switch (D-05) and adds the file to 1401's guard list. The "Update GitHub Copilot" sentence is gone. |
| M4 The new contract fields were untyped | Agreed | AC-06 pins them: finite numbers of zero or more, free-text unit, no amounts for an unlimited entitlement, percent stays authoritative, an old-schema decode test, and the server merge file is in T-02. |
| M5 The switch collided with the existing one, environment tokens, platforms and identity | True: `settings.ts:2355-2357`; environment paths in all three readers; `GrokDriver.ts:149-157` takes the email from the same read; `usageLimits.ts:139-149` builds the key from it | AC-08 reuses `cursorKeychainUsageEnabled`, gates file reads on every platform and treats an environment token as consent. AC-09 keeps the last identity so set renewal days stay attached, defines "Show it here" as opening that machine's setting, and shows the explanatory line whenever a switch is off. T-03 lists the missing files. |
| M6 Renewal precedence was undefined and the code prefers the reported date | True: `subscriptionRows.ts:188-193`, `SubscriptionRow.tsx:66-69` | AC-04: the person's day wins and stays editable. AC-05: Cursor reports a date only with plan information that says legacy. Billing links are dropped. Scope says alerts will fire near a reported renewal. |
| M7 A test that fails after 90 days is a time bomb | Agreed | AC-10: fixed-clock unit test, a scheduled job that opens an issue, never a merge gate. |
| S1 The header numbers were undefined and the sort changed 1340's | True: `subscriptionRows.ts:157-160` | AC-03 defines each number and keeps 1340's order (D-06). |
| S2 Imprecise citations | True for (a) to (g) | Problem rewritten with the corrected lines. `limits-research.md` section 1 corrected; its Cursor range and the two quote placements are noted in its section 5. |
| S3 Missing test files, two files over the size rule, no screenshot fixture | True: 2,901 and 1,343 lines; the two reader tests do not exist | T-03 uses the existing `GrokProvider.test.ts` and `OpenCodeProvider.test.ts`; new settings and the Copilot call go in new files; T-05 lists the fixture. |
| S4 Friction with 1397 AC-15 and 1401 D-01 | Agreed | Review section states the row states and the build order; 1401 D-01 names both Copilot outcomes. |

What the first version got wrong and the reports said to Anton: "the board already lists every account". It lists every account that has a reading.

# Round 2

Verdict: "fix first" again, 7 must-fix and 5 should-fix (`reports/reviews/review-muse-wonder-full-1.0-2.md`). Each was checked at `c46e2efe5`. Most sat on mechanisms version 2 had added, so version 3 cuts instead of pinning: the three reader switches moved to increment 1415, the Copilot reader is not changed, and no identity is kept for a reader that is off. Version 3 has not been reviewed.

| Finding | Checked | Response in version 3 |
|---|---|---|
| N1 The board-only collection had no row type, eligibility rule or agent id source | True. Also found: the list of accounts without a usable reading already exists, `collectUnreportedLimitAccounts` (`packages/shared/src/usageLimits.ts:446-507`), limited to Claude and Codex and drawn only by the pooled view | AC-01 widens that function by an option the board alone uses, keeps its key (machine and instance) and adds the table "Rows without a reading". Agent id plumbing and new links are out of scope. |
| N2 Copilot cannot hold a renewal day | True: `packages/shared/src/usageLimits.ts:139-149`, `apps/server/src/provider/copilotUsageLimits.ts:151-157` | AC-04: a renewal key that falls back to `subscriptionKey`; the account key is unchanged; a Copilot test. |
| N3 The table miskeyed Claude; Cursor's monthly rule could fire from a default | True: `apps/server/src/provider/ClaudeProvider.ts:261-276`, `apps/server/src/provider/cursorUsageLimits.ts:82-100` | The Claude Ultra rule is dropped. Notes fire on what the reading holds; Cursor's monthly note only when the reading has a renewal date, which AC-06 allows only for an explicit monthly period. |
| N4 The Copilot trial and its "no" branch were not executable or tasked | True | The reader change and the fourth switch are dropped (D-05). AC-08 keeps one exactly described trial; T-05 is its only task. 1401 D-01 now agrees with its AC-05. |
| N5 Off state, OpenCode's precedence, stale identity, the jump to the switch | True: `apps/server/src/provider/openCodeUsageLimits.ts:55-68`, `apps/server/src/provider/providerUsageLimits.ts:383-400` | Moved to increment 1415, which pins each: a per-reader table, the existing `unsupported` reason with a message, no kept identity, the real settings location. |
| N6 Cursor's "legacy" was not something the reader reports | True: `cursorUsageLimits.ts:36-46` | AC-06 defines it from the decoded fields and lists the cases. |
| N7 AC-01 excluded the held or signed-out row 1397 needs | True | The table gives a signed-out Claude or Codex account a row that shows the provider's message; 1397 T-07 owns the hold text. |
| N8 Sparse merge and unit source | True | AC-07: all three fields or none, cleared by an update without them (D-07), the unit named from the reader's own snapshot label. |
| N9 "Next reset" could name an unspent window | True | AC-03: the spent window's reset, with the fallbacks written out; the line's place is named. |
| N10 The issue job and the screenshot task | True | AC-09 (weekly, `issues: write`, one issue by title, a plain Node script with its own test). AC-10 and T-06 list `verify.mjs` and the fixture's build and verify commands. |
| N11 Two research defects left in the body | True | Fixed in place in `limits-research.md`. |
| N12 A stale reported renewal date | True | AC-05: a reported date that has passed is ignored. |

Round 1 items the reviewer marked partly closed (M1, M2, M3, M5, M6, S2, S3, S4) map to N1, N3, N4, N5, N6, N11, N10 and N7 above.

# Round 3

Verdict: "fix first", 4 must-fix and 7 should-fix (`reports/reviews/review-muse-wonder-full-1.0-3.md`). The reviewer found 8 of the 12 round 2 findings closed and the rest partly closed. Each new finding was checked at `c46e2efe5` and all hold. Version 4 applies them. It was not sent for a fourth round: every fix is a pin or a cut, and the build's own review reads the code.

| Finding | Checked | Response in version 4 |
|---|---|---|
| R1 The default result would change, and the row has no name | True: `packages/shared/src/usageLimits.ts:446-455`, `usageLimits.test.ts:1029-1039` | AC-01: the ids and `displayName` are returned only under the board option; the existing expectation is not edited; <name> is the display name, else the driver's label. |
| R2 "No second row" was false for a reader that is off and for accounts without a key | True: `usageLimits.ts:478-481`, `:139-149` | AC-01 and the table: under the option a key match suppresses the row whatever the reason; an account without a key gets its own row and the table says nothing ties the two. Both pinned in T-01. |
| R3 "At a limit" contradicted Copilot's "still runs"; spent window not computable | True: `apps/server/src/provider/copilotUsageLimits.ts:195-199`, `packages/contracts/src/providerUsageLimits.ts:80-82`, `packages/shared/src/usageWindows.ts:49-56` | AC-03: one formula, with `spendControlReached`, a live unscoped window and Copilot's flag; past resets never show. |
| R4 Where "all three or none" is enforced | True: `packages/contracts/src/baseSchemas.ts:128-137`, `copilotUsageLimits.ts:67-75`, `:113-125` | AC-07: no check in the contract, the reader emits all or none, the row treats anything else as no amounts; Copilot also publishes none when `remaining` is missing. |
| S1 Reasons and the count were built for two drivers | True: `usageLimits.ts:482-489`, `apps/server/src/provider/openCodeUsageLimits.ts:40` | Cut: the header counts reading rows only and adds "<m> without a reading" (D-09); `apiBilling` is for Claude and Codex only. |
| S2 The 1397 seam is narrower than claimed | True: `usageLimits.ts:500-502` | The paragraph under the table says what the table gives (a signed-out row) and what stays 1397 T-07's (`account.hold` in both row components). 1397's file list is updated in the sweep after 1413's review. |
| S3 The note and the sort had no file | True: `apps/web/src/components/usage/subscriptions/subscriptionRows.ts:25-39` | AC-02 names `subscriptionRows.ts`; T-02 lists it and its test; "shorter" is defined in the notes table. |
| S4 The survival test cannot see a plan-field flip | True: `copilotUsageLimits.ts:151-155` | Accepted and said in Risks. |
| S5 Cursor's expiry on weekly plans sat only in Risks | True: `apps/server/src/provider/cursorUsageLimits.ts:26-27` | Moved to Scope Out with the reason, and D-08 names the one clause that would publish it. Reported to Anton as a part of his request this plan does not deliver. |
| S6 The trial cannot prove the account | True | AC-08 records the CLI version and home and compares with what the signed-in CLI shows. |
| S7 The screenshots cannot evidence AC-01 or AC-03 | True: `apps/web/tests/subscription-resets/main.tsx:53-101` | AC-10 says the screenshots show row drawing; AC-01 and AC-03 rest on T-01's tests. |
| Minor points | True: `SubscriptionRow.tsx:119`, `cursorUsageLimits.ts:127-129` | AC-04 (two texts), AC-05 ("Set day"), AC-06 (no windows), the Cursor note's wording, a web test in T-04. |
