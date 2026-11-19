# Checks copies and busy chat folders retire safely

## Problem

Increment 1425 (PR #731, merged November 19, 2026) made merged and finished chat worktrees retire on their own, but review cut three things from it:

- **Checks copies are never retired.** Retiring one safely needs two things the app does not have: a lease that `checks run` and the sweep share, held from the first touch until the end, and proof that every commit in the copy exists somewhere else. Review round 1 showed recursive removal losing ignored `.env` files, history that exists only in the copy, and a copy that a check picked up during `du`.
- **Session logs are kept forever.** Only rotated `*.log.N` and `*.ndjson.N` files expire. A live terminal or provider log can be written while the sweep deletes it.
- **18 folders on m4 hold live agent or tool processes** (counted on November 19, 2026). The sweep rightly keeps them, so they never retire, and nobody owns ending those processes.

Non-blocking items from the 1425 reviews, still open:

- A malformed worktree-set manifest still gives a normal kept row and marks the plan complete.
- A failed removal records an inferred sentence, not Git's own diagnostic.
- While the disk stays low, backoff schedules no retry.
- Settled all-default folders with no pull request miss the six-hour path when only the merged rule is on.
- A `.env` basename that contains a newline slips past the secret matcher.

## Scope

In:

- Checks-copy retirement under a shared per-copy lease, with proof that the copy's history is held elsewhere.
- Retiring the logs of sessions whose writers are known to have ended.
- A report in Settings > Storage of folders that only live processes keep.
- The five non-blocking items above.

Out:

- `git worktree prune`. It stays banned in unattended cleanup.
- Any forced or recursive removal of a worktree.

## Acceptance Criteria

- [ ] AC-01: `checks run`, `checks copy` and the sweep take one cross-process lease per copy, from before the first touch through the end. The sweep re-reads its facts under that lease and keeps a copy it cannot lease.
- [ ] AC-02: The sweep retires a checks copy only when the app made it (a positive marker) and it holds no ignored files except known rebuildable ones. It must also hold no hidden tracked changes and no nested repository. Every commit reachable from its refs and reflogs must exist in the source checkout or on a remote. Anything unproven keeps the copy.
- [ ] AC-03: A terminal or provider session log is removed only after its owner has ended. Removal happens under the writer's guard, and the age is checked again under that guard.
- [ ] AC-04: Settings > Storage lists folders kept only because a live process is in them, naming each process and how long it has run.
- [ ] AC-05: An unreadable worktree-set manifest marks the plan incomplete, separately from "size unknown".
- [ ] AC-06: A failed removal keeps a bounded, sanitized copy of Git's own message next to the inferred sentence.
- [ ] AC-07: While the disk stays low, a retry is scheduled, and the backoff is updated from the result of the full pass.
- [ ] AC-08: With only the merged rule on, settled or archived folders whose repositories are all on the default branch, with no pull request, take the six-hour path.
- [ ] AC-09: The secret matcher matches every basename that starts with `.env`, case-insensitive, newlines included.

## Approach

- Lease: one lock file per copy, kept beside the copy under the app's state folder and taken by both CLI entry points and by `storageCleanup.ts`. Re-adds `checksCopyRetention.ts`, taking the 1425 round-1 to round-3 findings as requirements.
- Logs: the terminal and provider writers record when they end. Retention reads that record and never goes by age alone.
- Processes: reuse the `lsof` and process-cwd readers from 1425 in plan mode.
- Risks: the same writer races as 1425. Every check runs under the lease, and a check that cannot be done keeps the item.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The 18 busy folders are reported, never ended by the app (reversible).
### Open
- none

## Tasks

### T-01 Shared per-copy lease for checks copies
- AC: AC-01 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/cli/checks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/verificationCopy.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/cli/verificationCopy.test.ts

### T-02 Checks-copy retirement with history proof
- AC: AC-02 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/checksCopyRetention.ts, repositories/anton-abyzov/specwithcode/apps/server/src/checksCopyRetention.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/checksCopyRetention.test.ts

### T-03 Ended-session log retention
- AC: AC-03 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/storageLogRetention.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageLogRetention.test.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/storageLogRetention.test.ts

### T-04 Busy folders in Settings > Storage
- AC: AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StorageCleanupPlanSection.tsx] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/storageCleanup.test.ts

### T-05 1425 review leftovers
- AC: AC-05, AC-06, AC-07, AC-08, AC-09 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/worktreeCleanupSweep.ts, repositories/anton-abyzov/specwithcode/apps/server/src/worktreeRemovalFailures.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanupTriggers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/finishedWorktrees.ts] | Test: specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/finishedWorktrees.test.ts apps/server/src/storageCleanupTriggers.test.ts
