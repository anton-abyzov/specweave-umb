# Show the correct connection action for a saved Connect machine

## Problem

In 1.0.398, a Mac displays both “Connect” and “Connect machine” for a Windows PC whose SpecWithCode Connect route is already saved. The same screenshot shows “Connect” beside another machine labelled “Online”. Windows separately confirmed the Mac’s device approval after the owner entered its code. A saved relay route has an environment ID, while the machine card compares only direct HTTP origins. This explains the redundant pairing action. The ordinary desktop session needs a separate readback.

## Scope

The saved-route check shared by Settings > Machines and its connection details, plus regression coverage. The current app connection, device approvals and the grants in each direction keep their existing meanings.

## Acceptance Criteria

- [ ] AC-01 A saved relay route for the same environment, preferred or alternate, matches that machine’s Connect address. The header and expanded details stop offering to pair it again, including while its existing session connects.
- [ ] AC-02 A genuinely missing or changed direct address keeps its existing repair action. A relay route on a different environment and a rejected device cannot count as a successful saved connection.
- [ ] AC-03 The view still uses its current connection state for Online, Connecting or an error. A work grant or saved route alone cannot mark a machine online or grant access.

## Approach

Use the existing relay target identity alongside direct origins in the shared saved-route check. Use the fleet machine’s advertised address to select the matching route. Keep the handling for moved direct routes and rejected devices. Exercise both UI consumers and the public saved-route helper with real catalog shapes.

## Tasks

### T-01 Recognize saved Connect routes on the machine card
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/fleetAutoConnect.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/fleetAutoConnect.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/usePrimaryFleet.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StudioFleetConnections.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StudioFleetConnections.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/studio/fleetAutoConnect.test.ts src/components/settings/machinesSettings.logic.test.ts src/components/settings/StudioFleetConnections.test.tsx

## Review

Independent review of the candidate checks both Settings views, errors, moved addresses and the boundary between saved routes, live sessions and permissions. Release the display fix after the review and green CI. Verify and close 1430.
