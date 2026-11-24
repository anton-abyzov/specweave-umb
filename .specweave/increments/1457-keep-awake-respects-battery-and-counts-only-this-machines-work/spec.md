# Keep awake respects battery and counts only this machine's work

## Problem

On November 23 to 24, 2026 the M5 MacBook Pro (72.6 Wh, Apple rates about 13 h of web use) went from 87% to 1% in 2 h 38 min, about 24 W. On November 18 it went from 100% to 1% in 3 h 44 min. The battery is healthy (7 cycles, 100% capacity). During a 57-minute display-off stretch, 10 agent threads on M5 ran 514 shell commands (23 `tsc`, 15 `vp test`, Playwright captures). SpecWithCode's `NoIdleSleepAssertion "Electron"` kept macOS from its 1-minute battery idle sleep the whole time.

Two design gaps cause this:

1. `apps/desktop/src/ipc/methods/keepAwake.ts` holds `powerSaveBlocker("prevent-app-suspension")` with no battery check. The desktop app already reads `powerMonitor.isOnBatteryPower`.
2. `apps/web/src/components/desktop/KeepAwakeWhileWorking.tsx` counts an active thread on any connected environment, including other machines whose work does not need this laptop awake.

Evidence: `.specweave/reports/threads/2026-11-24-m5-battery-drain-investigation-november-24-2026-87bcc5-4896d1.md` (umbrella main checkout).

## Scope

In:

- The keep-awake count covers only threads on this machine's own environment.
- A battery choice for the keep-awake hold, enforced in the desktop main process.
- A one-time notice on battery that offers Hand off.

Out:

- Any automatic handoff. Per the Handoff and Sync decisions (November 19, 2026), closing the lid or running on battery never starts a handoff; it starts only by hand, by a coordinator instruction, or from the usage-limit setting.
- Deferring update relaunches on battery.
- Throttling builds or tests.

## Acceptance Criteria

- [x] AC-01: The desktop app holds off idle sleep only while a thread on this machine's own environment (the window's primary environment) is working. Active threads on other connected machines no longer count.
- [x] AC-02: Settings > General has "Keep awake on battery" next to "Keep awake while sessions work". The choices are Only on power adapter (the default), Until battery is below 20%, 30% or 50%, and Always. The desktop main process applies the choice using `powerMonitor` (on-battery and on-ac events and `isOnBatteryPower`) and the battery level the window reports. With Only on power adapter, the hold releases on unplug and returns on plug-in. With Until below N%, it releases at or below N%, and also releases when the level is unknown. With Always, it behaves as today.
- [x] AC-03: On battery, while this machine has working threads, the window shows at most one notice of each kind (released, kept) per battery session, so "Until below N%" can say "kept" and later "released" when the battery crosses the floor; each open window keeps its own count. If the hold is released, it reads "{machine} is on battery and can sleep while N threads work". If the hold is kept, it reads "Keeping {machine} awake on battery while N threads work". Both notices carry a "Hand off…" button that opens the existing Away/Hand off dialog. Nothing moves until the user confirms there.
- [x] AC-04: Unit tests cover the policy function, the main-process controller (power changes re-sync the blocker, and an old payload without a policy defaults to Only on power adapter), the local-only count, and the notice wording and once-per-session rule.

## Approach

- `packages/contracts/src/keepAwake.ts`: `KeepAwakeOnBattery` literals (`adapter-only`, `until-low`, `always`) and the pure function `keepAwakeAllowedOnPower(policy, floorPercent, { onBattery, level })`, exported from the contracts index. The window and the main process share this one rule.
- `packages/contracts/src/settings.ts`: `keepAwakeOnBattery` (default `adapter-only`) and `keepAwakeBatteryFloorPercent` (default 30) in the client settings and the patch.
- `packages/contracts/src/ipc.ts`: `setKeepAwake` takes `{ active, onBattery?, batteryFloorPercent?, batteryLevel? }` and returns `{ holding, onBattery }`.
- `apps/desktop/src/ipc/methods/keepAwake.ts`: the controller keeps each sender's report, works out the hold from the policy and the main process's own `isOnBatteryPower`, and re-syncs on `on-battery` and `on-ac`.
- `apps/web/src/components/desktop/keepAwake.logic.ts` (new): local working count and notice text. `KeepAwakeWhileWorking.tsx` reads the battery level from `navigator.getBattery()` when available, sends the policy, and shows the notice with `requestAway("away")`.
- `apps/web/src/components/settings/SettingsPanels.tsx` and `settingsSearch.ts`: the new row.

Rejected: an automatic handoff on unplug. It contradicts the Handoff decision ("sleep off") and Sync and Hand off (handoff starts only by hand).

Risk: `navigator.getBattery` can be missing. The main process still enforces Only on power adapter from `powerMonitor`, and Until below N% treats an unknown level as low.

## Decisions

### Asked
- D-01: Battery default → Only on power adapter, plus an offer to move heavy threads to a plugged-in machine (owner, November 24, 2026, as the recommended option).
### Defaulted (change any before sw-do)
- D-02: The Hand off offer opens the existing Away dialog (`requestAway("away")`), the machine-wide hand-off entry that decision_sync_and_hand_off keeps as a shortcut you start yourself. Reversible.
- D-03: Floor choices are 20%, 30% and 50%, with 30% stored as the default floor. Reversible.
### Open
- none

## Review

Adversarial reviewer: Gemini 4 Neon (Copilot Enterprise), else GPT-6.2 Sol. Never Grok.

## Tasks

### T-01 Shared battery policy and settings
- AC: AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/keepAwake.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/keepAwake.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/contracts/src/keepAwake.test.ts

### T-02 Main process applies the battery choice
- AC: AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/keepAwake.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/keepAwake.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/ipc/methods/keepAwake.test.ts

### T-03 Window counts only this machine and offers Hand off on battery
- AC: AC-01, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/desktop/KeepAwakeWhileWorking.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/desktop/keepAwake.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/desktop/keepAwake.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/desktop/keepAwake.logic.test.ts

### T-04 Settings row
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json
