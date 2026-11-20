# A thread's alert reaches its own machine when that machine is in use

Repo: `anton-abyzov/specwithcode` (checkout `repositories/anton-abyzov/specwithcode`). Code was read on `origin/main` `efc205f60`. `git diff v1.0.401 origin/main` is empty for `ThreadNotificationCoordinator.tsx`, `notificationTarget.ts`, `BackgroundPolicy.ts`, `backgroundActivityReporter.ts`, `actionMachine.tsx`, `threadNotifications.ts`, `notificationHistory.ts`, `projectAttention.ts` and `attentionOwner.ts`, so M4 (1.0.401) and M5 (1.0.404) ran the code read here.

## Problem

Anton, November 20, 2026, about 1:24 PM EST:

> "Strange that they see the notification only on M4, even though it's executed on M5, and this is what I am working on, so deeply investigate. There might be a problem identifying the machine for a thread."

The toast "Input needed on M5 · GTA 6 livestream kit" appeared in M4's window (`reports/screens/toast-on-m4.png`). M5, the machine that runs the thread and where he had to act (the thread's report starts its steps with "On M5:" and asks him to lock the iPhone next to that Mac), showed no popup.

The same day he added: "when I see a pop-up, like a notification message that something happened (for example, on an M5 machine), maybe it makes sense to put in a color around it (which is related to this machine), just to visualize where it happens."

## Findings

**1. The thread's machine is identified correctly.** "GTA 6 livestream kit" (`thread:delegated-task:command%3Amcp%3Afa43f133-3057-4a60-a8c7-bcc96542ad30%3Adelegate-task%3A870e7a6e-2fa6-4373-9c02-7e71b825bea5`) has `ownerMachineId` and `executionMachineId` `644195cc-3df8-418f-9708-3cd5ff059725` (M5) and `executionState: "running"`. It was never handed off or moved. The toast names M5, which is right: a toast names the machine only when it is not the window's own (`apps/web/src/studio/actionMachine.tsx:28-36`), so the window in the screenshot is M4's.

**2. The "Cursor limit reached · continued on Codex" line belongs to another thread.** It is the thread open behind the toast, "Instagram replies and posting schedule", which lives and runs on M4 (`4d73e481-1b03-4ee8-b4c1-87a448431538`). Its first run on Cursor failed at 18:16:22 UTC and it continued on Codex. It has nothing to do with the kit thread.

**3. Timeline (UTC, November 20).**

| Time | Event |
|---|---|
| 18:24:21.657 | Kit thread's run 28 completes on M5 with a "Blockers:" report. A reported blocker is an action (`reason: "message"`, `packages/client-runtime/src/state/projectAttention.ts:205-219`), and its alert title falls through to "Input needed" (`apps/web/src/components/ThreadNotificationCoordinator.tsx:589-609`). |
| 18:24:27.175 | The question in M4's Instagram thread is answered ("Post both replies"). The screenshot shows that thread with "Sent to the agent · 1:24 PM" in M4's window. No record names the app that sent the answer; if it was that window, M4 had input 6 s after the alert. |
| 18:25:26 | The screenshot reaches M5's coordinator. |
| 18:26:02 | The kit thread gets its reply ("...now I just locked it"). |

**4. Why M4 showed it.** M4's window was focused on another thread. A focused window toasts every alert of every machine it is connected to and never asks who the target is: the toast branch runs when `inApp` is true (`ThreadNotificationCoordinator.tsx:622`, `:693-738`), and the target is read only inside `if (!inApp)` (`:640-685`). That is 1278's design (its Scope lists focused-window toasts as out, and its D-08 says "Its toast always shows").

**5. Why M5 showed nothing.** M5's settings do not mute it: `notificationMode` is "off" and `inAppNotificationsEnabled` is false, but `inputNeededAlertsEnabled` is true, so a blocker still toasts or posts (`needsUser`, `:620`, `:693-695`, `:740-745`). That leaves three states of M5's window. The logs point at the first and cannot prove it (finding 6, `reports/m5-log-slice.md`):

- **Unfocused** (he was in OBS or at the phone, which is what the thread had asked for). M5's app asks its own server for the target (`:648`). The server elects the foreground app touched last (`apps/server/src/background/BackgroundPolicy.ts:234-236`), which was M4's. M5's app is then the owner but not the target, so it adds a dock badge and nothing else (`apps/web/src/notificationTarget.ts:96-104`). No popup, and no sound with the mode off. This is the likely state: M5's app made one policy read 0.34 s after the run completed, outside the periodic bursts, and with the mode off on M5 the only read an alert can cause is this one.
- **Focused with the kit thread open.** No toast is due, because he is looking at the thread (`:696-697`). Then M4's toast is the only thing wrong, and only by being redundant.
- **Focused on another thread.** A toast was due on M5. If none showed, the fault is in gating (dedupe in `notificationHistory.ts`, or the lead taking the question), and nothing in AC-01 to AC-04 would fix it. M5's app had one window, so window ownership is not it. Only AC-05's record can catch this state.

