# Usage meter that names its account, in the model chip

## Problem

On October 24, 2026, the user saw "19% left" beside a Codex mark in the coordinator footer, on the composer's first row, away from the "Codex · GPT-6.1-Sol" chip. They could not tell which model it belonged to. They asked for a clean way to show usage now that a fallback model can run instead of the home model.

The number is the weekly limit of the Codex account `admin@easychamp.com` on MacBook M4MAX. GPT-6.1-Sol has no separate limit; every Codex model on that ChatGPT account shares the allowance. Claude has account-wide 5-hour and weekly windows plus a weekly window for one model family ("Weekly · Fable").

The 1041 stack is open and unmerged:
- #637 removes the separate chip (`ProjectUsageIndicator`) and puts a meter for the running model in the coordinator's chip.
- #657 fits the meter into the measured chip ladder.
- #665 adds the "for <home>" detour.

Even with the stack merged, these gaps remain:
- the meter is `aria-hidden` and nothing names its account, machine or window;
- the number shows only at the `full` fit;
- "Limits by machine" lists the same account once per machine, with different read times (25% and 32% for one Claude account);
- nothing defines what the meter shows after an account switch.

At 18:45 UTC the same day the user reported that a thread chip, "Claude Code · Opus 5.5 ⭕5%", looked like "tokens left for the fallback". No fallback was running: the thread's pick and its run were both Opus 5.5, and the 5% was the Claude account's 5-hour window. Four cues cause the misreading:
- red at 5% left, with no window or account named;
- the same account percentage repeated on every model row;
- "Billing unverified" on every row;
- the footer "Running on Claude Opus 5.5 (Claude). A new pick applies from the next message.", shown even when the run is the pick.

The research report is `/Users/antonabyzov/.specwithcode/m4/evidence/usage-meter-model-unit-20261024/report.md` and the mockups are `/Users/antonabyzov/.specwithcode/m4/evidence/usage-meter-model-unit-20261024/mockups.html`.

## Scope

