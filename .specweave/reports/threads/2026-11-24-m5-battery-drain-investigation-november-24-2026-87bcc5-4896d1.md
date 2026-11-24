---
title: M5 battery drain investigation
date: November 24, 2026
machine: M5 (MacBook Pro 14", Apple M5 Max, Mac17,11, macOS 27.2.1)
status: read-only investigation, no changes applied
---

# M5 battery drain investigation

**Verdict:** the drain is real, and the battery is healthy. On battery this Mac runs about 10 SpecWithCode agent threads at once: typechecks, test runs, Playwright captures, and CI waits. That draws 18 to 24 W on average against Apple's light-use rating of about 5.6 W. SpecWithCode's "Keep awake while working" setting is what stops macOS from idle-sleeping while that work runs, including with the display off. Messages also keeps re-asserting a sleep hold. The keep-awake setting has two design gaps: it ignores battery power, and it counts threads on other connected machines.

## Battery health and rated life

| Item | Value |
|---|---|
| Battery (Apple spec) | 72.6 Wh. Apple rates up to 13 h web (about 5.6 W) and up to 20 h video (about 3.6 W) |
| Cycle count | 7 |
| Maximum capacity | 100% (raw 6,434 mAh against 6,195 mAh design) |
| Condition | Normal |
| Thermal warnings | none recorded |

Source: [Apple support, MacBook Pro 14-inch M5 Pro or M5 Max](https://support.apple.com/en-mide/148301). The search index text for this page was jumbled, so check the page itself before relying on the figures.

## Measured drain (from `pmset -g log`)

| Session | Charge | Time | Rate | Draw (72.6 Wh) |
|---|---|---|---|---|
| Lid closed, asleep, November 23 | 100% to 98% over 8.6 h, then 90% to 87% over 9.5 h | ~18 h | ~0.25 to 0.3%/h | ~0.2 W, normal |
| November 23 12:24 to 12:54, display on | 98% to 90% | 30 min | 16%/h | ~12 W (4 threads, 155 commands) |
| November 18 08:00 to 11:43 | 100% to 1% | 3 h 44 min | 26.5%/h | ~19 W |
| November 23 22:34 to November 24 01:12 | 87% to 1% | 2 h 38 min | 33%/h | ~24 W |

Breakdown of last night:

| Window | Display | Charge | Rate |
|---|---|---|---|
| 22:34 to 22:57 | on | 87% to 81% | ~16%/h |
| 22:57 to 23:10 | **off** | 81% to 73% | ~37%/h |
| 23:10 to 23:51 | on | 73% to 48% | ~37%/h |
| 23:51 to 00:48 | **off** | 48% to ~24% | ~25%/h (~18 W) |
| 00:48 to 01:12 | on | ~24% to 1% | ~60%/h |

Display-off drain (25 to 37%/h) matches display-on drain, so the screen, brightness and ProMotion are not the driver. On battery macOS should sleep after 1 minute idle, but it stayed awake for both display-off stretches.

## What kept it awake

- 22:57 to 23:10: audio assertions from coreaudiod, held until 23:47 (sources included a Chrome helper and Wispr Flow), plus SpecWithCode's `NoIdleSleepAssertion "Electron"`.
- 23:51 to 00:48: SpecWithCode's blocker, held continuously (created about 23:34, released at the 01:12 low-battery sleep). In the same hour, `runningboardd` re-asserted `PreventUserIdleSystemSleep` for **Messages** every ~31 s (106 times).
- The SpecWithCode blocker does release when work stops: 434 releases are logged since November 17. It is not stuck. It stays on because work keeps running: one hold lasted 10 h 39 min (November 23 12:54 to 23:34).

## What used the power

**Agent work on M5 during the display-off hour (04:51 to 05:48 UTC):** 1,363 turn items and 514 shell commands from 10 threads, taken from M5's own database.

| Thread | Items | Commands |
|---|---|---|
| ACP Registry usage stats and Effectiveness error | 349 | 143 |
| Personal assistants as one linked project | 262 | 137 |
| Board increment panel: Reports and Spec file | 105 | 36 |
| 1448 personal assistant link review | 91 | 38 |
| Adversarial review: Effectiveness crash fix | 76 | 30 |
| Adversarial review: Connect sign-in return page | 66 | 16 |
| ACP registry usage and Effectiveness review | 64 | 25 |
| Alerts follow the owner machine (1436) build | 59 | 22 |
| Google SSO page keeps loading after sign-in | 51 | 22 |
| Windows says Node.js missing for SpecWeave | 37 | 24 |

Commands in that hour included `tsc` 23 times, `vp test` 15, `typecheck` 3, `playwright` 4 and headless capture 6. They also included 26 `ci-wait` calls of about 9 minutes each. Those cost little CPU, but they keep a thread active and so keep the blocker on. 33 headless Chrome processes made captures between 22:34 and 01:12.

**Live snapshot now, on AC, not a battery figure:** total system draw 65 to 73 W. Three agent `tsc --noEmit` runs were going at once (395%, 198% and 200% CPU, up to 9.8 GB each). Over 60 s, the SpecWithCode renderer used 20 to 48% CPU while threads streamed, WindowServer 25 to 40% and the GPU 18 to 25%. Wispr Flow used about 20% CPU during the sample, while one of its helpers held an audio stream.

**Also seen:**

- Chrome turned a "Video Wake Lock" on and off 14 times. Some tab plays video.
- Three SpecWithCode updates ran on battery on November 18 (relaunches at 08:49 and 09:21, an update prepared at 11:03).
- `mediaanalysisd` has used 586 CPU-minutes in 12 days. That is new-Mac Photos analysis.

**Not the cause:** a battery fault, drain while asleep, an external display, High Power Mode, or heat. PS Remote Play was open and idle at 01:15. OBS and chiaki-ng don't appear in the power log for November 23 or 24.

## SpecWithCode design gaps

1. `apps/web/src/components/desktop/KeepAwakeWhileWorking.tsx`: the app holds the blocker when any thread on **any connected environment** is active. That includes remote machines such as M4, whose work doesn't need this laptop awake. This comes from reading the code, not from observation. Last night local threads were working anyway.
2. `apps/desktop/src/ipc/methods/keepAwake.ts`: calls `powerSaveBlocker("prevent-app-suspension")` without checking for battery. The app already reads `powerMonitor.isOnBatteryPower` (`apps/desktop/src/app/DesktopApp.ts:817`).
3. A thread waiting on `ci-wait` counts as working, so a cheap wait keeps the laptop awake just like a build does.

Side note, not tied to the drain: two provider turns have shown `running` since November 23 07:53 UTC (`specweave coordinator` and `Fable limit reset not recognized on M5`). That is worth a look in the open-gaps list.

## Proposed increment

**"Keep awake respects battery and counts only this machine's work"**

- AC-01: count only threads that run on this machine's own environment.
- AC-02: on battery, make the blocker a choice: Always, Only on power adapter, or Until battery is below N%. A notice shows when the Mac is held awake on battery. Pick the default together with the Handoff decision ("sleep off") and Away mode (1267, 1390).
- AC-03: on battery, offer to hand heavy verify, test and review threads to a plugged-in machine (M4), and defer app update relaunches.

## Fixes for the owner (none applied)

Nothing here is harmless and fully reversible without changing how the owner works, so nothing was changed.

1. Turn on Low Power Mode "Only on Battery" (System Settings > Battery). The CLI route needs sudo, so it was skipped.
2. When unplugged, turn off SpecWithCode Settings > "Keep awake while working", or move heavy threads to M4 first. Trade-off: local turns pause while the Mac sleeps.
3. Quit Wispr Flow when not dictating, and Messages if it isn't needed.
4. Close the Chrome tab that plays video.
5. On AC, display sleep and system sleep are set to Never. That doesn't affect the battery.

## Evidence

Folder: `/Users/anton/.specwithcode/m4/scratch/2026-11-24-battery/`

- `pmset-log.txt`, `charge-series.txt`
- `top-now.txt`, `cpu-60s.tsv`, `sysload-samples.txt`
- `renderer-samples.txt`, `ps-full.txt`
