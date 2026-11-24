# Picking the saved coordinator model switches back from a fallback

## Problem

On October 24, 2026, the EasyChamp coordinator ran on "Devin · GPT-6.1 Sol" as a fallback for its saved pick, Codex GPT-6.1-Sol. The Codex account had 4% of its weekly limit left. In the model picker, on the Codex tab, the user clicked GPT-6.1-Sol and nothing happened. The row looked selectable and gave no reason.

Read-only check: `studio_thread_configuration` for `project-coordinator:5848bdc2-3ac2-4ecb-b66e-c10840260324` returned `acpRegistry_devin / gpt-6-1-sol-medium`, and the project's `coordinatorModelSelection` is `codex / gpt-6.1-sol`.

Cause: `CoordinatorModelPicker.changeModel` returned early whenever the clicked row equalled the saved pick (`value`). While a fallback runs, the saved pick is the model the user wants back, so the click was swallowed. No usage, threshold or billing guard was involved. The rows were not disabled, 4% is not spent, and "Billing unverified" is display only.

## Scope

In (anton-abyzov/specwithcode-dev):
- the picker click on the saved row during a fallback;
- the row's disabled reason when no way back is available;
- a headless fixture.

Out:
- the server pre-switch threshold (`providerLimitSwitchAtPercent`, default 95);
- billing identity (1050);
- usage display (1054);
- the 1041 detour wording.

## Acceptance Criteria

- [x] AC-01: While the coordinator runs on a fallback, choosing the saved model from the list runs the same supported switch-back as the "Back to <model>" button. It does not save a new preference or pick another provider.
- [x] AC-02: Low remaining usage (4% left) does not disable the saved row. A saved model whose limit is spent can still be chosen explicitly: row disabling reads only host availability and the switch-back state, never usage. The tests prove the 96% case; no test sets a spent limit. The host's own limit checks still apply before the next turn.
- [x] AC-03: If no switch-back is available, the saved row is disabled with "Switching back isn't available here". While a switch back is in flight, the reason is "Switching models…". Neither triggers provider recovery ("Check again"). The first reason is defensive: in the live app a missing way back also disables the whole picker, so only the unit test and the fixture reach it.
- [x] AC-04: With no fallback running, choosing the saved model stays a no-op, and a different model still saves through `onChange`.
- [x] AC-05: A headless fixture clicks the real picker for the states fallback, noback, switching and home, in light and dark at 390 and 1280 px. On the unfixed code it fails at the first case (`unfixed-main-failure.txt`). Evidence is in `~/.specwithcode/m4/evidence/coordinator-pick-back-20261024/`. The fixture also captures the `*-reason.png` files and checks that "Check again" never appears.

Delivered in specwithcode-dev #685, merged as `94a8c8d3f38db249bf20276777f6e94b8282c082`. Installed acceptance waits for the 1.0.77 install.

Follow-up, outside this increment: comments at `apps/web/src/components/chat/ProviderModelPicker.tsx:82-83` and `apps/web/src/components/chat/ModelPickerContent.tsx:209-211` still say a model whose limit is spent "can't be chosen".

## Approach

`apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx`:
- `hostDisabledReason` keeps the host and folder checks and still drives provider recovery.
- `getModelDisabledReason` adds the switch-back reasons for the saved row during a fallback.
- `changeModel` calls `running.onSwitchBack()` for the saved row during a fallback.

The automatic reserve stays separate. The server pre-switch uses a command id that is deterministic for each usage window, so a manual return is not reversed again within the same window.

Rejected:
- re-saving the same selection through `onChange` (it is a no-op save and does not move the thread);
- disabling the row at a low percentage (usage is advisory for deliberate choices, #605).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Picking the saved row reuses `onSwitchBack` rather than adding a new command.
### Open
- none

## Tasks

### T-01 Picker switches back from the saved row
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx, apps/web/src/components/studio/shell/CoordinatorModelPicker.test.tsx | Test: vp test run apps/web/src/components/studio/shell/CoordinatorModelPicker.test.tsx

### T-02 Headless click fixture
- AC: AC-05 | Files: apps/web/tests/coordinator-pick-back/ | Test: vp build --config apps/web/tests/coordinator-pick-back/vite.config.ts && node apps/web/tests/coordinator-pick-back/verify.mjs

### T-03 Verify and close 1060
