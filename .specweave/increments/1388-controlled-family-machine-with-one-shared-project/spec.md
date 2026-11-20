# Controlled family machine with one shared project

## Problem

Anton wants his daughter's MacBook Air under his control: his machines (the M4 is main) run agent work on it and manage it, while her Mac cannot open or send into his projects, threads, memory, personal assistant, Google data or secrets, except one project he chooses to share. SpecWithCode has no way to say "this machine is controlled and gets no way back in". The safe path exists only by accident, and the obvious path leaks everything.

Evidence (specwithcode `origin/main` `05a2cadba`, after 1327 shipped in 1.0.343; citations re-checked by the review in `reports/muse-spec-review.md`):

- **The obvious path leaks.** If her Mac signs in to Anton's Connect account and he types its approval code (the normal join flow, [[decision_machine_join_flow]]), her app gets a session on every machine of the account that approves it. The relay lets any same-account device list the account's machines (`infra/relay/src/environments/EnvironmentLinks.ts:408`). Each approved session gets the standard scopes: threads, terminal, files, settings (`apps/server/src/cloud/CloudLink.ts:1794-1834`, `packages/contracts/src/auth.ts:224-238`). The mint issues it with no principal (`CloudLink.ts:1828-1834`). Owner-only RPCs refuse only coordinator principals (`apps/server/src/auth/RpcAuthorization.ts:408-409`), so her window could change Google, Telegram, Away and sealed-secret settings on the M4 (`packages/contracts/src/clientRpcPermissions.ts:92,108-117,251-260`).
- **The safe path is undeclared.** A join line made on her Mac redeems with no account check (`apps/server/src/studioFleetHttp.ts:614-691`; compare the account check for account join at `:781-796`). It gives the M4 a management key on the Air holding the standard scopes plus `access:write`, `fleet:update` and `fleet:skills` (`apps/server/src/fleet/fleetRedemption.ts:24-29`), and gives the Air nothing back. One click on her row on the M4 breaks that. "Make pairing link" gives her app a session on the M4 (`apps/web/src/components/settings/ConnectBothWays.tsx:93-103`, 30 days once redeemed, `apps/server/src/auth/SessionStore.ts:565`). The reverse Allow "hands out full access to this machine" (`studioFleetHttp.ts:833`). Nothing marks her machine as one that must never get these.
- **Things flow to the Air with no action.** The M4 exchanges its whole machine nickname map with every peer every minute, both ways (`apps/server/src/fleet/MachineNicknameSync.ts:30,83-104,137-162,185`). Because the M4 manages the Air, the grant defaults to all projects and all sign-ins (`apps/server/src/fleet/workGrantPolicy.ts:103-108`). Routines switch on once, by themselves (`apps/server/src/fleet/WorkGrants.ts:268-282`). A missing policy record reads as all projects, all sign-ins, routines on (`workGrantPolicy.ts:68-76`).
- **Sharing one project shares more than the project.** `studio_project_add_to_machine` and "Copy files only" both link the copy (`apps/server/src/mcp/toolkits/project/tools.ts:182`, `apps/web/src/studio/projectLink.ts:666-670`), and linked memory merges both ways (`apps/server/src/project/LinkedMemorySync.ts:40-45`). An existing copy with no threads of its own is linked by itself (`apps/server/src/mcp/toolkits/project/addToMachine.ts:466-487`). Folder copy sends `.git`, tracked, untracked and ignored data by default (`apps/server/src/fleet/folderTransfer/classify.ts:25-31`), so committed `CLAUDE.md`, `.specweave/` memory and evidence folders travel too.
- **Device identity stops at a key.** The 1327 gate knows a Connect device only by its proof-key thumbprint (`apps/server/src/fleet/ConnectDeviceTrust.ts:83-131`). Nothing ties a key to a machine, so a reset app or a browser on her Mac is a new device.
- **No role exists.** Principals are `device` or `coordinator` (`packages/contracts/src/auth.ts:394-397`). Machine roles are derived labels (`apps/web/src/components/settings/machineNextStep.logic.ts:123-160`). Team rules are any, none or same-rules, never per machine (`packages/shared/src/teamRules.ts:885-908`).
- **She owns her Mac.** Her app and local CLI hold every scope there (`apps/server/src/auth/LocalCliCredential.ts:59`). She can stop the M4's workers (`revokeWorkGrant`, `studioFleetHttp.ts:987`) or end its management key (principal revocation, `apps/server/src/persistence/AuthSessions.ts:336`), and she can read every thread it runs there. Today the M4 learns of either only when a call fails.

