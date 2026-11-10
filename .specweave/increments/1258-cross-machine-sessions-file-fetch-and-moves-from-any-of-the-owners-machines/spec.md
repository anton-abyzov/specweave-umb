# Cross-machine sessions, file fetch and moves from any of the owner's machines

## Problem

A thread on one of Anton's machines cannot start a session on, fetch a file from, or move itself to the machine that coordinates it. On November 7, 2026, a thread on the M1 ("Move club tutorials to EasyChamp") answered "The M4 isn't in the fleet, so I can't reach it" when Anton asked it to create a session on the M4.

Evidence:

- On the M1 (1.0.205), `studio_machine_list` returns `"machines":[]`.
- On the M4, the same call lists M1, M3 and Ministorm as `ready`, plus the M4 itself as an "M4 Max" row with status `needs_grant`.

Cause, traced in source (specwithcode-dev):

- Fleet membership is one-directional. Each machine reads only its own `studio-fleet.json` (`apps/server/src/fleet/FleetTargets.ts`, `apps/server/src/studioFleet.ts`). `addFleetMachine` writes only the caller's file (`apps/server/src/studioFleetJoin.ts`). Adding the M1 on the M4 gives the M1 inbound grants ("Who can run work here") and nothing it can use outward.
- `resolveMachine` (`apps/server/src/fleet/RemoteWorkers.ts`) is shared by `studio_thread_launch {machine}`, `studio_file_transfer` and `studio_thread_migrate`. It finds no M4 row on the M1, so all three fail with `unknown_machine`: "No machine named "M4". studio_machine_list shows the machines this one can use."
- Grants are per direction. `readGrant` (`apps/server/src/fleet/FleetWorkerGrants.ts`) accepts only grants minted for the local machine as coordinator, so the M4's grants on the M1 can never authorize M1 → M4.
- A thread the M4 delegated to the M1 is refused even after reverse pairing:
  - file transfer: `capability_denied` "M4 started this work…"
  - launching back to the M4: `delegation_cycle`
  - migrate: `outside_grant_scope`
- A one-click reverse setup already exists on the target: Settings > Machines > Who can run work here > Allow another machine to run work here (`apps/web/src/components/settings/IncomingWorkerSetup.tsx`). No message or button points to it.
- Self-row: `listMachines` never filters the local environmentId. The CLI `fleet add` skips the own-machine refusal when it cannot discover the local environment (`apps/server/src/cli/fleet.ts`).

## Scope

In:

- Hide and refuse the self-row.
- Agents told about machines that run work here but that this machine cannot use, with the exact one-click step.
- A one-click "Let <machine> use this machine too" on the target machine's card.
- Owner-approved reciprocal access lets a delegated thread launch on, fetch from and migrate to the machine it came from.

Out:

- SSH.
- Any new credential type.
- Automatic grants without the user's click.
- A bulk "connect all machines both ways" action.

## Acceptance Criteria

- [ ] AC-01: `studio_machine_list` never lists the local machine as a remote row, and resolving "m4" or "M4 Max" on the M4 means the local machine. `fleet add` refuses a line from this machine even when the server is not running.
- [ ] AC-02: On a machine that another of the owner's machines runs work on, `studio_machine_list` reports that machine in `incoming` with status `needs_reverse_grant`. Launch, file transfer and migrate aimed at it return `machine_not_authorized`. The message names the one-click step on that machine, "Settings > Machines > <this machine> > Let <this machine> use this machine too", and says what the agent can do meanwhile.
- [ ] AC-03: The target machine's Settings > Machines card for a connected machine that cannot yet run work on it shows "Let <machine> use this machine too". One confirmed click adds the target to that machine's fleet over Connect and allows its workers there, using the existing `setUpIncomingWorkers` flow. Afterwards that machine's `studio_machine_list` shows the target as `ready`.
- [ ] AC-04: A thread delegated by machine A to machine B, where B holds its own owner-approved worker grant on A, can launch a session on A, get a file from or send a file to A with `studio_file_transfer`, and migrate itself to A. The launch runs under B's own grant on A, and the delegation path still blocks multi-hop loops through other machines. Without B's own grant on A, every refusal keeps its current meaning and adds the one-click step from AC-02.
- [ ] AC-06: The reverse grant needs only the target machine's app. On the M4, "Let m1 use this machine too" is enabled with an owner session on the M4 alone. The M4 server uses the management key it already holds for the M1. The M1 accepts that key only for adding and allowing the key's own machine, never a third one. When the setup cannot run, the card states the accurate manual steps as plain text.
- [ ] AC-05: End to end on installed apps: a thread on the M1 lists the M4 as ready, launches a session on the M4, fetches a file from the M4 and migrates a scratch thread to the M4.

