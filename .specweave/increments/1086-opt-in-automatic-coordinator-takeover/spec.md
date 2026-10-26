# Opt-in automatic coordinator takeover

Repo: repositories/anton-abyzov/specweave-studio (specwithcode-dev). Branch: inc/1086-auto-takeover.

Paths are relative to `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/tailscale-optional`. A path that starts with `fleet-over-connect/` means `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fleet-over-connect`. That worktree is uncommitted, so its line numbers can move.

## Problem

Anton asked: "If I close my M4 for an hour, does the work move to M1 or M3 and get finished anyway?"

**Today the answer is no.**
- Takeover is a button in the client. It appears only after the coordinator has been unreachable for 10 minutes, and never while it is connected (apps/web/src/studio/projectLink.ts:85-102). The code comment at :90 says "There is no automatic failover."
- `autoTakeoverMinutes` is stored and never acted on:
  - schema at packages/contracts/src/handoffMode.ts:55, any integer from 0 to 1440;
  - default 0 at :64;
  - patch at apps/server/src/handoff/handoffState.ts:157;
  - UI at apps/web/src/components/settings/HandoffModeSettings.tsx:216-224.
- Threads that run on the M4 pause, unless the opt-in sleep handoff moved them.

**After this increment, with the feature turned on for a project and its standby armed:**
- Remote workers keep running during the hour, as they already do.
- After N minutes, the chosen standby takes over coordinator duty: notes, goal, instructions, and receiving worker results.
- Handoff-mode threads that ran on the M4 continue on the designated machine from their last copy.
- Threads that are not in handoff mode wait for the M4.
- Edits on the M4 that were never copied stay on the M4.
- If the standby is asleep or cannot be reached, nothing moves. The M4 stops its own coordinator once the standby could have acted. This is the price of never running two coordinators.
- Running without Tailscale also needs T-15, which is Connect auth for peers, invites and redeem.

**Facts this design rests on:**

1. **The coordinator pushes to workers. Workers never call the coordinator.**
   - Handoff peers send `Bearer` to `${target.url}/api/handoff/v1/<path>` (apps/server/src/handoff/handoffPeers.ts:227-231).
   - The route takes the caller identity from the grant, as `sourceEnvironmentId: grant.coordinatorEnvironmentId` (apps/server/src/handoff/handoffRoute.ts:90-93).
   - The route checks only that a grant exists and is not revoked (:74-88). Project scope is checked later in the receiver (apps/server/src/handoff/HandoffReceiver.ts:245-259).
2. **`ProjectLink.takeover` and `supersede` already exist.**
   - `takeover` (apps/server/src/project/ProjectLink.ts:755-826) runs under `admission.withLock` (:756-757). It is idempotent by `operationId` (:768-781), requires the copy to be `transferred` (:782-785), and writes `max(epoch, knownEpoch)+1` (:800).
   - `supersede` (:828-884) returns `ranWhileDisconnected` (:880). It does not interrupt a running turn (:867-879).
3. **More than one active coordinator is already possible.** `startCoordinator` makes a `transferred` copy `active` with no predecessor (ProjectLink.ts:887-891, :905-907, :931-935). `projectCoordinatorIsFenced` looks only at the local copy (packages/contracts/src/logicalProject.ts:85-94).
4. **The binding schema has no standby field** (logicalProject.ts:68-83). `operationId` allows at most 128 characters (:71), while a logical project id allows up to 512 (:31).
5. **Steering rules on a worker machine.**
   - In a linked project whose copy on the worker is not `active`, any grant whose scope covers the project may steer (apps/server/src/mcp/workGrantAccess.ts:224-232).
   - Worker machines do no epoch check (not found).
   - New grants default to `projects: {kind: "linked"}` (apps/server/src/fleet/workGrantPolicy.ts:68-69).
   - `allowFleetWorkers` takes only `{id, access, pairingCode}` (apps/server/src/studioFleetHttp.ts:350-363).
