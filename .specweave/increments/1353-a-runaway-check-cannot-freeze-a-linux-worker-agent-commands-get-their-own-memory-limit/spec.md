# A runaway check cannot freeze a Linux worker: agent commands get their own memory limit

## Problem

On November 14, 2026 linux-mini (Ubuntu, 28 GiB RAM, 8 GiB swap) became unreachable from the M4 three times: 3:10 PM to 5:11 PM, 11:04 PM to 11:07 PM and 11:30 PM to 11:42 PM EST. Its own logs (thread "linux-mini service drops: what its own logs say", read through SpecWithCode) show the cause each time:

- Agent threads started TypeScript typechecks (`tsc`) that grew to 7 to 14 GB each. Swap was 100% full (`Free swap = 0kB`), available memory fell under 1 GB, and the machine thrashed: 13,000 major faults per second, load 54 to 84.
- The kernel killed `tsc` six times, each a global kill (`constraint=CONSTRAINT_NONE ... global_oom`), minutes after the thrash began.
- During the thrash the SpecWithCode server stayed alive but its event loop stalled for 33 s, 45 s, 59 s and 129 s, and cloudflared lost its edge connections (`timeout: no recent network activity`). systemd never restarted the unit (`NRestarts=0`).

The unit's limits did not help: `MemoryMax` is 75% of RAM (23 GB) for the whole unit, server and agent commands together, and the desktop app, browsers and other apps outside the unit use the rest. Nothing reserves memory for the server, and nothing ends oversized agent work before the whole machine thrashes. Increment 1279 keeps the app alive when the kernel kills something; it does not stop the thrash that comes first.

## Scope

In: on Linux, the server and its tunnel keep answering while agent commands exhaust their memory; agent work that exceeds its share is ended quickly inside its own group, and the thread that started it is told why.

Out: macOS and Windows. Queueing or limiting how many heavy checks run at once. Telling other machines "busy" (follow-up of 1352). Changing swap or installing system packages on the machine.

## Acceptance Criteria

- [ ] AC-01: On a Linux worker, the server process and cloudflared run with a memory reservation that agent commands cannot take, and agent commands run under one limit below the machine's memory with no swap of their own. The limits are visible in the unit and its cgroup files.
- [ ] AC-02: With an agent command allocating past the limit, the server answers `/.well-known/studio/environment` in under 2 s throughout, and the command is ended within 30 s.
- [ ] AC-03: The thread whose command was ended gets a plain message naming the command, the limit and what to do (run fewer heavy checks at once).
- [ ] AC-04: A machine whose cgroup setup is unavailable (no cgroup v2, no delegation) starts and works as before, and says so once in the service log.
- [ ] AC-05: An existing installation picks up the new limits on its next update without a manual step.

## Approach

Decided in T-01 (closes O-01): cgroup v2 delegation inside `studio.service`, set up by the server when it starts. Evidence is in `reports/design-read.md`.

Mechanism:

- The unit gets `Delegate=yes`. Under the unit's cgroup the server makes three groups: `server` (launcher, server, cloudflared) with `memory.min` and `memory.swap.max=0`; `agents` (everything else the server starts: harnesses, their commands, terminals, helper browsers) with `memory.max` and `memory.swap.max=0`; `apps` (apps the user opened, the 1279 exemption) with no limit. The unit's `MemoryMax=75%` stays as the outer limit.
- Placement needs no change at the spawn sites: children start in `server` because they inherit it, and every 2 s the server reads `server/cgroup.procs` and moves whatever is not the launcher, itself or cloudflared into `agents`. The list comes from the group itself, so a recycled PID outside the unit is never touched (the 1228 rule). The existing per-session ACP groups are created under `agents`.
- The limit on `agents` is the smaller of a ceiling and what the machine has spare: `min(ceiling, max(share, in use + available - headroom))`, rewritten every 2 s. Ceiling = RAM minus the larger of 6 GB and 25% of RAM (D-02), never under half of RAM, and never above the unit limit minus the server reservation. Share = the larger of 4 GB and 25% of RAM, which agent work always keeps. Headroom = the larger of 1 GB and 8% of RAM that agent work may not take from the machine. With no swap of its own, a command that passes the limit is killed by the kernel inside `agents`, largest process first.
- The server reservation (`memory.min`) is the smaller of 2 GB and one eighth of RAM.
- Telling the thread (AC-03): the server watches `agents/memory.events`. Every 2 s while agent memory is high it records the largest agent processes with their command line and `SPECWEAVE_STUDIO_THREAD_ID`; when the kill count rises, the recorded process that is gone is the one ended, and its thread gets a message through `ThreadManagementService.sendToThread` (a notification row for the user, the text for the agent).
- Existing installs (AC-05): in-app and fleet updates on Linux only swap the server under the running launcher; the unit is never rewritten (linux-mini's unit still names 1.0.180). So the server itself adds `Delegate=yes` to an installed unit that lacks it and runs `systemctl --user daemon-reload`, which restarts nothing, then makes the groups. New installs get the line from the renderer.
- Fallback (AC-04): no cgroup v2, no memory controller, not the launcher's child, or a failed write: the server logs one line and runs as before. `STUDIO_AGENT_MEMORY_LIMIT=off` turns it off.

Why, and what was checked on linux-mini (Ubuntu 26.04, systemd 259, kernel 7.0, no root used):

- A user service with `Delegate=yes` may create child groups and set `memory.max`, `memory.swap.max` and `memory.min`; a 300 MB allocation under a 200 MB limit was killed in 0.1 s and counted in `memory.events`.
- Without `Delegate`, a `daemon-reload` removes the memory controller from the child groups (the limits vanish, the processes stay). With `Delegate=yes` added to the file of a running unit, one `daemon-reload` applies it and the limits then survive reloads and property changes. So the unit line is required, and no restart is.
- Stopping the unit ends processes in child groups, so `KillMode=mixed` keeps working.
- `memory.min` is not honoured against machine-wide reclaim: every ancestor up to `user.slice` has `memory.min=0` and the top two are root's. It protects the server only when the unit hits its own limit. The real protection is that agent work cannot swap and cannot grow past what is spare, and that the server's memory cannot be swapped out.
- A fixed limit of RAM minus the reserve would not have stopped the November 14 incident: the unit stayed under its 23 GB limit while other apps and a full swap used the rest. That is why the limit follows available memory.
- Transient scopes (`systemd-run --user --scope`) land outside `studio.service`: they escape the unit's outer limit and its stop, and need the user bus for every spawn. Rejected.
- Also rejected: a per-command cap (a legitimate typecheck of this repository needs 7 to 14 GB); `systemd-oomd` on the whole unit (it would end the server too, and is not installed); a watchdog restart of the server (it was alive, and a restart drops every thread's stream); setting the groups up in the launcher (it keeps running the old version across updates).

Risk: memory a process allocates before it is moved (at most 2 s) stays charged to `server`, so a command that grows very fast in its first seconds is limited only from the move on. The kernel ends the largest agent process, which can be an idle large one rather than the one growing, and may end two (round 3); every ended process's thread is told.

Known limits (review round 1): an ACP session group made before the first limit is written, or while a vanished limit waits to be set up again (at most 30 s), stays where it was made and is not limited until that session ends; moving its processes would break the session's own teardown. The thread named in a process's environment is told without checking which agent set it; the message is server-written and limited to one a minute per thread. Setup that fails five times stays off until the server restarts.

Risk: ending a command a user wanted. It can happen only when agent work is above its share and the machine has less than the headroom available, or agent work is at the ceiling; the kernel then ends the largest agent process, and the message in AC-03 says why. A harness is ended only if it is the largest agent process at that moment.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Limit agent commands as one group, not per command.
- D-02 Reserve for the server and the rest of the machine: the larger of 6 GB and 25% of RAM.
- D-03 Live proof runs on linux-mini with one bounded allocation, at a time no other heavy check runs there.
- D-04 (was O-01) Mechanism: cgroup delegation set up by the server, not transient scopes. See Approach.
- D-05 The agent limit follows available memory under a fixed ceiling; agent work always keeps the larger of 4 GB and 25% of RAM.
- D-06 The server adds `Delegate=yes` to an installed unit and reloads the user manager; it never restarts the unit.
### Open
- none

## Tasks

### T-01 Read the spawn path and the unit, record the mechanism
- AC: AC-01, AC-04 | Files: .specweave/increments/1353-a-runaway-check-cannot-freeze-a-linux-worker-agent-commands-get-their-own-memory-limit/spec.md | Test: grep -c "O-01" .specweave/increments/1353-a-runaway-check-cannot-freeze-a-linux-worker-agent-commands-get-their-own-memory-limit/spec.md

### T-02 Server and tunnel reserved, agent commands limited
- AC: AC-01, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/cloud/bootService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/bootService.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/resourceTelemetry, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpSessionRuntime.ts, repositories/anton-abyzov/specwithcode/docs/user | Test: pnpm --dir apps/server exec vp test run src/cloud/bootService.test.ts src/resourceTelemetry/AgentMemoryLimit.test.ts

### T-03 The thread hears why its command ended
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src | Test: pnpm --dir apps/server exec vp test run src/resourceTelemetry/AgentMemoryNotice.test.ts

### T-04 Live proof on linux-mini
- AC: AC-02 | Files: .specweave/increments/1353-a-runaway-check-cannot-freeze-a-linux-worker-agent-commands-get-their-own-memory-limit/reports | Test: test -s .specweave/increments/1353-a-runaway-check-cannot-freeze-a-linux-worker-agent-commands-get-their-own-memory-limit/reports/live-proof.md

### T-05 Verify and close 1353
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1353-a-runaway-check-cannot-freeze-a-linux-worker-agent-commands-get-their-own-memory-limit/spec.md | Test: specweave verify 1353