## Scope

In:
- A `controlled` role for a machine that Anton's machines manage, chosen on the M4 when the machine is added or later.
- The role spreads to every own machine the M4 manages.
- Each of those machines refuses every way in for a controlled machine.
- Marking a machine controlled revokes the ways in it already holds.
- Narrow grant defaults.
- Sharing one project as an unlinked export with a denylist.
- Rules for file transfer, folder copy and sealed secrets toward a controlled machine.
- A notice on the controlled machine.
- An alert on the M4 when its key stops working there.
- As a separate fix that the role depends on: owner-only RPCs refuse device sessions the owner has not marked as owner devices.

Out:
- Stopping her from removing the M4. She owns her macOS account, so the design is tamper-evident, not tamper-proof (D-03).
- Screen control. Another machine's agents get no computer-use tool, and that stays.
- Parental controls (Screen Time) and her provider and git accounts. These are macOS, provider and GitHub settings; the setup report covers them.
- Own machines the M4 does not manage. The setup report says not to approve her devices there.
- A person identity or child account in Connect (D-01). A hosted family console.
- Accepted disclosures, not fixed here:
  - The unauthenticated environment descriptor (`/.well-known/studio/environment`) shows environment ID, label and version to anyone who can reach an address.
  - Tailnet reach is decided by tailnet ACLs.
  - Content an M4 coordinator writes into a prompt for work on her Mac is hers to read (AC-08 reminds the owner).

## Acceptance Criteria

- [ ] AC-01: Owner-only RPCs (personal data, Google, Telegram, Away, sealed secrets) and the role change in AC-02 decide by session kind, per this table, enforced in `RpcAuthorization.ts` with a negative test per row:

  | Session kind | Owner-only RPCs |
  |---|---|
  | Local owner (`desktop-bootstrap`, `local-cli-owner`, `administrative-bootstrap`) | allowed |
  | Approved Connect device marked owner device | allowed |
  | Approved Connect device not marked owner device | refused |
  | Hub-linked phone marked owner device | allowed |
  | Coordinator principal (management key, worker grant, pairing link made for a machine) | refused (as today) |
  | Fleet management token for `fleet:update` / `fleet:skills` | not an owner-only route (as today) |

  An approved device with no flag reads as owner device permanently. The 1327 approval card asks "Is this your own device?" (default Yes). The answer is stored in a side file beside the device list, so an older build reading the device list never fails on a new key.
- [ ] AC-02: Adding a machine from a join line on the M4 asks "My machine" or "Someone else's machine I control"; an existing machine card offers "Make controlled". The role is stored in `studio-fleet-roles.json`, keyed by environment ID and written before the fleet entry. An unreadable roles file refuses every way in (AC-04) for every fleet machine until repaired, and shows a banner. Only a local owner session or an owner device (AC-01) can change the role. Every reader of the fleet file merges it, with a test per reader class (`FleetTargets`, nickname sync, phone roster, fleet update, remote workers, CLI targets).
- [ ] AC-03: The M4 sends the controlled role to every own machine it manages, using its management key, and each one applies AC-04 to AC-07 for that machine. A management key may add the mark and never remove it. Removing it takes a local owner or owner device on each machine (AC-02). Settings > Machines on the M4 lists the machines that applied it and the ones that did not (older build, offline).
- [ ] AC-04: For a controlled machine, each machine holding the role refuses every server path that would give it a way in. T-03 delivers a table of every handler, listed below, each marked refuse, allow (management direction) or not applicable with a reason, and a negative test that calls each refuse row:
  - every `handle(...)` in `studioFleetHttp.ts`, including `allowFleetWorkers`, account join and `selfAllowFleetWorkers`
  - pairing-link redemption and use, for links made for the controlled machine and for its reported keys (AC-05)
  - project link and auto-link
  - Away, handoff, limit handoff and standby targets (`AwayRunner.ts`, `AwayIntents.ts`, `ScheduledTaskTransfer.ts`)
  - `needs` placement of the owner's own project work
  - the CLI paths (`cli/fleet.ts`, `cli/pair.ts`)

  The matching controls are hidden. Refusals carry the stable code `controlled_machine` in the message field older clients already show (the `teamRulesMessage` pattern, `EnvironmentAuth.ts:636-640`), with one text per `{action}` row.
