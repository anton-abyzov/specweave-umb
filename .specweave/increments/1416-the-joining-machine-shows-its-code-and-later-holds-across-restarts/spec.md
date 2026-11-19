# The joining machine shows its code, and Later holds across restarts

## Problem

Two reports from Anton on November 18, 2026, both about device approval (1327, 1406).

**1. The joining Mac shows no code (11:45 AM).** On m3 (1.0.357) Anton opened "Set up SpecWithCode Connect", pressed Add next to Anton's MacBook M4MAX, and m4 at once showed "A new device wants to use Anton's MacBook M4MAX … Anton's MacBook Pro, ID GGXQ … Type the code shown on Anton's MacBook Pro". m3 showed no code. His photo (`reports/m3-setup-dialog.jpg`) shows why: the m4 row in the setup dialog reads "Reconnecting…", and the card with the code ("Open SpecWithCode on Anton's MacBook M4MAX and type this code", with Copy) sits at the top of the window, blurred under the dialog's backdrop.

- The machine rows (`CloudEnvironmentConnectRows` in `apps/web/src/components/cloud/CloudEnvironmentConnectList.tsx`) present a waiting machine through `presentSavedCloudEnvironmentConnection`, which knows only the phases, so a machine that answered "waiting for approval, here is your code" reads "Reconnecting…". The same rows are used in Settings > Connections and in first run's connection step.
- The floating card (`DeviceWaitingForApprovalHost`, `fixed … z-50`) shares the dialog's layer (`z-50`), and the dialog's backdrop covers it.

**2. The pop-up comes back after every restart (11:39 AM).** m4 shows "A new device wants to use Anton's MacBook M4MAX … Anton's MacBook Pro M1Max, ID XUNP, macOS, SpecWithCode 1.0.344, asked at 11:32 AM". Anton: "I keep seeing this message when I restart my SpecWithCode. It's actually happening on M4 and M5."

What the evidence shows:

- An approval survives a restart. It is kept in `connect-devices.json` under the device's proof key (`jkt:<thumbprint>`) and read at every start (`ConnectDeviceTrust.ts`, `load`, `check`). No start rewrites it once the `connect-devices.migrated` marker exists.
- m1's key did not change. The same key (`…WYMnpE`, ID XUNP) was in M5's allowed list at 10:47 AM and 2:11 PM UTC and asked m4 at 4:32 PM UTC. A window's key is loaded or made once and kept in that window's storage (`managedRelayLayer.ts`); the desktop window's origin (`studio://app`) has not changed since 1.0.5, and nothing in the app clears it.
- m4 ran 1.0.338 until today. Its first start on 1.0.357 (11:09 AM) wrote the list and kept only the two devices connected at that moment (a Linux computer and one Mac, "the update"). m1 was not connected then, so for m4 it is a new device. m4 has never had m1 in its list.
- m1 asks every few seconds without anyone at m1 acting: m4 is saved in m1's app, so its window keeps connecting.
- Later is held only in the window's memory (`ConnectDeviceHosts.tsx`, `useState`). Any restart or reload of m4's app brings the pop-up back while m1 keeps asking, and a restart of m4's server gives m1 a new code.
- M5: unreachable while this was written, so whether M5 asked again for a device it already allows is not verified. Read in T-08.

Where the code shows on the asking Mac today: the card at the top of its SpecWithCode window ("Open SpecWithCode on {machine} and type this code"). On 1.0.344 (m1) it is that card alone.

## Scope

In: the machine rows of the Connect lists show a waiting machine's code, this device's ID and the machine; the floating card stays readable over dialogs, and comes back whenever a row's code is out of view or covered (PR #622); Later is remembered on the approving machine across restarts; restart tests on the server; checks on real Macs after release.

Out: who may approve, what a code approves, sharing an approval between machines (D-01), the snapshot the first start takes, the iPhone waiting screen (1408), the relay.

Lanes. `[label]` changes only what is shown or which card is open and ships after review and green CI. `[access]` changes who gets access and waits for Anton's acceptance. Every AC below is `[label]`; D-01 would be `[access]` and is not built here.

## Acceptance Criteria

