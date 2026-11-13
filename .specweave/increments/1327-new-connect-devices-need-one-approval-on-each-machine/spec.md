# New Connect devices need one approval on each machine

## Problem

Any device signed in to the owner's SpecWithCode Connect account gets terminal, file write, settings, provider and update access on every linked machine, with no consent on the machine itself (Muse review XM-01, critical; `../1326-cross-machine-actions-name-who-acts-servers-refuse-ungranted-destinations-new-devices-need-approval/reports/muse-security-review.md`). A stolen Connect session or one compromised device controls every machine. Evidence: `apps/server/src/cloud/CloudLink.ts:1818` mints `AuthStandardClientScopes` for any device key the account presents; `packages/contracts/src/auth.ts:224`.

Anton, November 13, 2026: keep Connect as the one sign-in and full control between his machines, but if this is a real security concern add a clean, easy approval pop-up on the machine. It is real (XM-01), so this ships.

Design review: `../1326-…/reports/muse-design-review.md` (B-01 to B-11, X-01, X-03, X-04). This spec folds in its fixes.

## Scope

In: per-machine approval of each new human device key (subject `cloud-connect`, and phones paired through a hub, subject `phone-link:`), enforced at one point every session passes (HTTP, WebSocket ticket, browser cookie, MCP); a pop-up on the machine where the owner types the code shown on the new device; a device list with Remove; devices in use at the update kept but listed for review; local app recovery; a capability flag so Settings shows which machines enforce it.

Out: changing Connect sign-in or the relay; machine-to-machine sessions (`mcp-client` worker grants, `fleet-invitation`), which already pass fleet invitation and grants; per-move consent (accepted risk, below).

Accepted risk (X-01): an approved device keeps full control, including moving projects between machines and adding a machine through account join. That is the owner's model; approval is the gate.

## Acceptance Criteria

- [ ] AC-01: A human device key this machine has not approved gets no access on any route (HTTP, WebSocket, hosted web app, MCP, handoff, folder transfer): it is refused with a stable code `device_not_approved` and "Waiting for approval on {machine}. Code {CODE}."; an open socket closes within 10 seconds of the device being removed.
- [ ] AC-02: The refused device shows a 6-character code (31-character alphabet, random per request, about 30 bits). The machine's own app shows a pop-up "A new device wants to use {machine}. Type the code shown on it." with a code box, Allow and Deny. Allow with the right code lets the device in on its next attempt, which the client makes on its own; Deny refuses that key for 24 hours.
- [ ] AC-03: Pending requests are one per device key, expire after 10 minutes, survive a restart, and are capped at 3 per account address and 20 overall; a denied key gets no new pairing credential; refusals count in the failure limiter under their own budget.
- [ ] AC-04: Approving needs the machine's local owner session, or an already approved device that types the same code; the asking device cannot approve itself (negative test). Each approval records who approved it and when, and the machine's other approved devices get one notice: "New device approved on {machine} by {approver}."
- [ ] AC-05: Settings > Machines lists the devices that can use this machine (name, kind, approved when, approved by) with Remove; Remove ends that key's sessions at once and only that key's. Devices kept by the update show "Kept by the update. Check this list." until the owner confirms the list once.
- [ ] AC-06: The local desktop app and local CLI on the machine always work and can always approve, even when the trust store is missing or corrupt (that case shows a banner and refuses remote devices until repaired).
- [ ] AC-07: A worker grant over Connect, a remote thread and an already approved phone keep working while a new phone is pending (regression test).
- [ ] AC-08: Machines report support in their environment descriptor; Settings shows "This machine does not ask before new devices connect yet" for machines that do not.

## Approach

1. One choke point (B-01): a `DeviceTrust` check inside session verification that HTTP, WebSocket ticket, browser cookie and `authenticateMcpClient` all call. Carry `proofKeyThumbprint` into the browser-cookie session (`EnvironmentAuth.ts:896`, relax the no-thumbprint rule at `:1475` for Connect-born cookies) and the ticket session (`:1351`). Applies to subjects `cloud-connect` and `phone-link:`; `mcp-client` and `fleet-invitation` are exempt and tested as such (B-11). Phone-link sessions are keyed by the phone's own key, so the hub cannot fan a phone out without each machine's approval (B-08).
2. Codes (B-04, X-04): reuse `DeviceSignInRequests` (6 characters, `23456789ABCDEFGHJKMNPQRSTUVWXYZ`, random, hashed). The pop-up is a prompt to type, not a list to match, so a look-alike request cannot be approved by a click and codes cannot be ground offline.
3. Spam (B-05): create the pending request at pairing-credential mint (`CloudLink.ts:1818`), dedupe by thumbprint, 10 minute expiry, per-account and global caps, refuse mint for denied keys, and count refusals in `CredentialFailureLimiter` under a separate budget (today `:235` exempts anything with `teamRulesMessage`).
4. Who may approve (B-02, B-06): a server-side caller test, not a scope: local owner session, or a session whose thumbprint is approved here and which supplies the code. Record `approvedBy`; notify other approved devices (X-03).
5. Update (B-03): keep keys of `cloud-connect` sessions active at first start, marked `keptByUpdate`, listed with the banner until confirmed; no silent permanent grant.
6. Store (B-10): JSON beside `work-grants.json`, written like `WorkGrants.ts:296` (temp file, 0600, fsync, rename) under a semaphore (`:344`); corrupt store means remote devices refused with a banner, local owner unaffected.
7. Clients (B-07, B-09): refusal carries `device_not_approved` plus text in both the session-state answer and error bodies; desktop, web and iOS show "Approve this device on {machine}. Code {CODE}." and retry on their own every few seconds instead of telling the owner to re-pair. Recovery when the only device is away: the existing device sign-in typed into any approved session, or the machine's local app.
8. Settings (A-11): one card layout shared with 1326: "Devices that can use this machine" (people), then the two agent rows, then projects.

Rejected: gating the app by fleet work grants (Anton: grants stay about agents); a listed pop-up with a matching 4-character code (grindable, spam-prone; review B-04, B-05).

## Decisions

### Asked
- D-01 Approval for Connect devices → yes, one easy pop-up per new device per machine (Anton, November 13, 2026: "if this is a real security concern, then go ahead").
### Defaulted (change any before sw-do)
- D-02 Approve from the machine's own app with one code entry, or from an already approved device with the same code (not a click).
- D-03 Keep devices in use at the update, flagged for one review.
- D-04 Phones paired through a hub need approval on each machine too.
- D-05 Approved devices keep full control including project moves (accepted risk X-01).
### Open
- none

## Tasks

### T-01 Server trust store, choke point, refusal and socket close
- AC: AC-01, AC-03, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/phoneLinks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/ConnectDeviceTrust src/auth

### T-02 Approval RPCs, code entry pop-up and client retry
- AC: AC-02, AC-04, AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/, repositories/anton-abyzov/specwithcode/apps/web/src/components/, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCTransport/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings

### T-03 Device list with Remove and update review banner
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings

### T-04 Verify and close 1327
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: .specweave/increments/1327-new-connect-devices-need-one-approval-on-each-machine/ | Test: specweave verify 1327