**6. Nothing records an alert's delivery.** Messages carry no client, the server keeps leases in memory only, and the traces record that `server.getBackgroundPolicy` was called but not its answer or what the app did with it. Which window was focused at 18:24:21 cannot be recovered, on either machine.

**7. The election measures "which app was touched last", not "which computer the person is at".** A lease is foreground when its window is visible and focused or touched in the last moments (`BackgroundPolicy.ts:135-137`). Working in another program on the thread's own machine does not count, so two computers on one desk lose to whichever SpecWithCode window had the last click. 1278's D-01 put the thread's own machine first ("the thread's owner machine when it is in use, otherwise the most recently active device"), but its AC-02 and AC-07, accepted with it, let the last-touched app win outright. The host power contract has the machine's own idle time (`HostPowerSnapshot.idleSeconds`, `locked`, `suspended`, `packages/contracts/src/background.ts:35-46`), and the desktop shell samples it (`apps/desktop/src/telemetry/DesktopTelemetryPublisher.ts:211-268`), but the server's own monitor starts it at `null` (`apps/server/src/background/HostPowerMonitor.ts:28`) and the election never reads it.

**8. A toast for another machine looks like every other toast.** It names the machine in that machine's colour (`ActionMachineName`, `ThreadNotificationCoordinator.tsx:612-615`), two letters wide. The card itself has no mark, while the message box of a chat on that machine wears a tinted border, a 3px leading edge and a halo (`.machine-composer[data-machine-color]`, `apps/web/src/index.css:2615-2620`).

So this is not a machine identity fault. The alert followed the last click, by design, and the design has no case for one person using two machines at once.

## Scope

In: the thread's own machine also shows the popup while that machine is in use, judged by the machine's own keyboard and pointer activity and not only by the app window; a record of every election and every delivery decision; the settings line; tests and the two-server proof; in-app toasts that name a machine wear that machine's colour.

Out: system notifications' look (the operating system draws them; they keep "on M5" in the text); hand off notices; who the target is and its order (1278 AC-02 stays); toasts in a focused window (1278 D-08 stays); sidebar counts and dock badges (1278 AC-11 to AC-16 stay); phone pushes, the relay and project notification levels; a per-device "always notify here" switch (1278 D-06 stays).

## Acceptance Criteria

- [ ] AC-01: `server.getBackgroundPolicy` adds optional `ownerInUse: boolean`. It is true when a live desktop or web lease has `hostEnvironmentId` equal to this server's machine and that machine is in use: the lease is foreground, or the machine's last keyboard or pointer input is at most 120 s old. The input age is taken as `idleSeconds` plus the age of the host power report, so a stale report can only make the machine look idle. A locked or suspended machine, a stale or unknown host power reading with no foreground lease, and a server with no such lease all give false. `notificationTarget` and its order are unchanged.
- [ ] AC-02: An unfocused app that is not the target posts the popup (and plays its sound, under its own settings) when its own machine serves the thread and the read says `ownerInUse: true`. In every other case it does what it does today. The target app is unaffected, so with both machines in use the alert shows on both, and with the thread's machine idle it shows on the target alone.
- [ ] AC-03: The incident, as a test: M4's app is foreground with the latest input, M5's app is unfocused, M5's own machine had input 20 s ago, and an M5 thread reports a blocker. M5 posts one OS notification and M4 keeps its toast. With M5's last input 10 minutes old, or M5 locked, M5 only badges, as today.
- [ ] AC-04: Older versions keep working. A server without `ownerInUse` leaves every app on today's behaviour. An older app ignores the field. Only the thread's own machine needs the new version for AC-02 to apply.
- [ ] AC-05: Every delivery decision is recorded where a later reader finds it: the app records machine, thread, alert kind, whether the window was focused, whether the thread was the open one, the target's client and reason, `ownerInUse`, and the outcome (toast, system notification, badge, nothing, and why). The server records each change of target or of `ownerInUse` with the reason and each lease's last-input age. Both survive trace sampling. Given the two records of one alert, a reader can say which app showed it and why the others did not, which was not possible for this incident.
- [ ] AC-06: Settings > Notifications reads "Shown on the device you are using. A thread's own computer also shows it while you are using that computer. Your other computers show a badge." in the eight phrase catalogs.
- [ ] AC-07: This amends 1278 AC-07's second line and AC-10's "exactly one": after a move to another computer, the thread's own machine also pops up until its last input is 120 s old. The rest of 1278 holds: one person on one machine gets exactly one popup; a fenced copy never alerts; an old server, a failed or timed-out read and a `null` target behave as before; the phone is unchanged. The two-server headless proof shows two OS-notification calls when both machines are in use, one when the thread's machine is idle, and its switch step expects the second popup to stop after 120 s.
- [ ] AC-08: An in-app toast that names a machine ("Input needed on M5") wears that machine's colour on the card: the border in the machine's edge tone, a 3px leading edge in the machine's colour and the faint halo, the same treatment as the message box of a chat on that machine, from the same tokens (`--machine`, `--machine-edge`). The colour is the one the machine menu and sidebar show for it on this device. Mockup: `reports/screens/toast-machine-colour-mockup.png`.
- [ ] AC-09: A toast for the window's own machine names no machine and stays as it is. The alert's kind keeps its own icon and icon colour (question, approval, failure), the name in the title stays, so the colour never stands alone, and the leading edge is on the right in right-to-left layouts.
- [ ] AC-10: The coloured card keeps 3:1 for the edge against the canvas in light and dark for all eight machine colours, and the title, description and button keep their contrast. Headless captures of a toast for each of two machines, in light and dark, are in `reports/screens/`.

