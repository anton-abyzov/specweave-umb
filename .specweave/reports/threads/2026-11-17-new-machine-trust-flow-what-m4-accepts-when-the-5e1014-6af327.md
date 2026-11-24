---
title: "New-machine trust flow: what M4 accepts when the M5 joins"
thread: "thread:delegated-task:command%3Amcp%3Ab3208303-b232-4312-990b-30ea6ad43297%3Adelegate-task%3A9eb485a7-18a4-48b8-970d-856060256445"
threadTitle: "New machine trust and remote execution"
savedAt: "2026-11-17T07:06:37.330Z"
date: November 17, 2026
code: anton-abyzov/specwithcode origin/main 2f1a4f362; the 31 cited files are identical in 1.0.329, 1.0.330 and current main 8ad73fe68
status: read-only investigation, no code, grant or setting changed
---

# New-machine trust flow: what M4 accepts when the M5 joins

## Verdict

Your impression is right, and it is a real gap, not normal behaviour.

When the M5 signed in to SpecWithCode Connect with Google, nothing was accepted on M4, linux-mini or m1. From that moment the M5's window could open terminals, read and change files, change settings and sign-ins and start work on every machine linked to the account. M4 showed one toast after the fact.

The confirmation you are asking about was already decided on November 13, 2026 (increment 1327, "New Connect devices need one approval on each machine"). It was built in two pull requests, #361 and #362. Both are green and mergeable today, and neither was ever merged. `git grep device_not_approved` returns nothing on `main` and on the 1.0.330 tag. A report on November 14 said "Ships in the next release". 33 releases have gone out since (1.0.298 to 1.0.330), none with it.

Two different things happened in your join, and they get different verdicts:

| Plane | What happened | Confirmation on the target | Verdict |
|---|---|---|---|
| Person: the M5's window uses M4, linux-mini, m1 | Allowed by the Connect sign-in alone | None | Real gap. Fix is 1327 |
| Machine: M4's agents and M4's key on the M5 | Allowed by your click on "Allow m4" on the M5 | One click on the M5, none on M4 (your choice of November 11, 1296 D-25) | Works as decided, but the card understates what the click hands over |

## What you actually used

"Google SSH" and "Google console" read as Google sign-in to SpecWithCode Connect. Connect signs in through Clerk with Apple or Google. No SSH is part of joining a machine: the SSH keys step (increment 1364) only lists hosts in the copy dialog and connects nowhere.

The join itself was the same-account join card. M4's own record, `/Users/antonabyzov/.specwithcode/m4/studio-fleet-account-joins.json`:

- `anton-m5max-proled-2`, "Anton M5MAX PROLED", November 13, 2026, 12:30:51 PM EST
- `anton-m5max-proled`, "Anton M5MAX PROLED", November 16, 2026, 12:46:18 AM EST

M4's session table shows a new macOS desktop key (`Gmlp3urLQv…`) get its first Connect session on M4 at 12:45:51 AM EST on November 16, 27 seconds before the join was recorded. At 12:50:47 AM the M5's window started copying M4's specweave project, with no call from M4's own window (increment 1365 spec, Problem section).

Which sign-in provider was used is not visible from M4. M4 only learns that the account id matches its own.

## The flow as it works

Line numbers are at `origin/main` `2f1a4f362` in `repositories/anton-abyzov/specwithcode`.

