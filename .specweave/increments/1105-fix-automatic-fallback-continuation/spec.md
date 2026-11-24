# 1105 Fix automatic fallback continuation

## Problem

On October 27, 2026, 1011 run 47 failed on Claude with `Credit balance is too low`. The server automatically dispatched Codex run 48 within 1.7 seconds, but sent only `Continue where you left off.` Codex interpreted old Claude-only assignment prose as a reason to ask for substitution approval. One pending question remains. The user now explicitly authorizes eligible configured automatic fallback without another provider-substitution question.

## Scope

In: explain automatic fallback authorization in the server-generated continuation, including first-request replay; regressions for stale provider-only prose and existing eligibility gates; record the investigation and project policy. Out: answering 1011's card, taking over 1011, paid provider runs, grants, Stop overrides, settings mutation, branch changes, commits, publication and installed acceptance.

## Acceptance Criteria

- [ ] AC-01: A usage-limit automatic switch sends the chosen provider/model and tells the agent to continue the same assignment without asking for provider substitution because of older provider-specific assignment prose.
- [ ] AC-02: First-request replay retains its exact request and attachments plus the same authorization context; same-provider recovery receives no cross-provider authorization.
- [ ] AC-03: Ask/wait rules, unavailable fallback, billing eligibility, project admission and actual Stop holds still prevent unauthorized continuation, as covered by the existing focused suites.
- [ ] AC-04: A durable report identifies the actual 1011 switch and stale-prose cause, preserves its owner and unanswered card, and distinguishes source validation from installed behavior.

## Approach

Add a small server-only continuation-text helper and apply it only to `limit-fallback:` commands after the existing eligibility decision. Preserve its context when the sweep replays a request from a provider that never answered. Test the actual dispatch command and sweep, plus existing policy, API-credit, Stop and admission suites. No runtime decision or approval response is inferred from agent prose. Work in the approved app checkout without changing its current branch or unrelated untracked files, per this assignment's explicit restriction.

## Decisions

### Asked

- D-01: User policy: eligible configured automatic fallback continues without provider-substitution confirmation; billing, grants and actual Stop holds remain binding.

### Defaulted (change any before sw-do)

- D-02: Limit the new authorization text to server-generated usage-limit fallback. Do not generalize it to manual sends, same-provider credit recovery or non-limit errors.
- D-03: Existing 0968 and fallback-stack work is completed and concerns different behavior. Use this requested increment; preserve the sole 1011 owner.

### Open

- none

## Tasks

### T-01 Make eligible fallback authorization explicit and cover replay
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/automaticFallbackContinuation.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderFallbackWorker.continuation.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderFallbackWorker.unopenable.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ProviderFallbackWorker.continuation.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.policy.test.ts packages/shared/src/providerFallback.apiCreditHome.test.ts packages/shared/src/providerFallbackEligibility.test.ts

### T-02 Verify and close 1105
- AC: AC-04 | Files: .specweave/increments/1105-fix-automatic-fallback-continuation/reports/investigation.md, .specweave/increments/1105-fix-automatic-fallback-continuation/reports/review.md | Test: test -s .specweave/increments/1105-fix-automatic-fallback-continuation/reports/investigation.md
