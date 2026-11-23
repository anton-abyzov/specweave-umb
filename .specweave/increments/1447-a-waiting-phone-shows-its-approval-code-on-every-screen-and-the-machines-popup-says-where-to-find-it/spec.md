# A waiting phone shows its approval code on every screen, and the machine's popup says where to find it

Repo: `anton-abyzov/specwithcode` (checkout `repositories/anton-abyzov/specwithcode`). Code was read on `origin/main` `1c78231e4` (November 23, 2026), not on the checked-out branch. Plan only: nothing is built. This is an auth area, so building waits for Anton's approval (AGENTS.md).

## Problem

Anton, November 23, 2026, with a capture of the popup on M1 (`reports/popup-today-m1.png`):

> "On the M1 and Linux machine, I keep seeing this pop up, but on the iPhone itself, I don't see where this code is. I think maybe we need to improve the UI/UX."

The popup reads "A new device wants to use Anton's MacBook Pro M1Max", from iPhone Duo (ID BJ96, asked at 1:36 AM), and asks him to "Type the code shown on iPhone Duo". He could not find a code on the phone, so the request could not be finished on either machine.

## Findings

**1. The phone shows the code in two places only, both tied to the waiting machine.** A chat or project that lives on the waiting machine shows "Allow this phone on {machine}" with the code (`apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift:355`, `:384`), or a banner "Waiting for approval. Type {code} on {machine}." once the chat has loaded (`:1121`). The machine's own page (menu, then the machine row reading "Waiting for approval") shows it in a notice (`apps/ios/SWCKit/Sources/SWCFeatures/Machines/MachineViews.swift:234`, text in `apps/ios/SWCKit/Sources/SWCSync/MachineRecovery.swift:35`). The home screen says only "Some machines are offline" (`apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift:273`). A chat on a machine that already allows the phone (M5, m4) shows nothing. No notification is sent.

**2. The last numbered iPhone build has no code screen at all.** iPhone 0.1.8 (46) is commit `555f28bd9` (November 17, 2026). The code view arrived after it: PR #541 `d7e00ad6f` (November 17) and 1408 (November 18), and `d7e00ad6f` is not an ancestor of `555f28bd9`. No version bump followed. A phone on 0.1.8 (46) keeps asking and can never show a code. Which build iPhone Duo runs was not checked: the popup shows "iOS · SpecWithCode" with no version, because the phone sends none.

**3. The phone asked both machines in the same minute, and its key is stable.** linux-mini's device list (`/srv/specwithcode/minisforum/userdata/connect-devices.json`, read at 1:49 AM EST by a read-only thread there) holds one waiting request for "iPhone Duo", key `jkt:ZhBFQoMPd8…`, created at 1:36:40 AM EST, the minute of M1's popup. M5's list holds the same key as "An iPhone", kept by the 1327 update on November 17, which is why M5 never asks. So this is one phone with one unchanged key, asking each machine that has not allowed it. That is the per-machine rule working as decided (1416 D-01).

**4. The request never ends by itself while the phone's app is open.** The phone asks again every 4 seconds (`apps/ios/SWCKit/Sources/SWCTransport/MachineConnection.swift:77`). Each ask keeps the request alive (`ensureWaiting`, `apps/server/src/fleet/ConnectDeviceTrust.ts:750`); after 30 minutes a new request with a new code replaces it (`DEVICE_APPROVAL_PENDING_MAX_MS`, `:74`). On linux-mini the request was still alive at 1:50 AM, its expiry renewed to 1:58 AM. No Deny was recorded there.

**5. The popup has no exit that ends it.** Allow needs the code. Deny lasts a day (`DEVICE_APPROVAL_DENY_MS`, `:75`), then the phone asks again. Later, ×, Escape and a click outside all hide it for 30 days, but only in the window where it was pressed: it is kept in that window's local storage (`apps/web/src/components/devices/laterStore.ts`, used at `apps/web/src/components/devices/ConnectDeviceHosts.tsx:271`). Another browser or window on the same machine shows it again.

**6. The popup says nothing about where the code is.** It reads "Type the code shown on iPhone Duo" (`apps/web/src/components/devices/ConnectDeviceViews.tsx:340`) with no step for the phone.

