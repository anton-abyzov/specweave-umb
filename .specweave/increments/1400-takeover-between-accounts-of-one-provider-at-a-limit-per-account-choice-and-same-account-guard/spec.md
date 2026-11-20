# Takeover between accounts of one provider at a limit: per-account choice and same-account guard

## Problem

Split out of increment 1397 after its review (November 18, 2026) so this change ships and reverts alone. Anton chose option A on November 18, 2026 (D-01). Terms evidence: `.specweave/increments/1397-named-accounts-per-provider-add-sign-in-and-switch-without-the-terminal/reports/terms-of-service.md`. App paths are in `repositories/anton-abyzov/specwithcode` at `be3fee857`; citations are rechecked when a task starts.

1. **The app moves a limited thread to another account of the same vendor, by default.** `providerLimitAction` defaults to "switch" (`packages/contracts/src/settings.ts:2075-2077`) and the candidate rank puts the same driver first (`packages/shared/src/providerFallback.ts:459-462`). Anton kept this on October 27, 2026 (1055 D-01), before OpenAI's terms were read.
2. **OpenAI's terms forbid it on a plain reading.** "Interfere with or disrupt our Services, including circumvent any rate limits or restrictions"; "You cannot bypass a limit or increase it through a setting." Two free ChatGPT accounts rotated so Codex keeps running is that case. Anthropic does not name it but lists bypassing "restrictions, or guardrails" as abuse and says limits "assume ordinary, individual usage". Both may close accounts without notice. A consent in the app is the person accepting that risk; it does not make the use permitted.
3. **Nothing stops a "switch" between two instances on one account on the same machine.** Only the cross-machine path checks, and it fails closed on an unknown identity (`packages/shared/src/machineFallback.ts:167-189`).
4. **A takeover moves the conversation.** Shared Codex sessions and the Claude transcript copy (`apps/server/src/provider/Drivers/ClaudeTranscriptTransfer.ts`) put one account's conversation under another account's retention and, for a work account, its administrator's view.

## Scope

In: the same-account guard on one machine; a per-account "Take over at a limit" choice with the terms shown; what happens to existing installs; every caller of the fallback resolvers.

Out: fallback to other providers, wait, ask and auto-resume (unchanged). The rotation and cache policy of 1055. Choosing an account by hand, which stays possible and ungated: this switch is a disclosure gate on automatic behaviour, not a compliance boundary. Depends on 1397 T-01 to T-03: the account key, its read time, the plan class and the hold, all on `auth` in the provider snapshot.

## Acceptance Criteria

