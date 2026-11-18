# Project threads on a linked copy show under their project, and remote launches follow the project's models

## Problem

On November 18, 2026 the specweave project on m4 listed 13 idle threads that run on M5. The same threads also sat in the sidebar under Chats, the section for conversations with no project, and none of them ran on Fable 5.2, the project's saved model.

What the state shows (m4 `remote-workers.json`, the launch calls in m4's turn items, and a read on M5):

- **Why M5.** Workers of the m4 coordinator started each thread with `studio_thread_launch` and an explicit `machine`, as read-only probes of M5 itself ("is Muse Code installed", "why the Dock shows the old icon"). Nothing routes work to M5 by default (`projectWorkerMachines` is `["local"]`). The machine was right. Nobody recorded a delivery for them, so they stay unresolved.
- **Why Chats.** The threads are in M5's linked specweave copy `aed6d625-728f-47fa-a2be-fca0b276b965`, not in "No project". That copy handed the coordinator to m4: its `coordinatorBinding.state` is `transferred` and its own `coordinatorThreadId` is `null`. `projectPaneTargetForChat` (`apps/web/src/studio/projectPaneThreads.ts`) returns null for any project whose member has no coordinator, so `isProjectOwnedChat` is false and `buildChatGroups` lists the thread as a chat. The project page itself already lists and opens these threads through the link's member list.
- **Why Sonnet and Opus.** Seven launches named Sonnet 5.5 themselves, which is the rule for read-only checks. Six named no model, passed `taskLane: "routine"`, and got Opus 5.5 with the caller's options. A launch on another machine inherits the calling thread's own model (`remoteLaunch.ts`), and `RemoteWorkers.ts` sends it as a named model, so the project's saved model, its tracks and the lane hint are never consulted. `taskLane` and `taskClass` are accepted and dropped. A launch on this machine does consult them (`handlers.ts`).

## Scope

In: the sidebar's rule for which threads belong to a project when a linked copy has no coordinator of its own; the model an unnamed thread on another machine starts on.

Out: settling the 13 threads (the "M5 threads: verify, finish or move" thread owns it); the track lists, their defaults, Sources and the Settings > Models pages (the 1339 thread owns them); `effort`, `provider` and `tier` on a remote launch, which stay refused with their current message; quota boosts and room checks for a remote launch.

## Acceptance Criteria

- [ ] AC-01: A thread an agent started in a linked copy that has no coordinator of its own (its binding is `transferred`, or another linked copy of the same project runs the coordinator) is left out of the sidebar's Chats and opens in the project's right panel with its machine.
- [ ] AC-02: In such a copy, a chat the person started, its forks, and a thread from a server that does not say who started it stay under Chats and open full page.
- [ ] AC-03: An unlinked copy without a coordinator behaves as before: its agent threads stay in Chats.
- [ ] AC-04: With no model named, a thread on another machine starts on the project's own saved model when it has one, whatever model the calling thread runs on.
- [ ] AC-05: With no model named and no saved project model, `taskLane` or `taskClass`, or a project on tracks, picks the model through the same routing a launch on this machine uses; without them a worker's thread keeps the caller's model. Under a work grant the pick follows the local rules: a grant that excludes the project model's sign-in keeps the caller's model, and a grant that lists accounts is never routed.
- [ ] AC-06: A named model is sent as named. When routing on this machine refuses, the launch keeps its baseline model and is not refused, except on tracks with a baseline held back here (billed per use, or billing unknown): then the app picks nothing, the caller's own model is still sent as before, and with none (a coordinator on this host's default) the other machine uses its default. A scratch launch and a server without settings inherit as before.
- [ ] AC-07: The model the app picks (the project's saved model, a track or Auto pick, a coordinator's host default) never starts on the other machine on a sign-in its grant excludes, or on a model that machine holds back (billed per use, or billing unknown). The model the caller itself runs on is tried next, exactly as before this change, so no launch that ran before fails. A named model is unaffected.
- [ ] AC-08: The model is picked once per launch request, however many machines placement tries.