1. **Sign-in.** The M5's window holds a Clerk session. It makes a fresh key pair and exchanges the Clerk token for a relay token bound to that key. The relay checks the Clerk token and that the caller holds the key, nothing else: `infra/relay/src/http/Api.ts:884-946`.
2. **Machine link.** The M5's server signs a link proof with its own key and the relay stores the link under the signed-in account. No existing machine is asked: `infra/relay/src/http/Api.ts:687-704`.
3. **List.** Any signed-in client can list every machine of the account: `infra/relay/src/http/Api.ts:651-661`.
4. **Connect to M4.** The relay checks only that the account owns a link to M4, then signs a request naming the account and the window's key: `infra/relay/src/http/Api.ts:958-987`, `infra/relay/src/environments/EnvironmentConnector.ts:583-650`.
5. **M4 mints access.** M4 checks the relay's signature, that the account equals the one it was linked with, the key binding, and replay. It then issues the standard scopes under subject `cloud-connect`. No device check: `apps/server/src/cloud/CloudLink.ts:1751-1824`. The only switch that refuses is the team rule that turns Connect off on the machine: `apps/server/src/cloud/CloudLink.ts:195-202`.
6. **What those scopes are.** Operate threads, write settings, manage providers, maintain (update) the machine, open terminals, write source control, read and write files: `packages/contracts/src/auth.ts:224-238`. Every call is checked against the session's scopes only: `apps/server/src/auth/RpcAuthorization.ts:410-427`.
7. **The join card on the M5.** You pick M4 and press Allow. The M5's own app makes an invitation line (only that machine's own app can: `apps/server/src/studioFleetHttp.ts:594-608`, `:227-241`) and hands it to M4 through the M5 window's Connect session there: `apps/web/src/studio/fleet.ts:404-444`.
8. **M4 takes it with no click.** `apps/server/src/studioFleetHttp.ts:777-821`. The code says why at `:771-776`: "The relay proved that sign-in is this machine's own account, and it already carries terminal and file access here, so the line needs no second approval on this machine."
9. **What M4 now holds on the M5.** A management key with 16 scopes, bound to M4's machine key, for 365 days (`apps/server/src/fleet/fleetRedemption.ts:24-29`, `apps/server/src/studioFleetInvite.ts:51`, `apps/server/src/studioFleetHttp.ts:614-692`), and a worker grant for 30 days that renews by itself (`apps/server/src/auth/EnvironmentAuth.ts:127`, `apps/server/src/studioFleetJoin.ts:399-403`, `apps/server/src/fleet/workerGrantMint.ts:397-399`). The grant's defaults for your own machine are every project and every provider sign-in (`apps/server/src/fleet/workGrantPolicy.ts:103-108`), with routines switched on by themselves (`apps/server/src/fleet/WorkGrants.ts:268-284`).

What the M5 showed before the click (`apps/web/src/components/settings/AccountJoinCard.tsx:663-699`):

- "Most its work may do": Full access by default (`apps/web/src/studio/fleetWorkers.ts:52`)
- "Lasts": "Until you stop it here or on {coordinatorLabel}. It renews by itself."
- "Management key": "It also gets a key to manage access, updates and skills on this machine, for a year. Existing project and sign-in limits stay in force."
- "Secrets": "Not included. Each secret transfer still asks you."
- Button: "Allow {coordinatorLabel}"

What M4 showed afterwards (`apps/web/src/components/FleetJoinNotice.tsx:42-49`): a toast titled "{label} joined" with "It was added through your SpecWithCode Connect account, and agents on this machine can now run work on it. Nothing to accept. You can change or remove it in Settings > Machines."

## What is recorded where

| Place | Record | Source |
|---|---|---|
| M4 | One `cloud-connect` session row per hour per window: label "SpecWithCode Connect connect", desktop, macOS, Electron, address 127.0.0.1, key thumbprint. No machine name, no environment id | `specweave-studio db query` on `auth_sessions` |
| M4 | Fleet row "M5" (`anton-m5max-proled`, environment `644195cc…`), full access, grant until December 16, 2026 | `studio_machine_list` |
| M4 | Join notice entry, kept 7 days, 10 entries at most | the file above; `apps/server/src/fleet/accountJoins.ts:16-19` |
| M4 | Nothing that lets the M5's agents start work on M4. M4's incoming grants are linux-mini and m1 only | `/Users/antonabyzov/.specwithcode/m4/userdata/work-grants.json`, policy fields only |
| M5 | M4's management session, M4's worker session, a grant policy for M4, its own Connect link | From code only. Not read on the M5 |
| m1, linux-mini | A `cloud-connect` session row whenever the M5's window opens them | From code only. Not read there |
| Relay | Link row, tunnel allocation, machine credential, one client-key row per window. No history of connects | `infra/relay/src/persistence/schema.ts:80-162`. Deployed database not read |

## What executes on a machine, and whether that machine confirmed it

"Target" is the machine where the action runs.

