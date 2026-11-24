# A machine that stops answering reads reconnecting first, says why, and clears without flicker

## Problem

On November 14, 2026 linux-mini ran out of memory six times (agent `tsc` runs of 7 to 14 GB, swap 100% full). Each time its service froze for 33 to 129 seconds and its Connect tunnel lost its edge connections, so the M4 could not reach it for seconds to minutes (11:04 PM for 3 minutes, 11:30 PM for 16 seconds, 11:33 PM for 9 minutes). The machine was on and its desktop moved. The M4 showed "linux-mini is offline", moved all 23 of its threads to an "Offline" group and marked each "Host offline". Anton read that as wrong, and asked for a review of when a machine is displayed as offline.

A read-only review of main at `89d2a9518` (9 readers, 60 findings checked; report in `reports/2026-11-15-when-a-machine-shows-as-offline-review-and-propo-7365a9-0564e9.md`, all findings in `reports/findings-digest.txt`) found:

1. One word for four different things. Any phase other than `connected` or a first `connecting` counts as unreachable (`apps/web/src/state/environments.ts:125`). A 16-second drop, a busy machine, a machine with no tunnel and a stopped connection all read "is offline" and "Host offline". The 3 s grace is skipped whenever the drop carries an error, which a ping timeout or socket close always does (`packages/client-runtime/src/connection/presentation.ts:93`).
2. The cause is known and thrown away. The relay already tells the client whether the tunnel is up but the service is silent (`timeout`) or the tunnel has no connector (`endpoint-unavailable`). The presentation keeps only a phase and a message, and the message tells the user to try a phone hotspot ("Your DNS or firewall may be blocking SpecWithCode Connect") for a remote machine that is merely busy.
3. Surfaces disagree. The same state reads "is offline" (Threads banner, composer), "Can't reach" (chat banner), "Can't reach. Retrying automatically" (machine status), "connecting" (limits) and "Reconnecting to ..." (iPhone).
4. Recovery depends on the notice being on screen. The supervisor's retry gap grows to 300 s, or 600 s after the relay says the endpoint failed. Only a visible Threads notice asks again every 30 s. Another window, or a hidden one, can show a returned machine as offline for up to 10 minutes.
5. Try again can drop a slow machine. A manual retry probes a connected remote with a 3 s limit (`supervisor.ts:62`) and tears the session down when the answer is slower.
6. Connected can still read offline. After a reconnect the Offline group follows the thread list's resync, which has no timeout on its completion marker (`packages/client-runtime/src/state/shell.ts:169`), and a resyncing machine is worded "Some machines are offline" (`projectAttention.ts:437`).

## Scope

In: one reach judgement for a remote machine, used by every web surface; a 60 s reconnecting grace during which threads keep their groups; cause-specific wording after the grace; the firewall hint only when the relay itself could not be reached; a 60 s retry ceiling for a recently connected machine in every window; a manual retry that cannot drop a slow session; a bounded resync after reconnect worded as catching up.

Out: the worker announcing "updating", "restarting" or "busy" ahead of time (needs a relay contract change; follow-up). A push from the relay when a machine returns. Merging the server's own fleet check (Settings > Machines, pickers) with the browser's judgement. Handoff heartbeats. The iPhone app's wording. The memory problem on the worker itself (increment 1353).

## Acceptance Criteria

- [x] AC-01: For 60 s after a remote machine's connection drops, every web surface says "Reconnecting to {name}…", its threads stay in their groups (Needs you, Working, Idle) without "Host offline", and nothing says "offline". A drop that heals inside 60 s never shows the Offline group or an error text.
- [x] AC-02: After 60 s without a connection, the wording follows the cause: "{name} isn't answering" when the tunnel is up and the service is silent or a session stopped responding; "{name} is offline" when its Connect address has no service behind it; "This device has no network" when the browser is offline; the stopped text when the connection was refused. Each says when it last answered and that it retries by itself. The Threads banner, chat banner, composer, Overview row, machine status and limits view use the same words for the same state.
- [x] AC-03: "Your DNS or firewall may be blocking SpecWithCode Connect" appears only when the relay itself could not be reached, never when the relay answered about the machine or an established session went silent.
- [x] AC-04: A remote machine that was connected in the last 30 minutes is retried at most 60 s apart in every window, visible or not. A machine not seen for longer keeps the current ceilings (300 s, 600 s).
- [x] AC-05: A manual retry on a connected remote machine that answers in 3 to 15 s keeps the session.
- [x] AC-06: After a reconnect, a machine whose thread list is still resyncing reads "Catching up with {name}…", never offline, and reaches live within 15 s of the stream delivering no completion marker.
- [x] AC-07: Retry attempts do not make the banner or the row labels flicker between states.

