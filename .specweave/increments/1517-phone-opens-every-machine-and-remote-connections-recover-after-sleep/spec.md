# Phone opens every machine and remote connections recover after sleep

## Problem

Anton, November 28, 2026: "from a mobile phone, I cannot switch the coordinator to any machines that should be available (for example, to a Linux machine), and similarly from an iPhone 16 ... all the troubles that I had connecting to, for example, a Linux machine or an M1 machine for the past week, because I was in another city, like from Boston to my local machine."

Evidence: `reports/evidence.md` (timeline November 20 to 28), `reports/1352-findings-status.md` and `reports/1352-code-check.md` (earlier connection findings re-checked on main `946325374`), `reports/phone-switcher-before.png`.

Switching from the phone:

1. Phone web app (headless at 430x932 against M5 1.0.458, paired with phone scopes): the project's machine menu lists m4, linux-mini and m1 greyed with "This window cannot open X". Its "Connect…" only opens Settings > Machines, which tells a phone "Quit and reopen SpecWithCode so it signs in with full access to this computer" (`OrchestratorSwitcher.tsx` `onAllowWorkers`). Fleet pairing needs `access:write` (`studioFleet.ts:57`), which a phone pairing never gets, and nothing on the row asks Connect for the machine.
2. iPhone app: the switcher ("Coordinator runs on") lists a machine only after the phone loaded that machine's threads once (`ShellSummaries.swift:95`, switcher shown when `members.count > 1`). A machine still waiting to approve the phone, or one whose tunnel is down, is missing rather than shown as waiting. Both iPhones report app 0.1.8 to the relay; 0.1.9 (53), with the approval code on every screen, has been on TestFlight since November 23.

Connection troubles while away (`reports/evidence.md` (b) and (c)):

3. M5 was locked out of m3 on November 28 (393 tries every 4 s): `"Open SpecWithCode on Anton's MacBook Pro and type this code"`. A device allowed on m3 can type that code, but the web pop-up shows only for the window's own machine (`DeviceApprovalPromptHost`, `usePrimaryEnvironmentId`), and the iPhone offers it only inside that machine's page.
4. After every wake of M5 nothing was reachable for 6 to 20 minutes. Waking is handled only as an update check (`DesktopApp.ts:737`); a window in the background keeps its retry wait, which grows to 300 s, or 600 s for a machine the relay calls offline, once 30 minutes pass since the last session (`supervisor.ts:210`).
5. The tunnel watchdog marks a connector connected at its first "Registered tunnel connection" and never again checks it (`ManagedEndpointRuntime.ts:316`). A cloudflared that keeps running with no edge connections is never restarted. No outage this week is proven to be this; it is the remaining undetected tunnel failure from 1352.

Other causes found, not code: M5 asleep in the bag (confirmed, `pmset`), m3 offline most nights (likely asleep), win down November 26 to 27 (unknown), fleet restarts on November 28 (confirmed).

## Scope

In: the web machine menu's Connect and its wording on a phone; allowing a waiting device from any machine a window is allowed on; waking connections after sleep; a two-minute retry cap for machines seen in the last week; a cloudflared edge-loss restart; the iPhone switcher listing linked machines it has not reached; an iPhone build.

Out: skipping device codes between the owner's machines (D-01 kept codes); keeping Macs awake (1457 owns keep-awake); MCP session fallback and handoff self-pause (1352 findings, recorded in `reports/1352-findings-status.md` for a follow-up); the relay reaper setting.

## Acceptance Criteria

- [ ] AC-01: In the web machine menu, "Connect…" on a machine this window cannot open asks SpecWithCode Connect for that machine directly when the window is signed in to Connect and the machine is on the account; otherwise it opens Settings > Machines as today.
- [ ] AC-02: A row the window cannot open says why in words a phone can act on: connecting, waiting for approval on that machine, or sign in to SpecWithCode Connect, instead of only "This window cannot open X".
- [ ] AC-03: A device waiting for approval on machine X shows its pop-up in every window that is connected to X and allowed to approve there, not only in X's own app; the pop-up names X.
- [ ] AC-04: The waiting device's code card says the code can be typed on X or on any phone or computer X already allows.
- [ ] AC-05: When the computer wakes from sleep or is unlocked, every desktop window probes its connections and runs pending retries at once, without focus.
- [ ] AC-06: A machine this device had a session with in the last 7 days is retried at least every 2 minutes while unreachable; older or never-seen machines keep today's ceilings.
- [ ] AC-07: When cloudflared reports every edge connection lost for 2 minutes after it had registered one, the server restarts the connector and asks the relay to check the tunnel.
- [ ] AC-08: The iPhone switcher lists every machine a linked project names, including ones not reached yet, with their state (waiting for approval, offline, connecting), and the home screen says when a machine the phone is allowed on has a device waiting for approval.
- [ ] AC-09: The fixes ship in an app release and an iPhone TestFlight build, with a screenshot of the phone's machine menu opening linux-mini.