| Capability | Person's window from another machine (Connect) | M4's agents on the M5 (worker grant) | M4's key on the M5 (management key) |
|---|---|---|---|
| Start and steer threads | Yes, `orchestration:operate`. No confirmation on the target | Yes. Confirmed once by "Allow m4" on the M5 | Yes, same click |
| Terminal | Yes, `terminal:operate` (`RpcAuthorization.ts:255-258`). No confirmation | Through the agent's own shell in a Full access thread | Yes, the key holds `terminal:operate` |
| Files read and write | Yes (`RpcAuthorization.ts:233`). No confirmation | Through the agent | Yes |
| Source control | Yes, `source-control:write`. No confirmation | Through the agent, with the M5's Git sign-ins | Yes |
| Settings, providers, app update | Yes (`RpcAuthorization.ts:131`, `:138`). No confirmation | No tool for it | Yes |
| Non-secret file transfer | Yes, the copy dialog | Yes, inside the grant's project folders (`apps/server/src/fleet/fileTransfer/offers.ts:126-141`) | Yes |
| Secret files | Yes. One tick in the asking window, nothing on the source (`packages/contracts/src/clientRpcPermissions.ts:92`) | The M5 hands the file over when asked. The approval card appears in the asking thread on M4, not on the M5 (`offers.ts:145-165`, `apps/server/src/mcp/toolkits/fileTransfer/handlers.ts:133-135`, `:408-435`) | Yes |
| Computer use | Card on that Mac plus macOS permissions. A Connect window can answer the card itself: it needs only `orchestration:operate` (`RpcAuthorization.ts:188`) | Same card, raised on the M5. An agent cannot answer it | Same card. The key can answer it |
| Chrome on that machine | Not direct: Allow in Settings > Chrome there needs `access:write` (`clientRpcPermissions.ts:38`). Reachable through the terminal, see F-01 | Same switch | The key holds `access:write` |

The coordinator on linux-mini has no grant on the M5, so its agents are refused there directly. Two paths still reach the M5 without the M5 naming linux-mini: a window signed in to the account (first column), and a two-hop path linux-mini to M4 to M5, which the M5's grant for M4 admits because your own machines get two hops (`packages/contracts/src/studioFleet.ts:417`, `apps/server/src/fleet/workGrantPolicy.ts:128-151`).

## Adversarial findings

### Critical

**F-01. One Connect sign-in is the owner of every machine.** Stolen Google or Clerk credentials, or one compromised signed-in device, give a terminal on M4, the M5, m1, m3 and linux-mini. The attacker makes a new key, exchanges the Clerk token, connects, and opens a terminal. No machine is asked. Steps 1 to 6 above are the whole path. The terminal also lifts the caller to full local control, because the machine's own command line gets every scope (`apps/server/src/auth/LocalCliCredential.ts:59`), so limits that depend on `access:write` do not hold against a Connect session. Live evidence: 10 device keys have received Connect sessions on M4 since November 10 (6 macOS, 1 Linux, 3 iOS), none approved by anyone, none revoked. Unchanged since the November 13 review (XM-01).

### High

**F-02. The approved fix never shipped.** #361 (`feat/1327-device-approval`, head `753fc922d`) and #362 (head `8a1e43ae3`) are open, checks green, mergeable, 117 commits behind `main`, no review recorded. Increment 1327 has T-04 open.

**F-03. A rogue machine can join and stay.** Linking a machine needs only the account sign-in (step 2). The same sign-in can then make M4 add any machine a line names and allow work there, with no click on M4 (`apps/server/src/studioFleetHttp.ts:777-821`). The check that keeps phones out trusts the client's own word (`:790-796`). Ending the stolen sign-in later does not remove that machine from M4's list. This adds no power beyond F-01, but it survives the cleanup of F-01. The rogue machine gets no grant on M4; the harm is M4 sending work and project content to it. Rated High on the assumption that this can happen without you choosing that machine. Whether Away, handoff or automatic placement can pick it was not checked; if they cannot, this is Medium.

