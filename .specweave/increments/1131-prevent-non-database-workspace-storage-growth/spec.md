# 1131 Prevent non-database workspace storage growth

## Problem
Anton reports a Finder snapshot of `.specwithcode` at 214.67 GB logical and 239.23 GB on disk for 1,146,928 items. The live database accounts for only about 21 GB. Earlier cleanup has already run and must not be repeated. The user requests engineering root cause and prevention, with existing storage/setup/release owners preserved.

## Scope
In: current non-database category accounting, original/parallel session and owner reconciliation, the existing PR952 cleanup-gate and release-staging fixes, data-loss regression repair, fresh review, exact-head CI and merge. Out: additional cleanup/deletions, source/root relocation, shared mutable dependency installs, changing Spotlight settings, live database files/migrations, service restart, duplicate engine/setup/release workers.

## Acceptance Criteria
- [ ] AC-01: A retained report attributes current non-database logical bytes and inode-deduplicated allocated blocks by category and path, excludes every `statev2.sqlite*` name before filesystem access, reports symlink/shared-extent limitations, and gives supported-query database size plus current free space.
- [ ] AC-02: Eligible finished worktrees are not kept solely by Finder metadata, dependency symlinks, hook shims, Git GC reflog mtime or checkout-directory mtime; current owners, active writers, dirty/unpushed work and unknown ignored folders remain protected.
- [ ] AC-03: Superseded eligible release staging is pruned at public publication, with locked, foreign, resumable and current folders protected. Whole ignored build folders containing secrets survive the real-Git sweep byte-for-byte; Windows path and unavailable-size behavior pass.
- [ ] AC-04: Original Claude sessions and existing storage/setup/release owners are reconciled, fresh source review passes, exact-head CI is green before merge, the umbrella instruction reaches GitHub without unrelated shared-checkout commits, and source delivery is distinguished from runtime activation or reclaimed disk.

## Approach
Continue user-transferred branch `fix/storage-cleanup-gates` in `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/storage-cleanup-gates`, PR952. Initial changes were implemented by external Claude session `150646e5-8992-4528-85ef-be94678c1f77`. This continuation fixed Windows test portability and a fresh-review data-loss finding by removing broad build/output folder exemptions. Reuse existing owner work: history compaction1107/PR917, workspace lifecycle1108, setup performance1129. Do not treat pnpm logical totals as unique physical bytes: default imports already try CoW clones. Use a single metadata-only no-symlink scan and supported database query, not a duplicate whole-home scan.

## Decisions
### Asked
- D-01 Anton explicitly transferred remaining PR952 ownership to this thread and expanded scope to root cause/prevention.
### Defaulted
- D-02 Preserve broad ignored build/output folders rather than infer that a folder name authorizes deletion.
- D-03 Report allocated blocks as an upper bound because APFS shared clone extents cannot be deduplicated with ordinary stat data.
- D-04 Keep existing setup/dependency owners; no duplicate worker or silent mutable shared node_modules installation.
### Open
- none

## Tasks
### T-01 Measure and reconcile storage mechanisms
- AC: AC-01, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/non-db-usage.json, /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/report.md | Test: python3 /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/verify-evidence.py

### T-02 Repair cleanup safety and portability
- AC: AC-02, AC-03 | Files: apps/server/src/orphanWorktrees.ts, apps/server/src/orphanWorktrees.test.ts, apps/server/src/storageCleanup.ts, apps/server/src/storageCleanup.test.ts, apps/server/src/project/ProjectWorktreeCleanup.ts, apps/server/src/project/ProjectWorktreeCleanup.test.ts, scripts/release/release.sh, scripts/release/release-self-test.sh, AGENTS.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/storage-cleanup-gates && node node_modules/vite-plus/bin/vp test run apps/server/src/orphanWorktrees.test.ts apps/server/src/storageCleanup.test.ts apps/server/src/project/ProjectWorktreeCleanup.test.ts

### T-03 Verify release lifecycle and reviewed delivery
- AC: AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/release-self-test.log, /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/review-r2.md, /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/delivery.json | Test: python3 /Users/antonabyzov/.specwithcode/m4/evidence/disk-reclaim-completion-20261028/verify-delivery.py

Verify and close 1131.
