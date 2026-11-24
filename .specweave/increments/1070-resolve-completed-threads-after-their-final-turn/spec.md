# Resolve completed threads after their final turn

## Problem
An agent resolving its own thread is rejected because its final turn is still running. Its final report must remain deliverable before resolution.

## Scope
In: durable deferred self-resolution in SpecWithCode, guarded completion, focused regression coverage, merge and canonical app release. Out: changes to completed 1062, another SpecWeave CLI release, live service restart, other owners' worktrees.

## Acceptance Criteria
- [ ] AC-01: Self-resolution persists the exact expected current run and optional note without interrupting it. Automatic application ships behind a server-composition flag default off; only 1069 may activate it with current acceptance evidence.
- [ ] AC-02: A new user message, newer run, pending question/approval, child work, failed/interrupted run, user reopen, pin or auto-settle opt-out prevents stale resolution, including after persistence roundtrip.
- [ ] AC-03: Explicit other-thread resolution retains existing running/queued/request guards.
- [ ] AC-04: Focused tests, production server build, fresh-context adversarial review and exact-head CI pass; merged fix reaches the canonical signed/notarized app release with feed and runtime boundaries recorded.

## Approach
Persist an optional deferred resolution on the thread payload. The MCP handler adds the exact current run only for its own thread. The serialized decider records the intent, invalidates it on intervening work, and the terminal-run reactor resolves after successful completion under the thread lock. Startup recovery finds persisted requests; all guards recheck. Existing explicit settlement remains unchanged. Coordinate with the existing release owner and never restart the live service.

## Decisions
### Asked
- None. Push, merge and deployment are authorized.
### Defaulted
- D-01: Invalidated requests are discarded, never retried for a later run.
- D-02: All pending questions, including asynchronous questions, prevent deferred resolution.
- D-04: Merge-owner decision: default-off server activation until 1069 integrates mandatory acceptance evidence; no environment, UI or RPC toggle and no release hold.
- D-03: Self-settle requires expectedRunId from the observed current turn; missing or mismatched IDs fail closed rather than adopting the active run. Revocation persists for that exact run; a newer run may explicitly request again.
### Open
- none

## Tasks

### T-01 Implement and verify durable deferred self-resolution
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/packages/contracts/src/orchestrationV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/DeferredThreadResolution.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/ProjectionStore.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/DeferredThreadResolution.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/Orchestrator.control-reads.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/mcp/toolkits/thread/handlers.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/mcp/toolkits/thread/tools.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts | Test: focused deferred resolution and MCP tests, production server build

### T-02 Review, merge and deploy through the release owner
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1070-resolve-completed-threads-after-their-final-turn/reports/verification.md | Test: fresh-context adversarial review, exact-head CI, release/feed readback and installed/runtime boundary

### T-03 Persist invalidation and ship default-off activation
- AC: AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/EventSink.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/DeferredThreadResolution.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/Orchestrator.control-reads.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/packages/contracts/src/orchestrationV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/ProjectionStore.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/DeferredThreadResolution.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/mcp/toolkits/thread/handlers.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/mcp/toolkits/thread/tools.ts | Test: provider pending approval and child work appear then finish; deferred intent remains invalidated across guarded ingestion variants; production server build and supported server typecheck

### T-04 Fix CI Effect failure diagnostic
- AC: AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-deferred-self-resolution/apps/server/src/orchestration-v2/EventSink.ts | Test: CI-equivalent server typecheck gate, focused stale-command behavior and production server build

Verify and close 1070.
