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

In: the join on the new machine, the joined notice on the other machine, the device pop-up's wording, the first-run machine row's wording, and, after Anton decides, the second code and the reverse agent grant.

Out: the relay, the iPhone, Team rules, joins through a join line with another account (1388), and 1390's Sync, Add and Hand off themselves.

Lanes. `[label]` changes only what is shown and ships after review and green CI. `[access]` changes who gets access and waits for Anton's acceptance and a Muse Wonderful review.

## Acceptance Criteria

- [ ] AC-01 [label]: The device pop-up says what Allow adds and that letting a machine's agents run work is separate: Allow lets the SpecWithCode app on that device open this machine (chats, terminals, files, settings, sign-ins). No reassurance keys on the device's own name; the line that the name is the device's own word stays.
- [ ] AC-02 [label]: The joined notice on the machine that was joined says the join is one way: its agents can run work on the new machine and its app can open it; the new machine cannot use this machine. It offers Allow for the reverse direction (D-02), which nothing grants by itself.
- [ ] AC-03 [label]: The Allow on the new machine says what it covers: the other machine's agents may run work here and its SpecWithCode app may open this machine, with no second code; this machine gets no access to the other one.
- [ ] AC-09 [label]: The join's done card names the next step with 1390's verbs (Add a project to this machine) instead of sending the owner to the other machine's Settings.
- [ ] AC-04 [label]: First run names no main machine: the row reads as joining one of your machines (wording agreed with the 1390 owner so join, Sync and Hand off read as one concept).
- [ ] AC-05 [access]: After a join, the app that typed the new machine's code on the joined machine opens the new machine with no second code and no pop-up: the joined machine vouches for that app with the credential the join gave it, and the new machine checks that proof. No other device gets a vouch. It applies only when the grant the Allow gave is full access to all projects; a capped or project-limited grant, an older machine on either side, or a request without a valid proof falls back to the code. Remove and revoking the grant end it. (D-01)
- [ ] AC-06 [access]: A join grants agents one way only. The reverse is offered on the joined machine (AC-02) and set up only by the owner's Allow there. (D-02)
- [ ] AC-10 [access]: The code typed on the joined machine lets the new machine join and hand over its line; it gives the new machine's app no lasting access to the joined machine. A machine joined before this change keeps what it has until the owner removes it. (D-03)
- [ ] AC-07 [label]: Every new string goes through the translation function with entries for the eight shipped languages.
- [ ] AC-08 [label]: Checked after release with two real machines by Anton: the join's screens, then what each machine can open and run on the other.

## Decisions

- D-01 [access] Should the join stop asking for the second code? → Drop it; Allow covers it, and the Allow says so (Anton, November 19, 2026: "drop it. I think allow covers it, but just explain this"). Built as AC-05 and AC-03.
  Options weighed for Anton's "a code sounds tricky" (November 19): a one-click Allow for any device signed in to the same account would drop the guarantee the code gives, because a stolen sign-in is also the same account and the name is the device's own word (why 1327 kept the code, November 17). Comparing a code shown on both screens and clicking Allow is lighter but easier to click through. What keeps the guarantee and drops the typing is proof from a machine already trusted: the joined machine vouches for its own app with the credential the join gave it, which an attacker with only a sign-in does not have. So one typed code stays per new machine, and every later prompt between the two machines is covered by that proof.
- D-02 [access] Should a join let agents run work both ways? → One way; offer the reverse (Anton, November 19, 2026). Built as AC-06 and AC-02.
- D-03 [access] Should the code typed on the joined machine give the new machine's app access to it? → No, the code only joins (Anton, November 19, 2026, card answer "Yes, the code only joins"). Anton, November 19, 2026, on "Your first code let Windows's app into M5": "I think this Windows machine has no access to M5. I never intended this to be, or maybe I interpreted it wrong." It does today: M5's records show Windows's app approved at 9:54:29 AM with a live session, and photo 3 shows Windows listing M5's projects through it. Today that code approves the new machine's app as a full device on the joined machine (1327), because its app hands the join line over through that session (`accountJoinFleetWorkers`). Built as AC-10; replaces the November 17 reading in `decision_machine_join_flow` that the code is an ordinary device approval.

## Approach

D-01's vouch reverses a property project memory lists as sound ("A management key cannot approve devices itself"), within the bounds of AC-05; the design note and the review name it. It widens nothing only while the grant is full access to all projects, hence AC-05's condition. Which key the vouch names is not settled: read `apps/web/src/cloud/managedRelayLayer.ts` and the `relay.connection.deviceIdentity.resolve` span first, because a server does not obviously know the proof key of the app that typed a code (the local desktop app may approve over its local session). Design note and a Muse Wonderful design review come before code; tests fail first. T-07's strings ship together with T-03 and T-08, never ahead, since they are false before.


Wording first (AC-01 to AC-04, AC-07), then D-01 and D-02 as decided. Each side words only what it knows for certain: a window knows which machine it waits on, and a machine knows which machine it just allowed. A device request carries no machine identity (`packages/contracts/src/connectDevices.ts`), so the pop-up never claims "this is M5".

### Design

Design only, written November 19, 2026, round 2 the same day. Code was read at `origin/main` `c924fa8340` of `repositories/anton-abyzov/specwithcode` (PR 712 merged; the files cited are unchanged since `3eafbca0c9`). `D/` is `apps/desktop/src/`. Path prefixes: `S/` is `apps/server/src/`, `W/` is `apps/web/src/`, `C/` is `packages/contracts/src/`, `R/` is `packages/client-runtime/src/`. J is the joined machine (M5), N is the new machine (Windows).

