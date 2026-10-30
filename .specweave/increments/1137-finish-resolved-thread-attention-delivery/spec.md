# 1137: Finish resolved-thread attention delivery

## Problem
PR #940 remains open with a new server TS7022 diagnostic and a Windows Node download failure. Its original fix prevents update-reopened questions from returning resolved chats to Needs you. The user transferred this idle lane for completion.

## Scope
In: repair and validate the existing PR source, reconcile current main without discarding the branch, obtain final-head CI and independent review, and hand merge readiness to the root owner. Out: active update-redesign and terminal-link lanes, live account changes, new provider turns, deployment and worktree deletion.

## Acceptance Criteria
- [ ] AC-01: Existing intended behavior passes focused tests on the reconciled source without test weakening or new type diagnostics.
- [ ] AC-02: Applicable final-head CI and fresh independent review establish merge readiness; any required UI acceptance is explicitly recorded separately.
- [ ] AC-03: Root integration and manual acceptance where applicable are complete before verification and closure.

## Approach
Use the existing worktree and branch, preserve its original commits, merge current origin/main only after the user-authorized owner transfer, fix confirmed failures, and run the smallest focused test/build gates. Source completion does not imply installed acceptance. All browser runs are headless Chrome/Playwright with PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never and reporter open=never. The root coordinates merge/release and independent review.

## Decisions
### Asked
- D-01: On October 28, Anton explicitly approved taking over the idle PR lanes, including this one.
### Defaulted
- D-02: Preserve the existing branch and use normal merge commits for main reconciliation; never force-push or reset away source.
### Open
- None for source repair; new UI manual acceptance remains a closure gate.

## Tasks
### T-01 Reconcile and validate the transferred source
- AC: AC-01 | Files: apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.ts, apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts, packages/client-runtime/src/state/projectAttention.ts, packages/client-runtime/src/state/projectAttention.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts packages/client-runtime/src/state/projectAttention.test.ts apps/web/src/studio/shellModel.test.ts

### T-02 Establish exact-head delivery readiness
- AC: AC-02 | Files: none | Test: gh pr checks 940 -R anton-abyzov/specwithcode-dev and independent final-head review

### T-03 Verify and close 1137
- AC: AC-03 | Files: none | Test: specweave verify 1137, fresh closure review, required manual acceptance, and specweave complete 1137

### T-04 Preserve active forks across resolved ancestry
- AC: AC-01 | Files: apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.ts, apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts --maxWorkers=2

### T-05 Preserve original request chronology across update reopening
- AC: AC-01, AC-02 | Files: apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.ts, apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts, packages/client-runtime/src/state/projectAttention.ts, packages/client-runtime/src/state/projectAttention.test.ts, packages/contracts/src/orchestrationV2.ts, packages/contracts/src/latestProviderTurnForAttempt.ts, packages/contracts/src/reopenedRequestProvenance.test.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/userInputRuntimeRequest.ts, apps/server/src/orchestration-v2/userInputRuntimeRequest.test.ts | Test: actual reopener and client attention chronology regressions, provenance request/JSON round-trip, relevant builds/typecheck, headless attention behavior and fresh independent review

October 29: External independent review blocked9bb3f037 because an original ask newer than a retained ancestor settlement was lost on update. Root transferred this bounded repair. Compare the original ask with each applicable settlement, preserving nested-subagent and fork boundaries. Carry optional reopenedFromAskedAt through the server-only record command and existing request payload JSON; no new database column or migration. Legacy cards lacking provenance remain suppressed against settled ancestors. Capture on subsequent updates preserves original chronology. Extract existing helper/body code before adding to oversized source files. Preserve answered-request, hold/drain and idempotence semantics.