**F-04. A compromised M4 owns the M5 for a year.** The management key carries terminal, files, settings, providers and access management, and can mint further sessions on the M5 (`apps/server/src/auth/http.ts:696-738`). The card calls it "a key to manage access, updates and skills" and says "Existing project and sign-in limits stay in force". Those limits bind agent work only, not the key. Design-level, narrowed because the key is bound to M4's machine key (XM-03).

**F-05. "Each secret transfer still asks you" does not hold for the machine that owns the secret.** The card is shown where the request starts. The serving machine checks only that the grant is your own machine with Full access. Since 1365 a copy started from the other machine's window sends the source's secret files with one tick in that window (XM-05 plus 1365).

### Medium

**F-06. One Allow covers more than it names.** Full access by default, every project, every sign-in, routines on by themselves, renewal without end, two hops, and anything later mapped to an existing scope.

**F-07. Revocation is uneven.** Machine plane is sound: Revoke on the M5 ends M4's worker grant and management key together (`apps/server/src/fleet/WorkGrants.ts:383-395`, `:650-665`). Person plane has no lasting revoke for a desktop device: ending its session on M4 does not stop the next mint (step 5 has no key check), the relay removes phone keys only (`infra/relay/src/http/PhoneRemovalApi.ts:219-223`), and deregistering a machine leaves its window's Clerk session valid (1296 AC-51 note 4). Only ending the Clerk session or turning Connect off on the machine stops it.

**F-08. You cannot later see which machine did what.** Session rows carry no machine name and are deleted 7 days after they end (`apps/server/src/persistence/AuthRowPruning.ts:38`). Every command from any window is stamped as "user" from "web" (`apps/server/src/ws.ts:2081-2085`). The sender is recorded only when team rules are on (`apps/server/src/teamRules/TeamRulesRecords.ts:58-66`), and M4 has 0 such rows. M4's server trace covers about one hour. The join and redeem log lines were not found in M4's service logs. Work started by an agent is attributed to the starting machine (`apps/server/src/fleet/WorkGrants.ts:95-108`, `apps/server/src/mcp/workGrantAccess.ts:373`), and such a thread shows "From {label} · {machine}" (`apps/web/src/components/chat/ThreadOriginBadge.tsx:14-18`, present in 1.0.330). Terminal and file actions by a person's window are not attributable.

### Low

**F-09. M4's only signal is a toast.** It says agents on M4 can run work on the new machine. It does not say the new machine's window can now use M4.

**F-10. Two project memory notes disagreed** on where Allow is pressed. The code presses it on the new machine. Corrected in project memory (`decision_machine_join_flow.md`); the gap itself is recorded in `project_connect_device_trust.md`.

### Checked and sound

- Only a machine's own app can make its invitation line.
- The management key is bound to the main machine's key, so the token alone is useless.
- Agents on a machine without a grant are refused.
- The relay never issues access to a machine the account does not own (`EnvironmentConnector.ts:597-610`).
- Agents cannot answer approval cards. The agent tool answers "Only the user can answer an approval card. Wait for their answer." (`apps/server/src/mcp/toolkits/thread/handlers.ts:356-360`), and the secret-transfer card is one of those (`apps/server/src/mcp/toolkits/fileTransfer/handlers.ts:418-425`).
- Another machine's agents get no computer-use tool and no card-answering tool here (`apps/server/src/fleet/RemoteStudioMcpClient.ts:51-79`).

Not on this list: the Chrome switch and the computer-use card. Both are real gates for agents, and both fall to a Connect window through F-01.

## Compared with the machine access lines and 1327

The two lines on each machine card, "Agents on {here} can start work on {there}" and "Agents on {there} can start work on {here}" (decision of November 8, 2026), cover agent work only. Each has a switch, and "Who can run work here" edits the incoming project and sign-in limits. That plane is named, switchable and revocable today.

A person's window has no line and no list anywhere in Settings > Machines, although it is the stronger access. 1327 fills exactly that hole: a "Devices that can use this machine" list placed above the two agent lines, plus the pop-up. It leaves the agent lines and machine keys as they are (spec, Scope and Approach 8).

So the model you already approved for agents (a named line per direction, a switch on the machine that is affected) is not applied to people's devices yet. That is the inconsistency you noticed.

