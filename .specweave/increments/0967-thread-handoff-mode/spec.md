# Handoff mode: continue any thread on another machine or model

## Problem

Only the machine running a thread has its full context: the provider's own session folders (~/.claude, ~/.codex), the worktree's uncommitted changes, and the transcript. If that machine closes or its provider runs out of tokens, the work stops until it comes back. The user wants a "handoff mode": each finished step is recorded and replicated so any paired machine, or any other model, can continue the thread. It may cost a few more tokens. The user also wants to hand off one thread or a whole machine (for example before closing the main laptop), and to see which threads are ready with an accent-color badge.

## Scope

In: a per-thread handoff mode setting with project and global defaults; checkpoints (snapshot commits on hidden refs) at each turn end and every 5 minutes in long turns; replication to paired machines that have the logical project; an optional push of the hidden ref to origin; a short per-turn handoff note; badges; "Hand off to…" for one thread (machine plus provider/model); "Hand off this machine…" for all running threads; best-effort flush on sleep; a lease with fencing so two machines never run the same thread; continuing from the latest checkpoint when the source is unreachable.

Out: choosing targets from usage (0968), the second coordinator (0969), phone UI (0970), and unpaired machines.

## Acceptance Criteria

- [ ] AC-01: Handoff mode is a thread setting (Off, On) with project and global defaults, shown in the thread menu and settings. Default Off globally; the user can turn it on per project.
- [ ] AC-02: In handoff mode, at each turn end and every 5 minutes during a long turn, the server writes a snapshot commit of the worktree (temporary GIT_INDEX_FILE, `git add -A`, `git write-tree`, `git commit-tree` with HEAD as parent) to `refs/specwithcode/handoff/<threadId>` without touching HEAD, the index or the working tree. Secret-like and ignored files are excluded; files over a size cap are skipped and listed.
- [ ] AC-03: Each checkpoint is replicated to every paired machine that is a member of the logical project: an incremental git bundle of the hidden ref, the transcript delta in the MachineHandoffContext format, and the handoff note. Replication is retried with backoff and never blocks the turn.
- [ ] AC-04: When the repository has an origin, the hidden ref is also pushed there (setting, on by default); branches are never pushed by this feature.
- [ ] AC-05: Each turn end writes a handoff note (Done, Next, Open questions; at most 120 words) through the title-generation text service; the note model is configurable as Off, Cheap model (default) or Thread model.
- [ ] AC-06: Badges on the thread row and header: "Handoff ready" in the accent color once the latest checkpoint is replicated; "Checkpoint behind" when replication lags; "Handing off…" during a transfer; "Continued on <machine>" on the source, which becomes read-only with a link to the continuation.
- [ ] AC-07: "Hand off to…" on a thread picks a machine and provider/model. It bumps the lease epoch, fences the source (no further turns there), materializes the worktree on the destination (branch at the base commit plus the snapshot tree applied), and starts the destination thread with the transcript and note. A different model on the same machine is also allowed.
- [ ] AC-08: "Hand off this machine…" in the tray, Settings and command palette hands off every running handoff-mode thread to a chosen machine. A setting "When this Mac sleeps, hand off running threads to <machine>" (default off) triggers a best-effort flush and handoff on powerMonitor 'suspend' (not on screen lock).
- [ ] AC-09: The running machine renews a lease every 30 seconds. An explicit handoff or sleep notice lets the destination take over at once. On silent loss the destination shows "Handoff ready · <machine> unreachable" with a one-click "Continue here"; automatic takeover after N minutes is an opt-in setting (default off).
- [ ] AC-10: A machine that wakes after being fenced pauses its handoff-mode threads until it reaches its peers; if they stay unreachable it shows "Continue here anyway". Any changes it made after the fence are kept on `swc/from-<machine>/<branch>` for review, never merged silently.
- [ ] AC-11: A two-server verification script (two local servers, one repo) proves checkpoint, replication, explicit handoff, sleep handoff, silent-loss continue, and the fenced-wake case.
- [ ] AC-12: Headless screenshots of the badges, the Hand off to… dialog and the machine handoff dialog in light and dark.

Added October 20, 2026, 2:11 PM (lead update; user: "when running out of credits and handing off to another machine, the interrupted or in-progress sessions should restart on the new machine ... make sure to implement it properly"):

