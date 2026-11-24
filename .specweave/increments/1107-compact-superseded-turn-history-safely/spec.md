# 1107 Compact superseded turn history safely

## Problem
The active M4 database is 19.28 GB with no free pages. Existing growth reduction and scheduled compaction leave full turn-item snapshots and repeated subagent prompts. A backup shown in Finder is distinct from the active machine database and worktree storage. Anton requested a thorough comparison with current upstream and the complete database/storage optimization set, without cherry-picking.

## Scope
In: review current storage optimizations against upstream main 5b70d81b0d77bdd5883a835173735d55992009af; consolidate eligible turn-item snapshots; store repeated subagent prompts once with transparent replay; pace background compaction; retain existing update guards, offline reclaim, identity and licensing. Document already integrated improvements and architectural differences.
Out: unrelated upstream features/history, live database mutation or reclaim, backups deletion, service restart/release, shared owner checkouts and provider accounts. Worktree cleanup remains with its existing owner.

## Acceptance Criteria
- [ ] AC-01: Compaction keeps first/latest eligible turn-item snapshots, all commanded and subagent snapshots, and reproduces identical projections and insertion positions across full/incremental passes and event cursor gaps.
- [ ] AC-02: Repeated unchanged subagent prompts use one durable anchor, restore exactly on every replay/read path, and remain safe after rollback, restart, changed prompts and cache eviction.
- [ ] AC-03: Cached SQLite statements never retain large text/blob bindings and values queries respect SafeIntegers. Background compaction limits duty cycle and page size while preserving all existing update admission and per-delete guards; offline work remains unthrottled.
- [ ] AC-04: A source-backed report distinguishes install/runtime, backup, database and worktree paths, compares upstream optimizations, records synthetic validation and current read-only measurements, and states installed acceptance limits.

## Approach
Build on latest origin/main in isolated worktree /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/storage-history-consolidation. Retain the app's safe SQLite ownership and updater guards; do not replace them wholesale with upstream's connection architecture. Expand retention only for self-contained snapshots, use persisted prompt anchors with bounded in-memory hints validated inside inserts, and add monotonic duty-cycle pauses between background pages. Validate synthetic SQLite replay, receipts, rebuild and update interruption, then run focused persistence tests and production server build.

## Decisions
### Asked
- D-01 Complete storage optimization set or all upstream features? Anton selected complete database/storage optimizations.
### Defaulted
- D-02 No live reclaim or restart; implementation and synthetic evidence first.
- D-03 Preserve single-owner SQLite guards and independent source history. Consolidate behavior into current modules, no upstream cherry-picks.
### Open
- none

## Tasks
### T-01 Consolidate storage growth and compaction optimizations
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/orchestration-v2/ProjectionMaintenance.ts, apps/server/src/orchestration-v2/ProjectionMaintenance.compaction.test.ts, apps/server/src/orchestration-v2/TurnItemCompaction.test.ts, apps/server/src/persistence/OrchestrationEventStore.ts, apps/server/src/persistence/SubagentPromptStorage.test.ts, apps/server/src/persistence/StorageMaintenance.ts, apps/server/src/persistence/StorageMaintenance.test.ts, packages/shared/src/nodeSqliteClient.ts, packages/shared/src/nodeSqliteClient.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ProjectionMaintenance.compaction.test.ts apps/server/src/orchestration-v2/TurnItemCompaction.test.ts apps/server/src/persistence/SubagentPromptStorage.test.ts apps/server/src/persistence/StorageMaintenance.test.ts --maxWorkers=1

### T-02 Review integration and document measured storage behavior
- AC: AC-04 | Files: docs/operations/storage-history.md, reports/storage-review.md, reports/storage-review.html | Test: node apps/server/scripts/cli.ts build

Verify and close 1107.