## The smallest fix

1. **Ship 1327.** Rebase #361 and #362 (migration 075 is still free on `main`), run them on two real machines, release. The confirmation appears in the target machine's own app. As built in #362: title "A new device wants to use {machine}", line "{who} is asking. Allow lets it use {machine} like this app does.", a box "Type the code shown on {label}", buttons "Allow", "Deny" and "Later", and "Deny turns it away for a day." The asking device shows "Open SpecWithCode on {machine} and type this code:". Deny refuses that key for 24 hours. A request nobody answers expires after 10 minutes and grants nothing. Machine-to-machine keys stay exempt, as designed.
2. **Two fixes to 1327 before it merges.** Both read from the branch code, not run.
   - The pop-up cannot tell devices apart. `{who}` is the session label plus "(computer)" or "(phone)" (`apps/web/src/studio/connectDevices.logic.ts:16-28` on `feat/1327-device-approval-ui`), and every Connect session gets the same fixed label, "SpecWithCode Connect connect" (`apps/server/src/cloud/CloudLink.ts:1832` on `feat/1327-device-approval`; all 10 device keys on M4 carry it today). For the M5, linux-mini or a stranger it would read "SpecWithCode Connect connect (computer) is asking." Only the typed code ties the request to the device in your hands. It should name the device as it reports itself (name, system, app version; the system and version are already in the session row), the Connect account, and what Allow gives: terminals, files, settings and sign-ins, starting work.
   - The code is invisible during first run. #362 mounts the waiting card and the pop-up only in the normal app tree (`apps/web/src/routes/__root.tsx:286-288` on the branch). The first-run route returns its own tree without them (`:198-230`). A machine joining from the welcome wizard would hold a code nobody can see, and Allow would answer "Connect to {coordinatorLabel} first." (`apps/web/src/studio/fleet.ts:417`). Mount the waiting card in the first-run tree and let the join card wait for the approval.
3. **Wording, no auth change.** Rewrite the "Management key" and "Secrets" rows on the join card and the M4 toast so they say what is handed over.

One decision is yours. With 1327 a new machine's join needs the code typed on the main machine, which adds the main-machine step the November 12 join decision ruled out. The November 13 decision is later and explicit, so I recommend accepting the extra step and not exempting the join.

Until it ships, the only gate is the Google and Clerk sign-in itself.

## Unverified and unclear

- Nothing was read or run on the M5, linux-mini, m1 or the relay. Their records are derived from code.
- M4's fleet file was not read (it holds keys). The sanitized machine list was used.
- Whether Google 2-step verification or Clerk new-device emails are on is outside the code.
- That the thumbprint `Gmlp3urLQv…` is the M5's window is inferred from timing against M4's join record and the 1365 incident record.
- The open-socket lifetime finding from November 13 (XM-08) was not rechecked.
- Whether Away, handoff or automatic worker placement can send work to a fleet machine the owner did not pick. F-03's rating depends on it.
- Computer-use host role: the broker gives it to the newest subscriber holding `terminal:operate` and has no check that the subscriber is the machine's own app (`apps/server/src/computerUse/ComputerUseBroker.ts:33`, `:98-103`). Whether another machine's window can take the role in practice, and so feed that machine's agents its own screen, was not exercised.
- How 1327 behaves in the first-run join is read from the two branches, not run on two machines.
- The second, highest-effort review by another model that the request asks for has not been run.
- Unclear in the request: "Google SSH", "Google console", "M4 Notetaker" (M4 has no project of that name), and "match and use one of them" (possibly Muse, the model behind the earlier reviews).

## Method

Code read with `git show origin/main:<path>` and `git grep`; the 1327 branches read the same way. M4 state through `specweave-studio db query`, `studio_machine_list`, `studio_project_list`, and two small JSON files with no credentials. Pull request state through `gh pr view`. No database file opened, nothing changed in code, grants or settings, and no call made to the M5 or linux-mini. Prior work used as a checklist and re-derived: `.specweave/increments/1326-cross-machine-actions-name-who-acts-servers-refuse-ungranted-destinations-new-devices-need-approval/reports/muse-security-review.md`.