- [ ] AC-13: Single execution owner. Each thread has one lease with a monotonically increasing epoch. Every external side effect a turn performs through SpecWithCode (git push, PR create/comment/merge, tracker writes, mutating MCP calls, scheduled tasks) carries the epoch and is refused on a stale epoch. A fenced source never starts another turn and its running turn is interrupted.
- [ ] AC-14: Each turn has an idempotency key. Side effects are journaled under it and replicated with the checkpoint, so a resumed turn on the target does not repeat one the source already did: an existing PR is reused, not reopened.
- [ ] AC-15: Resume is not live process migration. The target starts a fresh provider session seeded from the portable checkpoint (hidden ref, transcript delta, handoff note, evidence). Only threads whose latest run is running, or was interrupted by a handoff, a sleep or a usage limit, are resumed. Completed, cancelled, user-stopped and failed runs are never restarted; a user Stop is final.
- [ ] AC-16: Migration preflight, per thread, on the target before anything moves: checkpoint ref present, required ignored files and secrets present (0950's copy), a work grant for that project, provider signed in, model available. A thread that fails stays on its source, untouched, with the exact reason ("Minis: no .env.local", "Minis: Claude not signed in"). A thread never half-moves.
- [ ] AC-17: Every thread keeps ownerMachineId (where it lives), executionMachineId (where it runs now) and an execution history of [machine, from, to, reason]. Thread summaries and the thread list API expose ownerMachineId, executionMachineId and executionState (running, fenced, unknown). This contract lands first as a small PR and its shape is sent to 0968, 0969 and 0970.
- [ ] AC-18: Unknown, not empty. When the executing machine is unreachable its threads read "Unknown · <machine> last seen <time>", never idle, empty or missing.
- [ ] AC-19: Source root mapping. The destination records the source environmentId, workspaceRoot and branch. The same project is never inferred from the same name; only an explicit link (0948) joins projects.
- [ ] AC-20: "Hand off this machine…" migrates selected or all threads: it lists running handoff-mode threads with checkboxes, runs the preflight per thread and reports a result per thread. Switching which orchestrator is viewed (0969) never moves a thread.
- [ ] AC-21: The two-server script also covers faults: the source goes offline mid-handoff, a lease expires, a stale-epoch machine rejoins, a partition then reconnect; it asserts no turn and no side effect runs twice. Proof is native and headless (script output files, screenshots).

## Approach

New contracts in packages/contracts/src/handoffMode.ts (settings, checkpoint record, note, lease, badge state); extend packages/contracts/src/machineHandoff.ts rather than fork it. Server: a CheckpointService (snapshot commit and hidden ref), a CheckpointReplicator on the existing fleet channel, and a ThreadLeaseService (epoch, heartbeat, fence) next to apps/server/src/fleet/MachineHandoff.ts and orchestration-v2/ThreadMoveService.ts. The destination worktree is created through the existing worktree service. Desktop: apps/desktop/src/telemetry/DesktopTelemetryPublisher.ts already listens to powerMonitor; add the suspend flush there. When the contracts and API have merged, this lane launches 0968 as its own thread in the specweave project.

## Decisions

### Asked

- Push the hidden checkpoint ref to origin by default? Defaulted to yes (hidden refs only); reported to the user as the open question.

### Defaulted

- D-01: Snapshot commits on hidden refs, so the user's branch, index and HEAD are never touched.
- D-02: Silent-loss automatic takeover is opt-in; the default is one click.
- D-03: Sleep handoff uses 'suspend' only; locking the screen is not leaving.
- D-04: Handoff notes use a cheap model by default to keep the extra token cost small.
- D-05 (lead, October 20): One lease per thread with a monotonic epoch is the single execution owner; stale-epoch side effects are refused, not merged.
- D-06 (lead, October 20): Resume starts a fresh provider session from the checkpoint; provider processes and session folders are never migrated.
- D-07 (lead, October 20): Projects are joined only by an explicit link (0948), never by matching names.
- D-08 (lead, October 20): Two-way pairing with explicit grants stands; the cancelled G3 one-way ban stays cancelled.
- D-09: Shell commands an agent runs itself (for example `git push` in its terminal) cannot be intercepted; the fence interrupts the source turn, and the side-effect journal plus the reuse checks (existing PR, already-pushed commit) keep the target from repeating them.

## Tasks

### T-01 Contracts and settings
- AC: AC-01 | Files: packages/contracts/src/handoffMode.ts, settings UI | Test: contract tests

### T-02 Checkpoint service
- AC: AC-02, AC-04 | Files: apps/server/src/handoff/CheckpointService.ts | Test: server tests on a temp repo (HEAD and index unchanged, secrets excluded)

### T-03 Replication
- AC: AC-03 | Files: CheckpointReplicator.ts, fleet wire | Test: server tests with two in-process peers

### T-04 Handoff note
- AC: AC-05 | Files: note generator on the text service | Test: unit tests with a stub model

### T-05 Lease and fencing
- AC: AC-09, AC-10 | Files: ThreadLeaseService.ts | Test: server tests for heartbeat, takeover, fenced wake

### T-06 Hand off one thread
- AC: AC-07 | Files: ThreadMoveService.ts extension, Hand off to… dialog | Test: server and component tests

### T-07 Hand off this machine and sleep flush
- AC: AC-08 | Files: tray, settings, command palette, DesktopTelemetryPublisher.ts | Test: unit tests with a simulated suspend

### T-08 Badges
- AC: AC-06 | Files: thread row and header | Test: component tests

### T-09 Two-server verification and screenshots
- AC: AC-11, AC-12 | Files: scripts/verify-handoff-mode | Test: the script, headless Playwright

### T-10 Launch 0968
- AC: none | Files: none | Test: thread link in the report (launched by the lead, October 20)

### T-11 Execution owner contract (first PR)
- AC: AC-17 | Files: packages/contracts/src/handoffMode.ts, orchestrationV2.ts thread shell, orchestratorMcp.ts thread list | Test: contract tests; shape sent to 0968, 0969, 0970

### T-12 Epoch-fenced side effects and turn idempotency
- AC: AC-13, AC-14 | Files: ThreadLeaseService.ts, SideEffectJournal.ts, MCP mutating tools, git push and PR paths | Test: server tests (stale epoch refused, PR reused)

### T-13 Resume from checkpoint
- AC: AC-15 | Files: HandoffResume.ts | Test: server tests for each run status

### T-14 Migration preflight
- AC: AC-16 | Files: HandoffPreflight.ts | Test: server tests with exact per-thread reasons

### T-15 Unknown state
- AC: AC-18 | Files: execution state projection, thread row | Test: server and component tests

### T-16 Source root mapping
- AC: AC-19 | Files: continuation record | Test: server tests (same name, different project is not joined)

### T-17 Selectable machine handoff
- AC: AC-20 | Files: Hand off this machine dialog, handOffMachine RPC | Test: server and component tests

### T-18 Fault and reconnect tests
- AC: AC-21 | Files: two-server script | Test: the script output files

### T-19 Verify and close 0967
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