6. **Arming gives broad rights today.** `inviteFleetMachine` mints a 365-day `coordinator` session that carries `access:write` (apps/server/src/studioFleetInvite.ts:42, :45, :59).
7. **The per-turn gate seam** is `HandoffTurnGate.check`, which returns a refusal string or null (apps/server/src/handoff/HandoffTurnGate.ts:55-80). It is used at apps/server/src/orchestration-v2/Orchestrator.ts:1133, :1727 and :5266.
8. **Follower behavior.**
   - `follow(rowId)` is idempotent, and `resume` is meant to run once at boot (apps/server/src/fleet/RemoteWorkerFollower.ts:106, :122-123).
   - A failed wake returns `"pending"` for every error except archived (:231-242).
   - The delivered-run window keeps 50 ids (:341).
9. **Connect.**
   - A `Bearer` coordinator grant is refused over Connect (fleet-over-connect/apps/server/src/auth/EnvironmentAuth.ts:1153-1156). A DPoP path exists (:1158-1168).
   - Peers and the MCP client still send `Bearer` (fleet-over-connect/apps/server/src/handoff/handoffPeers.ts:227-231; fleet-over-connect/apps/server/src/fleet/RemoteStudioMcpClient.ts:200-207).
   - Invite redeem is unfinished (fleet-over-connect/apps/server/src/studioFleetJoin.ts:256).
10. **Worker-grant expiry: not found in the base branch.** The only TTL in WorkGrants.ts is `ORIGIN_KEEP` = 90 days (apps/server/src/fleet/WorkGrants.ts:44). EnvironmentAuth in the Connect branch calls the bearer a 30-day grant (fleet-over-connect/apps/server/src/auth/EnvironmentAuth.ts:1151-1154).

## Scope

**In scope:**
- One explicit standby per logical project. Off by default.
- The owner arms it on both machines.
- A lease the coordinator pushes to the standby.
- A mandatory self-fence on the coordinator.
- A server-side automatic takeover.
- Worker machines check the coordinator epoch.
- Workers started by the coordinator thread are adopted.
- `autoTakeoverMinutes` is implemented, but only on the designated machine.
- The returning machine gives way and lists its turns for review.
- The desktop calls the server directly when the Mac suspends.
- UI, copy and docs.

**Out of scope:**
- Ranked successors and elections.
- M1 starting new work on the M4.
- Auto-continue for threads that are not in handoff mode.
- Carrying uncheckpointed edits.
- Memory written after the last client sync.
- Taking the coordinator back automatically.

## Acceptance Criteria

- [ ] AC-01: Off by default; owner arms both sides.
- A project has no standby until the owner sets it on the coordinator (`setStandby`) and accepts it on the standby (`acceptStandby`). Both are done from the desktop app.
- `acceptStandby` refuses when the standby's copy is `active`, or when the standby lacks the `coordinatorStandby` capability.
- `setStandby` changes only `standby` through the new ownership mode `set-standby`.

- [ ] AC-02: Narrow credentials.
- Arming gives the standby a worker grant on each worker machine W, scoped to W's copy of this one project (`projects: {kind: "listed"}`).
- Its access is capped at the M4's own access on W.
- Any management session created during arming is revoked once the grant exists.
- No credential is created for M1 → M4, or between non-chosen machines.

- [ ] AC-03: Authenticated, ordered leases.
- The standby accepts `coordinator-lease` only when all of these hold:
  - the caller's grant `coordinatorEnvironmentId` equals the registered coordinator;
  - the grant's project scope covers the standby's copy;
  - the epoch equals the registered epoch;
  - `seq` is strictly above the last persisted `seq`.
- Any other lease is ignored and logged.
- `lastLeaseAt` is the standby's own receive time.

