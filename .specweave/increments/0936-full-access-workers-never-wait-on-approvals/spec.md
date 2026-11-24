# Full access workers never wait on approvals

## Problem

On 2026-10-17/18 a Codex worker ("Complete pending handoff work") on the M3, child of a Full access coordinator restored from a machine handoff, sat 15h on a command approval for `cat AGENTS.md`, shown as "Running 15h / No activity". Causes: the M3 ran 1.0.42 (Full access auto-approval shipped in 1.0.44) and its updater waited forever for quiet because of that same open request; workers lost Full access through the project override, the handoff (destination default) and silent remote grant clamps; the reactor only reacted to new events; the UI read a person-blocked run as stalled.

## Scope

In: specwithcode-dev server mode inheritance, Full access approval reactor, update-quiet rule, waiting/stalled status and Needs you. Out: changing the Codex/Claude adapters' policy mapping.

## Acceptance Criteria

- [ ] AC-01: Workers created, delegated, forked or launched remotely by a Full access coordinator run Full access (Codex and Claude), even when the project default is lower; a lower caller never gets a higher mode; machine grants still cap.
- [ ] AC-02: A machine handoff carries the source coordinator's mode to the destination project.
- [ ] AC-03: On Full access no approval reaches the person: prompts are accepted on arrival, on start (left over from before), every 2 minutes, when a coordinator is raised (its app-owned workers too) and on retry after a failed answer; confirm-only MCP elicitations included; questions, sign-in and field elicitations still go to the person.
- [ ] AC-04: A run blocked on the person reads "Waiting on you" (header, subagent rows, remote worker cards) and is listed in Needs you, never "No activity"; a run quiet 30+ minutes with nothing in flight is listed as stalled.
- [ ] AC-05: An approval left 30+ minutes with no activity no longer blocks automatic updates: the turn is interrupted resumably; questions and sign-ins keep blocking.

## Approach

Orchestrator `creationRuntimeMode` keeps an agent caller's (already capped) mode; MachineHandoff bundle `context.runtimeMode` applied through ProjectRuntimeAccess; remote launch reports `runtimeMode`/`runtimeModeLoweredFrom`; FullAccessApprovals sweep, retry fiber, fan-out to `subagent` children; run health `awaitingPerson`; ServiceUpdatePreparation stale-wait release for approval-only threads with a race re-check.

## Decisions

### Asked
- D-01 On Full access, ask for any confirmation? → never (user, 2026-10-18)
### Defaulted (change any before sw-do)
- D-02 Stale questions/sign-ins still block automatic updates (shown in Needs you) → yes
- D-03 Stalled threshold → 30 minutes, keeping the long-command allowance
### Open
- none

## Tasks

### T-01 Full access inheritance, handoff mode and remote launch result
- AC: AC-01, AC-02 | Files: repositories/../specwithcode-dev apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/RemoteWorkers.ts | Test: vp test run Orchestrator.project-access.test.ts MachineHandoff*.test.ts RemoteWorkers.test.ts remoteWorkerMatching.test.ts remoteLaunch.test.ts

### T-02 Full access approval sweeps, retries and fan-out
- AC: AC-03 | Files: apps/server/src/orchestration-v2/FullAccessApprovals.ts | Test: vp test run FullAccessApprovals.test.ts

### T-03 Waiting and stalled status, Needs you
- AC: AC-04 | Files: packages/client-runtime/src/state/models.ts, apps/web/src/studio/overviewModel.ts, apps/web/src/components/chat/ThreadMetaRow.tsx, apps/server/src/fleet/RemoteWorkerFollower.ts | Test: vp test run threadRunHealth.test.ts overviewModel.test.ts ThreadMetaRow.test.tsx RemoteWorkerFollower.test.ts

### T-04 Hung approvals stop blocking updates
- AC: AC-05 | Files: apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts | Test: vp test run ServiceUpdatePreparation.staleWaits.test.ts ServiceUpdateCleanup.test.ts
