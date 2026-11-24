# Keep edited fork titles and seed automatic titles from typed messages

## Problem

A suffix heuristic cannot distinguish an automatic fork title from an explicitly chosen title.

## Scope

Keep edited fork titles and seed automatic titles from typed messages and targeted regression verification.

## Acceptance Criteria
- [ ] AC-01: Only the automatic placeholder is replaced by a typed first message. Custom titles survive. Existing forks without provenance retain their title.

## Tasks
### T-01 Keep edited fork titles and seed automatic titles from typed messages
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ThreadForkService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ThreadLaunchService.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/testkit/ThreadFork.integration.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatView.tsx | Test: pnpm --filter specweave-studio test ThreadLaunchService.test.ts ThreadFork.integration.test.ts