- [ ] AC-04: Release before change.
- Each of these makes the coordinator send `release` to the standby and wait for the acknowledgement before its local write commits: turning the standby off or changing it, a normal coordinator handoff, unlink, archive, and supersede.
- If the standby does not answer, the change is refused unless the owner confirms "Change anyway". Then a pending release is sent on every tick until it is acknowledged.
- The standby also disarms on a refused lease from the registered coordinator, such as a revoked grant (handoffRoute.ts:84-88), and when that coordinator's grant on M1 is revoked.

- [ ] AC-05: Standby fires only after real, continuous silence while it is awake.
- The standby takes over only if all of these hold:
  - it received at least one accepted lease since its current `watchingSince`;
  - `now - lastLeaseAt >= afterMinutes`;
  - it is armed by its own check of its grants on each worker machine;
  - it is not paused (`pausedUntil`, `standbySleeping`).
- `watchingSince` resets at process start, and on any tick where wall-clock time moved more than monotonic time by over 2 ticks, or moved backwards.
- `afterMinutes` is one of 5, 15, 30 or 60.

- [ ] AC-06: Mandatory self-fence on the coordinator.
- With a standby set, the coordinator refuses new coordinator turns once its persisted `lastSuccessfulLeaseAt` is older than `afterMinutes − (2×30 s + 10 s + 60 s)`.
- At the same moment it interrupts any running coordinator turn and its local children.
- It lifts after one successful lease round trip that answers `takenOver: null`.
- Three answers are not counted as silence:
  - `503 busy` and `standbySleeping` mean paused;
  - `404 not_found` means the standby lost the feature, so the standby is disarmed and shown.
- The fence state survives restarts. There is no "never heard from" exemption.
- "Run here anyway" turns the standby off, with a pending release, and logs an operation.

- [ ] AC-07: Takeover is atomic and fenced.
- The lease handler and the takeover run under the same `admission.withLock(projectId)`.
- Inside the lock the standby re-reads `lastLeaseAt` before it calls `takeover`.
- `takeover` is called with:
  - `knownEpoch` = the registered epoch;
  - `predecessor` = the registered coordinator member;
  - epoch E = `max(binding.epoch, knownEpoch)+1`, computed first;
  - `operationId = "auto:" + sha256(logicalProjectId).slice(0,32) + ":" + E`.
- The new binding records `takenOverBy: "auto"` and has no `standby`.
- Once the standby's copy is active, every lease is answered with `takenOver`.

- [ ] AC-08: Workers move without double steering.
- On takeover, the standby sends `claimEpoch {logicalProjectId, epoch: E}` to each worker machine.
- The worker machine persists the highest epoch for that project. It refuses steering calls with a lower epoch, and calls with no epoch after any claim.
- Shadow rows are adopted only when all of these hold:
  - the worker machine confirms their origin is the old coordinator (`originOf`, apps/server/src/fleet/WorkGrants.ts:113-120);
  - their caller was the old coordinator thread;
  - their state is `following` or `wake_pending`.
- Adopted rows have machine and project ids mapped to the standby's own ids and are followed through `follow(rowId)`.
- Runs whose ids are already in `deliveredRunIds` (50 ids) are not delivered again.
- A row is marked `readOnly` if the worker refuses the claim or lacks the capability.

- [ ] AC-09: The returning coordinator gives way safely.
- On a `takenOver` answer, the old coordinator verifies the binding:
  - `state === "active"`;
  - the epoch is above its own;
  - `predecessor` is its own member;
  - the sender is its configured standby.
- Then, in one lock:
  - it interrupts the coordinator turn and its children;
  - it calls `supersede`;
  - it marks rows whose caller is the fenced coordinator thread as `stopped`.
- The review boundary is `min(translated takenOverAt, lastSuccessfulLeaseAt)`.
- A binding that fails verification is logged and shown, and nothing is superseded.

