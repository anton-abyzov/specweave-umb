# Keep the iPhone approval wait steady and clear

## Problem

On November 18, 2026 at 3:31 AM Anton reported from iPhoneA (0.1.8 build 49) that the m1 chat "keeps reloading and disconnecting" and "displays wrong". Screenshot: `~/Downloads/Screenshot 2026-11-18 at 03.30.46.png`. Observed on the Duo through iPhone Mirroring (frames in `~/.specwithcode/m4/scratch/2026-11-18-ios-approval-loop/`):

- The screen contradicts itself. The title says "Waiting for approval on m1", yet it offers a Reconnect button and the composer says "Machine unavailable. Your draft is kept." With saved messages, the banner says "m1 is offline" and offers Reconnect.
- The wait doesn't hold. Going to the background drops the refusal: `MachineConnection.setActive(false)` publishes a fresh offline status without `lastError` (`SWCTransport/MachineConnection.swift:198-211`). Coming back starts the 3 s connecting grace (`SWCSync/LiveEngine.swift:213`), and the attempt reads `.connecting` (`MachineConnection.swift:412`). So the chat swaps the waiting screen for a spinner until the next refusal comes back. Each Reconnect tap does the same: the screen offers the button that makes it blink. Anton has to leave the app to type the code on m1, so every return flashes.
- Over 15 s at 4 Hz, the waiting screen itself held steady between retries. The phone retries every 4 s (two relay 401s per cycle in the Duo syslog), which is 1327's intended cadence.

Out of this increment, handed to the device-approval thread: the server mints a new code when a waiting entry passes its 10-minute TTL or the machine restarts (`apps/server/src/fleet/ConnectDeviceTrust.ts:67,632,719`). The Duo's m1 code changed from U63FZA to 6X9SF6 between 3:36 and 3:40 AM.

## Scope

In: iOS only (`apps/ios`). How a machine waiting for approval is published and drawn in chat. Out: server code minting and TTL, desktop approval dialog, device naming, the "machine: code" list (other thread), retry cadence (stays 4 s).

## Acceptance Criteria

- [ ] AC-01: While a machine refuses this phone for approval, the machine summary keeps the approval code and a steady status through retries, Reconnect, network changes and a background and foreground round trip. It never reads "Connecting" in that time. It changes only on a different outcome (connected, or another error).
- [ ] AC-02: The chat for that machine shows one waiting view. It has a title naming the machine, the code large and copyable, one instruction line, and a small "connects on its own" line with an activity indicator. It has no Reconnect button, and it offers Connection options plus "View on <machine>" when another copy of the project is reachable.
- [ ] AC-03: The composer and banner agree with the waiting view. The composer reads "Waiting for <machine> to allow this phone. Your draft is kept." With saved messages, the banner says the machine is waiting for approval with the code, not "offline" with Reconnect.
- [ ] AC-05: For 1406 AC-06 and AC-07: the waiting view lists every machine still waiting, one row each with "Open SpecWithCode on <machine> and type this code:" over its latest code, large and copyable. A machine leaves the list only once it connects or is switched off on this phone. A line reads "This phone: <name> · ID <XXXX>", with the name from the pairing label. The ID slot fills when 1406's `DeviceShortID` lands on main.
- [ ] AC-04: `make test-core` passes, with new tests for AC-01 and AC-03. The real-phone check before and after on iPhoneA or the Duo is recorded in reports/.

## Approach

- `MachineConnection.setActive(false)` keeps an `awaitingApproval` `lastError` on the offline status it publishes, so the code survives the background. Attempts already copy `lastError` forward.
- `LiveEngine.summary` holds a machine with an approval code at `.offline` and not settling unless it is connected. Grace and attempt states can't turn it into "Connecting".
- `ChatView`: `showsOfflineTranscript` is true while an approval code is set, a dedicated `approvalTranscript` view replaces the generic placeholder, and the composer's blocked reason and `connectionNotice` get approval wording. The waiting copy lives in `MachineRecovery.swift` (`MachineSummary.approval*`), where tests can reach it.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Keep the 4 s approval retry: it is 1327's intended cadence, and the captures show no flicker from it.
- D-02 No Reconnect on the waiting view: retries are automatic, and the button only made the screen blink.
### Open
- none

## Tasks

### T-01 Hold the approval state through background, retries and grace
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCTransport/MachineConnection.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/LiveEngine.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCTransportTests/MachineConnectionTests.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ConnectingGraceTests.swift | Test: make -C repositories/anton-abyzov/specwithcode/apps/ios test-core

### T-02 One clear waiting view in chat
- AC: AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/TeamRulesTests.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/MachineRecovery.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ConnectingGraceTests.swift | Test: make -C repositories/anton-abyzov/specwithcode/apps/ios test-core

### T-03 Verify on the phone and review
- AC: AC-04 | Files: .specweave/increments/1408-keep-the-iphone-approval-wait-steady-and-clear/reports/ | Test: make -C repositories/anton-abyzov/specwithcode/apps/ios test-core
