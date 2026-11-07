# Stop repeated finish-time PR failures on stale thread bindings

## Problem

Under "When a thread finishes: pull request", the thread "1209 skill authoring (app worktree)" (`mcp:6742c6aa-5ce2-4c47-b871-16549b70df54`) shows a yellow "Could not open a pull request: Git manager failed in runPrStep: Branch feat/1…" banner after almost every turn.

The full error in `~/.specwithcode/m4/userdata/logs/server.trace.ndjson*` is `GitManagerError: Git manager failed in runPrStep: Branch feat/1209-skill-authoring shares no commits with main, so there is nothing to propose into it.`, raised from `ThreadFinishActionService.finish` → `runStackedAction` → `runPrStep` (`apps/server/src/git/GitManager.ts`, the `sharesHistoryWithHead` guard).

Cause:

1. The thread is still bound to `/Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/feat-1209-skill-authoring`. That folder is still on disk, on `feat/1209-skill-authoring`, and the branch tracks the archived `dev` remote (`anton-abyzov/specwithcode-dev`), where it merged as #1430. The thread's own links record #1430 as merged.
2. After today's move, `origin` is the public `anton-abyzov/specwithcode`, and its `main` shares no history with that branch. `git.status` finds no PR on `origin` for the branch and counts it ahead of default, so `branchReadyForPullRequest` says yes and `create_pr` runs.
3. `finish` runs on every completed run, and each notice is keyed by run id, so the same failure is retried and shown again after every turn.
4. The thread's real work is in the shared checkout on `feat/1248-skill-management`, with PR #26 open and linked to the thread (source `agent`). `finish` never looks at the thread's linked pull requests.
5. The notice summary keeps the `Git manager failed in runPrStep:` prefix, so the banner truncates before the useful part.

## Scope

In: `ThreadFinishActionService` decides from the thread's linked pull requests and the checkout's real branch, does not repeat a failure it already reported for the same checkout state, and writes one actionable message. Out: rebinding threads to a different checkout automatically, persisting failure memory across service restarts, changing `runPrStep`'s base resolution.

## Acceptance Criteria

- [ ] AC-01: When the bound branch has a merged or closed pull request linked to the thread (any repository, matched by head branch, removed links ignored) and none open, the finish step opens nothing and shows no notice.
- [ ] AC-02: An open pull request for the branch is still handled by `create_pr`, which pushes new commits and reuses it; no second pull request is opened.
- [ ] AC-03: The finish step acts only on a bound checkout that exists and is on the thread's branch; a stale binding whose branch landed is skipped.
- [ ] AC-04: A failure is not retried while the checkout state (branch, upstream, commit counts) is unchanged, except once an hour, and the same error for the same state adds no second notice.
- [ ] AC-05: The failure notice's first line drops the `Git manager failed in <op>:` prefix and, for unrelated history, says what to do (rebase onto the base branch, or link the thread's pull request).

## Approach

`apps/server/src/orchestration-v2/ThreadFinishActionService.ts`: pure helpers `branchLanded(links, branch)` and `checkoutSignature(cwd, status)`; an in-memory map of the last failure per thread (checkout, error, time), retried after `FAILURE_RETRY_AFTER_MS`; `failureNotice` uses the GitManagerError `detail` and rewrites the unrelated-history case. Tests in `ThreadFinishActionService.test.ts`.

Rejected after review: skipping `create_pr` when any open link exists (it would stop pushing new commits and block a PR for a new branch); proposing `status.refName` instead of `thread.branch` (it would let auto-merge touch a branch someone else checked out). The engine has no record of a different checkout an agent moved to, so a moved thread is handled by its landed links, not by guessing a new folder.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Failure memory is in memory only → acceptable (reversible).
- D-02 Same-state failures retry once an hour → covers host outages and expired sign-ins (reversible).
### Open
- none

## Tasks

### T-01 Decide from linked pull requests and the real branch
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/orchestration-v2/ThreadFinishActionService.ts, apps/server/src/orchestration-v2/ThreadFinishActionService.test.ts | Test: cd ~/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/server && npx vitest run src/orchestration-v2/ThreadFinishActionService.test.ts

### T-02 Report a failure once, with an actionable message
- AC: AC-04, AC-05 | Files: apps/server/src/orchestration-v2/ThreadFinishActionService.ts, apps/server/src/orchestration-v2/ThreadFinishActionService.test.ts | Test: cd ~/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/server && npx vitest run src/orchestration-v2/ThreadFinishActionService.test.ts

### T-03 Verify and close 1252
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1252
