# Joining a machine is one way, and says what each approval adds

## Problem

Anton, November 19, 2026, 9:58 AM. He joined a new Windows machine (PRCTY-AABYZOV, SpecWithCode 1.0.386) to M5 (1.0.386). On Windows he picked M5 and pressed Allow, typed Windows's code on M5, and M5 showed "PRCTY-AABYZOV joined" (`reports/m5-joined-notice.jpg`). A moment later Windows showed "A new device wants to use PRCTY-AABYZOV … Anton M5MAX PROLED, ID VEE7, macOS · SpecWithCode 1.0.386 · Asked at 9:54 AM" (`reports/windows-asks-for-m5-window.jpg`). He asked whether that is a duplicate, and whether M5 can now control Windows. At 10:13 AM he sent a third photo, Windows's Settings > Advanced connections (`reports/windows-machines-settings.jpg`): M5's card reads "M5 can start work here · All projects · until you stop it" and "This machine can't start work on M5 · Not set up" with Set up…, under it the join's done card "M5 can run work here · Full access · renews by itself … Next, on M5: this machine can only run a project it has a copy of. Open Settings > Machines there and add a project to this machine" (`apps/web/src/components/settings/AccountJoinCard.tsx:290`). He asked whether that is another kind of permission, and said typing a code "sounds a bit tricky".

The three prompts, by kind:

| Prompt | Kind | What it lets in |
|---|---|---|
| Code typed on M5 (result: photo 1) | Device approval (1327) | Windows's app opens M5 |
| Allow M5 on Windows (result: photo 3, first line) | Machine-access grant | M5's agents run work on Windows |
| Code asked on Windows (photo 2) | Device approval (1327) | M5's app opens Windows |
| "This machine can't start work on M5 · Not set up" (photo 3) | Machine-access grant, not given | Windows's agents would run work on M5 |

What happened, from M5's own records (read by a worker on M5, `reports/evidence.md`), times EST:

| Time | Where | What |
|---|---|---|
| 9:54:11 | M5 | Windows's app asks to use M5 |
| 9:54:29 | M5 | Approved with the code typed on M5 (`connect-devices.json`, by "this machine") |
| 9:54:46 | M5 | Allow on Windows reaches M5 (`accountJoinFleetWorkers`, `apps/server/src/studioFleetHttp.ts`): M5 lists Windows and holds a grant there, full access, renewing, now until December 19. M5 records the join, so its app shows "PRCTY-AABYZOV joined" (`apps/web/src/components/FleetJoinNotice.tsx`) |
| 9:54:52 | M5 | M5's own window opens the machine that just granted it, by itself: it saves a Connect route (`RelayConnectionRegistration`) for each account machine that granted this one (`apps/web/src/cloud/GrantedAccountMachines.tsx`, selection in `apps/web/src/studio/grantedAccountMachines.ts`) |
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
- The join's done card sends the owner to the other machine's Settings > Machines to add a project, while 1390 names that step Add.
- First run still says "Choose your main machine" (`apps/web/src/components/onboarding/SignInFirstStep.tsx`), while 1390 has no main machine for projects (1390 D-20 kept the fleet's "Main machine" words).

## Scope

In: wording only, true to what the app does today: the device pop-up (done, T-01), the joined notice on the machine that was joined, the Allow on the new machine, the join's done card and the first-run machine row.

Out: every access change (D-01 to D-06 and D-08 to D-11), moved to 1428 with the design (D-07); retiring 1.0 (1429); the relay, the iPhone, Team rules, joins through a join line with another account (1388), and 1390's Sync, Add and Hand off themselves.

Lane: `[label]` only. It changes what is shown, never who gets access, and ships after review and green CI.

## Acceptance Criteria

- [ ] AC-01 [label]: The device pop-up says what Allow adds and that letting a machine's agents run work is separate: Allow lets the SpecWithCode app on that device open this machine (chats, terminals, files, settings, sign-ins). No reassurance keys on the device's own name; the line that the name is the device's own word stays.
- [ ] AC-02 [label]: The joined notice on the machine that was joined says what the join gave, as the app does today: its agents can run work on the new machine; the new machine's app can open this machine, because its code was typed here; the new machine's agents cannot run work here, and the existing Allow for that is offered (D-02; `apps/web/src/components/settings/IncomingWorkerSetup.tsx`), which nothing grants by itself; and this machine's app asks the new machine once for a code before it opens it, with that code shown here.
- [ ] AC-03 [label]: The Allow on the new machine says what it covers, as the app does today: the other machine's agents may run work here; the other machine's SpecWithCode app asks once for a code when it opens this machine, which the other machine shows and the owner types here. It claims neither that the Allow keeps that app out (the other machine's management key here is never device-gated) nor that this machine has no access to the other one (today the code typed there let this machine's app open it).
- [ ] AC-09 [label]: The join's done card names the next step with 1390's verbs (Add a project to this machine) instead of sending the owner to the other machine's Settings.
- [ ] AC-04 [label]: First run names no main machine: the row reads as joining one of your machines (wording agreed with the 1390 owner so join, Sync and Hand off read as one concept).
- [ ] AC-07 [label]: Every new string goes through the translation function with entries for the eight shipped languages.
- [ ] AC-08 [label]: Checked after release with two real machines by Anton: the join's screens say what each approval gives, and the second code is announced where it appears.

## Decisions

- D-01 [access] Should the join stop asking for the second code? → Drop it; Allow covers it, and the Allow says so (Anton, November 19, 2026: "drop it. I think allow covers it, but just explain this"). Built in 1428 (its AC-03); 1422's AC-03 says what Allow covers today.
  Options weighed for Anton's "a code sounds tricky" (November 19): a one-click Allow for any device signed in to the same account would drop the guarantee the code gives, because a stolen sign-in is also the same account and the name is the device's own word (why 1327 kept the code, November 17). Comparing a code shown on both screens and clicking Allow is lighter but easier to click through. What keeps the guarantee and drops the typing is proof from a machine already trusted: the joined machine vouches for its own app with the credential the join gave it, which an attacker with only a sign-in does not have. So one typed code stays per new machine, and every later prompt between the two machines is covered by that proof.
- D-02 [access] Should a join let agents run work both ways? → One way; offer the reverse (Anton, November 19, 2026). 1422's AC-02 offers the existing reverse Allow; the one-way grant is built in 1428 (its AC-05).
- D-03 [access] Should the code typed on the joined machine give the new machine's app access to it? → No, the code only joins (Anton, November 19, 2026, card answer "Yes, the code only joins"). Anton, November 19, 2026, on "Your first code let Windows's app into M5": "I think this Windows machine has no access to M5. I never intended this to be, or maybe I interpreted it wrong." It does today: M5's records show Windows's app approved at 9:54:29 AM with a live session, and photo 3 shows Windows listing M5's projects through it. Today that code approves the new machine's app as a full device on the joined machine (1327), because its app hands the join line over through that session (`accountJoinFleetWorkers`). Built in 1428 (its AC-02); replaces the November 17 reading in `decision_machine_join_flow` that the code is an ordinary device approval.
- D-04 [access] Should the new machine remember the access level chosen at Allow and refuse anything higher, even if the joined machine asks for more later? → Yes, remember my choice (Anton, November 19, 2026, card answer "Yes, remember my choice"). Built in 1428 as `ownerCap` (its AC-04).
- D-05 [access] Should the no-code vouch also need all sign-ins, not only all projects? → All projects and all sign-ins (Anton, November 19, 2026, card answer "All projects and all sign-ins"). Built in 1428 as its AC-03's condition.
- D-06 [access] After the reverse Allow, should the new machine's app open the joined machine by itself? → No (Anton, November 19, 2026, card answer "Don't open M5 by itself"). The automatic open (`apps/web/src/cloud/GrantedAccountMachines.tsx`) is skipped for a machine whose only tie is the reverse grant; the new machine's app reaches the joined machine only if the owner opens it there and types a code. Built in 1428 (its AC-05).

- D-07 [scope] How should 1422 continue after three design reviews that still said fix first? → Wording now, access later (Anton, November 19, 2026, card answer "Wording now, access later"; at 5:47 PM, relayed by the coordinator: "No, I wouldn't include it in this increment."). 1422 keeps only wording true to today; the access decisions and the design move to 1428. The coordinator's reading: the shipped behaviour round 3 found (the management key) also stays out of 1422.
- D-08 [access] Versions: if either machine runs an older app, should the join work as today, with the screens saying so? → "Yes, older works as today" (card answer). At 5:47 PM, relayed by the coordinator: "Think about what the best solution is. I suggest moving to 1.1 soon and just getting rid of all 1.0 versions at some point, so that you cannot download it and you could only upgrade. This will be kind of mandatory." The coordinator's reading: the new join rules need both machines on 1.1; a 1.0 machine works as today only until 1.0 is retired (upgrade only, mandatory, waiting for a quiet moment); no 1.0 compatibility paths. Built in 1428 (its AC-07); retiring 1.0 is 1429.
- D-09 [access] Older app: an older app's code makes it a full device on the joined machine; what should happen? → "Leave it as today" (card answer; it replaced an earlier card that overstated taking the access back, answered "Yes, take it back"). At 5:47 PM, relayed by the coordinator: "What do you mean, 'take back, remove the excess'? I don't think so, but yeah, we're a searching thing. Maybe for early versions, it makes sense because they are not stable." The coordinator's reading: a soft no. "Take back" meant the joined machine removing that older app's device approval a minute after the join, so only the join remains; it could not fully work, because in that minute the app can approve other devices there. With 1.0 retired (1429), no older app is left to need it.
- D-10 [access] Change level: should the new machine let the owner lower the joined machine's level later from its own Settings? → "Yes, add a level menu" (card answer). Built in 1428 (its AC-04).
- D-11 [access] Remove: if Remove is pressed on the joined machine while the new machine is offline, how fast must the no-code access end? → "Within a day" (card answer). Built in 1428 (its AC-06).

## Approach

Wording only. Each string says what the app does today and is checked against the code before it ships; 1428 updates the strings as its behaviour lands, never ahead of it. Each side words only what it knows for certain: a window knows which machine it waits on, and a machine knows which machine it just allowed. A device request carries no machine identity (`packages/contracts/src/connectDevices.ts`), so the pop-up never claims "this is M5". T-07 checks that the reverse offer only points at the existing Allow (`IncomingWorkerSetup.tsx`, `accountMachinesToOffer`); if it needs a new entry point that issues a grant, it moves to 1428. T-02's words are agreed with the 1390 owner, after rereading `decision_sync_and_hand_off` (revision 3 of November 19, 2026).

### Design

The access design (rounds 2 to 5) moved to 1428 on November 19, 2026 (D-07). Design reviews 1 to 3 stay here in `reports/`, and `reports/how-the-join-works.md` explains the join as it works today.

## Tasks

### T-01 The device pop-up says what Allow adds
- AC: AC-01, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/components/devices

### T-07 Joined notice and Allow say what the join gives today and announce the second code
- AC: AC-02, AC-03, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: focused web tests for both components

### T-02 First-run row and done card use 1390's words
- AC: AC-04, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/SignInFirstStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: focused web test; wording agreed with the 1390 owner

### T-05 Check on real machines after release
- AC: AC-08 | Files: .specweave/increments/1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds/reports/ | Test: Anton's screens of the join on both machines

### T-06 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-07, AC-08, AC-09 | Files: .specweave/increments/1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds/ | Test: specweave verify 1422

## Review

Reviewer: another model family for each pull request head. Muse Wonderful is out until November 23, 2026, so by Anton's standing rule of November 18, 2026 the reviews run on Copilot Enterprise with GPT-6.1 Sol while Muse and Codex are both out. Each review confirms that no `[label]` change alters who gets access. Muse Wonderful reviews 1428's access work.

Design reviews, November 19, 2026: Muse Wonderful was out on every machine (rate limit until November 23; on M5 the run ended at once with no details), so the design ran on Codex GPT-6.2 Sol, effort high, on M5, following the reviewer order behind Anton's standing rule of November 18, 2026 ("Yes, as a standing rule": whenever Muse and Codex are both out, Copilot Enterprise with GPT-6.1 Sol, no more asking); Muse was out and Codex on M5 was not, so Codex ran. Round 1 (`reports/design-review-1.md`) and round 2 (`reports/design-review-2.md`) said fix first. Round 3 (`reports/design-review-3.md`) said fix first too, and sorted its findings against today's baseline; the design then moved to 1428 (D-07).
