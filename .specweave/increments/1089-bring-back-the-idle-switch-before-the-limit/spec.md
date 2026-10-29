# Bring back the idle switch before the limit

Follow-up to 1075. Reconciled October 26, 2026 against main `0ed403feeb`.

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

## Tasks

### T-01 Reach the idle pre-switch from the sweep
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/orchestration-v2/ProviderFallbackWorker.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/1089-idle-preswitch/apps/server && pnpm exec vp test run src/orchestration-v2/ProviderFallbackWorker

### T-02 Scenario tests
- AC: AC-04 | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/1089-idle-preswitch/apps/server && pnpm exec vp test run src/orchestration-v2

### T-03 PR, exact-head CI, review, merge and release

### T-04 Verify and close 1089
