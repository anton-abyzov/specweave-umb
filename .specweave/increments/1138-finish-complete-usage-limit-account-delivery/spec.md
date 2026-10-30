# 1138: Finish complete usage-limit account delivery

## Problem
PR #945 remains open with a failed scripts gate and cancelled Windows checks. The change keeps API-billed, unread and recently seen subscription accounts visible in Usage Limits. The user transferred this idle lane for completion.

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
- AC: AC-01 | Files: apps/server/src/provider/ClaudeProvider.ts, apps/server/src/provider/ClaudeProvider.test.ts, apps/server/src/provider/claudeUsageLimits.ts, apps/server/src/provider/claudeUsageLimits.test.ts, apps/server/src/studio/ClaudeQuotaFailure.test.ts, apps/web/src/components/usage/, apps/web/src/routes/usage.tsx, apps/web/src/index.css, apps/web/tests/usage-limits/, packages/shared/src/usageLimits.ts, packages/shared/src/usageLimits.test.ts, packages/shared/src/usageLimitForecast.ts, packages/shared/src/usageLimitForecast.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/ClaudeProvider.test.ts apps/server/src/provider/claudeUsageLimits.test.ts apps/server/src/studio/ClaudeQuotaFailure.test.ts packages/shared/src/usageLimits.test.ts packages/shared/src/usageLimitForecast.test.ts apps/web/src/components/usage/

### T-02 Establish exact-head delivery readiness
- AC: AC-02 | Files: none | Test: gh pr checks 945 -R anton-abyzov/specwithcode-dev and independent final-head review

### T-03 Verify and close 1138
- AC: AC-03 | Files: none | Test: specweave verify 1138, fresh closure review, required manual acceptance, and specweave complete 1138
