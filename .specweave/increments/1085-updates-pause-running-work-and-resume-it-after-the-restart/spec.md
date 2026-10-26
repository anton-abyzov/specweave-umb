# Updates pause running work and resume it after the restart

## Problem

An automatic install waits for a fully quiet service. The update agent (`scripts/studio-fleet/update_agent.py` `quiet_then_install`) refuses on any running turn, agent process or open question, and tries again on its next launchd pass ten minutes later, forever. A long turn keeps "Waiting to install SpecWithCode X · Waiting for running work to stop" up for hours (owner, 2026-10-26, screenshot of 1.0.93). Only "Update now" drains work, and the turns it stops already continue after the restart (`RestartContinuation.ts`, `continueThreadsAfterServerUpdate`, on by default).

Second failure the same day: at 16:39–16:49Z the live `statev2.sqlite-wal` and `-shm` were deleted while the service wrote to them. Every update then refused with "The SpecWithCode service is using a database log that was deleted from disk. Restart SpecWithCode, then update". Cmd+Q cannot do that: the background service keeps running, and `database_restart_refusal` restarts a detached service only for a held Update now request, which the person had no way to reach. Tools that open the live database directly (and AGENTS.md guidance that tells agents to run `specweave-studio db query --base-dir <live home>`) are the likely cause.

## Scope

In: automatic installs wait at most a grace period, then pause running work and install; a visible countdown with Install now and Later; turns paused for an update continue with a note after the restart; Update now / Try again restart a service on a deleted log safely by themselves; the refusal text stops asking for a restart the person cannot do; tools and guidance stop opening the live database while the service runs. Out: cutting a release; touching the live M4 service; handoff-mode checkpoints (they never resume update-ended runs and are not needed here).

## Acceptance Criteria

- [ ] AC-01: An automatic install that has been refused for running work for `pauseWorkAfterMinutes` (default 10) drains the service the way Update now does (`service prepare-update --stop-work --hold --reason install`), writes a forced request and installs in the same agent run; before the grace it keeps waiting. A "Later" postpone pushes the pause back (default 1 hour). Fleet tests cover: waits before grace, drains and installs after, postponed, drain unavailable falls back to waiting.
- [ ] AC-02: While an automatic install waits for running work, the sidebar says when running work will be paused ("Installs at 2:41 PM. Running turns pause then and continue after the update"), with Install now (the existing Update now flow) and Later. Web tests cover the copy and both actions.
- [ ] AC-03: A turn paused by an update drain continues after the restart with "Continue where you left off." and its update label, from the automatic path as from Update now; a turn the person stopped never continues. Server integration test covers the automatic drain path.
- [ ] AC-04: With an explicit Update now or Try again request pending, a service on a deleted database log is stopped with SIGTERM (so it folds the deleted log into the database), started again and the update continues, without needing a hold; with no request it still never restarts. The person-facing refusal no longer says "Restart SpecWithCode, then update"; it says Update now or Try again fixes it. Fleet tests cover both.
- [ ] AC-05: `specweave-studio db query` / `db snapshot` and repository scripts never open the live `statev2.sqlite` read-write or without `readonly_shm` while the service runs, and project guidance (AGENTS.md) no longer tells agents to query the live database directly. The cause of the 2026-10-26 deletion is named in Decisions with evidence.

## Approach

1. Agent (`update_agent.py`, new `update_agent_pause.py` if the 1500-line cap needs it): record `automaticWaitSince` per version in state.json on the first busy refusal of an automatic pass; publish `automaticPauseAt`; once due and not postponed, call the service CLI drain (reuse `fleet_rollout.ServiceHold`, moved where the agent bundle can import it) and `update_request.write_request(force=True)`, then let `run_once`'s second iteration install. Config keys `pauseWorkAfterMinutes`, `automaticPausePostponedUntil` in `DEFAULT_CONFIG`/`load_config`, `update_request.DEFAULT_SETTINGS`, desktop `ServiceAgentConfig`.
2. Desktop: carry the new keys through `buildServiceAgentConfig`; read `automaticPauseAt` into `StudioServiceUpdateState`; a "postpone automatic pause" call.
3. Web: `describeAutomaticInstallWait` and the sidebar hint show the pause time with Install now and Later.
4. Resume: verify the automatic drain path ends runs `interrupted` with cause `service_update` so `continueUpdateInterruptedRuns` picks them up; add the integration test.
5. update.py `database_restart_refusal`: for `detached` with a pending forced request (Update now / Try again), restart via `stop_then_start_service` without requiring `assert_held`; keep the other guards (other openers, RESTART_EVERY, same pid). Change `DETACHED_DATABASE`/`LOCKS_LOST` texts and the agent's restart-needed error.
6. Live-database openers and guidance: from the forensics.