## Approach

Model. A remote machine, seen from this device, is in exactly one state:

| State | When | Threads |
|---|---|---|
| Connected | session up, list live | normal |
| Catching up | session up, list resyncing | keep groups |
| Reconnecting | dropped under 60 s ago, or first attempt | keep groups |
| Not answering | over 60 s; last failure is a relay `timeout`, a ping timeout or a failed health check | Offline group, row "Not answering" |
| Offline | over 60 s; relay says `endpoint-unavailable` | Offline group, row "Host offline" |
| No network | browser offline | Offline group |
| Stopped | blocked or unsupported | Offline group, existing texts |
| Can't reach | over 60 s; the relay itself gave no answer | Offline group, row "Can't reach host", firewall hint |
| Connecting | inside the grace with no session yet in this run | keep groups |
| Not connected | turned off | Offline group |

Changed during implementation (November 15, 2026): the code needed three more states than the table had. "Can't reach" carries the firewall hint (AC-03) so the hint is a state, not a suffix on every error. "Connecting" is a machine never reached in this run, so the grace names it "Connecting to {name}…" rather than "Reconnecting". "Not connected" is a machine turned off. The grace also covers no network.

- `packages/client-runtime/src/connection/model.ts`, `supervisor.ts`: the supervisor state keeps `lastConnectedAt` (set when a session ends), `lostAt` (when this outage started) and a sticky `lossFailure`, so a manual retry, which clears `lastFailure` and restarts at attempt 1, no longer blanks the cause or flips the phase back to "connecting" (the flicker in AC-07).
- `packages/client-runtime/src/connection/presentation.ts`, new `reach.ts`: the presentation carries `lostAt`, `retryAt` and `cause` (`not-answering`, `no-service`, `relay-unreachable`, `no-network`, `stopped`), derived from the failure's reason and `machineOffline`. A pure `machineReach(connection, now)` returns the state above. `RECONNECT_GRACE_MS = 60_000`.
- `apps/web/src/state/machineReach.ts` (new, re-exported from `state/environments.ts`), `studio/unreachableHosts.tsx`: one atom judges every machine; `isEnvironmentUnreachable` counts only the down states. The grace end is driven by a timer in the presentation atom (`packages/client-runtime/src/state/presentation.ts`), which publishes a new presentation when a machine's grace ends, rather than a `useClockWhile` per component. A `MachineReachContext` carries the state per machine to rows and banners.
- Web wording through one helper in `apps/web/src/lib/machineStatus.ts` (`machineReachWords`, `machineReachDetail`, `hostDownWord`), used by `components/studio/ProjectExecutionHistory.tsx`, the chat banner (moved to `components/chat/environmentUnavailableBanner.ts` because `ChatView.logic.ts` is at the 1,500-line limit), the composer host status, `components/studio/StudioOverview.tsx` with `studio/overviewMachines.ts` (its old `machineReach` is renamed `overviewMachineState`), `studio/shellModel.ts` (row word), `studio/hostLimitsModel.ts`, `components/studio/CapacityFleet.tsx`, the Run on picker and the thread machine chip. PR #457's Resolve gate keeps `connection.phase !== "connected"`; inside the grace its reason reads "Reconnecting to {name}. Try again in a moment." (`studio/threadResolveAccess.ts`).
- `supervisor.ts`: `retryMaxDelay` is 60 s while `now - lastConnectedAt < 30 min`; a manual retry on a connected remote uses the 15 s probe.
- `packages/client-runtime/src/state/shell.ts`: `SHELL_RESUME_COMPLETION_TIMEOUT_MS = 15_000`, like thread detail. `state/projectAttention.ts` and `studio/shellModel.ts`: a connected, resyncing machine is "catching up" and its threads keep their groups.
- `rpc/session.ts`, `connection/errors.ts`, `connection/supervisor.ts`, `authorization/service.ts`: the hint is no longer appended to socket, descriptor or setup-timeout errors. A relay request that got no answer (`transportFailed` or the client timeout) is marked `relayUnreachable`, which becomes the "Can't reach" state that shows the hint. `relay/managedRelay.ts` needed no change: its own timeout message, the relay request itself timing out, keeps the hint.
- Rejected: hiding drops for longer than 60 s (a truly dead machine must show within about 90 s of the last frame); polling the relay status endpoint as a second signal (the connect attempt already probes the machine); using the server's fleet check for the labels (it is cached for 5 minutes).
- Risk: a machine that is really off reads "Reconnecting" for its first minute. Threads on it show Working during that minute, as they do today during the 30 s it takes to notice silence.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Grace before a drop reads as a problem: 60 s. It covers an update restart (35 s seen) and short memory stalls.
- D-02 Words: "Reconnecting to {name}…", "{name} isn't answering", "{name} is offline". "Host offline" stays only for the offline cause; a busy machine's rows say "Not answering".
- D-03 Retry ceiling 60 s for 30 minutes after the last connection, in every window. A `retryAfterMs` the machine itself asks for still wins over the ceiling: it is the machine's own back-off, not this device giving up.
- D-07 After the grace the wording follows the latest attempt's cause. A relay that alternates `endpoint-unavailable` and a timeout can alternate "is offline" and "isn't answering"; both are true reports of a down machine and neither reads as a recovery, so no stabilisation rule is added.
- D-04 The worker announcing updates and restarts is a follow-up increment.
### Open
- none