## Approach

1. **Measure first.** Read what `HostPowerMonitor` holds for `idleSeconds` on macOS, Windows and Linux and how often it is refreshed (`apps/server/src/background/HostPowerMonitor.ts`, the desktop shell's reports from `apps/desktop/src/app/DesktopApp.ts` and `apps/desktop/src/telemetry/DesktopTelemetryPublisher.ts`). Several server sources set it to `null`. If the reading is missing or slower than about 30 s on a platform, the desktop shell reports it on the existing `server.reportHostPowerState` call; where no shell runs (a headless Linux server) AC-01 falls back to the foreground lease alone.
2. **Contract.** `packages/contracts/src/background.ts`: optional `ownerInUse` on `BackgroundPolicySnapshot`. No new reason literal, so an older app still decodes the snapshot.
3. **Server.** `apps/server/src/background/BackgroundPolicy.ts`: a pure `ownerMachineInUse({ leases, hostPower, selfEnvironmentId, now })` next to `electNotificationTarget`, and one service method that returns both. `apps/server/src/ws.ts` changes only in the `serverGetBackgroundPolicy` handler (`:2753-2759`); the file is over the 1,500-line limit already, so nothing else is added there.
4. **App.** `apps/web/src/notificationTarget.ts`: `NotificationTargetRead` carries `ownerInUse`, and `decideNotificationDelivery` returns "post" for the non-target app when `ownEnvironmentId === servingEnvironmentId` and `ownerInUse` is true. `ThreadNotificationCoordinator.tsx` needs no new branch for delivery; it gains the delivery record at each return of the `deliverNotificationOnce` callback.
5. **Record.** One named span or log line per decision in the app and per change on the server, exempt from sampling (`trace.sampling` drops most spans today), with no message text and no thread title.
6. **Toast colour.** `apps/web/src/components/ui/toast.tsx`: the toast data gains an optional `machineColor`; the card renders `data-machine-color` and a `machine-toast` class. `apps/web/src/index.css`: `.machine-toast[data-machine-color]` beside `.machine-composer`, with the right-to-left twin. `ThreadNotificationCoordinator.tsx` passes `actionMachine.color` in the `toastManager.add` call (`:699-737`).
7. **Copy and proof.** `NotificationSettings.tsx:103`, the eight catalogs under `apps/web/src/i18n/phrases/`, and `scripts/studio-logical-projects/notify-active.mjs` extended with the both-in-use and owner-idle cases.

Rejected:

- **The thread's own machine wins alone when in use.** After moving to another computer, alerts would keep landing on the one just left for up to two minutes, which is the lost alert 1278 was built to stop.
- **A focused window on another machine asks before toasting.** It adds up to 1.5 s to every toast and removes a notice the person is certain to see. M4's toast was correct and named the machine.
- **A longer foreground window for the app lease.** It still cannot see work done in another program on the same machine.

Risks:

- Two popups, and two sounds, when both machines were used within two minutes. This is the stated trade: a duplicate over a lost alert (1278 D-09).
- Whether one keyboard shared between two Macs (Universal Control) resets the idle time on both is unmeasured. T-01 measures it; if it resets both, AC-02 simply shows the alert on both, which is harmless.
- Idle time may not mean a person. An agent driving the machine (the kit thread was operating OBS and iPhone Mirroring on M5) may reset it with nobody there. T-01 measures that too. If agent input counts, the thread's own machine pops up while its agents work, which is a duplicate at worst.
- AC-03's "input 20 s ago" is an assumption about this incident. Whether M5 had input in the two minutes before 18:24:21 is unrecorded, so this fix is not proven to have changed that one alert.
- The cause of M5's silence is inferred for the unfocused state and unrecorded (finding 6). AC-05 ships first so the next report can be read from records.

## Decisions

### Asked
- none yet.

### Defaulted (change any before sw-do)
- D-02 "In use" for the thread's own machine means keyboard or pointer input on that computer within 120 s, in any program, with the screen unlocked (reversible).
- D-03 A focused window keeps toasting other machines' alerts with the machine named, as 1278 D-08 decided (reversible).
- D-05 The machine colour goes on toasts that name a machine, so colour means "this is on another computer". A toast for the window's own machine stays plain (reversible).
- D-06 The card reuses the message box's border, leading edge and halo, with no fill, so the alert kind's own colours stay readable (reversible).
- D-04 The delivery record holds ids, kinds and reasons only, no message text and no thread titles, and stays on the machine in its existing trace files (reversible).

### Open
- D-01 When two machines are both in use, where does a thread's popup show? It changes what Anton decided in 1278 (D-01 and AC-07 there), so it is his. Recommended: on both, the app touched last as today plus the thread's own machine. Alternatives: only the thread's own machine; or leave it, the last-touched app alone. AC-01 to AC-04 and AC-07 are written for the recommended answer and wait for it; AC-05 and AC-08 to AC-10 do not.
- Which state M5's window was in at 18:24:21 UTC (finding 5). Not recoverable; AC-03 covers the unfocused state, the focused-on-the-thread state needs no change, and the focused-elsewhere state would be a separate fault that AC-05's record is there to catch.

## Tasks

### T-01 Measure the machine idle reading per platform, under Universal Control and under agent-driven input, and record it
- AC: AC-01 | Files: .specweave/increments/1436-a-threads-alert-reaches-its-own-machine-when-that-machine-is-in-use/reports/host-idle-reading.md | Test: test -s .specweave/increments/1436-a-threads-alert-reaches-its-own-machine-when-that-machine-is-in-use/reports/host-idle-reading.md

### T-02 Record every election change and delivery decision
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/background/BackgroundPolicy.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/notificationDeliveryRecord.ts, repositories/anton-abyzov/specwithcode/apps/web/src/notificationDeliveryRecord.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/notificationDeliveryRecord.test.ts src/components/ThreadNotificationCoordinator.test.tsx

### T-03 Server says when its own machine is in use
- AC: AC-01, AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/background.ts, repositories/anton-abyzov/specwithcode/apps/server/src/background/BackgroundPolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/background/HostPowerMonitor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/background/NotificationTarget.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopApp.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/background/NotificationTarget.test.ts src/background/HostPowerMonitor.test.ts

### T-04 The thread's own machine posts while it is in use
- AC: AC-02, AC-03, AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/notificationTarget.ts, repositories/anton-abyzov/specwithcode/apps/web/src/notificationTarget.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.badge.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/notificationTarget.test.ts src/components/ThreadNotificationCoordinator.test.tsx src/components/ThreadNotificationCoordinator.badge.test.tsx

### T-05 Settings line in eight catalogs
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/NotificationSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/i18n

### T-06 Two-server proof: both in use, and the thread's machine idle
- AC: AC-03, AC-07 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-logical-projects/notify-active.mjs, .specweave/increments/1436-a-threads-alert-reaches-its-own-machine-when-that-machine-is-in-use/reports/notify-active-proof.md | Test: cd repositories/anton-abyzov/specwithcode && node scripts/studio-logical-projects/notify-active.mjs ~/.specwithcode/m4/scratch/1436-notify-active

### T-07 Toasts that name a machine wear its colour
- AC: AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ui/toast.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/index.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadNotificationCoordinator.test.tsx, .specweave/increments/1436-a-threads-alert-reaches-its-own-machine-when-that-machine-is-in-use/reports/screens/toast-machine-colour-after.png | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/ThreadNotificationCoordinator.test.tsx src/components/ui

### T-08 Check on M5 and M4 after release, verify and close
- AC: AC-02, AC-05, AC-08 | Files: .specweave/increments/1436-a-threads-alert-reaches-its-own-machine-when-that-machine-is-in-use/reports/real-machines.md | Test: specweave verify 1436-a-threads-alert-reaches-its-own-machine-when-that-machine-is-in-use
