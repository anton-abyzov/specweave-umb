# Device approval with several devices: the dialog stays open after Allow and devices look alike

## Problem

Anton, November 18, 2026, on m1 (1.0.343 or newer): "the pop-up stays even if it was successful, which is weird ... that's all still weird when there are multiple devices." Screenshot: the toast "iPhone can now use Anton's MacBook Pro M1Max" over an open "A new device wants to use Anton's MacBook Pro M1Max" dialog with an empty code box.

What happened (device approval is 1327, shipped in 1.0.343):

- Two iPhones on the same Connect account asked m1 within about a minute (M5 logged their token calls at 08:27:25Z and 08:28:08Z). Both call themselves "iPhone", so both requests read "iPhone is asking ... iOS · SpecWithCode · Asked at 3:28 AM".
- The dialog shows the first waiting request (`ConnectDeviceHosts.tsx`, `snapshot.pending` first entry), but the server matches a typed code against every waiting request (`ConnectDeviceTrust.ts`, `approve`). Anton typed the iPhone 16 Pro's code, that phone was approved, and the dialog went on showing the other phone's request, which looks the same. The footer read "Deny turns it away for a day", so one request was left of two.
- It is not a missing dismiss and not a stale card: the dialog closes when nothing waits.

Evidence from M5 (1.0.349): its list holds two different iPhone keys, one allowed since the update ("An iPhone", `jkt:…4LRcG8`) and one that asked at 08:27:25Z ("iPhone", `jkt:…z3tKzo`). The 08:28:08Z token call created no request there, so that phone was the one M5 already allows. A phone keeps one key: it lives in the Keychain and sign-out does not reset it (`Dpop.swift`). m1's own list could not be read (its project copy is not linked to this project); the conclusion for m1 rests on the screenshot and the code.

What is wrong, beyond the confusing moment:

1. Nothing in the dialog says the approved device was a different one from the one shown.
2. Devices of one model are indistinguishable everywhere: the dialog, Settings > Machines and the allowed list. The phone sends only its system name, which is "iPhone" for every iPhone (`DeviceLabel.swift`).
3. Deny acts on the request the dialog shows. After approving phone B, Deny on the identical card turns phone A away for a day and ends its sessions.
4. Settings > Machines has a code box under every waiting row, and any box approves any device.
5. A waiting request expires after 10 minutes and the device's next try gets a new request and a new code, so Later hides the dialog for 10 minutes at most.
6. A device waiting on several machines shows one card per machine, and never says which device it is.

## Scope

In: the approval dialog and the Settings > Machines device list on desktop and web; a short device ID derived from the device's key, shown on the machine and on the device; a default iPhone name that carries the model; the waiting card on a web or desktop window; the same facts handed to the iPhone waiting screen, whose layout the thread "Mobile app disconnects often" owns (branch `fix/ios-approval-wait-loop`).

Out: who may approve, what a code approves, how long a request or a code lives, the per-machine lists (approving on m1 never clears M5), the relay, notices to other devices. The iPhone reload and disconnect loop and the waiting screen's layout belong to "Mobile app disconnects often".

Lanes. Every AC is tagged. `[label]` changes only what is shown or which card is open, and ships after review and green CI. `[access]` changes who gets access or for how long, and waits for Anton's acceptance. This increment's first pull request holds `[label]` ACs only; the reviewer confirms the split.

## Acceptance Criteria

