# Ultracode from a track row reaches named-model launches and fallback hops

## Problem

On November 27, 2026 the owner found many M5 threads in the specweave project running without Ultracode, though he expected every thread to use it, and switched one on by hand (1497 "SpecWeave ledger tools", Opus 5.5).

Two causes, from code at `origin/main` `ab985faa1` (1.0.454) and m4's own data (M5 revoked m4's worker access):

1. **The row switches are off.** m4's saved tracks for this project (`projectSettingsOverrides`) have Daily rows Opus 5.5, GPT-6.2-Sol, Sonnet 5.5 and GPT-6-Luna with effort only and no `ultracode` option; Complex is the built-in order. The owner's screenshot of Project settings matches: the Ultracode pills render the off style of `TrackUltracodeToggle` (plain border, muted text, the word "Ultracode"), which reads like a label that is on. Both the owner and the coordinator read it as on.
2. **Launches that name their model never take a row's Ultracode.** 1441 applies a row's switch only to unnamed launches. Coordinators usually pass `target.model` to `delegate_task` and `modelSelection` to `studio_thread_launch`; a named target is "pinned", skips track routing (`autoRoutingApplies`), and so never reaches `withTrackEntryUltracode`. The same holds for a named launch onto another machine. A thread that falls back onto the same model on another account keeps its own options, so a thread that set none stays without the row's switch.

The Claude workflow mode is on-request (unset) on m4, so a thread with no `ultracode` option runs without it.

## Scope

In: named launches (`delegate_task`, `create_threads`, `studio_thread_launch`, launches onto another machine) and fallback hops on a Tracks project take the matching Daily or Complex row's Ultracode; the off pill says "Ultracode off" and is dashed; tests. Out: turning the switches on (the owner's click in Project settings on each machine), the project-wide default (1295), review launches and routines (unchanged by 1441's decision), composer picks a person makes by hand (the composer shows its own switch), existing threads.

## Acceptance Criteria

- [ ] AC-01: A shared helper finds the Daily or Complex row matching a selection's source and model, in the tracks as a launch reads them (`launchTrackLanes`, so the same model on another account of its source counts), and applies that row's Ultracode with `withTrackEntryUltracode`: only on a model that offers the switch, never over an `ultracode` the selection names either way.
- [ ] AC-02: `delegate_task` and `create_threads` with a named model on a Tracks project start with the matching row's Ultracode; a caller's own `ultracode: false` wins; another model gets nothing; review launches are unchanged.
- [ ] AC-03: `studio_thread_launch` with a named model, here or onto another machine, starts with the matching row's Ultracode from this machine's tracks; a review launch takes only its model.
- [ ] AC-04: A thread on a Tracks project that falls back onto a row with Ultracode on runs with it, including the same model on another account when the thread set none, and a worker launch moved off a full source; a thread that turned it off keeps it off; review fallbacks, a routine's route and a coordinator turn are unchanged.
- [ ] AC-05: A track row's Ultracode pill says "Ultracode off" with a dashed border when off and "Ultracode on" tinted when on.

## Approach

- `packages/shared/src/modelTracks.ts`: `withMatchingTrackRowUltracode(selection, lanes, providers)` and `withTrackRowUltracode(selection, savedLanes, providers, order)` (fits the lanes with `launchTrackLanes`).
- `apps/server/src/project/ProjectDelegation.ts`: `withProjectTrackRowUltracode(settings, project, selection, providers)`, a no-op off Tracks. `apps/server/src/project/TrackRowUltracode.ts`: `namedLaunchOnTrackRow` reads this machine's settings and providers, never fails.
- `OrchestratorMcpService.ts` `routeResolvedTarget`: a pinned target on Tracks (not review) gets the row's Ultracode instead of returning unrouted as is. `handlers.ts` (`studio_thread_launch`) and `remoteLaunch.ts` wrap the named selection.
- `providerFallback.ts` `resolveProviderFallback`: with `rowUltracode: true` (thread limit hops in `ProviderFallbackWorker.ts`, `unopenableFallback.ts`, `resolveWorkerLaunchSelection`), on Tracks and non-review, the target takes the row's Ultracode after `withMovedEffort`. The routine route (`ScheduledTaskProviderRoute.ts`) and the coordinator turn do not pass it.
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
- D-04 Fallback hops skip a row's Ultracode for the project coordinator and for any thread a routine runs in (its own or one it posts into). A stopped run does not say whether a routine's turn or a person's ended, so a person's turns in a routine-bound thread stay off too; off is the safe side. The routine lookup is read again under the project lock (review round 3).
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
