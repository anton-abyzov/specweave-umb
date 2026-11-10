# Machines settings: one-direction access model

## Problem

On November 8, 2026 the user could not tell what to allow so that Ministorm's coordinator can start workers on m4. The coordinator said "allow them in Settings > Connections on m4". Settings > Connections is the same page as Settings > Machines, and the step was on the wrong machine.

What the code shows (public `anton-abyzov/specwithcode` main `f2e360f5c6`, both machines on 1.0.207):

- The visible "Allow workers" link on a card under "Workers from this machine" links to `/settings/machines`, the page it sits on. The real Allow workers button is inside the collapsed "Access, routes and worker permissions" section, which repeats the card's name, status and buttons.
- "Workers from this machine" on another machine's card means "agents on the machine you are using may start work on that machine". The user read it as that machine's workers, so m4's ministorm card ("Workers allowed") read as "ministorm may use m4".
- "Work it may run here" and "Let ministorm use this machine too" are the other direction with different words. On 1.0.207 that button is disabled with "Manage access is needed on both m4 and ministorm" and a line that sends the user back to Allow workers on the other machine.
- "Add for agents" and "Connect both ways" are further steps of the same two directions with their own words. "Remote control" opens that machine's projects as the person and needs no worker permission, but reads like a permission.
- Coordinator errors name "Settings > Connections" and buttons that do not exist under that name.

## Scope

In: Settings > Machines card wording and layout in `apps/web`, the coordinator error and tool texts in `apps/server`, the 8 phrase files, tests. Out: the grant storage and protocol, the "Who can run work here" limits editor (kept as the place to set project and sign-in limits), team rules.

## Acceptance Criteria

- [ ] AC-01: Each machine card shows exactly two access lines, "Agents here can start work on {machine}" and "Agents on {machine} can start work here", each with a status and, when not allowed, one working button; no link on the card points to the page it is on.
- [ ] AC-02: The Allow workers control is rendered on the visible line, not inside the collapsed section, and the collapsed section is named "Connection details" and holds only routes, pairing, readiness, terminal and removal.
- [ ] AC-03: "Let X use this machine too" and "Work it may run here" are replaced by the second access line with an "Allow {machine}" button; "Add for agents" sits on the first line as its first step.
- [ ] AC-04: "Remote control" is renamed "Open projects" (or "View projects" without the operate scope), and the page intro says that opening another machine's projects needs no worker permission.
- [ ] AC-05: "Connect both ways" becomes "Its app sees this machine" with a "Make pairing link" button; "Connect automatically" says what it does on this device.
- [ ] AC-06: Coordinator tool errors and `studio_machine_list`/`reverseGrantStep` texts name Settings > Machines, the card and the line by their new names, on the correct machine.
- [ ] AC-07: Web and server unit tests for the changed components and texts pass, typecheck passes, and headless before and after screenshots are saved.

## Approach

`StudioFleetConnections.tsx`: `renderMachine` also receives the workers control, and omits it from the collapsed controls when composed. `MachinesSettings.tsx`: the two lines, renamed details, `AllowBack` label, intro. `MachineRemoteControl.tsx`: labels. `RemoteWorkers.ts`, `incomingMachines.ts`, MCP tool description: texts. Rejected: merging the "Who can run work here" editor into each card (large, and it is where incoming limits are edited).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Line labels use "here" and the other machine's name, so error texts stay valid on every machine → default.
- D-02 Keep `/settings/connections` as an alias route for old links; all texts say Settings > Machines → default.
### Open
- none

## Tasks

### T-01 Mockup of the simplified card
- AC: AC-01, AC-03, AC-04, AC-05 | Files: scratch mockup HTML | Test: headless render saved as PNG

### T-02 Two access lines and moved Allow workers control
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/settings/MachinesSettings.tsx, StudioFleetConnections.tsx | Test: npx vitest run apps/web/src/components/settings

### T-03 Remote control, connect both ways, connect automatically texts
- AC: AC-04, AC-05 | Files: MachineRemoteControl.tsx, MachinesSettings.tsx, ConnectionsSettings.tsx | Test: npx vitest run apps/web/src/components/settings

### T-04 Coordinator error and tool texts
- AC: AC-06 | Files: apps/server/src/fleet/RemoteWorkers.ts, incomingMachines.ts, MCP tool description | Test: npx vitest run apps/server/src/fleet

### T-05 Screenshots, typecheck, PR, merge, release
- AC: AC-07 | Files: none | Test: bun typecheck; headless screenshots

### T-06 Verify and close 1263
- AC: AC-07 | Files: none | Test: specweave verify 1263