- [ ] AC-01 [label]: In every list of machine rows (Set up SpecWithCode Connect, Settings > Connections, first run's connection step), a machine that is waiting to approve this device reads "Waiting for approval" in its row and button, never "Reconnecting…", and shows under the row the code to type, the machine's name ("Open SpecWithCode on {machine} and type this code:"), a Copy button and this device's ID ("This device's ID is {id}. The machine shows the same ID next to it."), the same ID the approving machine shows. The code updates when the machine gives a new one. The checkbox form of the list shows the same code block under its row.
- [ ] AC-02 [label]: The floating code card is drawn above any open dialog and its backdrop, so its code is readable while a dialog is open. While a row from AC-01 shows a machine's code, the floating card leaves that machine out, as the join card already does.
- [ ] AC-03 [label]: A machine that turned this device away, or has too many devices waiting, says so in its row in its own words, and no code block shows.
- [ ] AC-04 [label]: On the approving machine, Later is remembered across restarts and reloads: it is kept per machine in this window's storage by the device reference each request carries (by request ID when the machine sends none), so the pop-up does not come back for a device the owner put off. It comes back only when a device that is not in that list asks. The device stays listed as waiting under Settings > Machines with its code box. Each entry is kept 30 days from the last Later that set it, at most 100 per machine (the oldest go first); expired entries of other machines are dropped on the next Later. A storage that cannot be read or saved falls back to memory for the session. Later never allows, denies or removes anything.
- [ ] AC-05 [label]: Server tests prove the restart path without changing it: an approved device is still allowed after a restart (a new service over the same file) and asks for nothing; a device the update kept is still allowed after a later restart; a later start with the marker present never takes a new snapshot; a waiting device keeps its request across a restart with a new code, and the old code no longer allows it.
- [ ] AC-06 [label]: Every new string goes through the translation function with entries for the eight shipped languages. (Built with no new strings: "Waiting for approval" and the code block's lines already have entries in all eight catalogs.)
- [ ] AC-07 [label]: Checked after release on two real Macs: the joining Mac's setup dialog shows its code, its ID and the machine, and the approving Mac shows the same ID; screenshots of both. Typing the code on the approving Mac is Anton's step, or done with his explicit yes. After a real restart of the approving app, a device put off with Later does not bring the pop-up back.
  - Accepted by Anton on November 19, 2026 on m4's records (`reports/real-join-m3-m4.md`): m3 allowed once on m4 by its typed code and connecting since. He skipped the screenshots and the live Later-then-restart check; Later across restarts rests on the Later store tests and the headless fixture.

## Approach

1. `apps/web/src/components/cloud/CloudEnvironmentConnectList.tsx`: read `savedEnvironment.connection.deviceApprovalCode`; when set, the row's status and button read "Waiting for approval" and an `InlineDeviceApprovalCode` (from `inlineApprovalCode.tsx`, which already shows the ID and registers the machine so the floating card skips it) renders under the row, in both the button and the checkbox forms. Denied and full come through as the connection's error text; a test pins that it shows and no code block does.
2. `apps/web/src/components/devices/ConnectDeviceHosts.tsx`: the floating card's layer goes above the dialog layer (`z-[70]`, above the dialog's `z-50`/`z-[60]`); pointer events stay on the card only.
3. Later: a small store (`apps/web/src/components/devices/laterStore.ts`) keeps `{ key, at }` per environment in `localStorage` under one key, read when the machine changes and written on Later; `DeviceApprovalPromptHost` reads it instead of `useState`. A storage that cannot be read or written falls back to memory, as today.
4. `apps/server/src/fleet/ConnectDeviceTrust.test.ts`: the restart tests of AC-05, using a second service over the same test home.
5. Translations in the eight catalogs; the device-approval fixture (`apps/web/tests/device-approval`) gets a setup-dialog scene with a waiting row and a scene with the floating card over an open dialog.

Rejected: moving the floating card into every dialog (each dialog would need to know about approval); a toast (it leaves before the owner reads the code); persisting Later on the server (it is one window's choice and changes nothing on the machine).

Risks: an inline code mounted but scrolled out of view hides the floating card for that machine; the setup dialog is short, so the row is in view when it is open. A Later entry kept for 30 days hides a device that keeps asking; it stays listed under Settings > Machines and the next new device brings the pop-up back with every waiting device listed.

## Decisions

### Asked
- D-01 Should an approval on one of Anton's machines count on his other machines (so m1, allowed on M5, would not ask m4)? → No, each Mac approves once (Anton, November 18, 2026). Each machine keeps its own list; nothing is built for sharing.
### Defaulted (change any before sw-do)
- D-02 Later is kept for 30 days from the last Later, at most 100 per machine; no prune on allow, since an allowed device no longer asks → default (reversible).
### Open
- none

## Tasks

### T-01 Waiting machine rows show the code, the machine and this device's ID
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/cloud/CloudEnvironmentConnectList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/cloud/CloudEnvironmentConnectList.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/cloud/cloudEnvironmentConnectionPresentation.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/cloud/cloudEnvironmentConnectionPresentation.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/cloud

### T-02 The floating code card stays above dialogs
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/devices

### T-03 Later is remembered across restarts
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/laterStore.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/laterStore.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/connectDevices.logic.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/devices src/studio/connectDevices

### T-04 Restart tests on the server
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/ConnectDeviceTrust.test.ts

### T-05 Translations and fixture scenes
- AC: AC-01, AC-02, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/, repositories/anton-abyzov/specwithcode/apps/web/tests/device-approval/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/i18n && node tests/device-approval/verify.mjs

### T-06 Review, merge and release
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: .specweave/increments/1416-the-joining-machine-shows-its-code-and-later-holds-across-restarts/reports/ | Test: Muse Wonderful SHIP on the exact head, green CI, then cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released <merge commit>

### T-07 Check on real Macs after release
- AC: AC-07 | Files: .specweave/increments/1416-the-joining-machine-shows-its-code-and-later-holds-across-restarts/reports/ | Test: screenshots of the joining and approving Macs; restart of the approving app with a device put off

### T-08 Read M5 after its restarts
- AC: AC-05 | Files: .specweave/increments/1416-the-joining-machine-shows-its-code-and-later-holds-across-restarts/reports/ | Test: M5's connect-devices.json and today's server log read by a read-only worker

### T-09 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1416-the-joining-machine-shows-its-code-and-later-holds-across-restarts/ | Test: specweave verify 1416

## Review

Reviewer: Muse Wonderful, `muse-wonder-full-1.0`, effort xhigh, full access, named by Anton for device authorization. It reviews the exact pull request head and confirms that no change alters who gets access.