- [ ] AC-10: Handoff threads continue on one machine only.
- `autoTakeoverMinutes` acts only on the machine that the source named as `sleepTarget` or project standby in its own heartbeat.
- It never acts on a coordinator thread (`isProjectCoordinatorThreadId`, logicalProject.ts:124-135).
- The delay is clamped to at least 5 minutes.
- The source fences its handoff threads when that designated machine has been silent for delay − margin. The fence state is persisted.
- The reason `"auto-takeover"` is passed through an internal `continueHereAs`. The WebSocket input does not change.

- [ ] AC-11: Planned pauses do not trigger a takeover.
- Before the coordinator stops for a service update or a suspend, it sends a lease with `pausedUntil` (capped at 30 minutes), or `sleeping: true`. The standby's clock counts from that moment.
- The desktop main process makes the suspend call to the server directly, using the desktop service credential.

- [ ] AC-12: Copy and docs.
- All user-facing text is in short plain sentences, as in the Approach section on UI.
- docs/user/shared-projects.md:120-126 and docs/studio/logical-projects.md:51 describe the opt-in, its fence and its limits.

## Approach

### Data

**Coordinator binding** (packages/contracts/src/logicalProject.ts:68), new optional fields:

```ts
standby: Schema.optional(Schema.Struct({
  member: LogicalProjectMember,
  afterMinutes: Schema.Literals([5, 15, 30, 60]),
  enabledAt: IsoDateTime,
})),
takenOverBy: Schema.optional(Schema.Literals(["person", "auto"])),
```

Update the `takenOverAt` doc at :76-80.

**Standby state** in `coordinator-standby.json` in the state folder (JSON, for the reason at apps/server/src/fleet/RemoteWorkerStore.ts:15-20). Per project it holds:
- the registered coordinator member and epoch;
- `afterMinutes`;
- `lastLeaseAt` (receive time) and `lastSeq`;
- `watchingSince`;
- `pausedUntil`;
- `armedFor`, worked out locally;
- `runningThreads: {threadId, title}[]`;
- shadow worker rows;
- `lastRefusal`.

**Coordinator side**, persisted per project:
- `lastSuccessfulLeaseAt`;
- `seq`;
- `pendingRelease`.

### Wire (handoff peer route)

**New paths:**
- `coordinator-lease` carries `kind: lease | release | pause`.
- `coordinator-replica` carries the content.

Both are added to `PEER_PATHS` (handoffWire.ts:197-204) and to `TIMEOUT_MS` at 10 s (handoffPeers.ts:49-55). `coordinator-replica` gets its own byte cap instead of `HANDOFF_JSON_MAX_BYTES` (handoffRoute.ts:96).

**Lease body:**
- `protocolVersion`, `logicalProjectId`, `epoch`, `seq`;
- `afterMinutes`, `contentDigest` (ProjectLink.ts:155);
- `runningThreads`;
- `workers[]` (≤ 50 `deliveredRunIds` each);
- optional `pausedUntil` or `sleeping`.

**Lease reply:**
- `takenOver | null`, `wantsContent`;
- `standbySleeping`, `receivedAt`.

**Replica handling:**
- The replica is applied through a new `ProjectLink.replicateFromPeer`, which reuses the internals at ProjectLink.ts:670-698.
- It stores provenance. The takeover notice shows "Instructions changed by M4 at <time>" when goal or instructions differ from the last client-written replica.
- Once T-15 lands, both paths require DPoP over Connect, as do all peer paths.

### Loops

- **`CoordinatorLease`**, on the coordinator. Every 30 s it sends the lease, the replica when asked, and pending releases. It updates the fence state and handles the supersede verdict. It is forked with `forkParked` like HandoffModeReactor.ts:99-103.
- **`CoordinatorStandbyWatch`**, on the standby. It ticks every 30 s.
  - The pure `shouldTakeOver` takes an injected monotonic source, because Effect `TestClock` cannot simulate sleep.
  - It also runs a periodic grant check for `armedFor`.
