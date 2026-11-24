# Blocker count gate, routed to increment 1278

Decision: Anton, November 11, 2026 (1304 D-10, recorded in 1278 as D-07): **one owner, counted once**.

- A blocker stays visible wherever its thread is opened, with its machine named.
- Only the owner machine's app raises badges and "Needs you".
- Another app raises them only when the owner has nobody in front of it.
- The phone is unchanged.

The coordinator routed the build to 1278 (notify-active), because "nobody in front of it" is the presence election 1278 already specifies (`hostEnvironmentId`, `lastInteractionAt`, `notificationTarget`). Counts and popups must read one election.

Paths are in `anton-abyzov/specwithcode`, read at `origin/main` `05b4d5477e`.

## Owner machine

In this order:

1. The machine of the coordinator that launched the thread. The coordinator's machine tracks its remote workers (`apps/server/src/fleet/RemoteWorkerStore.ts:26`, `callerThreadId`, `machineId`, `remoteThreadId`), and the web app already reads them (`projectRemoteAttentionAtom`, used in `apps/web/src/studio/useProjectAttention.ts:42`).
2. The thread's `ownerMachineId` (`packages/contracts/src/threadExecution.ts`: a thread lives on its owner machine and runs on one execution machine; handoff moves execution, never ownership).
3. The machine that serves the thread (`environmentId`).

A project can have a coordinator on each machine (0969), so the owner is per thread, never per project. A plain chat has no coordinator and falls to rule 2 or 3.

## Raise rule

An app with own machine H (its primary environment) and client id C raises an item served by machine E with owner O when:

- H equals O, or
- E's `notificationTarget.clientId` is C (project-window suffix stripped, as 1278 AC-03 does).

Never hide on doubt: when E returns no `notificationTarget` (older server), the read fails or times out, the target is `null`, or O is unreachable from this app, the app raises the item as it does today.

Why the target and not "O has no foreground lease": the target is already "the device a person is using". If the owner's app is in the foreground it is the target, so no other app counts. If the person moved to another machine, that app is the target and counts. One election, so a badge never disagrees with a popup.

## Surfaces

| Surface | Today | Change |
|---|---|---|
| Sidebar project badge | `apps/web/src/components/studio/shell/StudioSidebar.tsx:369`, `aggregateProjectAttention` (`packages/client-runtime/src/state/projectAttention.ts:227`) over every paired machine | Count raised items only |
| Project page count | `apps/web/src/components/studio/ProjectWorkspaceSurface.tsx:1411`, `useProjectAttention` | Count raised items only |
| Overview "Needs you" | `apps/web/src/components/studio/StudioOverview.tsx:207`, `deriveSessions` (`apps/web/src/studio/overviewModel.ts:123`) | List and count raised items; one quiet line "N more on <machine>, in use there" that sets the machine scope (`StudioOverview.tsx:323`) |
| Threads pane rows, "Blocked" word | `apps/web/src/studio/shellModel.ts:449`, `:650` | Unchanged: shown in place, machine named |
| Chat list "Needs you" filter | `apps/web/src/studio/shellModel.ts:297` | Unchanged: a filter the person chose |
| Dock, taskbar and favicon badge | `apps/web/src/threadNotifications.ts:60`, fed by `ThreadNotificationCoordinator.tsx` | Target app and the owner machine's app only. This narrows 1278 AC-04 ("every other app counts the alert in its badge") |
| OS popup and sound | 1278 AC-03 | Unchanged: target only |
| Phone | `apps/server/src/relay/AgentAwarenessRelay.ts:211` | Unchanged |

## Conflict to settle in 1278

1278 D-01 (November 10) says "Other machines badge". D-10 (November 11) says only the owner machine's app raises badges. 1278 AC-14 records the newer answer: an app that is neither target nor owner adds no badge entry. AC-04 and the Minisforum line of AC-07 ("only badges") need that reading.

## Found on the way, not routed as criteria

- A remote worker whose final report has a **Blockers:** part wakes its coordinator only with the generic "finished" wake. `waitsOnPerson` reads pending requests, never the report (`apps/server/src/fleet/RemoteWorkerFollower.ts:302`), and `studio_thread_read` has no `reportedBlocker` field (`apps/server/src/mcp/OrchestratorMcpService.ts:932`). An app on the coordinator's machine that is not paired with the worker's machine therefore never counts that blocker. With the usual pairing it does.
- Phone pushes ignore report blockers and sign-in requests (`packages/shared/src/agentAwareness.ts:87`): a Blocked thread publishes as "Agent finished".
- A machine-level update wait is no longer a question after 1304: the rollout reports the machine as `deferred` and the fleet refusal says it is the owner's setting, not a blocker.

Full maps: `map-blocker-surfaces-ui.md` and `map-blocker-model-server.md` beside this file.
