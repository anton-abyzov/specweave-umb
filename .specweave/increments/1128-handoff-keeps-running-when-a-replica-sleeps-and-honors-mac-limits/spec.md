# Handoff keeps running when a replica sleeps and honors Mac limits

## Problem

Two gaps left open by 1121 (PR #941), confirmed by a read of `apps/server/src/handoff`:

1. Self-fence (`HandoffMoves.ts` heartbeat ~1053-1089): when every replica machine of a running thread is silent for more than 90 s, the source interrupts its own turn and sets a document-wide `pausedSince` that blocks new turns on every thread. A sleeping laptop is silent, so the M4 coordinator stops its own work whenever its only other machine sleeps. Silence cannot tell a sleeping peer from a partition.
2. Takeover (`HandoffReceiver.ts`) checks only the grant's project scope. It skips the destination Mac's "Who can run work on this Mac" limits: allowed sign-ins, the access-level ceiling, revoke during the move, and it records no WorkOrigin, so the revoke sweeper never stops a continuation.

## Scope

In: narrow the self-fence to proven own-network loss; guard Continue here with a direct probe of the source and a wake grace; apply account, access-ceiling, revoke and origin rules to peer takeovers. Out: protocol or contract changes, a "going to sleep" message, an isolation fence on side effects, auto-takeover.

## Acceptance Criteria

- [ ] AC-01: A source whose replica machines all go silent keeps running its turns and starts new ones, unless it also cannot reach SpecWithCode Connect (its own network is down); only then does it pause the affected threads.
- [ ] AC-02: Continue here refuses while the source still answers a direct probe, and for 60 s after this machine wakes; a source that is truly unreachable can still be continued.
- [ ] AC-03: A peer takeover is refused at preflight for a sign-in the destination's grant does not allow, runs at no more than the credential's access ceiling (with a notice), is refused if the grant was revoked during the move, and records a WorkOrigin so a later revoke stops it.

## Approach

Plan from a three-design panel plus judge (thread "Fix handoff sleep stop and Mac limits").

- GAP 1, `HandoffMoves.ts` heartbeat: keep the self-fence, but before fencing probe own connectivity (the Connect relay URL, 5 s timeout, any HTTP answer = online). Fence only when that probe fails. No relay configured means isolation cannot be shown, so no fence. Clear legacy `pausedSince` when online. `HandoffTurnGate` gate text no longer says "woke". `continueHere`: wake grace (60 s after server start or a clock jump seen by `HandoffModeReactor`), then `peers.negotiate(source)` with 5 s timeout; any decoded answer refuses `busy`, a non-local unreachable error continues, a local failure falls back to stale-lease only.
- GAP 2: `ReceiverCaller.runtimeCeiling` from `handoffRoute.ts` (credential's `clientRuntimeModeCeiling`); `threadFailures` adds the account check under check `'grant'`; `takeoverLocked` re-reads the grant, clamps runtime mode with `clampRuntimeMode`, records the origin before launch, adds a lowered-mode notice. Self continue (`grant: null`) stays unrestricted.
- Rejected: deleting the fence outright (user chose fence on proven own-network loss), isolation fence (guards only finish actions), new preflight enum value plus protocol bump.

## Decisions

### Asked
- D-01 Fix both gaps here rather than a new thread → yes, implement the recommended approach (user, 2026-10-28)
- D-02 When may the source stop its own threads → only when it can show it lost the network itself, e.g. it cannot reach Connect either (user, 2026-10-28)
### Defaulted (change any before sw-do)
- D-03 Access-level overrun on takeover → lower to the ceiling with a notice, not refuse
### Open
- none

## Tasks

### T-01 Self-fence only on proven own-network loss; guarded Continue here
- AC: AC-01, AC-02 | Files: apps/server/src/handoff/HandoffMoves.ts, apps/server/src/handoff/HandoffModeReactor.ts, apps/server/src/handoff/HandoffTurnGate.ts, apps/server/src/handoff/handoffMove.test.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-fence-grants && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp test run apps/server/src/handoff

### T-02 Takeover honors the destination Mac's work grant
- AC: AC-03 | Files: apps/server/src/handoff/HandoffReceiver.ts, apps/server/src/handoff/handoffRoute.ts, apps/server/src/handoff/handoffIncoming.test.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-fence-grants && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp test run apps/server/src/handoff apps/server/src/fleet

### T-03 Verify and close 1128
- AC: AC-01, AC-02, AC-03 | Files: none | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-fence-grants && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp run @specweave-studio/server#typecheck
