# Recheck current Team Rules before retrying auto approvals

## Problem

A queued retry can automatically approve a runtime request after the machine policy or the current thread mode no longer permits it.

## Scope

Full-access automatic answers on main. Phase 3 remains with its branch owner.

## Acceptance Criteria

- [ ] AC-01: Each automatic answer checks the current pending request, effective runtime mode, and machine policy. A retry under a tightened ceiling or a policy hold leaves the request pending for a person.

## Tasks

### T-01 Recheck authorization for each answer attempt
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/FullAccessApprovals.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/FullAccessApprovals.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm --filter specweave-studio test FullAccessApprovals.test.ts