## Approach

1. `apps/web/src/studio/projectPaneThreads.ts`: `chatProjectPaneTarget` tells `projectPaneTargetForChat` when the thread's copy is coordinated elsewhere: the copy is linked, has no coordinator, and either its binding is `transferred` or another linked member of the same logical project has a coordinator. The ownership walk (`isAgentOwnedProjectThread`) already handles a null coordinator, so a person's chat stays a chat.
2. `apps/server/src/mcp/toolkits/project/remoteLaunchModel.ts` (new): `remoteInheritedModel` picks the unnamed model on the asking machine: project's own model (`projectWorkerModel`), else the old inheritance as the baseline, then `autoRoutingApplies` and `routeWorkerTask` with the caller's hints. `remoteLaunch.ts` passes the result as `inheritedModelSelection`, so the other machine still maps it to its own sign-ins and falls back to its default when it lacks the model.
3. `apps/server/src/fleet/remoteWorkerMatching.ts`: `translateModel` takes `picked`; the app's pick does not match a provider the probe marks `allowedByGrant: false` or whose `paidModels` or `heldModels` lists it. `RemoteWorkers.launch` tries `pickedModelSelection` first, then `inheritedModelSelection` unguarded as before (review rounds 1 and 2).
4. `apps/server/src/fleet/remoteWorkerProbe.ts` (new): a machine reports `held` per model from `isHeldSource`; the asking machine reads it into `heldModels`. `readProviders` and `readProviderUsage` moved here from `RemoteWorkers.ts`, which is under 1,500 lines again.

Rejected: forwarding the hints so the other machine routes with its own tracks. The receiving handler needs a baseline model first, and a baseline sent as `modelSelection` is a pin there, so this needs a new wire field and breaks against older machines.

Known limits: a machine older than this change reports no `held` flag, so the pick is not held back there for an unknown-billing model; the caller's own model is inherited there whatever it costs, as before; `effort`, `provider` and `tier` are still refused for a launch on another machine.

Risk: routing judges this machine's sign-ins and limits, not the other machine's. A model with no room here but room there is skipped. Accepted: the other machine still falls back to its default, and a refusal here never stops the launch.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The model is picked on the machine that asks, not on the machine that runs it (reversible; see Rejected).
- D-02: A saved project model wins over a lane hint for a remote launch too, as it does here (confirmed by the 1339 thread, November 18, 2026).
### Open
- none

## Review

Adversarial review by Muse Wonderful (`muse-wonder-full-1.0`) at Extra High, of the diagnosis and the fix, before merge.

Round 1 (commit `f237584de`): fix first, 2 major and 2 minor. Fixed in `04dfb68ab`: the pick follows the caller's work grant; an unnamed model never lands on per-use billing or a grant-excluded sign-in there (AC-07); an id-less logical project no longer counts as the same project; the pick runs once per request (AC-08).

Round 2 (commit `04dfb68ab`): fix first, 1 major and 2 minor. Fixed in `3673b08f7`: machines report `held` models and the pick is never started on one; the guard covers only the pick, so the inherited model runs as before and a launch cannot fail because of it; an empty logical id is not an id.

Round 3 (commit `3673b08f7`): SHIP, 2 minor. Fixed in the next commit: AC-06 reworded to the round 3 design and its test retitled; the capabilities test now asserts the `held` flag, including an unknown-billing model.

## Tasks

### T-01 Linked copy threads belong to their project in the sidebar
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectPaneThreads.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectPaneThreads.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectPaneThreads.test.ts

### T-02 Unnamed remote launches follow the project's models
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunchModel.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunchModel.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/project/remoteLaunchModel.test.ts apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts

### T-03 Adversarial review, merge and release
- AC: AC-01, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectPaneThreads.ts | Test: gh pr view --repo anton-abyzov/specwithcode --json state,mergedAt
