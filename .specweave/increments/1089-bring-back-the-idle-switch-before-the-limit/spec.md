# Bring back the idle switch before the limit

Follow-up to 1075. Reconciled October 26, 2026 against main `0ed403feeb`; re-checked November 19, 2026 against `origin/main` `1d47f5078` of `repositories/anton-abyzov/specwithcode`: the gate is unchanged (`providerLimitStep` at line 494, its `!stoppedOnLimit` return at line 566, the `limit-preswitch:` id at line 281). Anton chose "fix the code" on November 19, 2026, so `docs/user/usage.md` ("Switch before the limit") stays as written.

## Problem

"Switch before the limit" (`providerLimitSwitchAtPercent`, docs/user/usage.md) promises that an idle thread whose provider has reached the threshold moves to the fallback before its next turn. The idle branch still exists in `providerFallbackCommand` (`limit-preswitch:` command ids in `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts`), but since `b19af6f228` the sweep reaches it only through `providerLimitStep`, which returns null unless the thread `stoppedOnLimit`. So no idle thread is ever pre-switched, no `limitPreswitchFrom` origin is recorded, and the 1075 way back (`limit-preswitch-return:`) never has anything to return.

## Scope

In: make the idle pre-switch reachable from the sweep again, with the same guards a limit stop has (Stop holds, admission re-check, snooze, machine handoff ordering, simulated limits, settings off by default).

Out: the chip tooltip (1088), the way back itself (1075), new settings.

## Acceptance criteria

- [ ] AC-01: With the switch rule on and `providerLimitSwitchAtPercent` set, an idle, free thread whose provider usage is at or over the threshold gets one `limit-preswitch:` model-selection move per usage window from the sweep, and the Orchestrator records `limitPreswitchFrom`.
- [ ] AC-02: Nothing moves mid-turn, for a settled thread, a thread with no run, a person's Stop hold, the `wait`/`ask` actions, or when no threshold is set; a limit stop keeps its existing step order (reset, credits, API credits, then switch).
- [ ] AC-03: The admission re-check, failed-target bookkeeping and machine-handoff trigger treat the idle move correctly (no repeated sends, no dispatch-retry loop for a model-selection command).
- [ ] AC-04: Deterministic tests cover the idle move end to end through the sweep, its idempotent command id, each AC-02 exclusion, and the pre-switch then 1075 return round trip.

## Approach

Let `providerLimitStep` fall through to the idle branch of `providerFallbackCommand` when the thread did not stop on the limit and the action is `switch`, returning it as a `switch` step, and audit every sweep consumer of `switch` steps for a `thread.model-selection.set` command.

Found in the November 19 re-check and two review rounds, and part of the fix:

- The move goes to a free thread between turns, after a turn that completed: never mid-turn, never for a provider-spawned subagent or a session still hosting background work (`activityRunStatus`, `hostsBackgroundWork`). `idlePreswitchId` decides this and names the window's `limit-preswitch:` id.
- Pick-wins is the documented contract: one move per usage window, and a hand switch back is kept until the window resets. A model picked while its provider is at the threshold is moved once per window between turns, then returned to when it has room. The latest-run pick heuristic was dropped in review round 2 (it blocked legitimate moves after a way back).
- A pick that lands after the sweep planned the move wins: the command carries `expectedModelSelection`, and the Orchestrator refuses a move whose thread selection changed since. It also refuses a `limit-preswitch:` move once a turn started or the latest one did not complete, and on a person's Stop on the latest turn (`limitPreswitchGuard.ts`, `stopHoldsLimitResume`). The sweep also reads the Stop on the latest run whatever its status (`stopHoldsLatestRun`), before the move and again at commit.
- One try per window. A retry id (`:retry-N`) would break `preswitchWindowResetAt`, which the way back reads, so a failed model-selection move stays sent and is never resent; it adds no failed target. An already-sent move leaves the thread as one with no step, so the way back still runs and the sweep reads nothing more each time. Accepted ids persist as command receipts across a restart.
- A forward pre-switch carries queued sends that inherited the old selection, as the way back does (`runsFollowingWayBack`), so the first to start does not put the thread back on the limited provider.
- A refusal because a turn beat the move (`PRESWITCH_TURN_STARTED`) is not recorded as a rejected receipt, and the worker frees the id for it, so the window's move can go out after that turn. Pick and Stop refusals keep the window spent.
- An idle thread at the threshold whose fallback readings are old reads them again through the existing throttled `refreshStaleTargets`, unless this window's move already went out.
- The top `pickedSinceStop` guard applies to limit stops only, and the 1075 way back no longer reads a pre-switched selection as a person's pick (`pickedSinceRun`).
- Settings and defaults do not change.

Test lines run from the umbrella root of a worktree or verification copy with the app's dependencies installed; on the M4, only through `specweave-studio checks run`.

## Review

- Reviewer: openai (gpt-6.1-sol)
- Depth: deep
- Required: yes

Run on Copilot Enterprise (`acpRegistry_copilot`, model `gpt-6.1-sol`) under Anton's standing rule of November 18, 2026: when Muse and Codex are both out, Claude-written code is reviewed there without asking again.

## Tasks

### T-01 Reach the idle pre-switch from the sweep
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitPreswitchGuard.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/ProviderFallbackWorker

### T-02 Scenario tests
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.idlePreswitch.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.preswitchReturn.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitPreswitchGuard.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.preswitchOrigin.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/ProviderFallbackWorker.idlePreswitch src/orchestration-v2/ProviderFallbackWorker.preswitchReturn src/orchestration-v2/MachineLimitHandoff src/orchestration-v2/limitPreswitchGuard src/orchestration-v2/Orchestrator.preswitchOrigin

### T-03 PR, exact-head CI, review, merge and release

### T-04 Verify and close 1089
