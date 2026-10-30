# Preserve Windows changed-server coverage across five shards

## Problem

Broad Windows changed-server CI jobs run for sixty minutes and are cancelled while tests still progress. Several dependent PRs also contain genuine assertions; those must remain visible. A shared repair must partition the same selected tests, not hide failures or force each PR owner to invent a workaround.

## Scope

In: Windows changed-server matrix only, coverage manifests and required aggregation, workflow/helper tests and five-way weighted sequencer regression tests. Out: #913 release pipelines, product assertions/manifest/portableGit repairs, other owners' branches, runner size/workers/timeout increases, install/restart/release, active job cancellation or manual reruns.

Owner: existing Windows/Linux lead, agent wl-installed-codex, explicitly authorized by Anton's Extend same lead decision. Branch ci/windows-changed-server-shards; worktree /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/windows-server-changed-sharding. Base2233025d4fe526ffb756c8addb9225b0067729e1.

## Acceptance Criteria

- [ ] AC-01: Changed Windows server selection uses five existing weighted shards with unchanged origin/base selection, two-worker limit and sixty-minute timeout; other matrices retain their coverage.
- [ ] AC-02: At the same pinned head/base, shard manifests prove exact equality with unsharded selected files and unique coverage; broad/narrow/empty selections pass and missing/duplicate/dropped files fail.
- [ ] AC-03: Every planned shard is required by the summary. Missing results, failed/cancelled jobs, mismatched identities and invalid coverage fail; stable artifact names retain all logs and source failures.
- [ ] AC-04: Workflow tests, actionlint and relevant typecheck pass; fresh independent exact-head review is SHIP and applicable real Windows/Linux CI completes without waiver.

## Approach

Emit five changed-server matrix rows using the existing WeightedShardSequencer. Record each job's unsharded Vitest selection and derive its own shard through the actual configured WeightedShardSequencer, with pinned source/base IDs. Vitest list ignores its shard flag, so that flag is deliberately not used for receipts. Verify the aggregate against the planned matrix, fail closed on missing/duplicate/extra results and inconsistent selection. Preserve existing changed reachability semantics and record explicit empty selections when they skip. Keep all planned job results required and retain normal failure summaries. Tests exercise actual embedded matrix logic and actual weighted sequencer, plus negative coverage manifests. No runtime AI or new dependency.

## Decisions

### Asked
- Anton approved Extend same lead, extending native Codex authority specifically to this separate repair.
### Defaulted
- Five shards reuse existing Windows full-suite count and sequencer. Keep two workers and60-minute cap. New manifests are file-backed evidence; no source/test exclusions.
### Open
- none

## Tasks

### T-01 Partition changed-server jobs and enforce exact coverage
- AC: AC-01, AC-02, AC-03 | Files: .github/workflows/platform-tests.yml, scripts/studio-verify/platform-shard-coverage.mjs, scripts/studio-verify/platform-shard-coverage.test.mjs, scripts/studio-verify/platform-tests-workflow.test.mjs, apps/server/src/testUtils/weightedShardSequencer.test.ts | Test: node --test scripts/studio-verify/platform-shard-coverage.test.mjs scripts/studio-verify/platform-tests-workflow.test.mjs; vp test run apps/server/src/testUtils/weightedShardSequencer.test.ts; actionlint .github/workflows/platform-tests.yml

### T-02 Independent review, source/file-union receipt and real OS CI
- AC: AC-02, AC-04 | Files: none | Test: exact-head fresh review and applicable Windows/Linux checks with complete coverage receipts

### T-04 Diagnose the terminal Windows packages timeout without weakening it
- AC: AC-04 | Files: packages/client-runtime/src/state/threadSnoozed.test.ts | Test: full client-runtime suite with unchanged assertions and 5000 ms default; capture bounded synchronous locale timing evidence; fresh exact-head review and real Windows Platform CI. Diagnose before any repair; do not treat a passing diagnostic run alone as proof of a fix.

### T-03 Verify and close 1113
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1113, fresh closure review, specweave complete 1113