- [ ] AC-05: Same-account sign-ins from the controlled machine are stopped by three layers, in this order of strength:
  1. **Anton's Connect credentials.** She never gets them (setup report).
  2. **The typed code.** On every machine holding the role, the 1327 approval card says "{controlled machine} is a controlled machine. If this request comes from it, press Deny." Deny has the focus.
  3. **Best effort only: reported keys.** The Connect proof key lives in the app window's IndexedDB (`apps/web/src/cloud/dpop.ts:49,113`), not in the local server. The controlled machine's app reports its key thumbprint to its own server, which forwards it to the M4 over the management channel; this reporting path is new. Every machine holding the role refuses those keys at the Connect mint (`CloudLink.ts:1820-1825`) and at the 1327 gate.

  The reporting is cooperative. She owns the app and the server, so a reset app, a browser or a modified build sends nothing. The spec claims no more than layers 1 and 2 for that case.
- [ ] AC-06: Making a machine controlled revokes, on every machine holding the role, what it already holds:
  - its Connect sessions and device approvals for reported keys (AC-05)
  - unredeemed pairing links made for it
  - work grants it holds as coordinator
  - project links with it
  - phone links that use it as hub

  The card then says "Data already on {machine} stays there: machine names, copied files and thread contents."
- [ ] AC-07: A controlled machine gets none of the following:
  - **Nickname map.** The M4 sends it only its own entry, and accepts from it only its own entry.
  - **Skills.** `fleet skills --all` skips it unless it is named.
  - **Memory and routines.** No linked memory, routine sync or person memory.
  - **Assistant seat.** When 1269's "Use Percy here too" ships, a controlled machine is never offered a seat and its join request is refused, even when it came in through a join line (an "own invitation").
  - **Sealed secrets.** These steps are refused.
  - **Agent-started transfers.** `studio_file_transfer` and folder copy started by an agent need the owner's approval card on the sending machine. The card names the controlled machine.

  A test drives the recorded fleet fetcher at the `FleetTargets` boundary for a nickname round, a skills `--all` run and an agent transfer, and finds no other machine's name, no skill and no unapproved file.
- [ ] AC-08: The grant for a controlled machine is written with:
  - projects `listed` (empty until a share)
  - accounts `listed`, with the provider instances the owner picks at share time, shown with their account labels
  - routines false
  - owner `other`, so the hop limit is 1: direct work only, no onward delegation (`packages/contracts/src/studioFleet.ts:417`)

  Owner `other` also makes the grant kind `team` (`workGrantPolicy.ts:92-96`). That has three effects:
  - Work on the controlled machine cannot send back to the M4 (`mayReturnToOrigin`, `workGrantPolicy.ts:203-212`).
  - The machine's own Google data is refused to the M4's work (`personalDataGate.ts:30`).
  - Routines need an explicit grant.

  These are intended, and tests pin them.

  Today only the controlled machine's own app can change a grant (`studioFleetHttp.ts:447-455,984-985`). A new path lets the management key write this narrowed grant, the share list (AC-09) and `controlledBy` (AC-10). That path may only narrow a grant, or add a project the owner shared from the M4; it can never widen accounts, routines or owner. On the controlled machine, a missing or unreadable policy record for a controlled coordinator reads as no access, never the unscoped default. Launching work there shows the owner "Everything in this prompt and its output can be read on {machine}."
