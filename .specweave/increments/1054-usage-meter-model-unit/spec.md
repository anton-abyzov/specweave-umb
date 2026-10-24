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

The research report is `/Users/antonabyzov/.specwithcode/m4/evidence/usage-meter-model-unit-20261024/report.md` and the mockups are `/Users/antonabyzov/.specwithcode/m4/evidence/usage-meter-model-unit-20261024/mockups.html`.

## Scope

In (anton-abyzov/specwithcode-dev, after #637, #657 and #665 merge):
- the model chip's usage meter: its accessible name, tooltip and fit steps;
- the limits view behind the chip (`MachineLimitsPanel`), grouped by account;
- meter states: stale, unknown, per token, spent, account switch.

Out:
- limit fallback policy (0955, 0968, 1052);
- billing logic (1050);
- the `/usage` dashboard (1007, 1029);
- the 1041 detour wording and row fit;
- any settings, sign-in or paid-spend change;
- iOS, which consumes the shared rule later.

## Acceptance Criteria

- [ ] AC-01: The model chip in both composers shows one usage meter. It is for the model the thread is on (the running model while a turn runs, otherwise the saved selection) and uses the execution machine's own reading. A home model shown through the fallback detour never gets a second meter. Neither composer renders a separate usage chip.
- [ ] AC-02: The chip's accessible name and tooltip give the provider, account (email, or plan when there is no email), the machine, the binding window's name, % left and reset. They also carry a scope sentence generated from the window's scope: shared by every model on the account, including use from other machines and apps, or "Counts only <family> models". Tone is never the only cue. The coordinator's `triggerAriaLabel` must include this.
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
- [ ] AC-07: Headless fixture screenshots cover AC-01 to AC-06: home, fallback, returned home, spent, stale, unknown, per token, account switch, and two machines sharing one account. Each is shot in light and dark at 390 and 1280 px, with PWDEBUG=0 and evidence saved to files.

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
### Open
- none

## Tasks

### T-01 Meter description and fit steps
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/chat/ModelUsage.tsx, apps/web/src/components/chat/modelChipFit.ts, apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/src/studio/modelAvailability.ts | Test: vp test run apps/web/src/components/chat/ModelUsage.test.tsx apps/web/src/studio/modelAvailability.test.ts

### T-02 Meter states and account switch
- AC: AC-05 | Files: apps/web/src/studio/modelAvailability.ts, apps/web/src/components/chat/ModelUsage.tsx | Test: vp test run apps/web/src/studio/modelAvailability.test.ts

### T-03 Limits view by account
- AC: AC-06 | Files: apps/web/src/components/studio/shell/ProjectUsageIndicator.tsx, apps/web/src/components/studio/shell/HostLimits.tsx, apps/web/src/studio/hostLimitsModel.ts | Test: vp test run apps/web/src/studio/hostLimitsModel.test.ts

### T-04 Headless evidence
- AC: AC-07 | Files: apps/web/tests/fallback-composer/model-controls.mjs | Test: headless matrix to ~/.specwithcode/m4/evidence/usage-meter-model-unit-1054/

### T-05 Verify and close 1054