- **`CoordinatorWakeGate`**: a new service, checked next to `handoffGate` at Orchestrator.ts:1727 and :5266. It returns a refusal string the same way HandoffTurnGate does, so no new enum is needed. If the dispatch path needs a code, add it to packages/contracts/src/projectWorkspace.ts:185-193.

### Taking the coordinator back

The `takeover` button cannot do this, because the coordinator is connected (projectLink.ts:94-102). Instead, "Make this Mac the coordinator again" opens the existing coordinator handoff (ownership mode `handoff`, apps/server/src/orchestration-v2/ProjectCommands.ts:344) on the active machine. If no client session to M1 exists, the copy says "Open M1 and hand the coordinator back."

### UI and copy

**Settings > Project > Machines.** New `CoordinatorStandbySettings.tsx`, extracted from ProjectMachinesSettings.tsx (659 lines).
- Section "If this Mac goes quiet".
- "Take over automatically on: Off / M1 / M3."
- "After: 5 / 15 / 30 / 60 minutes."
- Arming rows: "M3 lets M1 take over. Allow." / "Ready. M1 can take over." / "Not ready. M3 has not allowed M1 yet." Errors are shown per machine: rate limited (FleetWorkerGrants.ts:403-410) or unreachable.
- Warning: "M1 must stay awake. If it is off, this Mac pauses its coordinator."

**Standby status:**
- "Last heard from M4 2 min ago."
- "M4 has been quiet for 12 min. Taking over at 14:30."

**On M1 after a takeover:**
- "M1 took over from M4 at 14:30. M4 went quiet."
- "3 workers on M3 report here now."
- "2 threads were on M4 and wait for it."

**On M4 when it returns:**
- "M1 took over while this Mac was away. This Mac now runs workers."
- Buttons: "Review turns" and "Make this Mac the coordinator again".

**Fence:** "Checking with M1 before running. Run here anyway." The button also says "This turns off automatic takeover."

**Handoff settings** (HandoffModeSettings.tsx:213). New sentence: "Threads in handoff mode continue on your chosen Mac after this long. Off means they wait for your click."

## Decisions

- **D-01 One explicit standby, no ranking.** Ranking needs liveness checks between standbys, which means extra credentials, and there is no server-side election (not found).
- **D-02 The owner arms on both machines.** The standby learns its role and settings from `acceptStandby`, which runs through the owner's client, and not from a peer message. This closes the "lease names itself" hole. It replaces the stale `binding.successor` check (MachineHandoff.ts:1262-1263 keeps a `transferred` binding unchanged).
- **D-03 The self-fence is mandatory.** Its margin is 130 s below `afterMinutes`. Availability gives way to safety, as AC-06 describes.
- **D-04 The standby needs a lease seen while it was awake.** A standby that wakes up never fires before it hears from the coordinator again. If both machines slept, nothing moves.
- **D-05 Takeover is one-way.** The new coordinator has no standby. Taking the coordinator back is manual.
- **D-06 Default delay is 15 minutes.** The minimum is 5.

**Critiques rejected or partly rejected:**

- **Rejected: feasibility #16** (drop the successor check and accept any listed member). Any listed member holding a grant could then arm the standby or reset its clock. The registered coordinator from D-02 replaces both the stale successor check and the listed-member check.
- **Partly rejected: security #1, the "dormant grant"** (the worker machine refuses the grant until it sees M1 active). A worker machine cannot see another machine's binding (no mechanism found). The epoch claim in AC-08 gives the same protection for steering. Reading stays allowed on the single listed project.
- **Partly rejected: security #4** (DPoP for `coordinator-replica` even over Tailscale). Over Tailscale it keeps the same trust as the existing handoff `replicate` path, which already lets that grant write thread content. Provenance display, the byte cap and scope checks are added. DPoP becomes mandatory when T-15 lands.
- **Partly rejected: feasibility #9** (adopt `launching` rows). The outcome of a launch is settled from the old coordinator's records (`reconcile`, RemoteWorkerFollower.ts:108-111). Those rows are listed as "waiting for M4" instead.
- **Partly rejected: D4 and feasibility #12** (fence while the standby is off). Both are kept: the fence is mandatory, but a standby that is announced as sleeping or busy pauses it. Silence with no notice still fences. AC-06 has the override.

