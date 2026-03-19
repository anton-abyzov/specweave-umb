---
increment: 0605-init-async-clone-jobs
title: Refactor init repo cloning to use background jobs
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Refactor init repo cloning to use background jobs

## Overview

Replace the synchronous `cloneReposIntoWorkspace()` in `init.ts` with `launchCloneJob()` from the existing background job system. The repo count determines execution mode: 1-3 repos run in foreground (blocking with inline progress), 4+ repos run in background (non-blocking, monitored via `specweave jobs`). This eliminates the init command blocking on slow network operations for large workspaces while preserving the fast feedback loop for small setups.

## User Stories

### US-001: Init-time clone refactor — foreground mode (P1)
**Project**: specweave

**As a** developer initializing a workspace with 1-3 repos
**I want** cloning to use the job system in foreground mode
**So that** I get consistent job tracking and progress display without the init command returning before my repos are ready

**Acceptance Criteria**:
- [x] **AC-US1-01**: When user selects "clone-repos" during `specweave init` and provides 1-3 repo URLs, `launchCloneJob()` is called with `foreground: true`
- [x] **AC-US1-02**: The clone job runs inline (blocking) — init does not proceed to git-init/config until cloning completes
- [x] **AC-US1-03**: Progress is displayed inline (repo name + success/failure per repo) during foreground clone
- [x] **AC-US1-04**: `ParsedRepo { org, name, cloneUrl }` is mapped to `CloneLaunchOptions.repositories[]` format `{ owner, name, path, cloneUrl }` where `path = repositories/{org}/{name}`
- [x] **AC-US1-05**: The synchronous `cloneReposIntoWorkspace()` call in init.ts is fully replaced — no `execFileNoThrowSync` for cloning remains
- [x] **AC-US1-06**: The redundant `scanUmbrellaRepos()` re-scan after cloning is removed since the clone worker handles umbrella config registration

---

### US-002: Init-time clone refactor — background mode (P1)
**Project**: specweave

**As a** developer initializing a workspace with 4+ repos
**I want** cloning to run as a background job
**So that** the init command completes quickly and I can monitor clone progress via `specweave jobs`

**Acceptance Criteria**:
- [x] **AC-US2-01**: When 4+ repos are provided, `launchCloneJob()` is called with `foreground: false` (background mode)
- [x] **AC-US2-02**: Init command completes immediately after launching the background job — does not block on cloning
- [x] **AC-US2-03**: User sees a message with the job ID and instructions to monitor via `specweave jobs`
- [x] **AC-US2-04**: `umbrella.enabled: true` is set in config.json preemptively (before background clone completes) so the workspace is umbrella-ready immediately
- [x] **AC-US2-05**: Background clone job uses the existing `clone-worker.ts` which handles per-repo failure resilience, progress tracking, and umbrella config persistence on completion

---

### US-003: Single-repo handling consistency (P2)
**Project**: specweave

**As a** developer cloning a single repo during init
**I want** it to use the same `repositories/{org}/{repo}/` structure
**So that** single-repo and multi-repo workspaces have identical layout and can seamlessly grow

**Acceptance Criteria**:
- [x] **AC-US3-01**: A single repo provided during init is cloned to `repositories/{org}/{name}/` — not to the workspace root or any other layout
- [x] **AC-US3-02**: Single-repo clone uses foreground mode (1 repo < 4 threshold)
- [x] **AC-US3-03**: The resulting config.json has `umbrella.enabled: true` with the single repo in `childRepos[]`

---

### US-004: Edge cases — already-cloned repos and partial failures (P2)
**Project**: specweave

**As a** developer re-running init or recovering from a partial clone failure
**I want** the job system to handle already-cloned repos and failures gracefully
**So that** I can safely retry without duplicating work or losing progress

**Acceptance Criteria**:
- [x] **AC-US4-01**: If all provided repos already exist locally (have `.git` dir at target path), the clone job completes immediately with `skippedPreFlight: true` and no worker is spawned
- [x] **AC-US4-02**: Already-cloned repos are reported to the user as "skipped" with a count
- [x] **AC-US4-03**: In foreground mode, partial failures (some repos fail, some succeed) are reported with per-repo success/failure status — init continues to completion
- [x] **AC-US4-04**: In background mode, partial failures result in `completed_with_warnings` job status (never `failed`) — user can re-run to retry failed repos
- [x] **AC-US4-05**: The mapping from `ParsedRepo[]` to `CloneLaunchOptions.repositories[]` correctly handles repos with different orgs in the same batch

## Functional Requirements

### FR-001: Repo count threshold
The threshold between foreground and background mode is 3 repos. Repos <= 3: foreground. Repos >= 4: background. This threshold should be a named constant, not a magic number.

### FR-002: ParsedRepo to Job repo mapping
Map `ParsedRepo { org, name, cloneUrl }` to `{ owner: org, name, path: "repositories/{org}/{name}", cloneUrl }`. The `owner` field maps to the ParsedRepo `org` field.

### FR-003: Preemptive umbrella config
For background clones, set `umbrella.enabled: true` in config.json before launching the job. The clone worker will populate `childRepos[]` on completion. For foreground clones, the worker handles everything inline.

### FR-004: Remove dead code
After replacing `cloneReposIntoWorkspace()` in init.ts:
- Remove the `scanUmbrellaRepos()` re-scan call that follows cloning (line ~372 in init.ts) — the clone worker handles this
- The `cloneReposIntoWorkspace` function in `repo-connect.ts` can be removed or deprecated if no other callers exist
- Remove the `execFileNoThrowSync` import from init.ts if no longer needed for cloning (still used for git-init)

## Success Criteria

- Zero regressions: `specweave init` with 1-3 repos behaves identically to before (blocking, repos available after init)
- Background mode: `specweave init` with 4+ repos completes in < 5 seconds (excluding clone time)
- All existing clone-worker capabilities preserved: pre-flight skip, per-repo failure resilience, umbrella config persistence, resume support

## Out of Scope

- Changing the `specweave get` clone flow (uses its own `clone-repo.ts` helper — separate concern)
- Adding new CLI flags to `specweave init` for foreground/background override
- Changing the clone worker's internal behavior (sequential cloning, error handling, etc.)
- CI/non-interactive mode changes (those paths don't hit the clone prompt)

## Dependencies

- Existing `launchCloneJob()` in `src/core/background/job-launcher.ts` — already production-tested via `specweave get`
- Existing `clone-worker.ts` — handles actual git operations, progress, and umbrella config
- `ParsedRepo` type from `src/cli/helpers/init/repo-connect.ts`