- [ ] AC-01: A same-vendor instance is never an automatic takeover target when its account key equals the stopped instance's, or when either key is missing or its `accountKeyObservedAt` is more than 15 minutes old. The health refresh rereads the key only while a client watches provider status (1397 Approach), so the server-side callers (the fallback worker, the scheduled route, the unopenable fallback) ask for a fresh status probe of a candidate whose key is older than that (`ProviderRegistry.refreshInstance`, `apps/server/src/provider/ProviderRegistry.ts:109`) before deciding, and treat a failed probe as `unknown_account`. The interface shows what the last snapshot says and marks a stale key as "will be checked at the limit". The skipped candidate's reason is recorded as `same_account` or `unknown_account` and shown where the thread explains its stop.
- [ ] AC-02: Written for option A; B or C needs this spec amended before sw-do (see D-01). Under option A, a same-vendor account is a target only when its "Take over at a limit" is on, and an instance with no stored choice counts as off.
- [ ] AC-03: Under option A, the first start after the update on a machine that has two or more subscription accounts of one vendor and "switch" as its limit action shows one notice, once per machine (the fact that it was shown is kept in the server's state folder), also in the release notes: accounts of the same provider no longer take over at a limit until turned on per account. Nothing is shown on other machines.
- [ ] AC-04: Turning the switch on shows that vendor's quoted terms with links and says, in these words or their translation: the vendor may suspend or close accounts that do this; turning it on is your decision and does not make it allowed; threads that move carry their conversation to this account; it applies when any other <vendor> account on this machine hits a limit. It records the time and the signed-in app user. "Keep off" is the default button.
- [ ] AC-05: An account on a Free plan has no switch and is never a source or target; the row says why. An account on an organisation plan (Team, Business, Enterprise, Edu) is never a source or target for a personal one, or the reverse.
- [ ] AC-06: The rule holds in every caller of the resolvers: the fallback worker, the three calls in `apps/web/src/components/ChatView.tsx`, `apps/server/src/scheduledTasks/ScheduledTaskProviderRoute.ts` and `apps/server/src/orchestration-v2/unopenableFallback.ts`. Each has a test. What the interface says a thread will do at its limit matches what the server does.
- [ ] AC-07: With every switch off, a limited thread behaves exactly as if the other account were not installed: it goes to another provider, waits or asks as its settings say.
- [ ] AC-08: `docs/user/provider-accounts.md` states the rule, the terms and the risk. No copy presents takeover as a way past limits.

## Approach

`limitTakeover: { enabled, acknowledgedAt, acknowledgedBy }` on the instance's `account` block (`packages/contracts/src/providerInstance.ts`), stamped onto the snapshot with the account key by `withInstanceIdentity`, so resolvers that already receive snapshots need no new argument. Two pure rules in new `packages/shared/src/providerAccountTakeover.ts`, applied where candidates are built in `packages/shared/src/providerFallback.ts` (1,619 lines already, so only the call is added). The plan class is `auth.planClass` (`free`, `personal`, `organisation`, `unknown`), which 1397 T-02 derives from the CLI's `planType` or `subscriptionType`, not from the display label (`packages/contracts/src/providerUsageLimits.ts:111` calls that one display only); `unknown` counts as not eligible. The once-per-machine notice is recorded by new `apps/server/src/provider/takeoverNotice.ts`.

Ships as its own pull request. Risk: people who rely on today's takeover see threads wait at a limit after the update; AC-03's notice is the answer. Rejected: one global setting (hides which account is put at risk); gating manual account choice (the person's own act).

## Decisions

### Asked
- D-01 What should happen at a limit between two accounts of the same vendor? → Anton, November 18, 2026: A, "off until I turn it on".
  - A (chosen): off until turned on per account with the terms shown; never for Free plans; existing installs become off with a notice.
  - B: existing accounts keep taking over, with a notice; new accounts are off.
  - C: keep today's behaviour and add only the same-account guard.
  - AC-02 to AC-05, AC-08 and T-03 are written for A. B needs a rule and a criterion for which existing accounts keep taking over; C drops AC-02 to AC-05 and T-03. Either is a spec amendment and a fresh review before sw-do.

### Defaulted (change any before sw-do)
- D-02 Unknown or stale identity fails closed, as between machines.
- D-03 Free and cross personal/organisation takeover are excluded, not merely warned about.
- D-04 The 15-minute freshness matches the cross-machine guard and is three health refreshes.

### Open
- none

## Tasks

### T-01 Takeover choice in the contract and on the snapshot
- AC: AC-02 | Files: packages/contracts/src/providerInstance.ts, packages/contracts/src/providerInstance.test.ts, packages/contracts/src/server.ts, apps/server/src/provider/Drivers/instanceIdentity.ts | Test: cd repositories/anton-abyzov/specwithcode && vp test run packages/contracts/src/providerInstance.test.ts

### T-02 The two rules and every resolver caller
- AC: AC-01, AC-02, AC-05, AC-06, AC-07 | Files: packages/shared/src/providerAccountTakeover.ts, packages/shared/src/providerAccountTakeover.test.ts, packages/shared/src/providerFallback.ts, packages/shared/src/providerFallback.test.ts, apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, apps/server/src/orchestration-v2/ProviderFallbackWorker.takeover.test.ts, apps/server/src/orchestration-v2/unopenableFallback.ts, apps/server/src/orchestration-v2/unopenableFallback.test.ts, apps/server/src/scheduledTasks/ScheduledTaskProviderRoute.ts, apps/server/src/scheduledTasks/ScheduledTaskProviderRoute.test.ts, apps/web/src/components/ChatView.tsx, apps/web/src/components/ChatView.takeover.test.tsx | Test: cd repositories/anton-abyzov/specwithcode && vp test run packages/shared/src/providerAccountTakeover.test.ts packages/shared/src/providerFallback.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.takeover.test.ts apps/server/src/orchestration-v2/unopenableFallback.test.ts apps/server/src/scheduledTasks/ScheduledTaskProviderRoute.test.ts && cd apps/web && vp test run src/components/ChatView.takeover.test.tsx

### T-03 The switch, the consent dialog, the notice and the docs
- AC: AC-03, AC-04, AC-05, AC-08 | Files: apps/web/src/components/settings/TakeoverConsentDialog.tsx, apps/web/src/components/settings/TakeoverConsentDialog.test.tsx, apps/web/src/components/settings/ProviderAccounts.tsx, apps/server/src/provider/takeoverNotice.ts, apps/server/src/provider/takeoverNotice.test.ts, apps/web/src/i18n/phrases/de.ts, apps/web/src/i18n/phrases/es.ts, apps/web/src/i18n/phrases/fr.ts, apps/web/src/i18n/phrases/ja.ts, apps/web/src/i18n/phrases/ko.ts, apps/web/src/i18n/phrases/pt.ts, apps/web/src/i18n/phrases/ru.ts, apps/web/src/i18n/phrases/zh.ts, docs/user/provider-accounts.md, CHANGELOG.md | Test: cd repositories/anton-abyzov/specwithcode/apps/web && vp test run src/components/settings/TakeoverConsentDialog.test.tsx && cd ../.. && vp test run apps/server/src/provider/takeoverNotice.test.ts

### T-04 Verify and close 1400
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: .specweave/increments/1400-takeover-between-accounts-of-one-provider-at-a-limit-per-account-choice-and-same-account-guard/reports/acceptance.md | Test: specweave verify 1400-takeover-between-accounts-of-one-provider-at-a-limit-per-account-choice-and-same-account-guard