## Tasks

Test commands assume vitest from the repo root. The exact script in package.json was not checked.

### T-01 Schema for standby, takenOverBy and capability
- AC: AC-01, AC-07 | Files: packages/contracts/src/logicalProject.ts, packages/contracts/src/logicalProject.test.ts, packages/contracts/src/environment.ts, apps/server/src/ServerEnvironment.ts | Test: npx vitest run packages/contracts/src/logicalProject.test.ts

### T-02 Ownership mode set-standby
- AC: AC-01 | Files: apps/server/src/orchestration-v2/ProjectCommands.ts, apps/server/src/orchestration-v2/ProjectCommands.test.ts | Test: npx vitest run apps/server/src/orchestration-v2/ProjectCommands.test.ts

### T-03 Standby store and the pure clock
- `shouldTakeOver` with an injected monotonic source. Cases:
  - never fires before `afterMinutes`;
  - one lease resets the window;
  - a restart resets it;
  - no lease since `watchingSince` means no fire;
  - unarmed or paused means no fire;
  - a wall-clock jump, standby sleep, or an NTP step backwards resets the window.
- AC: AC-05, AC-11 | Files: apps/server/src/project/CoordinatorStandbyStore.ts, apps/server/src/project/CoordinatorStandbyWatch.ts, apps/server/src/project/CoordinatorStandbyWatch.test.ts | Test: npx vitest run apps/server/src/project/CoordinatorStandbyWatch.test.ts

### T-04 ProjectLink methods
- `setStandby`, `acceptStandby`, `replicateFromPeer`, and auto `takeover` with the epoch-first `operationId`. The RPCs go in packages/contracts/src/rpc.ts:2264.
- Split into `ProjectLinkStandby.ts`, because ProjectLink.ts is 1007 lines.
- AC: AC-01, AC-07 | Files: apps/server/src/project/ProjectLink.ts, apps/server/src/project/ProjectLinkStandby.ts, apps/server/src/project/ProjectLink.test.ts, packages/contracts/src/rpc.ts | Test: npx vitest run apps/server/src/project/ProjectLink.test.ts

### T-05 Peer wire and route handler
- The handler runs under the project lock. It enforces the AC-03 checks, records refused leases (AC-04), checks protocol version, and applies the byte cap.
- AC: AC-03, AC-04, AC-07 | Files: apps/server/src/handoff/handoffWire.ts, apps/server/src/handoff/handoffPeers.ts, apps/server/src/handoff/handoffRoute.ts, apps/server/src/project/CoordinatorLeaseRoute.ts, apps/server/src/project/CoordinatorLeaseRoute.test.ts | Test: npx vitest run apps/server/src/project/CoordinatorLeaseRoute.test.ts

### T-06 Coordinator lease loop
- Covers: `seq`, persisted `lastSuccessfulLeaseAt`, the release protocol, pause and sleep leases, and supersede verification under the lock with interrupt and row stop.
- AC: AC-04, AC-09, AC-11 | Files: apps/server/src/project/CoordinatorLease.ts, apps/server/src/project/CoordinatorLease.test.ts, apps/server/src/handoff/HandoffModeReactor.ts | Test: npx vitest run apps/server/src/project/CoordinatorLease.test.ts