## Approach

Server:

- `RemoteWorkers.ts` filters targets with the local environmentId once, at load. This covers listing, resolving and labels.
- `RemoteWorkers.ts` also gains an inbound-aware `noMachines` and `remoteFailure` message. It reads inbound coordinators from `WorkGrants` and `workGrantsSnapshot.ts`.
- `studioFleetJoin.ts` and `cli/fleet.ts` always refuse own-machine adds.
- Contracts `orchestratorMcp.ts` gains the `incoming` rows and the `needs_reverse_grant` status. The tool descriptions in `machines/tools.ts` cite the step.

Delegated work:

- `workGrantPolicy.ts` (`outgoingDelegation`), `remoteLaunch.ts`, `orchestrator/remote.ts`, `fileTransfer/handlers.ts` and `migrate.ts` allow the target only when it is the origin coordinator and this machine holds its own allowed or expiring grant there.
- The call then runs under that grant, and the remaining path still refuses multi-hop cycles.

Web:

- `machinesSettings.logic.ts` gets `canAllowBack`.
- `MachinesSettings.tsx` renders the existing `IncomingWorkerAction` preset to here = this machine and coordinator = that machine, with phrases in all locales.

Rejected:

- SSH.
- Writing the reverse fleet row automatically when allowing workers: it would grant access the user did not click.
- A new pairing protocol: the Connect line plus redeem plus `allowFleetWorkers` already exists.

Risk: relaxing the delegation cycle. It is limited to the direct origin and to a grant the user created on that origin.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: Delegated threads may reach their origin only through the executing machine's own owner-approved grant on that origin. They never reuse the inbound grant. This is the default; the user grant stays the only authority.
- D-02: The one-click action sits on the target machine, which must make the Connect line, and the agent message names that machine. This is the default.

### Open
- none

## Tasks

### T-01 Self-row filter and own-machine refusal
- AC: AC-01 | Files: apps/server/src/fleet/RemoteWorkers.ts, apps/server/src/studioFleetJoin.ts, apps/server/src/cli/fleet.ts, apps/server/src/fleet/RemoteWorkers.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/RemoteWorkers.test.ts apps/server/src/studioFleetJoin.test.ts

### T-02 Incoming rows and actionable reverse-grant messages
- AC: AC-02 | Files: packages/contracts/src/orchestratorMcp.ts, apps/server/src/fleet/RemoteWorkers.ts, apps/server/src/mcp/toolkits/machines/handlers.ts, apps/server/src/mcp/toolkits/machines/tools.ts, apps/server/src/mcp/toolkits/fileTransfer/handlers.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/RemoteWorkers.test.ts apps/server/src/mcp/toolkits/machines

### T-03 Reciprocal access for delegated work
- AC: AC-04 | Files: apps/server/src/fleet/workGrantPolicy.ts, apps/server/src/mcp/toolkits/project/remoteLaunch.ts, apps/server/src/mcp/toolkits/orchestrator/remote.ts, apps/server/src/mcp/toolkits/fileTransfer/handlers.ts, apps/server/src/mcp/toolkits/orchestrator/migrate.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/workGrantPolicy.test.ts apps/server/src/mcp/toolkits/fileTransfer apps/server/src/mcp/toolkits/orchestrator

### T-04 One-click "Let <machine> use this machine too"
- AC: AC-03 | Files: apps/web/src/components/settings/machinesSettings.logic.ts, apps/web/src/components/settings/MachinesSettings.tsx, apps/web/src/components/settings/IncomingWorkerSetup.tsx, apps/web/src/i18n/phrases | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/machinesSettings.logic.test.ts apps/web/src/components/settings/MachinesSettings.test.tsx

### T-05 Installed end-to-end check M1 to M4
- AC: AC-05 | Files: none | Test: manual on installed apps, receipt in ~/.specwithcode/m4/scratch/1258/

### T-07 Reverse grant from one place (follow-up, November 7, 2026)
- AC: AC-06 | Files: packages/contracts/src/environmentHttp.ts, apps/server/src/studioFleetHttp.ts, apps/server/src/environment/ServerEnvironment.ts, apps/web/src/studio/fleet.ts, apps/web/src/components/settings/IncomingWorkerSetup.tsx, apps/web/src/components/settings/MachinesSettings.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/IncomingWorkerSetup.test.tsx

### T-06 Verify and close 1258
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1258
