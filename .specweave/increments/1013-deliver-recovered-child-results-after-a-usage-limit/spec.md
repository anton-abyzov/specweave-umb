# Deliver recovered child results after a usage limit

## Problem
An app-owned child can report a usage-limit failure to its parent before automatic fallback starts. The first result transfer then suppresses the continuation result forever. The live limit-recovery child reproduced this on installed 1.0.74: Claude failed, Codex automatically continued, but the parent retained an acknowledged failure.

## Scope
Repair result delivery after a child resumes from a failed, cancelled or interrupted result. Preserve exactly-once delivery per result run, successful-result finality, disposed deliveries, parent cohorts and user Stop. Existing fallback selection, billing and reset workers remain unchanged.

## Acceptance Criteria
- [ ] AC-01: A recovered child can deliver its newer result after its earlier failure was acknowledged or delivered.
- [ ] AC-02: Replay creates no duplicate result or wake; successful prior results and disposed deliveries stay final.
- [ ] AC-03: Focused recovery tests and production server build pass; fresh review passes and the repair merges for the release owner.

## Approach
Use the previous result transfer's source run to distinguish replay from a genuinely later recovery. Re-arm completion delivery only for a later result after an unsuccessful run. Retain historical transfers and existing cohort disposal checks. Exercise the real orchestrator with persisted child and parent events, including acknowledged first failure and continuation completion.

## Decisions
### Defaulted
- Keep the initial failure visible; send a new result when recovery actually finishes.
- Do not start turns or change billing policy to repair delivery.
### Open
- none

## Tasks
### T-01 Repair recovered child result delivery
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/orchestration-v2/DelegatedCompletionDelivery.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/orchestration-v2/ProjectionStore.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/orchestration-v2/ProjectionRecovery.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/mcp/OrchestratorMcpService.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/packages/contracts/src/orchestrationV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/mcp/OrchestratorMcpService.test.ts | Test: focused DelegatedCompletionDelivery and fallback/reset tests; production server build

### T-02 Review and merge the repair
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/limit-child-result-20261023 | Test: fresh-context review and exact-head CI; merge repair; notify sole release owner

### T-03 Verify and close 1013
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1013-deliver-recovered-child-results-after-a-usage-limit | Test: specweave verify and fresh-context review, then specweave complete

### T-04 Keep the earlier result when a recovery is stopped
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/limit-child-result/apps/server/src/orchestration-v2/DelegatedCompletionDelivery.test.ts | Test: stopped-recovery test red then green, six focused suites, server build and typecheck, exact-head CI, merge PR #635
