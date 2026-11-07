# Worker child reports stay with the worker

## Problem

The installed 1094 check on 1.0.103 (October 27, 2026; receipt `/Users/antonabyzov/.specwithcode/m4/evidence/1094-review-state-grouping/installed-1103/RECEIPT.md`) still shows "Complete project work and disk audit · Answer needed · Review 0734 and 0850 closure" under Waiting on you. That child is a `delegate_task` review a worker started on October 21 (`creationSource: mcp`, parent = the worker, `pendingRequestCount: 0`). Its report went to the worker by automatic completion delivery, yet `observeProjectThread` still turns its `reportedBlocker` into an input request that folds into the worker's row. It never clears, because the child never gets a user message. 1094 excluded only provider-native subagents.

## Scope

In: `reportsToParentAgent` in `packages/client-runtime/src/state/projectAttention.ts` also covers a `delegate_task` child whose parent is not a project coordinator; tests and the headless review-routing fixture. Out: a coordinator's workers (they report to the person, because the coordinator never repeats their results), real pending approvals, questions, sign-ins, plans and held queues, iOS, server-side blocker derivation, thread state writes, merge, release and install.

## Follow-up scope (October 27, 2026)

Extend this existing PR chain with dependency waiting. Reserve Waiting on you for actual user actions, including real child permissions. Dependency reports and active dependency waits belong in Waiting, with a concrete reason. Do not mutate live requests or bypass approvals. Preserve Stop holds and settlement. Accepted-skip schema work is coordinated separately with the CLI/ledger owner.

## Acceptance Criteria

- [x] AC-01: A worker's `delegate_task` child with a report blocker and no pending request adds no attention. Its worker is grouped by its own state, and project counts exclude the child.
- [x] AC-02: The same child's real pending question still puts the worker under Waiting on you.
- [x] AC-03: A coordinator's worker (parent `project-coordinator:…`) with a report blocker still waits on the person as "Blocked".
- [x] AC-04: The headless review-routing fixture shows the worker of a delegate_task review under Idle with no "Answer needed", and the blocked-attention regression check still passes.

- [ ] AC-05: Explicit CI, review, PR merge and subagent dependencies appear under Waiting with specific reasons and add no user-attention count or notification.
- [ ] AC-06: Real questions, permissions, sign-in, plans and held queues still require the person; answered/superseded prompt regressions are covered without clearing actual pending approvals.
- [ ] AC-07: Headless desktop/mobile-width light/dark fixture proves dependency and user-request grouping, counts and row words agree.

- [ ] AC-08: Pending coordinator question cards survive bounded history outside their original turn; badges, explicit coordinator/worker totals and rendered requests remain consistent through answer, reconnect and empty/loading states.

- [ ] AC-09: Subagent popups show only the selected thread subtree, prioritize actionable/active/unknown/recent branches, preserve ancestry and active descendants, collapse older history with reconciled counts, and stay correct across thread switches.

## Approach

Extend the 1094 predicate. A subagent-lineage thread reports to an agent when it is provider-native, or when its parent is not a project coordinator. Every consumer (aggregation, row words, notifications, overview, live questions) already goes through `observeProjectThread` or `threadBlocker`, so they change together.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The coordinator is recognised by its `project-coordinator:` thread id prefix, the host's naming rule (`apps/web/src/studio/projectCoordinatorThreads.ts`).
### Open
- none

## Tasks

### T-01 Predicate, tests and fixture
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/review-routing-check.mjs | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/packages/client-runtime && ../../node_modules/.bin/vp test run src/state/projectAttention.test.ts

### T-02 Verify and close 1095
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1095-worker-child-reports-stay-with-the-worker/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/web && ../../node_modules/.bin/vp test run --project unit src/studio/shellModel.test.ts


### T-03 Distinguish dependency waits from user actions
- AC: AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/docs/studio/thread-status.md, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/reportDocument.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/reportDocument.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/models.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threadRequests.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threadRequests.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionSettlement.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectWorkspaceModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadSubagents.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadSubagents.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/SubagentsChip.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/SubagentsChip.test.tsx, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/projectAttention.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/review-routing-check.mjs | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/packages/client-runtime && ../../node_modules/.bin/vp test run src/state/projectAttention.test.ts

### T-04 Verify and close 1095
- AC: AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/1095-worker-child-reports-stay-with-the-worker/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/web && ../../node_modules/.bin/vp test run --project unit src/studio/shellModel.test.ts


### T-05 Preserve pending request cards and explain counted coordinator scope
- AC: AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/threadHistoryPaging.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/attention-fixture.tsx, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionStore.longTurns.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspace.question.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/review-routing-check.mjs, repositories/anton-abyzov/specwithcode-dev/docs/studio/thread-status.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/server && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/ProjectionStore.longTurns.test.ts

Verify and close 1095 after installed acceptance.


### T-06 Reconcile exact-head integration assertions
- AC: AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspace.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspace.threads.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectThreadHeader.test.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/web && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/studio/ProjectWorkspace.test.tsx src/components/studio/ProjectWorkspace.threads.test.tsx src/components/studio/shell/ProjectThreadHeader.test.tsx

Verify and close 1095 after exact-head CI and installed acceptance.


### T-07 Prioritize current subtree work in subagent popups
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/subagents-check.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectThreadHeader.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadSubagents.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadSubagents.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/SubagentsChip.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/SubagentsChip.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/panes.css, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/docs/studio/thread-status.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/web && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run --project unit src/studio/threadSubagents.test.ts src/components/studio/shell/SubagentsChip.test.tsx

Verify and close 1095 after exact-head CI and installed acceptance.


### T-08 Prove the installed EasyChamp legacy-request failure
- AC: AC-06, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threads.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threads-sync.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threadRequests.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionStore.longTurns.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threadRequests.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, .specweave/increments/1095-worker-child-reports-stay-with-the-worker/reports/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/packages/client-runtime && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/state/threadRequests.test.ts

Verify and close 1095 after exact-head CI and installed acceptance.


### T-09 Keep resolved parents out of working counts and verify badge transitions
- AC: AC-06, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectWorkspaceModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/attention-fixture.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/web && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run --project unit src/studio/shellModel.test.ts

Verify and close 1095 after exact-head CI and installed acceptance.

### T-10 Regress the disk owner's answered decision with historical review attention
- AC: AC-01, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectAttention.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/attention-fixture.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/packages/client-runtime && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/state/projectAttention.test.ts

Verify and close 1095 after exact-head CI and installed acceptance.
