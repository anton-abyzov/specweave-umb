# Copies follow the real main: one resolver for notice, switch and send

## Problem

Anton, November 17, 2026, on the M5 with 1.0.338 (which contains PR #536, `6075780c`). The specweave copy's message box read "Main for specweave is m4", but the hint said "Making M5 main moves the coordinator and its conversation here from m1". "Make M5 main" opened the move dialog from m1. The box could not send at all.

Evidence (read through `specweave-studio db query` on each machine; summary in `~/.specwithcode/m4/scratch/2026-11-17-m5-make-main/evidence.md`):

- m4 `1332065e`: `logical:bfc9fb16`, binding epoch 0 active, roster m4, linux-mini, M5. No change since October 30.
- m1 `mcp:d580ecec` (`/Users/antonabyzov/swc-projects/specweave`): joined on November 4 as a copy (epoch 1, successor linux-mini). On November 15 at 03:36Z, `project-start-coordinator:8a9fe27d…` made it active at epoch 2 with no predecessor. Its roster is m4, linux-mini, m1, without the M5.
- `copyRoles` (`apps/web/src/studio/projectDomain.ts`) ranked live coordinators by epoch, so m1's side coordinator became "main" for the switch. The notice instead followed the M5's own successor (m4). Two resolvers on one page disagreed.
- A copy's box was off by design in 1372 (Out: "Sending from the copy without leaving its page").

## Scope

In:
- The web resolver ranks the coordinator the link names first.
- The page's notice, the switch and the send route use that one resolver.
- A copy's message box sends to main's coordinator while main is connected and the window may run work there.
- Translations, tests and a headless repro of the M5 state.

Out:
- Repairing m1's stale record. That is a data migration, asked separately.
- Server-side changes to `startCoordinator`'s epoch.
- Attachments on a routed send.

## Acceptance Criteria

- [x] AC-01: With a coordinator started beside main at a higher epoch (no predecessor), a copy's main is the coordinator its own successor names. "Make {copy} main" moves from that main, and the notice names the same machine.
- [x] AC-02: After the switch (the new main is followed by the old one, and the side coordinator still has a higher epoch), the new main stays main. A copy that took over by naming a predecessor still leads over the main it replaced. With nothing naming a main, the newest epoch decides as before.
- [x] AC-03: On a copy whose main is connected and may run work from this window, the message box is on. The placeholder reads "Message {machine}'s coordinator for {project}.", Send names main's machine, and Send delivers the text to main's coordinator (`projects.coordinatorSend` on main's machine), then opens main's page. The notice says so instead of "Nothing is sent from here". With main offline or read-only, the box stays off as before.
- [x] AC-04: A headless repro builds the M5 records (m4 epoch 0 main, m5 its copy, m1 a side coordinator at epoch 2), runs the real resolver, and checks: main m4 in the notice and the hint, the move source m4, and a typed "time now?" routed to m4. Light and dark, plus all eight languages for the existing strings.

## Approach

- `endorsedCoordinators` in `projectDomain.ts` collects the end of each copy's successor chain, plus any active copy with a predecessor. `logicalCoordinators` and `copyRoles` rank those first, then epoch, then key.
- `followedMain` in `makeMain.ts` is the copy's main by that rule. `ProjectWorkspace` uses it for the notice (falling back to the successor chain), so the switch and the notice agree.
- `routeToMain.ts` (pure) and `useRouteToMain.ts` route the copy's send. `ProjectWorkspaceSurface` turns the box on only when routing is possible.
- Rejected:
  - Roster filtering (a main must list the copy). The M5 case works, but it fails after the switch, because m1 lists m4.
  - Changing `startCoordinator`'s epoch on the server. A wire and fencing change, out of scope.
- Risk: a person who started a coordinator on purpose to lead loses "main" to the followed one. "Make main" (move or takeover) is the way to lead, per 1372.

## Decisions

### Asked
- D-01 Every copy should be able to start work, or at least route to main → route to main (Anton's request, November 17, 2026). Reverses 1372's Out item.
### Defaulted (change any before sw-do)
- D-02 A routed send carries text only, and opens main's page after the send → default.
### Open
- D-03 Repair m1's stale record (`mcp:d580ecec`, epoch 2 active): ask Anton. It is a data migration.

## Tasks

### T-01 One main resolver
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectDomain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspace.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectDomain.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/makeMain.test.ts src/studio/projectDomain.test.ts

### T-02 Route a copy's send to main
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/routeToMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useRouteToMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/routeToMain.test.ts src/components/studio/CoordinatorBlockedNotice.test.tsx src/i18n

### T-03 Headless repro of the M5 state
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/coordinator-menu/vite.config.ts && node apps/web/tests/coordinator-menu/verify.mjs

### T-04 Review, release and check on the M5
- AC: AC-01, AC-03 | Files: none | Test: muse-wonder-1.0 xhigh review; `bash scripts/release/request-release.sh --by` then `--released`; on the M5, Make M5 main opens the move from m4 and a typed message reaches m4's coordinator
