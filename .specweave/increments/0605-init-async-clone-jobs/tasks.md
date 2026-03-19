---
increment: 0605-init-async-clone-jobs
title: "Refactor init repo cloning to use background jobs"
generated: 2026-03-19
---

# Tasks: Refactor init repo cloning to use background jobs

## US-001: Init-time clone refactor — foreground mode

### T-001: Add FOREGROUND_CLONE_THRESHOLD constant and mapParsedReposToCloneOptions()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given a `ParsedRepo[]` array with `{ org, name, cloneUrl }` fields → When `mapParsedReposToCloneOptions()` is called → Then each entry maps to `{ owner: org, name, path: "repositories/{org}/{name}", cloneUrl }` with no data loss; and `FOREGROUND_CLONE_THRESHOLD` equals 3

### T-002: Implement runForegroundClone() in repo-connect.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given a list of mapped repos and a valid projectPath → When `runForegroundClone()` is called → Then it calls `execFileNoThrow` (async, not sync) for each repo sequentially, prints inline progress per repo (name + success/failure), updates job progress via jobManager, and returns a `RepoConnectResult` with `totalCloned` and `totalFailed` counts

### T-003: Replace sync clone block in init.ts with foreground launchCloneJob (1-3 repos)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US1-06
**Status**: [ ] Not Started
**Test**: Given init is run with 2 repo URLs → When the clone block executes → Then `launchCloneJob()` is called with `foreground: true`, init blocks until clone completes, `umbrellaDiscovery` is built from clone results (not from `scanUmbrellaRepos`), and no `execFileNoThrowSync` is called for cloning

### T-004: Update src/cli/helpers/init/index.ts exports
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [ ] Not Started
**Test**: Given the updated index.ts → When imports are resolved → Then `mapParsedReposToCloneOptions`, `runForegroundClone`, and `FOREGROUND_CLONE_THRESHOLD` are exported; `cloneReposIntoWorkspace` is no longer exported

### T-005: Update repo-connect.test.ts — new functions, remove cloneReposIntoWorkspace tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given updated repo-connect.ts → When unit tests run → Then `mapParsedReposToCloneOptions` tests cover multi-org repos, single repo, and empty array; `runForegroundClone` tests cover success path, partial failure path, and all-failure path; no tests reference `cloneReposIntoWorkspace`

---

## US-002: Init-time clone refactor — background mode

### T-006: Add background branch to init.ts clone routing (4+ repos)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] Not Started
**Test**: Given init is run with 5 repo URLs → When the clone block executes → Then `launchCloneJob()` is called without `foreground: true`, init returns without waiting for clone completion, a message with job ID and "specweave jobs" instructions is printed, and existing init code sets `umbrella.enabled: true` in config.json before the command exits

### T-007: Update init.test.ts and init-multirepo.test.ts for background mode
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05
**Status**: [ ] Not Started
**Test**: Given mocked `launchCloneJob` → When init is tested with 4+ repos → Then tests assert `launchCloneJob` called without `foreground: true`, init resolves without blocking on clone, and the "Check progress: specweave jobs" message appears in output

---

## US-003: Single-repo handling consistency

### T-008: Verify and test single-repo path layout and foreground mode
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [ ] Not Started
**Test**: Given a single repo URL provided during init → When `mapParsedReposToCloneOptions()` maps it and the threshold check runs → Then `path` is `"repositories/{org}/{name}"` (not workspace root), `launchCloneJob` is called with `foreground: true` (1 repo ≤ 3 threshold), and resulting config.json has `umbrella.enabled: true` with the repo in `childRepos[]`

---

## US-004: Edge cases — already-cloned repos and partial failures

### T-009: Handle already-cloned repos pre-flight skip
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] Not Started
**Test**: Given all provided repos already have a `.git` directory at their target path → When `launchCloneJob()` is called → Then it completes immediately with `skippedPreFlight: true`, no worker is spawned, and the user sees a "skipped" message with the repo count

### T-010: Handle partial failures in foreground and background modes
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [ ] Not Started
**Test**: Given a 2-repo foreground batch where one repo fails to clone → When `runForegroundClone()` finishes → Then per-repo success/failure status is reported, init continues to completion (does not abort), and `RepoConnectResult` correctly reflects `totalCloned: 1, totalFailed: 1`; for background mode with failures, job status is `completed_with_warnings` not `failed`; and for repos with different orgs in the same batch, `mapParsedReposToCloneOptions` maps each to its own `repositories/{org}/{name}` path
