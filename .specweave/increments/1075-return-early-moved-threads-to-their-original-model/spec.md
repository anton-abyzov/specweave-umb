# Return early-moved threads to their original model

Follow-up to 0955 AC-06 (deferred there under D-04). Reconciled October 25, 2026 against main `04c2e06d55`.

## Problem

When a thread nears its usage limit, the server moves it to a fallback model before its next turn (`limit-preswitch:` in `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts`). The automatic way back (`limitFallbackReturnCommand` in `apps/server/src/orchestration-v2/limitFallbackReturn.ts`) only follows a continuation run, because it keys on `origin.continuedByRunId`. An early move has no such run, so the thread stays on the fallback after the original provider has room again. The only way back is a manual pick.

## Scope

In:
- record the origin of an early move;
- return to it automatically once the original has room or its reset passes.

Out:
- Claude multi-subscription rotation and the cache-aware return to a Claude home (1055);
- coordinator manual picks (1060);
- exclusions (1052).

## Acceptance criteria

- [ ] AC-01: An early move records its origin (thread, original model selection, usage window, reset time) durably, so a service restart keeps it.
- [ ] AC-02: Once the original provider has room below the switch threshold, or its reset time passes, an idle early-moved thread switches back with no turn of its own. It uses its own `limit-return:` style command id and the queued sends move with it.
- [ ] AC-03: A model the user picked after the early move is never reversed. The 1060 rule holds: the user's pick wins.
- [ ] AC-04: Nothing returns to an origin that is now excluded (1052), billed per token, or Gemini/Vertex. In those cases the thread stays on the fallback and the banner says why.
- [ ] AC-05: Deterministic tests cover early move then reset, early move then room below the threshold, a manual pick in between, a restart in between, and an excluded origin.

## Approach

Store the origin where the 1055 Claude-home return can also read it (a server-local record keyed by thread and command id), and reuse `limitFallbackReturnCommand` with a pre-switch origin in place of `continuedByRunId`.

## Tasks

### T-01 Persist the early-move origin
- AC: AC-01 | Files: apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, apps/server/src/orchestration-v2/limitFallbackReturn.ts | Test: vp test run apps/server/src/orchestration-v2/ProviderFallbackWorker

### T-02 Return after room or reset, never over a manual pick
- AC: AC-02, AC-03, AC-04 | Files: apps/server/src/orchestration-v2/limitFallbackReturn.ts | Test: vp test run apps/server/src/orchestration-v2/limitFallbackReturn

### T-03 Scenario tests
- AC: AC-05 | Test: vp test run apps/server/src/orchestration-v2

### T-04 Verify and close 1075