#### Facts the design rests on

- Order today: N's app picks J, which opens J over the relay at once (`W/components/settings/AccountJoinCard.tsx:235-262`). J has not approved N's app, so N shows J's code where Allow would be (`W/components/settings/IncomingWorkerSetup.tsx:258-263`). The code is typed on J before Allow, not after. Allow then mints N's line on N and posts it to J (`W/studio/fleet.ts:404-426`).
- A device is its relay proof key, `jkt:<thumbprint>` (`S/fleet/ConnectDeviceTrust.ts:126`, `:162-171`). The code approves that key as a full device: `approve` writes a `DeviceRecord` (`:993-1040`), and every later session of the key passes the gate (`:912-913`, `S/auth/EnvironmentAuth.ts:642-665`).
- `accountJoinFleetWorkers` needs only `orchestration:operate` and a Connect subject (`S/studioFleetHttp.ts:777-821`). It has no join-specific approval; it relies on the device gate above.
- Scopes cannot make a session join-only. Of 60 authenticated HTTP endpoints, 8 check no scope: the websocket ticket (`S/auth/http.ts:650-663`) and the six `connect-devices` routes, where an approved device is an approver whatever its scopes (`S/auth/connectDevicesHttp.ts:40-61`). `orchestration:operate` alone also opens `/ws` RPCs and project changes.
- The join gives J two credentials on N: a management token (subject `fleet-invitation`, coordinator principal J, Standard scopes plus `access:write`, bound to J's fleet key, 365 days, never renewed; `S/studioFleetHttp.ts:614-693`, `S/fleet/fleetRedemption.ts:24-29`) and a worker grant (subject `mcp-client`, 30 days, renewed; `S/fleet/workerGrantMint.ts:348-395`). Neither can approve devices today (`S/auth/connectDevicesHttp.ts:28-31`, `:51-52`).
- J's server never sees its own app's proof key. The local app signs in with a bearer or a cookie, and the approver is recorded as `key: null`, "this machine" (`S/auth/connectDevicesHttp.ts:58-60`). The key lives in the app's IndexedDB (`studio:cloud-auth`, id `relay-dpop-proof-key`, private half not extractable; `W/cloud/dpop.ts:24-27`, `:135`), one per install and OS user, shared by its windows. It is used only towards other machines (`W/cloud/managedRelayLayer.ts:16-37`). The span `relay.connection.deviceIdentity.resolve` (`R/authorization/service.ts:423-425`) resolves a relay device ID that the web and desktop app never send (`W/connection/platform.ts:341-343`); it does not name the key.
- N does not bound the grant's access level. J sends the level it wants at mint (`S/fleet/workerGrantMint.ts:277`), N copies it into the session (`S/auth/McpOAuth.ts:613-623`, `S/auth/EnvironmentAuth.ts:1654-1656`), and the level lives only in the signed token (`S/auth/SessionStore.ts:575-587`, claim `rtc`). The owner's choice in the Allow card is sent to J and never stored on N. `runtimeCap` in `work-grants.json` is copied from the caller's token on its first `/mcp` call (`S/fleet/WorkGrants.ts:519-523`). Project and account limits are different: only N's owner can change them (`S/studioFleetHttp.ts:227-241`, `:447-455`).
- Stop on N revokes every session of coordinator J, the management token included, and Restore does not bring it back (`S/fleet/WorkGrants.ts:650-665`, `S/persistence/AuthSessions.ts:317-341`). Remove on J revokes the management token on N (`S/studioFleetJoin.ts:586-639`).
- Older builds drop unknown keys on decode (Effect's default) and lose them on the next write. `connect-devices.json` is decoded that way (`S/fleet/ConnectDeviceTrust.ts:327-343`). Exact input structs refuse unknown keys with an empty 400: approve (`C/connectDevices.ts:11-17`, `:101`) and account-join (`C/studioFleet.ts:124-127`, `:158-161`). `/oauth/token` ignores unknown form fields (`C/auth.ts:323-332`). The descriptor is readable with no credential and the client reads it before the token exchange (`C/environmentHttp.ts:722-726`, `R/authorization/service.ts:454-463`).

- The window that opened N by itself is `W/cloud/GrantedAccountMachines.tsx:253-256` (selection in `W/studio/grantedAccountMachines.ts:30-77`): it saves a Connect route for each account machine that granted this one. `AutoConnectPrivateMachines.tsx` and `fleetAutoConnect.ts` are the Tailscale path (`W/studio/fleetAutoConnect.ts:155-161`, `:180`) and did not act in this join. The Problem table and `reports/evidence.md` now say so.
- "Owner" in `deviceApprover` is not "the app on this machine". Any session with `access:write` and a device principal counts (`S/auth/connectDevicesHttp.ts:58-60`), and a window on another machine can hold one: a pairing code made on J with "Manage access" ticked and redeemed there, the startup link of a web-mode server, or a token from `auth session issue`. The fleet's own "Connect machine" codes do not count, because they carry a coordinator principal (`S/studioFleet.ts:523-531`, `S/auth/http.ts:725-728`). Such a window reaches J over Tailscale, the LAN or an SSH tunnel, so "not over Connect" does not single out J's app either: `arrivedOverConnect` reads headers only and is documented as a reason to refuse, never to grant (`S/auth/CredentialFailureLimiter.ts:158-170`, `S/fleet/fleetOrigin.ts:70-74`). The peer address does not help: Tailscale Serve, the Connect tunnel and an SSH tunnel all arrive from loopback.
- What does mark J's own app: the session subject `desktop-bootstrap`. The server gives it only for a token derived from a secret the desktop app passes to the server it starts, over a private channel (`S/auth/PairingGrantStore.ts:545-553`, `packages/shared/src/desktopBootstrapToken.ts:4-8`); the exchange copies the subject into the session (`S/auth/EnvironmentAuth.ts:1129-1134`), and the pairing route can only ever mint `one-time-token` (`:1356-1360`). When the app instead attaches to an installed service, nothing marks it today: it pairs through the service's command line and gets `one-time-token` with a device principal and a label anyone can choose (`D/backend/localServiceAttach.ts:352-362`, `S/cli/pair.ts:268-281`), the same shape as a code redeemed on another machine.

#### 1. D-03: the code approves the join only

**Who declares it.** N's app, in the token exchange on J: a new optional form field `client_purpose=join` on `POST /oauth/token` (`S/auth/http.ts:571-649`). Nothing changes at the relay, which is out of scope. N sends it only when J's descriptor carries the new capability `deviceJoinApproval`; an older J would ignore the field and approve a full device, so against an older J the new N uses today's flow and today's words.

**What the server enforces.** The claim can only narrow, so it needs no proof.

- The session J issues carries a signed claim `pur: "join"` (a new optional key in `SessionClaims`, `S/auth/SessionStore.ts:575-587`) and one scope, the new `fleet:join`, which maps to no RPC, like `fleet:update` (`C/auth.ts:102-113`). `DeviceSessionFacts` (`S/fleet/ConnectDeviceTrust.ts:91-102`) gains `purpose`.
- A waiting request has a kind. The entry is first written at the relay mint from the thumbprint alone (`S/cloud/CloudLink.ts:1820-1825`) with kind "device". The kind becomes "join" when a join session asks (`ensureWaiting`, `S/fleet/ConnectDeviceTrust.ts:744-812`). The code is only ever revealed to a session (`:920-925`), so the kind is set before the code can be read. A later relay mint for the same key (`refuseAtMint`, `:933-949`) never changes an existing request's kind or code. If a session of the other kind asks for the same key, the kind changes and the code is replaced: a code approves exactly the kind it was shown with.
- `approve` on a join request (`:993-1040`) writes no `DeviceRecord` and no "new device" notice. It writes a join approval into a new top-level array `joins` of `connect-devices.json`: `{ key, approval, approvedAt, expiresAt, approverAppKey? }`. A separate array fails closed: an older build drops it and the key is unapproved again. `isApproved`, `bindingFor` and `deviceApprover` never read `joins`, so the key cannot approve devices, mint bound credentials or pair anything.
- The gate (`check`, `:892-931`) lets a key with a live join approval in only for a session whose claim says join, and marks the verdict join-only. A session without the claim finds no `DeviceRecord` and waits for a full-device code as today. A join approval never becomes a device approval.
- Deny by default at the source. `authenticateHttpRequest` and `authenticateWebSocketUpgrade` (`S/auth/EnvironmentAuth.ts:1489-1527`) refuse a join-only session. Two callers opt in: `layerAuthenticatedAuth` when the endpoint is `accountJoinFleetWorkers` (the middleware is handed the endpoint and ignores it today, `S/auth/http.ts:436-471`), and `getSessionState` for `GET /api/auth/session` (`S/auth/EnvironmentAuth.ts:874-899`). So no websocket ticket, no `/ws`, no media, no raw route, no `connect-devices` route. `/mcp` already refuses the subject (`:1576-1577`).
- `accountJoinFleetWorkers` accepts `fleet:join` from a join-only session, or `orchestration:operate` from a fully approved device as today (`S/studioFleetHttp.ts:781`). Its other refusals stay.

**What the approval gets, and when it ends.** One successful `accountJoinFleetWorkers` call. The handler spends the join approval and revokes the session when `addAndAllowWorkers` succeeds. Unspent, the approval ends 10 minutes after it was typed; the session itself lasts at most 1 hour (`S/auth/EnvironmentAuth.ts:1137-1141`). After that N's app has nothing on J. A machine joined before 1422 has a `DeviceRecord` and keeps it until the owner removes it.

**N's app.** It must not save a route to J. For a J with `deviceJoinApproval` the join card holds an in-memory join handle instead of `environmentCatalog.register` (`W/components/settings/AccountJoinCard.tsx:235-262`): a proof-bound token from the same mint and exchange, kept out of the saved token cache (`R/authorization/service.ts:502-665`, cache key gains the purpose), and a poll of `GET /api/auth/session` on J every 4 seconds for the code and then for "approved". `throughAccount` (`W/components/settings/IncomingWorkerSetup.tsx:256-257`) takes "join approved" in place of `operateThere`, and `joinAccountMachineForWorkers` (`W/studio/fleet.ts:404-426`) posts with that handle. The handle is dropped after the join, on failure and when the card closes, so N stops asking J. If the approval ran out before Allow, the next poll starts a new request with a new code. If the answer to the join is lost, a retry is refused because the approval is spent; the card then reads N's own "Who can run work here" list, shows the done card when J is on it, and asks for a new code only when it is not. An N whose app is already a full device on J keeps today's path.

**An older new machine.** It sends no purpose, so its request is an ordinary device request: J's pop-up says so, and the code approves a full device as today. D-03 cannot be enforced against a client that cannot declare the join, short of refusing it; the stated fallback is the code as today.

**What each screen says** (T-07; every string through `tx` with eight languages).

- J's pop-up for a join request (`C/connectDevices.ts:46-68` gains optional `purpose`; `W/components/devices/ConnectDeviceViews.tsx:236-261`, `:327`): "{device} wants to join {machine}. Typing its code lets it hand over a line, so agents on {machine} can run work on it. It does not let that device open {machine}." The line that the name is the device's own word stays. A plain device request keeps PR 712's wording.
- J after the code: "{device} can now join. Press Allow on it." in place of "{device} can now use {machine}" (`W/components/devices/ConnectDeviceHosts.tsx:165-189`). The approve result keeps status "approved" and adds optional `join: true`; a new status literal would break an older window's decode.
- N's card while waiting: today's code line, plus "This lets {machine} join you to it. It does not let this app open {machine}." Against an older J the second sentence is left out.
- J's joined notice and N's Allow: see 2 and 3.

#### 2. D-01: the joined machine vouches for its own app

**The key.** The relay proof key of the SpecWithCode app on J in which the owner typed the join's code: `jkt:<thumbprint>` of the key in that app's IndexedDB. It is proven, not claimed. The app adds a `dpop` header to its own approve request, a proof over `POST <its server>/api/auth/connect-devices/approve` signed with that key. The header is already in the contract (`C/environmentHttp.ts:162-165`), the signer signs any URL (`W/cloud/dpop.ts:145-184`), and a server from before 1422 ignores the header on a bearer or cookie request (`S/auth/EnvironmentAuth.ts:768-794`). The approve handler (`S/auth/connectDevicesHttp.ts:137-153`) calls `verifyRequestProof` (`S/auth/EnvironmentAuth.ts:1777-1782`; it checks method, URL, signature and age, and refuses a replayed proof) only when the caller is this machine's owner and the matched request is a join, and stores the thumbprint as `approverAppKey` on the join approval. A device that typed the code remotely is never vouched: it is not J's app, and its proof was already spent by the auth layer.

**Only J's own app.** The proof is read only when the approving session's subject is one of two that only the app on J can hold. Neither the caller's scopes nor how the request arrived decides it.

- `desktop-bootstrap`, which exists today, for an app that started its own server.
- `local-desktop-app`, new in T-03, for an app attached to an installed service. `POST /api/auth/pairing-token` (`S/auth/http.ts:707-771`, input `C/auth.ts:504-513`) gains optional `localApp`. The server honours it only when the caller's subject is `local-cli-credential`, the in-memory credential the service keeps in an owner-only file on J (`S/auth/LocalCliCredential.ts:44`, `:57-63`), and then mints the code with subject `local-desktop-app` instead of `one-time-token`. Only the desktop's own `pair` call passes the flag (`D/backend/localServiceAttach.ts:352-362`, `S/cli/pair.ts:268-281`); `auth pairing create`, which an SSH-attached window on another machine uses (`packages/ssh/src/tunnel.ts:776`), never does. The new subject gets everywhere the old one is named for this app (`S/auth/SessionStore.ts:138-152`, `S/design/DesignRpc.ts:32-46`).

Every other approver gets no vouch and the join still completes: a window paired from another machine, a browser tab on J, a remote device, a session from a pasted token. Not passing over Connect stays as an added refusal, never as the reason to accept. Both subjects rest on the same footing: a process running as the owner on J could read either secret, and it already owns J. The one way to carry such a session elsewhere is deliberate: `auth session issue --subject` in J's terminal with the service stopped (`S/cli/auth.ts:291-326`); T-03 refuses both subjects there.

**The chain.** Code typed in J's app (proof of key K) → join approval for N's app key → that key's join-only session hands over N's line → J redeems it and holds the management token on N → J vouches K on N. `accountJoinFleetWorkers` does the last step itself, inside the same uninterruptible region as `addAndAllowWorkers` (`S/studioFleetHttp.ts:368-391`) so a caller that hangs up cannot skip it, only when the grant came back allowed or expiring (a failed mint still answers 200 with "not allowed"), and before it records the join or answers, with `fleetRequest` and the management token (`S/fleet/fleetTransport.ts:358-403`, as `S/studioFleetHttp.ts:875-886` does for self-allow), and only when N's descriptor carries the capability `deviceJoinVouch` (`checkIdentity`, as `:846-856`). J vouches once per join and never on its own later. A failed vouch never fails the join; the code remains.

**The route on N.** New `POST /api/auth/connect-devices/vouch`, exact body `{ thumbprint }`. N accepts it only when all of these hold:

- the caller's subject is `fleet-invitation` with a coordinator principal, the session is bound to a proof key, and it holds `access:write`;
- N's grant to that coordinator is full access to all projects right now (the predicate below);
- the key is not one N's owner removed or denied (`isTurnedAway`, `S/fleet/ConnectDeviceTrust.ts:881-890`): after Remove only a typed code brings it back;
- team rules allow machine links and Connect, as for the join (`S/studioFleetHttp.ts:797-798`); the route is rate-limited like redeem (`:618`).

One key per coordinator: a new vouch replaces the earlier one and ends its sessions. If that key waits on N, the waiting request is cleared so N's pop-up closes.

**The record.** A new top-level array `vouched` in N's `connect-devices.json`, never `devices`: `{ key, coordinator: <J's environment ID>, session: <ID of the management session that vouched>, vouchId, vouchedAt, label, system, app }`. A field on a `DeviceRecord` would fail open, because an older build would read it as a plain approved device and erase the field; a separate array is dropped and the key waits for a code again.

**The binding.** The vouch stands only while all four hold, read on every request and every 5 seconds on an open socket (`S/auth/EnvironmentAuth.ts:1529-1536`):

1. the management session named in the record is live on N;
2. N's work grant for that coordinator is not stopped or ended, covers all projects and all accounts (`projects.kind` and `accounts.kind` are "all", `S/fleet/workGrantPolicy.ts:103-108`), and its owner-chosen level is full access;
3. that coordinator holds at least one live worker-grant session on N (`liveCoordinators`, `S/fleet/WorkGrants.ts:298-311`);
4. the key is not removed.

For the level N needs a record it does not have. T-03 adds it: N's app sends the level the owner chose with the line it mints (`C/studioFleet.ts:215-226` gains optional `access`; the request goes to N's own server). N keeps it with the line and writes it to the grant policy as `ownerCap` when the line is redeemed, and refuses a worker grant above `ownerCap` at `S/auth/McpOAuth.ts:530-550`. The policy must not be created when the line is minted: a policy made before J holds its management session defaults to linked projects, not all (`S/fleet/WorkGrants.ts:424-438`, `S/fleet/workGrantPolicy.ts:103-108`), and every join would become project-limited. Without `ownerCap`, "full access" would be J's word.

When any of the four stops holding, the gate treats the key as unapproved: the record is deleted, the device waits for a code like any new device, and what it minted stops (below). Nothing revives it: after narrowing and widening again, J would have to vouch again, and the route checks the bounds again.

| Event | Effect on the vouch |
|---|---|
| Owner narrows projects or accounts on N | ends within 5 seconds; J's app is asked for a code |
| Stop on N | ends at once: every session of J's principal is revoked, the management session included; Restore does not revive it |
| Stop workers on J, or the grant lapses | no live worker-grant session is left (condition 3), so the vouch ends |
| Remove N on J | the management session is revoked on N, so the vouch ends |
| Remove the device on N | ends, sessions ended (`endSessions`, `S/auth/connectDevicesHttp.ts:94-121`), and the key cannot be vouched again |
| The management token reaches 365 days | ends; the code, or a new join |

**What a vouched app is on N.** A device for use, never for approving. The gate allows it, and `bindingFor` and `checkBinding` (`S/fleet/ConnectDeviceTrust.ts:826-848`) honour it with `vouchId` as the approval, so `RequestDevice` (`:500-503`), asset URLs and uploads work (`S/fleet/deviceBoundTransfers.ts:30-52`) and die with the vouch, as `trackCredential`, `boundIds` and `creatorDeviceKey` already arrange for an approved device (`S/auth/EnvironmentAuth.ts:1214-1221`, `:1662-1667`). `deviceApprover` does not honour it: a vouched app cannot approve, deny, remove, confirm or repair on N. Otherwise a management key would approve devices through the app it vouched.

**Settings > Machines.** On N, "Devices that can use this machine" (`W/components/devices/ConnectDeviceViews.tsx:578-618`) lists the vouched app with its ID and "Let in by {machine}'s join, no code. Stays while {machine} has full access to all projects here.", with Remove. `ConnectDevice` (`C/connectDevices.ts:22-43`) gains optional `vouchedBy`. J's card on N gets a line under "can start work here": "Its SpecWithCode app can open this machine without a code." (`W/components/settings/machineDirections.logic.ts:37-110`).

**Saying it only when true.** The answer of `accountJoinFleetWorkers` and the recorded join (`C/studioFleet.ts:92-96`) gain optional `appOpens: "no-code" | "code"`. N's Allow promises "no second code" (AC-03) only when the level chosen is full access, both capabilities are present and J's join session state says the approving app proved its key; otherwise it says "{machine}'s app will ask for a code here."

**No pop-up.** J's window must not learn of N before J's vouch attempt has ended. Two changes make that hold for a first join.

- On J, `accountJoinFleetWorkers` holds the new machine back. Before it adds N it notes N's environment ID (known from the line, `decodeFleetJoinCode`) in an in-memory, counted set, only when N is not in the fleet file yet. `GET /api/studio/fleet` leaves a held machine out of `machines`, filtering after it has read the grants (`S/studioFleetHttp.ts:495-515`). The hold is released in a finalizer when add, allow and the vouch attempt have ended, whatever the outcome. Leaving N out needs no contract change, an older window is covered too, and it also holds back the Tailscale pairing path and the joined notice, which only announces a listed machine (`W/studio/fleetJoinNotice.ts:14-22`). The vouch call carries its own time limit of 5 seconds, as `S/studioFleet.ts:317-320` does, so the hold is bounded.
- On N, a standing vouch never makes a waiting request. `ensureWaiting` (`S/fleet/ConnectDeviceTrust.ts:744-812`), which the relay mint also runs (`:933-949`), answers "approved" without writing when the key has a standing vouch, as it does for an approved device. Landing a vouch deletes any waiting request of that key.

So when the vouch succeeds, N never has a request to show. When the vouch attempt fails or times out, N is listed after it, J's window opens it, and N asks for the code: that is AC-05's fallback, and the pop-up is the code prompt.

What the hold does not cover, all ending at the code as today: J's server restarts in the middle of a join (the hold and the vouch are both lost); a join again by a machine J already lists, whose route J's window may already be trying; a route added by hand, or by first-run machine selection, while the join runs.

**Where it falls back to the code by itself.** The code was typed in a browser tab or a development build and the installed app opens N (different keys); two windows that each made a key at first start (`W/cloud/managedRelayLayer.ts:20-36`, last write wins); a proxy in front of J's server changes the URL the proof names; the level chosen is below full access; the code was typed in anything that is not J's own app.

#### 3. D-02: one way, the reverse offered

The join mints nothing on J for N: `accountJoinFleetWorkers` only runs `grants.allow` on J against N (`S/studioFleetHttp.ts:368-391`). T-04 pins that with tests and changes no grant code.

The offer is on J's joined notice (`W/components/FleetJoinNotice.tsx:42-49`, `W/studio/fleetJoinNotice.ts:10-26`), which has no action today. New text: "{label} joined. Agents on this machine can run work on it, and this app can open it. It cannot use this machine." With `appOpens: "code"` the middle part reads "and this app can open it after its code is typed there." Action: "Let {label} run work here…".

J gives the reverse, by the owner's Allow on J, through the existing flow: the action opens N's card at "Let {there} start work here" (`AllowBack`, `W/components/settings/MachinesSettings.tsx:1105-1145`), which calls `allowIncomingFleetWorkers` on J's own server (`S/studioFleetHttp.ts:825-923`; owner only, same-origin, invite maker). J mints its own line for N and sends it to N's `selfAllowFleetWorkers` (`:738-770`) with the management token the join gave J. N redeems it and then holds a management token and a worker grant on J. The confirm dialog already says what that hands over.

Two changes make the offer usable. `canAllowBack` and `unavailable` require this app to be connected to the other machine (`W/components/settings/machinesSettings.logic.ts:776-788`, `W/components/settings/IncomingWorkerSetup.tsx:258-263`), though the request needs only the fleet ID on J's own server; that is relaxed for a machine J's server lists, so the offer also works when the vouch fell back. And the reverse grant does not renew: a fresh self-allow saves no `access:write` (`S/studioFleetJoin.ts:398-404`, `S/fleet/workerGrantMint.ts:397-399`), so it ends after 30 days and the card must say "until {date}".

#### 4. Threats

| Threat | Answer |
|---|---|
| Stolen Connect sign-in | It still needs a code typed by the owner on the machine it wants. Claiming a join gets it less than today: it can hand over a line for the attacker's own machine and gets nothing on J. The owner then sees "{label} joined" with a name the attacker chose, so the notice says agents here can now run work on it and offers Remove. It cannot be vouched: a vouch names only the key proven in an approve request made by J's owner session. |
| Stolen or replayed join credential | The line is spent once (`S/auth/EnvironmentAuth.ts:1303-1333`); if a thief redeems it first, J's redeem fails and the join fails in view. A thief who redeems it holds a management token as coordinator J (`S/studioFleetHttp.ts:679-686` logs it) and can then vouch its own app. That adds project-unbounded use for the vouched app, which the predicate allows only while the owner's limits are already "all", and it dies with that token. The management token and the join-only token are bound to proof keys, so a copy without the key is refused. Proofs are single use (`S/auth/dpop.ts:94-131`). |
| A window on another machine that is paired to J with Manage access types the join's code | It may approve the join, as it may approve any device today, but its key is never vouched: the proof is read only from a session whose subject is `desktop-bootstrap` or `local-desktop-app`, and neither can be minted for another machine. Per-machine approval (1416 D-01) holds: that window still needs N's own code. |
| A management key minting devices outside the bounds | One route, one key per coordinator, the predicate at vouch time and on every request, refused for a removed or denied key, tied to the vouching session, and the vouched app is not an approver. `deviceApprover` still refuses every coordinator. A coordinator cannot change project or account limits, and with `ownerCap` it cannot raise the level. |
| A device request claiming to be a join | It gets the join-only session: one route, one use, 10 minutes. Without the claim it gets today's full-device request with today's wording. A code approves only the kind it was shown with. The kind is in the signed session, so it cannot change after issue. |
| An older client on either side | See the table below. Every case lands on the code as today, with wording that is true for that case. |

| N | J | Result |
|---|---|---|
| new | new | join-only code, vouch, no second code |
| old app | new | full-device request and approval as today; no join approval, so no proven key and no vouch; second code |
| new | old (no `deviceJoinApproval`) | today's flow and wording; second code |
| new, old server on N | new | join-only code; no vouch; second code |
| any | J's window older than its server | no proof with the approve, no vouch; second code |

#### 5. Test plan

Failing tests first. Each task tests the server refusal and the UI gate.

**T-08** (also `S/auth/EnvironmentAuth.ts`, `S/auth/http.ts`, `S/auth/SessionStore.ts`, `S/auth/connectDevicesHttp.ts`, `S/environment/ServerEnvironment.ts`, `C/auth.ts`, `C/connectDevices.ts`, `C/environment.ts`, `R/authorization/service.ts`, `R/authorization/remote.ts`, `W/studio/fleet.ts`, `W/components/settings/IncomingWorkerSetup.tsx`, `W/components/devices/ConnectDeviceViews.tsx`):

- `S/fleet/ConnectDeviceTrust.test.ts`: a join request approved by code writes `joins` and no device; `isApproved` and `bindingFor` stay false; a session without the claim still waits and gets a different code; the kind change replaces the code; the approval ends after 10 minutes and after one use; a file with `joins` read by a build without it leaves the key unapproved.
- `S/auth/deviceApproval.test.ts` (real auth layer, `:31-38`): a join-only session gets 403 on the websocket ticket, on each `connect-devices` route, on a scoped route, on the `/ws` upgrade and on a media route; `GET /api/auth/session` answers join-only; a token without the claim for the same key is refused with a code.
- `S/studioFleetHttp.test.ts` (account-join block, `:888-1076`): a join-only session hands over its line once; the second call is refused; the approval is spent and the session revoked; a fully approved device still joins; a machine joined before keeps its device record.
- Web: `IncomingWorkerSetup.test.tsx` and `AccountJoinCard.test.tsx`: against a J with the capability the card registers no saved route, shows the code from the join handle, enables Allow on "join approved" and drops the handle after; against a J without it today's path and words. `ConnectDeviceViews.test.tsx`: join wording for a join request, PR 712 wording otherwise.

**T-03** (also `S/auth/connectDevicesHttp.ts`, `S/auth/http.ts`, `S/auth/EnvironmentAuth.ts`, `S/auth/SessionStore.ts`, `S/auth/McpOAuth.ts`, `S/cli/pair.ts`, `S/design/DesignRpc.ts`, `S/fleet/WorkGrants.ts`, `S/environment/ServerEnvironment.ts`, `D/backend/localServiceAttach.ts`, `C/auth.ts`, `C/connectDevices.ts`, `C/environmentHttp.ts`, `C/studioFleet.ts`, `W/studio/connectDevices.ts`, `W/components/devices/ConnectDeviceViews.tsx`):

- Approve with a valid proof from a `desktop-bootstrap` or `local-desktop-app` session stores `approverAppKey`; a bad, replayed or missing proof approves without it. The same valid proof from each of these approves and stores nothing: a `one-time-token` session with `access:write` (a paired window), an `administrative-bootstrap` session, a `local-cli-owner` token, an approved Connect device.
- `pairing-token` with `localApp` from the `local-cli-credential` session mints `local-desktop-app`; from any other caller, a paired window with `access:write` included, it is refused; without the flag the subject stays `one-time-token`.
- No pop-up: while a join runs, `GET /api/studio/fleet` on J leaves the new machine out and lists it once the vouch attempt ended, for success, refusal, timeout and a caller that hung up; a machine J already lists is never left out. On N, a mint and a session check for a key with a standing vouch write no waiting request, and a vouch deletes one that exists.
- `vouch` on N: accepted from the bound management session with a full grant; 403 for a Connect session, the owner, a worker grant, an unbound token, another coordinator's grant, a project-limited or account-limited grant, an `ownerCap` below full access, a stopped or ended grant, a removed or denied key; a second vouch replaces the first and ends its sessions.
- Binding over time (`TestClock`): narrow projects, Stop, Stop then Restore, Stop workers on J, a lapsed worker grant, revoke the management session, Remove the device: each makes the next request wait for a code and ends an open socket; nothing revives it.
- A vouched session gets 403 on every `connect-devices` route; its asset URL works and stops with the vouch.
- A worker grant above `ownerCap` is refused at the decision; a join still gets an all-projects policy, with `ownerCap` set at redeem.
- Account-join on J: vouches after the grant, skips it for an N without the capability or a join without `approverAppKey`, and answers `appOpens` truthfully; a failed vouch leaves the join done.
- Web: the approve request carries the proof; the devices list shows the vouched row with Remove; Allow says "no second code" only when the level is full access, both capabilities are present and the approving app proved its key.

**T-04** (also `W/components/FleetJoinNotice.tsx`, `W/studio/fleetJoinNotice.ts`, `W/components/settings/MachinesSettings.tsx`, `W/components/settings/machinesSettings.logic.ts`, `W/components/settings/IncomingWorkerSetup.tsx`):

- `S/studioFleetHttp.test.ts`: after account-join, J has no work-grant policy and no `fleet-invitation` session for N; `allowIncomingFleetWorkers` from J's owner sets up the reverse; the same call from a Connect session, a coordinator or a join-only session gets 403.
- Web: `GrantedAccountMachines.test.tsx`: no route is registered for a machine the snapshot does not list yet. The notice has the action (the assertion at `W/components/FleetJoinNotice.test.tsx:59` flips); the action opens N's card; "Let {there} start work here" is offered for a listed machine this app is not connected to; the reverse grant shows its end date.

**T-07** (also `W/components/devices/ConnectDeviceViews.tsx`, `W/components/devices/ConnectDeviceHosts.tsx`):

- `FleetJoinNotice.test.tsx`: both `appOpens` texts and the one-way sentence. `AccountJoinCard.test.tsx` and `IncomingWorkerSetup.test.tsx`: Allow's text for each row of the version table. Each new string has entries in the eight languages (the phrase tests in `W/i18n/phrases/`).
- Server side of the same gate: the tests of T-08 and T-03 that the screen's sentence is true (no access to J; no code on N only when vouched). T-07's strings merge with T-08 and T-03, never ahead.

#### 6. Routes and RPCs that change

All are HTTP. No WebSocket RPC method is added or changed, so `RPC_REQUIRED_SCOPES` (`S/auth/RpcAuthorization.ts:48-298`) and `CLIENT_GUARDED_RPC_SCOPES` (`C/clientRpcPermissions.ts:22-285`) need no entry; that table does not apply to HTTP routes. The new scope `fleet:join` maps to no RPC.

| Route | Change |
|---|---|
| `POST /oauth/token` | optional form field `client_purpose` |
| `GET /api/auth/session` | answers a join-only session, with whether the approving app proved its key |
| `POST /api/auth/connect-devices/approve` | reads the optional `dpop` header; answer gains optional `join` |
| `POST /api/auth/connect-devices/list` | requests gain optional `purpose`; devices gain optional `vouchedBy` |
| `POST /api/auth/connect-devices/vouch` | new, on the new machine, for the joined machine's management token |
| `POST /api/auth/connect-devices/remove` | also removes a vouched key |
| `POST /api/auth/pairing-token` | optional `localApp`, honoured only for the local command-line credential |
| `POST /api/studio/fleet/invite` | optional `access`, stored as `ownerCap` |
| `POST /api/studio/fleet/workers/account-join` | accepts a join-only session; vouches; answer gains optional `appOpens` |
| `GET /api/studio/fleet` | recorded joins gain optional `appOpens`; a machine is left out while its first join runs |
| `POST /oauth/mcp/decision` | refuses a level above `ownerCap` |
| `GET /.well-known/studio/environment` | capabilities `deviceJoinApproval`, `deviceJoinVouch` |

Every added response field is optional and no status literal is added, so an older window still decodes. Every added request field goes only to a server that advertises the capability, or to the app's own server.

#### Open for the owner

Asked on a card to the owner, November 19, 2026 (answers not recorded here yet):

1. AC-05 says a capped grant falls back to the code, but the new machine does not know the cap today: the joined machine names the level and can name a higher one later. The design stores the owner's choice on the new machine (`ownerCap`) and refuses grants above it. That tightens every join, not only the vouch. Without it the cap half of AC-05 rests on the joined machine's word. Recommended: keep `ownerCap` in T-03.
2. The predicate also requires all accounts, which AC-05 does not say. A vouched app can use every sign-in on the new machine, so an account-limited grant should not carry it. Say if accounts should not count.
4. The reverse Allow (D-02) brings the second code back the other way: N's window opens J by itself once J granted N, and J asks for N's code. Typing it makes N's app a full device on J, which D-03 just took away. Either the reverse Allow says so and keeps the code, or that automatic open is skipped for a machine whose only tie is the reverse grant. Recommended: skip the automatic open; the reverse is about agents.

Accepted limit, not asked:

3. D-03 holds only when the new machine's app is new enough to declare the join. The joined machine cannot tell an older new machine's request from a plain device request, so an older app's code approves a full device, with PR 712's wording, which says so. Refusing the join afterwards would not undo that approval.

Proposed for the acceptance gate:

5. The vouch ends when the management token does, after 365 days, since that token never renews. Then the code is asked once. It fails closed and changes nothing that exists today.

New in round 2:

6. An app attached to an installed service has no mark of its own today, so the design adds one (`local-desktop-app`, minted only for the service's local command-line credential). It touches the pairing route, the `pair` command and the desktop app. Without it such an install always falls back to the second code. Recommended: keep it in T-03.
7. Outside 1422, found while reading: the sleep and suspend routes say their caller is this machine's own app but accept any bearer session with `access:write` and a device principal (`S/project/CoordinatorSuspendRoute.ts:26-36`), so a window paired from another machine with Manage access passes. The marker from item 6 would close that too. Recommended: its own increment.

## Tasks

### T-01 The device pop-up says what Allow adds
- AC: AC-01, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/components/devices

### T-07 Joined notice and Allow say the join is one way and what Allow covers
- AC: AC-02, AC-03, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: focused web tests for both components

### T-02 First-run row and done card use 1390's words
- AC: AC-04, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/SignInFirstStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: focused web test; wording agreed with the 1390 owner

### T-08 The join's code approves the join only (D-03)
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/SessionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/connectDevicesHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/deviceApproval.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/auth.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/connectDevices.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/service.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/remote.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/fleet.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx | Test: server tests that the joining app can hand over its line and nothing else; Muse Wonderful review

### T-03 The joined machine vouches for its own app (D-01)
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ConnectDeviceTrust.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/WorkGrants.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/connectDevicesHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/connectDevicesHttp.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/deviceApproval.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/SessionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/McpOAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/pair.ts, repositories/anton-abyzov/specwithcode/apps/server/src/design/DesignRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/backend/localServiceAttach.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/auth.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/connectDevices.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environmentHttp.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/studioFleet.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/connectDevices.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/fleet.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/devices/ConnectDeviceViews.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machineDirections.logic.ts | Test: server tests for the binding and its refusals; Muse Wonderful review

### T-04 One-way grant with the reverse offered (D-02)
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetHttp.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/FleetJoinNotice.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/fleetJoinNotice.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/GrantedAccountMachines.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IncomingWorkerSetup.test.tsx | Test: server tests for both directions; Muse Wonderful review

### T-05 Check on real machines after release
- AC: AC-08 | Files: .specweave/increments/1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds/reports/ | Test: Anton's screens of the join on both machines

### T-06 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10 | Files: .specweave/increments/1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds/ | Test: specweave verify 1422

## Review

Reviewer: Muse Wonderful, `muse-wonder-full-1.0`, effort high, for anything touching device approval or grants. It confirms that no `[label]` change alters who gets access.
