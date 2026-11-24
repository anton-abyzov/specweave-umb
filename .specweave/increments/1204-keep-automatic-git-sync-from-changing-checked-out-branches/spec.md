# 1204 Keep automatic Git sync from changing checked out branches

## Problem

Another Git client can switch branches after automatic sync checks the current branch. The subsequent merge acts on the newly checked-out branch.

## Scope

Automatic repository sync before turns. Explicit pull and merge actions retain their behavior.

## Acceptance Criteria

- [ ] AC-01 Automatic sync updates remote-tracking refs without changing the branch, index or working files.
- [ ] AC-02 A custom fetch mapping cannot direct an automatic fetch into a local branch.
- [ ] AC-03 A clean checkout behind origin gets a clear notice that it can be pulled.

## Approach

Limit automatic fetch to origin remote-tracking refs. Report when the checkout is behind and leave the pull to an explicit action. The Git CLI does not provide a conditional merge that pins the checked-out symbolic ref throughout the index and worktree update.

## Tasks

### T-01 Make automatic Git sync fetch-only

- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/repositorySync.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/repositorySync.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectRepositorySync.test.ts, repositories/anton-abyzov/specwithcode-dev/docs/user/moving-a-project.md | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/fleet/repositorySync.test.ts src/project/ProjectRepositorySync.test.ts --maxWorkers=1