## Tasks

### T-01 One reach judgement in the connection layer
- AC: AC-01, AC-02, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/model.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/presentation.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/reach.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/reach.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/presentation.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.reach.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/presentation.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/presentation.test.ts | Test: pnpm --dir packages/client-runtime exec vp test run src/connection/reach.test.ts src/connection/presentation.test.ts src/connection/supervisor.reach.test.ts src/state/presentation.test.ts

### T-02 Every web surface uses it: grace, groups, one wording
- AC: AC-01, AC-02, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/state/environments.ts, repositories/anton-abyzov/specwithcode/apps/web/src/state/machineReach.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/unreachableHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/lib/machineStatus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectExecutionHistory.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/environmentUnavailableBanner.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/overviewMachines.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/hostLimitsModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectWorkspaceModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/threadResolveAccess.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd apps/web && pnpm exec vp test run src/lib/machineStatus.test.ts src/state/environments.test.ts src/studio/shellModel.test.ts src/components/studio/ProjectExecutionHistory.test.tsx src/components/studio/ComposerHostStatus.test.tsx src/components/ChatView.logic.test.ts src/studio/overviewMachines.test.ts src/studio/hostLimitsModel.test.ts src/studio/threadResolveAccess.test.ts src/i18n

### T-03 Recovery: 60 s ceiling for a recent machine, manual retry keeps a slow session
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.reach.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.thisMachine.test.ts | Test: pnpm --dir packages/client-runtime exec vp test run src/connection/supervisor.test.ts src/connection/supervisor.reach.test.ts src/connection/supervisor.thisMachine.test.ts

### T-04 Resync after reconnect is bounded and reads catching up
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/shell.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/shell-resync.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectAttention.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectAttention.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts | Test: pnpm --dir packages/client-runtime exec vp test run src/state/shell-resync.test.ts src/state/projectAttention.test.ts

### T-05 Firewall hint only when the relay could not be reached
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/service.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/rpc/session.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/errors.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/relay/managedRelay.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/errors/transport.ts | Test: pnpm --dir packages/client-runtime exec vp test run src/rpc/session.test.ts src/connection/errors.test.ts src/errors

### T-06 Screenshots of each state, then verify and close 1352
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1352-a-machine-that-stops-answering-reads-reconnecting-first-says-why-and-clears-without-flicker/spec.md | Test: specweave verify 1352