## Approach

Web (`apps/web`): the switcher row action calls `requestAccountMachineConnect`; when it returns false it navigates as today. Row reason comes from `accountAutoConnectStates()` and the connection's `deviceApprovalCode`. The device pop-up host renders one `DeviceApprovalPromptForMachine` per connected machine whose device list says `canApprove`, reusing the 30 s notice poll for machines other than the window's own.

Desktop: `powerMonitor` resume and unlock broadcast `desktop:system-resume` to every window (`systemResume.ts`); the web wakeups stream maps it to `application-active-probe`, which probes live sessions quickly and resets retry backoff.

Client runtime: `KNOWN_MACHINE_RETRY_MAX_DELAY_MS = 120_000` for `sinceLastConnectedMs < 7 days`.

Server: track live edge connections by cloudflared's `connIndex` (registered vs terminated, unregistered, lost, retrying); when the count falls to zero after a registration and stays there 2 minutes, kill the connector (the supervisor restarts it with its backoff) and offer recovery.

iPhone: `ShellSummaries` adds a member per machine named in `logicalProject.members` that has no snapshot, flagged not reached; the switcher row shows the machine's state. Built and screenshotted on m4 (iOS Simulator), TestFlight through `apps/ios/Tools/release.sh`.

Rejected: sharing approvals between machines (D-01); letting phone pairings mint fleet pairings (`allowConnectFrom`), an access change.

## Decisions

### Asked
- D-01 Should the owner's machines skip the device code for each other when one gives the other full access? → "Keep codes, allow from phone": no rule change; any device a machine already allows types the waiting code remotely, and the phone and pop-up say so (Anton, November 28, 2026).
### Defaulted (change any before sw-do)
- D-02 Retry cap for a machine seen in the last week → 2 minutes (reversible constant).
- D-03 Edge-loss restart after 2 minutes with no edge connection (reversible constant).
- D-04 Wake from sleep probes sessions quickly rather than replacing them, so a healthy local session is kept.
### Open
- none

## Tasks

### T-01 Web machine menu: Connect asks Connect, rows say why
- AC: AC-01, AC-02 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.test.ts] | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/studio/OrchestratorSwitcher.test.tsx src/studio/machineRowState.test.ts`

### T-02 Allow a waiting device from any machine this window is allowed on
- AC: AC-03, AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx] | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/devices`

### T-03 Waking the computer wakes every window's connections
- AC: AC-05 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/window/systemResume.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/systemResume.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopApp.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/apps/web/src/connection/platform.ts] | Test: `cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/window/systemResume.test.ts`

### T-04 Two-minute retries for machines seen in the last week
- AC: AC-06 | Files: [repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.test.ts] | Test: `cd repositories/anton-abyzov/specwithcode/packages/client-runtime && npx vp test run src/connection/supervisor.test.ts`

### T-05 Restart cloudflared after it loses every edge connection
- AC: AC-07 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/cloud/ManagedEndpointRuntime.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/edgeConnections.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/edgeConnections.test.ts] | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/cloud/edgeConnections.test.ts src/cloud/ManagedEndpointRuntime.test.ts`

### T-06 iPhone switcher lists machines not reached yet; waiting devices on the home screen
- AC: AC-08 | Files: [repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/OrchestratorSwitcher.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ShellSummariesTests.swift] | Test: `cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test --filter ShellSummariesTests`

### T-07 Release, TestFlight and the phone screenshot
- AC: AC-09 | Files: [.specweave/increments/1517-phone-opens-every-machine-and-remote-connections-recover-after-sleep/reports/report.md] | Test: `test -s .specweave/increments/1517-phone-opens-every-machine-and-remote-connections-recover-after-sleep/reports/report.md`
