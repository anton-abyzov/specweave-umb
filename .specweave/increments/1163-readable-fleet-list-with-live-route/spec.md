# 1163 Readable fleet list with live route

## Problem

`specwithcode fleet list` joins each machine's fields with tabs and has no header. Rows run past 100 characters and wrap mid-word in a normal terminal. Addresses print Tailscale first although traffic tries Connect first, and "via Connect" hides whether the Tailscale fallback works: on November 1, 2026 the M1 and M3 read "via Connect" while their Tailscale nodes had been offline for a day.

The machine's own row is checked through its own Tailscale address and reports "no management token", which reads like a fault and would report the machine unreachable whenever its Tailscale is off.

## Scope

In: `fleet list` output and probing. Out: the fleet HTTP snapshot, Settings UI, status page, `discoverFleet` and the routing rules in `fleetTransport`.

## Acceptance Criteria

- [ ] AC-01: `fleet list` prints a header and aligned columns MACHINE, STATUS, ROUTE, FALLBACK, and no row is wider than 74 columns for the current fleet's ids and addresses
- [ ] AC-02: ROUTE names the address that answered, Connect first, as traffic does; FALLBACK names the other address and whether it answered
- [ ] AC-03: Each address prints on its own line under its machine, Connect before Tailscale
- [ ] AC-04: The row whose environment id is this machine's says `this machine`, has no token note, and is probed over loopback only, so it stays reachable when Tailscale is off
- [ ] AC-05: All addresses are probed in parallel with a 2.5 second limit each, so a list with every machine down prints and exits in under 4 seconds beyond CLI startup, even when a peer drops packets. A local service that accepts connections but does not answer adds its own 2.5 second probe first, about 5 seconds in total
- [ ] AC-06: Probes send no credentials, and a token never appears in the output
- [ ] AC-07: An address that answers as a different machine is reported, not used as a route
- [ ] AC-08: A machine whose management token cannot cross Connect says so in a note, because its management traffic takes Tailscale whatever ROUTE reads

## Approach

New `apps/server/src/fleet/fleetListTable.ts`: `probeFleetList` probes every address with `checkIdentity` through a one-shot `node:https` GET with the short timeout, because aborting a global fetch leaves its connect holding the process open for ten seconds; `renderFleetTable` lays out the rows. `apps/server/src/cli/fleet.ts` takes this machine's id and loopback answer from `discoverPairTarget`, which probes the running service, and falls back to the `environment-id` file when no service answers.

Rejected: extending `discoverFleet`. It stops at the first answer, which is what the server wants, and it backs the HTTP snapshot and status page, which are out of scope.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Name and token note sit on detail lines under the row, not in columns → Anna's 18-character id and name together overflow an 80-column terminal (reversible).
- D-02 A fallback that fails reads `Tailscale no answer`, not `offline` → a probe cannot tell an offline node from a blocked route (reversible).
- D-03 If no local service answers, this machine's row reads `unreachable` with the note `service not answering` (reversible).
### Open
- none

## Tasks

### T-01 Probe and render the table
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: apps/server/src/fleet/fleetListTable.ts, apps/server/src/fleet/fleetListTable.test.ts, apps/server/src/cli/fleet.ts, apps/server/src/cli/fleet.test.ts | Test: cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/fleetListTable.test.ts src/cli/fleet.test.ts

### T-02 Merge, release and read the installed output
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specwithcode fleet list

Verify and close 1163.
