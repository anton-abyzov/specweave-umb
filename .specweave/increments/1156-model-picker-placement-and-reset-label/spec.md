# Model picker placement and Reset label

## Problem

On macOS the composer model picker opens detached from its chip, in both the thread composer and the project coordinator composer: at the top of the window, beside the chip, over the other column. Cause: the picker's natural height (about 930px) exceeds the room both above and below the chip before its max height applies, so Base UI's collision fallback moves it to the perpendicular axis (`data-side="right"` or `left`) and shifts it to the window top. Reproduced headless in the worktree dev app at 1400x900: chip at y 510, picker at x 605, y 7, side right.

Row provider names truncate to "Co…" or "C." because the plan pill ("ChatGPT Pro 20x Subscription") does not shrink.

The chip shows "Reset" with a dashed ring when a Claude usage window has reset since usage was last read. It is good news (the limit refilled; usage is read again before the next turn) but reads like a button or an error.

## Scope

In: picker placement for every `ProviderModelPicker` popup, row provider/plan truncation, the reset-since-read chip and header wording, a headless fixture check. Out: the picker's internal layout redesign, usage-read cadence.

## Acceptance Criteria

- [x] AC-01: The picker opens above (or below) its chip, left-aligned to it, never beside it, in the thread and coordinator composers, at wide and narrow widths, and stays fully inside the viewport.
- [x] AC-02: A provider name in a model row stays readable; the plan pill truncates first.
- [x] AC-03: A limit that reset since the last read shows no meter on the chip; the picker header and tooltip say "Limit reset since last read" with the full explanation.

- [x] AC-04: The picker opens once, in its final position: its chip-side edge does not move between the first visible frame and rest, in the coordinator and thread composers.
- [x] AC-05: The chip's tooltip and the picker's usage band show the email the provider reports for the account signed in on that machine; a provider that reports none says so. Read from the live provider snapshot, nothing stored.

## Approach

`ProviderModelPicker.tsx`: `collisionAvoidance={{ side: "flip", align: "shift", fallbackAxisSide: "none" }}`, so the popup flips between bottom and top only and its max height caps to `--available-height`. `ModelListRow.tsx`: provider label `shrink-[0.2]`, plan pill `min-w-0 truncate`. `ModelUsage.tsx` `meterParts`: stale + resetSinceRead with no spent window and no partial reading returns null. `modelAvailability.ts`: short text "Limit reset since last read". Fixture `apps/web/tests/picker-usage/verify.mjs` gains a 560px-tall placement check (fails without the fix) and a no-"Reset" check.

Follow-up: Base UI measures the popup with `--available-height: max-content`, which is invalid inside `min()`, so the combined `max-h` vanished and the popup measured its whole list (1105 px, cap 544). `ModelPickerContent.tsx` now separates the caps (wrapper `max-h-(--available-height)`, picker `max-h-[min(34rem,80dvh)]`). `accountEmailLine` in `modelAvailability.ts` feeds the tooltip, `ModelStateTip` and `ModelPickerUsageBand`. Group headers and Limits by account already show the email.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Reset state → show nothing on the chip; tooltip and header explain (the user offered either; nothing is quieter and the state needs no action).
### Open
- none

## Tasks

### T-01 Anchor the picker to its chip
- AC: AC-01 | Files: apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/tests/picker-usage/verify.mjs | Test: node apps/web/tests/picker-usage/verify.mjs <dir>

### T-02 Readable provider names in rows
- AC: AC-02 | Files: apps/web/src/components/chat/ModelListRow.tsx | Test: vp test run src/components/chat/ModelPickerContent.test.tsx

### T-03 Quiet reset-since-read state
- AC: AC-03 | Files: apps/web/src/components/chat/ModelUsage.tsx, apps/web/src/studio/modelAvailability.ts | Test: vp test run src/studio/modelAvailability.test.ts src/components/chat/ModelUsage.test.tsx

### T-04 Ship: PR, release, installed check on the M4
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: installed app headless or computer screenshot of both composers

### T-06 Open the picker once, in place
- AC: AC-04 | Files: apps/web/src/components/chat/ModelPickerContent.tsx, apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/tests/picker-usage/verify.mjs | Test: node apps/web/tests/picker-usage/verify.mjs <dir>

### T-07 Show the subscription's account email
- AC: AC-05 | Files: apps/web/src/studio/modelAvailability.ts, apps/web/src/components/chat/ModelUsage.tsx, apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/src/components/chat/ModelStateTag.tsx | Test: vp test run src/studio/modelAvailability.test.ts src/components/chat/ModelUsage.test.tsx

### T-05 Verify and close 1156
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1156