In (anton-abyzov/specwithcode-dev, after #637, #657 and #665 merge):
- the model chip's usage meter: its accessible name, tooltip and fit steps;
- the limits view behind the chip (`MachineLimitsPanel`), grouped by account;
- meter states: stale, unknown, per token, spent, account switch;
- the picker's model rows, the account line, rail dot copy, the running footer and the billing line;
- one shared window-name helper and one shared tone rule for every usage surface: chip, rows, rail, band, limits view, `/usage` and the coordinator chip;
- a server prerequisite: Codex per-model buckets get a `modelScope`.

Out:
- limit fallback policy (0955, 0968, 1052);
- billing logic (1050);
- the `/usage` dashboard (1007, 1029);
- the 1041 detour wording and row fit;
- any settings, sign-in or paid-spend change;
- iOS, which consumes the shared rule later.

## Acceptance Criteria

- [ ] AC-01: The model chip in both composers shows one usage meter. It is for the model the thread is on (the running model while a turn runs, otherwise the saved selection) and uses the execution machine's own reading. A home model shown through the fallback detour never gets a second meter. Neither composer renders a separate usage chip.
- [ ] AC-02: The chip's accessible name is short: model, % left and window name, for example "Model: Claude Code · Opus 5.5, 5% of 5-hour limit left. Change model". The tooltip and `aria-describedby` give the provider account (by plan or provider; the email appears only in the limits view), the machine, the window, % left and reset. They also carry a scope sentence generated from the window's scope: shared by every model on the account, including use from other machines and apps, or "Counts only <family> models". Tone is never the only cue. The coordinator's `triggerAriaLabel` must include this.
- [ ] AC-03: The binding window is the live window with the least left among those that apply to the model; a family-only window counts only for that family. When the home window is spent and a fallback is eligible, the chip says "Limit · next on <model>". Otherwise it says "Limit · resets in <reset>". While extra usage is allowed (`providerAllows`), the meter stays amber, not "Limit".
- [ ] AC-04: Fit: the % value shows at the `full` and `model` fits. The `name` fit drops the ring for the model name. At `icon`, the ring wraps the provider mark. The meter never pushes the model name below 2.5em. This is measured in the 1041 fit matrix at 320, 390, 520 and 1280 px, in light and dark.
- [ ] AC-05: States:
  - a reading older than 15 minutes shows a dashed ring and "~N%";
  - loading, unknown and an offline machine keep today's dashed ring with "Checking", the reason or "Offline";
  - an unreported reading shows no meter;
  - per-token billing shows a new "per token" tag and no ring;
  - after an account switch, no meter shows until the new account's first reading; the previous account's value is never shown.
- [ ] AC-06: The limits view lists:
  - "Coordinator now" first (in a thread, "This thread now"): account, machine, read time and every window, with the binding window marked;
  - then the fallback order, each entry with its state;
  - then the other accounts, once each, with their machines.

  An account read on several machines shows its freshest reading and its read time. Rows keyed `instance:` have no reported identity and stay per machine.
- [ ] AC-08: One shared tone rule decides every usage surface: chip, rows, rail, band, limits view, `/usage` and the coordinator chip. Room at 20% left or less, including 5%, is amber. Red appears only for a blocking read, always together with the word "Limit".
- [ ] AC-09: One shared `windowName(window)` helper names every window on every surface. It maps 300 minutes to "5-hour" and 10080 to "weekly", falls back to the label, and keeps a Codex bucket prefix. No surface shows "Session".
- [ ] AC-10: Model rows carry no account-wide room figures; they keep family windows, blocks and the denied, stale and unknown states. Whenever no provider band is shown (Favorites, search, the alternatives view), one account line sits above the list, for example "Account limits: Claude 5% of 5-hour · 55m (this thread) · Codex 17% of weekly · 5d 22h".
  - It covers only the providers that have visible rows, with the provider of the displayed model first.
  - It wraps rather than truncating to "+N".
  - Its marker reads "this thread" or "coordinator" depending on the surface, and is left out in multi-select.
  - It requires Codex per-model buckets to carry a `modelScope`, set on the server (`codexUsageLimits.ts`), with a test.
- [ ] AC-11: The tooltip and aria-label on the existing rail dots name the window, for example "Claude: 5% of the 5-hour limit left, resets in 55m". This is a copy change; the stale comment at `ModelPickerSidebar.tsx:67-71` is corrected.
- [ ] AC-12: When the running model equals the pick, the running footer reads "Picks apply from your next message." When they differ, it reads "This turn stays on <running>. Your pick, <pick>, starts with your next message."
- [ ] AC-13: The billing line renders only when it states a fact; "Billing unverified" is no longer the default. This is gated on agreement from 1050. Deferred to the 1050 owner (October 25, 2026): PR #756 leaves the billing line unchanged.
- [ ] AC-07: Headless fixture screenshots cover AC-01 to AC-06: home, fallback, returned home, spent, stale, unknown, per token, account switch, and two machines sharing one account. Each is shot in light and dark at 390 and 1280 px, with PWDEBUG=0 and evidence saved to files. Coverage extends to AC-08 to AC-13: the reported thread case (home model, 5% left, no fallback), Favorites, search and alternatives with the account line, and the running footer both matching and differing.

## Approach

1. Build on #657's `PARTS_BY_FIT` (`apps/web/src/components/chat/modelChipFit.ts`): `usage-value` joins the `model` fit, and the `icon` fit gains a mark-wrapping ring.
2. `ModelUsageMeter` (`apps/web/src/components/chat/ModelUsage.tsx`) exposes a description that the trigger puts into its accessible name and tooltip. That text comes from `modelAvailability.ts` and the account fields in `packages/shared/src/usageLimits.ts` (`describeLimitAccount`).
3. `MachineLimitsPanel` (#637) is regrouped by `accountKey`. It reuses `collectLimitAccounts` pooling, takes the freshest snapshot per account in the popover only, and lists `sharedWith` machines. #642's sheet button moves here when #642 is rebased onto #637.
4. Readings are keyed by account identity, so a switch drops the old value.

Rejected:
- a labeled separate chip (it stays detached and clips first);
- two rings, active and home (they suggest per-model limits);
- a segmented bar in the chip (unreadable at 14 px).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The meter follows the model the thread is on, not the home model or a predicted next turn. The home model's state appears in the tooltip and the limits view as a return time.
- D-02: The proposal waits for the 1041 stack to merge and does not fork it. 1041 keeps the coordinator's `pickInstanceId` change (#665).
- D-03: Copy says "limit" and names the window, never "quota for <model>".
- D-04: The fallback "Back to <home>" button stays enabled and adds "Limit resets <time>; sending now may fail". It is never disabled, because the reading may be stale or extra usage may be allowed. The fallback detail copy ("The Claude account's 5-hour limit is reached") belongs to 1041, as a follow-up on #665 after the stack is rebased onto origin/main `e201ddb568` (1.0.76).
- D-05: Overlap with #642. It edits the limits footer link that #637 moves into `MachineLimitsPanel`. Rebase #642 onto #637 and move its sheet button there before 1054 touches that view.
- D-06: The email stays out of the chip tooltip, because screenshots and recordings would expose it. It appears only in the limits view.
### Open
- none

## Tasks

### T-01 Meter description and fit steps
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/chat/ModelUsage.tsx, apps/web/src/components/chat/modelChipFit.ts, apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/src/studio/modelAvailability.ts | Test: vp test run apps/web/src/components/chat/ModelUsage.test.tsx apps/web/src/studio/modelAvailability.test.ts

### T-02 Meter states and account switch
- AC: AC-05 | Files: apps/web/src/studio/modelAvailability.ts, apps/web/src/components/chat/ModelUsage.tsx | Test: vp test run apps/web/src/studio/modelAvailability.test.ts

### T-03 Limits view by account
- AC: AC-06 | Files: apps/web/src/components/studio/shell/ProjectUsageIndicator.tsx, apps/web/src/components/studio/shell/HostLimits.tsx, apps/web/src/studio/hostLimitsModel.ts | Test: vp test run apps/web/src/studio/hostLimitsModel.test.ts

### T-04 Shared window name and tone rule
- AC: AC-08, AC-09 | Files: packages/shared/src/usageWindows.ts, apps/web/src/studio/usageIndicatorModel.ts, apps/web/src/studio/modelAvailability.ts, apps/web/src/components/chat/ModelUsage.tsx, apps/web/src/components/studio/shell/HostLimits.tsx, apps/web/src/components/usage/UsageLimits.tsx | Test: vp test run packages/shared/src/usageWindows.test.ts apps/web/src/studio/modelAvailability.test.ts

### T-05 Codex bucket scope (server)
- AC: AC-10 | Files: apps/server/src/provider/codexUsageLimits.ts | Test: vp test run apps/server/src/provider/codexUsageLimits.test.ts

### T-06 Rows, account line, rail copy, running footer, billing line
- AC: AC-10, AC-11, AC-12, AC-13 | Files: apps/web/src/components/chat/ModelPickerContent.tsx, apps/web/src/components/chat/ModelListRow.tsx, apps/web/src/components/chat/ModelPickerSidebar.tsx, apps/web/src/components/chat/HarnessDescription.tsx | Test: vp test run apps/web/src/components/chat/ModelPickerContent.test.tsx apps/web/src/components/chat/HarnessDescription.test.tsx

### T-07 Headless evidence
- AC: AC-07 | Files: apps/web/tests/fallback-composer/model-controls.mjs, apps/web/tests/picker-usage | Test: headless matrix to ~/.specwithcode/m4/evidence/usage-meter-model-unit-1054/

### T-08 Verify and close 1054