### T-07 Wake gate and self-fence
- A persisted fence. A running coordinator turn is interrupted through `interruptRun` (HandoffMoves.ts:1076-1088).
- AC: AC-06 | Files: apps/server/src/project/CoordinatorWakeGate.ts, apps/server/src/project/CoordinatorWakeGate.test.ts, apps/server/src/orchestration-v2/Orchestrator.ts (wiring at :1133, :1727, :5266 only), packages/contracts/src/projectWorkspace.ts | Test: npx vitest run apps/server/src/project/CoordinatorWakeGate.test.ts

### T-08 Epoch claim on worker machines
- Worker machines persist the highest epoch, refuse lower or missing epochs after a claim, and return origins for the listed threads.
- AC: AC-08 | Files: apps/server/src/mcp/workGrantAccess.ts, apps/server/src/fleet/WorkerEpochStore.ts, apps/server/src/fleet/RemoteStudioMcpClient.ts, apps/server/src/mcp/workGrantAccess.test.ts | Test: npx vitest run apps/server/src/mcp/workGrantAccess.test.ts

### T-09 Worker row adoption
- Shadow rows, id mapping, origin and caller filtering, `follow(rowId)`, and the 50-id dedup.
- On the old machine, rows whose wake fails with `transferred` are stopped.
- AC: AC-08, AC-09 | Files: apps/server/src/fleet/RemoteWorkerStore.ts, apps/server/src/fleet/RemoteWorkerAdoption.ts, apps/server/src/fleet/RemoteWorkerFollower.ts, apps/server/src/fleet/RemoteWorkerFollower.test.ts | Test: npx vitest run apps/server/src/fleet/RemoteWorkerFollower.test.ts

### T-10 Auto-continue for handoff threads
- The designated machine is taken from the source heartbeat. Coordinator threads are skipped, the delay is clamped to at least 5 minutes, and the per-thread fence on the source is persisted. Adds an internal `continueHereAs` on the moves port (HandoffMoves.ts:1151).
- AC: AC-10 | Files: apps/server/src/handoff/HandoffAutoContinue.ts, apps/server/src/handoff/HandoffAutoContinue.test.ts, apps/server/src/handoff/HandoffMoves.ts, apps/server/src/handoff/handoffState.ts | Test: npx vitest run apps/server/src/handoff/HandoffAutoContinue.test.ts

### T-11 Desktop suspend calls the server directly
- Uses the desktop service credential (apps/desktop/src/backend/desktopServiceCredential.ts) and a new endpoint allowed for that credential.
- AC: AC-11 | Files: apps/desktop/src/app/DesktopHandoffSleep.ts, apps/desktop/src/app/DesktopApp.ts, apps/server/src/project/CoordinatorSuspendRoute.ts | Test: npx vitest run apps/desktop/src/app/DesktopHandoffSleep.test.ts

### T-12 Arming chain
- Runs only in the desktop app, with full-access sessions to W and M1. The chain is invite, add, allow, narrow the scope to a listed project, then revoke the management session.
- Verify whether W can update a grant's project scope after `allowFleetWorkers`; it is not verified. Add an update path if it is missing.
- AC: AC-02 | Files: apps/web/src/studio/projectLink.ts, apps/web/src/studio/standbyArming.ts, apps/server/src/studioFleetHttp.ts, apps/server/src/fleet/FleetWorkerGrants.ts | Test: npx vitest run apps/web/src/studio/standbyArming.test.ts

### T-13 UI and copy
- AC: AC-12, AC-01 | Files: apps/web/src/components/studio/CoordinatorStandbySettings.tsx, apps/web/src/components/studio/ProjectMachinesSettings.tsx, apps/web/src/components/settings/HandoffModeSettings.tsx | Test: npx vitest run apps/web/src/components/studio/CoordinatorStandbySettings.test.tsx

### T-14 Docs
- AC: AC-12 | Files: docs/user/shared-projects.md, docs/studio/logical-projects.md | Test: npm --prefix repositories/anton-abyzov/specweave run lint:docs-refs

