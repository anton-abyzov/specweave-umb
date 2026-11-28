# Ultracode from a track row reaches named-model launches and fallback hops

## Problem

On November 27, 2026 the owner found many M5 threads in the specweave project running without Ultracode, though he expected every thread to use it, and switched one on by hand (1497 "SpecWeave ledger tools", Opus 5.5).

Two causes, from code at `origin/main` `ab985faa1` (1.0.454) and m4's own data (M5 revoked m4's worker access):

1. **The row switches are off.** m4's saved tracks for this project (`projectSettingsOverrides`) have Daily rows Opus 5.5, GPT-6.2-Sol, Sonnet 5.5 and GPT-6-Luna with effort only and no `ultracode` option; Complex is the built-in order. The owner's screenshot of Project settings matches: the Ultracode pills render the off style of `TrackUltracodeToggle` (plain border, muted text, the word "Ultracode"), which reads like a label that is on. Both the owner and the coordinator read it as on.
2. **Launches that name their model never take a row's Ultracode.** 1441 applies a row's switch only to unnamed launches. Coordinators usually pass `target.model` to `delegate_task` and `modelSelection` to `studio_thread_launch`; a named target is "pinned", skips track routing (`autoRoutingApplies`), and so never reaches `withTrackEntryUltracode`. The same holds for a named launch onto another machine. A thread that falls back onto the same model on another account keeps its own options, so a thread that set none stays without the row's switch.

The Claude workflow mode is on-request (unset) on m4, so a thread with no `ultracode` option runs without it.

## Scope

In: named launches (`delegate_task`, `create_threads`, `studio_thread_launch`, launches onto another machine) and worker launches moved off a full source on a Tracks project take the matching Daily or Complex row's Ultracode (fallback hops in the sweep: D-05); the off pill says "Ultracode off" and is dashed; tests. Out: turning the switches on (the owner's click in Project settings on each machine), the project-wide default (1295), review launches and routines (unchanged by 1441's decision), composer picks a person makes by hand (the composer shows its own switch), existing threads.

## Acceptance Criteria

- [ ] AC-01: A shared helper finds the Daily or Complex row matching a selection's source and model, in the tracks as a launch reads them (`launchTrackLanes`, so the same model on another account of its source counts), and applies that row's Ultracode with `withTrackEntryUltracode`: only on a model that offers the switch, never over an `ultracode` the selection names either way.
- [ ] AC-02: `delegate_task` and `create_threads` with a named model on a Tracks project start with the matching row's Ultracode; a caller's own `ultracode: false` wins; another model gets nothing; review launches are unchanged.
- [ ] AC-03: `studio_thread_launch` with a named model on this machine starts with the matching row's Ultracode from this machine's tracks; a review launch takes only its model. A named launch onto another machine is unchanged (D-06).
- [ ] AC-04: A worker launch moved off a full source (same model on another account, or onto another row) takes the matching row's Ultracode, except a review launch. The fallback sweep reads no row (D-05): a thread keeps its own Ultracode across a hop, and one that turned it off keeps it off on any model that offers the switch.
- [ ] AC-05: A track row's Ultracode pill says "Ultracode off" with a dashed border when off and "Ultracode on" tinted when on.

## Approach

- `packages/shared/src/modelTracks.ts`: `withMatchingTrackRowUltracode(selection, lanes, providers)` and `withTrackRowUltracode(selection, savedLanes, providers, order)` (fits the lanes with `launchTrackLanes`).
- `apps/server/src/project/ProjectDelegation.ts`: `withProjectTrackRowUltracode(settings, project, selection, providers)`, a no-op off Tracks. `apps/server/src/project/TrackRowUltracode.ts`: `namedLaunchOnTrackRow` reads this machine's settings and providers, never fails.
- `OrchestratorMcpService.ts` `routeResolvedTarget`: a pinned target on Tracks (not review) gets the row's Ultracode instead of returning unrouted as is. `handlers.ts` (`studio_thread_launch`) wraps the named selection for a launch on this machine; `remoteLaunch.ts` is unchanged (D-06).
- `providerFallback.ts` `resolveProviderFallback`: with `rowUltracode: true` (only `resolveWorkerLaunchSelection`, a launch), on Tracks and non-review, the target takes the row's Ultracode after `withMovedEffort`; otherwise an explicit off carries across (`withKeptUltracodeOff`). The fallback sweep (`ProviderFallbackWorker.ts`, `unopenableFallback.ts`) is unchanged from `ab985faa1`.
- `ModelTracksSettings.tsx`: off pill dashed, text says on or off.
- Rejected: applying it to composer picks (a person sees the thread's own switch there) and turning the owner's switches on from code (a settings change that is his).
- Risk: a named launch that matched a row now runs Ultracode and uses more of the Claude limit; that is what the row says.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Expected behaviour per the coordinator's brief (owner's use-recommended rule): Ultracode is on for every thread whose track row has it on, including named-model launches that match a row and fallback hops onto one, unless the caller explicitly turns it off.
- D-02 Review launches and routines stay as 1441 decided.
- D-03 Existing m4 threads are not switched on: no row on m4 has Ultracode on, so none qualifies.
- D-04 (superseded by D-05) Review rounds 2 to 6 tried to give sweep hops the row's Ultracode while keeping routines' turns, the coordinator and untraceable server turns off; each round found another path that granted it without proof of origin (`reports/reviews/review-gpt-6.2-sol-2.md` to `-7.md`).
- D-05 The fallback sweep never reads a row's Ultracode. A thread launched from a row with it on carries it across hops in its own options; a same-model move keeps them; a lane-order hop takes the row entry's saved options as before 1506; an explicit off carries across. Known limits, unchanged from before 1506: a thread that never had Ultracode does not gain it by moving onto a row, an explicit choice is lost through a model that lacks the switch, and a lane-order hop can hand a routine's turn a row entry's saved Ultracode (follow-up, not in this increment).
- D-06 A named launch onto another machine takes no row's Ultracode: the sender only knows the other machine's model slugs, not whether its model offers the switch there, so it could save an option that machine's Claude never applies (review round 8). The receiving machine does not apply its own rows to it either. An unnamed launch onto another machine keeps 1441's behaviour. A batch or `delegate_task` review moved off a full source passes its review intent to the room check.
### Open
- none

## Review

Reviewer: a non-Claude family other than Copilot (out of quota).

## Tasks

### T-01 Shared row helper and fallback hops
- AC: AC-01, AC-04 | Files: `repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.ts`, `repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.test.ts`, `repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts`, `repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.trackUltracode.test.ts` | Test: `node node_modules/vite-plus/bin/vp test run packages/shared/src/modelTracks.test.ts packages/shared/src/providerFallback.trackUltracode.test.ts`

### T-02 Named launches take the row's Ultracode
- AC: AC-02, AC-03 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectDelegation.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/TrackRowUltracode.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/TrackRowUltracode.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpTaskRouting.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/launchWorkspace.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts` | Test: `node node_modules/vite-plus/bin/vp test run apps/server/src/project/TrackRowUltracode.test.ts apps/server/src/mcp/OrchestratorMcpTaskRouting.test.ts apps/server/src/mcp/toolkits/project/launchWorkspace.test.ts apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts`

### T-03 The off pill says off
- AC: AC-05 | Files: `repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.effort.test.tsx` | Test: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/ModelTracksSettings.effort.test.tsx`
