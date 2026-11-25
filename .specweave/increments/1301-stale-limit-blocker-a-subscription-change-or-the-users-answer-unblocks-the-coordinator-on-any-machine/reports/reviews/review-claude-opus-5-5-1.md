<!-- specweave review: reviewer=claude-opus-5-5 model=claude-opus-5-5 family=claude author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=51c9a591a3efb7d38719a6ecba108aebc9da1862 at=2026-11-24T17:57:07.793Z -->
# Review: 1301 AC-02 Stop wins over a subscription change (specwithcode PR #883)
Verdict: ship · risk: medium · 5 files · 0 findings
Reviewer context: new session, Claude Opus 5.5 reviewing GPT-6.2-Astra code. Exact head `51c9a591a3efb7d38719a6ecba108aebc9da1862` against base `bf2021f9e971e6940da089ff7c971f5c5b1b9a7e`.

## Prior high finding: fixed

A subscription change could start a turn on an idle, completed, limit-blocked thread after a person's Stop. It is fixed at the server, where every sender has to pass.

- `limitLifted.ts:303` stamps the automatic message with `limitBlockedReportRunId` (the report's run). The contract field is optional (`packages/contracts/src/orchestrationV2.ts:3515`), so a client sending it can only add refusals.
- `Orchestrator.ts:5916-5923`, in `dispatchMessage`, refuses when the latest executed run is no longer that completed report, and refuses with `STOPPED_THREAD_REFUSAL` when `stopHoldsLimitResume` finds a person's Stop on it.
- Persisted Stop: on an idle thread, `dispatchThreadStop` (`Orchestrator.ts:11546-11554`) has no live target, so it calls `markStoppedRun` on the latest executed run, which is the completed report. That writes a `run_interrupt_request` turn item. `personStopHoldsRun` (`usageLimitRecovery.ts:415`) reads that item, so the hold survives a restart. The only exception is an explicit arm made after the Stop, which is intended.
- Agent and update stops do not hold (`systemInterruptReasons.ts:34`). That matches the existing fallback and recovery rules.
- Serialization: both `thread.stop` and `message.dispatch` go through `threadDispatch.withLock(commandThreadId(command))` (`Orchestrator.ts:13757-13759`). Stop either lands first and the check refuses, or it lands after the turn has started and interrupts it. The worker's own re-read under the settings snapshot (`UsageLimitRecoveryWorker.ts:572-585`) stays only an early skip.
- Normal continuation: shell `latestRunId` excludes queued runs (ProjectionStore tests 2344 and 2684), so it equals `latestExecutedRun` on a thread that passes `isLimitBlockedThread` (`limitLifted.ts:271-272`, which needs a non-null `latestRunId`, so the guard is always armed). The test "the message for a limit-blocked thread ends its Blocked state and starts a turn" still covers this path.
- Test: `Orchestrator.limitLiftedResume.test.ts:352-365` dispatches a real `thread.stop` after the report, then expects the exact refusal, one run and an unchanged blocker. It goes through the real orchestrator, with no mocked subject.

## Evidence

GitHub reports PR #883 OPEN and MERGEABLE at head `51c9a591a3ef`. Every required PR Gate check is SUCCESS: packages, server 1/3 to 3/3, web 1/2 and 2/2, typecheck, Google, and the PR Gate rollup. I ran no local tests (review is read-only). The 105-test green run and the red run on main come from the implementer, and are consistent with the diff: without the new block, main has no Stop check on this path.

SpecWeave: local CLI 3.1.25, registry latest 3.2.3. That is above the 3.1.21 floor, but the local CLI is behind the registry.

Nits: the worker treats a STOPPED_THREAD_REFUSAL as a failure. It logs `blocked-continue-failed` and retries up to `LIMIT_BLOCKED_ATTEMPTS` (3) times (`UsageLimitRecoveryWorker.ts:595-606`). Each retry is refused again, so nothing runs, but the warnings are noise. `isStoppedThreadRefusal` exists and could map the refusal to `skip`.