- [ ] AC-01 [label]: With two or more devices waiting, the dialog on the machine lists every one of them in one view, each with its name, system, app, the time it asked and its short ID, and has one code box labelled "Type the code shown on the device you want to allow". It never shows one request while approving another unseen.
- [ ] AC-02 [label]: After a successful Allow while others still wait, the dialog names the device it allowed ("Allowed {device} · ID {id}") in a line that stays until the dialog closes, removes that device from the waiting list, clears the code box and says how many are still waiting. When nothing waits it closes by itself. The toast keeps naming the device and now carries its ID.
- [ ] AC-03 [label]: Deny belongs to a row and names that row's device and ID in its label; no control in the dialog acts on a device the owner cannot tell from the others. Later hides the dialog until a device that was not in the list asks, also after a hidden request expired and the same device asked again. Later only hides: the device stays listed in Settings > Machines and gains nothing.
- [ ] AC-04 [label]: Every waiting request and every allowed device carries a short ID: four characters derived from the device's key by the server, never taken from what the device says. A device with its own key (every Connect device) gets the same ID on every machine; a hub-linked phone without a key gets one per machine and cannot show it itself. One shared function computes it for the server and the web app, and the server, web and iPhone test suites assert the same fixed key and ID. Two devices with the same name are told apart by it everywhere a device is named: the dialog, Settings > Machines, the Remove confirmation and the toast.
- [ ] AC-05 [label]: Settings > Machines lists waiting devices apart from allowed ones under their own headings, with one code box for the waiting group, a Deny per waiting row, and "Allowed" rows that show name, system, app, short ID and who approved it when.
- [ ] AC-06 [label]: A device that waits shows its own ID ("This device's ID is {id}. The machine shows the same ID next to it.") and one list of every machine it waits on with that machine's code, on web and desktop windows. A machine leaves the list as soon as it lets the device in; nothing closes a card for a machine that has not approved.
- [ ] AC-07 [label]: A new iPhone build names itself by model when the system name is only "iPhone" (for example "iPhone 16 Pro" or "iPhone Duo", and "iPhone (iPhone99,1)" for a model the app does not know), and a name set in the phone's settings still wins. It can compute its own short ID, equal to the one machines show for it. Showing the phone's ID and one list of machine and code on the iPhone waiting screen is owned by the increment of the thread "Mobile app disconnects often" (branch `fix/ios-approval-wait-loop`), which redesigns that screen; this increment delivers the helper and the requirement, and T-08 records whether a phone build shows them.
- [ ] AC-08 [label]: The short ID, the name and the model are hints. No code path uses them to match, merge, approve, deny or remove anything: approval stays the typed six-character code, and the dialog keeps saying so. The one use beyond display is Later (AC-03), which only hides a dialog. A test proves a device that names itself like an allowed one, or whose ID collides, gets nothing without its own code.
- [ ] AC-09 [label]: An older machine's list (no short ID) and an older device (no model name) still render: names fall back to today's, the ID is left out, and `connect-devices.json` written by 1.0.343 to 1.0.349 loads unchanged. The file format does not change.
- [ ] AC-10 [label]: Every new string goes through the translation function with entries for the eight shipped languages, and the texts quoted here match the built ones.
- [ ] AC-11 [label]: Checked on real machines after release: on M5 and on m4 once it runs a build with device approval, and on m1 and linux-mini if agents can reach them. The live check reads each machine's device list and shows that devices with the same name carry different IDs. The two-phones-waiting case is proven by the tests of AC-01 and AC-02 and the browser scene, not staged live: staging it would mean removing one of Anton's allowed devices or signing a phone in again.

Deferred, each `[access]`, not built here without Anton's acceptance (see Decisions): keeping a waiting device's code when its request expires and it asks again; refreshing an allowed device's stored name from its later sessions; one approval covering the same device on other machines.

## Approach

1. Server, display only (`apps/server/src/fleet/connectDeviceNames.ts`, `ConnectDeviceTrust.ts`, `packages/contracts/src/connectDevices.ts`): `deviceShortId` lives in `packages/shared/src/deviceShortId.ts`: the thumbprint is already a SHA-256, so its first four bytes each pick one character of the code alphabet (`23456789ABCDEFGHJKMNPQRSTUVWXYZ`), with no second hash and nothing async. A hub-linked phone without a key gets the SHA-256 of its link key on the server first. Added as optional `shortId` on `ConnectDeviceRequest` and `ConnectDevice` when the snapshot is built and on the approve answer in `connectDevicesHttp.ts`. Older windows (1.0.338 to 1.0.349 are live) drop the unknown key when they decode, checked against effect 4.0.1. Nothing is stored: `StoreFile` is untouched, so no file can turn "damaged". `approve`, `deny`, `remove` and `ensureWaiting` are not edited.
2. Web logic (`apps/web/src/studio/connectDevices.logic.ts`): `connectDeviceTitle` (name plus "· ID XXXX"), details with the ID last, a `laterKey` per device (kind plus short ID, else the request id), and the client-side `deviceShortIdOfThumbprint` used by the waiting card. Pure functions with unit tests.
3. Dialog (`ConnectDeviceViews.tsx`, `ConnectDeviceHosts.tsx`): `DeviceApprovalPrompt` takes the waiting list, not one request. Rows with per-row Deny, one `CodeForm`, an "Allowed" line fed by the approve result, the count of those still waiting, the existing provenance sentence kept. The host keeps the approved devices of this dialog session in state and drops them when the dialog closes.
4. Settings list (`ConnectDeviceViews.tsx`): headings "Waiting for approval" and "Allowed", one code box for the group, IDs in rows and in the Remove confirmation.
5. Waiting device (`inlineApprovalCode.tsx`, `ConnectDeviceHosts.tsx`): one card with the device line and a row per machine; the inline code in the join card and first run gets the device line.
6. iPhone (`apps/ios/App/DeviceLabel.swift`, new `SWCTransport/DeviceShortID.swift`, tests): model name from the table `LiveEngine.modelName` already keeps (its `hardwareIdentifier` becomes public in `LiveEngine+Push.swift`), with the raw identifier as fallback; the short ID helper. No edits to `MachineRecovery.swift`, `MachineViews.swift`, `RootView.swift`, `ChatView.swift`, `MachineConnection.swift` or `LiveEngine.swift`, which the other thread is changing; it gets the helper and the AC-06 wording.
7. Tests: server unit tests for the ID and for AC-08; web unit tests for the logic and both views, including two waiting "iPhone" requests where the second one's code is typed; Swift tests for the name and the ID. The browser fixture `apps/web/tests/device-approval` is not run by CI and its assertions predate the current dialog text, so it is brought up to date and used for screenshots only. Existing `data-device-*` attributes and the sentence in `DeviceApprovalCode` stay as they are: the join card and first run render it. Heavy runs go through `specweave-studio checks run`.

