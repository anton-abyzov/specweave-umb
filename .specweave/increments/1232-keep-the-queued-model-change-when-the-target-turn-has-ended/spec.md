# Keep the queued model change when the target turn has ended

## Problem

A delayed promote request can reorder the queue or interrupt background work after its target turn ends.

## Scope

Keep the queued model change when the target turn has ended and targeted regression verification.

## Acceptance Criteria
- [ ] AC-01: A terminal target is rejected before side effects and its queued request remains intact.

## Tasks
### T-01 Keep the queued model change when the target turn has ended
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/QueuedPromoteToSteer.integration.test.ts | Test: pnpm --filter specweave-studio test QueuedPromoteToSteer.integration.test.ts
