# Joining a machine sets up both directions, and says what each approval adds

## Problem

Anton, November 19, 2026, 9:58 AM. He joined a new Windows machine (PRCTY-AABYZOV, SpecWithCode 1.0.386) to M5 (1.0.386). On Windows he picked M5 and pressed Allow, typed Windows's code on M5, and M5 showed "PRCTY-AABYZOV joined" (`reports/m5-joined-notice.jpg`). A moment later Windows showed "A new device wants to use PRCTY-AABYZOV … Anton M5MAX PROLED, ID VEE7, macOS · SpecWithCode 1.0.386 · Asked at 9:54 AM" (`reports/windows-asks-for-m5-window.jpg`). He asked whether that is a duplicate, and whether M5 can now control Windows.

What happened, from M5's own records (read by a worker on M5, `reports/evidence.md`), times EST:

| Time | Where | What |
|---|---|---|
| 9:54:11 | M5 | Windows's app asks to use M5 |
| 9:54:29 | M5 | Approved with the code typed on M5 (`connect-devices.json`, by "this machine") |
| 9:54:46 | M5 | Allow on Windows reaches M5 (`accountJoinFleetWorkers`, `apps/server/src/studioFleetHttp.ts`): M5 lists Windows and holds a grant there, full access, renewing, now until December 19. M5 records the join, so its app shows "PRCTY-AABYZOV joined" (`apps/web/src/components/FleetJoinNotice.tsx`) |
| 9:54:52 | M5 | M5's own window opens the newly listed machine by itself (`apps/web/src/components/AutoConnectPrivateMachines.tsx`, `apps/web/src/studio/fleetAutoConnect.ts`) |
| 9:54 | Windows | Windows keeps its own device list (1327; 1416 D-01, each machine approves each device once), so it asks for the code of M5's window |

After the join:

| From | To | Window (a person at that machine opens the other) | Agents |
|---|---|---|---|
| Windows | M5 | Yes, code typed on M5 | No grant on M5 |
| M5 | Windows | Only after M5's code is typed on Windows | Yes, grant |

So the second prompt is not a duplicate of the code Anton typed: that one let Windows's window into M5, and this one lets M5's window into Windows. It is still a defect:

- The join was decided as five steps, "reject any join design that adds a step" (project memory `decision_machine_join_flow`). The second code is a sixth step the decision never planned. It follows from 1416 D-01 together with the automatic open.
- Neither screen links it to the join or says what it adds. Windows calls M5 "a new device" a minute after "Allow M5", and its line "Allow lets it use terminals, files, settings and sign-ins on PRCTY-AABYZOV and start work there" reads like the Allow just pressed (`apps/web/src/components/devices/ConnectDeviceViews.tsx:238`, `:327`).
- The question is on Windows, but the code to type is on M5's screen.
- Agents work one way. Under 1390's equal coordinators, Hand off from Windows to M5 has no grant to run on.
- First run still says "Choose your main machine" (`apps/web/src/components/onboarding/SignInFirstStep.tsx`), while 1390 has no main machine for projects (1390 D-20 kept the fleet's "Main machine" words).

## Scope

In: the join on the new machine, the joined notice on the other machine, the device pop-up's wording, the first-run machine row's wording, and, after Anton decides, the second code and the reverse agent grant.

Out: the relay, the iPhone, Team rules, joins through a join line with another account (1388), and 1390's Sync, Add and Hand off themselves.

Lanes. `[label]` changes only what is shown and ships after review and green CI. `[access]` changes who gets access and waits for Anton's acceptance and a Muse Wonderful review.

## Acceptance Criteria

- [ ] AC-01 [label]: The device pop-up says what Allow adds and that letting a machine's agents run work is separate: Allow lets the SpecWithCode app on that device open this machine (chats, terminals, files, settings, sign-ins). No reassurance keys on the device's own name; the line that the name is the device's own word stays.
- [ ] AC-02 [label]: While a window waits for a code on a machine that just joined this one, the joined notice says so: what the join already allows, and that to open that machine from this window too, the code this window shows is typed there. Without such a wait the notice reads as today.
- [ ] AC-03 [label]: After Allow on the new machine, the join step says what comes next on this screen: the other machine's window may ask for a code here, and that code is read on the other machine.
- [ ] AC-04 [label]: First run names no main machine: the row reads as joining one of your machines (wording agreed with the 1390 owner so join, Sync and Hand off read as one concept).
- [ ] AC-05 [access]: Built as Anton decides D-01.
- [ ] AC-06 [access]: Built as Anton decides D-02.
- [ ] AC-07 [label]: Every new string goes through the translation function with entries for the eight shipped languages.
- [ ] AC-08 [label]: Checked after release with two real machines by Anton: the join's screens, then what each machine can open and run on the other.

## Decisions

- D-01 [access], for Anton: should the join stop asking for the second code? (a) Keep it and explain it (AC-01 to AC-03). (b) When Allow is pressed on the new machine, the new machine also lets in the window that typed its code on the other machine, on that machine's word over the channel the join already uses. That machine's agents get full access through the same Allow, so this widens nothing it can reach. It is a narrow exception to 1416 D-01. Recommended: (b), five steps as decided.
- D-02 [access], for Anton: should a join let agents run work both ways? (a) Yes, by default, with a visible choice on the join card to keep it one way. (b) No; the joined notice offers a second Allow for the reverse direction. Recommended: (a), so Hand off works either way between equal machines.

## Approach

Wording first (AC-01 to AC-04, AC-07), then D-01 and D-02 as decided. Each side words only what it knows for certain: a window knows which machine it waits on, and a machine knows which machine it just allowed. A device request carries no machine identity (`packages/contracts/src/connectDevices.ts`), so the pop-up never claims "this is M5".

## Tasks

### T-01 Pop-up, joined notice and join step wording
- AC: AC-01, AC-02, AC-03, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: focused web tests for the three components

### T-02 First-run row names no main machine
- AC: AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/SignInFirstStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: focused web test; wording agreed with the 1390 owner

### T-03 Build D-01 as decided
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx | Test: server tests for the binding and its refusals; Muse Wonderful review

### T-04 Build D-02 as decided
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx | Test: server tests for both directions; Muse Wonderful review

### T-05 Check on real machines after release
- AC: AC-08 | Files: .specweave/increments/1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds/reports/ | Test: Anton's screens of the join on both machines

### T-06 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: .specweave/increments/1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds/ | Test: specweave verify 1422

## Review

Reviewer: Muse Wonderful, `muse-wonder-full-1.0`, effort high, for anything touching device approval or grants. It confirms that no `[label]` change alters who gets access.