Why a key-derived ID and not a phone-sent one: it works today for phones on the current build and for desktops, and a device cannot pick it. It can still be ground (four characters, about 20 bits), so it is a hint beside the code, never a proof (AC-08).

Rejected: closing the dialog after any successful Allow (hides a second device that is really waiting); matching the typed code only against the shown request (the owner would have to guess which identical card belongs to which phone); a model field in the token exchange (a new wire field for something the name already carries).

Risks: the dialog now lists devices, which 1327 avoided for click-to-approve designs (B-04). Here a row has no Allow, only the typed code allows, and the caps of 3 waiting per account and 20 overall bound the list. `ConnectDeviceViews.tsx` is 443 lines and stays under 1,500.

## Decisions

### Asked
- D-01 Machine access for checks on m1 and linux-mini → "I don't know, test yourself, work fully autonomously, maybe they can" (Anton, November 18, 2026). Agents retry the machines at verify time and report which ones they reached.

### Defaulted (change any before sw-do)
- D-02 One dialog that lists every waiting device, one code box → default. Reversible in the web app alone.
- D-03 Short ID: four characters from the key, same alphabet as codes, shown as "ID XXXX" → default.
- D-04 iPhone default name carries the model; no new wire field → default.
- D-05 The first pull request holds `[label]` ACs only and ships after Muse Wonderful's review and green CI, as the task allows for dismiss and labelling fixes → default.

### Open
- D-06 [access] Keep a waiting device's code and request when the 10 minutes run out and it is still asking, so the code on the phone does not change while the owner walks to the machine. Recommended: yes, with a 30 minute ceiling. The code also changes when the machine's server restarts, because the readable code lives only in memory (the file keeps its hash); keeping it across a restart means storing it, so it belongs to the same decision. Recommended: no, a restart is rare and a stored code is one more secret on disk. Needs Anton.
- D-07 [access] Refresh an allowed device's stored name from its later sessions, so phones allowed before this release show their model too. Recommended: yes; the key-derived ID stays fixed. Needs Anton.
- D-08 [access] One approval covering the same device on the owner's other machines. Recommended: no; 1327 keeps one list per machine.

## Review

Reviewer: Muse Wonderful, `muse-wonder-full-1.0`, effort xhigh, full access, named by the owner for device authorization. It reviews the exact pull request head and confirms that no `[label]` change alters who gets access. Any `[access]` change waits for Anton's acceptance before release.

## Tasks

### T-01 Short ID on the server and in the contract
- AC: AC-04, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/connectDeviceNames.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/connectDeviceNames.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/connectDevicesHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/connectDevicesHttp.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/connectDevices.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/deviceShortId.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/deviceShortId.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/connectDeviceNames src/fleet/ConnectDeviceTrust src/auth/connectDevicesHttp

### T-02 One dialog for every waiting device
- AC: AC-01, AC-02, AC-03, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/connectDevices.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/devices src/studio/connectDevices

### T-03 Settings list: waiting and allowed apart, one code box
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ConnectDevicesSection.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings/ConnectDevicesSection

### T-04 The waiting device says which device it is and lists machine codes
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/inlineApprovalCode.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ownDeviceId.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/devices

### T-05 iPhone names itself by model and knows its short ID
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/ios/App/DeviceLabel.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCTransport/DeviceShortID.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Push.swift, repositories/anton-abyzov/specwithcode/apps/ios/App/Tests/AppShellTests.swift | Test: cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test --filter DeviceShortID

### T-06 Translations and the two-phone browser scene
- AC: AC-01, AC-02, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/, repositories/anton-abyzov/specwithcode/apps/web/tests/device-approval/, repositories/anton-abyzov/specwithcode/apps/web/tests/team-rules/mocks.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/i18n; screenshots: npx vp build --config tests/device-approval/vite.config.ts && STUDIO_PLAYWRIGHT_MODULE=<installed playwright entry> node tests/device-approval/verify.mjs

### T-07 Review, merge and release the label lane
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10 | Files: .specweave/increments/1406-device-approval-with-several-devices/reports/ | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released <merge commit>

### T-08 Check on the machines and the phones
- AC: AC-11 | Files: .specweave/increments/1406-device-approval-with-several-devices/reports/ | Test: read the installed version and the device list on each reachable machine; screenshots of two waiting phones

### T-09 Verify and close 1406
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: .specweave/increments/1406-device-approval-with-several-devices/ | Test: specweave verify 1406