- [ ] AC-09: "Share a project…" on a controlled machine's card exports the project to it as its own project, with no link. The export uses a denylist:
  - instruction files (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/`)
  - `.specweave/` memory, increments and reports
  - untracked and ignored files
  - `.git`, which is off by default; the dialog says "Git history counts as shared" when it is turned on

  The share adds only that project to the grant list. A fixture test checks an export of a project holding a tracked `CLAUDE.md`, tracked memory, an untracked note and an ignored data folder, with the tick off, and finds none of them on the target. Removing a share takes it off the list and leaves her copy.
- [ ] AC-10: The M4 writes `controlledBy: {environmentId, label}` into the grant record on the controlled machine. Its app then shows "This Mac is managed by {label}. Work it starts here shows in your threads with 'From {label}'." and marks shared projects "Shared by {label}". If she deletes the field, the banner goes and nothing else changes (tamper-evident only). The M4 adds no other machine to her fleet list.
- [ ] AC-11: The M4 checks its key on each controlled machine at least every 5 minutes, separately from nickname sync. When a check fails with a revoked or unknown credential before the key's expiry (expiry and team-rules holds are told apart locally), the M4 shows "{label} stopped accepting {M4}'s key. Last worked {time}." on the machine card and as one notice in the M4's app. A test covers each outcome: revoked, expired, team-rules hold and offline.
- [ ] AC-12: New strings go through the translation function with entries for each shipped language. Quoted texts match the built ones. Two wire tests run against 1.0.343 as the oldest supported build. In the first, an older client receiving `controlled_machine` shows the server's text. In the second, the new build writes `studio-fleet-roles.json`, the owner-device side file and the grant with `controlledBy`, and 1.0.343 then reads the fleet file, the device list and the grant unchanged. Sharing or launching on a controlled machine below the minimum build says "Update {machine} first".

## Approach

1. **Session kinds first (AC-01).** Thread the session subject into `RpcAuthorization.layer` from `EnvironmentAuth.ts`. Add the owner-device side file beside the 1327 device list, with absent meaning yes. Make it a question on the approval card.
2. **Role store (AC-02).** `apps/server/src/fleet/controlledMachines.ts` owns `studio-fleet-roles.json`. It fails closed, keys by environment ID and is written before the fleet entry. The fleet *file* format in `apps/server/src/studioFleet.ts` stays unchanged, because strict keys there would make older builds drop the entry. The *snapshot* type in `packages/contracts/src/studioFleet.ts` gains an optional `role`.
3. **Spread (AC-03).** A management RPC sends the controlled environment IDs and reported keys to each own machine the M4 manages. Each machine stores them in its own role file.
4. **Guard (AC-04, AC-05, AC-06).** `assertNotControlled(environmentId, action)` is called from every refuse row of the handler table. Reported keys feed a deny list checked at the CloudLink mint and in `refuseUnapprovedDevice`. The transition runs the revocations once and records them.
5. **Reported keys (AC-05).** The controlled machine's app reports its Connect key thumbprint to its own server (new RPC), which forwards it to the management key holder on join and on change. This is best effort, and the spec does not rely on it.
6. **Outbound and inbound filters (AC-07).** Changes go in `MachineNicknameSync.ts` (both directions), `cli/fleet.ts`, the folder-transfer and file-transfer entry points, and the sealed-secrets steps.
7. **Grant (AC-08).** `workGrantPolicy.ts` and `WorkGrants.ts` take the role. The controlled machine writes the narrow grant when the management key asks, and a missing record reads as no access.
8. **Share (AC-09).** A new `link: false` path in `addToMachine.ts` (new work: today linking is the separate `linkCopy` step at `:478-487`) uses an export selection with the denylist instead of `DEFAULT_SELECTION`.
9. **Notice and probe (AC-10, AC-11).** Add a `controlledBy` field to the grant record and a probe loop in `controlledMachines.ts`.

Rejected:
- **A child Connect account linked to Anton's.** It needs relay identity and billing work, and a join line across accounts already gives the one-way shape.
- **A per-session visibility filter on the M4's projections.** It would touch every projection, and refusing the session is stricter.
- **Identifying her machine by an environment ID the client reports.** A client can spoof it or leave it out.
- **Running SpecWithCode under a separate admin macOS user.** Her app could no longer show the shared project, and launchd agents need that user logged in.

Risks:
- Own machines that the M4 does not manage, or that run builds older than 1.0.343, are not protected. AC-03 lists them.
- A key her Mac does not report (a browser, a reset app, a modified build) is caught only by Anton's credentials and the approval warning (AC-05).
- If her Mac is signed in to Anton's provider account, his claude.ai connectors (Gmail, Drive, Calendar, Slack) are reachable from her Mac whatever this increment does (D-06).
- AC-01 changes auth on every machine. It ships with the absent-means-owner rule and its own review.

## Decisions

### Asked
- none (Anton's acceptance of this spec is the gate; nothing is built before it)
### Defaulted (change any before sw-do)
- D-01 Identity → the role keys on the machine (environment ID, plus best-effort reported device keys), not on a person or a child Connect account. Her Mac uses her own Connect account, or none.
- D-02 Shared project → an unlinked export with the AC-09 denylist; `.git` off by default.
- D-03 Tamper-evident, not tamper-proof: she can stop the M4, and the M4 notices within 5 minutes (AC-11).
- D-04 AC-01 ships in this increment, because the role change and the controlled refusals depend on it. Devices with no flag stay owner devices.
- D-05 Reviewer → Muse Wonderful (`muse-wonder-full-1.0`) at xhigh, as the task asked. Round 1 findings are folded in here (`reports/review-response.md`). A second round on this rewrite is the first gate after Anton accepts the direction, before any code.
- D-06 Her Mac uses her own provider sign-ins or an API key, never Anton's claude.ai account. The share dialog shows the account label of each provider instance it lists.
- D-07 Agent-started file transfer and folder copy to a controlled machine need the owner's card; sealed secrets to it are refused outright.
### Open
- none

## Tasks

### T-01 Session kinds and owner devices for owner-only RPCs
- AC: AC-01, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/SessionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ownerDevices.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/RpcAuthorization.test.ts apps/server/src/fleet/ownerDevices.test.ts

### T-02 Role store, add dialog and spread to managed machines
- AC: AC-02, AC-03, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/controlledMachines.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/studioFleet.ts, repositories/anton-abyzov/specwithcode/apps/server/src/studioFleet.ts, repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetJoin.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/FleetTargets.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/phoneLinks.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StudioFleetConnections.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/controlledMachines.test.ts

### T-03 Handler table, guards, reported keys and the transition
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/addToMachine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayRunner.ts, repositories/anton-abyzov/specwithcode/apps/server/src/away/AwayIntents.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/fleet.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/pair.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ConnectBothWays.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, .specweave/increments/1388-controlled-family-machine-with-one-shared-project/reports/handler-table.md | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/controlledMachines.guard.test.ts

### T-04 Nothing flows that should not: nickname, skills, transfers, secrets
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/MachineNicknameSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/fleet.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fileTransfer/, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/MachineNicknameSync.test.ts apps/server/src/fleet/controlledMachines.flows.test.ts

### T-05 Narrow grant and unlinked project export
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/workGrantPolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/WorkGrants.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/addToMachine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/classify.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/shareToControlled.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/workGrantPolicy.test.ts apps/server/src/fleet/shareToControlled.test.ts

### T-06 Managed notice on the controlled machine and key probe on the M4
- AC: AC-10, AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/controlledMachines.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/WorkGrants.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/controlledMachines.probe.test.ts

### T-07 Verify, review at the exact head, close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12 | Files: .specweave/increments/1388-controlled-family-machine-with-one-shared-project/reports/ | Test: specweave verify 1388-controlled-family-machine-with-one-shared-project
