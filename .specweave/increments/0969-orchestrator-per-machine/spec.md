# An orchestrator on each machine of a project

## Problem

A logical project linked across machines (0948) has one active coordinator binding; the other machine can only take it over (0951). The user now wants pairing to work both ways: with M4 as the main machine and Minis as the dependent one, each machine runs its own orchestrator for the project, so work continues on Minis when M4 is closed. This replaces the one-way control proposal (G3 is cancelled).

## Scope

In: one active coordinator per member machine; separate view, move and migrate actions; honest offline state; thread location labels; an execution-machine policy; independent checkouts with a shared pull request list; migrating the single coordinatorBinding to a per-machine list; two-way work grants scoped to the linked project; two-way project memory replication; plan claims fenced across machines; message routing so each coordinator acts only on messages sent to it; a machine switcher on the project page; and the Minis coordinator seeing and continuing handoff-ready M4 threads once 0967 has merged.

Out: the handoff mechanism (0967), adding a project to a machine (0966), phone (0970).

## Acceptance Criteria

- [ ] AC-01: Coordinator bindings are per machine: the project's coordinator list is read as each member environment's own coordinatorBinding (one active binding per member environment allowed), with a read-time migration in which a missing or single legacy binding keeps the existing coordinator thread. No user data is rewritten until the next normal save.
- [ ] AC-02: 0951's takeover action becomes "Start a coordinator here", which adds a binding for this machine instead of moving the existing one.
- [ ] AC-03: Pairing a project grants work both ways, scoped to the linked project only. The loop check in apps/server/src/fleet/workGrantPolicy.ts (lines 90 to 157) stays and is tested with two coordinators.
- [ ] AC-04: Project memory replicates both ways between members: last writer wins per file, the losing version is kept as `<name>.conflict-<machine>.md`, and MEMORY.md is never silently dropped.
- [ ] AC-05: Plan task claims are fenced across machines: a claim made on one machine is visible and binding on the other; a stale claim from an unreachable machine is shown as such and only released by the user.
- [ ] AC-06: A message sent to one coordinator is handled only there; a thread is owned by the coordinator that started it or that it was migrated to (its execution machine may differ), and the other coordinator only reads it.
- [ ] AC-07: The project page shows a machine switcher listing each member machine with its coordinator and online state.
- [ ] AC-08: After 0967 merges: the Minis coordinator lists M4's handoff-ready threads and can continue one with a single action.
- [ ] AC-09: Two-server test proves migration, both coordinators active, two-way grants without loops, memory conflict copy and fenced claims.
- [ ] AC-10: The machine switcher has three separate actions that are never merged: "View <machine>'s orchestrator" reads that machine's coordinator conversation, threads, plan and memory remotely, and a message typed there is sent to and handled by that machine's coordinator; "Move coordinator here" is explicit, confirmed and recorded; "Migrate threads…" moves selected or all threads through 0967's handoff and shows a preflight result per thread. Switching the view never relocates a thread or the coordinator, and the saved client choice no longer decides which machine runs the coordinator.
- [ ] AC-11: Parity is stated honestly. Online, the view reads the remote server live, so messages and thread state are the same data as on that machine. Offline, the view shows the last replicated snapshot labeled "<machine> unreachable · last synced <time> · read-only", or "Unknown" when nothing was replicated. It never shows an empty list, never silently stands in another checkout, and never claims live parity while offline. What is replicated and what is remote-read only is listed under Approach.
- [ ] AC-12: Thread lists show where each thread lives and runs: "M4" when both are the same, "M4 → Minis" when the owner and execution machines differ, from 0967's ownerMachineId, executionMachineId and executionState and 0966's machine nicknames.
- [ ] AC-13: The orchestrator chooses the execution machine for each thread by a documented policy (explicit user choice, then the project worker machine, then the coordinator's machine; each candidate must be reachable, granted for the project, signed in to the provider and, once 0968 lands, have eligible capacity). A launch reports the chosen machine and why skipped candidates were refused; an explicit choice that is ineligible is refused, not substituted. Coordinator tools expose it: studio_thread_launch keeps its machine argument and a new studio_thread_migrate tool calls 0967's handoff.
- [ ] AC-14: Two checkouts of the same repository that are not explicitly linked stay two projects with two orchestrators and their own branches; nothing links them by name or by matching remote alone. The project page lists "Pull requests from both machines" for consolidation through the shared remote. When linked, each coordinator still owns its own threads unless they are migrated.
- [ ] AC-15: The two-server script covers faults and reconnects: a remote coordinator goes offline while viewed (the view shows last synced, never empty), reconnecting restores the live view, a message sent to an offline coordinator is refused with a clear error (never queued silently elsewhere), and a stale plan claim after a partition is shown and released only by the user. Native headless screenshots are saved.

## Approach

Data lives in workspaceSettings.logicalProject {id, title, coordinatorId, members[{environmentId, projectId, coordinatorThreadId}]} and coordinatorBinding {epoch, state}. Members already carry coordinatorThreadId; promote it to an active binding each. Grants: apps/server/src/fleet/workGrantPolicy.ts and transferGrant.ts. Memory replication rides the fleet channel used by 0948.

### Viewing, moving and migrating

Viewing another machine's orchestrator is a remote read through that machine's live environment connection; nothing is written on either machine except the viewer's own snapshot cache. Moving the coordinator is the existing ownership handoff with a confirmation and an audit entry. Migrating threads is 0967's handoff, one thread at a time, each with its own preflight result.

### What is replicated and what is remote-read only

| Data | How the other machine gets it | Offline |
|---|---|---|
| Project memory files, including MEMORY.md | Replicated both ways (AC-04) | Last replicated copy, read-only, with its sync time |
| Plan tasks and claims | Replicated both ways; claims carry the owning machine (AC-05) | Last replicated copy; claims from the unreachable machine shown stale |
| Coordinator conversation and thread list summaries (title, status, owner, execution machine, execution state, updated time) | Read live from that machine's server; the viewing device keeps what it loaded in its persisted environment cache | The cached copy, read-only, labeled "last synced" with the time this device last saw that machine connected |
| Thread checkpoints, transcript deltas and handoff notes | Replicated only by 0967 handoff mode for threads with handoff mode on | Whatever 0967 last replicated |
| Full thread transcripts, tool activity, diffs, terminals, queues, approvals, provider state | Remote read only | "Unknown" |

### Execution-machine policy

1. An explicit machine from the user or the launch call. If it is ineligible, the launch is refused with the reason.
2. Otherwise the project worker machine, if set and eligible.
3. Otherwise the coordinator's own machine.

Eligible means connected, granted for this project, signed in to the requested provider and, once 0968 lands, with eligible capacity. The launch result names the chosen machine and each skipped candidate with its reason.

## Decisions

### Asked

- None; the user asked for two orchestrators and two-way pairing.

### Defaulted

- D-01: Last writer wins per memory file with a conflict copy, rather than a merge.
- D-02: Stale claims are released only by the user.
- D-03: The one-way G3 proposal is cancelled.
- D-04: The offline snapshot is the viewing device's own persisted environment cache (nothing is pushed by the viewed machine), so a machine this device never loaded shows "Unknown". The saved switcher choice only records which orchestrator this device last viewed.
- D-05: A message to an offline coordinator is refused; it is never queued for later delivery or handled by another coordinator.

## Tasks

### T-01 Per-machine coordinator bindings and migration
- AC: AC-01, AC-02 | Files: contracts, project service, coordinator UI | Test: migration tests

### T-02 Two-way grants
- AC: AC-03 | Files: workGrantPolicy.ts, pairing flow | Test: loop tests with two coordinators

### T-03 Memory replication
- AC: AC-04 | Files: memory service, fleet wire | Test: conflict tests

### T-04 Fenced plan claims
- AC: AC-05 | Files: plan service | Test: server tests

### T-05 Message routing and ownership
- AC: AC-06 | Files: coordinator routing | Test: server tests

### T-06 Machine switcher
- AC: AC-07 | Files: project page | Test: component tests, headless screenshots

### T-07 Continue handoff-ready threads (after 0967)
- AC: AC-08 | Files: coordinator tools | Test: two-server test

### T-08 Two-server verification
- AC: AC-09 | Files: verification script | Test: the script

### T-09 View, move and migrate actions on the switcher
- AC: AC-10 | Files: CoordinatorConversation.tsx, ProjectWorkspace.tsx, projectCoordinatorMachine.ts | Test: component tests, headless screenshots

### T-10 Honest online and offline parity
- AC: AC-11 | Files: coordinator view snapshot store, project page | Test: server and component tests

### T-11 Thread location labels
- AC: AC-12 | Files: thread rows | Test: component tests

### T-12 Execution-machine policy and migrate tool
- AC: AC-13 | Files: orchestrator toolkit, launch placement | Test: server tests

### T-13 Independent checkouts and pull requests from both machines
- AC: AC-14 | Files: project grouping, project page | Test: unit and component tests

### T-14 Fault and reconnect tests
- AC: AC-15 | Files: two-server script | Test: the script, headless screenshots

### T-15 Verify and close 0969
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
