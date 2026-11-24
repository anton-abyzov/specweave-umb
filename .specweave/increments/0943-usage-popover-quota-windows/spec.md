# Every quota window in the limits popover

## Problem

The "Limits by machine" popover shows every window only for the coordinator's account. Every other provider row collapses to its fullest window with no window name: "Claude 12% left in 4d 16h" does not say whether the 5-hour or the weekly window is the one running out, and the other window is invisible (user screenshot, October 19, 2026). Claude's 5-hour window is labelled "Session", which is not the name people use for it.

## Scope

In: the usage chip popover (`HostLimitsCompactView`) and Usage → Limits by machine blocks (`ProviderRow`) in SpecWithCode (`anton-abyzov/specwithcode-dev`). Out: provider probes, account or plan changes, spending, the pooled view, the chip label.

## Acceptance Criteria

- [ ] AC-01: Every provider with source-reported windows lists each window on its own aligned row (label, bar, "N% left", reset), on every machine, not only the coordinator's.
- [ ] AC-02: A window whose source reports a duration under a day is named by it ("5-hour" for Claude's 300-minute session); weekly, model-scoped ("Weekly · Fable") and windows without a duration keep their reported label.
- [ ] AC-03: The window that runs out first (least left among live account-wide windows, or the spent window blocking the others) is marked as binding: full-contrast label and value, the others muted, and its accessible name says it limits the provider. Percentages are never averaged or merged.
- [ ] AC-04: A blocked, stale, unreported or API-billed state never renders as 0% or 100% left: blocked says "Blocked · by <window>" (that window's row shows its reset; screen readers also hear when it is usable again), stale says the window reset since the reading, notices stay text.
- [ ] AC-05: Account, plan and "also on" sharing lines stay per provider; the popover copy no longer says only the coordinator shows every window.
- [ ] AC-06: Headless light/dark evidence at 1440, 768, 390 and 320 px shows no overlap or wrapping in window rows and aligned columns across machines.

## Approach

`hostLimitsModel.ts`: keep `durationMins` on `HostLimitWindow`, add `windowDisplayLabel` and `bindingWindowId`. `HostLimits.tsx`: compact entries render the window ladder for every provider (the coordinator keeps its tag and plan); `ProviderRow` uses the same label and binding mark. `host-limits.css`: binding/muted styles. Fixture `apps/web/tests/usage-by-machine/` gains a Claude 5-hour + weekly case with weekly binding, a blocked case and a stale case; `verify.mjs` asserts the new rows.

Rejected: one combined bar (two fills in one track) because it hides which window binds; a single "effective" percentage because it hides the other window's reset.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Providers that report only a notice stay hidden in the compact popover except the coordinator's (unchanged from #349); the Limits page still lists them.
- D-02: No separate per-provider summary line; the binding row is emphasised in place so no number appears twice.

## Tasks

### T-01 Window ladder for every provider with the binding window marked
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/web/src/studio/hostLimitsModel.ts, apps/web/src/studio/hostLimitsModel.test.ts, apps/web/src/components/studio/shell/HostLimits.tsx, apps/web/src/components/studio/shell/HostLimitsCompact.test.tsx, apps/web/src/components/studio/shell/host-limits.css, apps/web/src/components/studio/shell/ProjectUsageIndicator.tsx | Test: vp test run apps/web/src/studio/hostLimitsModel.test.ts apps/web/src/components/studio/shell/HostLimitsCompact.test.tsx

### T-02 Headless evidence, PR, release and installed check
- AC: AC-06 | Files: apps/web/tests/usage-by-machine/ | Test: node apps/web/tests/usage-by-machine/verify.mjs

### T-03 Verify and close 0943