**7. What brought it back on M1 after Later is not confirmed.** M1 is not in M5's machine list, so its version and device list could not be read. linux-mini runs 1.0.407, which has the per-device Later of PR #793 (first in 1.0.405). An M1 older than 1.0.405, or a second window, would explain a return; T-01 settles it.

**8. No m4 thread is working on this.** The closest, "Device approval popup and multiple phones" on m4, last ran on November 20 and ended with the release check of PR #784.

## Scope

In: an app-wide "Allow this phone" block on the iPhone that lists every waiting machine with its code; a "Stop asking" action on the phone; the phone's app version in what it tells a machine; "Where is the code?" steps in the machine's popup, and a different line when the phone's app cannot show a code; Later kept by the machine so every window of that machine agrees; an iPhone release that carries the code screens; phrases in the eight catalogs; headless fixtures with captures.

Out: sharing an approval between machines, or one request for all machines (1416 D-01 says per machine; D-01 below asks again); sending a code in a push or through the relay (the code lives only in the machine's memory, 1406 D-06); changing how a code approves, its lifetime, Deny's day or the 30 days of Later; Android; the desktop app's own floating code card (PR #793).

## Acceptance Criteria

- [ ] AC-01: On the iPhone, while one or more machines wait to allow this phone, every screen (home, menu, any chat, settings) shows one "Allow this phone" block that lists each waiting machine by name with its current code and the line "This phone: {name} · ID {id}".
- [ ] AC-02: The block opens by itself the first time a machine starts waiting. After Hide it becomes one row, "{n} machines are waiting · Show codes", and stays hidden through new codes, reconnects and restarts. It opens by itself again only for a machine that was not waiting when it was hidden, or after 30 days (same rule as PR #793).
- [ ] AC-03: A code in the block is the one the machine accepts at that moment: when the machine issues a new code, the block shows it within 10 seconds, and a machine that allowed, denied or stopped answering leaves the block or is marked "{machine} isn't reachable right now".
- [ ] AC-04: "Stop asking" on the block pauses this phone's connection to the listed machines (the existing Disconnect). Within 10 minutes each machine's request runs out and its popup closes with no action there. The machine's page on the phone offers Reconnect, which asks again.
- [ ] AC-05: The phone tells each machine its app version, and the popup shows it ("iOS · SpecWithCode 0.1.9").
- [ ] AC-06: The popup shows "Where is the code?" with steps for the asking device's kind. For an iPhone: open SpecWithCode on {device}; the code for {machine} is at the top of the screen under "Allow this phone"; check the phone also says ID {id}.
- [ ] AC-07: When the asking phone reports no version, or one older than the first build with AC-01, the popup replaces the steps with "This iPhone's app cannot show the code yet. Update SpecWithCode on {device}, then open it again." The code box, Deny and Later stay.
- [ ] AC-08: Later pressed in any window of a machine hides that device's popup in every window of that machine (its own app and browsers) for 30 days. The device stays listed under Settings > Machines, where its code can still be typed. A machine that does not support this keeps today's per-window Later.
- [ ] AC-09: Nothing in this increment lets a device in without its typed code, changes which machine an approval covers, or stores or sends a plain code anywhere new. The existing device-approval tests pass unchanged.
- [ ] AC-10: An iPhone build with AC-01 to AC-05 is released, and the first version that has it is the one AC-07 compares against.
- [ ] AC-11: T-01's findings are written in `reports/m1-repro.md`: M1's app version, whether Later was pressed there, in which window the popup returned, and which finding above explains it.

## Approach

Mockup: `reports/mockup.html` (phone block and popup, with the new parts marked).

1. Reproduce first (T-01). The fix for "comes back after Later" depends on whether M1 is old or a second window showed it. If M1 is older than 1.0.405, updating it is the fix and AC-08 is still worth having.
2. iPhone block (AC-01 to AC-04). `AppModel.machinesAwaitingApproval` already returns the waiting machines with their codes (`apps/ios/SWCKit/Sources/SWCSync/AppModel.swift:963`). Add one view over it, mounted in the root layout so it sits above every screen, and reuse the rows of `approvalOthers` in `ChatView.swift`. Hide is kept on the phone per machine and per this phone's ID, never with a code. "Stop asking" calls the engine's existing enable switch (`MachineViews.swift:169`).
3. Version (AC-05, AC-07). The phone sends its app version with its client label; the server already stores `app` for a device (`describeSession`, `ConnectDeviceTrust.ts:117`). The web compares it with one constant, the first iPhone version that shows the block.
4. Popup steps (AC-06, AC-07). One new block in `DeviceApprovalPrompt` (`ConnectDeviceViews.tsx`), text chosen by device kind and version. Words only, no new control.
5. Later on the machine (AC-08). Two routes on the machine's device list, read and add, open to whoever can already approve there (`canApprove`). Stored beside the device list by the device reference the popup already uses (`deviceReferenceOfKey`), never by key or code. Advertised by a capability; the window falls back to local storage when it is absent.
6. Release (AC-10) through `request-release.sh` for the desktop parts and the iPhone release steps in `apps/ios/docs/app-store.md`.

Rejected: a push that carries the code (the relay would see it, and the code is only in the machine's memory); one approval for all machines (an access change against 1416 D-01); a push that only says "open the app" (the phone asks only while its app is open, so the owner is already looking at it); making Later end the request on the server (the phone would create a new one 4 seconds later).

Risks: the version is what the phone says about itself, so it only picks which help text shows and never approves anything. Later kept on the machine is a new write on the trust store; it must be refused for a device that is not approved there.

## Decisions

### Asked
- none yet

### Defaulted (change any before sw-do)
- D-01: approval stays per machine; the phone shows every waiting machine's code in one place instead of one request covering all machines → keep (1416 D-01; changing it is an access decision for Anton).
- D-02: no push or notification for a waiting code → none (the code never leaves the machine and the phone; 1406 D-06).
- D-03: Later moves from the window to the machine → yes, with the per-window fallback for older machines.
- D-04: "Stop asking" reuses Disconnect instead of a new server call that withdraws the request → reuse (no new auth surface; the request runs out in at most 10 minutes).
- D-05: the Hide rule on the phone copies PR #793 (closed stays closed for the unchanged request; 30 days) → copy.

### Open
- D-06: should the phone's block also appear as a Live Activity or lock-screen line while the app is in the background? Not planned; the phone does not ask in the background.

## Review

Auth area: an adversarial review by another model family is required before release, and Anton's acceptance of the popup wording and the phone block on a real iPhone.

## Tasks

### T-01 Reproduce on M1 and record what brings the popup back
- AC: AC-11 | Files: [.specweave/increments/1447-a-waiting-phone-shows-its-approval-code-on-every-screen-and-the-machines-popup-says-where-to-find-it/reports/m1-repro.md] | Test: `test -s .specweave/increments/1447-a-waiting-phone-shows-its-approval-code-on-every-screen-and-the-machines-popup-says-where-to-find-it/reports/m1-repro.md`

### T-02 iPhone: one "Allow this phone" block above every screen, with Hide
- AC: AC-01, AC-02, AC-03 | Files: [repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Pairing/ApprovalCodesBlock.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ApprovalCodesBlockTests.swift] | Test: `cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test --filter ApprovalCodesBlockTests`

### T-03 iPhone: "Stop asking" and the app version sent to machines
- AC: AC-04, AC-05 | Files: [repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Pairing/ApprovalCodesBlock.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Connect.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCTransportTests/MachineHTTPTests.swift] | Test: `cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test --filter MachineHTTPTests`

### T-04 Popup: "Where is the code?" steps and the old-app line
- AC: AC-06, AC-07 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/connectDevices.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx] | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && npx vitest run src/components/devices/ConnectDeviceViews.test.tsx`

### T-05 Later kept by the machine, with the per-window fallback
- AC: AC-08, AC-09 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/connectDevicesHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.test.tsx] | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && npx vitest run src/fleet/ConnectDeviceTrust.test.ts src/auth/deviceApproval.test.ts`

### T-06 Captures, catalogs and the iPhone release
- AC: AC-10 | Files: [repositories/anton-abyzov/specwithcode/apps/web/tests/device-approval/verify.mjs, repositories/anton-abyzov/specwithcode/apps/ios/project.yml] | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && node tests/device-approval/verify.mjs`