## Decisions

### Asked
- D-01: Automatic installs may pause running work → yes (owner, 2026-10-26: "we should be abandoning this work and restarting those after the update"). Supersedes 0991 D-01 for running turns; questions closed by the drain are recorded and asked again as with Update now (0991 D-03).
### Defaulted (change any before sw-do)
- D-02: Grace before pausing an automatic install → 10 minutes of refused waiting, setting `pauseWorkAfterMinutes`; Later postpones 1 hour.
- D-03: `continueThreadsAfterServerUpdate` off still means no automatic continuation: it is an explicit per-project opt-out (default on).
- D-04: A deleted log restarts without a hold only for an explicit request (Update now / Try again or an automatic install past its grace, which writes one); SIGTERM, never SIGKILL, as today.
- D-05: The automatic pause is gated on capability, not version: it runs only when the service writes `userdata/secrets/local-cli-credential.bin` (PR #847), so an older CLI never opens the live database read-write during a drain. Until #847 ships, automatic installs keep waiting for quiet and the waiting line offers Update now.
- D-06: Deleted-log forensics (2026-10-26): window 13:28-16:49Z; most likely cause is `specweave-studio pair` (desktop attach runs `pair --ttl 2m`, 11 runs 14:43-16:27Z) opening statev2.sqlite read-write through EnvironmentAuth after the service had lost its locks. What made the service lose its locks first is still unknown. `db query` is read-only (`readonly_shm`) and safe.
- D-07: Split: PR #845 (agent pause, Update now restarts on a deleted log, Install now/Later) merged 2026-10-26 as 6220c70; PR #847 (CLI through the running service, owner marker, loopback-only bearer) is an auth change and waits for the owner's OK.
### Open
- none

## Tasks

### T-01 Agent pauses work after the grace and installs
- AC: AC-01 | Files: scripts/studio-fleet/update_agent.py, scripts/studio-fleet/update_agent_pause.py, scripts/studio-fleet/update_request.py, scripts/studio-fleet/fleet_rollout.py, scripts/studio-fleet/test-update-agent-pause.py | Test: python3 -B scripts/studio-fleet/test-update-agent-pause.py

### T-02 Desktop carries the pause settings and time
- AC: AC-01, AC-02 | Files: apps/desktop/src/updates/studioServiceUpdates.ts, apps/desktop/src/ipc/methods/serviceUpdates.ts, packages/contracts/src/*.ts | Test: pnpm --filter @specweave-studio/desktop exec vp test run src/updates/studioServiceUpdates.test.ts

### T-03 Sidebar countdown with Install now and Later
- AC: AC-02 | Files: apps/web/src/components/serviceUpdateRunView.ts, apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx | Test: pnpm --filter @specweave-studio/web exec vp test run src/components/serviceUpdateRunView.test.ts

### T-04 Paused turns continue after an automatic install
- AC: AC-03 | Files: apps/server/src/orchestration-v2/UpdateContinuation.integration.test.ts | Test: pnpm --filter specweave-studio exec vp test run src/orchestration-v2/UpdateContinuation.integration.test.ts

### T-05 Deleted database log restarts on request
- AC: AC-04 | Files: scripts/studio-fleet/update.py, scripts/studio-fleet/service_handles.py, scripts/studio-fleet/database_restart.py, scripts/studio-fleet/update_agent.py, scripts/studio-fleet/test-database-restart.py | Test: python3 -B scripts/studio-fleet/test-database-restart.py

### T-06 Nothing opens the live database directly
- AC: AC-05 | Files: apps/server/src/cli/db.ts, AGENTS.md, docs/operations/live-database.md | Test: pnpm --filter specweave-studio exec vp test run src/cli/db.test.ts
