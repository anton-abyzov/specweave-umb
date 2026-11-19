# New Connect devices need one approval on each machine

## Problem

Any device signed in to the owner's SpecWithCode Connect account gets terminal, file write, settings, provider and update access on every linked machine, with no consent on the machine itself (Muse review XM-01, critical; `../1326-cross-machine-actions-name-who-acts-servers-refuse-ungranted-destinations-new-devices-need-approval/reports/muse-security-review.md`). A stolen Connect session or one compromised device controls every machine. Evidence: `apps/server/src/cloud/CloudLink.ts:1818` mints `AuthStandardClientScopes` for any device key the account presents; `packages/contracts/src/auth.ts:224`.

Anton, November 13, 2026: keep Connect as the one sign-in and full control between his machines, but if this is a real security concern add a clean, easy approval pop-up on the machine. It is real (XM-01), so this ships.

Design review: `../1326-…/reports/muse-design-review.md` (B-01 to B-11, X-01, X-03, X-04). This spec folds in its fixes.

November 17, 2026: the M5 joined on November 16 with nothing accepted on M4, because the two pull requests (#361, #362) were never merged. Two reviews of the unmerged branches (`../../reports/threads/2026-11-17-new-machine-trust-flow-what-m4-accepts-when-the-5e1014-6af327.md`, `reports/2026-11-17-second-stage-review-new-machine-trust.md`) found four gaps in them: the code never shows during first run, every device is named "SpecWithCode Connect connect", iOS was left out, and the join card says less than Allow gives. Anton accepted one code typed on the main machine during a join and asked to ship it. AC-09 to AC-15 and T-05 to T-11 cover that.

## Scope

In: per-machine approval of each new human device key (subject `cloud-connect`, and phones paired through a hub, subject `phone-link:`), enforced at one point every session passes (HTTP, WebSocket ticket, browser cookie, MCP); a pop-up on the machine where the owner types the code shown on the new device; a device list with Remove; devices in use at the update kept but listed for review; local app recovery; a capability flag so Settings shows which machines enforce it. Added November 17: the code visible in first run and on the join card; each device's own name, system and first seen; honest wording on the join card and the joined notice; translated views; an iPhone that waits and retries; the release and rollout.

Out: changing Connect sign-in or the relay; machine-to-machine sessions (`mcp-client` worker grants, `fleet-invitation`), which already pass fleet invitation and grants; per-move consent (accepted risk, below); the management key's scopes and lifetime, machines that already joined, the shared waiting cap and the computer-use host role (D-08).

Accepted risk (X-01): an approved device keeps full control, including moving projects between machines and adding a machine through account join. That is the owner's model; approval is the gate.

## Acceptance Criteria

- [x] AC-01: A human device key this machine has not approved gets no access on any route (HTTP, WebSocket, hosted web app, MCP, handoff, folder transfer): it is refused with a stable code `device_not_approved` and "Open SpecWithCode on {machine} and type this code: {CODE}"; an open socket closes within 10 seconds of the device being removed.
- [x] AC-02: The refused device shows a 6-character code (31-character alphabet, random per request, about 30 bits). The machine's own app shows a pop-up "A new device wants to use {machine}. Type the code shown on it." with a code box, Allow and Deny. Allow with the right code lets the device in on its next attempt, which the client makes on its own; Deny refuses that key for 24 hours.
- [x] AC-03: Pending requests are one per device key, expire after 10 minutes, survive a restart, and are capped at 3 per account address and 20 overall; a denied key gets no new pairing credential; refusals count in the failure limiter under their own budget.
- [x] AC-04: Approving needs the machine's local owner session, or an already approved device that types the same code; the asking device cannot approve itself (negative test). Each approval records who approved it and when, and the machine's other approved devices get one notice: "New device approved on {machine} by {approver}."
- [x] AC-05: Settings > Machines lists the devices that can use this machine (name, kind, approved when, approved by) with Remove; Remove ends that key's sessions at once and only that key's. Devices kept by the update show "Kept by the update. Check this list." until the owner confirms the list once.
- [x] AC-06: The local desktop app and local CLI on the machine always work and can always approve, even when the trust store is missing or corrupt (that case shows a banner and refuses remote devices until repaired).
- [x] AC-07: A worker grant over Connect, a remote thread and an already approved phone keep working while a new phone is pending (regression test).
- [x] AC-08: Machines report support in their environment descriptor; Settings shows "This machine does not ask before new devices connect yet" for machines that do not.
- [x] AC-09: A device waiting for approval shows the code wherever it waits, first run included. On `/welcome` the join card shows "Open SpecWithCode on {machine} and type this code:" with the code for the picked main machine, not "Connect to {machine} first."; it keeps asking on its own and enables Allow once approved, without leaving first run.
- [x] AC-10: A request, a listed device and a kept-by-update row each show the device's own name, its system and app (with the version when known) and when it was first seen. A client that sends no name is named from what its session already records (device type, system, browser or app version); the fixed text "SpecWithCode Connect connect" never appears. The name is the device's own word: the pop-up says so, and the typed code stays the only thing that approves.
- [x] AC-11: The pop-up names the Connect account the device signed in with (this machine's own account, with its address when the app knows it; the hub machine for a phone paired through a hub) and says what Allow gives: terminals, files, settings and sign-ins, and starting work on {machine}.
- [x] AC-12: The join card's "Management key" row names terminals, files, settings and sign-ins for a year; its "Secrets" row says the approval card appears on the machine that asks, not on this one; the "{label} joined" notice says the new machine's app can use this machine because it was approved here. No promise on the card is wider than the code.
- [x] AC-13: Every string in the device approval views, and the refusal text the server sends, goes through the app's translation function (1243) with entries for each shipped language, and the texts quoted in this spec match the built ones.
- [x] AC-14: A new iPhone or iPad waiting for approval shows the machine and the code and retries on its own, not a team rules error. It ships with the next iOS build; the desktop release does not wait for it (D-09).
- [x] AC-15: Shipping this locks nobody out by mistake. The fleet update over Connect, worker grants, management keys, the release walkers and the installed checks use sessions the gate exempts or local sessions, proven by a trace of each path and a test; the first-run setup walkers still pass.

## Approach

1. One choke point (B-01): a `DeviceTrust` check inside session verification that HTTP, WebSocket ticket, browser cookie and `authenticateMcpClient` all call. Carry `proofKeyThumbprint` into the browser-cookie session (`EnvironmentAuth.ts:896`, relax the no-thumbprint rule at `:1475` for Connect-born cookies) and the ticket session (`:1351`). Applies to subjects `cloud-connect` and `phone-link:`; `mcp-client` and `fleet-invitation` are exempt and tested as such (B-11). Phone-link sessions are keyed by the phone's own key, so the hub cannot fan a phone out without each machine's approval (B-08).
2. Codes (B-04, X-04): reuse `DeviceSignInRequests` (6 characters, `23456789ABCDEFGHJKMNPQRSTUVWXYZ`, random, hashed). The pop-up is a prompt to type, not a list to match, so a look-alike request cannot be approved by a click and codes cannot be ground offline.
3. Spam (B-05): create the pending request at pairing-credential mint (`CloudLink.ts:1818`), dedupe by thumbprint, 10 minute expiry, per-account and global caps, refuse mint for denied keys, and count refusals in `CredentialFailureLimiter` under a separate budget (today `:235` exempts anything with `teamRulesMessage`).
4. Who may approve (B-02, B-06): a server-side caller test, not a scope: local owner session, or a session whose thumbprint is approved here and which supplies the code. Record `approvedBy`; notify other approved devices (X-03).
5. Update (B-03): keep keys of `cloud-connect` sessions active at first start, marked `keptByUpdate`, listed with the banner until confirmed; no silent permanent grant.
6. Store (B-10): JSON beside `work-grants.json`, written like `WorkGrants.ts:296` (temp file, 0600, fsync, rename) under a semaphore (`:344`); corrupt store means remote devices refused with a banner, local owner unaffected.
7. Clients (B-07, B-09): refusal carries `device_not_approved` plus text in both the session-state answer and error bodies; desktop, web and iOS show "Approve this device on {machine}. Code {CODE}." and retry on their own every few seconds instead of telling the owner to re-pair. Recovery when the only device is away: the existing device sign-in typed into any approved session, or the machine's local app.
8. Settings (A-11): one card layout shared with 1326: "Devices that can use this machine" (people), then the two agent rows, then projects.
9. First run (AC-09): the waiting card host sits only inside `FirstRunGate` in `apps/web/src/routes/__root.tsx`; the `/welcome` route returns its own tree without it. Mount it there, and give `AccountJoinCard` and `IncomingWorkerSetup` a waiting state read from the picked machine's `connection.deviceApprovalCode`. No wizard step is added, but check every setup walker anyway (`grep -rln "Do not import projects" scripts apps/web/tests`); PR CI does not run them.
10. Names (AC-10, AC-11): the desktop app, the web app and the phone send a device name with the session they open, beside the device type and app version they already send. The device entry stores name, device type, system, app and first seen, and never takes the pairing link's label (`CloudLink.ts` sets "SpecWithCode Connect connect" for every device). Kept rows and nameless clients are named from the `auth_sessions` client fields. The relay does not change.
11. One branch (T-05): rebase both pull requests onto `main` as one branch on #361, so the refusal never ships without the pop-up; use migration 075 only if it is still free; bind 1365's sealed secret copy to the device like the other transfers.
12. Deploy path (AC-15): before merge, trace the session subject used by the fleet update over Connect, the `release.sh` walkers and the installed checks. Only `cloud-connect` and `phone-link:` are gated.
13. Rollout: kept-by-update is one snapshot at each machine's first start after the update. Before the rollout, tell the owner which devices each machine keeps, and that any other device shows a code to type on that machine's own app or in a window that machine already approved.

Rejected: gating the app by fleet work grants (Anton: grants stay about agents); a listed pop-up with a matching 4-character code (grindable, spam-prone; review B-04, B-05).

## Decisions

### Asked
- D-01 Approval for Connect devices → yes, one easy pop-up per new device per machine (Anton, November 13, 2026: "if this is a real security concern, then go ahead").
- D-06 Account join and device approval → the join is not exempt: the main machine types the new machine's code once (Anton, November 17, 2026: "yes I accept it, implement it fully").
- D-07 Adversarial reviewer → Meta Muse Wonder Full (`muse-wonder-full-1.0`, max effort) at the exact head before merge, and again after verify (Anton, November 17, 2026: "use meta muse wonderful as adversarial review").
### Defaulted (change any before sw-do)
- D-02 Approve from the machine's own app with one code entry, or from an already approved device with the same code (not a click).
- D-03 Keep devices in use at the update, flagged for one review.
- D-04 Phones paired through a hub need approval on each machine too.
- D-05 Approved devices keep full control including project moves (accepted risk X-01).
- D-08 Left out and recorded, each for its own increment: the management key's scopes and one-year life; machines that already joined through the account; the computer-use host role going to the newest subscriber; the waiting cap of 3 shared by every Connect device (a stolen sign-in can keep it full, and ending that sign-in is the cure).
- D-09 iPhone support ships on the iOS track and does not hold the desktop release. Until it does, a new iPhone shows the code inside a team rules error and is retried by hand.
- D-10 The device name is the device's own claim, shown as a hint. Approval stays tied to the typed code.
- D-11 Approving or removing a device on an installed machine is Anton's step. Agents verify with tests, fixtures, a private copy of the installed build and read-only checks.
### Open
- none

## Tasks

### T-01 Server trust store, choke point, refusal and socket close
- AC: AC-01, AC-03, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/phoneLinks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/ConnectDeviceTrust src/auth

### T-02 Approval RPCs, code entry pop-up and client retry
- AC: AC-02, AC-04, AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/, repositories/anton-abyzov/specwithcode/apps/web/src/components/, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCTransport/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings

### T-03 Device list with Remove and update review banner
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings

### T-05 One branch on current main, with sealed secret copies bound to the device
- AC: AC-01, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/, repositories/anton-abyzov/specwithcode/apps/server/src/persistence/Migrations/, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/ | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet src/auth

### T-06 Show the code in first run and on the join card
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/routes/__root.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/onboarding src/components/settings

### T-07 Name each device: its own name, system, app and first seen
- AC: AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/, repositories/anton-abyzov/specwithcode/packages/contracts/src/connectDevices.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/, repositories/anton-abyzov/specwithcode/apps/web/src/studio/ | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/ConnectDeviceTrust src/auth

### T-08 Say what Allow gives, and translate the views
- AC: AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings src/components/devices src/themeContrastClasses.test.ts

### T-09 iPhone waits with the code and retries
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCTransport/, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/ | Test: cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test

### T-10 Prove the rollout and the setup walkers are not gated
- AC: AC-15 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-fleet/, repositories/anton-abyzov/specwithcode/scripts/desktop-e2e/, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/ConnectDeviceTrust

### T-11 Review, merge, release, roll out and read back
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-15 | Files: .specweave/increments/1327-new-connect-devices-need-one-approval-on-each-machine/reports/ | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released <merge commit>

### T-04 Verify and close 1327
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15 | Files: .specweave/increments/1327-new-connect-devices-need-one-approval-on-each-machine/ | Test: specweave verify 1327
