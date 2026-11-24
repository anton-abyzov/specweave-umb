# Usage and availability in the chat model picker

## Problem

The user (October 21, 2026): "Why, when we are in the chat, don't we see usage? ... combining the usage and available models ... when nothing is left for a model, specifically for a provider, we show it disabled. It must be clear to the user why." Their screenshots show the chat composer's model picker with no usage anywhere.

Cause: the only usage chip, `ProjectUsageIndicator`, is mounted in one place, the project coordinator composer (`apps/web/src/components/studio/ProjectWorkspaceSurface.tsx`). Chat threads never render it, and nothing in the model picker, its provider rail or send validation reads `ServerProvider.usageLimits`. Even where the chip is mounted it returns nothing when a provider reports no windows, so unknown states vanish instead of saying so.

## Scope

In: the SpecWithCode app repository (`anton-abyzov/specwithcode-dev`), web only: the composer model trigger, `ModelPickerContent` rows, its provider rail and a usage band, the coordinator picker list, a pure availability model, user docs and a headless fixture.

Out:
- automatic switching, fallback order, limit handoff and auto-continue (owned by 0955 and 0968; this reads the same windows and adds no router);
- blocking send on usage (the existing limit flow decides what a message does when the selected model is out);
- settings pickers (defaults, fallback order, scheduled tasks), which may point at a model that is only out until its reset;
- hub (`usageLimitSources`) accounts, which can't lend capacity to this machine's instance;
- iOS and mobile;
- live database access of any kind (the M4 store is under a malformed-image incident).

## Acceptance Criteria

- [ ] AC-01: The chat composer's model button shows the selected model's room: a ring and `62%` (amber at 20% left, red at 5%), `Limit` when a fresh read shows its limit reached, and a dashed ring with a word for states that can't be vouched for (`Checking`, `Unknown`, `Offline`, `Reset`, `~46%`, `Limit?`). On a narrow composer only the ring shows; the button's accessible name and tooltip carry the full sentence.
- [ ] AC-02: Every model row in the picker shows its room after the provider name (`Claude · 18% left · resets in 2d 5h`). Providers that never report usage, or bill per token, say so once in the band (and in Favorites and search rows), never as a number.
- [ ] AC-03: Selecting a provider in the rail shows a band above its models: "<provider> on <machine>", when it was read, each live window with a bar of what is left, its value and reset, account-wide windows before model-family windows (`Weekly · Fable`), windows blocked by a spent one as Blocked, and windows that reset since the read as "Reset, not read since".
- [ ] AC-04: A model is disabled only on confirmed evidence: a read under 15 minutes old with a live spent window that applies to it (and the provider not still reporting that it accepts turns), or the provider's own admission denial (`ordinaryUsageAllowed: false`, spend cap, rate limit) on a fresh read. The row stays readable at full opacity, names the limit and its reset, and its tooltip explains whether the limit is shared by every model on the account or caps one family.
- [ ] AC-05: A spent model-family window (Fable weekly) disables only that family; the rail marks a provider red only when an account-wide limit is out, amber when low. Claude through GitHub Copilot is judged on its own instance and is never disabled by native Claude's limit.
- [ ] AC-06: Missing or untrusted telemetry never disables anything and never renders as 0% or 100%: no read yet, an old read, a reset since the read, a failed probe, not signed in, an offline machine, a provider that doesn't report, per-token billing.
- [ ] AC-07: Keyboard shortcuts keep their numbers: a usage-blocked row keeps its ⌘N label (dimmed) and the shortcut, Enter and click do nothing on it; other shortcuts still pick. Context-disabled rows (locked provider) keep today's behavior.
- [ ] AC-08: While a turn runs, the picker says which model it runs on and that a new pick applies from the next message.
- [ ] AC-09: The coordinator picker list shows the same row usage and band for its host; settings pickers are unchanged.
- [ ] AC-10: Headless evidence over the real picker components: room, account limit, family limit, old read, reset since read, loading, probe failed, offline and running, at 390 and 1280 px, light and dark, with no sideways scrolling, plus a trigger gallery and the real `ChatComposer` regression fixture.

## Approach

- `apps/web/src/studio/modelAvailability.ts`: `modelAvailability()` folds one provider snapshot and model into room / exhausted / denied / stale / loading / unknown / perToken / unreported / offline, reusing `usageWindows` (`windowAppliesToModel`, `isLiveWindow`, `windowModelScope`) and `providerFallback` (`usageDeniesTurn`, `isPerTokenProvider`), with `MACHINE_USAGE_MAX_AGE_MS` as the freshness bound. `availabilityText()` writes the short and long words.
- `apps/web/src/components/chat/ModelUsage.tsx`: `useModelPickerUsage` (clock advances on open and on snapshot changes, never on a timer), `ModelUsageMeter`, `ModelPickerUsageBand`, `ModelPickerRunningNote`.
- `ProviderModelPicker` takes an opt-in `usage` config; `ModelPickerContent` merges usage blocks with the existing `getModelDisabledReason` but numbers shortcuts only around structural disables; `ModelListRow` and `ModelPickerSidebar` render row text and the rail mark.
- `ChatComposer` passes connection, machine nickname and the running selection; `CoordinatorModelPicker` passes its host.
- Fixture `apps/web/tests/picker-usage/` with a frozen clock and fictional providers.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Send stays allowed when the selected model is out; the existing usage-limit setting (wait, switch, ask) owns what happens, so the picker never bypasses it or the paid-API opt-in.
- D-02: 15 minutes is "fresh", the same bound fleet capacity uses; provider snapshots refresh every 5 minutes by default.
- D-03: A spent window with `ordinaryUsageAllowed: true` stays selectable and says "still accepted", since the provider itself accepts the turn (extra usage).
- D-04: Usage in the trigger is for single-model pickers without a custom label; the coordinator already shows its usage chip, so its trigger is unchanged.

## Tasks

### T-01 Availability model
- AC: AC-04, AC-05, AC-06 | Files: apps/web/src/studio/modelAvailability.ts, apps/web/src/studio/modelAvailability.test.ts | Test: vp test run apps/web/src/studio/modelAvailability.test.ts

### T-02 Picker trigger, rows, rail and band
- AC: AC-01, AC-02, AC-03, AC-07, AC-08, AC-09 | Files: apps/web/src/components/chat/ModelUsage.tsx, ModelListRow.tsx, ModelPickerContent.tsx, ModelPickerSidebar.tsx, ProviderModelPicker.tsx, ChatComposer.tsx, apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx (+ test mock), docs/user/usage.md, AGENTS.md | Test: vp test run on the picker, coordinator picker and settings picker tests; web typecheck; web production build

### T-03 Headless evidence
- AC: AC-10 | Files: apps/web/tests/picker-usage/ | Test: node apps/web/tests/picker-usage/verify.mjs <dir> and node apps/web/tests/decision-card-reply/verify.mjs <dir> (headless)

### T-04 Verify and close 0983
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