### T-15 End-to-end scenarios
- Build the M4, M1 and M3 ProjectLink layers and a peers stub for the new paths. The existing test at handoffMove.test.ts:326 and :402 uses a hand-built `HandoffPeers.of` with no ProjectLink.
- Scenarios:
  - a normal takeover with a worker wake landing on M1;
  - M4 returns, supersedes and reviews its turns;
  - a flap, where one lease mid-window means no takeover;
  - an asymmetric partition, where M4 reaches M3 but not M1;
  - a turn running at the moment of takeover;
  - a lease arriving during a takeover;
  - the standby turned off, or the coordinator handed to M3, then M4 goes quiet;
  - standby sleep or a wall-clock jump;
  - two machines holding handoff copies with `autoTakeoverMinutes > 0`;
  - M4 restarting during a partition;
  - an M4 service update with `pausedUntil`;
  - a revoked M4 grant on M1;
  - an inflated lease epoch;
  - a replayed `seq`.
- AC: AC-03..AC-11 | Files: apps/server/src/project/coordinatorAutoTakeover.test.ts | Test: npx vitest run apps/server/src/project/coordinatorAutoTakeover.test.ts

### T-16 Connect dependency (fleet-over-connect line of work)
- DPoP for handoff peers and `RemoteStudioMcpClient`, plus v2 invite and redeem with the fleet proof key.
- AC: AC-02, AC-03 | Files: fleet-over-connect/apps/server/src/handoff/handoffPeers.ts, fleet-over-connect/apps/server/src/fleet/RemoteStudioMcpClient.ts, fleet-over-connect/apps/server/src/studioFleetJoin.ts | Test: npx vitest run apps/server/src/handoff (in that worktree)

### T-17 Release proof
- A two-Mac manual check: M4's lid closed for 20 minutes, standby M1 set to 15 minutes. Then the same with M1 asleep, where M4 must fence and nothing may move. Owner manual verification is required.
- AC: AC-05, AC-06, AC-07 | Files: none | Test: manual, recorded in the increment's reports/

**Order:** T-01 → T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08 → T-09 → T-10 → T-11 → T-12 → T-13 → T-14 → T-15. T-16 runs in parallel and gates use without Tailscale. T-17 comes last.

## Risks

1. **No Tailscale before T-16.** Over Connect the coordinator's `Bearer` is refused (fleet-over-connect/apps/server/src/auth/EnvironmentAuth.ts:1153-1156), so leases fail and the fence pauses M4. Until T-16 lands, the feature is offered only when every link is on Tailscale.
2. **Availability.** A standby that goes offline with no notice makes M4 pause its coordinator after about `afterMinutes − 130 s`. "Run here anyway" turns auto-takeover off, but if M1 is in fact awake and cut off, it may still take over. M4 then learns of it on reconnect, and the review list shows the overlap.
3. **A coordinator nobody chose.** `startCoordinator` can still create another active copy (ProjectLink.ts:887-891). The standby refuses to arm or take over while its own copy is active. Copies elsewhere remain outside this feature.
4. **Memory.** Memory sync is client-driven (docs/studio/logical-projects.md:57). Memory written after the last sync is missing on M1.
5. **Uncheckpointed edits.** Up to 5 minutes of edits (HANDOFF_LONG_TURN_CHECKPOINT_MS, handoffMode.ts:29) stay on M4. Threads that are not in handoff mode wait for it.
6. **Mixed versions.** A worker machine without epoch support makes adopted rows read-only. A standby without the capability cannot be chosen.
7. **File sizes.** HandoffMoves.ts has 1167 lines, RemoteWorkers.ts 1216 and Orchestrator.ts 13,142. New logic goes in new files; Orchestrator.ts gets wiring only.
8. **Not found:**
   - a server-side election;
   - an epoch check on worker machines;
   - a project-scoped invite without `access:write`;
   - a worker-grant expiry in the base branch;
   - a way to update a grant's project scope after `allowFleetWorkers` (not verified).