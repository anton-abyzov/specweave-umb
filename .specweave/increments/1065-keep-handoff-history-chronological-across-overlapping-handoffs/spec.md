# Keep handoff history chronological across overlapping handoffs

## Problem

Found by the 1004 review (R27, `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/context-switch-audit.md` section "overlapping handoffs can reverse semantic chronology"). `ContextHandoffDelivery.ts:108` (specwithcode-dev `ab96f4d1c`) reselects all pending histories under one budget by concatenating them in creation order and keeping the first copy of each item ID. When two pending histories overlap, `[later]` then `[earlier, later]`, the delivered order is `[later, earlier]`, so the receiving model reads history out of order. Upstream T3 does the same (`ContextHandoffDelivery.ts:56` at `18e2742519`). Whether a real switch builds that pair (bounded selection, overlapping recovery records, appended missed items) is not established.

Repro (isolated): copy `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/probes/ContextHandoffOrdering.audit.test.ts` into `apps/server/src/orchestration-v2/` of a main checkout and run `pnpm exec vp test run apps/server/src/orchestration-v2/ContextHandoffOrdering.audit.test.ts` on Node 22. Expected `["item:earlier","item:later"]`, actual `["item:later","item:earlier"]`; assertion at line 115 fails. Receipt: `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/context-switch-ordering-probe.log`.

## Scope

In: a caller-level test showing whether production paths create overlapping pending histories, then a global chronological merge when combining them. Out: approval cleanup (1064); changes to handoff budgets or pointer-only delivery (#611).

## Acceptance Criteria

- [x] AC-01: A caller-level regression establishes whether the provider-switch, recovery and missed-item paths can produce overlapping pending histories.
- [x] AC-02: Combined delivery orders items chronologically by a real ordinal (not lexical IDs or run IDs); the probe passes.
- [x] AC-03: Cross-thread and fork attribution and the 4,096-byte pointer floor behave as before (existing ContextHandoff tests stay green).

## Results

Fixed in PR 671 (merge `b8f9c0bcc`), released in 1.0.378. The audit probe reproduced on pre-fix main `1d47f5078`: `["item:later","item:earlier"]`.

- Proof for AC-01: the caller-level regression in `testkit/ProviderSwitch.integration.test.ts` (Claude run, failed Claude start, Codex detour, back to Claude) passes on the tests-only commit `cb478f865` too, so that production path already delivers the missed run before the detour; the reorder was not reached through it. The merge is kept as a guard (D-01 stays P2).
- Proof for AC-02: `ContextHandoffBudget.test.ts` "pending handoff chronology" (probe, same-thread ordinal order, delivered bridge, 2,000 histories); the probe and ordinal cases fail on `cb478f865` and pass in PR 671 CI.
- Proof for AC-03: single and fork-source histories keep their order; existing ContextHandoff suites green in PR 671 CI (server shards and typecheck).
- Review: Copilot Enterprise `gpt-6.1-sol`, three rounds, ship at `651c6fc1e`.

## Approach

Find or add a durable item ordinal (run ordinal plus item position) on historical messages, then merge pending histories by it before the budget pass. If AC-01 shows overlap cannot happen, record that and keep the probe as a guard test.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: P2 until AC-01 proves reachability on a production path.
### Open
- none

## Tasks

### T-01 Caller-level reachability test
- AC: AC-01 | Files: apps/server/src/orchestration-v2/testkit/ProviderSwitch.integration.test.ts | Test: pnpm exec vp test run apps/server/src/orchestration-v2/testkit/ProviderSwitch.integration.test.ts
- Files changed from `ContextHandoffService.test.ts` on November 19, 2026: the pending list is assembled in `ProviderTurnStartService.ts` (resume-fallback summary prepended, missed-run retry appended), so the caller-level test drives a real switch in the switch harness.

### T-02 Chronological merge of pending histories
- AC: AC-02, AC-03 | Files: apps/server/src/orchestration-v2/ContextHandoffDelivery.ts, apps/server/src/orchestration-v2/ContextHandoffBudget.ts, apps/server/src/orchestration-v2/ContextHandoffBudget.test.ts, packages/contracts/src/orchestrationV2.ts | Test: pnpm exec vp test run apps/server/src/orchestration-v2/ContextHandoff

### T-03 Verify and close 1065
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1065-keep-handoff-history-chronological-across-overlapping-handoffs | Test: specweave verify 1065 and fresh-context review
